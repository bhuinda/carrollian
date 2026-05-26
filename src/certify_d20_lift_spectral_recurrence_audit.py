from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_lift_spectral_recurrence_audit import (
        ARTIFACT_PATH,
        BASELINE_NEAR_RETURN_DISTANCE_MAX,
        EXPECTED_LAPLACIAN_BANDS,
        INDEX_PATH,
        OUT_DIR,
        PERTURBATION_NEAR_RETURN_DISTANCE_MAX,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_lift_spectral_recurrence_audit import (
        ARTIFACT_PATH,
        BASELINE_NEAR_RETURN_DISTANCE_MAX,
        EXPECTED_LAPLACIAN_BANDS,
        INDEX_PATH,
        OUT_DIR,
        PERTURBATION_NEAR_RETURN_DISTANCE_MAX,
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
    "spectral_timeseries_audit_certified",
    "laplacian_band_signature_matches_expected",
    "baseline_sample_count_matches_schedule",
    "baseline_has_no_boundary_loss",
    "baseline_near_return_found",
    "baseline_near_return_gap_large",
    "baseline_near_return_distance_small",
    "baseline_has_no_exact_quantized_recurrence",
    "baseline_visits_all_nonconstant_dominant_bands",
    "baseline_radius_stays_inside_full_window",
    "perturbation_trials_have_no_boundary_loss",
    "perturbation_trials_have_near_returns",
    "perturbation_trials_change_dominant_band",
}

EXPECTED_DOMINANT_BANDS = {"0.763932", "2.000000", "3.000000", "5.000000", "5.236068"}


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


def _assert_near_return(row: dict[str, Any], max_distance: float, min_gap: int, label: str) -> None:
    if row.get("found") is not True:
        raise AssertionError(f"{label} near-return missing")
    if float(row.get("distance", 1.0)) >= max_distance:
        raise AssertionError(f"{label} near-return distance too large")
    if int(row.get("frame_gap", 0)) < min_gap:
        raise AssertionError(f"{label} near-return frame gap too small")
    frame_pair = row.get("frame_pair", [])
    if len(frame_pair) != 2 or int(frame_pair[1]) <= int(frame_pair[0]):
        raise AssertionError(f"{label} near-return frame pair malformed")


def validate_d20_lift_spectral_recurrence_audit() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.lift_spectral_recurrence_audit.artifact@1":
        raise AssertionError("spectral recurrence artifact schema mismatch")
    if artifact.get("status") != "D20_LIFT_SPECTRAL_RECURRENCE_AUDIT_DERIVED":
        raise AssertionError("spectral recurrence artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral recurrence artifact self hash mismatch")

    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral recurrence artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("spectral recurrence checks mismatch")
    if artifact.get("laplacian_band_signature") != EXPECTED_LAPLACIAN_BANDS:
        raise AssertionError("spectral recurrence band signature mismatch")

    baseline = artifact.get("baseline_orbit", {}).get("summary", {})
    if baseline.get("boundary_loss_range") != [0, 0]:
        raise AssertionError("baseline boundary-loss range mismatch")
    if int(baseline.get("exact_quantized_collision_count", -1)) != 0:
        raise AssertionError("baseline exact quantized recurrence unexpectedly present")
    if set(baseline.get("dominant_band_counts", {})) != EXPECTED_DOMINANT_BANDS:
        raise AssertionError("baseline dominant-band support mismatch")
    if float(baseline.get("spatial_radius_range", [0, 999])[1]) >= 32.0:
        raise AssertionError("baseline radius exceeds full-window guard")
    _assert_near_return(
        baseline.get("nearest_return", {}),
        BASELINE_NEAR_RETURN_DISTANCE_MAX,
        512,
        "baseline",
    )

    perturbations = artifact.get("perturbation_trials", [])
    if len(perturbations) != 2:
        raise AssertionError("perturbation trial count mismatch")
    for row in perturbations:
        summary = row.get("summary", {})
        if summary.get("boundary_loss_range") != [0, 0]:
            raise AssertionError(f"{row.get('id')} boundary-loss range mismatch")
        if len(summary.get("dominant_band_counts", {})) < 3:
            raise AssertionError(f"{row.get('id')} dominant-band support too small")
        _assert_near_return(
            summary.get("nearest_return", {}),
            PERTURBATION_NEAR_RETURN_DISTANCE_MAX,
            96,
            str(row.get("id")),
        )

    if report.get("schema") != "d20.proof_obligation.lift_spectral_recurrence_audit@1":
        raise AssertionError("spectral recurrence report schema mismatch")
    if report.get("status") != "D20_LIFT_SPECTRAL_RECURRENCE_AUDIT_CERTIFIED":
        raise AssertionError("spectral recurrence report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("spectral recurrence report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("spectral recurrence report checks differ from artifact")
    if report.get("witness", {}).get("baseline_summary") != baseline:
        raise AssertionError("spectral recurrence report baseline summary differs from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral recurrence report self hash mismatch")

    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact input")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("report artifact internal hash mismatch")
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_lift_spectral_recurrence_audit.py",
        "validator input",
    )
    _check_input_file(
        report.get("inputs", {}).get("visualization", {}),
        "generated/d20_sandpile_visualization.html",
        "visualization input",
    )

    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral recurrence report is not reproducible")

    if manifest.get("schema") != "d20.proof_obligation.lift_spectral_recurrence_audit_manifest@1":
        raise AssertionError("spectral recurrence manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral recurrence manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral recurrence manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("spectral recurrence manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("spectral recurrence manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("spectral recurrence registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral recurrence registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("spectral recurrence registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_lift_spectral_recurrence_audit()
    print("D20 lift spectral recurrence audit validated")
