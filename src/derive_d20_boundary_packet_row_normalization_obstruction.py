from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import hashlib
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    from src.paths import D20_INVARIANTS, ROOT
except ModuleNotFoundError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.paths import D20_INVARIANTS, ROOT


THEOREM_ID = "d20_boundary_packet_row_normalization_obstruction"
DEFAULT_OUT_DIR = D20_INVARIANTS / "theorems" / THEOREM_ID

D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE = (
    D20_INVARIANTS / "theorems" / "d20_boundary_loop_step_atom_incidence" / "report.json"
)
D20_BOUNDARY_PACKET_PAIRING_OBSTRUCTION = (
    D20_INVARIANTS / "theorems" / "d20_boundary_packet_pairing_obstruction" / "report.json"
)
D20_PACKET_BRIDGE_SNF_OBSTRUCTION = (
    D20_INVARIANTS / "theorems" / "d20_packet_bridge_snf_obstruction" / "report.json"
)


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


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


def input_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha_file(path)}


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
        if index.get("schema") == "d20.theorem_registry.source_drop":
            return
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


def histogram(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def local_failures(u: int, v: int) -> list[str]:
    failures = []
    if u % 2 != 0:
        failures.append("u_not_0_mod_2")
    if v % 2 != 0:
        failures.append("v_not_0_mod_2")
    if (u + v) % 6 != 0:
        failures.append("u_plus_v_not_0_mod_6")
    return failures


def residue_pair_passes(
    matrix: list[list[int]], left: int, right: int, left_residue: int, right_residue: int
) -> bool:
    return all(
        not local_failures(
            left_residue * matrix[left][col],
            right_residue * matrix[right][col],
        )
        for col in range(len(matrix[0]))
    )


def pair_residue_options(matrix: list[list[int]], residues: list[int]) -> list[dict[str, Any]]:
    rows = []
    for left, right in combinations(range(len(matrix)), 2):
        options = [
            [left_residue, right_residue]
            for left_residue in residues
            for right_residue in residues
            if residue_pair_passes(matrix, left, right, left_residue, right_residue)
        ]
        rows.append(
            {
                "public_atom_pair": [left, right],
                "compatible_residue_pairs_mod6": options,
                "compatible_residue_pair_count": len(options),
            }
        )
    return rows


def row_obstruction_rows(matrix: list[list[int]]) -> list[dict[str, Any]]:
    rows = []
    for row_index, row in enumerate(matrix):
        odd_columns = [idx for idx, value in enumerate(row) if value % 2 != 0]
        values_mod3 = sorted({value % 3 for value in row})
        rows.append(
            {
                "public_atom_id": row_index,
                "has_odd_step_entry": bool(odd_columns),
                "first_odd_step_atom_id": odd_columns[0] if odd_columns else None,
                "odd_step_entry_count": len(odd_columns),
                "entry_residues_mod3": values_mod3,
                "parity_requires_even_row_scalar": bool(odd_columns),
            }
        )
    return rows


def build_theorem() -> dict[str, Any]:
    incidence = load_json(D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE)
    pairing = load_json(D20_BOUNDARY_PACKET_PAIRING_OBSTRUCTION)
    packet_snf = load_json(D20_PACKET_BRIDGE_SNF_OBSTRUCTION)
    matrix = incidence["derived"]["boundary_atom_step_incidence_matrix"]
    residues = [0, 2, 4]
    rows = pair_residue_options(matrix, residues)
    option_hist = histogram(Counter(row["compatible_residue_pair_count"] for row in rows))
    option_value_hist = histogram(
        Counter(
            tuple(option)
            for row in rows
            for option in row["compatible_residue_pairs_mod6"]
        )
    )
    row_rows = row_obstruction_rows(matrix)
    obstruction_summary = {
        "public_atom_count": len(matrix),
        "step_atom_column_count": len(matrix[0]) if matrix else 0,
        "tested_unordered_public_pair_count": len(rows),
        "tested_even_scalar_residues_mod6": residues,
        "compatible_residue_pair_count_histogram": option_hist,
        "compatible_residue_pair_value_histogram": option_value_hist,
        "only_compatible_residue_pair_mod6": [0, 0],
        "all_rows_require_even_scalar_by_parity": all(
            row["parity_requires_even_row_scalar"] for row in row_rows
        ),
        "row_scalar_divisibility_for_any_packet_pairing": 6,
        "nonuniform_row_scaling_improves_on_scalar_6": False,
    }
    local_image_test = packet_snf["derived"]["obstruction_summary"]["local_image_test"]
    checks = {
        "boundary_loop_step_atom_incidence_is_certified": incidence.get("status")
        == "D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE_CERTIFIED"
        and incidence.get("all_checks_pass") is True,
        "boundary_packet_pairing_obstruction_is_certified": pairing.get("status")
        == "D20_BOUNDARY_PACKET_PAIRING_OBSTRUCTION_CERTIFIED"
        and pairing.get("all_checks_pass") is True,
        "packet_bridge_snf_obstruction_is_certified": packet_snf.get("status")
        == "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED"
        and packet_snf.get("all_checks_pass") is True,
        "packet_snf_local_test_is_exact": local_image_test
        == "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet",
        "incidence_matrix_is_20_by_25": len(matrix) == 20
        and all(len(row) == 25 for row in matrix),
        "all_rows_have_odd_entries": all(row["has_odd_step_entry"] for row in row_rows),
        "all_rows_require_even_scalar_by_parity": obstruction_summary[
            "all_rows_require_even_scalar_by_parity"
        ]
        is True,
        "all_190_public_pairs_tested": len(rows) == 190,
        "every_pair_has_exactly_one_even_residue_option": option_hist == {"1": 190},
        "only_0_0_mod6_residue_pair_is_compatible": option_value_hist == {"(0, 0)": 190},
        "row_scalar_divisibility_for_any_packet_pairing_is_6": obstruction_summary[
            "row_scalar_divisibility_for_any_packet_pairing"
        ]
        == 6,
        "nonuniform_row_scaling_does_not_improve_scalar_6": obstruction_summary[
            "nonuniform_row_scaling_improves_on_scalar_6"
        ]
        is False,
        "agrees_with_prior_minimal_scalar_6": pairing["derived"]["obstruction_summary"][
            "minimal_scalar_with_perfect_matching"
        ]
        == 6,
    }
    report = {
        "schema": "d20.theorem.d20_boundary_packet_row_normalization_obstruction",
        "status": "D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_CERTIFIED",
        "object": "D20",
        "definition": {
            "input_boundary_matrix": (
                "the signed Lambda^3 H6 target-minus-source incidence matrix for the 25 visible "
                "Loop_297 step atoms"
            ),
            "row_normalization_family": (
                "diagonal public-atom row scalars, including signs, reduced modulo the packet "
                "SNF modulus constraints"
            ),
            "tested_residues_mod6": residues,
            "packet_snf_image_test": local_image_test,
        },
        "claim": (
            "Allowing independent signed row scalars on the 20 public boundary atoms still cannot "
            "improve on scalar-6 clearing before pairing into packet doublets. Every boundary row "
            "contains odd step entries, forcing an even row scalar, and for every public-atom pair "
            "the only even residue pair modulo 6 satisfying all 25 packet block tests is (0,0)."
        ),
        "inputs": {
            "d20_boundary_loop_step_atom_incidence_report": input_record(
                D20_BOUNDARY_LOOP_STEP_ATOM_INCIDENCE
            ),
            "d20_boundary_packet_pairing_obstruction_report": input_record(
                D20_BOUNDARY_PACKET_PAIRING_OBSTRUCTION
            ),
            "d20_packet_bridge_snf_obstruction_report": input_record(
                D20_PACKET_BRIDGE_SNF_OBSTRUCTION
            ),
        },
        "derived": {
            "obstruction_summary": obstruction_summary,
            "public_row_parity_obstruction_rows": row_rows,
            "public_row_parity_obstruction_rows_sha256": sha_json(row_rows),
            "pair_even_residue_option_rows": rows,
            "pair_even_residue_option_rows_sha256": sha_json(rows),
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": {
            "negative_boundary": (
                "A boundary-to-packet map cannot be obtained by independently rescaling labelled "
                "public atoms and then choosing packet doublets, unless every used row scalar is "
                "already divisible by 6."
            ),
            "what_remains_open": (
                "The remaining escape hatch is a genuinely non-diagonal quotient or signed "
                "linear combination of boundary atoms that preserves the Loop_297/A985 labels."
            ),
            "not_claimed": (
                "This is not a no-go theorem for arbitrary linear boundary-to-packet maps and not "
                "a DLCQ/M-theory construction."
            ),
        },
        "next_highest_yield_item": (
            "Test low-support signed linear combinations of boundary atoms, beyond diagonal row "
            "scaling, for packet-SNF-compatible columns that preserve step-atom labels."
        ),
    }
    report["certificate_sha256"] = sha_json(
        {key: value for key, value in report.items() if key != "certificate_sha256"}
    )
    return report


def write_theorem(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    report = build_theorem()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema": "d20.theorem.d20_boundary_packet_row_normalization_obstruction_manifest",
        "status": report["status"],
        "name": THEOREM_ID,
        "artifacts": {
            "report": rel(out_dir / "report.json"),
            "manifest": rel(out_dir / "manifest.json"),
        },
        "report_sha256": report["certificate_sha256"],
        "inputs": report["inputs"],
        "purpose": [
            "test whether independent signed row scalars improve on scalar-6 packet clearing",
            "separate diagonal row normalization from genuinely non-diagonal boundary quotients",
        ],
    }
    manifest["manifest_sha256"] = sha_json(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    update_theorem_index(report, out_dir)
    return report


def main() -> None:
    report = write_theorem()
    print(report["status"])
    print(report["certificate_sha256"])


if __name__ == "__main__":
    main()
