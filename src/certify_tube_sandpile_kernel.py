from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_tube_sandpile_kernel_flips() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/tube_sandpile_kernel_flips/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("tube_sandpile_kernel_flips")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 tube sandpile kernel-flips certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_KERNEL_FLIPS_CERTIFIED":
        raise AssertionError("tube sandpile kernel-flips status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile kernel-flips checks did not pass")

    derived = rec.get("derived", {})
    if int(derived.get("screen0_defect_mask")) != 640:
        raise AssertionError("tube sandpile kernel-flips defect mask mismatch")
    if int(derived.get("exact_divisor_fiber_count")) != 1368:
        raise AssertionError("tube sandpile exact-divisor fiber count mismatch")
    if int(derived.get("sandpile_class_count")) != 1360:
        raise AssertionError("tube sandpile class count mismatch")
    if derived.get("sandpile_class_exact_divisor_count_histogram") != {"1": 1352, "2": 8}:
        raise AssertionError("tube sandpile class/divisor histogram mismatch")
    if derived.get("exact_divisor_fiber_size_histogram") != {
        "1": 1040,
        "2": 189,
        "3": 66,
        "4": 30,
        "5": 22,
        "6": 6,
        "7": 8,
        "9": 6,
        "56": 1,
    }:
        raise AssertionError("tube sandpile exact-divisor fiber histogram mismatch")
    if int(derived.get("mixed_exact_divisor_fiber_count")) != 154:
        raise AssertionError("tube sandpile mixed exact-divisor fiber count mismatch")
    if int(derived.get("mixed_exact_divisor_mask_count")) != 576:
        raise AssertionError("tube sandpile mixed exact-divisor mask count mismatch")
    if int(derived.get("same_divisor_pair_count")) != 2801:
        raise AssertionError("tube sandpile same-divisor pair count mismatch")
    if int(derived.get("grade_flip_pair_count")) != 1285:
        raise AssertionError("tube sandpile grade-flip pair count mismatch")
    if int(derived.get("grade_preserving_pair_count")) != 1516:
        raise AssertionError("tube sandpile grade-preserving pair count mismatch")
    if int(derived.get("unique_grade_flip_delta_count")) != 392:
        raise AssertionError("tube sandpile unique flip delta count mismatch")
    if int(derived.get("unique_grade_preserving_delta_count")) != 365:
        raise AssertionError("tube sandpile unique preserving delta count mismatch")
    if derived.get("single_bit_flip_deltas") != [128, 512]:
        raise AssertionError("tube sandpile single-bit flip deltas mismatch")
    if int(derived.get("grade_flip_delta_rank_over_f2")) != 11:
        raise AssertionError("tube sandpile flip-delta rank mismatch")
    if derived.get("unique_flip_delta_weight_histogram") != {
        "1": 2,
        "2": 14,
        "3": 42,
        "4": 86,
        "5": 107,
        "6": 89,
        "7": 42,
        "8": 9,
        "9": 1,
    }:
        raise AssertionError("tube sandpile unique flip-delta weight histogram mismatch")
    if derived.get("grade_flip_pair_delta_weight_histogram") != {
        "1": 128,
        "2": 172,
        "3": 177,
        "4": 310,
        "5": 217,
        "6": 192,
        "7": 74,
        "8": 14,
        "9": 1,
    }:
        raise AssertionError("tube sandpile flip-pair weight histogram mismatch")

    divisor_rows = derived.get("divisor_fiber_rows", [])
    if len(divisor_rows) != 1368:
        raise AssertionError("tube sandpile divisor-fiber row count mismatch")
    if h_json(divisor_rows) != derived.get("divisor_fiber_rows_sha256"):
        raise AssertionError("tube sandpile divisor-fiber row hash mismatch")

    flip_pair_rows = derived.get("grade_flip_pair_rows", [])
    if len(flip_pair_rows) != 1285:
        raise AssertionError("tube sandpile flip-pair row count mismatch")
    if h_json(flip_pair_rows) != derived.get("grade_flip_pair_rows_sha256"):
        raise AssertionError("tube sandpile flip-pair row hash mismatch")
    if any(row.get("grade_a") == row.get("grade_b") for row in flip_pair_rows):
        raise AssertionError("tube sandpile flip-pair row grade mismatch")
    if any(((int(row.get("delta_mask")) & 640).bit_count() & 1) != 1 for row in flip_pair_rows):
        raise AssertionError("tube sandpile flip-pair parity mismatch")

    flip_delta_rows = derived.get("flip_delta_rows", [])
    if len(flip_delta_rows) != 392:
        raise AssertionError("tube sandpile flip-delta row count mismatch")
    if h_json(flip_delta_rows) != derived.get("flip_delta_rows_sha256"):
        raise AssertionError("tube sandpile flip-delta row hash mismatch")
    if any(int(row.get("screen0_parity")) != 1 for row in flip_delta_rows):
        raise AssertionError("tube sandpile flip-delta parity mismatch")

    preserve_delta_rows = derived.get("preserve_delta_rows", [])
    if len(preserve_delta_rows) != 365:
        raise AssertionError("tube sandpile preserving-delta row count mismatch")
    if h_json(preserve_delta_rows) != derived.get("preserve_delta_rows_sha256"):
        raise AssertionError("tube sandpile preserving-delta row hash mismatch")
    if any(int(row.get("screen0_parity")) != 0 for row in preserve_delta_rows):
        raise AssertionError("tube sandpile preserving-delta parity mismatch")

    witnesses = derived.get("canonical_flip_witness_rows", [])
    if len(witnesses) != 154:
        raise AssertionError("tube sandpile canonical witness row count mismatch")
    if h_json(witnesses) != derived.get("canonical_flip_witness_rows_sha256"):
        raise AssertionError("tube sandpile canonical witness row hash mismatch")

    cover = derived.get("small_flip_cover_rows", [])
    if [int(row.get("delta_mask")) for row in cover] != [1560, 128, 512, 130, 421]:
        raise AssertionError("tube sandpile five-cover delta mismatch")
    if sum(int(row.get("new_mixed_fiber_count")) for row in cover) != 154:
        raise AssertionError("tube sandpile five-cover count mismatch")
    if h_json(cover) != derived.get("small_flip_cover_rows_sha256"):
        raise AssertionError("tube sandpile five-cover row hash mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile kernel-flips self hash mismatch")
    return rec
