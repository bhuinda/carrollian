from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = (
    "data/invariants/d20/theorems/d20_boundary_packet_row_normalization_obstruction/report.json"
)
INPUT_RELS = {
    "d20_boundary_loop_step_atom_incidence_report": (
        "data/invariants/d20/theorems/d20_boundary_loop_step_atom_incidence/report.json"
    ),
    "d20_boundary_packet_pairing_obstruction_report": (
        "data/invariants/d20/theorems/d20_boundary_packet_pairing_obstruction/report.json"
    ),
    "d20_packet_bridge_snf_obstruction_report": (
        "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 boundary packet row normalization {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 boundary packet row normalization {key} hash mismatch")


def validate_d20_boundary_packet_row_normalization_obstruction() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_boundary_packet_row_normalization_obstruction")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 boundary packet row normalization certificate")

    if rec.get("schema") != "d20.theorem.d20_boundary_packet_row_normalization_obstruction":
        raise AssertionError("D20 boundary packet row normalization schema mismatch")
    if rec.get("status") != "D20_BOUNDARY_PACKET_ROW_NORMALIZATION_OBSTRUCTION_CERTIFIED":
        raise AssertionError("D20 boundary packet row normalization status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 boundary packet row normalization checks did not pass")

    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(rec.get("inputs", {}), key, rel_path)

    definition = rec.get("definition", {})
    if definition.get("tested_residues_mod6") != [0, 2, 4]:
        raise AssertionError("D20 boundary packet row normalization residue set mismatch")
    if definition.get("packet_snf_image_test") != (
        "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet"
    ):
        raise AssertionError("D20 boundary packet row normalization image-test mismatch")

    derived = rec.get("derived", {})
    summary = derived.get("obstruction_summary", {})
    if summary.get("public_atom_count") != 20:
        raise AssertionError("D20 boundary packet row normalization public count mismatch")
    if summary.get("step_atom_column_count") != 25:
        raise AssertionError("D20 boundary packet row normalization column count mismatch")
    if summary.get("tested_unordered_public_pair_count") != 190:
        raise AssertionError("D20 boundary packet row normalization pair count mismatch")
    if summary.get("tested_even_scalar_residues_mod6") != [0, 2, 4]:
        raise AssertionError("D20 boundary packet row normalization tested residues mismatch")
    if summary.get("compatible_residue_pair_count_histogram") != {"1": 190}:
        raise AssertionError("D20 boundary packet row normalization option count mismatch")
    if summary.get("compatible_residue_pair_value_histogram") != {"(0, 0)": 190}:
        raise AssertionError("D20 boundary packet row normalization option value mismatch")
    if summary.get("only_compatible_residue_pair_mod6") != [0, 0]:
        raise AssertionError("D20 boundary packet row normalization compatible residue mismatch")
    if summary.get("all_rows_require_even_scalar_by_parity") is not True:
        raise AssertionError("D20 boundary packet row normalization parity mismatch")
    if summary.get("row_scalar_divisibility_for_any_packet_pairing") != 6:
        raise AssertionError("D20 boundary packet row normalization divisibility mismatch")
    if summary.get("nonuniform_row_scaling_improves_on_scalar_6") is not False:
        raise AssertionError("D20 boundary packet row normalization improvement overclaim")

    row_rows = derived.get("public_row_parity_obstruction_rows", [])
    if len(row_rows) != 20:
        raise AssertionError("D20 boundary packet row normalization row obstruction count mismatch")
    if h_json(row_rows) != derived.get("public_row_parity_obstruction_rows_sha256"):
        raise AssertionError("D20 boundary packet row normalization row obstruction hash mismatch")
    for idx, row in enumerate(row_rows):
        if row.get("public_atom_id") != idx:
            raise AssertionError("D20 boundary packet row normalization public row order mismatch")
        if row.get("has_odd_step_entry") is not True:
            raise AssertionError("D20 boundary packet row normalization missing odd row witness")
        if row.get("parity_requires_even_row_scalar") is not True:
            raise AssertionError("D20 boundary packet row normalization parity row mismatch")
        if row.get("first_odd_step_atom_id") is None:
            raise AssertionError("D20 boundary packet row normalization missing first odd atom")

    option_rows = derived.get("pair_even_residue_option_rows", [])
    if len(option_rows) != 190:
        raise AssertionError("D20 boundary packet row normalization option row count mismatch")
    if h_json(option_rows) != derived.get("pair_even_residue_option_rows_sha256"):
        raise AssertionError("D20 boundary packet row normalization option row hash mismatch")
    for row in option_rows:
        if row.get("compatible_residue_pair_count") != 1:
            raise AssertionError("D20 boundary packet row normalization pair option count mismatch")
        if row.get("compatible_residue_pairs_mod6") != [[0, 0]]:
            raise AssertionError("D20 boundary packet row normalization pair option mismatch")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("D20 boundary packet row normalization check table mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 boundary packet row normalization self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_boundary_packet_row_normalization_obstruction()
    print(rec["status"])
    print(rec["certificate_sha256"])
