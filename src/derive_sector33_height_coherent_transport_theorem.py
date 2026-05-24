from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT
from src.derive_sector33_boundary_annihilation_theorem import (
    FIELD_PRIME,
    regular_trace_coefficients,
    signed_mod,
    vec_digest,
)
from src.derive_sector33_residual_lift_theorem import (
    character_evaluation,
    quotient_shadow,
    vector_from_entries,
)


THEOREM_ID = "sector33_height_coherent_transport"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

BOUNDARY_TO_LOOP_REPORT = D20_INVARIANTS / "boundary_to_loop" / "report.json"
ANNIHILATION_REPORT = D20_INVARIANTS / "theorems" / "sector33_boundary_annihilation" / "report.json"
RESIDUAL_LIFT_REPORT = D20_INVARIANTS / "theorems" / "sector33_residual_lift" / "report.json"
SECTOR_ATTACHMENT_REPORT = D20_INVARIANTS / "theorems" / "sector33_residual_attachment" / "report.json"
D20_EDGES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"
RELATION_NPZ = ROOT / "data" / "raw" / "relation_memberships.npz"
QUOTIENT_NPZ = ROOT / "data" / "raw" / "quotients.npz"
TENSOR_NPZ = ROOT / "data" / "raw" / "T_985.npz"


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha_json(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def split_ids(value: str) -> list[int]:
    return [int(part) for part in value.split()] if value else []


def load_edges() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            edge_id = int(row["edge_id"])
            rows[edge_id] = {
                "edge_id": edge_id,
                "u": int(row["u"]),
                "v": int(row["v"]),
                "u_label": row["u_label"],
                "v_label": row["v_label"],
                "shared_duad": row["shared_duad"],
                "swapped_pair": row["swapped_pair"],
                "interface_weight": int(row["interface_weight"]),
                "selector_duad_index": int(row["selector_duad_index"]),
                "selector_duad": row["selector_duad"],
                "selector_choice": int(row["selector_choice"]),
            }
    return rows


def load_cycle(cycle_id: int) -> dict[str, Any]:
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["cycle_id"]) == cycle_id:
                return {
                    "cycle_id": int(row["cycle_id"]),
                    "length": int(row["length"]),
                    "optical_action": int(row["optical_action"]),
                    "connection_product": int(row["connection_product"]),
                    "connection_log_action": row["connection_log_action"],
                    "entropy_proxy_A_over_4WD6": row["entropy_proxy_A_over_4WD6"],
                    "vertices": split_ids(row["vertices"]),
                    "vertex_labels": row["vertex_labels"],
                    "edge_ids": split_ids(row["edge_ids"]),
                    "turn_addresses": row["turn_addresses"].split(),
                }
    raise ValueError(f"cycle {cycle_id} not found")


def active_circuit_witness(cycle: dict[str, Any], edges: dict[int, dict[str, Any]]) -> dict[str, Any]:
    edge_count = len(edges)
    vertices = cycle["vertices"]
    edge_ids = cycle["edge_ids"]
    incidence = [0] * edge_count
    signed_incidence = [0] * edge_count
    vertex_boundary: dict[int, int] = {}
    steps = []
    action = 0
    for source, target, edge_id in zip(vertices, vertices[1:], edge_ids):
        edge = edges[int(edge_id)]
        if {int(edge["u"]), int(edge["v"])} != {int(source), int(target)}:
            raise ValueError(f"edge {edge_id} does not connect {source}->{target}")
        sign = 1 if (int(edge["u"]), int(edge["v"])) == (int(source), int(target)) else -1
        incidence[int(edge_id)] = 1
        signed_incidence[int(edge_id)] = sign
        vertex_boundary[int(source)] = vertex_boundary.get(int(source), 0) - 1
        vertex_boundary[int(target)] = vertex_boundary.get(int(target), 0) + 1
        action += int(edge["interface_weight"])
        steps.append(
            {
                "edge_id": int(edge_id),
                "source": int(source),
                "target": int(target),
                "orientation_sign": sign,
                "height": int(edge["interface_weight"]),
                "selector_duad": edge["selector_duad"],
                "selector_choice": int(edge["selector_choice"]),
            }
        )

    vertex_boundary = {key: value for key, value in sorted(vertex_boundary.items()) if value}
    active_matrix_row = [[edge_id, incidence[edge_id]] for edge_id in range(edge_count) if incidence[edge_id]]
    signed_row = [[edge_id, signed_incidence[edge_id]] for edge_id in range(edge_count) if signed_incidence[edge_id]]
    heights = [edges[edge_id]["interface_weight"] for edge_id in range(edge_count)]
    return {
        "edge_count": edge_count,
        "active_matrix_row": active_matrix_row,
        "signed_circuit_row": signed_row,
        "height_vector_sha256": hashlib.sha256(canonical(heights)).hexdigest(),
        "height_dot_active_row": int(sum(incidence[i] * heights[i] for i in range(edge_count))),
        "all_active_heights_positive": all(heights[i] > 0 for i in range(edge_count) if incidence[i]),
        "vertex_boundary": vertex_boundary,
        "steps": steps,
    }


