from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_sector33_w24_typed_coordinate_search import build_artifact
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_sector33_w24_typed_coordinate_search import build_artifact


THEOREM_ID = "d20_sector33_w24_typed_coordinate_search"
ARTIFACT_REL = "generated/d20_sector33_w24_typed_coordinate_search.json"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"

SOURCE_RELS = {
    "d20_json": "d20.json",
    "w24_row_alphabetization": (
        "data/invariants/d20/proof_obligations/d20_w24_hexacode_row_alphabetization/report.json"
    ),
    "minor_puncture_search": (
        "data/invariants/d20/proof_obligations/d20_golay_hamming_minor_puncture_search/report.json"
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


def validate_d20_sector33_w24_typed_coordinate_search() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.sector33_w24_typed_coordinate_search.artifact@1":
        raise AssertionError("sector33 W24 typed coordinate artifact schema mismatch")
    if artifact.get("status") != "D20_SECTOR33_W24_TYPED_COORDINATE_SEARCH_DERIVED":
        raise AssertionError("sector33 W24 typed coordinate artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("sector33 W24 typed coordinate artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("sector33 W24 typed coordinate artifact does not replay")

    checks = artifact.get("checks", {})
    required_checks = {
        "w24_row_alphabetization_is_certified",
        "sector33_dual_input_is_certified",
        "minor_puncture_search_is_certified_negative",
        "target_w24_is_h6_by_f4",
        "sector33_ground_is_30_edges_plus_e33",
        "fixed_cocircuit_has_five_edges_plus_e33",
        "each_lambda2_h6_duad_has_two_sector_edges",
        "extra_removed_pool_has_25_edges",
        "deterministic_projection_candidate_count_is_150",
        "all_deterministic_candidates_leave_24_edges",
        "no_deterministic_h6_projection_is_w24_balanced",
        "relaxed_pair_assignment_is_too_weak",
        "typed_coordinate_morphism_remains_open",
    }
    if set(checks) != required_checks or any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("sector33 W24 typed coordinate check mismatch")

    target = artifact.get("target_w24_type", {})
    if target.get("column_labels") != ["B-", "B+", "V-", "V+", "S-", "S+"]:
        raise AssertionError("sector33 W24 typed coordinate column labels mismatch")
    if len(target.get("row_f4_labels", [])) != 4 or target.get("coordinate_count") != 24:
        raise AssertionError("sector33 W24 typed coordinate target shape mismatch")

    source = artifact.get("sector33_edge_type", {})
    if source.get("ground_edge_count") != 30 or source.get("new_element_id") != 30:
        raise AssertionError("sector33 W24 typed coordinate source ground mismatch")
    if source.get("positive_cocircuit_support") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("sector33 W24 typed coordinate cocircuit mismatch")
    if len(source.get("lambda2_h6_duad_profile", {})) != 15:
        raise AssertionError("sector33 W24 typed coordinate duad profile mismatch")
    if not all(len(value) == 2 for value in source.get("lambda2_h6_duad_profile", {}).values()):
        raise AssertionError("sector33 W24 typed coordinate duad multiplicity mismatch")

    search = artifact.get("typed_search", {})
    if search.get("candidate_count") != 150 or search.get("balanced_candidate_count") != 0:
        raise AssertionError("sector33 W24 typed coordinate search count mismatch")
    if search.get("extra_removed_count") != 25 or len(search.get("extra_removed_pool", [])) != 25:
        raise AssertionError("sector33 W24 typed coordinate extra pool mismatch")
    if search.get("projection_rules") != [
        "shared_duad[0]",
        "shared_duad[1]",
        "swapped_pair[0]",
        "swapped_pair[1]",
        "missing_pair[0]",
        "missing_pair[1]",
    ]:
        raise AssertionError("sector33 W24 typed coordinate projection rules mismatch")
    if search.get("all_remaining_sets_have_24_edges") is not True:
        raise AssertionError("sector33 W24 typed coordinate remaining length mismatch")
    if search.get("best_l1_defect_from_four_per_h6_label") is None:
        raise AssertionError("sector33 W24 typed coordinate best defect missing")
    if int(search.get("best_l1_defect_from_four_per_h6_label")) <= 0:
        raise AssertionError("sector33 W24 typed coordinate unexpectedly balanced")

    relaxed = artifact.get("relaxed_assignment_boundary", {}).get(
        "balanced_extra_deletions_by_pair_family", {}
    )
    if sorted(relaxed) != ["missing_pair", "shared_duad", "swapped_pair"]:
        raise AssertionError("sector33 W24 typed coordinate relaxed family mismatch")
    if not all(len(value) == 25 for value in relaxed.values()):
        raise AssertionError("sector33 W24 typed coordinate relaxed assignment mismatch")

    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(artifact.get("source_reports", {}).get(key, {}), rel_path, f"artifact {key}")

    if report.get("schema") != "d20.proof_obligation.sector33_w24_typed_coordinate_search@1":
        raise AssertionError("sector33 W24 typed coordinate report schema mismatch")
    if report.get("status") != "D20_SECTOR33_W24_TYPED_COORDINATE_SEARCH_CERTIFIED":
        raise AssertionError("sector33 W24 typed coordinate report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sector33 W24 typed coordinate report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 typed coordinate report self hash mismatch")
    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact_sha:
        raise AssertionError("sector33 W24 typed coordinate report artifact hash mismatch")
    witness = report.get("witness", {})
    if witness.get("target_w24_type") != artifact.get("target_w24_type"):
        raise AssertionError("sector33 W24 typed coordinate report target mismatch")
    if witness.get("sector33_edge_type") != artifact.get("sector33_edge_type"):
        raise AssertionError("sector33 W24 typed coordinate report source mismatch")
    if witness.get("typed_search") != artifact.get("typed_search"):
        raise AssertionError("sector33 W24 typed coordinate report search mismatch")
    if witness.get("relaxed_assignment_boundary") != artifact.get("relaxed_assignment_boundary"):
        raise AssertionError("sector33 W24 typed coordinate report relaxed boundary mismatch")
    if report.get("checks") != artifact.get("checks"):
        raise AssertionError("sector33 W24 typed coordinate report checks mismatch")
    for key, rel_path in SOURCE_RELS.items():
        _check_input_file(report.get("inputs", {}).get(key, {}), rel_path, f"report {key}")

    if manifest.get("schema") != "d20.proof_obligation.sector33_w24_typed_coordinate_search_manifest@1":
        raise AssertionError("sector33 W24 typed coordinate manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 typed coordinate manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("sector33 W24 typed coordinate manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("sector33 W24 typed coordinate manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("sector33 W24 typed coordinate registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sector33 W24 typed coordinate registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sector33 W24 typed coordinate registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_sector33_w24_typed_coordinate_search()
    print("D20 sector33 W24 typed coordinate search proof obligation validated")
