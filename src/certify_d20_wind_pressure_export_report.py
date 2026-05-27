from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_wind_pressure_export_report import (
        ARTIFACT_PATH,
        D20_H6_TRIPLES,
        FINITE_STATE_REPORT,
        GATE_AUTOMATON_REPORT,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        VALIDATOR,
        VISUALIZATION,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_wind_pressure_export_report import (
        ARTIFACT_PATH,
        D20_H6_TRIPLES,
        FINITE_STATE_REPORT,
        GATE_AUTOMATON_REPORT,
        INDEX_PATH,
        OUT_DIR,
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
GATE_AUTOMATON_REPORT_REL = GATE_AUTOMATON_REPORT.relative_to(ROOT).as_posix()
FINITE_STATE_REPORT_REL = FINITE_STATE_REPORT.relative_to(ROOT).as_posix()
VISUALIZATION_REL = VISUALIZATION.relative_to(ROOT).as_posix()
VALIDATOR_REL = VALIDATOR.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "gate_automaton_certified",
    "finite_state_wind_tunnel_certified",
    "all_six_inlets_exported",
    "all_nonidentity_null_permutations_exported",
    "identity_rows_exported",
    "pressure_vectors_are_d20_atoms",
    "finite_values",
    "renderer_embeds_wind_tunnel",
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


def _assert_rate(value: Any, label: str) -> None:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise AssertionError(f"{label} is not finite")
    if not 0.0 <= numeric <= 1.0:
        raise AssertionError(f"{label} is outside [0, 1]")


def _validate_pressure_row(row: dict[str, Any], label: str) -> None:
    if len(row.get("pressure_vector", [])) != len(D20_H6_TRIPLES):
        raise AssertionError(f"{label} pressure vector shape mismatch")
    for key in (
        "throughput_rate",
        "recirc_rate",
        "aperture_loss_rate",
        "branch_accept_rate",
        "alignment_rate",
        "pressure",
        "total_pressure",
    ):
        _assert_rate(row.get(key), f"{label} {key}")
    for index, value in enumerate(row["pressure_vector"]):
        if not math.isfinite(float(value)):
            raise AssertionError(f"{label} pressure vector {index} is not finite")


def validate_d20_wind_pressure_export_report() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.wind_pressure_export_report.artifact@1":
        raise AssertionError("wind pressure artifact schema mismatch")
    if artifact.get("status") != "D20_WIND_PRESSURE_EXPORT_REPORT_DERIVED":
        raise AssertionError("wind pressure artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("wind pressure artifact self hash mismatch")
    expected_artifact = build_artifact()
    if expected_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("wind pressure artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise AssertionError("wind pressure checks mismatch")

    witness = artifact.get("witness", {})
    identity_rows = witness.get("identity_rows", [])
    null_rows = witness.get("null_rows", [])
    if len(identity_rows) != 6:
        raise AssertionError("identity row count mismatch")
    if len(null_rows) != 6 * 719:
        raise AssertionError("null row count mismatch")
    for row in identity_rows:
        _validate_pressure_row(row, f"identity inlet {row.get('inlet')}")
    for row_index, row in enumerate(null_rows):
        _validate_pressure_row(row, f"null row {row_index}")
    for summary_name in ("identity_summary", "null_summary"):
        summary = witness.get(summary_name, {})
        if len(summary.get("mean_pressure_vector", [])) != len(D20_H6_TRIPLES):
            raise AssertionError(f"{summary_name} mean pressure vector shape mismatch")
    for value in witness.get("identity_minus_null_mean", {}).values():
        if not math.isfinite(float(value)):
            raise AssertionError("wind pressure delta is not finite")

    if report.get("schema") != "d20.wind_pressure_export_report@1":
        raise AssertionError("wind pressure report schema mismatch")
    if report.get("status") != "D20_WIND_PRESSURE_EXPORT_REPORT_CERTIFIED":
        raise AssertionError("wind pressure report status mismatch")
    if report.get("checks") != checks:
        raise AssertionError("wind pressure report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("wind pressure report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("wind pressure report is not reproducible")

    inputs = report.get("inputs", {})
    _check_input_file(inputs.get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(inputs.get("validator", {}), VALIDATOR_REL, "validator input")
    _check_input_file(inputs.get("gate_automaton_report", {}), GATE_AUTOMATON_REPORT_REL, "gate report input")
    _check_input_file(inputs.get("finite_state_report", {}), FINITE_STATE_REPORT_REL, "finite state report input")
    _check_input_file(inputs.get("visualization", {}), VISUALIZATION_REL, "visualization input")

    if manifest.get("schema") != "d20.wind_pressure_export_report_manifest@1":
        raise AssertionError("wind pressure manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("wind pressure manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("wind pressure manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("wind pressure manifest is not reproducible")

    entry = next(
        (
            row
            for row in index.get("obligations", [])
            if isinstance(row, dict) and row.get("id") == THEOREM_ID
        ),
        None,
    )
    if entry is None:
        raise AssertionError("wind pressure registry entry missing")
    if entry.get("status") != report.get("status"):
        raise AssertionError("wind pressure registry status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("wind pressure registry report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_wind_pressure_export_report()
    print("D20 wind pressure export report validated")
