from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_golay_entropy_direct_attempt_import import (
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
    from derive_d20_golay_entropy_direct_attempt_import import (
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
    "handoff_manifest_declares_direct_attempt_files",
    "handoff_manifest_file_hashes_all_match",
    "direct_certificate_status_matches_expected",
    "handoff_report_records_no_counterexample_status",
    "certificate_summary_has_shells_12_and_16",
    "summary_csv_matches_certificate_summary",
    "no_counterexample_recorded_for_each_shell",
    "all_csv_exceeds_zero_counts_are_zero",
    "max_observed_F_within_roundoff",
    "w24_endpoint_is_certified",
    "w24_weight_enumerator_matches_direct_attempt",
    "dodecad_and_weight16_shell_sizes_match",
    "golay_hamming_probe_records_morphism_open",
    "sector33_w24_local_matching_still_open",
    "handoff_internal_certificate_hash_not_used_as_repo_self_hash",
    "final_entropy_inequality_not_certified",
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


def validate_d20_golay_entropy_direct_attempt_import() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.golay_entropy_direct_attempt_import.artifact@1":
        raise AssertionError("Golay entropy import artifact schema mismatch")
    if artifact.get("status") != "D20_GOLAY_ENTROPY_DIRECT_ATTEMPT_IMPORTED_NO_COUNTEREXAMPLE":
        raise AssertionError("Golay entropy import artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay entropy import artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay entropy import artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Golay entropy import checks mismatch")

    direct = artifact.get("direct_attempt", {})
    if direct.get("status") != "DIRECT_VARIATIONAL_AND_SANDPILE_ATTEMPT_COMPLETE_NO_COUNTEREXAMPLE":
        raise AssertionError("Golay entropy direct-attempt status mismatch")
    if direct.get("weight_enumerator") != {"0": 1, "8": 759, "12": 2576, "16": 759, "24": 1}:
        raise AssertionError("Golay entropy weight enumerator mismatch")
    if float(direct.get("max_observed_F")) > 3e-15:
        raise AssertionError("Golay entropy max F exceeds roundoff threshold")
    summary = direct.get("summary", [])
    if [row.get("shell") for row in summary] != [12, 16]:
        raise AssertionError("Golay entropy shell summary mismatch")
    if any(row.get("any_counterexample_found") is not False for row in summary):
        raise AssertionError("Golay entropy summary unexpectedly found counterexample")
    if summary[0].get("blocks") != 2576 or summary[1].get("blocks") != 759:
        raise AssertionError("Golay entropy shell block counts mismatch")

    integrity = artifact.get("handoff_integrity", {})
    if not all(row.get("matches") is True for row in integrity.get("manifest_file_hashes", {}).values()):
        raise AssertionError("Golay entropy handoff manifest hash mismatch")
    if integrity.get("recorded_certificate_hash_matches_repo_canonical_hash") is not False:
        raise AssertionError("Golay entropy handoff hash boundary mismatch")

    connection = artifact.get("connection_to_current_problem", {})
    if connection.get("w24_endpoint", {}).get("status") != "D20_W24_HEXACODE_ROW_ALPHABETIZATION_CERTIFIED":
        raise AssertionError("Golay entropy W24 endpoint status mismatch")
    if connection.get("sector33_to_w24_map_status") != "OPEN_NOT_CONSTRUCTED":
        raise AssertionError("Golay entropy sector33 map boundary mismatch")

    if report.get("schema") != "d20.proof_obligation.golay_entropy_direct_attempt_import@1":
        raise AssertionError("Golay entropy import report schema mismatch")
    if report.get("status") != "D20_GOLAY_ENTROPY_DIRECT_ATTEMPT_IMPORT_CERTIFIED":
        raise AssertionError("Golay entropy import report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Golay entropy import report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("Golay entropy import report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay entropy import report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay entropy import report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_golay_entropy_direct_attempt_import.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_golay_entropy_direct_attempt_import.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.golay_entropy_direct_attempt_import_manifest@1":
        raise AssertionError("Golay entropy import manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay entropy import manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay entropy import manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay entropy import manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay entropy import manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Golay entropy import registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay entropy import registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Golay entropy import registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_golay_entropy_direct_attempt_import()
    print("D20 Golay entropy direct-attempt import validated")
