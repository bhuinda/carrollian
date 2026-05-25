from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_intrinsic_triple_ordering_clock/report.json"
INPUT_RELS = {
    "sector26_invariant_suite_report": (
        "data/invariants/d20/theorems/sector26_invariant_suite/report.json"
    ),
    "d20_strict_weak_order_sector26_clock_report": (
        "data/invariants/d20/theorems/d20_strict_weak_order_sector26_clock/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 intrinsic triple clock {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 intrinsic triple clock {key} hash mismatch")


def validate_d20_intrinsic_triple_ordering_clock() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_intrinsic_triple_ordering_clock")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 intrinsic triple ordering clock certificate")

    if rec.get("status") != "D20_INTRINSIC_TRIPLE_ORDERING_CLOCK_CERTIFIED":
        raise AssertionError("D20 intrinsic triple clock status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 intrinsic triple clock checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    triple = derived.get("intrinsic_triple_summary", {})
    if triple.get("basis_order") != ["R33", "K_mixed_S", "K_pure_Sminus"]:
        raise AssertionError("D20 intrinsic triple basis order mismatch")
    if triple.get("canonical_element_order") != ["R33", "K_mixed_S", "K_pure_Sminus"]:
        raise AssertionError("D20 intrinsic triple canonical order mismatch")
    if triple.get("matrix") != [[4, 0, 0], [0, 5, 1], [0, 1, 2]]:
        raise AssertionError("D20 intrinsic triple matrix mismatch")
    if triple.get("smith_normal_form_diagonal") != [1, 1, 36]:
        raise AssertionError("D20 intrinsic triple Smith diagonal mismatch")
    if triple.get("determinant") != 36 or triple.get("trace") != 11:
        raise AssertionError("D20 intrinsic triple determinant/trace mismatch")
    if triple.get("composite_block_basis_order") != ["K_mixed_S", "K_pure_Sminus"]:
        raise AssertionError("D20 intrinsic triple composite block order mismatch")
    if triple.get("composite_block_discriminant") != 13:
        raise AssertionError("D20 intrinsic triple discriminant mismatch")
    if triple.get("transport_preserving_permutation_count") != 1:
        raise AssertionError("D20 intrinsic triple permutation stabilizer mismatch")
    if triple.get("transport_preserving_permutations") != [[0, 1, 2]]:
        raise AssertionError("D20 intrinsic triple preserving permutation mismatch")

    elements = derived.get("intrinsic_element_records", [])
    if len(elements) != 3:
        raise AssertionError("D20 intrinsic triple element count mismatch")
    if [row.get("label") for row in elements] != ["R33", "K_mixed_S", "K_pure_Sminus"]:
        raise AssertionError("D20 intrinsic triple element label mismatch")
    if [row.get("self_transport") for row in elements] != [4, 5, 2]:
        raise AssertionError("D20 intrinsic triple self transport mismatch")
    if [row.get("offdiagonal_abs_sum") for row in elements] != [0, 1, 1]:
        raise AssertionError("D20 intrinsic triple offdiagonal mismatch")

    perm_records = derived.get("transport_permutation_records", [])
    if len(perm_records) != 6:
        raise AssertionError("D20 intrinsic triple permutation record count mismatch")
    if h_json(perm_records) != derived.get("transport_permutation_records_sha256"):
        raise AssertionError("D20 intrinsic triple permutation record hash mismatch")
    if sum(1 for row in perm_records if row.get("preserves_transport_matrix")) != 1:
        raise AssertionError("D20 intrinsic triple permutation rigidity mismatch")

    clock = derived.get("clock_summary", {})
    if clock.get("strict_weak_order_count") != 13:
        raise AssertionError("D20 intrinsic triple weak-order count mismatch")
    if clock.get("profile_counts") != {"1,1,1": 6, "1,2": 3, "2,1": 3, "3": 1}:
        raise AssertionError("D20 intrinsic triple weak-order profile mismatch")
    if clock.get("even_sector26_residue_image") != list(range(0, 26, 2)):
        raise AssertionError("D20 intrinsic triple even residue image mismatch")
    if clock.get("polarity_doubled_sector26_image") != list(range(26)):
        raise AssertionError("D20 intrinsic triple doubled residue image mismatch")
    if clock.get("matches_prior_weak_order_clock_line") is not True:
        raise AssertionError("D20 intrinsic triple line mismatch")
    if clock.get("matches_prior_weak_order_count") is not True:
        raise AssertionError("D20 intrinsic triple prior count mismatch")
    if clock.get("uses_external_placeholder_labels") is not False:
        raise AssertionError("D20 intrinsic triple placeholder guard mismatch")
    if clock.get("external_placeholders_replaced_by_intrinsic_labels") != {
        "a": "R33",
        "b": "K_mixed_S",
        "c": "K_pure_Sminus",
    }:
        raise AssertionError("D20 intrinsic triple replacement map mismatch")

    records = derived.get("intrinsic_order_records", [])
    if len(records) != 13:
        raise AssertionError("D20 intrinsic triple order record count mismatch")
    if h_json(records) != derived.get("intrinsic_order_records_sha256"):
        raise AssertionError("D20 intrinsic triple order record hash mismatch")
    for index, row in enumerate(records):
        if row.get("code_mod13") != index:
            raise AssertionError("D20 intrinsic triple order code mismatch")
        if row.get("sector26_even_residue") != (2 * index) % 26:
            raise AssertionError("D20 intrinsic triple residue mismatch")

    pairs = derived.get("anti_diagonal_pairs_mod26", [])
    if pairs != [[(2 * index) % 26, (-2 * index) % 26] for index in range(13)]:
        raise AssertionError("D20 intrinsic triple anti-diagonal pair mismatch")
    if h_json(pairs) != derived.get("anti_diagonal_pairs_sha256"):
        raise AssertionError("D20 intrinsic triple anti-diagonal hash mismatch")

    checks = rec.get("checks", {})
    required_true = [
        "intrinsic_triple_has_three_distinct_labels",
        "intrinsic_triple_is_expected_hidden_transport_basis",
        "hidden_transport_matrix_is_expected",
        "canonical_order_is_derived_from_transport_signatures",
        "transport_form_is_permutation_rigid",
        "composite_block_discriminant_is_13",
        "strict_weak_order_count_is_13",
        "profile_counts_are_1_3_3_6",
        "even_residue_image_is_order13_subgroup",
        "polarity_doubled_image_is_all_sector26",
        "intrinsic_line_matches_prior_clock_line",
        "placeholder_labels_are_removed",
    ]
    for key in required_true:
        if checks.get(key) is not True:
            raise AssertionError(f"D20 intrinsic triple check failed: {key}")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 intrinsic triple self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_intrinsic_triple_ordering_clock()
    print(rec["status"])
    print(rec["certificate_sha256"])