def update_theorem_index(report: dict[str, Any], out_dir: Path) -> None:
    index_path = out_dir.parent / "index.json"
    entry = {
        "id": THEOREM_ID,
        "manifest": rel(out_dir / "manifest.json"),
        "report": rel(out_dir / "report.json"),
        "report_sha256": report["certificate_sha256"],
        "status": report["status"],
    }
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry.source_drop",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_theorem() -> dict[str, Any]:
    boundary = load_json(BOUNDARY_TO_LOOP_REPORT)
    annihilation = load_json(ANNIHILATION_REPORT)
    residual_lift_report = load_json(RESIDUAL_LIFT_REPORT)
    attachment = load_json(SECTOR_ATTACHMENT_REPORT)
    edges = load_edges()
    cycle = load_cycle(8)
    circuit = active_circuit_witness(cycle, edges)

    relation_count = int(np.load(RELATION_NPZ)["block_i"].shape[0])
    quotients = np.load(QUOTIENT_NPZ)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    trace_coeff = regular_trace_coefficients(triples, relation_count)

    e33 = vector_from_entries(
        annihilation["derived"]["sector33_tube_idempotent"]["vector"]["entries"],
        relation_count,
    )
    lambda_gamma8 = vector_from_entries(
        boundary["derived"]["cycle8_lift"]["vector"]["entries"],
        relation_count,
    )
    dimension = int(annihilation["derived"]["sector33_profile"]["block_dimension"])
    inverse_dimension = pow(dimension, -1, FIELD_PRIME)
    derived_action = int(circuit["height_dot_active_row"])
    derived_residual_integral = -derived_action
    derived_residual_mod = derived_residual_integral % FIELD_PRIME
    derived_scalar = (derived_residual_mod * inverse_dimension) % FIELD_PRIME
    height_transport = (derived_scalar * e33) % FIELD_PRIME
    corrected_transport = (lambda_gamma8 + height_transport) % FIELD_PRIME

    chi_e33 = character_evaluation(triples, trace_coeff, e33, e33, dimension)
    chi_lambda = character_evaluation(triples, trace_coeff, e33, lambda_gamma8, dimension)
    chi_height = character_evaluation(triples, trace_coeff, e33, height_transport, dimension)
    chi_corrected = character_evaluation(triples, trace_coeff, e33, corrected_transport, dimension)

    q42_shadow = quotient_shadow(height_transport, np.asarray(quotients["q42_map"], dtype=np.int64), 42)
    q12_shadow = quotient_shadow(height_transport, np.asarray(quotients["q12_map"], dtype=np.int64), 12)

    certified_residual = attachment["derived"]["sector_attachment"]
    prior_lift = residual_lift_report["derived"]
    checks = {
        "boundary_to_loop_is_certified": boundary.get("status") == "D20_BOUNDARY_TO_LOOP_MAP_CERTIFIED"
        and boundary.get("all_checks_pass") is True,
        "sector33_annihilation_is_certified": annihilation.get("status")
        == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        and annihilation.get("all_checks_pass") is True,
        "normalized_residual_lift_is_certified": residual_lift_report.get("status")
        == "D20_SECTOR33_RESIDUAL_LIFT_CERTIFIED"
        and residual_lift_report.get("all_checks_pass") is True,
        "active_circuit_is_closed": circuit["vertex_boundary"] == {},
        "active_circuit_has_five_edges": len(circuit["active_matrix_row"]) == 5,
        "active_circuit_matches_gamma8_edges": [edge_id for edge_id, _ in circuit["active_matrix_row"]]
        == sorted(cycle["edge_ids"]),
        "height_dot_active_row_matches_cycle_optical_action": derived_action == int(cycle["optical_action"]),
        "height_values_positive_on_active_circuit": circuit["all_active_heights_positive"] is True,
        "derived_residual_matches_sector_attachment": derived_residual_integral
        == int(certified_residual["residual_integral"])
        and derived_residual_mod == int(certified_residual["residual_mod_prime"]),
        "derived_scalar_matches_prior_normalized_residual_lift": derived_scalar
        == int(prior_lift["residual"]["residual_lift_scalar"]),
        "bare_lambda_pi33_coefficient_is_zero": chi_lambda["coefficient_mod_prime"] == 0,
        "chi33_of_e33_equals_sector_dimension": chi_e33["coefficient_mod_prime"] == dimension,
        "height_transport_pi33_coefficient_is_edge_derived_residual": chi_height["coefficient_mod_prime"]
        == derived_residual_mod
        and chi_height["coefficient_signed"] == derived_residual_integral,
        "corrected_transport_pi33_coefficient_is_edge_derived_residual": chi_corrected["coefficient_mod_prime"]
        == derived_residual_mod
        and chi_corrected["coefficient_signed"] == derived_residual_integral,
        "height_transport_has_zero_q42_shadow": q42_shadow["nonzero_count"] == 0,
        "height_transport_has_zero_q12_shadow": q12_shadow["nonzero_count"] == 0,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        if all_checks_pass
        else "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector33_height_coherent_transport.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The first sector-33 hidden correction is derived from the active D20 circuit itself: "
            "the closed gamma_8 circuit has height action 374784, so the refined transport adds "
            "-374784/dim(Pi_33) times e_33. This recovers the Pi_33 residual while remaining invisible "
            "to A42 and A12."
        ),
        "definition": {
            "active_circuit": "The gamma_8 row in the D20 edge-circuit matrix with support {1,2,11,21,22}.",
            "height_cochain": "h(e)=interface_weight(e), the certified optical edge height.",
            "height_action": "A_h(gamma)=<C_gamma,h>, the dot product of the active circuit row with edge heights.",
            "transport": "Lambda_hc(gamma)=lambda_boundary(gamma) - (A_h(gamma)/dim(Pi_33)) e_33.",
        },
        "inputs": {
            "boundary_to_loop_report": {
                "path": rel(BOUNDARY_TO_LOOP_REPORT),
                "sha256": sha_file(BOUNDARY_TO_LOOP_REPORT),
            },
            "sector33_boundary_annihilation_report": {
                "path": rel(ANNIHILATION_REPORT),
                "sha256": sha_file(ANNIHILATION_REPORT),
            },
            "sector33_residual_lift_report": {
                "path": rel(RESIDUAL_LIFT_REPORT),
                "sha256": sha_file(RESIDUAL_LIFT_REPORT),
            },
            "sector33_residual_attachment_report": {
                "path": rel(SECTOR_ATTACHMENT_REPORT),
                "sha256": sha_file(SECTOR_ATTACHMENT_REPORT),
            },
            "d20_edges": {
                "path": rel(D20_EDGES_CSV),
                "sha256": sha_file(D20_EDGES_CSV),
            },
            "primitive_cycles": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
            "relation_memberships": {
                "path": rel(RELATION_NPZ),
                "sha256": sha_file(RELATION_NPZ),
            },
            "quotients": {
                "path": rel(QUOTIENT_NPZ),
                "sha256": sha_file(QUOTIENT_NPZ),
            },
            "t985_tensor": {
                "path": rel(TENSOR_NPZ),
                "sha256": sha_file(TENSOR_NPZ),
            },
        },
        "derived": {
            "cycle": cycle,
            "active_circuit": circuit,
            "edge_derived_residual": {
                "height_action": derived_action,
                "residual_integral": derived_residual_integral,
                "residual_mod_prime": derived_residual_mod,
                "dimension": dimension,
                "inverse_dimension": inverse_dimension,
                "transport_scalar": derived_scalar,
                "transport_scalar_signed": signed_mod(derived_scalar),
            },
            "vectors": {
                "lambda_boundary_gamma8": vec_digest(lambda_gamma8),
                "e33": vec_digest(e33),
                "height_transport": vec_digest(height_transport),
                "corrected_transport": vec_digest(corrected_transport),
            },
            "pi33_tube_character": {
                "e33": chi_e33,
                "lambda_boundary_gamma8": chi_lambda,
                "height_transport": chi_height,
                "corrected_transport": chi_corrected,
            },
            "public_shadows": {
                "height_transport_q42": q42_shadow,
                "height_transport_q12": q12_shadow,
            },
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Generalize Lambda_hc from gamma_8 to all 2047 nonzero D20 closed-return residue classes "
            "and certify which sector idempotent, if any, carries each height-derived residual."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector33_height_coherent_transport_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify gamma_8 is a closed active circuit in the D20 edge graph",
            "derive the residual scalar from edge heights, not from the residual attachment scalar",
            "verify the height-derived transport has Pi_33 coefficient -374784",
            "verify the height-derived transport has zero A42 and A12 shadows",
            "verify the result agrees with the earlier normalized residual lift certificate",
        ],
    }
    manifest["report_sha256"] = report["certificate_sha256"]
    manifest["manifest_sha256"] = sha_json({k: v for k, v in manifest.items() if k != "manifest_sha256"})

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report.get("all_checks_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
