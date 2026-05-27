from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_finite_state_collider_report import (
        ARTIFACT_PATH,
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
    from derive_d20_finite_state_collider_report import (
        ARTIFACT_PATH,
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
VISUALIZATION_REL = VISUALIZATION.relative_to(ROOT).as_posix()
VALIDATOR_REL = VALIDATOR.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "gate_automaton_certified",
    "lambda3_h6_boundary_has_20_atoms",
    "null_symbol_map_is_permutation",
    "real_and_null_event_counts_match",
    "renderer_routes_to_finite_state_collider",
    "renderer_projects_finite_events_to_3d_atom",
    "renderer_embeds_finite_word_ledger",
    "renderer_embeds_finite_wind_tunnel",
    "visuals_pause_by_default",
    "old_force_solver_removed",
    "renderer_embeds_null_symbol_map",
    "renderer_note_declares_grammar_experiment",
    "real_accepts_certified_word",
    "finite_values",
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


def validate_d20_finite_state_collider_report() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.finite_state_collider_report.artifact@1":
        raise AssertionError("finite-state collider artifact schema mismatch")
    if artifact.get("status") != "D20_FINITE_STATE_COLLIDER_REPORT_DERIVED":
        raise AssertionError("finite-state collider artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("finite-state collider artifact self hash mismatch")
    expected_artifact = build_artifact()
    if expected_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("finite-state collider artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise AssertionError("finite-state collider checks mismatch")

    witness = artifact.get("witness", {})
    for side in ("real", "null"):
        data = witness.get(side, {})
        for key in (
            "accept_rate",
            "branch_accept_rate",
            "certified_trigram_rate",
            "missing_aperture_rate",
            "letter_entropy",
            "residue",
        ):
            _assert_rate(data.get(key), f"{side} {key}")
        if len(data.get("letter_counts", [])) != 6:
            raise AssertionError(f"{side} letter count shape mismatch")
    for value in witness.get("deltas_real_minus_null", {}).values():
        if not math.isfinite(float(value)):
            raise AssertionError("finite-state collider delta is not finite")
    wind = witness.get("wind_tunnel", {})
    for side in ("real", "null"):
        data = wind.get(side, {})
        for key in (
            "throughput_rate",
            "recirc_rate",
            "aperture_loss_rate",
            "alignment_rate",
            "pressure",
            "total_pressure",
        ):
            _assert_rate(data.get(key), f"wind {side} {key}")
    for value in wind.get("deltas_real_minus_null", {}).values():
        if not math.isfinite(float(value)):
            raise AssertionError("finite wind tunnel delta is not finite")

    if report.get("schema") != "d20.finite_state_collider_report@1":
        raise AssertionError("finite-state collider report schema mismatch")
    if report.get("status") != "D20_FINITE_STATE_COLLIDER_REPORT_CERTIFIED":
        raise AssertionError("finite-state collider report status mismatch")
    if report.get("checks") != checks:
        raise AssertionError("finite-state collider report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("finite-state collider report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("finite-state collider report is not reproducible")

    inputs = report.get("inputs", {})
    _check_input_file(inputs.get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(inputs.get("validator", {}), VALIDATOR_REL, "validator input")
    _check_input_file(inputs.get("gate_automaton_report", {}), GATE_AUTOMATON_REPORT_REL, "gate report input")
    _check_input_file(inputs.get("visualization", {}), VISUALIZATION_REL, "visualization input")

    if manifest.get("schema") != "d20.finite_state_collider_report_manifest@1":
        raise AssertionError("finite-state collider manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("finite-state collider manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("finite-state collider manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("finite-state collider manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("finite-state collider registry entry missing")
    if entry.get("status") != report.get("status"):
        raise AssertionError("finite-state collider registry status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("finite-state collider registry report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_finite_state_collider_report()
    print("D20 finite-state collider report validated")
