from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_sector33_w24_per_edge_rowspace_prune import (
        F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP,
        build_artifact,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_sector33_w24_per_edge_rowspace_prune import (
        F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP,
        build_artifact,
    )


THEOREM_ID = "d20_sector33_w24_per_edge_rowspace_prune"
ARTIFACT_REL = "generated/d20_sector33_w24_per_edge_rowspace_prune.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "d20_json": "d20.json",
    "w24_row_alphabetization": (
        "data/invariants/d20/proof_obligations/d20_w24_hexacode_row_alphabetization/report.json"
    ),
    "typed_coordinate_search": (
        "data/invariants/d20/proof_obligations/d20_sector33_w24_typed_coordinate_search/report.json"
    ),
    "f4_row_lift_solver": (
        "data/invariants/d20/proof_obligations/d20_sector33_w24_f4_row_lift_solver/report.json"
    ),
    "sector33_dual": "data/invariants/d20/theorems/d20_oriented_matroid_sector33_dual/report.json",
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


def validate_d20_sector33_w24_per_edge_rowspace_prune() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.sector33_w24_per_edge_rowspace_prune.artifact@1":
        raise AssertionError("sector33 W24 per-edge rowspace prune artifact schema mismatch")
    if artifact.get("status") != "D20_SECTOR33_W24_PER_EDGE_ROWSPACE_PRUNE_DERIVED":
        raise AssertionError("sector33 W24 per-edge rowspace prune artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("sector33 W24 per-edge rowspace prune artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("sector33 W24 per-edge rowspace prune artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "w24_row_alphabetization_is_certified",
        "typed_coordinate_search_input_is_certified",
        "f4_row_lift_solver_input_is_certified",
        "sector33_dual_input_is_certified",
        "target_golay_rank_is_12",
        "relaxed_h6_maps_exist",
        "relaxed_h6_maps_balance_every_pair_family_and_extra",
        "f4_row_assignment_multiplier_is_24_to_6",
        "rowspace_case_count_is_50",
        "all_deleted_rowspaces_have_length_24",
        "primal_deleted_rank_histogram_is_18_19",
        "dual_deleted_rank_histogram_is_3",
        "no_deleted_rowspace_has_rank_12",
        "column_permutation_cannot_change_rank",
        "all_per_edge_coordinate_bijections_pruned_before_golay_basis_compare",
        "explicit_morphism_remains_open",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("sector33 W24 per-edge rowspace prune check mismatch")

    target = artifact.get("target_golay_profile", {})
    if target.get("length") != 24 or target.get("rank") != 12:
        raise AssertionError("sector33 W24 per-edge rowspace prune target mismatch")
    if target.get("weight_histogram") != {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1}:
        raise AssertionError("sector33 W24 per-edge rowspace prune target histogram mismatch")

    h6 = artifact.get("balanced_relaxed_h6_coordinate_maps", {})
    expected_by_family = {
        "shared_duad": 665760,
        "swapped_pair": 791215,
        "missing_pair": 358440,
    }
    if h6.get("balanced_h6_map_count_by_pair_family") != expected_by_family:
        raise AssertionError("sector33 W24 per-edge rowspace prune H6 count mismatch")
    expected_total = sum(expected_by_family.values())
    if h6.get("balanced_h6_map_count_total") != expected_total:
        raise AssertionError("sector33 W24 per-edge rowspace prune H6 total mismatch")
    if h6.get("f4_row_assignments_per_balanced_h6_map") != F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP:
        raise AssertionError("sector33 W24 per-edge rowspace prune F4 multiplier mismatch")
    if h6.get("coordinate_bijection_count_pruned_by_rank") != (
        expected_total * F4_ROW_ASSIGNMENTS_PER_BALANCED_H6_MAP
    ):
        raise AssertionError("sector33 W24 per-edge rowspace prune coordinate count mismatch")
    if h6.get("extra_removed_count") != 25 or h6.get("all_pair_families_balance_every_extra") is not True:
        raise AssertionError("sector33 W24 per-edge rowspace prune H6 extra mismatch")

    prune = artifact.get("deleted_rowspace_prune", {})
    if prune.get("fixed_removed_cocircuit") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("sector33 W24 per-edge rowspace prune cocircuit mismatch")
    if prune.get("extra_removed_count") != 25 or prune.get("rowspace_case_count") != 50:
        raise AssertionError("sector33 W24 per-edge rowspace prune case count mismatch")
    if prune.get("rank12_candidate_count_total") != 0:
        raise AssertionError("sector33 W24 per-edge rowspace prune rank12 mismatch")
    if prune.get("all_remaining_sets_have_24_edges") is not True:
        raise AssertionError("sector33 W24 per-edge rowspace prune length mismatch")
    sources = prune.get("source_summaries", {})
    primal = sources.get("sector33_primal_mod2", {})
    dual = sources.get("sector33_dual_mod2", {})
    if primal.get("rank_histogram") != {"18": 5, "19": 20}:
        raise AssertionError("sector33 W24 per-edge rowspace prune primal rank mismatch")
    if dual.get("rank_histogram") != {"3": 25}:
        raise AssertionError("sector33 W24 per-edge rowspace prune dual rank mismatch")
    if primal.get("remaining_length_histogram") != {"24": 25}:
        raise AssertionError("sector33 W24 per-edge rowspace prune primal length mismatch")
    if dual.get("remaining_length_histogram") != {"24": 25}:
        raise AssertionError("sector33 W24 per-edge rowspace prune dual length mismatch")
    if dual.get("self_orthogonal_histogram_for_enumerated_low_rank_codes") != {"False": 25}:
        raise AssertionError("sector33 W24 per-edge rowspace prune dual orthogonality mismatch")

    argument = artifact.get("rank_invariance_argument", {})
    if argument.get("basis_compare_attempted") is not False:
        raise AssertionError("sector33 W24 per-edge rowspace prune basis compare boundary mismatch")
    if argument.get("target_rank") != 12:
        raise AssertionError("sector33 W24 per-edge rowspace prune target rank argument mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.sector33_w24_per_edge_rowspace_prune@1":
        raise AssertionError("sector33 W24 per-edge rowspace prune report schema mismatch")
    if report.get("status") != "D20_SECTOR33_W24_PER_EDGE_ROWSPACE_PRUNE_CERTIFIED":
        raise AssertionError("sector33 W24 per-edge rowspace prune report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sector33 W24 per-edge rowspace prune report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 per-edge rowspace prune report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("sector33 W24 per-edge rowspace prune report artifact hash mismatch")
    witness = report.get("witness", {})
    if witness.get("target_golay_profile") != artifact.get("target_golay_profile"):
        raise AssertionError("sector33 W24 per-edge rowspace prune report target mismatch")
    if witness.get("balanced_relaxed_h6_coordinate_maps") != artifact.get(
        "balanced_relaxed_h6_coordinate_maps"
    ):
        raise AssertionError("sector33 W24 per-edge rowspace prune report H6 mismatch")
    if witness.get("deleted_rowspace_prune") != artifact.get("deleted_rowspace_prune"):
        raise AssertionError("sector33 W24 per-edge rowspace prune report rowspace mismatch")
    if witness.get("rank_invariance_argument") != artifact.get("rank_invariance_argument"):
        raise AssertionError("sector33 W24 per-edge rowspace prune report argument mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("sector33 W24 per-edge rowspace prune report checks mismatch")
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != "d20.proof_obligation.sector33_w24_per_edge_rowspace_prune_manifest@1":
        raise AssertionError("sector33 W24 per-edge rowspace prune manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 per-edge rowspace prune manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("sector33 W24 per-edge rowspace prune manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("sector33 W24 per-edge rowspace prune manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("sector33 W24 per-edge rowspace prune registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 per-edge rowspace prune registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sector33 W24 per-edge rowspace prune registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_sector33_w24_per_edge_rowspace_prune()
    print("D20 sector33 W24 per-edge rowspace prune proof obligation validated")
