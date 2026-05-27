from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_duality_support import (
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        REGISTRY_TRANSPOSE,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        TRIANGLE_REPORT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_duality_support import (
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        REGISTRY_TRANSPOSE,
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


def validate_c985_duality_support() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    duality_table = load_json(OUT_DIR / "duality_support_table.json")
    duality_certificate = load_json(OUT_DIR / "duality_certificate.json")
    index = load_json(INDEX_PATH)
    records = np.load(OUT_DIR / "duality_support_records.npz", allow_pickle=False)["records"]

    if not np.array_equal(records, expected["duality_support_records"]):
        raise AssertionError("duality_support_records.npz is not reproducible")
    if duality_table != expected["duality_support_table"]:
        raise AssertionError("duality_support_table.json is not reproducible")
    if duality_certificate != expected["duality_certificate"]:
        raise AssertionError("duality_certificate.json is not reproducible")

    if report.get("schema") != "c985.proof_obligation.duality_support@1":
        raise AssertionError("C985 duality support report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 duality support is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 duality support all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 duality support report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 duality support report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 duality support report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_registry_certified",
        "fusion_multiplicity_typing_certified",
        "unit_triangle_coherence_certified",
        "duality_record_count_is_985",
        "transpose_is_involution",
        "transpose_flips_all_source_targets",
        "identity_orbitals_are_self_dual",
        "evaluation_spaces_are_nonzero",
        "coevaluation_spaces_are_nonzero",
        "duality_failures_are_zero",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 duality support missing true checks: {missing}")

    witness = report.get("witness", {})
    summary = witness.get("duality_summary", {})
    if witness.get("relation_count") != 985:
        raise AssertionError("duality relation count mismatch")
    if witness.get("identity_relations") != [6, 163, 227, 349, 618, 893]:
        raise AssertionError("duality identity relations mismatch")
    if summary.get("duality_failure_count") != 0:
        raise AssertionError("duality support failures present")
    if int(summary.get("eval_dim_min", 0)) <= 0 or int(summary.get("coeval_dim_min", 0)) <= 0:
        raise AssertionError("duality support has zero-dimensional eval/coeval space")
    if records.shape != (985, 10):
        raise AssertionError("duality support record shape mismatch")
    if records.dtype != np.int32:
        raise AssertionError("duality support record dtype mismatch")
    if not np.array_equal(records[:, 0], np.arange(985, dtype=np.int32)):
        raise AssertionError("duality records are not alpha ordered")
    if "full finite semisimple multi-fusion category status" not in report.get(
        "closure_boundary", {}
    ).get("does_not_certify", []):
        raise AssertionError("duality certificate no longer records open multi-fusion status")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report input")
    assert_file_hash(inputs.get("triangle_report", {}), TRIANGLE_REPORT, "triangle report input")
    assert_file_hash(inputs.get("source_target", {}), REGISTRY_SOURCE_TARGET, "source target input")
    assert_file_hash(inputs.get("transpose", {}), REGISTRY_TRANSPOSE, "transpose input")
    assert_file_hash(inputs.get("identity_orbitals", {}), REGISTRY_IDENTITIES, "identity input")
    assert_file_hash(inputs.get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(inputs.get("fusion_basis_points", {}), FUSION_BASIS_NPZ, "fusion basis input")
    assert_file_hash(inputs.get("fusion_basis_index", {}), FUSION_INDEX_NPZ, "fusion index input")

    if manifest.get("schema") != "c985.proof_obligation.duality_support_manifest@1":
        raise AssertionError("C985 duality support manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 duality support manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 duality support manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 duality support missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 duality support index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 duality support index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.duality_support@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "relation_count": witness.get("relation_count"),
        "eval_dim_min": summary.get("eval_dim_min"),
        "coeval_dim_min": summary.get("coeval_dim_min"),
        "duality_failures": summary.get("duality_failure_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_duality_support()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
