from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .certify_io import ROOT, h_file, h_json
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json


THEOREM_ID = "d20_voltage_lift_family_robust_oblongness"
REPORT_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json"
MANIFEST_REL = f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json"
INDEX_REL = "data/invariants/d20/proof_obligations/index.json"
FAMILY_REL = "generated/d20_voltage_lift_family_comparison.json"
INTRINSIC_ARTIFACT_REL = "generated/d20_voltage_lift_intrinsic_hex_metric.json"
INTRINSIC_REPORT_REL = (
    "data/invariants/d20/proof_obligations/d20_voltage_lift_intrinsic_hex_metric/report.json"
)
ROBUST_THEOREM_REPORT_REL = "data/invariants/d20/theorems/d20_voltage_lift_robust_oblongness/report.json"


def _load_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _self_hash(payload: dict[str, Any], field: str) -> str:
    tmp = dict(payload)
    tmp.pop(field, None)
    return h_json(tmp)


def _family_artifact_hash(family: dict[str, Any]) -> str:
    tmp = dict(family)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return h_json(tmp)


def _artifact_hash(payload: dict[str, Any]) -> str:
    tmp = dict(payload)
    tmp.pop("artifact_sha256_excluding_this_field", None)
    return h_json(tmp)


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n % 2 == 1:
        return ordered[n // 2]
    return (ordered[n // 2 - 1] + ordered[n // 2]) / 2


def _close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return abs(a - b) <= tolerance


def validate_d20_voltage_lift_family_robust_oblongness() -> dict[str, Any]:
    report = _load_json(REPORT_REL)
    manifest = _load_json(MANIFEST_REL)
    index = _load_json(INDEX_REL)
    family = _load_json(FAMILY_REL)
    intrinsic = _load_json(INTRINSIC_ARTIFACT_REL)
    intrinsic_report = _load_json(INTRINSIC_REPORT_REL)
    theorem_report = None
    theorem_path = ROOT / ROBUST_THEOREM_REPORT_REL
    if theorem_path.exists():
        theorem_report = _load_json(ROBUST_THEOREM_REPORT_REL)

    if report.get("schema") != "d20.proof_obligation.voltage_lift_family_robust_oblongness@1":
        raise AssertionError("proof obligation schema mismatch")
    status = report.get("status")
    if status not in {
        "D20_VOLTAGE_LIFT_FAMILY_ROBUST_OBLONGNESS_NEEDS_REVIEW",
        "D20_VOLTAGE_LIFT_FAMILY_ROBUST_OBLONGNESS_CERTIFIED",
    }:
        raise AssertionError("proof obligation status mismatch")
    if status == "D20_VOLTAGE_LIFT_FAMILY_ROBUST_OBLONGNESS_NEEDS_REVIEW":
        if report.get("all_checks_pass") is not False:
            raise AssertionError("provisional proof obligation must not claim theorem closure")
    if status == "D20_VOLTAGE_LIFT_FAMILY_ROBUST_OBLONGNESS_CERTIFIED":
        if report.get("all_checks_pass") is not True:
            raise AssertionError("certified proof obligation checks did not pass")
    if report.get("witness_checks_pass") is not True:
        raise AssertionError("witness checks are not marked as passing")
    if _self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("proof obligation report self hash mismatch")

    if manifest.get("schema") != "d20.proof_obligation.voltage_lift_family_robust_oblongness_manifest@1":
        raise AssertionError("proof obligation manifest schema mismatch")
    if _self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("proof obligation manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("proof obligation manifest report hash mismatch")

    family_input = report.get("inputs", {}).get("voltage_lift_family_comparison", {})
    if family_input.get("path") != FAMILY_REL:
        raise AssertionError("family artifact path mismatch")
    if h_file(ROOT / FAMILY_REL) != family_input.get("sha256"):
        raise AssertionError("family artifact file hash mismatch")
    artifact_hash = _family_artifact_hash(family)
    if artifact_hash != family.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("family artifact internal hash mismatch")
    if artifact_hash != family_input.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("family artifact embedded hash mismatch")

    intrinsic_input = report.get("inputs", {}).get("intrinsic_hex_metric_artifact", {})
    if intrinsic_input.get("path") != INTRINSIC_ARTIFACT_REL:
        raise AssertionError("intrinsic hex metric artifact input missing")
    if h_file(ROOT / INTRINSIC_ARTIFACT_REL) != intrinsic_input.get("sha256"):
        raise AssertionError("intrinsic hex metric artifact file hash mismatch")
    intrinsic_hash = _artifact_hash(intrinsic)
    if intrinsic_hash != intrinsic.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("intrinsic hex metric artifact self hash mismatch")
    if intrinsic_hash != intrinsic_input.get("artifact_sha256_excluding_this_field"):
        raise AssertionError("intrinsic hex metric artifact embedded hash mismatch")
    if intrinsic.get("covariance", {}).get("anisotropy_ratio_exact") != "31/23":
        raise AssertionError("intrinsic hex metric ratio mismatch")
    if intrinsic.get("render_family_comparison", {}).get("matched_variant_id") != "regular_hex_label_delta":
        raise AssertionError("intrinsic hex metric family match mismatch")

    intrinsic_report_input = report.get("inputs", {}).get("intrinsic_hex_metric_report", {})
    if intrinsic_report_input.get("path") != INTRINSIC_REPORT_REL:
        raise AssertionError("intrinsic hex metric report input missing")
    if intrinsic_report.get("status") != "D20_VOLTAGE_LIFT_INTRINSIC_HEX_METRIC_CERTIFIED":
        raise AssertionError("intrinsic hex metric report status mismatch")
    if intrinsic_report.get("certificate_sha256") != intrinsic_report_input.get("certificate_sha256"):
        raise AssertionError("intrinsic hex metric report certificate hash mismatch")

    variants = family.get("variants", [])
    if len(variants) != 5:
        raise AssertionError("expected five natural lift variants")
    ratios = [float(row["covariance"]["anisotropy_ratio"]) for row in variants]
    if not all(ratio > 1.0 for ratio in ratios):
        raise AssertionError("not all lift variants are anisotropic")

    summary = family.get("survival_summary", {})
    if summary.get("variants_tested") != 5:
        raise AssertionError("family summary variant count mismatch")
    if summary.get("anisotropic_variant_count") != 5:
        raise AssertionError("family summary anisotropic count mismatch")
    if not _close(float(summary.get("anisotropy_ratio_min")), min(ratios)):
        raise AssertionError("family summary min mismatch")
    if not _close(float(summary.get("anisotropy_ratio_median")), _median(ratios)):
        raise AssertionError("family summary median mismatch")
    if not _close(float(summary.get("anisotropy_ratio_max")), max(ratios)):
        raise AssertionError("family summary max mismatch")

    ranking = family.get("ranking_by_anisotropy_desc", [])
    if [row.get("rank") for row in ranking] != [1, 2, 3, 4, 5]:
        raise AssertionError("family ranking is not complete")
    if ranking[0].get("id") != "cooriented_sign_selector":
        raise AssertionError("cooriented selector lift is not the strongest tested lift")
    if ranking[-1].get("id") != "regular_hex_label_delta":
        raise AssertionError("regular hex label-delta lift is not the weakest tested lift")

    witness = report.get("witness", {})
    if witness.get("variants_tested") != summary.get("variants_tested"):
        raise AssertionError("report witness variant count mismatch")
    if witness.get("anisotropic_variant_count") != summary.get("anisotropic_variant_count"):
        raise AssertionError("report witness anisotropic count mismatch")
    if not _close(float(witness.get("anisotropy_ratio_min")), float(summary.get("anisotropy_ratio_min"))):
        raise AssertionError("report witness min mismatch")
    if not _close(float(witness.get("anisotropy_ratio_median")), float(summary.get("anisotropy_ratio_median"))):
        raise AssertionError("report witness median mismatch")
    if not _close(float(witness.get("anisotropy_ratio_max")), float(summary.get("anisotropy_ratio_max"))):
        raise AssertionError("report witness max mismatch")

    witnessed = {row.get("id"): row for row in report.get("witnessed_obligations", [])}
    for obligation_id in ("intrinsic_lift_family_definition", "canonical_metric_selection"):
        row = witnessed.get(obligation_id)
        if row is None or row.get("status") != "witnessed":
            raise AssertionError(f"{obligation_id} was not witnessed")
        if row.get("witness_report") != INTRINSIC_REPORT_REL:
            raise AssertionError(f"{obligation_id} witness report mismatch")
        if row.get("witness_sha256") != intrinsic_report.get("certificate_sha256"):
            raise AssertionError(f"{obligation_id} witness hash mismatch")

    if status == "D20_VOLTAGE_LIFT_FAMILY_ROBUST_OBLONGNESS_NEEDS_REVIEW":
        open_obligations = report.get("open_obligations", [])
        if [row.get("id") for row in open_obligations] != ["proof_layer_integration"]:
            raise AssertionError("unexpected remaining open proof obligations")
        if any(row.get("status") != "open" for row in open_obligations):
            raise AssertionError("open proof obligation is not marked open")
    else:
        if report.get("open_obligations") != []:
            raise AssertionError("certified proof obligation still has open obligations")
        if theorem_report is None:
            raise AssertionError("robust oblongness theorem report missing")
        if theorem_report.get("status") != "D20_VOLTAGE_LIFT_ROBUST_OBLONGNESS_CERTIFIED":
            raise AssertionError("robust oblongness theorem status mismatch")
        proof_layer = witnessed.get("proof_layer_integration")
        if proof_layer is None or proof_layer.get("status") != "witnessed":
            raise AssertionError("proof-layer integration was not witnessed")
        if proof_layer.get("witness_report") != ROBUST_THEOREM_REPORT_REL:
            raise AssertionError("proof-layer integration witness report mismatch")
        if proof_layer.get("witness_sha256") != theorem_report.get("certificate_sha256"):
            raise AssertionError("proof-layer integration witness hash mismatch")
        theorem_input = report.get("inputs", {}).get("robust_oblongness_theorem_report", {})
        if theorem_input.get("path") != ROBUST_THEOREM_REPORT_REL:
            raise AssertionError("robust oblongness theorem input missing")
        if theorem_input.get("certificate_sha256") != theorem_report.get("certificate_sha256"):
            raise AssertionError("robust oblongness theorem input hash mismatch")

    obligations = index.get("obligations", [])
    entry = next((row for row in obligations if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("proof obligation index entry missing")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("proof obligation index report hash mismatch")
    if _self_hash(index, "registry_sha256") != index.get("registry_sha256"):
        raise AssertionError("proof obligation registry self hash mismatch")

    return report


if __name__ == "__main__":
    validate_d20_voltage_lift_family_robust_oblongness()
    print("D20 voltage lift family robust oblongness proof obligation validated")
