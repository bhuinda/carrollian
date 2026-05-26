from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from .paths import D20_INVARIANTS, HCYCLE_INVARIANTS
except ImportError:  # Supports `python src/derive_d20_fourier_residue_screen_theorem.py`.
    from derive_d20_sandpile_critical_group_theorem import rel, sha_file, sha_json
    from paths import D20_INVARIANTS, HCYCLE_INVARIANTS


THEOREM_ID = "fourier_residue_screen"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID
PUBLIC_BOUNDARY_REPORT = (
    D20_INVARIANTS / "theorems" / "public_boundary_graph_invariants" / "report.json"
)
SANDPILE_REPORT = D20_INVARIANTS / "theorems" / "sandpile_critical_group" / "report.json"
RESIDUE_CSV = HCYCLE_INVARIANTS / "d20_Hcycle_mod2_residue_spectrum_all_subsets.csv"
RESIDUE_RANK = 11
MASK_COUNT = 1 << RESIDUE_RANK


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
        schema = index.get("schema", "d20.theorem_registry")
        theorems = [item for item in index.get("theorems", []) if item.get("id") != THEOREM_ID]
    else:
        schema = "d20.theorem_registry"
        theorems = []
    theorems.append(entry)
    theorems = sorted(theorems, key=lambda item: item["id"])
    index = {
        "schema": schema,
        "status": "D20_THEOREM_REGISTRY_BUILT",
        "theorem_count": len(theorems),
        "theorems": theorems,
    }
    index["registry_sha256"] = sha_json({k: v for k, v in index.items() if k != "registry_sha256"})
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bit_indices(mask: int, width: int = RESIDUE_RANK) -> list[int]:
    return [idx for idx in range(width) if (mask >> idx) & 1]


def parse_basis_cycle_ids(value: str) -> list[int]:
    if not value.strip():
        return []
    return [int(part) for part in value.split()]


def load_residue_rows(path: Path = RESIDUE_CSV) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = []
        for row in csv.DictReader(f):
            mask = int(row["mask"])
            basis_cycle_ids = parse_basis_cycle_ids(row["basis_cycle_ids"])
            parsed_mask = sum(1 << idx for idx in basis_cycle_ids)
            rows.append(
                {
                    "mask": mask,
                    "basis_cycle_ids": basis_cycle_ids,
                    "parsed_mask_from_basis_cycle_ids": parsed_mask,
                    "residue_edge_weight": int(row["residue_edge_weight"]),
                    "total_basis_length": int(row["total_basis_length"]),
                    "total_optical_action": int(row["total_optical_action"]),
                    "incidence_vector_mod2": row["incidence_vector_mod2"],
                }
            )
    return sorted(rows, key=lambda row: row["mask"])


def f2_rank(vectors: list[int]) -> int:
    basis: dict[int, int] = {}
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
                continue
            basis[pivot] = value
            break
    return len(basis)


def phase_parity(mask: int, defect_mask: int) -> int:
    return (mask & defect_mask).bit_count() & 1


def phase_value(mask: int, defect_mask: int) -> int:
    return -1 if phase_parity(mask, defect_mask) else 1


def screen_record(gate: dict[str, Any], rows: list[dict[str, Any]], index: int) -> dict[str, Any]:
    defect_cycle_ids = [int(value) for value in gate["defect_cycle_ids"]]
    defect_vector_mask = sum(1 << idx for idx in defect_cycle_ids)
    coherent_masks = [row["mask"] for row in rows if phase_value(row["mask"], defect_vector_mask) == 1]
    odd_masks = [row["mask"] for row in rows if phase_value(row["mask"], defect_vector_mask) == -1]
    return {
        "screen_id": f"signed_turn_screen_{index}",
        "source_positive_phase_labels": gate["positive_phase_labels"],
        "source_negative_phase_labels": gate["negative_phase_labels"],
        "defect_cycle_ids": defect_cycle_ids,
        "defect_vector_mask": defect_vector_mask,
        "defect_vector_bits": bit_indices(defect_vector_mask),
        "defect_vector_weight": len(defect_cycle_ids),
        "character_formula": "chi(mask)=(-1)^(popcount(mask & defect_vector_mask) mod 2)",
        "kernel_dimension": RESIDUE_RANK - 1,
        "coherent_mask_count": len(coherent_masks),
        "odd_mask_count": len(odd_masks),
        "coherent_masks_first_16": coherent_masks[:16],
        "odd_masks_first_16": odd_masks[:16],
        "coherent_masks_sha256": hashlib.sha256(canonical(coherent_masks)).hexdigest(),
        "odd_masks_sha256": hashlib.sha256(canonical(odd_masks)).hexdigest(),
    }


