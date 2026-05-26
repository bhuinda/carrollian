from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_d20_loop_step_packet_snf_probe.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_loop_step_packet_snf_probe/report.json"
INPUT_RELS = {
    "boundary_to_loop_report": "data/invariants/d20/boundary_to_loop/report.json",
    "loop297_scattering_amplitude_lift_report": (
        "data/invariants/d20/theorems/loop297_scattering_amplitude_lift/report.json"
    ),
    "amplitude_quotient_fourier_mode_classifier_report": (
        "data/invariants/d20/theorems/amplitude_quotient_fourier_mode_classifier/report.json"
    ),
    "projective_packet_spectral_charge_table_report": (
        "data/invariants/d20/theorems/projective_packet_spectral_charge_table/report.json"
    ),
    "full_exposure_canonical_labelled_frame_report": (
        "data/invariants/d20/theorems/full_exposure_canonical_labelled_frame/report.json"
    ),
    "full_exposure_packet_propagation_graph_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
    ),
    "d20_packet_bridge_snf_obstruction_report": (
        "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
    ),
}

EXPECTED_COMPONENT_PAIRS = [
    [174, 175],
    [190, 191],
    [238, 239],
    [246, 247],
    [254, 255],
    [430, 431],
    [446, 447],
    [494, 495],
    [502, 503],
    [510, 511],
]
EXPECTED_FAILURE_HISTOGRAM = {
    "u_not_0_mod_2|u_plus_v_not_0_mod_6": 12,
    "u_not_0_mod_2|v_not_0_mod_2|u_plus_v_not_0_mod_6": 2,
    "u_plus_v_not_0_mod_6": 236,
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 loop-step packet SNF probe {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 loop-step packet SNF probe {key} hash mismatch")


def validate_d20_loop_step_packet_snf_probe() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_loop_step_packet_snf_probe")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 loop-step packet SNF probe certificate")

    if rec.get("status") != "D20_LOOP_STEP_PACKET_SNF_PROBE_CERTIFIED":
        raise AssertionError("D20 loop-step packet SNF probe status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 loop-step packet SNF probe checks did not pass")
    if rec.get("schema") != "d20.theorem.d20_loop_step_packet_snf_probe":
        raise AssertionError("D20 loop-step packet SNF probe schema mismatch")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    definition = rec.get("definition", {})
    if definition.get("packet_snf_image_test") != (
        "u = 0 mod 2, v = 0 mod 2, and u+v = 0 mod 6 on each packet doublet"
    ):
        raise AssertionError("D20 loop-step packet SNF probe image-test mismatch")

    derived = rec.get("derived", {})
    summary = derived.get("probe_summary", {})
    if summary.get("visible_candidate") != "Loop_297_step_atom_mode_incidence_count_columns":
        raise AssertionError("D20 loop-step packet SNF probe candidate mismatch")
    if summary.get("full_exposure_packet_count") != 20:
        raise AssertionError("D20 loop-step packet SNF probe packet count mismatch")
    if summary.get("component_count") != 10:
        raise AssertionError("D20 loop-step packet SNF probe component count mismatch")
    if summary.get("loop297_step_atom_count") != 25:
        raise AssertionError("D20 loop-step packet SNF probe atom count mismatch")
    if summary.get("step_atom_ids") != list(range(25)):
        raise AssertionError("D20 loop-step packet SNF probe atom ids mismatch")
    if summary.get("tested_column_count") != 25:
        raise AssertionError("D20 loop-step packet SNF probe column count mismatch")
    if summary.get("columns_passing_packet_snf_image") != []:
        raise AssertionError("D20 loop-step packet SNF probe passing-column overclaim")
    if summary.get("columns_failing_packet_snf_image") != list(range(25)):
        raise AssertionError("D20 loop-step packet SNF probe failing columns mismatch")
    if summary.get("failed_blocks_per_column_histogram") != {"10": 25}:
        raise AssertionError("D20 loop-step packet SNF probe failed-block histogram mismatch")
    if summary.get("component_pair_value_histogram") != {"1|1": 2, "1|2": 12, "2|2": 236}:
        raise AssertionError("D20 loop-step packet SNF probe pair-value histogram mismatch")
    if summary.get("failure_reason_histogram") != EXPECTED_FAILURE_HISTOGRAM:
        raise AssertionError("D20 loop-step packet SNF probe failure-reason histogram mismatch")
    if summary.get("natural_column_outcome") != "all_visible_loop_step_columns_fail_packet_snf_image":
        raise AssertionError("D20 loop-step packet SNF probe outcome mismatch")

    if derived.get("component_packet_pairs") != EXPECTED_COMPONENT_PAIRS:
        raise AssertionError("D20 loop-step packet SNF probe component pairs mismatch")

    packet_rows = derived.get("packet_mode_incidence_rows", [])
    if len(packet_rows) != 20:
        raise AssertionError("D20 loop-step packet SNF probe packet-row count mismatch")
    if h_json(packet_rows) != derived.get("packet_mode_incidence_rows_sha256"):
        raise AssertionError("D20 loop-step packet SNF probe packet-row hash mismatch")
    for row in packet_rows:
        counts = row.get("step_atom_incidence_counts", [])
        if len(counts) != 25 or any(value not in (1, 2) for value in counts):
            raise AssertionError("D20 loop-step packet SNF probe packet incidence mismatch")
        if row.get("loop297_atom_union_count") != 25:
            raise AssertionError("D20 loop-step packet SNF probe packet union mismatch")
        if len(row.get("mode_masks", [])) != 2:
            raise AssertionError("D20 loop-step packet SNF probe packet mode count mismatch")

    column_rows = derived.get("step_atom_column_rows", [])
    if len(column_rows) != 25:
        raise AssertionError("D20 loop-step packet SNF probe column-row count mismatch")
    if h_json(column_rows) != derived.get("step_atom_column_rows_sha256"):
        raise AssertionError("D20 loop-step packet SNF probe column-row hash mismatch")
    if h_json([row.get("target_vector_component_order") for row in column_rows]) != derived.get(
        "step_atom_target_vectors_sha256"
    ):
        raise AssertionError("D20 loop-step packet SNF probe target-vector hash mismatch")
    for atom_id, row in enumerate(column_rows):
        if row.get("loop297_step_atom_id") != atom_id:
            raise AssertionError("D20 loop-step packet SNF probe atom row order mismatch")
        if row.get("passes_packet_snf_image") is not False:
            raise AssertionError("D20 loop-step packet SNF probe column pass overclaim")
        if row.get("failed_component_count") != 10:
            raise AssertionError("D20 loop-step packet SNF probe failed component count mismatch")
        if len(row.get("target_vector_component_order", [])) != 20:
            raise AssertionError("D20 loop-step packet SNF probe target vector length mismatch")
        if len(row.get("component_pair_values", [])) != 10:
            raise AssertionError("D20 loop-step packet SNF probe component-pair value count mismatch")
        if "pass" in row.get("failure_reason_histogram", {}):
            raise AssertionError("D20 loop-step packet SNF probe column contains pass reason")

    checks = rec.get("checks", {})
    if not checks or any(value is not True for value in checks.values()):
        raise AssertionError("D20 loop-step packet SNF probe check table mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 loop-step packet SNF probe self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_loop_step_packet_snf_probe()
    print(rec["status"])
    print(rec["certificate_sha256"])
