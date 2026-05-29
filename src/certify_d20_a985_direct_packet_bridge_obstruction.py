from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import sys
from pathlib import Path
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_a985_direct_packet_bridge_obstruction import build_theorem
except ImportError:  # Supports direct script execution.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.certify_io import ROOT, h_file, h_json
    from src.derive_d20_a985_direct_packet_bridge_obstruction import build_theorem


THEOREM_ID = "d20_a985_direct_packet_bridge_obstruction"
REPORT_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/manifest.json"

INPUT_RELS = {
    "relation_memberships_npz": "data/raw/relation_memberships.npz",
    "quotients_npz": "data/raw/quotients.npz",
    "halloween_npz": "data/raw/Halloween.npz",
    "projective_packet_spectral_charge_table_report": (
        "data/invariants/d20/theorems/projective_packet_spectral_charge_table/report.json"
    ),
    "full_exposure_canonical_labelled_frame_report": (
        "data/invariants/d20/theorems/full_exposure_canonical_labelled_frame/report.json"
    ),
    "full_exposure_packet_propagation_graph_report": (
        "data/invariants/d20/theorems/full_exposure_packet_propagation_graph/report.json"
    ),
    "fourier_screen0_tube_central_element_report": (
        "data/invariants/d20/theorems/fourier_screen0_tube_central_element/report.json"
    ),
}

EXPECTED_CHECKS = {
    "projective_packet_table_is_certified",
    "full_exposure_frame_is_certified",
    "packet_graph_is_certified",
    "tube_input_is_certified",
    "full_mode_count_is_40",
    "all_985_relations_touch_full_modes",
    "only_six_relations_preserve_full_modes",
    "preserving_relations_are_tube_object_identities",
    "all_nonidentity_relations_leak",
    "direct_relation_restrictions_do_not_match_target_actions",
    "q42_q12_aggregates_do_not_match_target_actions",
    "direct_compressed_map_fails_multiplicativity",
    "q42_preserving_classes_are_only_identity_singletons",
    "q12_preserving_class_is_identity_pair",
}

EXPECTED_SUMMARY = {
    "label_hypothesis": "mode_mask_equals_raw_point_id",
    "full_exposure_packet_count": 20,
    "full_exposure_mode_count": 40,
    "raw_relation_count": 985,
    "relations_touching_full_packet_modes": 985,
    "relations_with_inside_hits": 628,
    "relations_preserving_full_packet_modes_on_source": 6,
    "leaking_relation_count": 979,
    "zero_source_hit_relation_count": 0,
    "block_landing_relation_count": 28,
    "preserving_relation_ids": [6, 163, 227, 349, 618, 893],
    "tube_identity_relation_ids": [6, 163, 227, 349, 618, 893],
    "relation_target_action_matches": {"2I": [], "4S": [], "2I+4S": []},
    "quotient_target_action_matches": {
        "q42": {"2I": [], "4S": [], "2I+4S": []},
        "q12": {"2I": [], "4S": [], "2I+4S": []},
    },
    "q42_preserving_class_ids": [2, 3],
    "q12_preserving_class_ids": [1],
    "direct_compressed_map_is_multiplicative": False,
}

EXPECTED_Q42_PRESERVING = [
    {
        "quotient": "q42",
        "class_id": 2,
        "relation_count": 1,
        "source_hits": 3,
        "inside_hits": 3,
        "source_leak": 0,
        "preserves_full_packet_modes_on_source": True,
        "lands_in_Mat_2_Q_power_10": True,
        "off_block_mass": 0,
        "nonzero_packet_entries": 3,
        "target_action_matches": [],
        "relation_ids": [227],
    },
    {
        "quotient": "q42",
        "class_id": 3,
        "relation_count": 1,
        "source_hits": 8,
        "inside_hits": 8,
        "source_leak": 0,
        "preserves_full_packet_modes_on_source": True,
        "lands_in_Mat_2_Q_power_10": True,
        "off_block_mass": 0,
        "nonzero_packet_entries": 8,
        "target_action_matches": [],
        "relation_ids": [349],
    },
]

EXPECTED_Q12_PRESERVING = [
    {
        "quotient": "q12",
        "class_id": 1,
        "relation_count": 2,
        "source_hits": 11,
        "inside_hits": 11,
        "source_leak": 0,
        "preserves_full_packet_modes_on_source": True,
        "lands_in_Mat_2_Q_power_10": True,
        "off_block_mass": 0,
        "nonzero_packet_entries": 11,
        "target_action_matches": [],
        "relation_ids": [227, 349],
    }
]

EXPECTED_MULTIPLICATIVITY_VIOLATION = {
    "left_relation_id": 53,
    "right_relation_id": 291,
    "rhs_term_count": 1,
    "rhs_terms_head": [[0, 8]],
    "lhs_nonzero_entries": 6,
    "rhs_nonzero_entries": 8,
    "diff_nonzero_entries": 14,
    "diff_l1": 70,
    "first_difference": {
        "row": 4,
        "col": 6,
        "lhs": 0,
        "rhs": 8,
        "diff": -8,
    },
}

