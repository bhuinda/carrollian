from __future__ import annotations

import json
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json


THEOREM_ID = "d20_voltage_lift_robust_oblongness"
REPORT_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/theorems/{THEOREM_ID}/manifest.json"
THEOREM_INDEX_REL = "data/invariants/d20/theorems/index.json"
PROOF_INDEX_REL = "data/invariants/d20/proof_obligations/index.json"
FAMILY_ARTIFACT_REL = "generated/d20_voltage_lift_family_comparison.json"
INTRINSIC_ARTIFACT_REL = "generated/d20_voltage_lift_intrinsic_hex_metric.json"
INTRINSIC_REPORT_REL = (
    "data/invariants/d20/proof_obligations/d20_voltage_lift_intrinsic_hex_metric/report.json"
)
FAMILY_OBLIGATION_REL = (
    "data/invariants/d20/proof_obligations/d20_voltage_lift_family_robust_oblongness/report.json"
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


def _artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return h_json(tmp)


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    return ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def _close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance


def validate_d20_voltage_lift_robust_oblongness() -> dict[str, Any]:
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    theorem_index = _load_json(THEOREM_INDEX_REL)
    proof_index = _load_json(PROOF_INDEX_REL)
    family = _load_json(FAMILY_ARTIFACT_REL)
    intrinsic = _load_json(INTRINSIC_ARTIFACT_REL)
    intrinsic_report = _load_json(INTRINSIC_REPORT_REL)
    family_obligation = _load_json(FAMILY_OBLIGATION_REL)

    if report.get("schema") != "d20.theorem.voltage_lift_robust_oblongness@1":
        raise AssertionError("robust oblongness theorem schema mismatch")
    if report.get("status") != "D20_VOLTAGE_LIFT_ROBUST_OBLONGNESS_CERTIFIED":
        raise AssertionError("robust oblongness theorem status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("robust oblongness theorem checks did not pass")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("robust oblongness theorem self hash mismatch")

    if manifest.get("schema") != "d20.theorem.voltage_lift_robust_oblongness_manifest@1":
        raise AssertionError("robust oblongness manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("robust oblongness manifest report hash mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("robust oblongness manifest self hash mismatch")

    if _artifact_hash(family) != family.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("family artifact hash mismatch")
    if _artifact_hash(intrinsic) != intrinsic.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("intrinsic artifact hash mismatch")
    if intrinsic_report.get("status") != "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_CERTIFIED":
        raise AssertionError("intrinsic metric report status mismatch")
    if intrinsic.get("covariance", {}).get("anisotropy_ratio_exact") != "31/23":
        raise AssertionError("intrinsic metric exact ratio mismatch")

    variants = family.get("variants", [])
    if len(variants) != 5:
        raise AssertionError("expected five named lift variants")
    ratios = [float(row["covariance"]["anisotropy_ratio"]) for row in variants]
    if not all(ratio > 1.0 for ratio in ratios):
        raise AssertionError("not all named lift variants are oblong")
    summary = family.get("survival_summary", {})
    if summary.get("variants_tested") != 5 or summary.get("anisotropic_variant_count") != 5:
        raise AssertionError("family survival count mismatch")
    if not _close(float(summary.get("anisotropy_ratio_min")), min(ratios)):
        raise AssertionError("family survival min mismatch")
    if not _close(float(summary.get("anisotropy_ratio_median")), _median(ratios)):
        raise AssertionError("family survival median mismatch")
    if not _close(float(summary.get("anisotropy_ratio_max")), max(ratios)):
        raise AssertionError("family survival max mismatch")

    witness = report.get("witness", {})
    if witness.get("variants_tested") != 5:
        raise AssertionError("theorem witness variant count mismatch")
    if witness.get("anisotropic_variant_count") != 5:
        raise AssertionError("theorem witness anisotropic count mismatch")
    if witness.get("intrinsic_ratio_exact") != "31/23":
        raise AssertionError("theorem witness intrinsic ratio mismatch")
    if not _close(float(witness.get("intrinsic_ratio")), 31 / 23):
        raise AssertionError("theorem witness intrinsic numeric ratio mismatch")
    if not _close(float(witness.get("coordinate_amplification_over_intrinsic")), max(ratios) / (31 / 23)):
        raise AssertionError("theorem witness coordinate amplification mismatch")
    if witness.get("ranking_by_anisotropy_desc", [{}])[0].get("id") != "cooriented_sign_selector":
        raise AssertionError("cooriented selector is not recorded as strongest projection")

    checks = report.get("checks", {})
    required_checks = {
        "family_artifact_hash_verified",
        "intrinsic_artifact_hash_verified",
        "five_named_variants_tested",
        "all_named_variants_are_oblong",
        "summary_min_median_max_match_variants",
        "intrinsic_ratio_is_31_over_23",
        "regular_hex_label_delta_matches_intrinsic",
        "cooriented_selector_is_coordinate_amplified",
    }
    if any(checks.get(key) is not True for key in required_checks):
        raise AssertionError("robust oblongness theorem check failed")

    theorem_entry = next(
        (row for row in theorem_index.get("theorems", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if theorem_entry is None:
        raise AssertionError("robust oblongness theorem registry entry missing")
    if theorem_entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("robust oblongness theorem registry hash mismatch")
    if _self_hash(theorem_index, "registry_sha256") != theorem_index.get("registry_sha256"):
        raise AssertionError("theorem registry self hash mismatch")

    proof_entry = next(
        (
            row
            for row in proof_index.get("obligations", [])
            if row.get("id") == "d20_voltage_lift_family_robust_oblongness"
        ),
        None,
    )
    if proof_entry is None:
        raise AssertionError("family robust-oblongness proof obligation registry entry missing")
    if proof_entry.get("status") != "D20_VOLTAGE_LIFT_FAMILY_ROBUST_OBLONGNESS_CERTIFIED":
        raise AssertionError("family robust-oblongness proof obligation not closed")
    if proof_entry.get("report_sha256") != family_obligation.get("certificate_sha256"):
        raise AssertionError("family robust-oblongness proof obligation registry hash mismatch")
    if _self_hash(proof_index, "registry_sha256") != proof_index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    if family_obligation.get("status") != "D20_VOLTAGE_LIFT_FAMILY_ROBUST_OBLONGNESS_CERTIFIED":
        raise AssertionError("family robust-oblongness obligation status mismatch")
    if family_obligation.get("all_checks_pass") is not True:
        raise AssertionError("family robust-oblongness obligation checks did not pass")
    if family_obligation.get("open_obligations") != []:
        raise AssertionError("family robust-oblongness obligation still has open obligations")
    witnessed = {row.get("id"): row for row in family_obligation.get("witnessed_obligations", [])}
    proof_layer = witnessed.get("proof_layer_integration")
    if proof_layer is None or proof_layer.get("status") != "witnessed":
        raise AssertionError("proof-layer integration was not witnessed")
    if proof_layer.get("witness_report") != REPORT_REL:
        raise AssertionError("proof-layer witness report mismatch")
    if proof_layer.get("witness_sha256") != report.get("certificate_sha256"):
        raise AssertionError("proof-layer witness hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_voltage_lift_robust_oblongness()
    print("D20 voltage lift robust oblongness theorem validated")
