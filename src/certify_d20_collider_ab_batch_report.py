from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_collider_ab_batch_report import (
        ARTIFACT_PATH,
        BATCH_SHOTS,
        INDEX_PATH,
        OUT_DIR,
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
    from derive_d20_collider_ab_batch_report import (
        ARTIFACT_PATH,
        BATCH_SHOTS,
        INDEX_PATH,
        OUT_DIR,
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
    "renderer_embeds_collider_batch_harness",
    "null_assignment_is_permutation",
    "shot_count_matches_renderer",
    "contact_activity_observed",
    "capture_activity_observed",
    "finite_batch_values",
    "residue_values_in_unit_interval",
    "clump_values_in_unit_interval",
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


def validate_d20_collider_ab_batch_report() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.collider_ab_batch_report.artifact@1":
        raise AssertionError("collider A/B artifact schema mismatch")
    if artifact.get("status") != "D20_COLLIDER_AB_BATCH_REPORT_DERIVED":
        raise AssertionError("collider A/B artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("collider A/B artifact self hash mismatch")
    expected_artifact = build_artifact()
    if expected_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("collider A/B artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise AssertionError("collider A/B checks mismatch")

    witness = artifact.get("witness", {})
    for side in ("real", "null"):
        data = witness.get(side, {})
        averages = data.get("averages", {})
        shots = data.get("shots", [])
        if len(shots) != BATCH_SHOTS:
            raise AssertionError(f"{side} shot count mismatch")
        for key in ("contacts", "captures", "escapes", "residue", "clump"):
            _assert_finite(averages.get(key), f"{side} average {key}")
        if not (0.0 <= float(averages["residue"]) <= 1.0):
            raise AssertionError(f"{side} residue average out of range")
        if not (0.0 <= float(averages["clump"]) <= 1.0):
            raise AssertionError(f"{side} clump average out of range")
        for shot in shots:
            for key in (
                "contacts",
                "captures",
                "escapes",
                "residue",
                "clump",
                "final_overlap",
                "final_scatter",
                "final_fusion",
                "final_coupling",
            ):
                _assert_finite(shot.get(key), f"{side} shot {shot.get('shot')} {key}")
    deltas = witness.get("deltas_real_minus_null", {})
    for key in ("contacts", "captures", "escapes", "residue", "clump"):
        _assert_finite(deltas.get(key), f"delta {key}")

    if report.get("schema") != "d20.collider_ab_batch_report@1":
        raise AssertionError("collider A/B report schema mismatch")
    if report.get("status") != "D20_COLLIDER_AB_BATCH_REPORT_CERTIFIED":
        raise AssertionError("collider A/B report status mismatch")
    if report.get("checks") != checks:
        raise AssertionError("collider A/B report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("collider A/B report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("collider A/B report is not reproducible")
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

    if manifest.get("schema") != "d20.collider_ab_batch_report_manifest@1":
        raise AssertionError("collider A/B manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("collider A/B manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("collider A/B manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("collider A/B manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("collider A/B registry entry missing")
    if entry.get("status") != report.get("status"):
        raise AssertionError("collider A/B registry status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("collider A/B registry report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_collider_ab_batch_report()
    print("D20 collider A/B batch report validated")
