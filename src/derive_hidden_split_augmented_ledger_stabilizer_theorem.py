from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.derive_finite_flux_balance_theorem import d20_charge, parse_label, sub_charge
from src.paths import D20_INVARIANTS, HCYCLE_INVARIANTS, ROOT


THEOREM_ID = "hidden_split_augmented_ledger_stabilizer"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

FINITE_FLUX_BALANCE_REPORT = (
    D20_INVARIANTS / "theorems" / "finite_flux_balance" / "report.json"
)
GLOBAL_COUNTERTERM_LATTICE_REPORT = (
    D20_INVARIANTS / "theorems" / "global_counterterm_lattice" / "report.json"
)
HIDDEN_SPLIT_SYMMETRY_REPORT = (
    D20_INVARIANTS / "theorems" / "global_corrected_hidden_split_symmetry" / "report.json"
)
EDGE_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_d20_edges.csv"
PRIMITIVE_CYCLES_CSV = HCYCLE_INVARIANTS / "subscript_Hcycle_primitive_cycles.csv"

PUBLIC_COMPONENTS = ("M", "J", "P", "Phi")
RESIDUE_RANK = 11
VERTEX_COUNT = 20
EDGE_COUNT = 30
CLOCK_MODULUS = 26


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
        index = load_json(index_path)
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": "d20.theorem_registry",
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bit_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def z_function(mask: int, weights: list[int], modulus: int | None = None) -> int:
    value = sum(weights[idx] for idx in bit_indices(mask))
    return value if modulus is None else value % modulus


def load_edges() -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    with EDGE_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            edge = {
                "edge_id": int(row["edge_id"]),
                "u": int(row["u"]),
                "v": int(row["v"]),
                "u_label": row["u_label"],
                "v_label": row["v_label"],
                "interface_weight": int(row["interface_weight"]),
                "selector_duad_index": int(row["selector_duad_index"]),
                "selector_choice": int(row["selector_choice"]),
            }
            edges.append(edge)
    return sorted(edges, key=lambda item: item["edge_id"])


def load_primitive_actions() -> list[int]:
    actions: list[int] = []
    with PRIMITIVE_CYCLES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in sorted(csv.DictReader(f), key=lambda item: int(item["cycle_id"])):
            actions.append(int(row["optical_action"]))
    return actions


def vertex_charges(edges: list[dict[str, Any]]) -> dict[int, dict[str, int]]:
    vertices: dict[int, tuple[str, ...]] = {}
    for edge in edges:
        vertices.setdefault(edge["u"], parse_label(edge["u_label"]))
        vertices.setdefault(edge["v"], parse_label(edge["v_label"]))
    return {vertex: d20_charge(parts) for vertex, parts in vertices.items()}


def edge_fluxes(edges: list[dict[str, Any]], charges: dict[int, dict[str, int]]) -> list[dict[str, int]]:
    return [sub_charge(charges[edge["v"]], charges[edge["u"]]) for edge in edges]


def first_functional_failure(
    source_values: list[int],
    image_values: list[int],
    basis_image_masks: list[int],
) -> dict[str, Any] | None:
    for idx, (source, image) in enumerate(zip(source_values, image_values)):
        if source != image:
            return {
                "basis_coordinate": idx,
                "source_mask": 1 << idx,
                "source_value": source,
                "image_mask": basis_image_masks[idx],
                "image_basis_cycle_indices": bit_indices(basis_image_masks[idx]),
                "image_value": image,
            }
    return None


def first_edge_weight_failure(
    edges: list[dict[str, Any]],
    edge_permutation: list[int],
    column: str,
) -> dict[str, Any] | None:
    values = [edge[column] for edge in edges]
    for edge_id, image_edge_id in enumerate(edge_permutation):
        if values[edge_id] != values[image_edge_id]:
            return {
                "edge_id": edge_id,
                "image_edge_id": image_edge_id,
                "source_value": values[edge_id],
                "image_value": values[image_edge_id],
                "column": column,
            }
    return None


def first_state_charge_failure(
    charges: dict[int, dict[str, int]],
    vertex_permutation: list[int],
) -> dict[str, Any] | None:
    for vertex, image_vertex in enumerate(vertex_permutation):
        if charges[vertex] != charges[image_vertex]:
            return {
                "vertex": vertex,
                "image_vertex": image_vertex,
                "source_charge": charges[vertex],
                "image_charge": charges[image_vertex],
            }
    return None


