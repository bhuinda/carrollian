from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_horizon_flux_astar_probe import (
        ARTIFACT_PATH,
        ASTAR_FRAME_STRIDE,
        ASTAR_NULL_SAMPLES,
        FLUX_NULL_SAMPLES,
        FRAME_COUNT,
        INDEX_PATH,
        OUT_DIR,
        PATH_PAIR_COUNT,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_horizon_flux_astar_probe import (
        ARTIFACT_PATH,
        ASTAR_FRAME_STRIDE,
        ASTAR_NULL_SAMPLES,
        FLUX_NULL_SAMPLES,
        FRAME_COUNT,
        INDEX_PATH,
        OUT_DIR,
        PATH_PAIR_COUNT,
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
    "phase_entropy_audit_certified",
    "tesla_coil_probe_is_recorded",
    "timeseries_frame_count_is_97",
    "horizon_has_inward_flux",
    "horizon_weighted_flux_beats_shuffle_mean",
    "horizon_weighted_flux_beats_shuffle_on_majority_frames",
    "inner_band_inward_flux_exceeds_bulk_mean",
    "astar_sampled_paths_all_found",
    "astar_paths_bend_toward_horizon_more_than_shuffle",
    "astar_paths_sweep_more_than_shuffle",
}

EXPECTED_STATUSES = {
    "D20_HORIZON_FLUX_ASTAR_PROBE_CERTIFIED",
    "D20_HORIZON_FLUX_ASTAR_PROBE_PROVISIONAL",
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


def validate_d20_horizon_flux_astar_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.horizon_flux_astar_probe.artifact@1":
        raise AssertionError("horizon flux artifact schema mismatch")
    if artifact.get("status") not in EXPECTED_STATUSES:
        raise AssertionError("horizon flux artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("horizon flux artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("horizon flux artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS:
        raise AssertionError("horizon flux checks mismatch")
    if artifact.get("status") == "D20_HORIZON_FLUX_ASTAR_PROBE_CERTIFIED" and not all(checks.values()):
        raise AssertionError("certified horizon flux artifact has failing checks")
    if artifact.get("status") == "D20_HORIZON_FLUX_ASTAR_PROBE_PROVISIONAL" and all(checks.values()):
        raise AssertionError("provisional horizon flux artifact has no failing checks")

    witness = artifact.get("witness", {})
    flux = witness.get("flux_summary", {})
    astar = witness.get("astar_lensing_summary", {})
    flux_rows = witness.get("flux_rows_first_16", [])
    astar_rows = witness.get("astar_rows", [])

    if int(flux.get("frame_count", 0)) != FRAME_COUNT:
        raise AssertionError("horizon flux frame count mismatch")
    if int(astar.get("sampled_frame_count", 0)) != (FRAME_COUNT - 1) // ASTAR_FRAME_STRIDE + 1:
        raise AssertionError("horizon A* sampled frame count mismatch")
    if int(astar.get("path_pair_count", 0)) != PATH_PAIR_COUNT:
        raise AssertionError("horizon A* path pair count mismatch")
    if len(flux_rows) != 16:
        raise AssertionError("horizon flux first rows witness mismatch")
    if len(astar_rows) != int(astar.get("sampled_frame_count", 0)):
        raise AssertionError("horizon A* row count mismatch")

    for row in flux_rows:
        if int(row.get("inner_band_cell_count", 0)) <= 0:
            raise AssertionError("horizon inner band is empty in witness row")
        if row.get("weighted_flux_above_null_mean") not in {True, False}:
            raise AssertionError("horizon flux null comparison flag is not boolean")
    for row in astar_rows:
        if float(row.get("paths_found", 0.0)) != float(PATH_PAIR_COUNT):
            raise AssertionError("horizon A* sampled row did not find all paths")

    for label, value in {
        "weighted_flux_delta_vs_null_mean": flux.get("weighted_flux_delta_vs_null_mean"),
        "weighted_flux_z_vs_null_mean": flux.get("weighted_flux_z_vs_null_mean"),
        "inner_to_bulk_inward_flux_ratio_mean": flux.get("inner_to_bulk_inward_flux_ratio_mean"),
        "cumulative_raw_inward_flux": flux.get("cumulative_raw_inward_flux"),
        "astar_inner_band_fraction_delta": astar.get("inner_band_fraction_delta_vs_null_mean"),
        "astar_angular_sweep_delta": astar.get("angular_sweep_turns_delta_vs_null_mean"),
        "astar_axis_alignment_mean": astar.get("axis_alignment_mean"),
    }.items():
        _assert_finite(value, label)

    if report.get("schema") != "d20.proof_obligation.horizon_flux_astar_probe@1":
        raise AssertionError("horizon flux report schema mismatch")
    if report.get("status") != artifact.get("status"):
        raise AssertionError("horizon flux report status mismatch")
    if report.get("all_checks_pass") != all(checks.values()):
        raise AssertionError("horizon flux report all_checks_pass mismatch")
    if report.get("checks") != checks:
        raise AssertionError("horizon flux report checks differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("horizon flux report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("horizon flux report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("phase_entropy_audit_report", {}),
        "data/invariants/d20/proof_obligations/d20_geon_phase_entropy_audit/report.json",
        "phase audit input",
    )
    _check_input_file(
        report.get("inputs", {}).get("tesla_coil_astar_flux_probe_report", {}),
        "data/invariants/d20/proof_obligations/d20_tesla_coil_astar_flux_probe/report.json",
        "Tesla coil probe input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_horizon_flux_astar_probe.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.horizon_flux_astar_probe_manifest@1":
        raise AssertionError("horizon flux manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("horizon flux manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("horizon flux manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("horizon flux manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("horizon flux manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("horizon flux registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("horizon flux registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("horizon flux registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    _ = FLUX_NULL_SAMPLES
    _ = ASTAR_NULL_SAMPLES
    return report


if __name__ == "__main__":
    validate_d20_horizon_flux_astar_probe()
    print("D20 horizon flux A* probe validated")
