from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_packet_quotient_action_probe/report.json"
INPUT_RELS = {
    "constants": "data/raw/constants.json",
    "quotients_npz": "data/raw/quotients.npz",
    "full_exposure_packet_propagation_cells_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_cells/report.json"
    ),
    "full_exposure_packet_propagation_graph_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
    ),
    "full_exposure_label_coordinate_transition_operator_report": (
        "data/invariants/d20/theorems/full_exposure_label_coordinate_transition_operator/report.json"
    ),
    "d20_full_packet_matrix_lift_report": (
        "data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json"
    ),
    "compact_amplitude_quotient_report": (
        "data/invariants/d20/theorems/compact_amplitude_quotient/report.json"
    ),
    "reduced_amplitude_quotient_scattering_automaton_report": (
        "data/invariants/d20/theorems/reduced_amplitude_quotient_scattering_automaton/report.json"
    ),
    "fourier_screen0_tube_central_element_report": (
        "data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json"
    ),
    "tube_sandpile_divisor_map_report": (
        "data/invariants/d20/theorems/tube_sandpile_divisor_map/report.json"
    ),
    "tube_sandpile_kernel_flips_report": (
        "data/invariants/d20/theorems/tube_sandpile_kernel_flips/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 packet quotient-action probe {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 packet quotient-action probe {key} hash mismatch")


def validate_d20_packet_quotient_action_probe() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_packet_quotient_action_probe")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 packet quotient-action probe certificate")

    if rec.get("status") != "D20_PACKET_QUOTIENT_ACTION_PROBE_CERTIFIED":
        raise AssertionError("D20 packet quotient-action probe status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 packet quotient-action probe checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("operator_probe_summary", {})
    if summary.get("packet_space_dimension") != 20:
        raise AssertionError("D20 packet quotient-action probe packet dimension mismatch")
    if summary.get("full_exposure_packet_count") != 20:
        raise AssertionError("D20 packet quotient-action probe packet count mismatch")
    if summary.get("active_partner_doublet_count") != 10:
        raise AssertionError("D20 packet quotient-action probe doublet count mismatch")
    if summary.get("block_algebra") != "Mat_2(Q)^10":
        raise AssertionError("D20 packet quotient-action probe algebra mismatch")
    if summary.get("positive_packet_action_count") != 3:
        raise AssertionError("D20 packet quotient-action probe positive action count mismatch")
    if summary.get("strongest_certified_packet_action") != "full_paired_cross_return_sum":
        raise AssertionError("D20 packet quotient-action probe strongest action mismatch")
    if summary.get("strongest_certified_packet_action_block") != "2I+4S":
        raise AssertionError("D20 packet quotient-action probe strongest block mismatch")
    if summary.get("source_loop_action_block") != "2I":
        raise AssertionError("D20 packet quotient-action probe source-loop block mismatch")
    if summary.get("active_partner_action_block") != "4S":
        raise AssertionError("D20 packet quotient-action probe active-partner block mismatch")
    if summary.get("preserves_full_exposure_20_packet_subspace") is not True:
        raise AssertionError("D20 packet quotient-action probe preservation mismatch")
    if summary.get("lands_in_block_lift") is not True:
        raise AssertionError("D20 packet quotient-action probe block landing mismatch")
    if summary.get("a985_dimension") != 985:
        raise AssertionError("D20 packet quotient-action probe A985 dimension mismatch")
    if summary.get("block_lift_image_dimension_bound") != 40:
        raise AssertionError("D20 packet quotient-action probe block dimension mismatch")
    if summary.get("minimum_kernel_dimension_for_any_a985_map_into_this_block_lift") != 945:
        raise AssertionError("D20 packet quotient-action probe kernel bound mismatch")
    if summary.get("certified_a985_to_packet_operator_map_present") is not False:
        raise AssertionError("D20 packet quotient-action probe A985 map overclaim")
    if summary.get("a985_or_tube_packet_operator_found") is not False:
        raise AssertionError("D20 packet quotient-action probe tube/A985 overclaim")
    if summary.get("terminal_quotient_packet_operator_found") is not False:
        raise AssertionError("D20 packet quotient-action probe terminal quotient overclaim")
    if summary.get("only_scattering_quotient_packet_actions_found") is not True:
        raise AssertionError("D20 packet quotient-action probe scattering boundary mismatch")

    actions = derived.get("certified_packet_actions", [])
    if h_json(actions) != derived.get("certified_packet_actions_sha256"):
        raise AssertionError("D20 packet quotient-action probe action hash mismatch")
    if [row.get("operator_id") for row in actions] != [
        "source_loop_5_10_plus_10_5",
        "active_partner_cross_pair_sum",
        "full_paired_cross_return_sum",
    ]:
        raise AssertionError("D20 packet quotient-action probe action ids mismatch")
    if actions[0].get("block_on_each_active_partner_doublet") != [[2, 0], [0, 2]]:
        raise AssertionError("D20 packet quotient-action probe source-loop matrix mismatch")
    if actions[1].get("block_on_each_active_partner_doublet") != [[0, 4], [4, 0]]:
        raise AssertionError("D20 packet quotient-action probe active-partner matrix mismatch")
    if actions[2].get("block_on_each_active_partner_doublet") != [[2, 4], [4, 2]]:
        raise AssertionError("D20 packet quotient-action probe full matrix mismatch")
    if any(row.get("lands_in_block_lift") is not True for row in actions):
        raise AssertionError("D20 packet quotient-action probe action landing mismatch")

    sources = derived.get("candidate_source_rows", [])
    if len(sources) != 10:
        raise AssertionError("D20 packet quotient-action probe source row count mismatch")
    if h_json(sources) != derived.get("candidate_source_rows_sha256"):
        raise AssertionError("D20 packet quotient-action probe source row hash mismatch")
    source_status = {row.get("source_id"): row.get("packet_operator_status") for row in sources}
    if source_status.get("full_exposure_packet_propagation_graph") != (
        "supplies_20_by_20_transition_matrix"
    ):
        raise AssertionError("D20 packet quotient-action probe graph source mismatch")
    for key in (
        "compact_amplitude_quotient",
        "reduced_amplitude_quotient_scattering_automaton",
        "fourier_screen0_tube_central_element",
        "tube_sandpile_divisor_map",
        "tube_sandpile_kernel_flips",
        "raw_quotients_npz",
    ):
        if "no_" not in source_status.get(key, ""):
            raise AssertionError("D20 packet quotient-action probe negative source mismatch")

    boundary = derived.get("negative_boundary", {})
    for key in (
        "a985_multiplication_tensor_restricted_to_packets",
        "tube_central_element_restricted_to_packets",
        "raw_quotient_tensor_restricted_to_packets",
    ):
        if boundary.get(key) != "not_certified":
            raise AssertionError("D20 packet quotient-action probe boundary mismatch")
    if boundary.get("scattering_operator_is_a985_element") is not False:
        raise AssertionError("D20 packet quotient-action probe A985 element overclaim")
    if boundary.get("scattering_operator_is_tube_central_element") is not False:
        raise AssertionError("D20 packet quotient-action probe tube element overclaim")
    if boundary.get("scattering_operator_is_terminal_quotient_element") is not False:
        raise AssertionError("D20 packet quotient-action probe quotient element overclaim")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 packet quotient-action probe self hash mismatch")
    return rec