def first_edge_flux_failure(
    edges: list[dict[str, Any]],
    charges: dict[int, dict[str, int]],
    vertex_permutation: list[int],
) -> dict[str, Any] | None:
    source_fluxes = edge_fluxes(edges, charges)
    for edge in edges:
        edge_id = edge["edge_id"]
        source_flux = source_fluxes[edge_id]
        image_flux = sub_charge(
            charges[vertex_permutation[edge["v"]]],
            charges[vertex_permutation[edge["u"]]],
        )
        if source_flux != image_flux:
            return {
                "edge_id": edge_id,
                "source_oriented_edge": [edge["u"], edge["v"]],
                "image_oriented_edge": [
                    vertex_permutation[edge["u"]],
                    vertex_permutation[edge["v"]],
                ],
                "source_flux": source_flux,
                "image_flux": image_flux,
            }
    return None


def record_for_preserver(
    preserver: dict[str, Any],
    edges: list[dict[str, Any]],
    charges: dict[int, dict[str, int]],
    counterterms_mod26: list[int],
    basis_weights_mod26: list[int],
    corrected_basis_clock_mod26: list[int],
    primitive_actions: list[int],
) -> dict[str, Any]:
    basis_images = [int(mask) for mask in preserver["basis_image_masks"]]
    edge_permutation = [int(edge) for edge in preserver["edge_permutation"]]
    vertex_permutation = [int(vertex) for vertex in preserver["vertex_permutation"]]

    counterterm_image_values = [
        z_function(mask, counterterms_mod26, CLOCK_MODULUS) for mask in basis_images
    ]
    optical_clock_image_values = [
        z_function(mask, basis_weights_mod26, CLOCK_MODULUS) for mask in basis_images
    ]
    corrected_clock_image_values = [
        z_function(mask, corrected_basis_clock_mod26, CLOCK_MODULUS) for mask in basis_images
    ]
    primitive_action_image_values = [
        z_function(mask, primitive_actions, None) for mask in basis_images
    ]

    counterterm_failure = first_functional_failure(
        counterterms_mod26,
        counterterm_image_values,
        basis_images,
    )
    optical_clock_failure = first_functional_failure(
        basis_weights_mod26,
        optical_clock_image_values,
        basis_images,
    )
    corrected_clock_failure = first_functional_failure(
        corrected_basis_clock_mod26,
        corrected_clock_image_values,
        basis_images,
    )
    primitive_action_failure = first_functional_failure(
        primitive_actions,
        primitive_action_image_values,
        basis_images,
    )
    edge_interface_failure = first_edge_weight_failure(edges, edge_permutation, "interface_weight")
    state_charge_failure = first_state_charge_failure(charges, vertex_permutation)
    edge_flux_failure = first_edge_flux_failure(edges, charges, vertex_permutation)

    preserves = {
        "hidden_corrected_split": bool(preserver["preserves_hidden_split"]),
        "sector26_counterterm_vector_mod26": counterterm_failure is None,
        "normalized_optical_clock_mod26": optical_clock_failure is None,
        "corrected_clock_mod26": corrected_clock_failure is None,
        "primitive_optical_action_weights": primitive_action_failure is None,
        "edge_interface_weights": edge_interface_failure is None,
        "public_state_charge_components": state_charge_failure is None,
        "public_oriented_edge_flux_components": edge_flux_failure is None,
    }
    preserves["full_augmented_ledger"] = all(preserves.values())

    return {
        "automorphism_id": int(preserver["automorphism_id"]),
        "is_identity": vertex_permutation == list(range(VERTEX_COUNT)),
        "vertex_cycle_notation": preserver.get("vertex_cycle_notation", []),
        "edge_cycle_notation": preserver.get("edge_cycle_notation", []),
        "basis_image_masks": basis_images,
        "preserves": preserves,
        "failures": {
            "sector26_counterterm_vector_mod26": counterterm_failure,
            "normalized_optical_clock_mod26": optical_clock_failure,
            "corrected_clock_mod26": corrected_clock_failure,
            "primitive_optical_action_weights": primitive_action_failure,
            "edge_interface_weights": edge_interface_failure,
            "public_state_charge_components": state_charge_failure,
            "public_oriented_edge_flux_components": edge_flux_failure,
        },
    }


