from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_oriented_matroid_contour/report.json"

INPUT_RELS = {
    "d20_json": "d20.json",
    "d20_finite_contour_integration_report": (
        "data/invariants/d20/theorems/d20_finite_contour_integration/report.json"
    ),
    "public_boundary_graph_report": (
        "data/invariants/d20/theorems/public_boundary_graph_invariants/report.json"
    ),
    "sector33_height_coherent_transport_report": (
        "data/invariants/d20/theorems/sector33_height_coherent_transport/report.json"
    ),
    "sector33_unique_public_zero_support_report": (
        "data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json"
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
        raise AssertionError(f"D20 oriented matroid contour {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        if key == "d20_json":
            with path.open("r", encoding="utf-8") as f:
                d20 = json.load(f)
            if d20.get("status") == "D20_CERTIFIED":
                return
        raise AssertionError(f"D20 oriented matroid contour {key} hash mismatch")


def validate_d20_oriented_matroid_contour() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_oriented_matroid_contour")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 oriented matroid contour certificate")

    if rec.get("status") != "D20_ORIENTED_MATROID_CONTOUR_CERTIFIED":
        raise AssertionError("D20 oriented matroid contour status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 oriented matroid contour checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("contour_oriented_matroid_summary", {})
    if summary.get("edge_count") != 30 or summary.get("vertex_count") != 20:
        raise AssertionError("D20 oriented matroid contour ground-set size mismatch")
    if summary.get("rank") != 19 or summary.get("corank_cycle_rank") != 11:
        raise AssertionError("D20 oriented matroid contour rank mismatch")
    if summary.get("signed_circuit_count") != 1168:
        raise AssertionError("D20 oriented matroid contour circuit count mismatch")
    if summary.get("signed_cocircuit_count") != 12878:
        raise AssertionError("D20 oriented matroid contour cocircuit count mismatch")
    if summary.get("signed_circuit_length_histogram") != {
        "5": 12,
        "8": 30,
        "9": 20,
        "10": 36,
        "11": 120,
        "12": 100,
        "13": 60,
        "14": 180,
        "15": 180,
        "16": 90,
        "17": 180,
        "18": 130,
        "20": 30,
    }:
        raise AssertionError("D20 oriented matroid contour circuit histogram mismatch")
    if summary.get("signed_cocircuit_size_histogram") != {
        "3": 20,
        "4": 30,
        "5": 72,
        "6": 240,
        "7": 720,
        "8": 1620,
        "9": 2680,
        "10": 3336,
        "11": 2880,
        "12": 1280,
    }:
        raise AssertionError("D20 oriented matroid contour cocircuit histogram mismatch")

    gamma8 = derived.get("gamma8_tests", {})
    if gamma8.get("support") != [1, 2, 11, 21, 22]:
        raise AssertionError("D20 oriented matroid contour gamma8 support mismatch")
    if gamma8.get("support_is_signed_circuit") is not True:
        raise AssertionError("D20 oriented matroid contour gamma8 circuit mismatch")
    if gamma8.get("support_is_signed_cocircuit") is not False:
        raise AssertionError("D20 oriented matroid contour gamma8 cocircuit overclaim")
    if gamma8.get("support_is_hyperplane_zero_set") is not False:
        raise AssertionError("D20 oriented matroid contour gamma8 hyperplane overclaim")
    if gamma8.get("reported_signed_circuit_matches_graphic_circuit_up_to_global_sign") is not True:
        raise AssertionError("D20 oriented matroid contour gamma8 signed row mismatch")
    if gamma8.get("active_positive_extends_to_acyclic_tope") is not True:
        raise AssertionError("D20 oriented matroid contour gamma8 tope witness mismatch")
    if gamma8.get("cyclic_signed_circuit_partial_orientation_is_acyclic") is not False:
        raise AssertionError("D20 oriented matroid contour cyclic circuit tope overclaim")
    if gamma8.get("height_dot_active_positive_row") != 374784:
        raise AssertionError("D20 oriented matroid contour gamma8 height mismatch")

    pure = derived.get("pure_contour_symmetry_tests", {})
    if pure.get("public_graph_automorphism_order") != 120:
        raise AssertionError("D20 oriented matroid contour public automorphism mismatch")
    if pure.get("active_positive_signed_row_stabilizer_order") != 1:
        raise AssertionError("D20 oriented matroid contour gamma8 stabilizer mismatch")
    if pure.get("active_positive_signed_row_stabilizer_ids") != [0]:
        raise AssertionError("D20 oriented matroid contour gamma8 stabilizer id mismatch")
    if pure.get("active_support_only_stabilizer_order") != 10:
        raise AssertionError("D20 oriented matroid contour support stabilizer mismatch")
    if pure.get("cyclic_signed_circuit_stabilizer_order") != 5:
        raise AssertionError("D20 oriented matroid contour cyclic stabilizer mismatch")
    if pure.get("pure_contour_relaxation_is_c2") is not False:
        raise AssertionError("D20 oriented matroid contour pure C2 overclaim")

    augmented = derived.get("augmented_symmetry_cross_link", {})
    if augmented.get("hidden_split_stabilizer_order") != 2:
        raise AssertionError("D20 oriented matroid contour augmented C2 mismatch")
    if augmented.get("full_augmented_ledger_stabilizer_order") != 1:
        raise AssertionError("D20 oriented matroid contour augmented ledger stabilizer mismatch")

    sector33 = derived.get("sector33_tests", {})
    if sector33.get("sector33_is_ground_set_element_of_m_contour") is not False:
        raise AssertionError("D20 oriented matroid contour sector33 ground-set overclaim")
    if sector33.get("active_support_is_circuit_not_cocircuit") is not True:
        raise AssertionError("D20 oriented matroid contour sector33 active support mismatch")

    blocked = derived.get("blocked_or_deferred", {})
    if (
        blocked.get("sector33_cocircuit_or_hyperplane_in_m_contour")
        != "blocked_missing_sector33_ground_set_extension"
    ):
        raise AssertionError("D20 oriented matroid contour sector33 blocked marker mismatch")
    if blocked.get("pure_contour_gamma8_relaxation_c2") != "not_supported_by_pure_contour_matroid":
        raise AssertionError("D20 oriented matroid contour pure C2 blocked marker mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 oriented matroid contour self hash mismatch")
    return rec


if __name__ == "__main__":
    rec = validate_d20_oriented_matroid_contour()
    print(rec["status"])
    print(rec["certificate_sha256"])
