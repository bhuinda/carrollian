from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_sector33_w24_marked_quotient_shadow_obstruction import (
        ARTIFACT_PATH,
        INDEX_PATH,
        OUT_DIR,
        THEOREM_ID,
        build_artifact,
        build_manifest,
        build_report,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_d20_sector33_w24_marked_quotient_shadow_obstruction import (
        ARTIFACT_PATH,
        INDEX_PATH,
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

EXPECTED_CHECKS = {
    "w24_row_alphabetization_is_certified",
    "per_edge_rowspace_prune_input_is_certified",
    "f4_row_lift_solver_input_is_certified",
    "sector33_dual_input_is_certified",
    "target_golay_is_self_dual_rank12",
    "target_allowed_weights_are_0_8_12_16_24",
    "extra_removed_pool_has_25_edges",
    "primal_orthogonal_shadow_cases_are_25",
    "primal_orthogonal_shadow_rank_histogram_is_5_6",
    "primal_orthogonal_shadow_has_no_golay_weight_compatible_case",
    "dual_rowspace_shadow_cases_are_25",
    "dual_rowspace_shadow_rank_histogram_is_3",
    "dual_rowspace_shadow_has_no_golay_weight_compatible_case",
    "weight_obstruction_is_coordinate_permutation_invariant",
    "marked_quotient_shadow_route_remains_open_outside_tested_family",
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


def _check_shadow_summary(summary: dict[str, Any], rank_histogram: dict[str, int]) -> None:
    if summary.get("case_count") != 25:
        raise AssertionError("shadow case count mismatch")
    if summary.get("rank_histogram") != rank_histogram:
        raise AssertionError("shadow rank histogram mismatch")
    if summary.get("golay_weight_compatible_case_count") != 0:
        raise AssertionError("unexpected Golay-compatible shadow case")
    if summary.get("all_cases_have_forbidden_weights") is not True:
        raise AssertionError("shadow did not record forbidden weights in every case")
    records = summary.get("sample_records", [])
    if not records:
        raise AssertionError("shadow sample records missing")
    for record in records:
        if record.get("golay_weight_compatible") is not False:
            raise AssertionError("sample record unexpectedly Golay-compatible")
        if not record.get("forbidden_weights"):
            raise AssertionError("sample record forbidden weights missing")


def validate_d20_sector33_w24_marked_quotient_shadow_obstruction() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_quotient_shadow_obstruction.artifact@1"
    ):
        raise AssertionError("marked quotient shadow artifact schema mismatch")
    if artifact.get("status") != "D20_SECTOR33_W24_MARKED_QUOTIENT_SHADOW_OBSTRUCTION_DERIVED":
        raise AssertionError("marked quotient shadow artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("marked quotient shadow artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("marked quotient shadow artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("marked quotient shadow checks mismatch")

    target = artifact.get("target_golay_weight_test", {})
    if target.get("target_rank") != 12 or target.get("self_dual") is not True:
        raise AssertionError("target Golay profile mismatch")
    if target.get("allowed_nonzero_weights") != [8, 12, 16, 24]:
        raise AssertionError("target Golay allowed weights mismatch")
    if target.get("coordinate_permutation_invariant") is not True:
        raise AssertionError("target Golay coordinate-invariance flag mismatch")

    analysis = artifact.get("deletion_shadow_analysis", {})
    if analysis.get("fixed_removed_cocircuit") != [1, 2, 11, 21, 22, 30]:
        raise AssertionError("fixed cocircuit mismatch")
    if analysis.get("extra_removed_count") != 25:
        raise AssertionError("extra pool count mismatch")
    if analysis.get("allowed_golay_weights") != [0, 8, 12, 16, 24]:
        raise AssertionError("allowed Golay weights mismatch")
    shadows = analysis.get("shadow_summaries", {})
    _check_shadow_summary(shadows.get("primal_orthogonal_shadow", {}), {"5": 20, "6": 5})
    _check_shadow_summary(shadows.get("dual_rowspace_shadow", {}), {"3": 25})

    if report.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_quotient_shadow_obstruction@1"
    ):
        raise AssertionError("marked quotient shadow report schema mismatch")
    if report.get("status") != "D20_SECTOR33_W24_MARKED_QUOTIENT_SHADOW_OBSTRUCTION_CERTIFIED":
        raise AssertionError("marked quotient shadow report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("marked quotient shadow report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("marked quotient shadow report checks mismatch")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("marked quotient shadow report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("marked quotient shadow report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("derive_script", {}),
        "src/derive_d20_sector33_w24_marked_quotient_shadow_obstruction.py",
        "derive input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_sector33_w24_marked_quotient_shadow_obstruction.py",
        "validator input",
    )

    if manifest.get("schema") != (
        "d20.proof_obligation.sector33_w24_marked_quotient_shadow_obstruction_manifest@1"
    ):
        raise AssertionError("marked quotient shadow manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("marked quotient shadow manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("marked quotient shadow manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("marked quotient shadow manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("marked quotient shadow manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("marked quotient shadow registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("marked quotient shadow registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("marked quotient shadow registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_sector33_w24_marked_quotient_shadow_obstruction()
    print("D20 sector33 W24 marked quotient shadow obstruction validated")
