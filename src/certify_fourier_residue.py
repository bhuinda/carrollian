from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_json


def validate_fourier_residue_screen() -> Dict[str, Any]:
    candidates = [
        ROOT / "data/invariants/d20/theorems/fourier_residue_screen/report.json",
    ]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("fourier_residue_screen")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 Fourier residue-screen certificate")

    if rec.get("status") != "D20_FOURIER_RESIDUE_SCREEN_CERTIFIED":
        raise AssertionError("Fourier residue-screen status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("Fourier residue-screen checks did not pass")

    derived = rec.get("derived", {})
    residue = derived.get("residue_space", {})
    if int(residue.get("rank")) != 11 or int(residue.get("mask_count")) != 2048:
        raise AssertionError("Fourier residue-screen space size mismatch")
    if residue.get("masks_are_complete") is not True:
        raise AssertionError("Fourier residue-screen masks are incomplete")
    if residue.get("basis_parse_matches_mask") is not True:
        raise AssertionError("Fourier residue-screen basis parse mismatch")

    screens = derived.get("screens", [])
    if len(screens) != 3:
        raise AssertionError("Fourier residue-screen count mismatch")
    expected_defects = [[7, 9], [2, 8], [5, 6]]
    if [screen.get("defect_cycle_ids") for screen in screens] != expected_defects:
        raise AssertionError("Fourier residue-screen defect vectors mismatch")
    for screen in screens:
        if int(screen.get("defect_vector_weight")) != 2:
            raise AssertionError("Fourier residue-screen defect-vector weight mismatch")
        if int(screen.get("coherent_mask_count")) != 1024:
            raise AssertionError("Fourier residue-screen coherent-mask count mismatch")
        if int(screen.get("odd_mask_count")) != 1024:
            raise AssertionError("Fourier residue-screen odd-mask count mismatch")
        if int(screen.get("kernel_dimension")) != 10:
            raise AssertionError("Fourier residue-screen kernel dimension mismatch")

    combined = derived.get("combined_screen", {})
    if int(combined.get("rank_over_f2")) != 3:
        raise AssertionError("Fourier residue-screen combined rank mismatch")
    cell_counts = combined.get("cell_counts_by_signature")
    if not isinstance(cell_counts, dict) or len(cell_counts) != 8:
        raise AssertionError("Fourier residue-screen cell count mismatch")
    if set(int(value) for value in cell_counts.values()) != {256}:
        raise AssertionError("Fourier residue-screen cell sizes mismatch")
    if int(combined.get("common_kernel_mask_count")) != 256:
        raise AssertionError("Fourier residue-screen common kernel size mismatch")
    rows = combined.get("residue_screen_rows", [])
    if len(rows) != 2048:
        raise AssertionError("Fourier residue-screen row table length mismatch")
    if [int(row.get("mask")) for row in rows] != list(range(2048)):
        raise AssertionError("Fourier residue-screen row table mask order mismatch")
    row_counts = {key: int(value) for key, value in Counter(row.get("signature") for row in rows).items()}
    if row_counts != cell_counts:
        raise AssertionError("Fourier residue-screen row table signature counts mismatch")
    if h_json(rows) != combined.get("residue_screen_rows_sha256"):
        raise AssertionError("Fourier residue-screen row table hash mismatch")

    seam = derived.get("sandpile_pairing_seam", {})
    if seam.get("mask_to_divisor_map_certified") is not False:
        raise AssertionError("Fourier residue-screen sandpile seam mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("Fourier residue-screen self hash mismatch")
    return rec
