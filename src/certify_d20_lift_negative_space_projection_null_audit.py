from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_d20_lift_negative_space_projection_null_audit import (
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
    from derive_d20_lift_negative_space_projection_null_audit import (
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
    "prior_negative_space_grid_audit_certified",
    "cooriented_projection_has_exact_axis27_top_four",
    "regular_hex_projection_does_not_have_axis27_top_four",
    "unprojected_state_does_not_have_axis27_top_four",
    "eight_zero_tie_randomizations_tested",
    "all_zero_tie_randomizations_have_high_axis_band_28_to_33",
    "zero_tie_high_axis_band_is_not_fixed_at_27",
    "all_zero_tie_axis_power_z_scores_exceed_100",
    "some_zero_tie_spectra_depart_from_baseline",
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


def validate_d20_lift_negative_space_projection_null_audit() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)

    if artifact.get("schema") != "d20.proof_obligation.lift_negative_space_projection_null_audit.artifact@1":
        raise AssertionError("projection-null artifact schema mismatch")
    if artifact.get("status") != "D20_LIFT_NEGATIVE_SPACE_PROJECTION_NULL_AUDIT_DERIVED":
        raise AssertionError("projection-null artifact status mismatch")
    if _self_hash(artifact, "artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("projection-null artifact self hash mismatch")
    rebuilt_artifact = build_artifact()
    if rebuilt_artifact.get("artifact_sha256_excluding_this_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("projection-null artifact is not reproducible")

    checks = artifact.get("checks", {})
    if set(checks) != EXPECTED_CHECKS or any(checks.get(key) is not True for key in EXPECTED_CHECKS):
        raise AssertionError("projection-null checks mismatch")

    projections = {row.get("id"): row for row in artifact.get("projection_variants", [])}
    if projections.get("cooriented_screen_projection", {}).get("top_four_are_axis27") is not True:
        raise AssertionError("cooriented projection did not keep axis-27")
    if projections.get("regular_hex_projection", {}).get("top_four_are_axis27") is not False:
        raise AssertionError("regular-hex projection unexpectedly kept axis-27")
    if projections.get("unprojected_state_grid", {}).get("top_four_are_axis27") is not False:
        raise AssertionError("unprojected state unexpectedly kept axis-27")

    zero_tie = artifact.get("zero_tie_randomization_variants", [])
    if len(zero_tie) != 8:
        raise AssertionError("expected eight zero-tie randomizations")
    band_values = [row.get("high_axis_band_28_to_33") for row in zero_tie]
    if any(value is None or int(value) < 28 or int(value) > 33 for value in band_values):
        raise AssertionError("zero-tie high-axis band outside expected range")
    if any(int(value) == 27 for value in band_values):
        raise AssertionError("zero-tie band should not be recorded as exact 27")
    if any(float(row.get("negative_edge_axis_power", {}).get("axis_power_z_score", 0.0)) <= 100.0 for row in zero_tie):
        raise AssertionError("zero-tie axis-power z-score too small")
    if min(float(row.get("negative_edge_spectral_cosine_to_cooriented_baseline", 1.0)) for row in zero_tie) >= 0.50:
        raise AssertionError("zero-tie spectra did not witness departure from baseline")

    summary = artifact.get("summary", {})
    if summary.get("cooriented_exact_top_frequency_abs") != 27:
        raise AssertionError("cooriented exact frequency summary mismatch")
    if summary.get("zero_tie_high_axis_band_range") != [28, 33]:
        raise AssertionError("zero-tie band range mismatch")

    if report.get("schema") != "d20.proof_obligation.lift_negative_space_projection_null_audit@1":
        raise AssertionError("projection-null report schema mismatch")
    if report.get("status") != "D20_LIFT_NEGATIVE_SPACE_PROJECTION_NULL_AUDIT_CERTIFIED":
        raise AssertionError("projection-null report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("projection-null report checks did not pass")
    if report.get("checks") != checks:
        raise AssertionError("projection-null report checks differ from artifact")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("projection-null report self hash mismatch")
    expected_report = build_report(artifact)
    if expected_report.get("certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("projection-null report is not reproducible")

    _check_input_file(report.get("inputs", {}).get("artifact", {}), ARTIFACT_REL, "artifact input")
    _check_input_file(
        report.get("inputs", {}).get("visualization", {}),
        "generated/d20_sandpile_visualization.html",
        "visualization input",
    )
    _check_input_file(
        report.get("inputs", {}).get("prior_negative_space_grid_audit", {}),
        "data/invariants/d20/proof_obligations/d20_lift_negative_space_grid_perturbation_audit/report.json",
        "prior negative-space audit input",
    )
    _check_input_file(
        report.get("inputs", {}).get("validator", {}),
        "src/certify_d20_lift_negative_space_projection_null_audit.py",
        "validator input",
    )

    if manifest.get("schema") != "d20.proof_obligation.lift_negative_space_projection_null_audit_manifest@1":
        raise AssertionError("projection-null manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("projection-null manifest report hash mismatch")
    if manifest.get("artifact_sha256_excluding_hash_field") != artifact.get(
        "artifact_sha256_excluding_this_field"
    ):
        raise AssertionError("projection-null manifest artifact hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("projection-null manifest self hash mismatch")
    expected_manifest = build_manifest(report, artifact)
    if expected_manifest.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("projection-null manifest is not reproducible")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("projection-null registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("projection-null registry report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("projection-null registry status mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_lift_negative_space_projection_null_audit()
    print("D20 lift negative-space projection/null audit validated")
