from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_unit_triangle_coherence import (
        ACTION_NPZ,
        ASSOCIATOR_REPORT,
        FUSION_BASIS_NPZ,
        FUSION_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PAIR_TRANSPORT_NPZ,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        UNIT_RECORDS_NPZ,
        UNIT_REPORT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_unit_triangle_coherence import (
        ACTION_NPZ,
        ASSOCIATOR_REPORT,
        FUSION_BASIS_NPZ,
        FUSION_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PAIR_TRANSPORT_NPZ,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        UNIT_RECORDS_NPZ,
        UNIT_REPORT,
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


def validate_c985_unit_triangle_coherence() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    triangle_certificate = load_json(OUT_DIR / "triangle_certificate.json")
    index = load_json(INDEX_PATH)
    witness_npz = np.load(OUT_DIR / "unit_triangle_witness.npz", allow_pickle=False)
    witness_arrays = {key: np.asarray(witness_npz[key]) for key in witness_npz.files}

    for key, expected_array in expected["unit_triangle_witness"].items():
        if key not in witness_arrays:
            raise AssertionError(f"unit triangle witness missing array: {key}")
        if not np.array_equal(witness_arrays[key], expected_array):
            raise AssertionError(f"unit triangle witness array is not reproducible: {key}")
    if triangle_certificate != expected["triangle_certificate"]:
        raise AssertionError("triangle_certificate.json is not reproducible")

    if report.get("schema") != "c985.proof_obligation.unit_triangle_coherence@1":
        raise AssertionError("C985 unit triangle report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 unit triangle coherence is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 unit triangle all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 unit triangle report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 unit triangle report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 unit triangle report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_registry_certified",
        "fusion_multiplicity_typing_certified",
        "associator_oracle_certified",
        "unit_tensor_laws_certified",
        "all_fusion_basis_rows_checked",
        "middle_object_mismatches_are_zero",
        "unit_record_mismatches_are_zero",
        "unit_basis_mismatches_are_zero",
        "basis_typing_mismatches_are_zero",
        "transport_failures_are_zero",
        "triangle_failures_are_zero",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 unit triangle missing true checks: {missing}")

    witness = report.get("witness", {})
    check_counts = witness.get("check_counts", {})
    if witness.get("basis_rows_checked") != 2537360:
        raise AssertionError("unit triangle basis row count mismatch")
    if witness.get("identity_relations") != [6, 163, 227, 349, 618, 893]:
        raise AssertionError("unit triangle identity relations mismatch")
    expected_zero_counts = {
        "middle_object_mismatches",
        "right_unit_record_mismatches",
        "left_unit_record_mismatches",
        "right_unit_basis_mismatches",
        "left_unit_basis_mismatches",
        "basis_typing_mismatches",
        "left_transport_failures",
        "right_transport_failures",
        "triangle_failures",
    }
    nonzero = sorted(key for key in expected_zero_counts if int(check_counts.get(key, -1)) != 0)
    if nonzero:
        raise AssertionError(f"unit triangle nonzero failure counts: {nonzero}")
    if witness_arrays["transport_groups"].shape != (2537360, 2):
        raise AssertionError("unit triangle transport group shape mismatch")
    if witness_arrays["failure_indices"].shape != (0,):
        raise AssertionError("unit triangle failure index array is not empty")
    if witness_arrays["sample_records"].shape[1] != 8:
        raise AssertionError("unit triangle sample record column count mismatch")
    if "full finite semisimple multi-fusion category status" not in report.get(
        "closure_boundary", {}
    ).get("does_not_certify", []):
        raise AssertionError("triangle certificate no longer records open multi-fusion status")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report input")
    assert_file_hash(inputs.get("associator_report", {}), ASSOCIATOR_REPORT, "associator report input")
    assert_file_hash(inputs.get("unit_report", {}), UNIT_REPORT, "unit report input")
    assert_file_hash(inputs.get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(inputs.get("source_target", {}), REGISTRY_SOURCE_TARGET, "source target input")
    assert_file_hash(inputs.get("identity_orbitals", {}), REGISTRY_IDENTITIES, "identity input")
    assert_file_hash(inputs.get("fusion_basis_points", {}), FUSION_BASIS_NPZ, "fusion basis input")
    assert_file_hash(inputs.get("pair_transport_section", {}), PAIR_TRANSPORT_NPZ, "transport input")
    assert_file_hash(inputs.get("be3_action", {}), ACTION_NPZ, "Be3 action input")
    assert_file_hash(inputs.get("unit_action_records", {}), UNIT_RECORDS_NPZ, "unit records input")

    if manifest.get("schema") != "c985.proof_obligation.unit_triangle_coherence_manifest@1":
        raise AssertionError("C985 unit triangle manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 unit triangle manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 unit triangle manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 unit triangle missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 unit triangle index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 unit triangle index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.unit_triangle_coherence@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "basis_rows_checked": witness.get("basis_rows_checked"),
        "triangle_failures": check_counts.get("triangle_failures"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_unit_triangle_coherence()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
