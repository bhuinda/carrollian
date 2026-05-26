from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_strict_weak_order_sector26_clock/report.json"
INPUT_RELS = {
    "d20_contour_charge_pairing_snf_report": (
        "data/invariants/d20/theorems/d20_contour_charge_pairing_snf/report.json"
    ),
    "hidden_split_augmented_ledger_stabilizer_report": (
        "data/invariants/d20/theorems/hidden_split_augmented_ledger_stabilizer/report.json"
    ),
    "sourced_balance_label_relaxed_orbit_quotient_report": (
        "data/invariants/d20/theorems/full_exposure_zero_pair_sourced_balance_label_relaxed_orbit_quotient/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 strict weak order clock {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 strict weak order clock {key} hash mismatch")


def validate_d20_strict_weak_order_sector26_clock() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_strict_weak_order_sector26_clock")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 strict weak order sector-26 clock certificate")

    if rec.get("status") != "D20_STRICT_WEAK_ORDER_SECTOR26_CLOCK_CERTIFIED":
        raise AssertionError("D20 strict weak order clock status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 strict weak order clock checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("weak_order_summary", {})
    if summary.get("strict_weak_order_count") != 13:
        raise AssertionError("D20 strict weak order count mismatch")
    if summary.get("profile_counts") != {"1,1,1": 6, "1,2": 3, "2,1": 3, "3": 1}:
        raise AssertionError("D20 strict weak order profile mismatch")
    if summary.get("even_sector26_residue_image") != list(range(0, 26, 2)):
        raise AssertionError("D20 strict weak order even residue image mismatch")
    if summary.get("polarity_doubled_sector26_image") != list(range(26)):
        raise AssertionError("D20 strict weak order doubled residue image mismatch")
    if summary.get("matches_contour_charge_pairing_order13_line") is not True:
        raise AssertionError("D20 strict weak order line hash mismatch")
    if summary.get("relabel_orbit_count") != 4:
        raise AssertionError("D20 strict weak order relabel orbit count mismatch")
    if summary.get("relabel_orbit_size_histogram") != {"1": 1, "3": 2, "6": 1}:
        raise AssertionError("D20 strict weak order relabel orbit histogram mismatch")
    if summary.get("pointwise_clock_preserving_relabelling_count") != 1:
        raise AssertionError("D20 strict weak order pointwise relabel mismatch")
    if summary.get("affine_mod13_relabelling_count") != 1:
        raise AssertionError("D20 strict weak order affine relabel mismatch")

    records = derived.get("weak_order_records", [])
    if len(records) != 13:
        raise AssertionError("D20 strict weak order record count mismatch")
    if h_json(records) != derived.get("weak_order_records_sha256"):
        raise AssertionError("D20 strict weak order record hash mismatch")
    for index, row in enumerate(records):
        if row.get("code_mod13") != index:
            raise AssertionError("D20 strict weak order code mismatch")
        if row.get("sector26_even_residue") != (2 * index) % 26:
            raise AssertionError("D20 strict weak order residue mismatch")
        if row.get("sector26_polarity_residues", {}).get("positive") != (2 * index) % 26:
            raise AssertionError("D20 strict weak order positive residue mismatch")
        if row.get("sector26_polarity_residues", {}).get("negative") != (2 * index + 1) % 26:
            raise AssertionError("D20 strict weak order negative residue mismatch")

    pairs = derived.get("anti_diagonal_pairs_mod26", [])
    if pairs != [[(2 * index) % 26, (-2 * index) % 26] for index in range(13)]:
        raise AssertionError("D20 strict weak order anti-diagonal pair mismatch")
    if h_json(pairs) != derived.get("anti_diagonal_pairs_sha256"):
        raise AssertionError("D20 strict weak order anti-diagonal hash mismatch")

    relabel_records = derived.get("relabel_records", [])
    if len(relabel_records) != 6:
        raise AssertionError("D20 strict weak order relabel record count mismatch")
    if h_json(relabel_records) != derived.get("relabel_records_sha256"):
        raise AssertionError("D20 strict weak order relabel hash mismatch")
    if sum(1 for row in relabel_records if row.get("pointwise_preserves_clock_codes")) != 1:
        raise AssertionError("D20 strict weak order relabel pointwise count mismatch")
    if sum(1 for row in relabel_records if row.get("affine_mod13_clock_action") is not None) != 1:
        raise AssertionError("D20 strict weak order relabel affine count mismatch")
    if any(row.get("preserves_even_residue_set") is not True for row in relabel_records):
        raise AssertionError("D20 strict weak order relabel set preservation mismatch")

    sym = derived.get("d20_symmetry_test", {})
    if sym.get("full_augmented_ledger_preserving_automorphism_ids") != [0]:
        raise AssertionError("D20 strict weak order full-ledger automorphism mismatch")
    if sym.get("full_augmented_ledger_stabilizer_order") != 1:
        raise AssertionError("D20 strict weak order full-ledger stabilizer mismatch")
    if sym.get("hidden_split_c2_order") != 2:
        raise AssertionError("D20 strict weak order hidden C2 order mismatch")
    if sym.get("hidden_split_nonidentity_automorphism_id") != 1:
        raise AssertionError("D20 strict weak order hidden C2 nonidentity mismatch")
    if sym.get("hidden_split_nonidentity_preserves_corrected_clock_mod26") is not True:
        raise AssertionError("D20 strict weak order corrected clock preservation mismatch")
    if sym.get("hidden_split_nonidentity_preserves_sector26_counterterm_vector_mod26") is not False:
        raise AssertionError("D20 strict weak order counterterm preservation mismatch")
    if sym.get("hidden_split_nonidentity_preserves_normalized_optical_clock_mod26") is not False:
        raise AssertionError("D20 strict weak order optical clock preservation mismatch")
    if sym.get("sector26_clock_must_be_forgotten_for_hidden_c2_quotient") is not True:
        raise AssertionError("D20 strict weak order C2 clock forget mismatch")
    if sym.get("sector26_counterterm_must_be_forgotten_for_hidden_c2_quotient") is not True:
        raise AssertionError("D20 strict weak order C2 counterterm forget mismatch")
    if sym.get("public_automorphism_count") != 120:
        raise AssertionError("D20 strict weak order public automorphism count mismatch")
    if sym.get("full_public_action_requires_forgetting_source_anchor") is not True:
        raise AssertionError("D20 strict weak order public action guard mismatch")

    checks = rec.get("checks", {})
    required_true = [
        "strict_weak_order_count_is_13",
        "profile_counts_are_1_3_3_6",
        "even_residue_image_is_order13_subgroup",
        "polarity_doubled_image_is_all_sector26",
        "weak_order_line_matches_contour_charge_pairing_line",
        "natural_relabelling_orbits_are_1_3_3_6",
        "only_identity_relabelling_pointwise_preserves_clock",
        "no_nontrivial_relabelling_is_affine_mod13_for_this_clock",
        "full_augmented_d20_ledger_stabilizer_is_identity",
        "hidden_c2_does_not_preserve_sector26_clock_map",
        "sector26_clock_is_not_c2_quotient_coherent",
        "full_public_action_requires_forgetting_source_anchor",
    ]
    for key in required_true:
        if checks.get(key) is not True:
            raise AssertionError(f"D20 strict weak order check failed: {key}")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 strict weak order self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_strict_weak_order_sector26_clock()
    print(rec["status"])
    print(rec["certificate_sha256"])
