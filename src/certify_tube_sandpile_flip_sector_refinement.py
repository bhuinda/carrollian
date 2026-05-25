from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_sector_refinement/report.json"
PROFILE_REL = "data/invariants/d20/theorems/tube_sandpile_flip_profile_compression/report.json"
COSET_REL = "data/invariants/d20/theorems/tube_sandpile_flip_coset_classifier/report.json"
PRESENTATION_REL = "data/invariants/d20/theorems/tube_sandpile_flip_move_presentation/report.json"
KERNEL_REL = "data/invariants/d20/theorems/tube_sandpile_kernel_flips/report.json"
FOURIER_RESIDUE_REL = "data/invariants/d20/theorems/fourier_residue_screen/report.json"
FOURIER_A985_REL = "data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json"


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"tube sandpile flip sector-refinement {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"tube sandpile flip sector-refinement {key} hash mismatch")


def _partition_is_complete(rows: list[dict[str, Any]]) -> bool:
    return sorted(idx for row in rows for idx in row.get("coset_indices", [])) == list(range(64))


def validate_tube_sandpile_flip_sector_refinement() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("tube_sandpile_flip_sector_refinement")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 tube sandpile flip sector-refinement certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_FLIP_SECTOR_REFINEMENT_CERTIFIED":
        raise AssertionError("tube sandpile flip sector-refinement status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile flip sector-refinement checks did not pass")

    inputs = rec.get("inputs", {})
    _check_input_hash(inputs, "tube_sandpile_flip_profile_compression_report", PROFILE_REL)
    _check_input_hash(inputs, "tube_sandpile_flip_coset_classifier_report", COSET_REL)
    _check_input_hash(inputs, "tube_sandpile_flip_move_presentation_report", PRESENTATION_REL)
    _check_input_hash(inputs, "tube_sandpile_kernel_flips_report", KERNEL_REL)
    _check_input_hash(inputs, "fourier_residue_screen_report", FOURIER_RESIDUE_REL)
    _check_input_hash(inputs, "fourier_a985_sector_character_candidates_report", FOURIER_A985_REL)

    derived = rec.get("derived", {})
    screen_summary = derived.get("screen_summary", {})
    if screen_summary.get("defect_vectors") != [640, 260, 96]:
        raise AssertionError("tube sandpile flip sector-refinement defect-vector mismatch")
    if screen_summary.get("screen_ids") != [
        "signed_turn_screen_0",
        "signed_turn_screen_1",
        "signed_turn_screen_2",
    ]:
        raise AssertionError("tube sandpile flip sector-refinement screen order mismatch")
    candidate_rows = screen_summary.get("candidate_rows", [])
    if len(candidate_rows) != 3 or h_json(candidate_rows) != screen_summary.get("candidate_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-refinement screen row hash mismatch")

    combined = derived.get("combined_order_profile", {})
    if int(combined.get("source_class_count")) != 48:
        raise AssertionError("tube sandpile flip sector-refinement combined class count mismatch")
    if combined.get("source_class_size_histogram") != {"1": 36, "2": 9, "3": 2, "4": 1}:
        raise AssertionError("tube sandpile flip sector-refinement combined histogram mismatch")
    if int(combined.get("non_singleton_class_count")) != 12:
        raise AssertionError("tube sandpile flip sector-refinement non-singleton count mismatch")
    if int(combined.get("non_singleton_coset_mass")) != 28:
        raise AssertionError("tube sandpile flip sector-refinement non-singleton mass mismatch")

    full_profile = derived.get("screen_pair_transition_profile", {})
    if int(full_profile.get("class_count")) != 64:
        raise AssertionError("tube sandpile flip sector-refinement full transition count mismatch")
    if full_profile.get("class_size_histogram") != {"1": 64}:
        raise AssertionError("tube sandpile flip sector-refinement full transition histogram mismatch")
    full_rows = full_profile.get("class_rows", [])
    if not _partition_is_complete(full_rows):
        raise AssertionError("tube sandpile flip sector-refinement full transition partition mismatch")
    if h_json(full_rows) != full_profile.get("class_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-refinement full transition row hash mismatch")

    screen12_profile = derived.get("screen12_pair_transition_profile", {})
    if int(screen12_profile.get("class_count")) != 64:
        raise AssertionError("tube sandpile flip sector-refinement screen12 transition count mismatch")
    if screen12_profile.get("class_size_histogram") != {"1": 64}:
        raise AssertionError("tube sandpile flip sector-refinement screen12 transition histogram mismatch")
    screen12_rows = screen12_profile.get("class_rows", [])
    if not _partition_is_complete(screen12_rows):
        raise AssertionError("tube sandpile flip sector-refinement screen12 partition mismatch")
    if h_json(screen12_rows) != screen12_profile.get("class_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-refinement screen12 row hash mismatch")

    endpoint_profile = derived.get("screen_endpoint_profile", {})
    if int(endpoint_profile.get("class_count")) != 64:
        raise AssertionError("tube sandpile flip sector-refinement endpoint count mismatch")
    if endpoint_profile.get("class_size_histogram") != {"1": 64}:
        raise AssertionError("tube sandpile flip sector-refinement endpoint histogram mismatch")
    endpoint_rows = endpoint_profile.get("class_rows", [])
    if h_json(endpoint_rows) != endpoint_profile.get("class_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-refinement endpoint row hash mismatch")

    coset_rows = derived.get("coset_screen_refinement_rows", [])
    if len(coset_rows) != 64:
        raise AssertionError("tube sandpile flip sector-refinement coset row count mismatch")
    if h_json(coset_rows) != derived.get("coset_screen_refinement_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-refinement coset row hash mismatch")
    if [int(row.get("coset_index")) for row in coset_rows] != list(range(64)):
        raise AssertionError("tube sandpile flip sector-refinement coset row order mismatch")
    if not all(
        signature.startswith("1")
        for row in coset_rows
        for signature in row.get("pair_delta_screen_signature_histogram", {})
    ):
        raise AssertionError("tube sandpile flip sector-refinement delta signature mismatch")

    split = derived.get("combined_order_split_rows", [])
    if len(split) != 12:
        raise AssertionError("tube sandpile flip sector-refinement split row count mismatch")
    if h_json(split) != derived.get("combined_order_split_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-refinement split row hash mismatch")
    if not all(row.get("singleton_after_screen12_refinement") is True for row in split):
        raise AssertionError("tube sandpile flip sector-refinement split singleton mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile flip sector-refinement self hash mismatch")
    return rec
