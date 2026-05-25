from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_matrix_lift_conjecture/report.json"
INPUT_RELS = {
    "constants": "data/raw/constants.json",
    "zero_axiom_coorient": "data/invariants/d20/zero_axiom_coorient.json",
    "zero_pair_charge_kernel_report": (
        "data/invariants/d20/theorems/full_exposure_zero_pair_propagator_charge_kernel/report.json"
    ),
    "zero_pair_symmetry_ward_report": (
        "data/invariants/d20/theorems/full_exposure_zero_pair_propagator_symmetry_ward/report.json"
    ),
    "sector26_invariant_suite_report": (
        "data/invariants/d20/theorems/sector26_invariant_suite/report.json"
    ),
    "sector33_unique_public_zero_support_report": (
        "data/invariants/d20/theorems/sector33_unique_public_zero_support/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 matrix lift conjecture {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 matrix lift conjecture {key} hash mismatch")


def validate_d20_matrix_lift_conjecture() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_matrix_lift_conjecture")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 matrix lift conjecture certificate")

    if rec.get("status") != "D20_MATRIX_LIFT_CONJECTURE_REGISTERED":
        raise AssertionError("D20 matrix lift conjecture status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 matrix lift conjecture checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    classification = derived.get("classification", {})
    if classification.get("safe_name") != "Finite Matrix-Theoretic Charge-Wall Shadow":
        raise AssertionError("D20 matrix lift conjecture safe name mismatch")
    if classification.get("strength") != "finite_shadow_not_m_theory":
        raise AssertionError("D20 matrix lift conjecture strength mismatch")
    if classification.get("m_theory_claimed") is not False:
        raise AssertionError("D20 matrix lift conjecture overclaimed M-theory")

    dictionary = derived.get("finite_shadow_dictionary", [])
    if len(dictionary) != 8:
        raise AssertionError("D20 matrix lift conjecture dictionary row count mismatch")
    if dictionary[-1].get("d20_layer") != "OP11":
        raise AssertionError("D20 matrix lift conjecture OP11 boundary row mismatch")
    if dictionary[-1].get("level") != "conjectural name, not a proved bridge":
        raise AssertionError("D20 matrix lift conjecture OP11 level mismatch")

    descent = derived.get("half_integral_descent", {})
    if descent.get("raw_half_residues_are_not_native_z26_classes") is not True:
        raise AssertionError("D20 matrix lift conjecture half-residue mismatch")
    if len(descent.get("fractional_residue_ids", [])) != 6:
        raise AssertionError("D20 matrix lift conjecture fractional residue count mismatch")
    if descent.get("plus_denominator_cleared_sector26_image") != {
        "sector26_clock_delta_mod26": 8,
        "sector26_clock_pair_mod26": [24, 6],
        "sector26_clock_sum_mod26": 4,
    }:
        raise AssertionError("D20 matrix lift conjecture plus image mismatch")
    if descent.get("minus_denominator_cleared_sector26_image") != {
        "sector26_clock_delta_mod26": 18,
        "sector26_clock_pair_mod26": [2, 20],
        "sector26_clock_sum_mod26": 22,
    }:
        raise AssertionError("D20 matrix lift conjecture minus image mismatch")
    if descent.get("paired_residue_is_sector26_neutral") is not True:
        raise AssertionError("D20 matrix lift conjecture neutral pair mismatch")

    wall_sector = derived.get("wall_sector", {})
    if wall_sector.get("primitive_wall_sector") != 33:
        raise AssertionError("D20 matrix lift conjecture wall sector mismatch")
    if wall_sector.get("public_zero_sectors") != [33]:
        raise AssertionError("D20 matrix lift conjecture public-zero sector mismatch")

    conjecture = derived.get("matrix_lift_conjecture", {})
    if conjecture.get("name") != "D20 Matrix Lift Conjecture":
        raise AssertionError("D20 matrix lift conjecture name mismatch")
    if conjecture.get("status") != "registered_conjecture_not_proven":
        raise AssertionError("D20 matrix lift conjecture proof status mismatch")
    bridges = conjecture.get("promotion_bridges", [])
    if len(bridges) != 3 or derived.get("missing_bridge_count") != 3:
        raise AssertionError("D20 matrix lift conjecture bridge count mismatch")
    if any(bridge.get("current_status") != "missing" for bridge in bridges):
        raise AssertionError("D20 matrix lift conjecture bridge status mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 matrix lift conjecture self hash mismatch")
    return rec
