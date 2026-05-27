from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_pentagon_chain_normal_form import (
        ASSOCIATOR_REPORT,
        DUALITY_REPORT,
        FUSION_REPORT,
        FUSION_TENSOR_NPZ,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_REPORT,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        TRIANGLE_REPORT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_pentagon_chain_normal_form import (
        ASSOCIATOR_REPORT,
        DUALITY_REPORT,
        FUSION_REPORT,
        FUSION_TENSOR_NPZ,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_REPORT,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        TRIANGLE_REPORT,
        build_payloads,
        self_hash,
    )


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')} != {expected_rel}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_c985_pentagon_chain_normal_form() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    normal_form = load_json(OUT_DIR / "pentagon_normal_form.json")
    pentagon_certificate = load_json(OUT_DIR / "pentagon_certificate.json")
    sample_rows = np.load(OUT_DIR / "pentagon_sample_chains.npz", allow_pickle=False)["rows"]
    index = load_json(INDEX_PATH)

    if normal_form != expected["pentagon_normal_form"]:
        raise AssertionError("pentagon_normal_form.json is not reproducible")
    if pentagon_certificate != expected["pentagon_certificate"]:
        raise AssertionError("pentagon_certificate.json is not reproducible")
    if not np.array_equal(sample_rows, expected["pentagon_sample_chains"]):
        raise AssertionError("pentagon_sample_chains.npz is not reproducible")

    if report.get("schema") != "c985.proof_obligation.pentagon_chain_normal_form@1":
        raise AssertionError("C985 pentagon report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 pentagon normal form is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 pentagon all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 pentagon report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 pentagon report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 pentagon report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_registry_certified",
        "fusion_multiplicity_typing_certified",
        "associator_oracle_certified",
        "unit_triangle_coherence_certified",
        "duality_support_certified",
        "all_parenthesization_counts_match_exact_chain_count",
        "exact_chain_count_is_985_times_2576_cubed",
        "all_edges_preserve_chain_normal_form",
        "top_and_bottom_paths_have_same_normal_form",
        "sample_chain_typing_failures_are_zero",
        "sample_count_is_256",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 pentagon missing true checks: {missing}")

    witness = report.get("witness", {})
    address_counts = witness.get("address_counts", {})
    parenthesization_counts = address_counts.get("parenthesization_counts", {})
    exact = 16837352591360
    if address_counts.get("exact_length_four_chain_count") != exact:
        raise AssertionError("pentagon exact chain count mismatch")
    if any(count != exact for count in parenthesization_counts.values()):
        raise AssertionError("pentagon parenthesization count mismatch")
    if witness.get("chain_normal_form") != "typed_length_four_chain(x0,x1,x2,x3,x4)":
        raise AssertionError("pentagon chain normal form mismatch")
    if sample_rows.shape != (256, 16):
        raise AssertionError("pentagon sample row shape mismatch")
    if sample_rows.dtype != np.int32:
        raise AssertionError("pentagon sample row dtype mismatch")
    if "pentagon coherence" in report.get("closure_boundary", {}).get("does_not_certify", []):
        raise AssertionError("pentagon certificate still lists pentagon coherence as open")
    if "full finite semisimple multi-fusion category status" not in report.get(
        "closure_boundary", {}
    ).get("does_not_certify", []):
        raise AssertionError("pentagon certificate no longer records open multi-fusion status")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report input")
    assert_file_hash(inputs.get("associator_report", {}), ASSOCIATOR_REPORT, "associator report input")
    assert_file_hash(inputs.get("triangle_report", {}), TRIANGLE_REPORT, "triangle report input")
    assert_file_hash(inputs.get("duality_report", {}), DUALITY_REPORT, "duality report input")
    assert_file_hash(inputs.get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(inputs.get("fusion_tensor", {}), FUSION_TENSOR_NPZ, "fusion tensor input")

    if manifest.get("schema") != "c985.proof_obligation.pentagon_chain_normal_form_manifest@1":
        raise AssertionError("C985 pentagon manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 pentagon manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 pentagon manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 pentagon missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 pentagon index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 pentagon index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.pentagon_chain_normal_form@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "exact_length_four_chain_count": address_counts.get("exact_length_four_chain_count"),
        "parenthesization_counts": parenthesization_counts,
        "sample_count": witness.get("sample_summary", {}).get("sample_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_pentagon_chain_normal_form()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
