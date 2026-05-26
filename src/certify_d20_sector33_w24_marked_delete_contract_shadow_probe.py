from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_sector33_w24_marked_delete_contract_shadow_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_sector33_w24_marked_delete_contract_shadow_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "w24_row_alphabetization_is_certified",
    "minor_puncture_search_input_is_certified_negative",
    "deletion_shadow_obstruction_input_is_certified",
    "sector33_dual_input_is_certified",
    "target_allowed_weights_are_0_8_12_16_24",
    "delete_contract_candidate_count_is_6400",
    "primal_delete_contract_shadow_candidate_count_is_3200",
    "primal_delete_contract_shadow_has_no_golay_weight_compatible_case",
    "dual_delete_contract_shadow_candidate_count_is_3200",
    "dual_delete_contract_shadow_compatible_count_is_70",
    "dual_compatible_shadows_are_rank0_or_rank1",
    "dual_has_one_unique_nontrivial_weight8_support",
    "unique_dual_octad_not_in_current_w24_under_identity_labels",
    "delete_contract_route_reduced_to_typed_octad_placement",
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
        raise AssertionError(f"{label} path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} file hash mismatch")


def validate_d20_sector33_w24_marked_delete_contract_shadow_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_delete_contract_shadow_probe.artifact@1"
    ):
        raise AssertionError("delete/contract shadow artifact schema mismatch")
    if artifact.get("status") != "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_DERIVED":
        raise AssertionError("delete/contract shadow artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("delete/contract shadow artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("delete/contract shadow artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("delete/contract shadow checks mismatch")

    analysis = artifact.get("delete_contract_shadow_analysis", {})
    if analysis.get("candidate_count") != 6400:
        raise AssertionError("delete/contract candidate count mismatch")
    if analysis.get("allowed_golay_weights") != [0, 8, 12, 16, 24]:
        raise AssertionError("delete/contract allowed weights mismatch")
    shadows = analysis.get("shadow_summaries", {})
    primal = shadows.get("primal_orthogonal_shadow", {})
    dual = shadows.get("dual_rowspace_shadow", {})
    if primal.get("candidate_count") != 3200:
        raise AssertionError("primal candidate count mismatch")
    if primal.get("golay_weight_compatible_case_count") != 0:
        raise AssertionError("unexpected primal compatible case")
    if primal.get("source_rank_histogram") != {
        "14": 450,
        "15": 1040,
        "16": 986,
        "17": 542,
        "18": 162,
        "19": 20,
    }:
        raise AssertionError("primal source rank histogram mismatch")
    if dual.get("candidate_count") != 3200:
        raise AssertionError("dual candidate count mismatch")
    if dual.get("golay_weight_compatible_case_count") != 70:
        raise AssertionError("dual compatible count mismatch")
    if dual.get("golay_weight_compatible_rank_histogram") != {"0": 55, "1": 15}:
        raise AssertionError("dual compatible rank histogram mismatch")
    supports = dual.get("unique_nonzero_supports", [])
    if supports != [
        {
            "case_count": 15,
            "extra_removed_values": [5, 6, 9],
            "support": [0, 3, 12, 13, 14, 16, 20, 24],
            "support_weight": 8,
        }
    ]:
        raise AssertionError("unique dual octad support mismatch")
    identity = artifact.get("unique_dual_octad_identity_w24_test", [])
    if len(identity) != 1 or identity[0].get("contained_in_current_w24_golay_under_identity_labels") is not False:
        raise AssertionError("identity W24 containment mismatch")

    if report.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_delete_contract_shadow_probe@1"
    ):
        raise AssertionError("delete/contract shadow report schema mismatch")
    if report.get("status") != "D20_SECTOR33_W24_MARKED_DELETE_CONTRACT_SHADOW_PROBE_CERTIFIED":
        raise AssertionError("delete/contract shadow report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("delete/contract shadow report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("delete/contract shadow report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("delete/contract shadow report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("delete/contract shadow report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_sector33_w24_marked_delete_contract_shadow_probe.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_sector33_w24_marked_delete_contract_shadow_probe.py",
        "validator input",
    )

    if manifest.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_delete_contract_shadow_probe_manifest@1"
    ):
        raise AssertionError("delete/contract shadow manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("delete/contract shadow manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("delete/contract shadow manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("delete/contract shadow manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("delete/contract shadow manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("delete/contract shadow registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("delete/contract shadow registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("delete/contract shadow registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_sector33_w24_marked_delete_contract_shadow_probe()
    print("D20 sector33 W24 marked delete/contract shadow probe validated")
