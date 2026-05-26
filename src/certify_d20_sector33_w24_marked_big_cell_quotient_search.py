from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_sector33_w24_marked_big_cell_quotient_search import (
        MODE_NAMES,
        build_artifact,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_sector33_w24_marked_big_cell_quotient_search import (
        MODE_NAMES,
        build_artifact,
    )


THEOREM_ID = "d20_sector33_w24_marked_big_cell_quotient_search"
ARTIFACT_REL = "generated/d20_sector33_w24_marked_big_cell_quotient_search.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "d20_json": "d20.json",
    "w24_row_alphabetization": (
        "data/invariants/d20/proof_obligations/d20_w24_hexacode_row_alphabetization/report.json"
    ),
    "per_edge_rowspace_prune": (
        "data/invariants/d20/proof_obligations/d20_sector33_w24_per_edge_rowspace_prune/report.json"
    ),
    "sector33_dual": "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json",
    "wu_spinh_6j_marking": "data/selectors/wu_spinh_6j_marking.json",
}

EXPECTED_MODE_RANKS = {
    "duplicate_xor_collapse": 11,
    "first_edge_selector": 16,
    "second_edge_selector": 14,
}

EXPECTED_WEIGHT_HISTOGRAMS = {
    "duplicate_xor_collapse": {
        "0": 1,
        "1": 1,
        "3": 20,
        "4": 65,
        "5": 117,
        "6": 232,
        "7": 400,
        "8": 435,
        "9": 315,
        "10": 216,
        "11": 156,
        "12": 75,
        "13": 15,
    },
    "first_edge_selector": {
        "0": 1,
        "1": 16,
        "2": 120,
        "3": 560,
        "4": 1820,
        "5": 4368,
        "6": 8008,
        "7": 11440,
        "8": 12870,
        "9": 11440,
        "10": 8008,
        "11": 4368,
        "12": 1820,
        "13": 560,
        "14": 120,
        "15": 16,
        "16": 1,
    },
    "second_edge_selector": {
        "0": 1,
        "1": 7,
        "2": 33,
        "3": 135,
        "4": 437,
        "5": 1075,
        "6": 2021,
        "7": 2915,
        "8": 3235,
        "9": 2805,
        "10": 1955,
        "11": 1109,
        "12": 487,
        "13": 145,
        "14": 23,
        "15": 1,
    },
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


def _artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} input path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} input file hash mismatch")


