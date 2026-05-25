from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_explicit_packet_restriction_map_test/report.json"
INPUT_RELS = {
    "constants": "data/raw/constants.json",
    "quotients_npz": "data/raw/quotients.npz",
    "relation_memberships_npz": "data/raw/relation_memberships.npz",
    "full_exposure_canonical_labelled_frame_report": (
        "data/invariants/d20/theorems/full_exposure_canonical_labelled_frame/report.json"
    ),
    "projective_packet_spectral_charge_table_report": (
        "data/invariants/d20/theorems/projective_packet_spectral_charge_table/report.json"
    ),
    "reduced_amplitude_quotient_scattering_automaton_report": (
        "data/invariants/d20/theorems/reduced_amplitude_quotient_scattering_automaton/report.json"
    ),
    "full_exposure_packet_propagation_cells_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_cells/report.json"
    ),
    "full_exposure_packet_propagation_graph_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
    ),
    "fourier_screen0_tube_central_element_report": (
        "data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json"
    ),
    "d20_packet_quotient_action_probe_report": (
        "data/invariants/d20/theorems/d20_packet_quotient_action_probe/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 explicit packet restriction map test {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 explicit packet restriction map test {key} hash mismatch")


def validate_d20_explicit_packet_restriction_map_test() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_explicit_packet_restriction_map_test")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 explicit packet restriction map test certificate")

    if rec.get("status") != "D20_EXPLICIT_PACKET_RESTRICTION_MAP_TEST_CERTIFIED":
        raise AssertionError("D20 explicit packet restriction map test status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 explicit packet restriction map test checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    inventory = derived.get("domain_inventory", {})
    if inventory.get("a985_relation_count") != 985:
        raise AssertionError("D20 explicit packet restriction map test A985 count mismatch")
    if inventory.get("q42_class_count") != 42 or inventory.get("q12_class_count") != 12:
        raise AssertionError("D20 explicit packet restriction map test quotient count mismatch")
    if inventory.get("automaton_mask_state_count") != 2048:
        raise AssertionError("D20 explicit packet restriction map test automaton count mismatch")
    if inventory.get("kernel_mode_count") != 1024:
        raise AssertionError("D20 explicit packet restriction map test kernel mode count mismatch")
    if inventory.get("packet_count") != 512:
        raise AssertionError("D20 explicit packet restriction map test packet count mismatch")
    if inventory.get("full_exposure_packet_count") != 20:
        raise AssertionError("D20 explicit packet restriction map test full packet count mismatch")
    if inventory.get("full_exposure_mode_count") != 40:
        raise AssertionError("D20 explicit packet restriction map test full mode count mismatch")
    if inventory.get("tube_closed_loop_basis_count") != 297:
        raise AssertionError("D20 explicit packet restriction map test tube basis mismatch")
    if inventory.get("tube_identity_relation_count") != 6:
        raise AssertionError("D20 explicit packet restriction map test tube identity mismatch")
    if inventory.get("quotient_shapes", {}).get("q42_map") != [985]:
        raise AssertionError("D20 explicit packet restriction map test q42 map shape mismatch")
    if inventory.get("quotient_shapes", {}).get("q12_tensor") != [12, 12, 12]:
        raise AssertionError("D20 explicit packet restriction map test q12 tensor shape mismatch")

    summary = derived.get("restriction_summary", {})
    if summary.get("constructed_restriction") != (
        "reduced_scattering_automaton_mask_to_full_packet_projection"
    ):
        raise AssertionError("D20 explicit packet restriction map test restriction mismatch")
    if summary.get("constructed_projection_mode_count") != 40:
        raise AssertionError("D20 explicit packet restriction map test projection mode mismatch")
    if summary.get("constructed_projection_packet_count") != 20:
        raise AssertionError("D20 explicit packet restriction map test projection packet mismatch")
    if summary.get("crossing_generators_tested") != [5, 9, 10]:
        raise AssertionError("D20 explicit packet restriction map test generator mismatch")
    if summary.get("one_step_kernel_packet_action_exists") is not False:
        raise AssertionError("D20 explicit packet restriction map test one-step overclaim")
    if summary.get("two_step_packet_action_exists") is not True:
        raise AssertionError("D20 explicit packet restriction map test two-step mismatch")
    if summary.get("two_step_block") != "2I+4S":
        raise AssertionError("D20 explicit packet restriction map test two-step block mismatch")
    if summary.get("block_algebra") != "Mat_2(Q)^10":
        raise AssertionError("D20 explicit packet restriction map test algebra mismatch")
    for key in (
        "a985_relation_restriction_constructed",
        "tube_screen0_restriction_constructed",
        "q42_q12_restriction_constructed",
    ):
        if summary.get(key) is not False:
            raise AssertionError("D20 explicit packet restriction map test raw restriction overclaim")
    if summary.get("missing_bridge_count") != 3:
        raise AssertionError("D20 explicit packet restriction map test missing bridge count mismatch")

    projection_rows = derived.get("full_packet_mode_projection_rows", [])
    if len(projection_rows) != 40:
        raise AssertionError("D20 explicit packet restriction map test projection row count mismatch")
    if h_json(projection_rows) != derived.get("full_packet_mode_projection_rows_sha256"):
        raise AssertionError("D20 explicit packet restriction map test projection hash mismatch")
    packet_counts: dict[int, int] = {}
    for row in projection_rows:
        packet_counts[int(row["packet_id"])] = packet_counts.get(int(row["packet_id"]), 0) + 1
    if len(packet_counts) != 20 or set(packet_counts.values()) != {2}:
        raise AssertionError("D20 explicit packet restriction map test projection multiplicity mismatch")

    source_rows = derived.get("automaton_restricted_source_rows", [])
    if len(source_rows) != 20:
        raise AssertionError("D20 explicit packet restriction map test source row count mismatch")
    if h_json(source_rows) != derived.get("automaton_restricted_source_rows_sha256"):
        raise AssertionError("D20 explicit packet restriction map test source row hash mismatch")
    for row in source_rows:
        source = int(row["source_packet_id"])
        partner = source ^ 1
        if row.get("one_step_target_kind_histogram") != {"odd": 3}:
            raise AssertionError("D20 explicit packet restriction map test one-step parity mismatch")
        hist = row.get("two_step_target_histogram", {})
        if hist.get(str(source)) != 2 or hist.get(str(partner)) != 4 or len(hist) != 2:
            raise AssertionError("D20 explicit packet restriction map test target histogram mismatch")
        if row.get("source_return_ordered_crossings") != [[5, 10], [10, 5]]:
            raise AssertionError("D20 explicit packet restriction map test source return mismatch")
        if row.get("active_partner_ordered_crossings") != [[5, 9], [9, 5], [9, 10], [10, 9]]:
            raise AssertionError("D20 explicit packet restriction map test partner return mismatch")

    blocks = derived.get("automaton_block_rows", [])
    if len(blocks) != 10:
        raise AssertionError("D20 explicit packet restriction map test block count mismatch")
    if h_json(blocks) != derived.get("automaton_block_rows_sha256"):
        raise AssertionError("D20 explicit packet restriction map test block hash mismatch")
    if any(row.get("block_matrix") != [[2, 4], [4, 2]] for row in blocks):
        raise AssertionError("D20 explicit packet restriction map test block matrix mismatch")

    missing = derived.get("missing_bridge_inventory", [])
    if len(missing) != 3:
        raise AssertionError("D20 explicit packet restriction map test bridge row count mismatch")
    if h_json(missing) != derived.get("missing_bridge_inventory_sha256"):
        raise AssertionError("D20 explicit packet restriction map test bridge row hash mismatch")
    if [row.get("candidate") for row in missing] != [
        "A985_relation_basis_to_full_packets",
        "screen0_tube_element_to_full_packets",
        "q42_q12_tensor_to_full_packets",
    ]:
        raise AssertionError("D20 explicit packet restriction map test bridge candidates mismatch")
    if any(not str(row.get("status", "")).startswith("blocked_missing_") for row in missing):
        raise AssertionError("D20 explicit packet restriction map test bridge status mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 explicit packet restriction map test self hash mismatch")
    return rec
