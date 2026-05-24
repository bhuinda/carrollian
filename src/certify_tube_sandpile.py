from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_tube_sandpile_divisor_map() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/tube_sandpile_divisor_map/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("tube_sandpile_divisor_map")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 tube sandpile divisor-map certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_DIVISOR_MAP_CERTIFIED":
        raise AssertionError("tube sandpile divisor-map status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile divisor-map checks did not pass")

    derived = rec.get("derived", {})
    if int(derived.get("tree_count")) != 5_184_000:
        raise AssertionError("tube sandpile tree count mismatch")
    if int(derived.get("screen0_defect_mask")) != 640:
        raise AssertionError("tube sandpile defect mask mismatch")
    if derived.get("tube_grade_counts") != {"-1": 1024, "1": 1024}:
        raise AssertionError("tube sandpile grade-count mismatch")
    if int(derived.get("sandpile_class_count_in_mask_image")) != 1360:
        raise AssertionError("tube sandpile image class-count mismatch")
    if int(derived.get("sandpile_recurrent_class_count")) != 5_184_000:
        raise AssertionError("tube sandpile recurrent class-count mismatch")
    if derived.get("zero_class_masks") != [0]:
        raise AssertionError("tube sandpile zero class mismatch")
    if derived.get("class_multiplicity_histogram") != {
        "1": 1024,
        "2": 197,
        "3": 66,
        "4": 30,
        "5": 22,
        "6": 6,
        "7": 8,
        "9": 6,
        "56": 1,
    }:
        raise AssertionError("tube sandpile class multiplicity histogram mismatch")

    comparison = derived.get("tube_grade_vs_sandpile_class", {})
    if comparison.get("tube_grade_class_invariant") is not False:
        raise AssertionError("tube sandpile grade invariance mismatch")
    if int(comparison.get("pure_plus_class_count")) != 582:
        raise AssertionError("tube sandpile pure plus class count mismatch")
    if int(comparison.get("pure_minus_class_count")) != 624:
        raise AssertionError("tube sandpile pure minus class count mismatch")
    if int(comparison.get("mixed_class_count")) != 154:
        raise AssertionError("tube sandpile mixed class count mismatch")
    if int(comparison.get("mixed_class_mask_count")) != 576:
        raise AssertionError("tube sandpile mixed class mask count mismatch")

    adj = derived.get("adjugate_certificate", {})
    if adj.get("reduced_laplacian_shape") != [19, 19]:
        raise AssertionError("tube sandpile reduced Laplacian shape mismatch")
    if adj.get("adjugate_identity_holds") is not True:
        raise AssertionError("tube sandpile adjugate identity mismatch")

    rows = derived.get("mask_divisor_rows", [])
    if len(rows) != 2048:
        raise AssertionError("tube sandpile mask row count mismatch")
    if [int(row.get("mask")) for row in rows] != list(range(2048)):
        raise AssertionError("tube sandpile mask row order mismatch")
    if h_json(rows) != derived.get("mask_divisor_rows_sha256"):
        raise AssertionError("tube sandpile mask row hash mismatch")
    if any(int(row.get("divisor_degree")) != 0 for row in rows):
        raise AssertionError("tube sandpile divisor degree mismatch")
    if Counter(int(row.get("tube_grade")) for row in rows) != Counter({1: 1024, -1: 1024}):
        raise AssertionError("tube sandpile row grade-count mismatch")

    class_rows = derived.get("sandpile_class_rows", [])
    if len(class_rows) != 1360:
        raise AssertionError("tube sandpile class row count mismatch")
    if h_json(class_rows) != derived.get("sandpile_class_rows_sha256"):
        raise AssertionError("tube sandpile class row hash mismatch")
    if sum(1 for row in class_rows if row.get("tube_grade_invariant_on_class") is False) != 154:
        raise AssertionError("tube sandpile mixed class row count mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile divisor-map self hash mismatch")
    return rec
