from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_coset_classifier/report.json"
PRESENTATION_REL = "data/invariants/d20/theorems/tube_sandpile_flip_move_presentation/report.json"
KERNEL_FLIPS_REL = "data/invariants/d20/theorems/tube_sandpile_kernel_flips/report.json"
EXPECTED_COVER_DELTAS = [1560, 128, 512, 130, 421]


def validate_tube_sandpile_flip_coset_classifier() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("tube_sandpile_flip_coset_classifier")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 tube sandpile flip-coset classifier certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_FLIP_COSET_CLASSIFIER_CERTIFIED":
        raise AssertionError("tube sandpile flip-coset classifier status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile flip-coset classifier checks did not pass")

    inputs = rec.get("inputs", {})
    presentation_input = inputs.get("tube_sandpile_flip_move_presentation_report", {})
    kernel_input = inputs.get("tube_sandpile_kernel_flips_report", {})
    if presentation_input.get("path") != PRESENTATION_REL:
        raise AssertionError("tube sandpile flip-coset presentation path mismatch")
    if kernel_input.get("path") != KERNEL_FLIPS_REL:
        raise AssertionError("tube sandpile flip-coset kernel path mismatch")
    if (ROOT / PRESENTATION_REL).exists() and h_file(ROOT / PRESENTATION_REL) != presentation_input.get("sha256"):
        raise AssertionError("tube sandpile flip-coset presentation hash mismatch")
    if (ROOT / KERNEL_FLIPS_REL).exists() and h_file(ROOT / KERNEL_FLIPS_REL) != kernel_input.get("sha256"):
        raise AssertionError("tube sandpile flip-coset kernel hash mismatch")

    derived = rec.get("derived", {})
    if int(derived.get("residue_rank")) != 11:
        raise AssertionError("tube sandpile flip-coset residue rank mismatch")
    if int(derived.get("cover_rank")) != 5:
        raise AssertionError("tube sandpile flip-coset cover rank mismatch")
    if derived.get("cover_delta_masks") != EXPECTED_COVER_DELTAS:
        raise AssertionError("tube sandpile flip-coset cover delta mismatch")
    if int(derived.get("quotient_dimension")) != 6:
        raise AssertionError("tube sandpile flip-coset quotient dimension mismatch")
    if int(derived.get("coset_count")) != 64:
        raise AssertionError("tube sandpile flip-coset count mismatch")
    if int(derived.get("generator_delta_mass")) != 392:
        raise AssertionError("tube sandpile flip-coset generator mass mismatch")
    if int(derived.get("grade_flip_pair_mass")) != 1285:
        raise AssertionError("tube sandpile flip-coset pair mass mismatch")
    if int(derived.get("exact_divisor_fiber_union_count")) != 154:
        raise AssertionError("tube sandpile flip-coset fiber union mismatch")
    if int(derived.get("sandpile_class_union_count")) != 154:
        raise AssertionError("tube sandpile flip-coset class union mismatch")

    if derived.get("generator_delta_count_histogram") != {
        "1": 1,
        "2": 6,
        "3": 3,
        "4": 8,
        "5": 7,
        "6": 13,
        "7": 7,
        "8": 6,
        "9": 8,
        "10": 2,
        "11": 1,
        "12": 1,
        "13": 1,
    }:
        raise AssertionError("tube sandpile flip-coset generator histogram mismatch")
    if derived.get("pair_sandpile_class_order_histogram") != {
        "2": 2,
        "6": 7,
        "10": 1,
        "15": 31,
        "30": 1244,
    }:
        raise AssertionError("tube sandpile flip-coset sandpile order histogram mismatch")

    rows = derived.get("coset_rows", [])
    if len(rows) != 64:
        raise AssertionError("tube sandpile flip-coset row count mismatch")
    if h_json(rows) != derived.get("coset_rows_sha256"):
        raise AssertionError("tube sandpile flip-coset row hash mismatch")
    if [int(row.get("coset_index")) for row in rows] != list(range(64)):
        raise AssertionError("tube sandpile flip-coset index mismatch")

    generator_deltas = [
        int(delta)
        for row in rows
        for delta in row.get("generator_delta_masks", [])
    ]
    if len(generator_deltas) != 392 or len(set(generator_deltas)) != 392:
        raise AssertionError("tube sandpile flip-coset generator partition mismatch")
    if any(((delta & 640).bit_count() & 1) != 1 for delta in generator_deltas):
        raise AssertionError("tube sandpile flip-coset generator parity mismatch")

    pair_mass = sum(int(row.get("grade_flip_pair_count")) for row in rows)
    if pair_mass != 1285:
        raise AssertionError("tube sandpile flip-coset pair mass recompute mismatch")
    fiber_union = {
        int(idx)
        for row in rows
        for idx in row.get("exact_divisor_fiber_indices", [])
    }
    class_union = {
        int(idx)
        for row in rows
        for idx in row.get("sandpile_class_indices", [])
    }
    if len(fiber_union) != 154 or len(class_union) != 154:
        raise AssertionError("tube sandpile flip-coset support union mismatch")
    if any(
        int(row.get("exact_divisor_fiber_count")) != int(row.get("sandpile_class_count"))
        for row in rows
    ):
        raise AssertionError("tube sandpile flip-coset fiber/class count mismatch")

    cover_rows = [row for row in rows if row.get("in_five_cover_span") is True]
    if len(cover_rows) != 1:
        raise AssertionError("tube sandpile flip-coset cover row count mismatch")
    cover = cover_rows[0]
    if int(cover.get("coset_index")) != 0:
        raise AssertionError("tube sandpile flip-coset cover index mismatch")
    if cover.get("cover_move_deltas") != sorted(EXPECTED_COVER_DELTAS):
        raise AssertionError("tube sandpile flip-coset cover moves mismatch")
    if int(cover.get("generator_delta_count")) != 9:
        raise AssertionError("tube sandpile flip-coset cover generator count mismatch")
    if int(cover.get("grade_flip_pair_count")) != 271:
        raise AssertionError("tube sandpile flip-coset cover pair count mismatch")
    if int(cover.get("exact_divisor_fiber_count")) != 154:
        raise AssertionError("tube sandpile flip-coset cover fiber count mismatch")
    if any(row.get("cover_move_deltas") for row in rows if row.get("in_five_cover_span") is not True):
        raise AssertionError("tube sandpile flip-coset noncover move mismatch")

    pair_hist = Counter(int(row.get("grade_flip_pair_count")) for row in rows)
    if {str(key): int(value) for key, value in sorted(pair_hist.items())} != derived.get(
        "grade_flip_pair_count_histogram"
    ):
        raise AssertionError("tube sandpile flip-coset pair histogram mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile flip-coset classifier self hash mismatch")
    return rec
