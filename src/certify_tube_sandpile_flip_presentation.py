from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/tube_sandpile_flip_move_presentation/report.json"
SOURCE_REL = "data/invariants/d20/theorems/tube_sandpile_kernel_flips/report.json"
EXPECTED_BASIS_DELTAS = [128, 129, 130, 134, 136, 144, 161, 192, 384, 512, 1152]
EXPECTED_COVER_DELTAS = [1560, 128, 512, 130, 421]


def rank_over_f2(values: list[int]) -> int:
    echelon: dict[int, int] = {}
    for value in values:
        x = value
        for pivot in sorted(echelon, reverse=True):
            if (x >> pivot) & 1:
                x ^= echelon[pivot]
        if x:
            echelon[x.bit_length() - 1] = x
    return len(echelon)


def xor_all(values: list[int]) -> int:
    out = 0
    for value in values:
        out ^= value
    return out


def validate_tube_sandpile_flip_move_presentation() -> Dict[str, Any]:
    candidates = [ROOT / REPORT_REL]
    rec: dict[str, Any] | None = None
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                rec = json.load(f)
            break
    if rec is None:
        cached = cached_core_block("tube_sandpile_flip_move_presentation")
        if cached is not None:
            rec = cached
        else:
            raise FileNotFoundError("missing D20 tube sandpile flip-move presentation certificate")

    if rec.get("status") != "D20_TUBE_SANDPILE_FLIP_MOVE_PRESENTATION_CERTIFIED":
        raise AssertionError("tube sandpile flip-move presentation status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("tube sandpile flip-move presentation checks did not pass")

    source_path = ROOT / SOURCE_REL
    inputs = rec.get("inputs", {})
    source_input = inputs.get("tube_sandpile_kernel_flips_report", {})
    if source_input.get("path") != SOURCE_REL:
        raise AssertionError("tube sandpile flip-move presentation source path mismatch")
    if source_path.exists() and h_file(source_path) != source_input.get("sha256"):
        raise AssertionError("tube sandpile flip-move presentation source hash mismatch")

    derived = rec.get("derived", {})
    if int(derived.get("residue_rank")) != 11:
        raise AssertionError("tube sandpile flip-move residue rank mismatch")
    if int(derived.get("screen0_defect_mask")) != 640:
        raise AssertionError("tube sandpile flip-move defect mask mismatch")

    presentation = derived.get("presentation", {})
    if int(presentation.get("generator_count")) != 392:
        raise AssertionError("tube sandpile flip-move generator count mismatch")
    if int(presentation.get("basis_count")) != 11:
        raise AssertionError("tube sandpile flip-move basis count mismatch")
    if int(presentation.get("relation_count")) != 381:
        raise AssertionError("tube sandpile flip-move relation count mismatch")
    if int(presentation.get("rank_over_f2")) != 11:
        raise AssertionError("tube sandpile flip-move rank mismatch")
    if int(presentation.get("relation_space_dimension")) != 381:
        raise AssertionError("tube sandpile flip-move relation dimension mismatch")
    if int(presentation.get("quotient_order")) != 2048:
        raise AssertionError("tube sandpile flip-move quotient order mismatch")
    if presentation.get("basis_delta_masks") != EXPECTED_BASIS_DELTAS:
        raise AssertionError("tube sandpile flip-move basis delta mismatch")
    if presentation.get("relation_weight_histogram") != {"4": 93, "6": 199, "8": 86, "10": 3}:
        raise AssertionError("tube sandpile flip-move relation weight histogram mismatch")

    generator_rows = derived.get("generator_rows", [])
    if len(generator_rows) != 392:
        raise AssertionError("tube sandpile flip-move generator row count mismatch")
    if h_json(generator_rows) != derived.get("generator_rows_sha256"):
        raise AssertionError("tube sandpile flip-move generator row hash mismatch")
    generator_deltas = [int(row.get("delta_mask")) for row in generator_rows]
    if len(set(generator_deltas)) != 392:
        raise AssertionError("tube sandpile flip-move generator uniqueness mismatch")
    if rank_over_f2(generator_deltas) != 11:
        raise AssertionError("tube sandpile flip-move generator span mismatch")
    if any(((delta & 640).bit_count() & 1) != 1 for delta in generator_deltas):
        raise AssertionError("tube sandpile flip-move generator parity mismatch")

    basis_rows = derived.get("basis_rows", [])
    if len(basis_rows) != 11:
        raise AssertionError("tube sandpile flip-move basis row count mismatch")
    if h_json(basis_rows) != derived.get("basis_rows_sha256"):
        raise AssertionError("tube sandpile flip-move basis row hash mismatch")
    if [int(row.get("delta_mask")) for row in basis_rows] != EXPECTED_BASIS_DELTAS:
        raise AssertionError("tube sandpile flip-move basis row delta mismatch")

    relation_rows = derived.get("relation_rows", [])
    if len(relation_rows) != 381:
        raise AssertionError("tube sandpile flip-move relation row count mismatch")
    if h_json(relation_rows) != derived.get("relation_rows_sha256"):
        raise AssertionError("tube sandpile flip-move relation row hash mismatch")
    if any(int(row.get("xor_sum")) != 0 for row in relation_rows):
        raise AssertionError("tube sandpile flip-move relation xor mismatch")
    if any(xor_all([int(value) for value in row.get("relation_delta_masks", [])]) != 0 for row in relation_rows):
        raise AssertionError("tube sandpile flip-move relation recompute mismatch")
    if sorted(int(row.get("source_delta_mask")) for row in relation_rows) != sorted(
        set(generator_deltas) - set(EXPECTED_BASIS_DELTAS)
    ):
        raise AssertionError("tube sandpile flip-move relation support mismatch")

    cover = derived.get("five_cover", {})
    if cover.get("cover_delta_masks") != EXPECTED_COVER_DELTAS:
        raise AssertionError("tube sandpile flip-move cover delta mismatch")
    if int(cover.get("rank_over_f2")) != 5:
        raise AssertionError("tube sandpile flip-move cover rank mismatch")
    if int(cover.get("relation_count")) != 0:
        raise AssertionError("tube sandpile flip-move cover relation count mismatch")
    if int(cover.get("nonzero_sum_count")) != 31:
        raise AssertionError("tube sandpile flip-move cover nonzero sum count mismatch")
    if int(cover.get("span_size")) != 32:
        raise AssertionError("tube sandpile flip-move cover span size mismatch")
    if int(cover.get("span_flip_delta_count")) != 9:
        raise AssertionError("tube sandpile flip-move cover span intersection mismatch")
    if int(cover.get("quotient_dimension")) != 6:
        raise AssertionError("tube sandpile flip-move cover quotient dimension mismatch")
    if int(cover.get("coset_count")) != 64:
        raise AssertionError("tube sandpile flip-move cover coset count mismatch")

    cover_coordinate_rows = derived.get("cover_coordinate_rows", [])
    if len(cover_coordinate_rows) != 5:
        raise AssertionError("tube sandpile flip-move cover coordinate row count mismatch")
    if h_json(cover_coordinate_rows) != derived.get("cover_coordinate_rows_sha256"):
        raise AssertionError("tube sandpile flip-move cover coordinate row hash mismatch")
    if [int(row.get("delta_mask")) for row in cover_coordinate_rows] != EXPECTED_COVER_DELTAS:
        raise AssertionError("tube sandpile flip-move cover coordinate delta mismatch")

    cover_nonzero_sum_rows = derived.get("cover_nonzero_sum_rows", [])
    if len(cover_nonzero_sum_rows) != 31:
        raise AssertionError("tube sandpile flip-move cover sum row count mismatch")
    if h_json(cover_nonzero_sum_rows) != derived.get("cover_nonzero_sum_rows_sha256"):
        raise AssertionError("tube sandpile flip-move cover sum row hash mismatch")
    if any(int(row.get("sum_delta_mask")) == 0 for row in cover_nonzero_sum_rows):
        raise AssertionError("tube sandpile flip-move cover relation mismatch")

    cover_coset_rows = derived.get("cover_coset_rows", [])
    if len(cover_coset_rows) != 64:
        raise AssertionError("tube sandpile flip-move cover coset row count mismatch")
    if h_json(cover_coset_rows) != derived.get("cover_coset_rows_sha256"):
        raise AssertionError("tube sandpile flip-move cover coset row hash mismatch")
    if sum(int(row.get("generator_delta_count")) for row in cover_coset_rows) != 392:
        raise AssertionError("tube sandpile flip-move cover coset mass mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("tube sandpile flip-move presentation self hash mismatch")
    return rec
