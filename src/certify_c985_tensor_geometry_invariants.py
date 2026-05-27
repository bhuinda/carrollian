from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_tensor_geometry_invariants import (
        FINAL_REPORT,
        FUSION_REPORT,
        FUSION_TENSOR,
        INDEX_PATH,
        ORBITALS,
        OUT_DIR,
        REGISTRY_REPORT,
        SOURCE_TARGET,
        STATUS,
        THEOREM_ID,
        TRANSPOSE,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_tensor_geometry_invariants import (
        FINAL_REPORT,
        FUSION_REPORT,
        FUSION_TENSOR,
        INDEX_PATH,
        ORBITALS,
        OUT_DIR,
        REGISTRY_REPORT,
        SOURCE_TARGET,
        STATUS,
        THEOREM_ID,
        TRANSPOSE,
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


def validate_c985_tensor_geometry_invariants() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    summary = load_json(OUT_DIR / "tensor_geometry_summary.json")
    geometry_certificate = load_json(OUT_DIR / "geometry_certificate.json")
    index = load_json(INDEX_PATH)

    cubes = np.load(OUT_DIR / "object_sector_cubes.npz", allow_pickle=False)
    support_cube = np.asarray(cubes["support_cube"], dtype=np.int64)
    coefficient_cube = np.asarray(cubes["coefficient_cube"], dtype=np.int64)
    signatures = np.load(OUT_DIR / "relation_geometry_signatures.npz", allow_pickle=False)
    relation_records = np.asarray(signatures["relation_records"], dtype=np.int64)
    signature_matrix = np.asarray(signatures["signature_matrix"], dtype=np.int64)

    if not np.array_equal(support_cube, expected["object_support_cube"]):
        raise AssertionError("object support cube is not reproducible")
    if not np.array_equal(coefficient_cube, expected["object_coefficient_cube"]):
        raise AssertionError("object coefficient cube is not reproducible")
    if not np.array_equal(relation_records, expected["relation_geometry_records"]):
        raise AssertionError("relation geometry records are not reproducible")
    if not np.array_equal(signature_matrix, expected["relation_signature_matrix"]):
        raise AssertionError("relation signature matrix is not reproducible")
    if summary != expected["tensor_geometry_summary"]:
        raise AssertionError("tensor geometry summary is not reproducible")
    if geometry_certificate != expected["geometry_certificate"]:
        raise AssertionError("geometry certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.tensor_geometry_invariants@1":
        raise AssertionError("C985 tensor geometry report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 tensor geometry invariants are not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 tensor geometry all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 tensor geometry checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 tensor geometry report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 tensor geometry report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "registry_certified",
        "fusion_certified",
        "final_c985_certificate_present",
        "source_target_shape_is_985_by_2",
        "fusion_tensor_shape_is_1414965_by_4",
        "fusion_coefficient_total_is_2537360",
        "object_sector_support_cube_has_all_216_cells",
        "support_cube_sum_matches_tensor_support",
        "coefficient_cube_sum_matches_tensor_mass",
        "relation_geometry_records_shape_is_985_by_12",
        "every_output_relation_has_point_mass_2576",
        "transpose_symmetry_failure_count_is_zero",
        "transpose_preserves_relation_size",
        "left_support_matches_right_support_under_transpose",
        "left_mass_matches_right_mass_under_transpose",
        "output_support_matches_transpose_output_support",
        "histogram_support_total_matches_tensor_support",
        "histogram_mass_total_matches_tensor_mass",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 tensor geometry missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("tensor_support") != 1414965:
        raise AssertionError("C985 tensor support mismatch")
    if witness.get("coefficient_total") != 2537360:
        raise AssertionError("C985 coefficient total mismatch")
    if witness.get("object_sector_nonzero_cells") != 216:
        raise AssertionError("C985 object-sector cube is not fully populated")
    if witness.get("output_coefficient_mass_min") != 2576:
        raise AssertionError("C985 output mass minimum mismatch")
    if witness.get("output_coefficient_mass_max") != 2576:
        raise AssertionError("C985 output mass maximum mismatch")
    if witness.get("transpose_symmetry_failure_count") != 0:
        raise AssertionError("C985 transpose symmetry failures present")
    if support_cube.shape != (6, 6, 6):
        raise AssertionError("object support cube shape mismatch")
    if coefficient_cube.shape != (6, 6, 6):
        raise AssertionError("object coefficient cube shape mismatch")
    if relation_records.shape != (985, 12):
        raise AssertionError("relation geometry record shape mismatch")
    if int(relation_records[:, 11].min()) != 2576 or int(relation_records[:, 11].max()) != 2576:
        raise AssertionError("relation output mass is not constant 2576")
    if int(support_cube.sum()) != 1414965:
        raise AssertionError("object support cube total mismatch")
    if int(coefficient_cube.sum()) != 2537360:
        raise AssertionError("object coefficient cube total mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report input")
    assert_file_hash(inputs.get("final_c985_report", {}), FINAL_REPORT, "final report input")
    assert_file_hash(inputs.get("source_target", {}), SOURCE_TARGET, "source target input")
    assert_file_hash(inputs.get("transpose", {}), TRANSPOSE, "transpose input")
    assert_file_hash(inputs.get("orbitals", {}), ORBITALS, "orbitals input")
    assert_file_hash(inputs.get("fusion_tensor", {}), FUSION_TENSOR, "fusion tensor input")

    if manifest.get("schema") != "c985.proof_obligation.tensor_geometry_invariants_manifest@1":
        raise AssertionError("C985 tensor geometry manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 tensor geometry manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 tensor geometry manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 tensor geometry obligation missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 tensor geometry index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 tensor geometry index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.tensor_geometry_invariants@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "tensor_support": witness.get("tensor_support"),
        "coefficient_total": witness.get("coefficient_total"),
        "object_sector_nonzero_cells": witness.get("object_sector_nonzero_cells"),
        "output_coefficient_mass": witness.get("output_coefficient_mass_min"),
        "coefficient_max": witness.get("coefficient_max"),
        "unique_relation_signature_count": witness.get("unique_relation_signature_count"),
        "transpose_symmetry_failure_count": witness.get("transpose_symmetry_failure_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_tensor_geometry_invariants()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
