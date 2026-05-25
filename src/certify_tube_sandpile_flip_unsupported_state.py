from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_unsupported_state_classification/report.json"
SUPPORT_PULLBACK_REL = "data/invariants/d20/theorems/tube_sandpile_flip_sector_support_pullback/report.json"
FOURIER_RESIDUE_REL = "data/invariants/d20/theorems/fourier_residue_screen/report.json"
FOURIER_A985_REL = "data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json"


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"tube sandpile flip unsupported-state {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"tube sandpile flip unsupported-state {key} hash mismatch")


def validate_tube_sandpile_flip_unsupported_state_classification() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("tube_sandpile_flip_unsupported_state_classification")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 tube sandpile flip unsupported-state certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_FLIP_UNSUPPORTED_STATE_CLASSIFIED":
        raise AssertionError("tube sandpile flip unsupported-state status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile flip unsupported-state checks did not pass")

    inputs = rec.get("inputs", {})
    _check_input_hash(inputs, "tube_sandpile_flip_sector_support_pullback_report", SUPPORT_PULLBACK_REL)
    _check_input_hash(inputs, "fourier_residue_screen_report", FOURIER_RESIDUE_REL)
    _check_input_hash(inputs, "fourier_a985_sector_character_candidates_report", FOURIER_A985_REL)

    derived = rec.get("derived", {})
    classification = derived.get("classification", {})
    if classification.get("unsupported_state") != "11":
        raise AssertionError("tube sandpile flip unsupported-state id mismatch")
    if classification.get("classification") != "residue_visible_but_outside_current_object_phase_image":
        raise AssertionError("tube sandpile flip unsupported-state classification mismatch")

    object_rows = derived.get("object_phase_rows", [])
    if len(object_rows) != 6:
        raise AssertionError("tube sandpile flip unsupported-state object row count mismatch")
    if h_json(object_rows) != derived.get("object_phase_rows_sha256"):
        raise AssertionError("tube sandpile flip unsupported-state object row hash mismatch")
    if derived.get("object_state_counts") != {"00": 2, "01": 2, "10": 2}:
        raise AssertionError("tube sandpile flip unsupported-state object count mismatch")
    if derived.get("object_labels_by_state", {}).get("11") != []:
        raise AssertionError("tube sandpile flip unsupported-state object labels mismatch")

    residue = derived.get("residue_screen12_counts", {})
    if residue.get("screen12_counts") != {"00": 512, "01": 512, "10": 512, "11": 512}:
        raise AssertionError("tube sandpile flip unsupported-state residue count mismatch")
    if any(split != {"0": 256, "1": 256} for split in residue.get("screen0_split_by_screen12", {}).values()):
        raise AssertionError("tube sandpile flip unsupported-state screen0 split mismatch")

    support_rows = derived.get("sector_support_state_rows", [])
    if len(support_rows) != 4:
        raise AssertionError("tube sandpile flip unsupported-state support row count mismatch")
    if h_json(support_rows) != derived.get("sector_support_state_rows_sha256"):
        raise AssertionError("tube sandpile flip unsupported-state support row hash mismatch")
    support_counts = {
        row["screen12_state"]: int(row["local_pre_idempotent_count"])
        for row in support_rows
    }
    if support_counts != {"00": 30, "01": 35, "10": 44, "11": 0}:
        raise AssertionError("tube sandpile flip unsupported-state support count mismatch")

    obstruction = derived.get("transition_obstruction_summary", {})
    if int(obstruction.get("missing_state_pair_count")) != 420:
        raise AssertionError("tube sandpile flip unsupported-state transition count mismatch")
    if int(obstruction.get("coset_count_using_missing_state")) != 56:
        raise AssertionError("tube sandpile flip unsupported-state coset count mismatch")

    profile = derived.get("support_pullback_profile_summary", {})
    if int(profile.get("class_count")) != 64 or profile.get("class_size_histogram") != {"1": 64}:
        raise AssertionError("tube sandpile flip unsupported-state profile mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile flip unsupported-state self hash mismatch")
    return rec