def signature_for_mask(mask: int, defect_vectors: list[int]) -> str:
    return "".join(str(phase_parity(mask, vector)) for vector in defect_vectors)


def build_screen_rows(rows: list[dict[str, Any]], defect_vectors: list[int]) -> list[dict[str, Any]]:
    return [
        {
            "mask": row["mask"],
            "basis_cycle_ids": row["basis_cycle_ids"],
            "signature": signature_for_mask(row["mask"], defect_vectors),
        }
        for row in rows
    ]


def build_theorem() -> dict[str, Any]:
    public_boundary = load_json(PUBLIC_BOUNDARY_REPORT)
    sandpile = load_json(SANDPILE_REPORT) if SANDPILE_REPORT.exists() else {}
    residue_rows = load_residue_rows()
    gates = public_boundary["derived"]["fourier_screen"]["representative_best_gates"]
    screens = [screen_record(gate, residue_rows, idx) for idx, gate in enumerate(gates)]
    defect_vectors = [int(screen["defect_vector_mask"]) for screen in screens]
    screen_rows = build_screen_rows(residue_rows, defect_vectors)
    cell_counts = Counter(row["signature"] for row in screen_rows)
    sorted_cell_counts = {key: int(cell_counts[key]) for key in sorted(cell_counts)}
    combined_rank = f2_rank(defect_vectors)
    all_mask_values = [row["mask"] for row in residue_rows]
    parsed_consistent = all(
        row["mask"] == row["parsed_mask_from_basis_cycle_ids"] for row in residue_rows
    )
    optical_action_by_signature = {
        signature: {
            "mask_count": int(sum(1 for row in residue_rows if signature_for_mask(row["mask"], defect_vectors) == signature)),
            "total_optical_action_sum": int(
                sum(
                    row["total_optical_action"]
                    for row in residue_rows
                    if signature_for_mask(row["mask"], defect_vectors) == signature
                )
            ),
        }
        for signature in sorted_cell_counts
    }

    checks = {
        "public_boundary_report_is_certified": public_boundary.get("status")
        == "D20_PUBLIC_BOUNDARY_GRAPH_INVARIANTS_CERTIFIED"
        and public_boundary.get("all_checks_pass") is True,
        "source_best_gate_count_is_3": len(gates) == 3,
        "source_best_defect_count_is_2": int(
            public_boundary["derived"]["fourier_screen"]["best_nontrivial_defect_count"]
        )
        == 2,
        "residue_mask_count_is_2048": len(residue_rows) == MASK_COUNT,
        "residue_masks_are_complete": all_mask_values == list(range(MASK_COUNT)),
        "residue_basis_parse_matches_mask": parsed_consistent,
        "each_screen_vector_has_weight_2": all(
            int(screen["defect_vector_weight"]) == 2 for screen in screens
        ),
        "each_screen_splits_1024_1024": all(
            int(screen["coherent_mask_count"]) == 1024 and int(screen["odd_mask_count"]) == 1024
            for screen in screens
        ),
        "each_screen_kernel_dimension_is_10": all(
            int(screen["kernel_dimension"]) == 10 for screen in screens
        ),
        "combined_screen_rank_is_3": combined_rank == 3,
        "combined_screen_has_8_cells": len(sorted_cell_counts) == 8,
        "combined_screen_cells_are_256_each": set(sorted_cell_counts.values()) == {256},
        "sandpile_report_agrees_if_present": not sandpile
        or (
            sandpile.get("status") == "D20_SANDPILE_CRITICAL_GROUP_CERTIFIED"
            and sandpile.get("all_checks_pass") is True
            and int(sandpile.get("derived", {}).get("critical_group", {}).get("order", 0))
            == 5_184_000
        ),
    }
    all_checks_pass = all(checks.values())
    status = (
        "D20_FOURIER_RESIDUE_SCREEN_CERTIFIED"
        if all_checks_pass
        else "D20_FOURIER_RESIDUE_SCREEN_NEEDS_REVIEW"
    )

    report = {
        "schema": "d20.theorem.fourier_residue_screen",
        "status": status,
        "object": "d20",
        "claim": (
            "The three best signed-turn two-defect phase gates induce explicit nonzero "
            "F2 characters on the 2048-element closed-return residue cube. Each character "
            "has a 1024-mask kernel and a 1024-mask odd coset. Together the three defect "
            "vectors have F2 rank 3 and split the residue cube into eight cells of 256 masks."
        ),
        "definition": {
            "finite_residue_character": (
                "For a two-defect signed-turn gate with defect vector d in F2^11, "
                "chi_d(mask)=(-1)^(<d,mask>) where <d,mask> is computed by bit parity."
            ),
            "residue_cube": (
                "The 2048 closed-return masks are the complete F2^11 basis-cycle activation "
                "space from d20_Hcycle_mod2_residue_spectrum_all_subsets.csv."
            ),
            "a985_lift_boundary": (
                "This report certifies finite F2 residue characters only. A true A985 "
                "sector character still requires a separate tube/idempotent character "
                "evaluation against the certified A985 data."
            ),
            "sandpile_boundary": (
                "The sandpile critical group has 5,184,000 recurrent classes, but this "
                "report does not define a mask-to-divisor firing map."
            ),
        },
        "inputs": {
            "public_boundary_graph_invariants_report": {
                "path": rel(PUBLIC_BOUNDARY_REPORT),
                "sha256": sha_file(PUBLIC_BOUNDARY_REPORT),
            },
            "closed_return_residue_spectrum": {
                "path": rel(RESIDUE_CSV),
                "sha256": sha_file(RESIDUE_CSV),
            },
            "sandpile_critical_group_report": {
                "path": rel(SANDPILE_REPORT),
                "sha256": sha_file(SANDPILE_REPORT),
            }
            if SANDPILE_REPORT.exists()
            else None,
        },
        "derived": {
            "residue_space": {
                "rank": RESIDUE_RANK,
                "mask_count": len(residue_rows),
                "masks_are_complete": all_mask_values == list(range(MASK_COUNT)),
                "basis_parse_matches_mask": parsed_consistent,
            },
            "screens": screens,
            "combined_screen": {
                "defect_vectors": defect_vectors,
                "rank_over_f2": combined_rank,
                "cell_counts_by_signature": sorted_cell_counts,
                "common_kernel_signature": "000",
                "common_kernel_mask_count": int(sorted_cell_counts.get("000", 0)),
                "residue_screen_rows_sha256": hashlib.sha256(canonical(screen_rows)).hexdigest(),
                "residue_screen_rows": screen_rows,
                "optical_action_by_signature": optical_action_by_signature,
            },
            "sandpile_pairing_seam": {
                "sandpile_recurrent_class_count": sandpile.get("derived", {})
                .get("critical_group", {})
                .get("order"),
                "mask_to_divisor_map_certified": False,
                "status": "not_certified_in_this_report",
            },
        },
        "interpretation": {
            "what_is_certified": (
                "The signed-turn two-defect screens now act on every closed-return mask as "
                "linear F2 characters, with exact kernel/coset counts and a rank-3 combined split."
            ),
            "what_this_does_not_prove": (
                "This is not yet an A985 sector character certificate, and it does not classify "
                "which mask cells correspond to sandpile recurrent divisor classes."
            ),
        },
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "next_highest_yield_item": (
            "Materialize A985/tube sector-character candidates for these three F2 screens, "
            "evaluate them on primitive idempotent or tube character data, and then build "
            "a mask-to-divisor map for comparison with the sandpile critical group."
        ),
    }
    report["certificate_sha256"] = sha_json({k: v for k, v in report.items() if k != "certificate_sha256"})
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    manifest = {
        "schema": "d20.theorem.fourier_residue_screen_manifest",
        "name": THEOREM_ID,
        "inputs": report["inputs"],
        "outputs": {
            "manifest": rel(out_dir / "manifest.json"),
            "report": rel(out_dir / "report.json"),
        },
        "certification_tests": [
            "verify the public-boundary signed-turn screen source is certified",
            "verify all 2048 closed-return masks are present",
            "verify basis-cycle ids reconstruct each mask",
            "lift each two-defect gate to a nonzero F2 residue character",
            "verify each screen splits masks 1024/1024",
            "verify the three screens have F2 rank 3 and eight equal 256-mask cells",
            "record the A985 sector-character and sandpile divisor-map boundaries",
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