EXPECTED_RELATION_TOUCH_HISTOGRAM = {
    "source_hit_histogram": {
        "3": 4,
        "4": 2,
        "6": 2,
        "7": 6,
        "8": 8,
        "11": 2,
        "12": 4,
        "14": 4,
        "16": 9,
        "21": 18,
        "24": 6,
        "28": 2,
        "32": 38,
        "33": 2,
        "42": 110,
        "44": 3,
        "48": 20,
        "63": 32,
        "64": 74,
        "66": 12,
        "84": 158,
        "96": 48,
        "126": 124,
        "128": 114,
        "132": 33,
        "192": 63,
        "264": 87,
    },
    "inside_hit_histogram": {
        "0": 357,
        "1": 210,
        "2": 173,
        "3": 93,
        "4": 77,
        "5": 28,
        "6": 27,
        "7": 14,
        "8": 2,
        "10": 3,
        "11": 1,
    },
    "source_leak_zero_count": 6,
}


def _load_json(rel_path: str) -> dict[str, Any]:
    with (ROOT / rel_path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} input path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} input hash mismatch")


def validate_d20_a985_direct_packet_bridge_obstruction() -> dict[str, Any]:
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)

    if report.get("schema") != "d20.theorem.d20_a985_direct_packet_bridge_obstruction":
        raise AssertionError("A985 direct packet bridge obstruction schema mismatch")
    if report.get("status") != "D20_A985_DIRECT_PACKET_BRIDGE_OBSTRUCTION_CERTIFIED":
        raise AssertionError("A985 direct packet bridge obstruction status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("A985 direct packet bridge obstruction checks did not pass")

    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("A985 direct packet bridge obstruction self hash mismatch")

    for key, rel_path in INPUT_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    recomputed = build_theorem()
    if recomputed != report:
        raise AssertionError("A985 direct packet bridge obstruction does not replay")

    checks = report.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("A985 direct packet bridge obstruction check table mismatch")

    derived = report.get("derived", {})
    if derived.get("direct_bridge_summary") != EXPECTED_SUMMARY:
        raise AssertionError("A985 direct packet bridge obstruction summary mismatch")
    if derived.get("q42_preserving_class_rows") != EXPECTED_Q42_PRESERVING:
        raise AssertionError("A985 direct packet bridge obstruction q42 row mismatch")
    if derived.get("q12_preserving_class_rows") != EXPECTED_Q12_PRESERVING:
        raise AssertionError("A985 direct packet bridge obstruction q12 row mismatch")
    if derived.get("multiplicativity_violation") != EXPECTED_MULTIPLICATIVITY_VIOLATION:
        raise AssertionError("A985 direct packet bridge obstruction violation mismatch")
    if derived.get("relation_touch_histogram") != EXPECTED_RELATION_TOUCH_HISTOGRAM:
        raise AssertionError("A985 direct packet bridge obstruction histogram mismatch")

    preserving_rows = derived.get("preserving_relation_rows", [])
    if [row.get("relation_id") for row in preserving_rows] != [6, 163, 227, 349, 618, 893]:
        raise AssertionError("A985 direct packet bridge obstruction preserving relations mismatch")
    if h_json(preserving_rows) != derived.get("preserving_relation_rows_sha256"):
        raise AssertionError("A985 direct packet bridge obstruction preserving hash mismatch")
    if h_json(EXPECTED_Q42_PRESERVING) != derived.get("q42_preserving_class_rows_sha256"):
        raise AssertionError("A985 direct packet bridge obstruction q42 hash mismatch")
    if h_json(EXPECTED_Q12_PRESERVING) != derived.get("q12_preserving_class_rows_sha256"):
        raise AssertionError("A985 direct packet bridge obstruction q12 hash mismatch")

    definition = report.get("definition", {})
    if definition.get("target_actions") != ["2I", "4S", "2I+4S"]:
        raise AssertionError("A985 direct packet bridge obstruction target actions mismatch")
    scope = definition.get("scope", "")
    if "literal current labels only" not in scope:
        raise AssertionError("A985 direct packet bridge obstruction scope overclaim")
    if "does not rule out" not in scope:
        raise AssertionError("A985 direct packet bridge obstruction remaining-seam mismatch")

    if manifest.get("schema") != "d20.theorem.d20_a985_direct_packet_bridge_obstruction_manifest":
        raise AssertionError("A985 direct packet bridge obstruction manifest schema mismatch")
    if manifest.get("status") != report.get("status"):
        raise AssertionError("A985 direct packet bridge obstruction manifest status mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("A985 direct packet bridge obstruction manifest report hash mismatch")
    if manifest.get("artifacts", {}).get("report") != REPORT_REL:
        raise AssertionError("A985 direct packet bridge obstruction manifest report path mismatch")
    if manifest.get("artifacts", {}).get("manifest") != MANIFEST_REL:
        raise AssertionError("A985 direct packet bridge obstruction manifest path mismatch")
    if manifest.get("inputs") != report.get("inputs"):
        raise AssertionError("A985 direct packet bridge obstruction manifest input mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("A985 direct packet bridge obstruction manifest hash mismatch")

    return report


if __name__ == "__main__":
    rec = validate_d20_a985_direct_packet_bridge_obstruction()
    print(rec["status"])
    print(rec["certificate_sha256"])
