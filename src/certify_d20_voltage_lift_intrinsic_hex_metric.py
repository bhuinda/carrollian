from __future__ import annotations
import sitecustomize as _carrollian_token_burn_guard_bootstrap  # noqa: F401  # carrollian-token-burn-guard-bootstrap

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json


THEOREM_ID = "d20_voltage_lift_intrinsic_hex_metric"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"
ARTIFACT_REL = "generated/d20_voltage_lift_intrinsic_hex_metric.json"
FAMILY_REL = "generated/d20_voltage_lift_family_comparison.json"


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


def _close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance


def validate_d20_voltage_lift_intrinsic_hex_metric() -> dict[str, Any]:
    artifact = _load_json(ARTIFACT_REL)
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)
    family = _load_json(FAMILY_REL)

    if artifact.get("schema") != "d20.sandpile.voltage_lift.intrinsic_hex_metric@1":
        raise AssertionError("intrinsic hex metric artifact schema mismatch")
    if artifact.get("status") != "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_DERIVED":
        raise AssertionError("intrinsic hex metric artifact status mismatch")
    artifact_hash = _artifact_hash(artifact)
    if artifact_hash != artifact.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("intrinsic hex metric artifact self hash mismatch")
    if artifact.get("edge_count") != 30:
        raise AssertionError("intrinsic hex metric edge count mismatch")
    if artifact.get("intrinsic_definition", {}).get("residual_label_symmetry") != "Dih_6":
        raise AssertionError("intrinsic hex metric residual symmetry mismatch")
    if artifact.get("intrinsic_definition", {}).get("selector_boundary") != (
        "selector_choice is read only for audit histograms and is not used by the intrinsic hex metric"
    ):
        raise AssertionError("intrinsic hex metric selector boundary mismatch")
    if artifact.get("selector_choice_histogram_not_used_by_metric") != {"0": 14, "1": 10, "2": 6}:
        raise AssertionError("intrinsic hex metric selector histogram mismatch")

    cov = artifact.get("covariance", {})
    if cov.get("exact_matrix") != [["5/4", "-1/10*sqrt(3)"], ["-1/10*sqrt(3)", "29/20"]]:
        raise AssertionError("intrinsic hex metric covariance matrix mismatch")
    if cov.get("eigenvalues_exact") != {"major": "31/20", "minor": "23/20"}:
        raise AssertionError("intrinsic hex metric eigenvalue mismatch")
    if cov.get("anisotropy_ratio_exact") != "31/23":
        raise AssertionError("intrinsic hex metric ratio mismatch")
    if not _close(float(cov.get("anisotropy_ratio")), 31 / 23):
        raise AssertionError("intrinsic hex metric numeric ratio mismatch")
    if not _close(float(cov.get("principal_axis_angle_degrees")), -60.0):
        raise AssertionError("intrinsic hex metric axis mismatch")

    checks = artifact.get("checks", {})
    required_artifact_checks = {
        "all_edges_change_one_signed_label",
        "coorient_source_residual_symmetry_is_dih6",
        "edge_count_is_30",
        "metric_does_not_use_selector_choice",
        "regular_hex_label_delta_family_variant_matches",
        "anisotropy_ratio_is_31_over_23",
    }
    if any(checks.get(key) is not True for key in required_artifact_checks):
        raise AssertionError("intrinsic hex metric artifact check failed")

    family_variant = next((row for row in family.get("variants", []) if row.get("id") == "regular_hex_label_delta"), None)
    if family_variant is None:
        raise AssertionError("regular hex label-delta family variant missing")
    if not _close(float(family_variant["covariance"]["anisotropy_ratio"]), float(cov["anisotropy_ratio"])):
        raise AssertionError("intrinsic hex metric family ratio mismatch")
    if not _close(float(family_variant["covariance"]["principal_axis_angle_degrees"]), -60.0):
        raise AssertionError("intrinsic hex metric family axis mismatch")

    if report.get("schema") != "d20.proof_obligation.voltage_lift_intrinsic_hex_metric@1":
        raise AssertionError("intrinsic hex metric report schema mismatch")
    if report.get("status") != "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_CERTIFIED":
        raise AssertionError("intrinsic hex metric report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("intrinsic hex metric report checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("intrinsic hex metric report self hash mismatch")
    report_artifact_input = report.get("inputs", {}).get("intrinsic_hex_metric_artifact", {})
    if report_artifact_input.get("path") != ARTIFACT_REL:
        raise AssertionError("intrinsic hex metric report artifact path mismatch")
    if h_file(ROOT / ARTIFACT_REL) != report_artifact_input.get("sha256"):
        raise AssertionError("intrinsic hex metric artifact file hash mismatch")
    if artifact_hash != report_artifact_input.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("intrinsic hex metric artifact hash input mismatch")

    if manifest.get("schema") != "d20.proof_obligation.voltage_lift_intrinsic_hex_metric_manifest@1":
        raise AssertionError("intrinsic hex metric manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("intrinsic hex metric manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("intrinsic hex metric manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("intrinsic hex metric registry entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("intrinsic hex metric registry report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")
    return report


if __name__ == "__main__":
    validate_d20_voltage_lift_intrinsic_hex_metric()
    print("D20 voltage lift intrinsic hex metric proof obligation validated")
