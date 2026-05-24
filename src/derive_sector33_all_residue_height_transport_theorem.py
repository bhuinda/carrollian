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


THEOREM_ID = "sector33_all_residue_height_transport"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

ANNIHILATION_REPORT = D20_INVARIANTS / "theorems" / "sector33_boundary_annihilation" / "report.json"
HEIGHT_TRANSPORT_REPORT = (
    D20_INVARIANTS / "theorems" / "sector33_height_coherent_transport" / "report.json"
)
RESIDUE_SPECTRUM_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv"
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


def load_edge_heights() -> list[int]:
    rows: list[tuple[int, int]] = []
    with D20_EDGES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append((int(row["edge_id"]), int(row["interface_weight"])))
    rows = sorted(rows)
    if [edge_id for edge_id, _ in rows] != list(range(len(rows))):
        raise ValueError("D20 edge ids are not contiguous from zero")
    return [weight for _, weight in rows]


def load_basis_cycle_heights() -> list[int]:
    rows: list[tuple[int, int]] = []
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append((int(row["cycle_id"]), int(row["optical_action"])))
    rows = sorted(rows)
    if [cycle_id for cycle_id, _ in rows] != list(range(len(rows))):
        raise ValueError("primitive cycle ids are not contiguous from zero")
    return [height for _, height in rows]