def _mode_map(artifact: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modes = artifact.get("quotient_search", {}).get("modes", [])
    if not isinstance(modes, list):
        raise AssertionError("marked big-cell quotient modes must be a list")
    return {mode.get("mode"): mode for mode in modes}


def validate_d20_sector33_w24_marked_big_cell_quotient_search() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_big_cell_quotient_search.artifact@1"
    ):
        raise AssertionError("marked big-cell quotient artifact schema mismatch")
    if artifact.get("status") != "D20_SECTOR33_W24_MARKED_BIG_CELL_QUOTIENT_SEARCH_DERIVED":
        raise AssertionError("marked big-cell quotient artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("marked big-cell quotient artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("marked big-cell quotient artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "d20_input_is_certified",
        "w24_row_alphabetization_is_certified",
        "per_edge_rowspace_prune_input_is_certified",
        "sector33_dual_input_is_certified",
        "wu_marking_is_certified_external_boundary",
        "source_matrix_shape_is_21_by_31",
        "d20_selector_duad_profile_has_15_pairs",
        "d20_selector_duads_have_two_edges_each",
        "big_cell_has_scalar_plus_15_two_forms",
        "big_cell_pair_set_matches_d20_selector_duads",
        "big_cell_pair_order_matches_d20_selector_duad_index",
        "quotient_mode_count_is_3",
        "all_quotient_lengths_are_16",
        "duplicate_xor_collapse_rank_is_11",
        "first_edge_selector_rank_is_16",
        "second_edge_selector_rank_is_14",
        "mode_rank_histogram_is_11_14_16",
        "no_mode_has_rank_12",
        "no_mode_is_self_orthogonal",
        "natural_marked_quotients_fail_candidate_gate",
        "explicit_morphism_remains_open",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("marked big-cell quotient check mismatch")

    target = artifact.get("target_golay_profile", {})
    if target.get("length") != 24 or target.get("rank") != 12:
        raise AssertionError("marked big-cell quotient target Golay profile mismatch")
    if target.get("weight_histogram") != {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1}:
        raise AssertionError("marked big-cell quotient target Golay histogram mismatch")

    big_cell = artifact.get("marked_big_cell_profile", {})
    if big_cell.get("status") != (
        "WU_SPINH_OCTAD_SPIN12_6J_MARKING_CERTIFIED_GOLAY_SELECTOR_STILL_EXTERNAL"
    ):
        raise AssertionError("marked big-cell quotient Wu marking status mismatch")
    if big_cell.get("golay_selector_constructed") is not False:
        raise AssertionError("marked big-cell quotient external boundary mismatch")
    if big_cell.get("foam_big_cell_dimension") != 16:
        raise AssertionError("marked big-cell quotient big-cell dimension mismatch")
    if big_cell.get("scalar_coordinate_count") != 1:
        raise AssertionError("marked big-cell quotient scalar count mismatch")
    if big_cell.get("two_form_coordinate_count") != 15:
        raise AssertionError("marked big-cell quotient two-form count mismatch")
    if big_cell.get("lambda2_H6_coordinate_count") != 15:
        raise AssertionError("marked big-cell quotient lambda2 count mismatch")
    if big_cell.get("h6_labels") != ["B-", "B+", "V-", "V+", "S-", "S+"]:
        raise AssertionError("marked big-cell quotient H6 label mismatch")
    if big_cell.get("pair_set_matches_d20_selector_duads") is not True:
        raise AssertionError("marked big-cell quotient pair set mismatch")
    if big_cell.get("pair_order_matches_d20_selector_duad_index") is not True:
        raise AssertionError("marked big-cell quotient pair order mismatch")

    search = artifact.get("quotient_search", {})
    if search.get("source_matrix") != "sector33_primal_mod2":
        raise AssertionError("marked big-cell quotient source matrix mismatch")
    if search.get("source_shape") != {"rows": 21, "cols": 31}:
        raise AssertionError("marked big-cell quotient source shape mismatch")
    if search.get("quotient_mode_count") != 3:
        raise AssertionError("marked big-cell quotient mode count mismatch")
    if search.get("mode_rank_histogram") != {"11": 1, "14": 1, "16": 1}:
        raise AssertionError("marked big-cell quotient rank histogram mismatch")
    if search.get("rank12_mode_count") != 0:
        raise AssertionError("marked big-cell quotient rank12 count mismatch")
    if search.get("self_orthogonal_mode_count") != 0:
        raise AssertionError("marked big-cell quotient self-orthogonal count mismatch")
    if search.get("all_modes_fail_rank12_precondition") is not True:
        raise AssertionError("marked big-cell quotient rank gate mismatch")
    if search.get("all_modes_fail_self_orthogonal_precondition") is not True:
        raise AssertionError("marked big-cell quotient orthogonality gate mismatch")

    profile = search.get("d20_selector_duad_profile", {})
    if profile.get("selector_duad_count") != 15:
        raise AssertionError("marked big-cell quotient selector-duad count mismatch")
    if profile.get("all_selector_duads_have_two_edges") is not True:
        raise AssertionError("marked big-cell quotient selector-duad multiplicity mismatch")
    if profile.get("selector_duad_index_set") != list(range(15)):
        raise AssertionError("marked big-cell quotient selector-duad index mismatch")
    if len(search.get("quotient_column_order", [])) != 16:
        raise AssertionError("marked big-cell quotient column order length mismatch")

    modes = _mode_map(artifact)
    if set(modes) != set(MODE_NAMES):
        raise AssertionError("marked big-cell quotient mode names mismatch")
    for mode_name, expected_rank in EXPECTED_MODE_RANKS.items():
        mode = modes[mode_name]
        if mode.get("reduced_rank") != expected_rank:
            raise AssertionError(f"{mode_name} rank mismatch")
        if mode.get("output_length") != 16:
            raise AssertionError(f"{mode_name} output length mismatch")
        if mode.get("weight_histogram") != EXPECTED_WEIGHT_HISTOGRAMS[mode_name]:
            raise AssertionError(f"{mode_name} weight histogram mismatch")
        if mode.get("rank12_precondition_pass") is not False:
            raise AssertionError(f"{mode_name} rank gate mismatch")
        if mode.get("self_orthogonal") is not False:
            raise AssertionError(f"{mode_name} self-orthogonal mismatch")
        if mode.get("self_orthogonal_precondition_pass") is not False:
            raise AssertionError(f"{mode_name} orthogonality gate mismatch")
        if mode.get("doubly_even") is not False:
            raise AssertionError(f"{mode_name} doubly-even mismatch")

    gate = artifact.get("candidate_gate", {})
    if gate.get("tested_modes") != list(MODE_NAMES):
        raise AssertionError("marked big-cell quotient candidate gate mode mismatch")
    if gate.get("rank12_mode_count") != 0 or gate.get("self_orthogonal_mode_count") != 0:
        raise AssertionError("marked big-cell quotient candidate gate count mismatch")
    if gate.get("basis_compare_attempted") is not False:
        raise AssertionError("marked big-cell quotient basis boundary mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.sector33_w24_marked_big_cell_quotient_search@1":
        raise AssertionError("marked big-cell quotient report schema mismatch")
    if report.get("status") != "D20_SECTOR33_W24_MARKED_BIG_CELL_QUOTIENT_SEARCH_CERTIFIED":
        raise AssertionError("marked big-cell quotient report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("marked big-cell quotient report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("marked big-cell quotient report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("marked big-cell quotient report artifact hash mismatch")
    witness = report.get("witness", {})
    if witness.get("target_golay_profile") != artifact.get("target_golay_profile"):
        raise AssertionError("marked big-cell quotient report target mismatch")
    if witness.get("marked_big_cell_profile") != artifact.get("marked_big_cell_profile"):
        raise AssertionError("marked big-cell quotient report big-cell mismatch")
    if witness.get("quotient_search") != artifact.get("quotient_search"):
        raise AssertionError("marked big-cell quotient report search mismatch")
    if witness.get("candidate_gate") != artifact.get("candidate_gate"):
        raise AssertionError("marked big-cell quotient report gate mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("marked big-cell quotient report checks mismatch")
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_big_cell_quotient_search_manifest@1"
    ):
        raise AssertionError("marked big-cell quotient manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("marked big-cell quotient manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("marked big-cell quotient manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("marked big-cell quotient manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("marked big-cell quotient registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("marked big-cell quotient registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("marked big-cell quotient registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_sector33_w24_marked_big_cell_quotient_search()
    print("D20 sector33 W24 marked big-cell quotient search proof obligation validated")
