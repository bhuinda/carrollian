from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_lift_negative_space_grid_perturbation_audit import (
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
    from derive_d20_lift_negative_space_grid_perturbation_audit import (
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
    "source_visualization_loaded",
    "robust_oblongness_theorem_certified",
    "intrinsic_hex_metric_certified",
    "seven_perturbation_variants_tested",
    "baseline_and_all_perturbations_have_axis27_top_four",
    "all_edge_axis_power_z_scores_exceed_100",
    "all_perturbed_edge_spectral_cosines_exceed_0_94",
    "all_perturbed_negative_jaccards_exceed_0_78",
    "exact_negative_edge_mask_not_claimed_invariant",
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


def _is_axis27(freq: list[int]) -> bool:
    return sorted([abs(int(freq[0])), abs(int(freq[1]))]) == [0, 27]


def validate_d20_lift_negative_space_grid_perturbation_audit() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.lift_negative_space_grid_perturbation_audit.artifact@1":
        raise AssertionError("negative-space grid artifact schema mismatch")
    if artifact.get("status") != "D20_LIFT_NEGATIVE_SPACE_GRID_PERTURBATION_AUDIT_DERIVED":
        raise AssertionError("negative-space grid artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("negative-space grid artifact self hash mismatch")

    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("negative-space grid artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("negative-space grid checks mismatch")

    variants = artifact.get("variants", [])
    if len(variants) != 7:
        raise AssertionError("expected seven perturbation variants")
    if variants[0].get("id") != "baseline":
        raise AssertionError("first variant must be baseline")
    nonbaseline = variants[1:]
    for row in variants:
        if row.get("top_four_are_axis_frequency_27") is not True:
            raise AssertionError(f"{row.get('id')} top-four axis-27 flag missing")
        if not all(_is_axis27(freq) for freq in row.get("top_four_frequency_signature", [])):
            raise AssertionError(f"{row.get('id')} top-four signature is not axis-27")
        if float(row.get("negative_edge_axis_power", {}).get("axis_power_z_score", 0.0)) <= 100.0:
            raise AssertionError(f"{row.get('id')} axis-power z-score too small")
    if not all(float(row.get("negative_edge_spectral_cosine_to_baseline", 0.0)) > 0.94 for row in nonbaseline):
        raise AssertionError("perturbed edge spectra are not close enough to baseline")
    if not all(float(row.get("negative_jaccard_to_baseline", 0.0)) > 0.78 for row in nonbaseline):
        raise AssertionError("perturbed negative masks are not close enough to baseline")
    if not any(float(row.get("negative_edge_jaccard_to_baseline", 1.0)) < 0.70 for row in nonbaseline):
        raise AssertionError("exact edge-mask non-invariance was not witnessed")

    summary = artifact.get("summary", {})
    if summary.get("common_top_four_axis_frequency_abs") != 27:
        raise AssertionError("common axis frequency summary mismatch")
    if float(summary.get("perturbed_edge_spectral_cosine_range", [0.0])[0]) <= 0.94:
        raise AssertionError("summary spectral cosine range mismatch")
    if float(summary.get("perturbed_negative_jaccard_range", [0.0])[0]) <= 0.78:
        raise AssertionError("summary negative jaccard range mismatch")

    if report.get("schema") != "d20.proof_obligation.lift_negative_space_grid_perturbation_audit@1":
        raise AssertionError("negative-space grid report schema mismatch")
    if report.get("status") != "D20_LIFT_NEGATIVE_SPACE_GRID_PERTURBATION_AUDIT_CERTIFIED":
        raise AssertionError("negative-space grid report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("negative-space grid report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("negative-space grid report checks differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("negative-space grid report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("negative-space grid report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("visualization", {}),
        "generated/d20_sandpile_visualization.html",
        "visualization input",
    )
    _check_input_file(
        report.get("inputs", {}).get("robust_oblongness_theorem_report", {}),
        "data/invariants/d20/theorems/d20_voltage_lift_robust_oblongness/report.json",
        "robust oblongness input",
    )
    _check_input_file(
        report.get("inputs", {}).get("intrinsic_hex_metric_report", {}),
        "data/invariants/d20/proof_obligations/d20_voltage_lift_intrinsic_hex_metric/report.json",
        "intrinsic hex input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_lift_negative_space_grid_perturbation_audit.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.lift_negative_space_grid_perturbation_audit_manifest@1":
        raise AssertionError("negative-space grid manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("negative-space grid manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("negative-space grid manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("negative-space grid manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("negative-space grid manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("negative-space grid registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("negative-space grid registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("negative-space grid registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_lift_negative_space_grid_perturbation_audit()
    print("D20 lift negative-space grid perturbation audit validated")