def load_residue_rows(edge_heights: list[int], basis_cycle_heights: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with RESIDUE_SPECTRUM_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            incidence_bits = [1 if char == "1" else 0 for char in row["incidence_vector_mod2"].strip()]
            if len(incidence_bits) != len(edge_heights):
                raise ValueError(f"bad incidence length for mask {row['mask']}")
            basis_cycle_ids = split_ids(row["basis_cycle_ids"])
            edge_mod2_action = int(sum(bit * edge_heights[idx] for idx, bit in enumerate(incidence_bits)))
            height_action = int(sum(basis_cycle_heights[idx] for idx in basis_cycle_ids))
            active_edges = [idx for idx, bit in enumerate(incidence_bits) if bit]
            total_action = int(row["total_optical_action"])
            residual_integral = -height_action
            residual_mod = residual_integral % FIELD_PRIME
            rows.append(
                {
                    "mask": int(row["mask"]),
                    "basis_cycle_ids": basis_cycle_ids,
                    "active_edges": active_edges,
                    "active_edge_count": int(len(active_edges)),
                    "basis_active_count": int(len(basis_cycle_ids)),
                    "total_basis_length": int(row["total_basis_length"]),
                    "recorded_total_optical_action": total_action,
                    "height_dot_active_row": height_action,
                    "height_coherent": bool(height_action == total_action),
                    "edge_mod2_height_action": edge_mod2_action,
                    "edge_mod2_height_gap": int(total_action - edge_mod2_action),
                    "edge_mod2_height_coherent": bool(edge_mod2_action == total_action),
                    "residual_integral": residual_integral,
                    "residual_mod_prime": int(residual_mod),
                    "incidence_vector_mod2": row["incidence_vector_mod2"].strip(),
                }
            )
    return sorted(rows, key=lambda item: item["mask"])


def transport_rows(rows: list[dict[str, Any]], dimension: int) -> list[dict[str, Any]]:
    inverse_dimension = pow(dimension, -1, FIELD_PRIME)
    out = []
    for row in rows:
        scalar = (int(row["residual_mod_prime"]) * inverse_dimension) % FIELD_PRIME
        coefficient = (scalar * dimension) % FIELD_PRIME
        out.append(
            {
                "mask": int(row["mask"]),
                "basis_cycle_ids": row["basis_cycle_ids"],
                "active_edge_count": int(row["active_edge_count"]),
                "basis_active_count": int(row["basis_active_count"]),
                "height_action": int(row["height_dot_active_row"]),
                "edge_mod2_height_action": int(row["edge_mod2_height_action"]),
                "edge_mod2_height_gap": int(row["edge_mod2_height_gap"]),
                "residual_integral": int(row["residual_integral"]),
                "residual_mod_prime": int(row["residual_mod_prime"]),
                "transport_scalar": int(scalar),
                "transport_scalar_signed": signed_mod(int(scalar)),
                "support_sector": 33,
                "pi33_coefficient_mod_prime": int(coefficient),
                "coefficient_matches_residual_mod_prime": bool(coefficient == row["residual_mod_prime"]),
            }
        )
    return out


def digest_rows(rows: list[dict[str, Any]]) -> str:
    return sha_json(rows)


def action_histogram(rows: list[dict[str, Any]]) -> dict[str, int]:
    hist: dict[str, int] = {}
    for row in rows:
        key = str(int(row["height_dot_active_row"]))
        hist[key] = hist.get(key, 0) + 1
    return dict(sorted(hist.items(), key=lambda item: int(item[0])))


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
    annihilation = load_json(ANNIHILATION_REPORT)
    gamma8_transport = load_json(HEIGHT_TRANSPORT_REPORT)
    edge_heights = load_edge_heights()
    basis_cycle_heights = load_basis_cycle_heights()
    rows = load_residue_rows(edge_heights, basis_cycle_heights)
    nonzero_rows = [row for row in rows if row["mask"] != 0]
    transported = transport_rows(rows, int(annihilation["derived"]["sector33_profile"]["block_dimension"]))
    nonzero_transports = [row for row in transported if row["mask"] != 0]
    edge_mod2_mismatch_rows = [row for row in rows if not row["edge_mod2_height_coherent"]]

    relation_count = int(np.load(RELATION_NPZ)["block_i"].shape[0])
    quotients = np.load(QUOTIENT_NPZ)
    triples = np.asarray(np.load(TENSOR_NPZ)["triples"], dtype=np.int64)
    trace_coeff = regular_trace_coefficients(triples, relation_count)
    e33 = vector_from_entries(
        annihilation["derived"]["sector33_tube_idempotent"]["vector"]["entries"],
        relation_count,
    )
    dimension = int(annihilation["derived"]["sector33_profile"]["block_dimension"])
    chi_e33 = character_evaluation(triples, trace_coeff, e33, e33, dimension)
    e33_q42_shadow = quotient_shadow(e33, np.asarray(quotients["q42_map"], dtype=np.int64), 42)
    e33_q12_shadow = quotient_shadow(e33, np.asarray(quotients["q12_map"], dtype=np.int64), 12)

    masks = [row["mask"] for row in rows]
    gamma8_row = next(row for row in transported if row["mask"] == 256)
    max_action = max(row["height_dot_active_row"] for row in rows)
    max_action_rows = [row for row in transported if row["height_action"] == max_action]
    first_nonzero = min(nonzero_transports, key=lambda row: (row["height_action"], row["mask"]))
    class_samples = [transported[0], first_nonzero, gamma8_row, max_action_rows[0]]
    sample_masks = []
    samples = []
    for row in class_samples:
        if row["mask"] not in sample_masks:
            sample_masks.append(row["mask"])
            samples.append(row)

    checks = {
        "sector33_annihilation_is_certified": annihilation.get("status")
        == "D20_SECTOR33_BOUNDARY_TO_LOOP_ANNIHILATION_CERTIFIED"
        and annihilation.get("all_checks_pass") is True,
        "gamma8_height_transport_is_certified": gamma8_transport.get("status")
        == "D20_SECTOR33_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        and gamma8_transport.get("all_checks_pass") is True,
        "residue_class_count_is_2048": len(rows) == 2048,
        "nonzero_residue_class_count_is_2047": len(nonzero_rows) == 2047,
        "residue_masks_are_complete": masks == list(range(2048)),
        "edge_mod2_incidence_matrix_has_30_columns": all(
            len(row["incidence_vector_mod2"]) == len(edge_heights) == 30 for row in rows
        ),
        "basis_active_circuit_matrix_has_11_columns": len(basis_cycle_heights) == 11
        and all(all(0 <= idx < 11 for idx in row["basis_cycle_ids"]) for row in rows),
        "basis_active_circuit_matrix_is_height_coherent": all(row["height_coherent"] for row in rows),
        "edge_mod2_incidence_is_not_globally_height_coherent": len(edge_mod2_mismatch_rows) > 0,
        "gamma8_edge_mod2_row_is_height_coherent": next(row for row in rows if row["mask"] == 256)[
            "edge_mod2_height_coherent"
        ]
        is True,
        "zero_class_has_zero_transport_scalar": transported[0]["mask"] == 0
        and transported[0]["transport_scalar"] == 0,
        "all_nonzero_integral_residuals_are_nonzero": all(
            int(row["residual_integral"]) != 0 for row in nonzero_transports
        ),
        "all_nonzero_field_residuals_are_nonzero": all(
            int(row["residual_mod_prime"]) != 0 for row in nonzero_transports
        ),
        "all_transport_coefficients_match_height_residuals": all(
            row["coefficient_matches_residual_mod_prime"] for row in transported
        ),
        "all_transports_carried_by_sector33": all(row["support_sector"] == 33 for row in transported),
        "chi33_of_e33_equals_dimension": chi_e33["coefficient_mod_prime"] == dimension,
        "e33_has_zero_q42_shadow": e33_q42_shadow["nonzero_count"] == 0,
        "e33_has_zero_q12_shadow": e33_q12_shadow["nonzero_count"] == 0,
        "all_scalar_e33_transports_have_zero_public_shadow": e33_q42_shadow["nonzero_count"] == 0
        and e33_q12_shadow["nonzero_count"] == 0,
        "gamma8_row_matches_prior_height_transport": gamma8_row["height_action"]
        == gamma8_transport["derived"]["edge_derived_residual"]["height_action"]
        and gamma8_row["transport_scalar"]
        == gamma8_transport["derived"]["edge_derived_residual"]["transport_scalar"],
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_CERTIFIED"
        if all_checks_pass
        else "D20_ALL_RESIDUE_HEIGHT_COHERENT_TRANSPORT_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.sector33_all_residue_height_transport.source_drop",
        "status": status,
        "object": "d20",
        "claim": (
            "The full D20 basis-cycle active circuit matrix is height-coherent: each certified closed-return "
            "residue row pairs with the primitive-cycle height vector to give its optical action. The edge "
            "mod-2 incidence matrix is not globally height-coherent because symmetric differences cancel "
            "repeated traversals. The sector-33 "
            "height-coherent transport Lambda_hc(gamma)=lambda_boundary(gamma)-(<C_gamma,h>/dim(Pi_33))e_33 "
            "therefore carries every height-derived residual in the public-zero sector 33."
        ),
        "definition": {
            "basis_active_circuit_matrix": "The 2048 x 11 matrix whose rows are basis-cycle activation masks in the residue spectrum.",
            "basis_height_cochain": "h_B(c_i)=optical_action(c_i) for each primitive basis cycle.",
            "height_coherence": "For every residue row C_gamma, <C_gamma,h_B> equals total_optical_action.",
            "edge_mod2_caveat": "The 2048 x 30 incidence_vector_mod2 matrix records edge symmetric differences, not traversal multiplicity, so it is not globally height-coherent.",
            "global_transport": "Lambda_hc(gamma)=lambda_boundary(gamma)-(<C_gamma,h>/dim(Pi_33))e_33.",
            "support_sector": "Pi_33, because e_33 is public-zero and chi_33(e_33)=dim(Pi_33).",
        },
        "inputs": {
            "sector33_boundary_annihilation_report": {
                "path": rel(ANNIHILATION_REPORT),
                "sha256": sha_file(ANNIHILATION_REPORT),
            },
            "gamma8_height_transport_report": {
                "path": rel(HEIGHT_TRANSPORT_REPORT),
                "sha256": sha_file(HEIGHT_TRANSPORT_REPORT),
            },
            "residue_spectrum": {
                "path": rel(RESIDUE_SPECTRUM_CSV),
                "sha256": sha_file(RESIDUE_SPECTRUM_CSV),
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
            "field_prime": FIELD_PRIME,
            "edge_height_vector": edge_heights,
            "edge_height_vector_sha256": hashlib.sha256(canonical(edge_heights)).hexdigest(),
            "basis_cycle_height_vector": basis_cycle_heights,
            "basis_cycle_height_vector_sha256": hashlib.sha256(canonical(basis_cycle_heights)).hexdigest(),
            "residue_class_count": len(rows),
            "nonzero_residue_class_count": len(nonzero_rows),
            "unique_height_action_count": len({row["height_dot_active_row"] for row in rows}),
            "min_nonzero_height_action": int(min(row["height_dot_active_row"] for row in nonzero_rows)),
            "max_height_action": int(max_action),
            "edge_mod2_height_incoherence": {
                "mismatch_count": int(len(edge_mod2_mismatch_rows)),
                "first_mismatch": {
                    key: edge_mod2_mismatch_rows[0][key]
                    for key in (
                        "mask",
                        "basis_cycle_ids",
                        "recorded_total_optical_action",
                        "edge_mod2_height_action",
                        "edge_mod2_height_gap",
                        "incidence_vector_mod2",
                    )
                }
                if edge_mod2_mismatch_rows
                else None,
            },
            "field_zero_nonzero_residual_count": int(
                sum(1 for row in nonzero_transports if row["residual_mod_prime"] == 0)
            ),
            "sector33_support": {
                "sector": 33,
                "dimension": dimension,
                "chi33_e33": chi_e33,
                "e33": vec_digest(e33),
                "e33_q42_shadow": e33_q42_shadow,
                "e33_q12_shadow": e33_q12_shadow,
            },
            "gamma8_row": gamma8_row,
            "transport_rows_sha256": digest_rows(transported),
            "height_action_histogram_sha256": sha_json(action_histogram(rows)),
            "class_samples": samples,
            "transport_rows": transported,
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Materialize the public-zero sector-idempotent basis and prove whether sector 33 is the unique "
            "support available for all height residuals, or only the canonical support selected here."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.sector33_all_residue_height_transport_manifest.source_drop",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the 2048 residue rows form a complete 11-cycle residue space",
            "verify every edge-mod2 row has 30 columns and every basis activation row uses 11 cycles",
            "verify each basis activation row dot primitive-cycle height vector equals its recorded optical action",
            "verify edge-mod2 incidence is not globally height-coherent, due cancellation of repeated traversals",
            "verify every height-derived residual is carried by the sector-33 e_33 transport",
            "verify e_33 gives zero A42 and A12 shadows, hence all scalar transports do too",
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
