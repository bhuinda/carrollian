from __future__ import annotations

import json
from typing import Any, Dict

try:
    from .certify_io import ROOT, cached_core_block, h_file, h_json
except ImportError:  # Supports `python src/certify_core.py`.
    from certify_io import ROOT, cached_core_block, h_file, h_json


REPORT_REL = "data/invariants/d20/theorems/d20_packet_bridge_snf_obstruction/report.json"
INPUT_RELS = {
    "full_exposure_packet_propagation_graph_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
    ),
    "d20_full_packet_matrix_lift_report": (
        "data/invariants/d20/theorems/d20_full_packet_matrix_lift/report.json"
    ),
    "d20_explicit_packet_restriction_map_test_report": (
        "data/invariants/d20/theorems/d20_explicit_packet_restriction_map_test/report.json"
    ),
}


def _check_input_hash(inputs: dict[str, Any], key: str, rel_path: str) -> None:
    if inputs.get(key, {}).get("path") != rel_path:
        raise AssertionError(f"D20 packet bridge SNF obstruction {key} path mismatch")
    path = ROOT / rel_path
    if path.exists() and h_file(path) != inputs[key].get("sha256"):
        raise AssertionError(f"D20 packet bridge SNF obstruction {key} hash mismatch")


def validate_d20_packet_bridge_snf_obstruction() -> Dict[str, Any]:
    rec: dict[str, Any] | None = None
    path = ROOT / REPORT_REL
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            rec = json.load(f)
    else:
        cached = cached_core_block("d20_packet_bridge_snf_obstruction")
        if cached is not None:
            rec = cached
    if rec is None:
        raise FileNotFoundError("missing D20 packet bridge SNF obstruction certificate")

    if rec.get("status") != "D20_PACKET_BRIDGE_SNF_OBSTRUCTION_CERTIFIED":
        raise AssertionError("D20 packet bridge SNF obstruction status mismatch")
    if rec.get("all_checks_pass") is not True:
        raise AssertionError("D20 packet bridge SNF obstruction checks did not pass")

    inputs = rec.get("inputs", {})
    for key, rel_path in INPUT_RELS.items():
        _check_input_hash(inputs, key, rel_path)

    derived = rec.get("derived", {})
    summary = derived.get("obstruction_summary", {})
    if summary.get("packet_operator") != "direct_sum_10_copies_of_2I_plus_4S":
        raise AssertionError("D20 packet bridge SNF obstruction operator mismatch")
    if summary.get("matrix_shape") != [20, 20] or summary.get("rank_over_Q") != 20:
        raise AssertionError("D20 packet bridge SNF obstruction matrix shape/rank mismatch")
    if summary.get("smith_diagonal_multiplicities") != {"2": 10, "6": 10}:
        raise AssertionError("D20 packet bridge SNF obstruction Smith multiplicity mismatch")
    if summary.get("nonunit_invariant_factors") != [2] * 10 + [6] * 10:
        raise AssertionError("D20 packet bridge SNF obstruction invariant factors mismatch")
    if summary.get("cokernel") != "Z/2^10 x Z/6^10":
        raise AssertionError("D20 packet bridge SNF obstruction cokernel mismatch")
    if int(summary.get("cokernel_order", 0)) != 12**10:
        raise AssertionError("D20 packet bridge SNF obstruction cokernel order mismatch")
    if summary.get("torsion_primes") != [2, 3]:
        raise AssertionError("D20 packet bridge SNF obstruction torsion-prime mismatch")
    if summary.get("local_block_smith_diagonal") != [2, 6]:
        raise AssertionError("D20 packet bridge SNF obstruction local SNF mismatch")
    if summary.get("raw_bridge_columns_available") is not False:
        raise AssertionError("D20 packet bridge SNF obstruction raw-column overclaim")
    if summary.get("raw_bridge_candidate_count") != 3:
        raise AssertionError("D20 packet bridge SNF obstruction candidate count mismatch")

    matrix = derived.get("packet_operator_matrix", [])
    if len(matrix) != 20 or any(len(row) != 20 for row in matrix):
        raise AssertionError("D20 packet bridge SNF obstruction matrix dimensions mismatch")
    if h_json(matrix) != derived.get("packet_operator_matrix_sha256"):
        raise AssertionError("D20 packet bridge SNF obstruction matrix hash mismatch")

    snf = derived.get("smith_normal_form", {})
    if snf.get("diagonal") != [2] * 10 + [6] * 10:
        raise AssertionError("D20 packet bridge SNF obstruction Smith diagonal mismatch")
    if snf.get("diagonal_multiplicities") != {"2": 10, "6": 10}:
        raise AssertionError("D20 packet bridge SNF obstruction Smith diagonal count mismatch")
    if snf.get("off_diagonal_nonzero") != 0 or snf.get("divisibility_chain_valid") is not True:
        raise AssertionError("D20 packet bridge SNF obstruction Smith form mismatch")

    congruence_rows = derived.get("packet_image_congruence_rows", [])
    if len(congruence_rows) != 10:
        raise AssertionError("D20 packet bridge SNF obstruction congruence row count mismatch")
    if h_json(congruence_rows) != derived.get("packet_image_congruence_rows_sha256"):
        raise AssertionError("D20 packet bridge SNF obstruction congruence hash mismatch")
    for row in congruence_rows:
        if row.get("block_matrix") != [[2, 4], [4, 2]]:
            raise AssertionError("D20 packet bridge SNF obstruction block mismatch")
        if row.get("local_smith_diagonal") != [2, 6]:
            raise AssertionError("D20 packet bridge SNF obstruction row SNF mismatch")
        if row.get("local_cokernel") != "Z/2 x Z/6":
            raise AssertionError("D20 packet bridge SNF obstruction row cokernel mismatch")
        if row.get("image_test_for_target_pair_u_v") != [
            "u_minus_v_is_0_mod_2",
            "u_plus_v_is_0_mod_6",
        ]:
            raise AssertionError("D20 packet bridge SNF obstruction row congruence mismatch")

    tasks = derived.get("raw_bridge_snf_tasks", [])
    if len(tasks) != 3:
        raise AssertionError("D20 packet bridge SNF obstruction task count mismatch")
    if h_json(tasks) != derived.get("raw_bridge_snf_tasks_sha256"):
        raise AssertionError("D20 packet bridge SNF obstruction task hash mismatch")
    if [row.get("candidate") for row in tasks] != [
        "A985_relation_basis_to_full_packets",
        "screen0_tube_element_to_full_packets",
        "q42_q12_tensor_to_full_packets",
    ]:
        raise AssertionError("D20 packet bridge SNF obstruction task candidate mismatch")
    if any(row.get("snf_status") != "packet_obstruction_template_ready_no_raw_columns" for row in tasks):
        raise AssertionError("D20 packet bridge SNF obstruction task status mismatch")

    hfield = rec.get("certificate_sha256")
    tmp = dict(rec)
    tmp.pop("certificate_sha256", None)
    if h_json(tmp) != hfield:
        raise AssertionError("D20 packet bridge SNF obstruction self hash mismatch")

    return rec


if __name__ == "__main__":
    rec = validate_d20_packet_bridge_snf_obstruction()
    print(rec["status"])
    print(rec["certificate_sha256"])
