from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_sector_support_pullback/report.json"
SECTOR_REFINEMENT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_sector_refinement/report.json"
FOURIER_A985_REL = "data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json"
SECTOR_UNIQUE_REL = "data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json"


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"tube sandpile flip sector-support pullback {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"tube sandpile flip sector-support pullback {key} hash mismatch")


def validate_tube_sandpile_flip_sector_support_pullback() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("tube_sandpile_flip_sector_support_pullback")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 tube sandpile flip sector-support pullback certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_FLIP_SECTOR_SUPPORT_PULLBACK_CERTIFIED":
        raise AssertionError("tube sandpile flip sector-support pullback status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile flip sector-support pullback checks did not pass")

    inputs = rec.get("inputs", {})
    _check_input_hash(inputs, "tube_sandpile_flip_sector_refinement_report", SECTOR_REFINEMENT_REL)
    _check_input_hash(inputs, "fourier_a985_sector_character_candidates_report", FOURIER_A985_REL)
    _check_input_hash(inputs, "sector33_unique_public_zero_support_report", SECTOR_UNIQUE_REL)

    derived = rec.get("derived", {})
    if derived.get("supported_screen12_states") != ["00", "01", "10"]:
        raise AssertionError("tube sandpile flip sector-support pullback supported-state mismatch")
    if derived.get("missing_screen12_states") != ["11"]:
        raise AssertionError("tube sandpile flip sector-support pullback missing-state mismatch")

    sector_rows = derived.get("sector_state_rows", [])
    if len(sector_rows) != 39:
        raise AssertionError("tube sandpile flip sector-support pullback sector row count mismatch")
    if h_json(sector_rows) != derived.get("sector_state_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-support pullback sector row hash mismatch")

    cell_rows = derived.get("state_cell_rows", [])
    if [row.get("screen12_state") for row in cell_rows] != ["00", "01", "10", "11"]:
        raise AssertionError("tube sandpile flip sector-support pullback state-cell order mismatch")
    if h_json(cell_rows) != derived.get("state_cell_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-support pullback state-cell hash mismatch")
    piece_counts = {
        row["screen12_state"]: int(row["local_pre_idempotent_count"])
        for row in cell_rows
    }
    if piece_counts != {"00": 30, "01": 35, "10": 44, "11": 0}:
        raise AssertionError("tube sandpile flip sector-support pullback piece count mismatch")
    touch_counts = {
        row["screen12_state"]: int(row["sector_touch_count"])
        for row in cell_rows
    }
    if touch_counts != {"00": 23, "01": 27, "10": 32, "11": 0}:
        raise AssertionError("tube sandpile flip sector-support pullback touch count mismatch")
    homogeneous_counts = {
        row["screen12_state"]: int(row["homogeneous_sector_count"])
        for row in cell_rows
    }
    if homogeneous_counts != {"00": 0, "01": 4, "10": 5, "11": 0}:
        raise AssertionError("tube sandpile flip sector-support pullback homogeneous count mismatch")
    if not any(row["screen12_state"] == "01" and row["public_zero_sector_ids"] == [33] for row in cell_rows):
        raise AssertionError("tube sandpile flip sector-support pullback public-zero cell mismatch")

    obstruction = derived.get("transition_obstruction_summary", {})
    if int(obstruction.get("total_pair_count")) != 1285:
        raise AssertionError("tube sandpile flip sector-support pullback total pair count mismatch")
    if int(obstruction.get("support_admissible_pair_count")) != 865:
        raise AssertionError("tube sandpile flip sector-support pullback support pair count mismatch")
    if int(obstruction.get("missing_state_pair_count")) != 420:
        raise AssertionError("tube sandpile flip sector-support pullback missing pair count mismatch")
    if int(obstruction.get("coset_count_using_missing_state")) != 56:
        raise AssertionError("tube sandpile flip sector-support pullback missing coset count mismatch")
    if obstruction.get("endpoint_state_multiplicity") != {
        "00": 795,
        "01": 592,
        "10": 686,
        "11": 497,
    }:
        raise AssertionError("tube sandpile flip sector-support pullback endpoint histogram mismatch")

    pullback_rows = derived.get("coset_support_pullback_rows", [])
    if len(pullback_rows) != 64:
        raise AssertionError("tube sandpile flip sector-support pullback coset row count mismatch")
    if h_json(pullback_rows) != derived.get("coset_support_pullback_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-support pullback coset row hash mismatch")
    if [int(row.get("coset_index")) for row in pullback_rows] != list(range(64)):
        raise AssertionError("tube sandpile flip sector-support pullback coset row order mismatch")

    profile = derived.get("support_pullback_profile", {})
    if int(profile.get("class_count")) != 64:
        raise AssertionError("tube sandpile flip sector-support pullback class count mismatch")
    if profile.get("class_size_histogram") != {"1": 64}:
        raise AssertionError("tube sandpile flip sector-support pullback class histogram mismatch")
    class_rows = profile.get("class_rows", [])
    if sorted(idx for row in class_rows for idx in row.get("coset_indices", [])) != list(range(64)):
        raise AssertionError("tube sandpile flip sector-support pullback partition mismatch")
    if h_json(class_rows) != profile.get("class_rows_sha256"):
        raise AssertionError("tube sandpile flip sector-support pullback class row hash mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile flip sector-support pullback self hash mismatch")
    return rec
