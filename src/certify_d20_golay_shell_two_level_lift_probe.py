from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_golay_shell_two_level_lift_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        TOL,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_golay_shell_two_level_lift_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        TOL,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()
CSV_REL = (OUT_DIR / "two_level_lift_profiles.csv").relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "w24_endpoint_certified",
    "archive_indicator_shell_input_certified",
    "direct_entropy_attempt_import_certified",
    "generated_code_has_4096_words",
    "generated_code_weight_histogram_matches_w24",
    "two_level_rows_nonempty",
    "all_selected_two_level_maxima_within_tolerance",
    "all_selected_endpoint_limits_within_tolerance",
    "equality_orbit_seen_at_t_zero",
    "final_arbitrary_vector_theorem_not_certified",
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


def validate_d20_golay_shell_two_level_lift_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.golay_shell_two_level_lift_probe.artifact@1":
        raise AssertionError("Golay shell two-level artifact schema mismatch")
    if artifact.get("status") != "D20_GOLAY_SHELL_TWO_LEVEL_LIFT_PROBE_NO_COUNTEREXAMPLE":
        raise AssertionError("Golay shell two-level artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay shell two-level artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay shell two-level artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("Golay shell two-level checks mismatch")

    selection = artifact.get("selection", {})
    if selection.get("split_mask_count", 0) < 4000:
        raise AssertionError("Golay shell two-level split family unexpectedly small")
    if selection.get("two_level_row_count") != 2 * selection.get("split_mask_count"):
        raise AssertionError("Golay shell two-level row count mismatch")
    if selection.get("shells") != [12, 16]:
        raise AssertionError("Golay shell two-level shell list mismatch")

    witness = artifact.get("witness", {})
    if float(witness.get("max_F")) > TOL:
        raise AssertionError("Golay shell two-level maximum exceeds tolerance")
    _check_input_file(witness.get("csv", {}), CSV_REL, "two-level CSV")

    top_rows = witness.get("top_rows", [])
    if not top_rows:
        raise AssertionError("Golay shell two-level top rows missing")
    if any(row.get("exceeds_tolerance") is not False for row in top_rows):
        raise AssertionError("Golay shell two-level top row exceeds tolerance")

    if report.get("schema") != "d20.proof_obligation.golay_shell_two_level_lift_probe@1":
        raise AssertionError("Golay shell two-level report schema mismatch")
    if report.get("status") != "D20_GOLAY_SHELL_TWO_LEVEL_LIFT_PROBE_CERTIFIED_NO_COUNTEREXAMPLE":
        raise AssertionError("Golay shell two-level report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Golay shell two-level report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("Golay shell two-level report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay shell two-level report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay shell two-level report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_golay_shell_two_level_lift_probe.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_golay_shell_two_level_lift_probe.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.golay_shell_two_level_lift_probe_manifest@1":
        raise AssertionError("Golay shell two-level manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay shell two-level manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Golay shell two-level manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay shell two-level manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Golay shell two-level manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Golay shell two-level registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Golay shell two-level registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Golay shell two-level registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_golay_shell_two_level_lift_probe()
    print("D20 Golay shell two-level lift probe validated")
