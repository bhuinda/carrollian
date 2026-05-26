from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_lift_spectral_timeseries_audit import (
        ARTIFACT_PATH,
        EXPECTED_LAPLACIAN_BANDS,
        INDEX_PATH,
        OUT_DIR,
        SAMPLE_FRAMES,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_lift_spectral_timeseries_audit import (
        ARTIFACT_PATH,
        EXPECTED_LAPLACIAN_BANDS,
        INDEX_PATH,
        OUT_DIR,
        SAMPLE_FRAMES,
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
    "phase_entropy_audit_certified",
    "laplacian_band_signature_matches_expected",
    "sample_frame_schedule_complete",
    "all_samples_have_live_mass",
    "observed_samples_have_no_boundary_loss",
    "all_samples_support_every_nonconstant_laplacian_band",
    "spectral_centroid_stays_inside_nonconstant_band_range",
    "dominant_band_changes_during_replay",
    "golden_pair_visible_in_every_sample",
    "spatial_radius_stays_inside_full_window",
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


def _assert_sample(row: dict[str, Any]) -> None:
    if int(row.get("live_grains", 0)) <= 0:
        raise AssertionError("spectral sample has no live grains")
    if int(row.get("boundary_loss", -1)) != 0:
        raise AssertionError("spectral sample has boundary loss")
    spectral = row.get("spectral", {})
    bands = spectral.get("bands", [])
    if len(bands) != len(EXPECTED_LAPLACIAN_BANDS) - 1:
        raise AssertionError("spectral sample band count mismatch")
    if any(float(band.get("probability", 0.0)) <= 0.0 for band in bands):
        raise AssertionError("spectral sample has unsupported nonconstant band")
    probability_sum = sum(float(band.get("probability", 0.0)) for band in bands)
    if abs(probability_sum - 1.0) > 1e-9:
        raise AssertionError("spectral sample probabilities do not sum to one")
    centroid = float(spectral.get("centroid", 0.0))
    if not (0.763932 < centroid < 5.236068):
        raise AssertionError("spectral centroid outside nonconstant band range")
    if float(spectral.get("golden_pair_probability", 0.0)) <= 0.15:
        raise AssertionError("golden pair probability too small")
    if float(row.get("spatial", {}).get("radius", 0.0)) >= 32.0:
        raise AssertionError("sample radius exceeds full-window guard")


def validate_d20_lift_spectral_timeseries_audit() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.lift_spectral_timeseries_audit.artifact@1":
        raise AssertionError("spectral timeseries artifact schema mismatch")
    if artifact.get("status") != "D20_LIFT_SPECTRAL_TIMESERIES_AUDIT_DERIVED":
        raise AssertionError("spectral timeseries artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral timeseries artifact self hash mismatch")

    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral timeseries artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("spectral timeseries checks mismatch")

    summary = artifact.get("summary", {})
    if summary.get("sample_frames") != SAMPLE_FRAMES:
        raise AssertionError("spectral timeseries sample frame schedule mismatch")
    if summary.get("laplacian_band_signature") != EXPECTED_LAPLACIAN_BANDS:
        raise AssertionError("spectral timeseries band signature mismatch")
    if int(summary.get("sample_count", 0)) != len(SAMPLE_FRAMES):
        raise AssertionError("spectral timeseries sample count mismatch")
    if summary.get("boundary_loss_range") != [0, 0]:
        raise AssertionError("spectral timeseries boundary-loss range mismatch")
    if len(summary.get("dominant_band_counts", {})) < 2:
        raise AssertionError("spectral timeseries dominant band did not change")

    samples = artifact.get("samples", [])
    if len(samples) != len(SAMPLE_FRAMES):
        raise AssertionError("spectral timeseries samples length mismatch")
    for row in samples:
        _assert_sample(row)

    if report.get("schema") != "d20.proof_obligation.lift_spectral_timeseries_audit@1":
        raise AssertionError("spectral timeseries report schema mismatch")
    if report.get("status") != "D20_LIFT_SPECTRAL_TIMESERIES_AUDIT_CERTIFIED":
        raise AssertionError("spectral timeseries report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("spectral timeseries report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("spectral timeseries report checks differ from artifact")
    if report.get("witness", {}).get("summary") != summary:
        raise AssertionError("spectral timeseries report summary differs from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral timeseries report self hash mismatch")

    artifact_input = report.get("inputs", {}).get("artifact", {})
    _check_input_file(artifact_input, ARTIFACT_REL, "report artifact input")
    if artifact_input.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("report artifact internal hash mismatch")
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_lift_spectral_timeseries_audit.py",
        "validator input",
    )
    _check_input_file(
        report.get("inputs", {}).get("visualization", {}),
        "generated/d20_sandpile_visualization.html",
        "visualization input",
    )

    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral timeseries report is not reproducible")

    if manifest.get("schema") != "d20.proof_obligation.lift_spectral_timeseries_audit_manifest@1":
        raise AssertionError("spectral timeseries manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral timeseries manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("spectral timeseries manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("spectral timeseries manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("spectral timeseries manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("spectral timeseries registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("spectral timeseries registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("spectral timeseries registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_lift_spectral_timeseries_audit()
    print("D20 lift spectral timeseries audit validated")
