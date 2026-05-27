from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_transport_eigenmode_report import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        REPLAY_FRAMES,
        STRESS_GRAPH_ARTIFACT,
        STRESS_GRAPH_REPORT,
        THEOREM_ID,
        VALIDATOR,
        VISUALIZATION,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_transport_eigenmode_report import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        REPLAY_FRAMES,
        STRESS_GRAPH_ARTIFACT,
        STRESS_GRAPH_REPORT,
        THEOREM_ID,
        VALIDATOR,
        VISUALIZATION,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()
STRESS_GRAPH_ARTIFACT_REL = STRESS_GRAPH_ARTIFACT.relative_to(ROOT).as_posix()
STRESS_GRAPH_REPORT_REL = STRESS_GRAPH_REPORT.relative_to(ROOT).as_posix()
VISUALIZATION_REL = VISUALIZATION.relative_to(ROOT).as_posix()
VALIDATOR_REL = VALIDATOR.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "stress_graph_certified",
    "renderer_embeds_eigenmode_witness",
    "real_mode_unit_norm",
    "null_mode_unit_norm",
    "null_assignment_is_permutation",
    "replay_frames_present",
    "alignment_values_finite",
    "active_cells_nonzero",
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
        raise AssertionError(f"{label} hash mismatch")


def _assert_finite(value: Any, label: str) -> None:
    if not math.isfinite(float(value)):
        raise AssertionError(f"{label} is not finite")


def validate_d20_transport_eigenmode_report() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.transport_eigenmode_report.artifact@1":
        raise AssertionError("transport eigenmode artifact schema mismatch")
    if artifact.get("status") != "D20_TRANSPORT_EIGENMODE_REPORT_DERIVED":
        raise AssertionError("transport eigenmode artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("transport eigenmode artifact self hash mismatch")
    expected_artifact = build_artifact()
    if expected_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("transport eigenmode artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise AssertionError("transport eigenmode checks mismatch")

    witness = artifact.get("witness", {})
    summary = witness.get("summary", {})
    frames = witness.get("frame_samples", [])
    if len(frames) != REPLAY_FRAMES:
        raise AssertionError("transport eigenmode frame count mismatch")
    for key in (
        "real_alignment_mean",
        "null_alignment_mean",
        "real_minus_null_gap_mean",
        "positive_gap_fraction",
        "active_cells_mean",
    ):
        _assert_finite(summary.get(key), key)
    for key in ("real_mode", "null_mode"):
        vector = witness.get(key, [])
        if len(vector) != 20:
            raise AssertionError(f"{key} length mismatch")
        norm = math.sqrt(sum(float(value) * float(value) for value in vector))
        if abs(norm - 1.0) > 1e-10:
            raise AssertionError(f"{key} norm mismatch")
    for sample in frames:
        for key in ("real_alignment", "null_alignment", "signal_l2_norm"):
            _assert_finite(sample.get(key), f"frame {sample.get('frame')} {key}")
        if not (0.0 <= float(sample["real_alignment"]) <= 1.0):
            raise AssertionError("real alignment out of range")
        if not (0.0 <= float(sample["null_alignment"]) <= 1.0):
            raise AssertionError("null alignment out of range")

    if report.get("schema") != "d20.transport_eigenmode_report@1":
        raise AssertionError("transport eigenmode report schema mismatch")
    if report.get("status") != "D20_TRANSPORT_EIGENMODE_REPORT_CERTIFIED":
        raise AssertionError("transport eigenmode report status mismatch")
    if report.get("checks") != checks:
        raise AssertionError("transport eigenmode report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("transport eigenmode report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("transport eigenmode report is not reproducible")
    inputs = report.get("inputs", {})
    _check_input_file(inputs.get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(inputs.get("validator", {}), VALIDATOR_REL, "validator input")
    _check_input_file(
        inputs.get("stress_graph_artifact", {}),
        STRESS_GRAPH_ARTIFACT_REL,
        "stress graph artifact input",
    )
    _check_input_file(
        inputs.get("stress_graph_report", {}),
        STRESS_GRAPH_REPORT_REL,
        "stress graph report input",
    )
    _check_input_file(inputs.get("visualization", {}), VISUALIZATION_REL, "visualization input")

    if manifest.get("schema") != "d20.transport_eigenmode_report_manifest@1":
        raise AssertionError("transport eigenmode manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("transport eigenmode manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("transport eigenmode manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("transport eigenmode manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("transport eigenmode registry entry missing")
    if entry.get("status") != report.get("status"):
        raise AssertionError("transport eigenmode registry status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("transport eigenmode registry report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_transport_eigenmode_report()
    print("D20 transport eigenmode report validated")
