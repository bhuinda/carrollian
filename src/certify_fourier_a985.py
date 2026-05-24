from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


EXPECTED_COUNTS = {
    "signed_turn_screen_0": {"homogeneous": 16, "mixed": 23},
    "signed_turn_screen_1": {"homogeneous": 12, "mixed": 27},
    "signed_turn_screen_2": {"homogeneous": 16, "mixed": 23},
}


def validate_fourier_a985_sector_character_candidates() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("fourier_a985_sector_character_candidates")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 Fourier A985 sector-character candidate certificate")

    if rec.get("status") != "D20_FOURIER_A985_SECTOR_CHARACTER_CANDIDATES_EVALUATED":
        raise AssertionError("Fourier A985 sector-character candidate status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("Fourier A985 sector-character candidate checks did not pass")

    derived = rec.get("derived", {})
    if int(derived.get("sector_count")) != 39:
        raise AssertionError("Fourier A985 sector count mismatch")
    if int(derived.get("local_primitive_piece_count")) != 109:
        raise AssertionError("Fourier A985 local primitive-piece count mismatch")
    if int(derived.get("candidate_count")) != 3:
        raise AssertionError("Fourier A985 candidate count mismatch")
    if derived.get("pi33_scalars") != {
        "signed_turn_screen_0": 1,
        "signed_turn_screen_1": 1,
        "signed_turn_screen_2": -1,
    }:
        raise AssertionError("Fourier A985 Pi33 scalar profile mismatch")
    if derived.get("public_zero_scalar_profile") != {
        "signed_turn_screen_0": True,
        "signed_turn_screen_1": False,
        "signed_turn_screen_2": False,
    }:
        raise AssertionError("Fourier A985 public-zero scalar profile mismatch")

    records = derived.get("candidates", [])
    if len(records) != 3:
        raise AssertionError("Fourier A985 candidate record count mismatch")
    for record in records:
        screen_id = record.get("screen_id")
        expected = EXPECTED_COUNTS.get(str(screen_id))
        if expected is None:
            raise AssertionError("Fourier A985 unexpected screen id")
        if int(record.get("homogeneous_sector_count")) != expected["homogeneous"]:
            raise AssertionError("Fourier A985 homogeneous sector count mismatch")
        if int(record.get("mixed_sector_count")) != expected["mixed"]:
            raise AssertionError("Fourier A985 mixed sector count mismatch")
        if record.get("descends_to_all_39_sector_scalars") is not False:
            raise AssertionError("Fourier A985 global scalar descent mismatch")
        if record.get("local_phase_operator_involution") is not True:
            raise AssertionError("Fourier A985 local phase involution mismatch")
        if sum(int(value) for value in record.get("local_primitive_phase_counts", {}).values()) != 109:
            raise AssertionError("Fourier A985 local phase count mismatch")
        sector_rows = record.get("sector_evaluations", [])
        if len(sector_rows) != 39:
            raise AssertionError("Fourier A985 sector evaluation row count mismatch")
        if h_json(sector_rows) != record.get("sector_evaluations_sha256"):
            raise AssertionError("Fourier A985 sector evaluation hash mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("Fourier A985 sector-character candidate self hash mismatch")
    return rec
