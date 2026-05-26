from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_lift_spectral_poincare_audit import (
        ARTIFACT_PATH,
        BASELINE_NEAR_RETURN_DISTANCE_MAX,
        DIVERGENCE_GAIN_MIN,
        HORIZON_FRAMES,
        INDEX_PATH,
        INITIAL_DISTANCE_TOLERANCE,
        OUT_DIR,
        SAMPLE_STRIDE,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_lift_spectral_poincare_audit import (
        ARTIFACT_PATH,
        BASELINE_NEAR_RETURN_DISTANCE_MAX,
        DIVERGENCE_GAIN_MIN,
        HORIZON_FRAMES,
        INDEX_PATH,
        INITIAL_DISTANCE_TOLERANCE,
        OUT_DIR,
        SAMPLE_STRIDE,
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
    "visualization_data_loaded",
    "full_window_canvas_embedded",
    "recurrence_audit_certified",
    "laplacian_band_signature_matches_expected",
    "checkpoint_pair_matches_recurrence_nearest_return",
    "initial_distance_matches_recurrence_report",
    "initial_distance_is_near_return",
    "natural_branch_has_no_boundary_loss",
    "cursor_aligned_branch_has_no_boundary_loss",
    "natural_branch_diverges_from_near_return",
    "cursor_aligned_branch_diverges_from_near_return",
    "branches_stay_inside_full_window",
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


def _check_branch_summary(summary: dict[str, Any], label: str) -> None:
    if int(summary.get("horizon_frames", -1)) != HORIZON_FRAMES:
        raise AssertionError(f"{label} horizon mismatch")
    if int(summary.get("sample_stride", -1)) != SAMPLE_STRIDE:
        raise AssertionError(f"{label} stride mismatch")
    if int(summary.get("sample_count", -1)) != HORIZON_FRAMES // SAMPLE_STRIDE + 1:
        raise AssertionError(f"{label} sample count mismatch")
    if float(summary.get("initial_distance", 1.0)) >= BASELINE_NEAR_RETURN_DISTANCE_MAX:
        raise AssertionError(f"{label} initial distance is not a near-return")
    if float(summary.get("divergence_gain", 0.0)) <= DIVERGENCE_GAIN_MIN:
        raise AssertionError(f"{label} divergence gain too small")
    if summary.get("boundary_loss_range") != [0, 0]:
        raise AssertionError(f"{label} boundary loss mismatch")
    radius_range = summary.get("radius_range", [0.0, 999.0])
    if float(radius_range[1]) >= 32.0:
        raise AssertionError(f"{label} radius exceeds full-window guard")


def validate_d20_lift_spectral_poincare_audit() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.lift_spectral_poincare_audit.artifact@1":
        raise AssertionError("spectral Poincare artifact schema mismatch")
    if artifact.get("status") != "D20_LIFT_SPECTRAL_POINCARE_AUDIT_DERIVED":
        raise AssertionError("spectral Poincare artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral Poincare artifact self hash mismatch")

    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral Poincare artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("spectral Poincare checks mismatch")

    nearest = artifact.get("nearest_return", {})
    natural = artifact.get("natural_source_phase", {}).get("summary", {})
    aligned = artifact.get("cursor_aligned", {}).get("summary", {})
    if abs(float(nearest.get("distance", 1.0)) - float(natural.get("initial_distance", 0.0))) >= INITIAL_DISTANCE_TOLERANCE:
        raise AssertionError("spectral Poincare initial distance mismatch")
    _check_branch_summary(natural, "natural source-phase")
    _check_branch_summary(aligned, "cursor-aligned")

    if report.get("schema") != "d20.proof_obligation.lift_spectral_poincare_audit@1":
        raise AssertionError("spectral Poincare report schema mismatch")
    if report.get("status") != "D20_LIFT_SPECTRAL_POINCARE_AUDIT_CERTIFIED":
        raise AssertionError("spectral Poincare report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("spectral Poincare report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("spectral Poincare report checks differ from artifact")
    if report.get("witness", {}).get("natural_source_phase_summary") != natural:
        raise AssertionError("spectral Poincare natural summary differs from artifact")
    if report.get("witness", {}).get("cursor_aligned_summary") != aligned:
        raise AssertionError("spectral Poincare aligned summary differs from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral Poincare report self hash mismatch")

    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact input")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("report artifact internal hash mismatch")
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_lift_spectral_poincare_audit.py",
        "validator input",
    )
    _check_input_file(
        report.get("inputs", {}).get("visualization", {}),
        "generated/d20_sandpile_visualization.html",
        "visualization input",
    )
    _check_input_file(
        report.get("inputs", {}).get("recurrence_report", {}),
        "data/invariants/d20/proof_obligations/d20_lift_spectral_recurrence_audit/report.json",
        "recurrence report input",
    )

    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral Poincare report is not reproducible")

    if manifest.get("schema") != "d20.proof_obligation.lift_spectral_poincare_audit_manifest@1":
        raise AssertionError("spectral Poincare manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral Poincare manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral Poincare manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("spectral Poincare manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("spectral Poincare manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("spectral Poincare registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral Poincare registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("spectral Poincare registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_lift_spectral_poincare_audit()
    print("D20 lift spectral Poincare audit validated")
