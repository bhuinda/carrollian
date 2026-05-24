from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_fourier_screen0_tube_central_element() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("fourier_screen0_tube_central_element")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 Fourier screen-0 tube central-element certificate")

    if rec.get("status") != "D20_FOURIER_SCREEN0_TUBE_CENTRAL_ELEMENT_CERTIFIED":
        raise AssertionError("Fourier screen-0 tube central-element status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("Fourier screen-0 tube central-element checks did not pass")

    derived = rec.get("derived", {})
    if derived.get("screen_id") != "signed_turn_screen_0":
        raise AssertionError("Fourier screen-0 tube selected screen mismatch")
    if int(derived.get("closed_loop_basis_count")) != 297:
        raise AssertionError("Fourier screen-0 tube closed-loop basis count mismatch")
    if int(derived.get("full_relation_count")) != 985:
        raise AssertionError("Fourier screen-0 tube full relation count mismatch")
    if int(derived.get("local_primitive_piece_count")) != 109:
        raise AssertionError("Fourier screen-0 tube primitive-piece count mismatch")
    if derived.get("primitive_piece_phase_counts") != {"+1": 79, "-1": 30}:
        raise AssertionError("Fourier screen-0 tube primitive-piece phase count mismatch")
    if derived.get("object_phase_assignment") != {
        "B-": -1,
        "B+": 1,
        "V-": -1,
        "V+": 1,
        "S-": 1,
        "S+": 1,
    }:
        raise AssertionError("Fourier screen-0 tube object phase assignment mismatch")

    signed_unit = derived.get("signed_object_unit", {})
    reconstructed = derived.get("reconstructed_from_local_primitives", {})
    if signed_unit.get("sha256") != reconstructed.get("sha256"):
        raise AssertionError("Fourier screen-0 tube reconstruction hash mismatch")
    if int(reconstructed.get("support")) != 6:
        raise AssertionError("Fourier screen-0 tube reconstruction support mismatch")
    if int(derived.get("screen_square", {}).get("support")) != 6:
        raise AssertionError("Fourier screen-0 tube square support mismatch")
    if derived.get("screen_square", {}).get("sha256") != derived.get("closed_loop_unit", {}).get("sha256"):
        raise AssertionError("Fourier screen-0 tube square/unit hash mismatch")

    closed = derived.get("closed_loop_commutator", {})
    if int(closed.get("basis_relations_checked")) != 297 or int(closed.get("failure_count")) != 0:
        raise AssertionError("Fourier screen-0 tube closed-loop commutator mismatch")
    full = derived.get("full_a985_commutator_boundary", {})
    if int(full.get("basis_relations_checked")) != 985:
        raise AssertionError("Fourier screen-0 tube full commutator check count mismatch")
    if int(full.get("failure_count")) <= 0:
        raise AssertionError("Fourier screen-0 tube full commutator did not detect boundary")
    if int(full.get("failure_count")) != int(full.get("phase_mismatch_relation_count")):
        raise AssertionError("Fourier screen-0 tube full commutator failure-count mismatch")

    public_zero_rows = derived.get("public_zero_support_action", [])
    if len(public_zero_rows) != 5:
        raise AssertionError("Fourier screen-0 tube public-zero support count mismatch")
    if any(int(row.get("support_scalar")) != 1 for row in public_zero_rows):
        raise AssertionError("Fourier screen-0 tube public-zero support scalar mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("Fourier screen-0 tube central-element self hash mismatch")
    return rec
