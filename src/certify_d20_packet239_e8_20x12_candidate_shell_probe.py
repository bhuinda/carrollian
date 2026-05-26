from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_packet239_e8_20x12_candidate_shell_probe import (
        ARTIFACT_PATH,
        FULL_EXPOSURE_FRAME_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PREVIOUS_PROBE_REPORT,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_packet239_e8_20x12_candidate_shell_probe import (
        ARTIFACT_PATH,
        FULL_EXPOSURE_FRAME_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PREVIOUS_PROBE_REPORT,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )


ARTIFACT_REL = ARTIFACT_PATH.relative_to(ROOT).as_posix()
REPORT_REL = (OUT_DIR / "report.json").relative_to(ROOT).as_posix()
MANIFEST_REL = (OUT_DIR / "manifest.json").relative_to(ROOT).as_posix()
INDEX_REL = INDEX_PATH.relative_to(ROOT).as_posix()
PREVIOUS_PROBE_REL = PREVIOUS_PROBE_REPORT.relative_to(ROOT).as_posix()
FULL_FRAME_REL = FULL_EXPOSURE_FRAME_REPORT.relative_to(ROOT).as_posix()

EXPECTED_CHECKS = {
    "d20_input_is_certified",
    "previous_packet239_e8_probe_is_certified",
    "full_exposure_frame_is_certified",
    "a12_class_count_is_12",
    "full_exposure_packet_count_is_20",
    "cartesian_candidate_has_240_rows",
    "candidate_rows_are_uniquely_labelled",
    "packet239_contributes_12_candidate_rows",
    "natural_product_embedding_has_240_norm2_vectors",
    "standard_e8_shell_has_240_norm2_roots",
    "standard_e8_shell_rank_is_8",
    "natural_product_embedding_rank_is_31",
    "natural_product_embedding_rank_is_not_e8_rank",
    "standard_e8_shell_has_240_ordered_antipodal_pairs",
    "natural_product_embedding_has_no_antipodal_pairs",
    "natural_product_embedding_inner_histogram_is_not_e8",
    "candidate_is_cardinality_match_not_root_witness",
    "nontrivial_morphism_or_projection_still_required",
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


def _artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return h_json(tmp)


def _check_input_file(entry: dict[str, Any], rel_path: str, label: str) -> None:
    if entry.get("path") != rel_path:
        raise AssertionError(f"{label} input path mismatch")
    if h_file(ROOT / rel_path) != entry.get("sha256"):
        raise AssertionError(f"{label} input file hash mismatch")


def validate_d20_packet239_e8_20x12_candidate_shell_probe() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if (
        artifact.get("schema")
        != "d20.proof_obligation.packet239_e8_20x12_candidate_shell_probe.artifact@1"
    ):
        raise AssertionError("packet239 E8 20x12 artifact schema mismatch")
    if artifact.get("status") != "D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_DERIVED":
        raise AssertionError("packet239 E8 20x12 artifact status mismatch")
    artifact_sha = _artifact_hash(artifact)
    if artifact_sha != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("packet239 E8 20x12 artifact self hash mismatch")
    if build_artifact() != artifact:
        raise AssertionError("packet239 E8 20x12 artifact does not replay")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("packet239 E8 20x12 checks mismatch")

    witness = artifact.get("witness", {})
    candidate = witness.get("candidate_definition", {})
    if candidate.get("full_exposure_packet_count") != 20:
        raise AssertionError("packet239 E8 20x12 full exposure count mismatch")
    if candidate.get("a12_class_count") != 12:
        raise AssertionError("packet239 E8 20x12 A12 count mismatch")
    if candidate.get("candidate_count") != 240:
        raise AssertionError("packet239 E8 20x12 candidate count mismatch")
    rows = candidate.get("candidate_rows", [])
    if len(rows) != 240:
        raise AssertionError("packet239 E8 20x12 candidate row length mismatch")
    if len({row.get("candidate_label") for row in rows}) != 240:
        raise AssertionError("packet239 E8 20x12 candidate label uniqueness mismatch")
    packet239_rows = [row for row in rows if row.get("packet_id") == 239]
    if len(packet239_rows) != 12:
        raise AssertionError("packet239 E8 20x12 packet239 row count mismatch")
    if {row.get("a12_class") for row in packet239_rows} != set(range(12)):
        raise AssertionError("packet239 E8 20x12 packet239 A12 coverage mismatch")

    product_stats = witness.get("natural_product_embedding", {}).get("stats", {})
    e8_stats = witness.get("standard_e8_reference_shell", {}).get("stats", {})
    if product_stats.get("vector_count") != 240 or product_stats.get("ambient_dimension") != 32:
        raise AssertionError("packet239 E8 20x12 product shape mismatch")
    if product_stats.get("rank_over_q") != 31:
        raise AssertionError("packet239 E8 20x12 product rank mismatch")
    if product_stats.get("norm_sq_histogram") != {"2": 240}:
        raise AssertionError("packet239 E8 20x12 product norm mismatch")
    if product_stats.get("ordered_inner_product_histogram") != {
        "0": 50160,
        "1": 7200,
        "2": 240,
    }:
        raise AssertionError("packet239 E8 20x12 product inner histogram mismatch")

    if e8_stats.get("vector_count") != 240 or e8_stats.get("ambient_dimension") != 8:
        raise AssertionError("packet239 E8 20x12 E8 shape mismatch")
    if e8_stats.get("rank_over_q") != 8:
        raise AssertionError("packet239 E8 20x12 E8 rank mismatch")
    if e8_stats.get("norm_sq_histogram") != {"2": 240}:
        raise AssertionError("packet239 E8 20x12 E8 norm mismatch")
    e8_hist = e8_stats.get("ordered_inner_product_histogram", {})
    if e8_hist.get("-2") != 240 or e8_hist.get("2") != 240:
        raise AssertionError("packet239 E8 20x12 E8 antipodal/diagonal mismatch")
    if e8_hist == product_stats.get("ordered_inner_product_histogram"):
        raise AssertionError("packet239 E8 20x12 inner histograms unexpectedly match")

    comparison = witness.get("comparison", {})
    if comparison.get("same_cardinality") is not True:
        raise AssertionError("packet239 E8 20x12 cardinality comparison mismatch")
    if comparison.get("same_norm_square") is not True:
        raise AssertionError("packet239 E8 20x12 norm comparison mismatch")
    if comparison.get("rank_product") != 31 or comparison.get("rank_e8") != 8:
        raise AssertionError("packet239 E8 20x12 rank comparison mismatch")
    if comparison.get("ordered_antipodal_pairs_product") != 0:
        raise AssertionError("packet239 E8 20x12 product antipodal mismatch")
    if comparison.get("ordered_antipodal_pairs_e8") != 240:
        raise AssertionError("packet239 E8 20x12 E8 antipodal mismatch")

    _check_input_file(artifact.get("inputs", {}).get("d20", {}), "d20.json", "artifact d20")
    _check_input_file(
        artifact.get("inputs", {}).get("previous_packet239_e8_probe", {}),
        PREVIOUS_PROBE_REL,
        "artifact previous probe",
    )
    _check_input_file(
        artifact.get("inputs", {}).get("full_exposure_frame", {}),
        FULL_FRAME_REL,
        "artifact full frame",
    )

    if report.get("schema") != "d20.proof_obligation.packet239_e8_20x12_candidate_shell_probe@1":
        raise AssertionError("packet239 E8 20x12 report schema mismatch")
    if report.get("status") != "D20_PACKET239_E8_20X12_CANDIDATE_SHELL_PROBE_CERTIFIED":
        raise AssertionError("packet239 E8 20x12 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("packet239 E8 20x12 report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("packet239 E8 20x12 report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 20x12 report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 20x12 report is not reproducible")
    if report.get("witness") != witness:
        raise AssertionError("packet239 E8 20x12 report witness mismatch")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "report artifact")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_packet239_e8_20x12_candidate_shell_probe.py",
        "derive script",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_packet239_e8_20x12_candidate_shell_probe.py",
        "validator",
    )
    _check_input_file(report.get("inputs", {}).get("d20", {}), "d20.json", "report d20")
    _check_input_file(
        report.get("inputs", {}).get("previous_packet239_e8_probe", {}),
        PREVIOUS_PROBE_REL,
        "report previous probe",
    )
    _check_input_file(
        report.get("inputs", {}).get("full_exposure_frame", {}),
        FULL_FRAME_REL,
        "report full frame",
    )

    if (
        manifest.get("schema")
        != "d20.proof_obligation.packet239_e8_20x12_candidate_shell_probe_manifest@1"
    ):
        raise AssertionError("packet239 E8 20x12 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 20x12 manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact_sha:
        raise AssertionError("packet239 E8 20x12 manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("packet239 E8 20x12 manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("packet239 E8 20x12 manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("packet239 E8 20x12 registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("packet239 E8 20x12 registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("packet239 E8 20x12 registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_packet239_e8_20x12_candidate_shell_probe()
    print("D20 packet239 E8 20x12 candidate shell probe certificate validated")
