from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json"
INPUT_RELS = {
    "constants": "data/raw/constants.json",
    "full_exposure_packet_propagation_graph_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
    ),
    "full_exposure_label_coordinate_transition_operator_report": (
        "data/invariants/d20/theorems/full_exposure_label_coordinate_transition_operator/report.json"
    ),
    "d20_minimal_matrix_charge_lift_report": (
        "data/invariants/d20/theorems/d20_minimal_matrix_charge_lift/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 full packet matrix lift {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 full packet matrix lift {key} hash mismatch")


def validate_d20_full_packet_matrix_lift() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_full_packet_matrix_lift")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 full packet matrix lift certificate")

    if rec.get("status") != "D20_FULL_PACKET_MATRIX_LIFT_CERTIFIED":
        raise AssertionError("D20 full packet matrix lift status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 full packet matrix lift checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("acting_summary", {})
    if summary.get("block_algebra") != "Mat_2(Q)^10":
        raise AssertionError("D20 full packet matrix lift algebra mismatch")
    if summary.get("block_algebra_dimension_over_Q") != 40:
        raise AssertionError("D20 full packet matrix lift dimension mismatch")
    if summary.get("packet_vector_space_dimension") != 20:
        raise AssertionError("D20 full packet matrix lift packet dimension mismatch")
    if summary.get("component_count") != 10:
        raise AssertionError("D20 full packet matrix lift component count mismatch")
    if summary.get("full_exposure_transition_operator") != "direct_sum_10_copies_of_2I_plus_4S":
        raise AssertionError("D20 full packet matrix lift transition mismatch")
    if summary.get("transition_operator_integer_eigenvalue_histogram") != {"-2": 10, "6": 10}:
        raise AssertionError("D20 full packet matrix lift spectrum mismatch")
    if summary.get("minimal_charge_lift_oriented_basis") != [239, 238]:
        raise AssertionError("D20 full packet matrix lift minimal basis mismatch")

    rows = derived.get("component_lift_rows", [])
    if len(rows) != 10:
        raise AssertionError("D20 full packet matrix lift row count mismatch")
    if h_json(rows) != derived.get("component_lift_rows_sha256"):
        raise AssertionError("D20 full packet matrix lift row hash mismatch")
    if sum(1 for row in rows if row.get("is_zero_pair_component")) != 1:
        raise AssertionError("D20 full packet matrix lift zero-pair row mismatch")
    for row in rows:
        if row.get("block_matrix") != [[2, 4], [4, 2]]:
            raise AssertionError("D20 full packet matrix lift block mismatch")
        if row.get("swap_involution") != [["0", "1"], ["1", "0"]]:
            raise AssertionError("D20 full packet matrix lift swap mismatch")
        if row.get("plus_projector") != [["1/2", "1/2"], ["1/2", "1/2"]]:
            raise AssertionError("D20 full packet matrix lift plus projector mismatch")
        if row.get("minus_projector") != [["1/2", "-1/2"], ["-1/2", "1/2"]]:
            raise AssertionError("D20 full packet matrix lift minus projector mismatch")
        if row.get("hidden_R33_transfer_mod26_sum") != 0:
            raise AssertionError("D20 full packet matrix lift hidden transfer mismatch")
        if row.get("net_height_flux_delta_sum") != 0:
            raise AssertionError("D20 full packet matrix lift height flux mismatch")

    probe = derived.get("a985_action_probe", {})
    if probe.get("a985_dimension") != 985:
        raise AssertionError("D20 full packet matrix lift A985 dimension mismatch")
    if probe.get("block_lift_image_dimension_bound") != 40:
        raise AssertionError("D20 full packet matrix lift image dimension mismatch")
    if probe.get("faithful_full_a985_action_possible_in_this_block_lift") is not False:
        raise AssertionError("D20 full packet matrix lift A985 action overclaim")
    if probe.get("minimum_kernel_dimension_for_any_a985_map_into_this_block_lift") != 945:
        raise AssertionError("D20 full packet matrix lift kernel bound mismatch")
    if probe.get("certified_a985_to_packet_operator_map_present") is not False:
        raise AssertionError("D20 full packet matrix lift A985 map boundary mismatch")
    if probe.get("tested_action_lands_in_block_lift") is not True:
        raise AssertionError("D20 full packet matrix lift tested action mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 full packet matrix lift self hash mismatch")
    return rec
