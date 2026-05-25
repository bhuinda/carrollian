from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_finite_contour_integration/report.json"
D20_REL = "d20.json"
EXPECTED_PRIMITIVE_RESIDUE = [-106, -94, 12, 20, -40, -159, -174, -180, -40, -67, -81]
EXPECTED_MOD26_RESIDUE = [24, 10, 12, 20, 12, 23, 8, 2, 12, 11, 23]


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 finite contour integration {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 finite contour integration {key} hash mismatch")


def validate_d20_finite_contour_integration() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_finite_contour_integration")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 finite contour integration certificate")

    if rec.get("status") != "D20_FINITE_CONTOUR_INTEGRATION_TEST_PASS":
        raise AssertionError("D20 finite contour integration status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 finite contour integration checks did not pass")

    _check_input_hash(rec.get("inputs", {}), "d20_json", D20_REL)

    derived = rec.get("derived", {})
    summary = derived.get("contour_summary", {})
    if summary.get("vertex_count") != 20 or summary.get("edge_count") != 30:
        raise AssertionError("D20 finite contour integration graph size mismatch")
    if summary.get("rank_incidence_over_Q") != 19:
        raise AssertionError("D20 finite contour integration rational incidence rank mismatch")
    if summary.get("rank_incidence_over_F2") != 19:
        raise AssertionError("D20 finite contour integration mod-2 incidence rank mismatch")
    if summary.get("cycle_rank_expected") != 11:
        raise AssertionError("D20 finite contour integration cycle rank mismatch")
    if summary.get("primitive_cycle_count") != 11:
        raise AssertionError("D20 finite contour integration primitive cycle count mismatch")
    if summary.get("primitive_cycle_rank_over_F2") != 11:
        raise AssertionError("D20 finite contour integration primitive cycle rank mismatch")
    if summary.get("boundary_defects_over_F2") != 0:
        raise AssertionError("D20 finite contour integration boundary defect mismatch")

    positive = derived.get("positive_contour_action", {})
    if positive.get("all_match_stored_optical_actions") is not True:
        raise AssertionError("D20 finite contour integration positive action mismatch")
    if positive.get("W_D6_order") != 23040:
        raise AssertionError("D20 finite contour integration W(D6) mismatch")

    signed = derived.get("signed_contour_residue", {})
    if signed.get("gcd_signed_integrals") != 3072 or signed.get("normalization") != 3072:
        raise AssertionError("D20 finite contour integration signed gcd mismatch")
    if signed.get("primitive_residue_vector") != EXPECTED_PRIMITIVE_RESIDUE:
        raise AssertionError("D20 finite contour integration primitive residue mismatch")
    if signed.get("primitive_residue_vector_gcd") != 1:
        raise AssertionError("D20 finite contour integration primitive gcd mismatch")
    if signed.get("mod26_residue_vector") != EXPECTED_MOD26_RESIDUE:
        raise AssertionError("D20 finite contour integration mod-26 residue mismatch")
    if signed.get("zero_signed_integral_cycles") != []:
        raise AssertionError("D20 finite contour integration zero-residue cycle mismatch")

    exact = derived.get("exactness_obstruction", {})
    if exact.get("rank_gradient_over_Q") != 19:
        raise AssertionError("D20 finite contour integration gradient rank mismatch")
    if exact.get("rank_augmented_over_Q") != 20:
        raise AssertionError("D20 finite contour integration augmented rank mismatch")
    if exact.get("exact_1_form_over_Q") is not False:
        raise AssertionError("D20 finite contour integration exactness overclaim")

    cycle_rows = derived.get("cycle_rows", [])
    if len(cycle_rows) != 11:
        raise AssertionError("D20 finite contour integration cycle row count mismatch")
    if h_json(cycle_rows) != derived.get("cycle_rows_sha256"):
        raise AssertionError("D20 finite contour integration cycle row hash mismatch")
    if any(row.get("positive_matches_stored") is not True for row in cycle_rows):
        raise AssertionError("D20 finite contour integration cycle positive mismatch")
    if any(row.get("entropy_proxy_matches_stored") is not True for row in cycle_rows):
        raise AssertionError("D20 finite contour integration entropy mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 finite contour integration self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_finite_contour_integration()
    print(rec["status"])
    print(rec["certificate_sha256"])