def build_theorem() -> dict[str, Any]:
    finite_flux = load_json(FINITE_FLUX_BALANCE_REPORT)
    global_lattice = load_json(GLOBAL_COUNTERTERM_LATTICE_REPORT)
    hidden_split = load_json(HIDDEN_SPLIT_SYMMETRY_REPORT)
    edges = load_edges()
    primitive_actions = load_primitive_actions()
    charges = vertex_charges(edges)

    derived_lattice = global_lattice["derived"]
    counterterms_mod26 = [int(value) for value in derived_lattice["counterterm_lifts_mod26"]]
    basis_weights_mod26 = [int(value) for value in derived_lattice["basis_weights_mod26"]]
    corrected_basis_clock_mod26 = [
        int(value) for value in derived_lattice["corrected_basis_clock_mod26"]
    ]
    preservers = hidden_split["derived"]["symmetry_classification"]["preserving_automorphisms"]
    records = [
        record_for_preserver(
            preserver,
            edges,
            charges,
            counterterms_mod26,
            basis_weights_mod26,
            corrected_basis_clock_mod26,
            primitive_actions,
        )
        for preserver in preservers
    ]
    identity_records = [record for record in records if record["is_identity"]]
    nonidentity_records = [record for record in records if not record["is_identity"]]
    full_ledger_preservers = [
        record for record in records if record["preserves"]["full_augmented_ledger"]
    ]
    nonidentity = nonidentity_records[0] if nonidentity_records else {}
    nonidentity_preserves = nonidentity.get("preserves", {})

    checks = {
        "finite_exact_flux_balance_is_certified": finite_flux.get("status")
        == "D20_FINITE_EXACT_FLUX_BALANCE_CERTIFIED"
        and finite_flux.get("all_checks_pass") is True,
        "global_counterterm_lattice_is_certified": global_lattice.get("status")
        == "D20_GLOBAL_COUNTERTERM_LATTICE_CERTIFIED"
        and global_lattice.get("all_checks_pass") is True,
        "hidden_split_symmetry_is_certified": hidden_split.get("status")
        == "D20_GLOBAL_CORRECTED_HIDDEN_SPLIT_SYMMETRY_CERTIFIED"
        and hidden_split.get("all_checks_pass") is True,
        "hidden_split_stabilizer_candidate_count_is_2": len(records) == 2,
        "identity_preserves_full_augmented_ledger": len(identity_records) == 1
        and identity_records[0]["preserves"]["full_augmented_ledger"] is True,
        "nonidentity_preserves_hidden_split_and_corrected_clock": len(nonidentity_records) == 1
        and nonidentity_preserves.get("hidden_corrected_split") is True
        and nonidentity_preserves.get("corrected_clock_mod26") is True,
        "nonidentity_breaks_sector26_counterterm_vector": nonidentity_preserves.get(
            "sector26_counterterm_vector_mod26"
        )
        is False,
        "nonidentity_breaks_optical_weights": nonidentity_preserves.get(
            "normalized_optical_clock_mod26"
        )
        is False
        and nonidentity_preserves.get("primitive_optical_action_weights") is False
        and nonidentity_preserves.get("edge_interface_weights") is False,
        "nonidentity_breaks_public_charge_components": nonidentity_preserves.get(
            "public_state_charge_components"
        )
        is False
        and nonidentity_preserves.get("public_oriented_edge_flux_components") is False,
        "full_augmented_ledger_stabilizer_is_identity": len(full_ledger_preservers) == 1
        and full_ledger_preservers[0]["is_identity"] is True,
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_CERTIFIED"
        if all_checks_pass
        else "D20_HIDDEN_SPLIT_AUGMENTED_LEDGER_STABILIZER_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.hidden_split_augmented_ledger_stabilizer",
        "status": status,
        "object": "d20",
        "claim": (
            "The C2 stabilizer of the global corrected hidden split does not lift to a nontrivial symmetry "
            "of the augmented charge/action ledger. The nonidentity split-preserver keeps only the corrected "
            "order-two hidden character; it breaks the sector-26 counterterm vector, optical action weights, "
            "and public charge components. The full augmented ledger stabilizer is therefore trivial."
        ),
        "definition": {
            "candidate_group": (
                "The two graph automorphisms certified by global_corrected_hidden_split_symmetry as preserving "
                "the corrected hidden closed-return split."
            ),
            "augmented_ledger_fields": [
                "corrected hidden split character",
                "sector-26 counterterm vector modulo 26",
                "normalized optical clock modulo 26",
                "primitive optical action weights",
                "edge interface weights",
                "public D20 state charge components (M,J,P,Phi)",
                "public oriented edge flux components",
            ],
            "preservation_test": (
                "A candidate preserves a functional field when the field value on each basis cycle equals "
                "the field value on its induced cycle-space image; it preserves public state/edge fields when "
                "the labeled (M,J,P,Phi) vectors are unchanged under the vertex-induced action."
            ),
        },
        "inputs": {
            "finite_flux_balance_report": {
                "path": rel(FINITE_FLUX_BALANCE_REPORT),
                "sha256": sha_file(FINITE_FLUX_BALANCE_REPORT),
            },
            "global_counterterm_lattice_report": {
                "path": rel(GLOBAL_COUNTERTERM_LATTICE_REPORT),
                "sha256": sha_file(GLOBAL_COUNTERTERM_LATTICE_REPORT),
            },
            "hidden_split_symmetry_report": {
                "path": rel(HIDDEN_SPLIT_SYMMETRY_REPORT),
                "sha256": sha_file(HIDDEN_SPLIT_SYMMETRY_REPORT),
            },
            "hcycle_edge_table": {"path": rel(EDGE_CSV), "sha256": sha_file(EDGE_CSV)},
            "primitive_cycle_table": {
                "path": rel(PRIMITIVE_CYCLES_CSV),
                "sha256": sha_file(PRIMITIVE_CYCLES_CSV),
            },
        },
        "derived": {
            "candidate_group": {
                "hidden_split_stabilizer_order": len(records),
                "full_augmented_ledger_stabilizer_order": len(full_ledger_preservers),
                "full_augmented_ledger_preserving_automorphism_ids": [
                    record["automorphism_id"] for record in full_ledger_preservers
                ],
            },
            "ledger_vectors": {
                "counterterm_lifts_mod26": counterterms_mod26,
                "basis_weights_mod26": basis_weights_mod26,
                "corrected_basis_clock_mod26": corrected_basis_clock_mod26,
                "primitive_optical_actions": primitive_actions,
            },
            "candidate_records": records,
            "summary": {
                "identity_preserves_everything": bool(identity_records)
                and identity_records[0]["preserves"]["full_augmented_ledger"],
                "nonidentity_preserves_only_corrected_hidden_layer": bool(nonidentity_records)
                and nonidentity_records[0]["preserves"]["hidden_corrected_split"]
                and nonidentity_records[0]["preserves"]["corrected_clock_mod26"]
                and not nonidentity_records[0]["preserves"]["sector26_counterterm_vector_mod26"]
                and not nonidentity_records[0]["preserves"]["primitive_optical_action_weights"]
                and not nonidentity_records[0]["preserves"]["public_state_charge_components"],
                "nonidentity_first_failures": nonidentity.get("failures"),
            },
            "candidate_records_sha256": sha_json(records),
        },
        "interpretation": {
            "what_this_proves": [
                "the hidden split alone has a C2 finite symmetry",
                "adding the sector-26 counterterms and optical/public ledgers breaks that C2",
                "the full augmented finite boundary ledger is rigid under the tested public graph symmetries",
            ],
            "what_this_does_not_prove": (
                "This does not classify A985 automorphisms or continuum symmetry groups; it classifies the "
                "finite H-cycle graph action on the certified augmented D20 ledger fields."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Use the trivial augmented-ledger stabilizer to define a canonical orientation/marking for the "
            "finite boundary screen, then test whether that marking gives a unique flux-balance gauge."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.hidden_split_augmented_ledger_stabilizer_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the finite exact flux, global counterterm lattice, and hidden split symmetry inputs",
            "evaluate both hidden-split preserving automorphisms on the sector-26 counterterm vector",
            "evaluate both hidden-split preserving automorphisms on optical action weights",
            "evaluate both hidden-split preserving automorphisms on public charge components",
            "verify the full augmented ledger stabilizer is the identity only",
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
