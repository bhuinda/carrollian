from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_lift_negative_space_crop_window_artifact import (
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
    from derive_d20_lift_negative_space_crop_window_artifact import (
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
    "source_visualization_loaded",
    "robust_oblongness_theorem_certified",
    "intrinsic_hex_metric_certified",
    "projection_null_audit_certified",
    "dynamic_half_span_is_13_5",
    "dynamic_frequency_equals_two_times_half_span",
    "small_fixed_windows_track_two_times_half_span",
    "uncropped_lift_coordinates_do_not_have_axis27",
    "uncropped_lift_coordinates_low_frequency_dominated",
    "wide_windows_are_low_frequency_dominated",
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


def validate_d20_lift_negative_space_crop_window_artifact() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.lift_negative_space_crop_window_artifact.artifact@1":
        raise AssertionError("crop-window artifact schema mismatch")
    if artifact.get("status") != "D20_LIFT_NEGATIVE_SPACE_CROP_WINDOW_ARTIFACT_DERIVED":
        raise AssertionError("crop-window artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("crop-window artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("crop-window artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("crop-window checks mismatch")

    dynamic = artifact.get("dynamic_crop", {})
    if abs(float(dynamic.get("half_span")) - 13.5) > 1e-12:
        raise AssertionError("dynamic half-span mismatch")
    if int(dynamic.get("dominant_high_axis_frequency")) != 27:
        raise AssertionError("dynamic high-axis frequency mismatch")
    for row in artifact.get("fixed_small_windows", []):
        if int(row.get("dominant_high_axis_frequency")) != int(row.get("expected_scale_frequency")):
            raise AssertionError(f"{row.get('id')} frequency does not track window scale")
    raw = artifact.get("uncropped_lift_coordinates", {})
    if raw.get("dominant_high_axis_frequency") == 27:
        raise AssertionError("uncropped state unexpectedly has axis-27")
    if raw.get("low_frequency_dominated_top_four") is not True:
        raise AssertionError("uncropped state is not low-frequency dominated")
    if any(row.get("low_frequency_dominated_top_four") is not True for row in artifact.get("fixed_wide_windows", [])):
        raise AssertionError("wide fixed window is not low-frequency dominated")

    if report.get("schema") != "d20.proof_obligation.lift_negative_space_crop_window_artifact@1":
        raise AssertionError("crop-window report schema mismatch")
    if report.get("status") != "D20_LIFT_NEGATIVE_SPACE_CROP_WINDOW_ARTIFACT_CERTIFIED":
        raise AssertionError("crop-window report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("crop-window report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("crop-window report checks differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("crop-window report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("crop-window report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("visualization", {}),
        "generated/d20_sandpile_visualization.html",
        "visualization input",
    )
    _check_input_file(
        report.get("inputs", {}).get("projection_null_audit_report", {}),
        "data/invariants/d20/proof_obligations/d20_lift_negative_space_projection_null_audit/report.json",
        "projection-null input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_lift_negative_space_crop_window_artifact.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.lift_negative_space_crop_window_artifact_manifest@1":
        raise AssertionError("crop-window manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("crop-window manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("crop-window manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("crop-window manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("crop-window manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("crop-window registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("crop-window registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("crop-window registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_lift_negative_space_crop_window_artifact()
    print("D20 lift negative-space crop/window artifact validated")
