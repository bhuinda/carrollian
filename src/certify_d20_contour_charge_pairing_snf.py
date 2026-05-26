from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_contour_charge_pairing_snf/report.json"
INPUT_RELS = {
    "d20_finite_contour_integration_report": (
        "data/invariants/d20/theorems/d20_finite_contour_integration/report.json"
    ),
    "full_exposure_zero_pair_propagator_charge_kernel_report": (
        "data/invariants/d20/theorems/full_exposure_zero_pair_propagator_charge_kernel/report.json"
    ),
    "d20_contour_sector_packet_prime_alignment_report": (
        "data/invariants/d20/theorems/d20_contour_sector_packet_prime_alignment/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 contour charge pairing {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 contour charge pairing {key} hash mismatch")


def validate_d20_contour_charge_pairing_snf() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_contour_charge_pairing_snf")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 contour charge pairing certificate")

    if rec.get("status") != "D20_CONTOUR_CHARGE_PAIRING_SNF_CERTIFIED":
        raise AssertionError("D20 contour charge pairing status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 contour charge pairing checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("pairing_summary", {})
    if summary.get("residue_line_length") != 11 or summary.get("residue_line_gcd") != 1:
        raise AssertionError("D20 contour charge pairing residue line mismatch")
    if summary.get("charge_doublets_centered", {}).get("sum") != [4, -4]:
        raise AssertionError("D20 contour charge pairing sum doublet mismatch")
    if summary.get("charge_doublets_centered", {}).get("delta") != [8, -8]:
        raise AssertionError("D20 contour charge pairing delta doublet mismatch")
    if summary.get("finite_row_subgroup_order") != 13:
        raise AssertionError("D20 contour charge pairing row subgroup order mismatch")
    if summary.get("finite_ambient_group") != "(Z/26)^2":
        raise AssertionError("D20 contour charge pairing ambient group mismatch")
    if summary.get("finite_ambient_order") != 676:
        raise AssertionError("D20 contour charge pairing ambient order mismatch")
    if summary.get("finite_quotient_smith_diagonal") != [2, 26]:
        raise AssertionError("D20 contour charge pairing quotient Smith diagonal mismatch")
    if summary.get("finite_quotient_group") != "Z/2 x Z/26":
        raise AssertionError("D20 contour charge pairing quotient group mismatch")
    if summary.get("finite_quotient_order") != 52:
        raise AssertionError("D20 contour charge pairing quotient order mismatch")
    if summary.get("finite_quotient_order_factorization") != {"2": 2, "13": 1}:
        raise AssertionError("D20 contour charge pairing quotient factorization mismatch")

    primitive = derived.get("primitive_residue_vector", [])
    mod26 = derived.get("mod26_residue_vector", [])
    if len(primitive) != 11 or len(mod26) != 11:
        raise AssertionError("D20 contour charge pairing vector length mismatch")
    if [int(value) % 26 for value in primitive] != mod26:
        raise AssertionError("D20 contour charge pairing mod-26 reduction mismatch")

    raw_rows = derived.get("raw_pairing_rows", {})
    residue_rows = derived.get("residue_pairing_rows_mod26", {})
    if h_json(raw_rows) != derived.get("raw_pairing_rows_sha256"):
        raise AssertionError("D20 contour charge pairing raw row hash mismatch")
    if h_json(residue_rows) != derived.get("residue_pairing_rows_mod26_sha256"):
        raise AssertionError("D20 contour charge pairing residue row hash mismatch")
    for key in ["sum", "delta", "packet_clock_0", "packet_clock_1"]:
        if len(raw_rows.get(key, [])) != 11:
            raise AssertionError(f"D20 contour charge pairing raw row count mismatch: {key}")
        if len(residue_rows.get(key, [])) != 11:
            raise AssertionError(f"D20 contour charge pairing residue row count mismatch: {key}")

    raw_snf = derived.get("raw_pairing_smith_forms", {})
    if raw_snf.get("sum", {}).get("diagonal") != [4]:
        raise AssertionError("D20 contour charge pairing raw sum Smith mismatch")
    if raw_snf.get("delta", {}).get("diagonal") != [8]:
        raise AssertionError("D20 contour charge pairing raw delta Smith mismatch")

    lift_snf = derived.get("residue_lift_smith_forms", {})
    quotient_snf = derived.get("finite_quotient_smith_forms", {})
    for key in ["sum", "delta", "packet_clock_0", "packet_clock_1"]:
        if lift_snf.get(key, {}).get("diagonal") != [2, 26]:
            raise AssertionError(f"D20 contour charge pairing residue-lift Smith mismatch: {key}")
        if quotient_snf.get(key, {}).get("diagonal") != [2, 26]:
            raise AssertionError(f"D20 contour charge pairing quotient Smith mismatch: {key}")
        if quotient_snf.get(key, {}).get("quotient_order") != 52:
            raise AssertionError(f"D20 contour charge pairing quotient order mismatch: {key}")
        if quotient_snf.get(key, {}).get("quotient_group") != "Z/2 x Z/26":
            raise AssertionError(f"D20 contour charge pairing quotient group mismatch: {key}")

    subgroup_sizes = derived.get("row_subgroup_sizes", {})
    if subgroup_sizes != {
        "delta": 13,
        "packet_clock_0": 13,
        "packet_clock_1": 13,
        "sum": 13,
    }:
        raise AssertionError("D20 contour charge pairing subgroup size mismatch")

    weak = derived.get("weak_order_summary", {})
    if weak.get("strict_weak_order_count") != 13:
        raise AssertionError("D20 contour charge pairing weak-order count mismatch")
    if weak.get("raw_pairwise_ternary_comparison_count") != 27:
        raise AssertionError("D20 contour charge pairing ternary count mismatch")
    if weak.get("transitive_ternary_comparison_count") != 13:
        raise AssertionError("D20 contour charge pairing transitive count mismatch")
    if weak.get("polarity_doubled_count") != 26:
        raise AssertionError("D20 contour charge pairing polarity count mismatch")
    if weak.get("ordered_partition_profile_counts") != {
        "1,1,1": 6,
        "1,2": 3,
        "2,1": 3,
        "3": 1,
    }:
        raise AssertionError("D20 contour charge pairing weak-order profile mismatch")

    checks = rec.get("checks", {})
    required_true = [
        "residue_line_is_11_dimensional_and_primitive",
        "sector26_charge_doublet_is_plus_minus",
        "all_pairing_rows_generate_same_order_13_line",
        "finite_quotient_smith_form_is_2_26",
        "finite_quotient_order_is_52",
        "strict_weak_orders_on_three_elements_count_13",
        "strict_weak_order_polarity_double_is_26",
        "weak_order_count_is_comparison_not_source_claim",
    ]
    for key in required_true:
        if checks.get(key) is not True:
            raise AssertionError(f"D20 contour charge pairing check failed: {key}")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 contour charge pairing self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_contour_charge_pairing_snf()
    print(rec["status"])
    print(rec["certificate_sha256"])
