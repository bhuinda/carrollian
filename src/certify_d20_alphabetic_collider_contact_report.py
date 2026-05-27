from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401

import json
import math
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_alphabetic_collider_contact_report import (
        ARTIFACT_PATH,
        BATCH_SHOTS,
        BASE_COLLIDER_DERIVE_SCRIPT,
        GATE_AUTOMATON_REPORT,
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
    from derive_d20_alphabetic_collider_contact_report import (
        ARTIFACT_PATH,
        BATCH_SHOTS,
        BASE_COLLIDER_DERIVE_SCRIPT,
        GATE_AUTOMATON_REPORT,
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
GATE_AUTOMATON_REPORT_REL = GATE_AUTOMATON_REPORT.relative_to(ROOT).as_posix()
VISUALIZATION_REL = VISUALIZATION.relative_to(ROOT).as_posix()
VALIDATOR_REL = VALIDATOR.relative_to(ROOT).as_posix()
BASE_COLLIDER_DERIVE_SCRIPT_REL = BASE_COLLIDER_DERIVE_SCRIPT.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "stress_graph_certified",
    "gate_automaton_certified",
    "lambda3_h6_boundary_has_20_atoms",
    "gate_sequence_has_16_symbols",
    "accepting_states_match_six_branches",
    "missing_apertures_are_x2_x4",
    "renderer_embeds_alphabetic_contact_harness",
    "renderer_embeds_alphabetic_interaction_mask",
    "null_assignment_is_permutation",
    "shot_count_matches_collider_batch",
    "kiss_activity_observed",
    "finite_alphabetic_values",
    "rates_in_unit_interval",
}

RATE_KEYS = (
    "kiss_rate",
    "match_rate",
    "accept_rate",
    "certified_trigram_rate",
    "missing_aperture_rate",
    "letter_entropy",
)


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


def _assert_rate(value: Any, label: str) -> None:
    _assert_finite(value, label)
    if not (0.0 <= float(value) <= 1.0):
        raise AssertionError(f"{label} is outside [0, 1]")


def _validate_side(data: dict[str, Any], side: str) -> None:
    averages = data.get("averages", {})
    shots = data.get("shots", [])
    if len(shots) != BATCH_SHOTS:
        raise AssertionError(f"{side} shot count mismatch")
    for key in (
        "contacts",
        "captures",
        "escapes",
        "residue",
        "clump",
        "kiss_contacts",
        "coarse_contacts",
        *RATE_KEYS,
    ):
        _assert_finite(averages.get(key), f"{side} average {key}")
    for key in RATE_KEYS:
        _assert_rate(averages.get(key), f"{side} average {key}")
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
        alphabet = shot.get("alphabet", {})
        for key in (
            "raw_contacts",
            "kiss_contacts",
            "coarse_contacts",
            "matched_letters",
            "rejected_letters",
            "branch_accepts",
            "completed_words",
            "certified_trigram_hits",
            "uncertified_trigram_hits",
            "missing_aperture_hits",
        ):
            _assert_finite(alphabet.get(key), f"{side} shot {shot.get('shot')} alphabet {key}")
        if len(alphabet.get("letter_counts", [])) != 6:
            raise AssertionError(f"{side} shot {shot.get('shot')} alphabet count shape mismatch")
        for key in RATE_KEYS:
            _assert_rate(alphabet.get(key), f"{side} shot {shot.get('shot')} alphabet {key}")


def validate_d20_alphabetic_collider_contact_report() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.alphabetic_collider_contact_report.artifact@1":
        raise AssertionError("alphabetic collider artifact schema mismatch")
    if artifact.get("status") != "D20_ALPHABETIC_COLLIDER_CONTACT_REPORT_DERIVED":
        raise AssertionError("alphabetic collider artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("alphabetic collider artifact self hash mismatch")
    expected_artifact = build_artifact()
    if expected_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("alphabetic collider artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise AssertionError("alphabetic collider checks mismatch")

    witness = artifact.get("witness", {})
    _validate_side(witness.get("real", {}), "real")
    _validate_side(witness.get("null", {}), "null")
    deltas = witness.get("deltas_real_minus_null", {})
    for key in RATE_KEYS:
        _assert_finite(deltas.get(key), f"delta {key}")

    if report.get("schema") != "d20.alphabetic_collider_contact_report@1":
        raise AssertionError("alphabetic collider report schema mismatch")
    if report.get("status") != "D20_ALPHABETIC_COLLIDER_CONTACT_REPORT_CERTIFIED":
        raise AssertionError("alphabetic collider report status mismatch")
    if report.get("checks") != checks:
        raise AssertionError("alphabetic collider report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("alphabetic collider report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("alphabetic collider report is not reproducible")
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
    _check_input_file(
        inputs.get("gate_automaton_report", {}),
        GATE_AUTOMATON_REPORT_REL,
        "gate automaton report input",
    )
    _check_input_file(inputs.get("visualization", {}), VISUALIZATION_REL, "visualization input")
    _check_input_file(
        inputs.get("base_collider_derive_script", {}),
        BASE_COLLIDER_DERIVE_SCRIPT_REL,
        "base collider derive script input",
    )

    if manifest.get("schema") != "d20.alphabetic_collider_contact_report_manifest@1":
        raise AssertionError("alphabetic collider manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("alphabetic collider manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("alphabetic collider manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("alphabetic collider manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("alphabetic collider registry entry missing")
    if entry.get("status") != report.get("status"):
        raise AssertionError("alphabetic collider registry status mismatch")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("alphabetic collider registry report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_alphabetic_collider_contact_report()
    print("D20 alphabetic collider contact report validated")
