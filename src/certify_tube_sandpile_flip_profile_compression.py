from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_profile_compression/report.json"
COSET_CLASSIFIER_REL = "data/invariants/d20/theorems/tube_sandpile_flip_coset_classifier/report.json"
PUBLIC_BOUNDARY_REL = "data/invariants/d20/theorems/public_boundary_graph_invariants/report.json"


def validate_tube_sandpile_flip_profile_compression() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("tube_sandpile_flip_profile_compression")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 tube sandpile flip-profile compression certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_FLIP_PROFILE_COMPRESSION_CERTIFIED":
        raise AssertionError("tube sandpile flip-profile compression status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile flip-profile compression checks did not pass")

    inputs = rec.get("inputs", {})
    if inputs.get("tube_sandpile_flip_coset_classifier_report", {}).get("path") != COSET_CLASSIFIER_REL:
        raise AssertionError("tube sandpile flip-profile coset input path mismatch")
    if inputs.get("public_boundary_graph_invariants_report", {}).get("path") != PUBLIC_BOUNDARY_REL:
        raise AssertionError("tube sandpile flip-profile public-boundary input path mismatch")
    if (ROOT / COSET_CLASSIFIER_REL).exists() and h_file(ROOT / COSET_CLASSIFIER_REL) != inputs[
        "tube_sandpile_flip_coset_classifier_report"
    ].get("sha256"):
        raise AssertionError("tube sandpile flip-profile coset input hash mismatch")
    if (ROOT / PUBLIC_BOUNDARY_REL).exists() and h_file(ROOT / PUBLIC_BOUNDARY_REL) != inputs[
        "public_boundary_graph_invariants_report"
    ].get("sha256"):
        raise AssertionError("tube sandpile flip-profile public-boundary input hash mismatch")

    derived = rec.get("derived", {})
    automorphism = derived.get("automorphism_compression", {})
    if int(automorphism.get("automorphism_count")) != 120:
        raise AssertionError("tube sandpile flip-profile automorphism count mismatch")
    if automorphism.get("flip_generator_preserver_ids") != [0]:
        raise AssertionError("tube sandpile flip-profile flip-preserver mismatch")
    if automorphism.get("five_cover_span_preserver_ids") != [0]:
        raise AssertionError("tube sandpile flip-profile cover-span preserver mismatch")
    if automorphism.get("five_cover_set_preserver_ids") != [0]:
        raise AssertionError("tube sandpile flip-profile cover-set preserver mismatch")
    if automorphism.get("flip_quotient_preserver_ids") != [0]:
        raise AssertionError("tube sandpile flip-profile quotient preserver mismatch")
    if automorphism.get("public_automorphism_compression_is_trivial") is not True:
        raise AssertionError("tube sandpile flip-profile automorphism compression mismatch")
    failure = automorphism.get("first_flip_set_failure", {})
    if int(failure.get("source_delta")) != 134 or int(failure.get("image_delta")) != 642:
        raise AssertionError("tube sandpile flip-profile first failure mismatch")

    pair = derived.get("pair_order_profile", {})
    if int(pair.get("class_count")) != 30:
        raise AssertionError("tube sandpile flip-profile pair-order class count mismatch")
    if pair.get("class_size_histogram") != {"1": 15, "2": 5, "3": 6, "5": 3, "6": 1}:
        raise AssertionError("tube sandpile flip-profile pair-order size histogram mismatch")

    fiber = derived.get("fiber_order_profile", {})
    if int(fiber.get("class_count")) != 15:
        raise AssertionError("tube sandpile flip-profile fiber-order class count mismatch")
    if fiber.get("class_size_histogram") != {"1": 10, "3": 1, "5": 1, "7": 1, "15": 1, "24": 1}:
        raise AssertionError("tube sandpile flip-profile fiber-order size histogram mismatch")

    combined = derived.get("combined_order_profile", {})
    if int(combined.get("class_count")) != 48:
        raise AssertionError("tube sandpile flip-profile combined-order class count mismatch")
    if combined.get("class_size_histogram") != {"1": 36, "2": 9, "3": 2, "4": 1}:
        raise AssertionError("tube sandpile flip-profile combined-order size histogram mismatch")
    combined_rows = combined.get("class_rows", [])
    if len(combined_rows) != 48:
        raise AssertionError("tube sandpile flip-profile combined-order row count mismatch")
    if h_json(combined_rows) != combined.get("class_rows_sha256"):
        raise AssertionError("tube sandpile flip-profile combined-order row hash mismatch")
    if sorted(idx for row in combined_rows for idx in row.get("coset_indices", [])) != list(range(64)):
        raise AssertionError("tube sandpile flip-profile combined-order partition mismatch")
    if not any(row.get("coset_indices") == [0] for row in combined_rows):
        raise AssertionError("tube sandpile flip-profile cover class mismatch")

    measured = derived.get("measured_profile", {})
    if int(measured.get("class_count")) != 58:
        raise AssertionError("tube sandpile flip-profile measured class count mismatch")
    measured_rows = measured.get("class_rows", [])
    if h_json(measured_rows) != measured.get("class_rows_sha256"):
        raise AssertionError("tube sandpile flip-profile measured row hash mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile flip-profile compression self hash mismatch")
    return rec
