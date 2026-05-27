from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_unit_tensor_laws import (
        ASSOCIATOR_REPORT,
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        FUSION_TENSOR_NPZ,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_unit_tensor_laws import (
        ASSOCIATOR_REPORT,
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        FUSION_TENSOR_NPZ,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
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


def validate_c985_unit_tensor_laws() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    unit_table = load_json(OUT_DIR / "unit_action_table.json")
    unit_certificate = load_json(OUT_DIR / "unit_certificate.json")
    index = load_json(INDEX_PATH)
    records = np.load(OUT_DIR / "unit_action_records.npz", allow_pickle=False)["records"]

    if not np.array_equal(records, expected["unit_action_records"]):
        raise AssertionError("unit_action_records.npz is not reproducible")
    if unit_table != expected["unit_action_table"]:
        raise AssertionError("unit_action_table.json is not reproducible")
    if unit_certificate != expected["unit_certificate"]:
        raise AssertionError("unit_certificate.json is not reproducible")

    if report.get("schema") != "c985.proof_obligation.unit_tensor_laws@1":
        raise AssertionError("C985 unit tensor laws report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 unit tensor laws are not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 unit tensor laws all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 unit tensor laws report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 unit tensor laws report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 unit tensor laws report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_registry_certified",
        "fusion_multiplicity_typing_certified",
        "associator_oracle_certified",
        "identity_relation_count_is_6",
        "unit_record_count_is_985",
        "left_unit_failures_are_zero",
        "wrong_unit_products_are_zero",
        "left_unit_basis_points_are_source_endpoints",
        "right_unit_basis_points_are_target_endpoints",
        "unit_action_records_are_integral",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 unit tensor laws missing true checks: {missing}")

    witness = report.get("witness", {})
    unit_summary = witness.get("unit_summary", {})
    if witness.get("relation_count") != 985:
        raise AssertionError("unit relation count mismatch")
    if witness.get("identity_relations") != [6, 163, 227, 349, 618, 893]:
        raise AssertionError("unit identity relations mismatch")
    if unit_summary.get("unit_failure_count") != 0:
        raise AssertionError("unit failures present")
    if unit_summary.get("wrong_unit_nonzero_count") != 0:
        raise AssertionError("wrong unit products present")
    if records.shape != (985, 7):
        raise AssertionError("unit action record shape mismatch")
    if records.dtype != np.int32:
        raise AssertionError("unit action record dtype mismatch")
    if not np.array_equal(records[:, 0], np.arange(985, dtype=np.int32)):
        raise AssertionError("unit action records are not alpha-ordered")
    if "full finite semisimple multi-fusion category status" not in report.get(
        "closure_boundary", {}
    ).get("does_not_certify", []):
        raise AssertionError("unit certificate no longer records open multi-fusion status")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(inputs.get("source_target", {}), REGISTRY_SOURCE_TARGET, "source target input")
    assert_file_hash(inputs.get("identity_orbitals", {}), REGISTRY_IDENTITIES, "identity input")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report input")
    assert_file_hash(inputs.get("associator_report", {}), ASSOCIATOR_REPORT, "associator report input")
    assert_file_hash(inputs.get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(inputs.get("fusion_tensor", {}), FUSION_TENSOR_NPZ, "fusion tensor input")
    assert_file_hash(inputs.get("fusion_basis_points", {}), FUSION_BASIS_NPZ, "fusion basis input")
    assert_file_hash(inputs.get("fusion_basis_index", {}), FUSION_INDEX_NPZ, "fusion index input")

    if manifest.get("schema") != "c985.proof_obligation.unit_tensor_laws_manifest@1":
        raise AssertionError("C985 unit tensor laws manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 unit tensor laws manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 unit tensor laws manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 unit tensor laws missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 unit tensor laws index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 unit tensor laws index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.unit_tensor_laws@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "relation_count": witness.get("relation_count"),
        "identity_relations": witness.get("identity_relations"),
        "unit_failure_count": unit_summary.get("unit_failure_count"),
        "wrong_unit_nonzero_count": unit_summary.get("wrong_unit_nonzero_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_unit_tensor_laws()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
