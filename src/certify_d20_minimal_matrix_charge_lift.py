from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_minimal_matrix_charge_lift/report.json"
INPUT_RELS = {
    "zero_pair_charge_kernel_report": (
        "data/invariants/d20/theorems/full_exposure_zero_pair_propagator_charge_kernel/report.json"
    ),
    "d20_matrix_lift_conjecture_report": (
        "data/invariants/d20/theorems/d20_matrix_lift_conjecture/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 minimal matrix charge lift {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 minimal matrix charge lift {key} hash mismatch")


def validate_d20_minimal_matrix_charge_lift() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_minimal_matrix_charge_lift")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 minimal matrix charge lift certificate")

    if rec.get("status") != "D20_MINIMAL_MATRIX_CHARGE_LIFT_CERTIFIED":
        raise AssertionError("D20 minimal matrix charge lift status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 minimal matrix charge lift checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    lift = derived.get("minimal_matrix_charge_lift", {})
    if lift.get("algebra") != "Mat_2(Q)":
        raise AssertionError("D20 minimal matrix charge lift algebra mismatch")
    if lift.get("coefficient_ring") != "Z[1/2] inside Q":
        raise AssertionError("D20 minimal matrix charge lift coefficient ring mismatch")
    if lift.get("basis_order") != [239, 238]:
        raise AssertionError("D20 minimal matrix charge lift basis mismatch")
    if lift.get("source_vector") != ["1", "0"]:
        raise AssertionError("D20 minimal matrix charge lift source vector mismatch")
    if lift.get("swap_involution") != [["0", "1"], ["1", "0"]]:
        raise AssertionError("D20 minimal matrix charge lift swap mismatch")
    if lift.get("plus_projector") != [["1/2", "1/2"], ["1/2", "1/2"]]:
        raise AssertionError("D20 minimal matrix charge lift plus projector mismatch")
    if lift.get("minus_projector") != [["1/2", "-1/2"], ["-1/2", "1/2"]]:
        raise AssertionError("D20 minimal matrix charge lift minus projector mismatch")
    if lift.get("plus_raw_residue_vector") != ["1/2", "1/2"]:
        raise AssertionError("D20 minimal matrix charge lift plus raw vector mismatch")
    if lift.get("minus_raw_residue_vector") != ["1/2", "-1/2"]:
        raise AssertionError("D20 minimal matrix charge lift minus raw vector mismatch")
    if lift.get("plus_denominator_cleared_vector") != [1, 1]:
        raise AssertionError("D20 minimal matrix charge lift plus cleared vector mismatch")
    if lift.get("minus_denominator_cleared_vector") != [1, -1]:
        raise AssertionError("D20 minimal matrix charge lift minus cleared vector mismatch")
    if lift.get("plus_denominator_cleared_sector26_image") != {
        "sector26_clock_delta_mod26": 8,
        "sector26_clock_pair_mod26": [24, 6],
        "sector26_clock_sum_mod26": 4,
    }:
        raise AssertionError("D20 minimal matrix charge lift plus sector-26 image mismatch")
    if lift.get("minus_denominator_cleared_sector26_image") != {
        "sector26_clock_delta_mod26": 18,
        "sector26_clock_pair_mod26": [2, 20],
        "sector26_clock_sum_mod26": 22,
    }:
        raise AssertionError("D20 minimal matrix charge lift minus sector-26 image mismatch")
    if lift.get("primitive_wall_sector") != 33:
        raise AssertionError("D20 minimal matrix charge lift wall sector mismatch")
    if lift.get("lift_status") != "minimal_charge_kernel_lift_constructed_full_A985_DLCQ_lift_not_constructed":
        raise AssertionError("D20 minimal matrix charge lift scope mismatch")

    rows = derived.get("mode_direction_checks", [])
    if len(rows) != 6 or any(row.get("direction_matches") is not True for row in rows):
        raise AssertionError("D20 minimal matrix charge lift mode direction mismatch")
    bridge = derived.get("remaining_promotion_bridge", {})
    if bridge.get("id") != "A985_to_DLCQ_matrix_model" or bridge.get("current_status") != "missing":
        raise AssertionError("D20 minimal matrix charge lift bridge status mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 minimal matrix charge lift self hash mismatch")
    return rec
