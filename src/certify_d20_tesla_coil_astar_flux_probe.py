from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_tesla_coil_astar_flux_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        NULL_SAMPLES,
        OUT_DIR,
        PATH_PAIR_COUNT,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_tesla_coil_astar_flux_probe import (
        ARTIFACT_PATH,
        INDEX_PATH,
        NULL_SAMPLES,
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
    "rgba_replay_archive_certified",
    "shell_has_nonempty_hole",
    "shell_has_nonempty_transport",
    "astar_found_all_path_pairs",
    "vector_field_index_measurable",
    "hole_flux_anomaly_ratio_exceeds_bulk",
    "astar_alignment_exceeds_invariant_shuffle_mean",
    "astar_high_flux_overlap_exceeds_invariant_shuffle_mean",
}

EXPECTED_STATUSES = {
    "D20_TESLA_COIL_ASTAR_FLUX_PROBE_CERTIFIED",
    "D20_TESLA_COIL_ASTAR_FLUX_PROBE_PROVISIONAL",
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


def validate_d20_tesla_coil_astar_flux_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.tesla_coil_astar_flux_probe.artifact@1":
        raise AssertionError("Tesla coil A* artifact schema mismatch")
    if artifact.get("status") not in EXPECTED_STATUSES:
        raise AssertionError("Tesla coil A* artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Tesla coil A* artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Tesla coil A* artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS:
        raise AssertionError("Tesla coil A* checks mismatch")
    if artifact.get("status") == "D20_TESLA_COIL_ASTAR_FLUX_PROBE_CERTIFIED" and not all(
        checks.values()
    ):
        raise AssertionError("certified Tesla coil A* artifact has failing checks")
    if artifact.get("status") == "D20_TESLA_COIL_ASTAR_FLUX_PROBE_PROVISIONAL" and all(
        checks.values()
    ):
        raise AssertionError("provisional Tesla coil A* artifact has no failing checks")

    witness = artifact.get("witness", {})
    shell = witness.get("shell", {})
    flux = witness.get("flux", {})
    paths = witness.get("astar_paths", {})
    aggregate = paths.get("aggregate", {})
    null = witness.get("null_shuffle", {})
    effects = witness.get("effect_sizes", {})
    index_witness = witness.get("vector_field_index", {})

    if int(shell.get("shell_cell_count", 0)) <= 0 or int(shell.get("hole_cell_count", 0)) <= 0:
        raise AssertionError("Tesla coil shell/hole witness is empty")
    if not (0.0 <= float(shell.get("shell_coverage_ratio", -1.0)) <= 1.0):
        raise AssertionError("Tesla coil shell coverage ratio out of range")
    if int(paths.get("pair_count", 0)) != PATH_PAIR_COUNT:
        raise AssertionError("Tesla coil A* path pair count mismatch")
    if len(paths.get("paths", [])) != PATH_PAIR_COUNT:
        raise AssertionError("Tesla coil A* path row count mismatch")
    if float(aggregate.get("paths_found", 0.0)) != float(PATH_PAIR_COUNT):
        raise AssertionError("not all Tesla coil A* paths were found")
    if int(null.get("sample_count", 0)) != NULL_SAMPLES:
        raise AssertionError("Tesla coil null sample count mismatch")
    if int(index_witness.get("nonzero_vector_samples", 0)) < 64:
        raise AssertionError("Tesla coil vector-field index has too few samples")

    for label, value in {
        "hole_flux_anomaly_ratio": flux.get("hole_flux_anomaly_ratio"),
        "axis_alignment_delta_vs_null": effects.get("axis_alignment_delta_vs_null"),
        "axis_alignment_z_vs_null": effects.get("axis_alignment_z_vs_null"),
        "high_flux_overlap_delta_vs_null": effects.get("high_flux_overlap_delta_vs_null"),
        "high_flux_overlap_z_vs_null": effects.get("high_flux_overlap_z_vs_null"),
        "vector_field_index": index_witness.get("index_turns"),
    }.items():
        _assert_finite(value, label)

    if report.get("schema") != "d20.proof_obligation.tesla_coil_astar_flux_probe@1":
        raise AssertionError("Tesla coil A* report schema mismatch")
    if report.get("status") != artifact.get("status"):
        raise AssertionError("Tesla coil A* report status mismatch")
    if report.get("all_checks_pass") != all(checks.values()):
        raise AssertionError("Tesla coil A* report all_checks_pass mismatch")
    if report.get("checks") != checks:
        raise AssertionError("Tesla coil A* report checks differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Tesla coil A* report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Tesla coil A* report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("phase_entropy_audit_report", {}),
        "data/invariants/d20/proof_obligations/d20_geon_phase_entropy_audit/report.json",
        "phase audit input",
    )
    _check_input_file(
        report.get("inputs", {}).get("rgba_replay_archive_report", {}),
        "data/invariants/d20/proof_obligations/d20_geon_rgba_replay_frame_archive/report.json",
        "RGBA replay input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_tesla_coil_astar_flux_probe.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.tesla_coil_astar_flux_probe_manifest@1":
        raise AssertionError("Tesla coil A* manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Tesla coil A* manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("Tesla coil A* manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Tesla coil A* manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("Tesla coil A* manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("Tesla coil A* registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Tesla coil A* registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Tesla coil A* registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_tesla_coil_astar_flux_probe()
    print("D20 Tesla coil A* flux probe validated")
