from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_micro_black_hole_raw_transport_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        MICRO_ARTIFACT,
        MICRO_REPORT,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_micro_black_hole_raw_transport_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        MICRO_ARTIFACT,
        MICRO_REPORT,
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
MICRO_ARTIFACT_REL = MICRO_ARTIFACT.relative_to(ROOT).as_posix()
MICRO_REPORT_REL = MICRO_REPORT.relative_to(ROOT).as_posix()

EXPECTED_STATUSES = {
    "D20_MICRO_BLACK_HOLE_RAW_TRANSPORT_PROBE_CERTIFIED_RAW_POSITIVE",
    "D20_MICRO_BLACK_HOLE_RAW_TRANSPORT_PROBE_NEGATIVE",
}

EXPECTED_CHECKS = {
    "micro_backreaction_probe_is_certified",
    "raw_astar_shadow_fields_are_present",
    "raw_transport_delta_matches_source_summary",
    "lensed_transport_delta_matches_source_summary",
    "lensed_reference_bends_toward_horizon",
    "raw_and_lensed_measurements_are_distinct",
    "raw_transport_bends_toward_horizon_without_lens",
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


def _assert_finite(value: Any, label: str) -> None:
    if not math.isfinite(float(value)):
        raise AssertionError(f"{label} is not finite")


def validate_d20_micro_black_hole_raw_transport_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.micro_black_hole_raw_transport_probe.artifact@1":
        raise AssertionError("raw transport artifact schema mismatch")
    if artifact.get("status") not in EXPECTED_STATUSES:
        raise AssertionError("raw transport artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("raw transport artifact self hash mismatch")
    expected_artifact = build_artifact()
    if expected_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("raw transport artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS:
        raise AssertionError("raw transport checks mismatch")
    raw_positive = bool(checks.get("raw_transport_bends_toward_horizon_without_lens"))
    if artifact.get("status") == "D20_MICRO_BLACK_HOLE_RAW_TRANSPORT_PROBE_CERTIFIED_RAW_POSITIVE":
        if not raw_positive:
            raise AssertionError("raw-positive status has failing raw transport check")
    if artifact.get("status") == "D20_MICRO_BLACK_HOLE_RAW_TRANSPORT_PROBE_NEGATIVE":
        if raw_positive:
            raise AssertionError("negative raw transport status has passing raw transport check")

    witness = artifact.get("witness", {})
    summary = witness.get("summary", {})
    rows = witness.get("frame_deltas", [])
    if int(summary.get("astar_sample_count", -1)) != len(rows):
        raise AssertionError("raw transport frame delta count mismatch")
    if len(rows) <= 0:
        raise AssertionError("raw transport has no frame deltas")
    if int(summary.get("raw_positive_frame_count", -1)) != sum(
        1 for row in rows if float(row.get("raw_delta", 0.0)) > 0.0
    ):
        raise AssertionError("raw transport positive frame count mismatch")
    if int(summary.get("lensed_positive_frame_count", -1)) != sum(
        1 for row in rows if float(row.get("lensed_delta", 0.0)) > 0.0
    ):
        raise AssertionError("lensed transport positive frame count mismatch")
    for label, value in {
        "raw_astar_inner_band_delta_vs_baseline_mean": summary.get(
            "raw_astar_inner_band_delta_vs_baseline_mean"
        ),
        "lensed_astar_inner_band_delta_vs_baseline_mean": summary.get(
            "lensed_astar_inner_band_delta_vs_baseline_mean"
        ),
        "final_horizon_mass": summary.get("final_horizon_mass"),
        "horizon_lens_factor_mean": summary.get("horizon_lens_factor_mean"),
    }.items():
        _assert_finite(value, label)
    for row in rows:
        for key in (
            "frame",
            "raw_backreaction_inner_band_fraction",
            "raw_baseline_inner_band_fraction",
            "raw_delta",
            "lensed_backreaction_inner_band_fraction",
            "lensed_baseline_inner_band_fraction",
            "lensed_delta",
            "lens_factor",
            "horizon_mass",
        ):
            _assert_finite(row.get(key), f"raw transport frame {key}")

    if report.get("schema") != "d20.proof_obligation.micro_black_hole_raw_transport_probe@1":
        raise AssertionError("raw transport report schema mismatch")
    if report.get("status") != artifact.get("status"):
        raise AssertionError("raw transport report status mismatch")
    if report.get("checks") != checks:
        raise AssertionError("raw transport report checks differ from artifact")
    if report.get("all_checks_pass") != all(checks.values()):
        raise AssertionError("raw transport report all_checks_pass mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("raw transport report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("raw transport report is not reproducible")

    inputs = report.get("inputs", {})
    _check_input_file(inputs.get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(inputs.get("validator", {}), "src/certify_d20_micro_black_hole_raw_transport_probe.py", "validator input")
    _check_input_file(
        inputs.get("micro_black_hole_backreaction_artifact", {}),
        MICRO_ARTIFACT_REL,
        "micro backreaction artifact input",
    )
    _check_input_file(
        inputs.get("micro_black_hole_backreaction_report", {}),
        MICRO_REPORT_REL,
        "micro backreaction report input",
    )

    if manifest.get("schema") != "d20.proof_obligation.micro_black_hole_raw_transport_probe_manifest@1":
        raise AssertionError("raw transport manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("raw transport manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("raw transport manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("raw transport manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("raw transport manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("raw transport registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("raw transport registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("raw transport registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_micro_black_hole_raw_transport_probe()
    print("D20 micro black hole raw transport probe validated")
