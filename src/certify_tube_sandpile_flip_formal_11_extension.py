from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_formal_11_extension_test/report.json"
UNSUPPORTED_REL = "data/invariants/d20/theorems/tube_sandpile_flip_unsupported_state_classification/report.json"
FOURIER_A985_REL = "data/invariants/d20/theorems/fourier_a985_sector_character_candidates/report.json"


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"tube sandpile flip formal 11 extension {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"tube sandpile flip formal 11 extension {key} hash mismatch")


def validate_tube_sandpile_flip_formal_11_extension_test() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("tube_sandpile_flip_formal_11_extension_test")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 tube sandpile flip formal 11 extension certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_FLIP_FORMAL_11_EXTENSION_OBSTRUCTED":
        raise AssertionError("tube sandpile flip formal 11 extension status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile flip formal 11 extension checks did not pass")

    inputs = rec.get("inputs", {})
    _check_input_hash(inputs, "tube_sandpile_flip_unsupported_state_classification_report", UNSUPPORTED_REL)
    _check_input_hash(inputs, "fourier_a985_sector_character_candidates_report", FOURIER_A985_REL)

    derived = rec.get("derived", {})
    object_rows = derived.get("object_full_phase_rows", [])
    if len(object_rows) != 6:
        raise AssertionError("tube sandpile flip formal 11 extension object row count mismatch")
    if h_json(object_rows) != derived.get("object_full_phase_rows_sha256"):
        raise AssertionError("tube sandpile flip formal 11 extension object row hash mismatch")
    if derived.get("object_full_signature_counts") != {"001": 2, "010": 2, "100": 2}:
        raise AssertionError("tube sandpile flip formal 11 extension full signature mismatch")
    if derived.get("object_screen12_counts") != {"00": 2, "01": 2, "10": 2}:
        raise AssertionError("tube sandpile flip formal 11 extension screen12 count mismatch")
    labels_by_full = derived.get("object_labels_by_full_signature", {})
    if labels_by_full.get("011") != [] or labels_by_full.get("111") != []:
        raise AssertionError("tube sandpile flip formal 11 extension state-11 lift mismatch")
    if derived.get("object_labels_by_screen12", {}).get("11") != []:
        raise AssertionError("tube sandpile flip formal 11 extension screen12 labels mismatch")

    lifts = derived.get("residue_state11_screen0_lifts", {})
    if lifts != {"011": 256, "111": 256}:
        raise AssertionError("tube sandpile flip formal 11 extension residue lift mismatch")
    obstruction = derived.get("state11_transition_obstruction", {})
    if int(obstruction.get("missing_state_pair_count")) != 420:
        raise AssertionError("tube sandpile flip formal 11 extension transition count mismatch")
    if int(obstruction.get("coset_count_using_missing_state")) != 56:
        raise AssertionError("tube sandpile flip formal 11 extension coset count mismatch")

    scenarios = derived.get("formal_extension_scenarios", [])
    if len(scenarios) != 6:
        raise AssertionError("tube sandpile flip formal 11 extension scenario count mismatch")
    if h_json(scenarios) != derived.get("formal_extension_scenarios_sha256"):
        raise AssertionError("tube sandpile flip formal 11 extension scenario hash mismatch")
    if derived.get("constraint_preserving_scenarios") != ["empty_formal_11_cell"]:
        raise AssertionError("tube sandpile flip formal 11 extension preserving scenario mismatch")
    if derived.get("valid_nonempty_extension_scenarios") != []:
        raise AssertionError("tube sandpile flip formal 11 extension nonempty scenario mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile flip formal 11 extension self hash mismatch")
    return rec
