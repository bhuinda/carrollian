from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_sector33_w24_mixed_duad_quotient_orthogonality_prune import (
        CHOICE_NAMES,
        LEFT_DUAD_COUNT,
        build_artifact,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_sector33_w24_mixed_duad_quotient_orthogonality_prune import (
        CHOICE_NAMES,
        LEFT_DUAD_COUNT,
        build_artifact,
    )


THEOREM_ID = "d20_sector33_w24_mixed_duad_quotient_orthogonality_prune"
ARTIFACT_REL = "generated/d20_sector33_w24_mixed_duad_quotient_orthogonality_prune.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "d20_json": "d20.json",
    "w24_row_alphabetization": (
        "data/invariants/d20/proof_obligations/d20_w24_hexacode_row_alphabetization/report.json"
    ),
    "marked_big_cell_quotient_search": (
        "data/invariants/d20/proof_obligations/d20_sector33_w24_marked_big_cell_quotient_search/report.json"
    ),
    "sector33_dual": "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json",
    "wu_spinh_6j_marking": "data/selectors/wu_spinh_6j_marking.json",
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


def validate_d20_sector33_w24_mixed_duad_quotient_orthogonality_prune() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != (
        "d20.proof_obligation.sector33_w24_mixed_duad_quotient_orthogonality_prune.artifact@1"
    ):
        raise AssertionError("mixed duad quotient artifact schema mismatch")
    if artifact.get("status") != (
        "D20_SECTOR33_W24_MIXED_DUAD_QUOTIENT_ORTHOGONALITY_PRUNE_DERIVED"
    ):
        raise AssertionError("mixed duad quotient artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("mixed duad quotient artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("mixed duad quotient artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "d20_input_is_certified",
        "w24_row_alphabetization_is_certified",
        "marked_big_cell_quotient_input_is_certified",
        "sector33_dual_input_is_certified",
        "wu_marking_is_certified_external_boundary",
        "source_matrix_shape_is_21_by_31",
        "d20_selector_duad_profile_has_15_pairs",
        "d20_selector_duads_have_two_edges_each",
        "big_cell_pair_order_matches_d20_selector_duad_index",
        "choice_family_size_is_3_to_15",
        "gram_upper_triangle_has_231_coordinates",
        "meet_in_middle_split_is_7_and_8",
        "left_assignment_count_is_3_to_7",
        "right_assignment_count_is_3_to_8",
        "left_gram_states_are_collision_free",
        "right_gram_states_are_collision_free",
        "no_matching_gram_state_pairs",
        "no_mixed_assignment_is_self_orthogonal",
        "all_mixed_assignments_pruned_by_orthogonality",
        "rank12_count_not_needed_after_orthogonality_prune",
        "explicit_morphism_remains_open",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("mixed duad quotient check mismatch")

    target = artifact.get("target_golay_profile", {})
    if target.get("length") != 24 or target.get("rank") != 12:
        raise AssertionError("mixed duad quotient target Golay profile mismatch")
    if target.get("weight_histogram") != {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1}:
        raise AssertionError("mixed duad quotient target Golay histogram mismatch")

    big_cell = artifact.get("marked_big_cell_profile", {})
    if big_cell.get("pair_order_matches_d20_selector_duad_index") is not True:
        raise AssertionError("mixed duad quotient big-cell order mismatch")
    if big_cell.get("golay_selector_constructed") is not False:
        raise AssertionError("mixed duad quotient external boundary mismatch")

    search = artifact.get("mixed_orthogonality_search", {})
    if search.get("source_matrix") != "sector33_primal_mod2":
        raise AssertionError("mixed duad quotient source matrix mismatch")
    if search.get("source_shape") != {"rows": 21, "cols": 31}:
        raise AssertionError("mixed duad quotient source shape mismatch")
    profile = search.get("d20_selector_duad_profile", {})
    if profile.get("selector_duad_count") != 15:
        raise AssertionError("mixed duad quotient selector-duad count mismatch")
    if profile.get("all_selector_duads_have_two_edges") is not True:
        raise AssertionError("mixed duad quotient selector-duad multiplicity mismatch")
    if profile.get("selector_duad_index_set") != list(range(15)):
        raise AssertionError("mixed duad quotient selector-duad index mismatch")

    family = search.get("choice_family", {})
    if family.get("choice_names") != list(CHOICE_NAMES):
        raise AssertionError("mixed duad quotient choice names mismatch")
    if family.get("choice_count_per_duad") != 3:
        raise AssertionError("mixed duad quotient choice count mismatch")
    if family.get("duad_count") != 15:
        raise AssertionError("mixed duad quotient family duad count mismatch")
    if family.get("assignment_count") != 14348907:
        raise AssertionError("mixed duad quotient assignment count mismatch")
    if family.get("scalar_source_element_id") != 30:
        raise AssertionError("mixed duad quotient scalar mismatch")
    if len(family.get("column_options", [])) != 15:
        raise AssertionError("mixed duad quotient column option count mismatch")
    if not all(row.get("choice_names") == list(CHOICE_NAMES) for row in family.get("column_options", [])):
        raise AssertionError("mixed duad quotient per-duad choice names mismatch")

    gram = search.get("gram_encoding", {})
    if gram.get("row_count") != 21:
        raise AssertionError("mixed duad quotient gram row count mismatch")
    if gram.get("upper_triangle_coordinate_count") != 231:
        raise AssertionError("mixed duad quotient gram coordinate count mismatch")
    if not isinstance(gram.get("scalar_gram_hex"), str) or not gram.get("scalar_gram_hex"):
        raise AssertionError("mixed duad quotient scalar gram missing")

    mitm = search.get("meet_in_middle", {})
    if mitm.get("left_duad_count") != LEFT_DUAD_COUNT or mitm.get("right_duad_count") != 8:
        raise AssertionError("mixed duad quotient split mismatch")
    if mitm.get("left_assignment_count") != 2187:
        raise AssertionError("mixed duad quotient left assignment count mismatch")
    if mitm.get("right_assignment_count") != 6561:
        raise AssertionError("mixed duad quotient right assignment count mismatch")
    if mitm.get("left_gram_state_count") != 2187:
        raise AssertionError("mixed duad quotient left state count mismatch")
    if mitm.get("right_gram_state_count") != 6561:
        raise AssertionError("mixed duad quotient right state count mismatch")
    if mitm.get("left_max_state_multiplicity") != 1:
        raise AssertionError("mixed duad quotient left state multiplicity mismatch")
    if mitm.get("right_max_state_multiplicity") != 1:
        raise AssertionError("mixed duad quotient right state multiplicity mismatch")
    if mitm.get("matching_state_pair_count") != 0:
        raise AssertionError("mixed duad quotient matching state pair mismatch")
    if mitm.get("self_orthogonal_assignment_count") != 0:
        raise AssertionError("mixed duad quotient self-orthogonal count mismatch")

    gate = search.get("candidate_gate", {})
    if gate.get("rank12_count_computed") is not False:
        raise AssertionError("mixed duad quotient rank boundary mismatch")
    if gate.get("assignment_count_pruned_by_orthogonality") != 14348907:
        raise AssertionError("mixed duad quotient pruned count mismatch")
    if gate.get("basis_compare_attempted") is not False:
        raise AssertionError("mixed duad quotient basis boundary mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != (
        "d20.proof_obligation.sector33_w24_mixed_duad_quotient_orthogonality_prune@1"
    ):
        raise AssertionError("mixed duad quotient report schema mismatch")
    if report.get("status") != (
        "D20_SECTOR33_W24_MIXED_DUAD_QUOTIENT_ORTHOGONALITY_PRUNE_CERTIFIED"
    ):
        raise AssertionError("mixed duad quotient report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("mixed duad quotient report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("mixed duad quotient report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("mixed duad quotient report artifact hash mismatch")
    witness = report.get("witness", {})
    if witness.get("target_golay_profile") != artifact.get("target_golay_profile"):
        raise AssertionError("mixed duad quotient report target mismatch")
    if witness.get("marked_big_cell_profile") != artifact.get("marked_big_cell_profile"):
        raise AssertionError("mixed duad quotient report big-cell mismatch")
    if witness.get("mixed_orthogonality_search") != artifact.get("mixed_orthogonality_search"):
        raise AssertionError("mixed duad quotient report search mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("mixed duad quotient report checks mismatch")
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != (
        "d20.proof_obligation.sector33_w24_mixed_duad_quotient_orthogonality_prune_manifest@1"
    ):
        raise AssertionError("mixed duad quotient manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("mixed duad quotient manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("mixed duad quotient manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("mixed duad quotient manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("mixed duad quotient registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("mixed duad quotient registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("mixed duad quotient registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_sector33_w24_mixed_duad_quotient_orthogonality_prune()
    print("D20 sector33 W24 mixed duad quotient orthogonality prune proof obligation validated")
