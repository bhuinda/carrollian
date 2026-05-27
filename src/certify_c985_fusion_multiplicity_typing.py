from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_fusion_multiplicity_typing import (
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_REPORT,
        SOURCE_RELATION_NPZ,
        SOURCE_TENSOR_NPZ,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_fusion_multiplicity_typing import (
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_REPORT,
        SOURCE_RELATION_NPZ,
        SOURCE_TENSOR_NPZ,
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


def validate_c985_fusion_multiplicity_typing() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    fusion_typing = load_json(OUT_DIR / "fusion_typing_certificate.json")
    basis_index_json = load_json(OUT_DIR / "multiplicity_basis_index.json")
    index = load_json(INDEX_PATH)

    fusion_tensor = np.load(OUT_DIR / "fusion_tensor_coo.npz", allow_pickle=False)["triples"]
    basis_points = np.load(OUT_DIR / "multiplicity_basis_points.npz", allow_pickle=False)["basis_records"]
    basis_index = np.load(OUT_DIR / "multiplicity_basis_index.npz", allow_pickle=False)["index_records"]

    if not np.array_equal(fusion_tensor, expected["fusion_tensor_coo"]):
        raise AssertionError("fusion_tensor_coo.npz is not reproducible")
    if not np.array_equal(basis_points, expected["multiplicity_basis_points"]):
        raise AssertionError("multiplicity_basis_points.npz is not reproducible")
    if not np.array_equal(basis_index, expected["multiplicity_basis_index_array"]):
        raise AssertionError("multiplicity_basis_index.npz is not reproducible")
    if fusion_typing != expected["fusion_typing_certificate"]:
        raise AssertionError("fusion_typing_certificate.json is not reproducible")
    if basis_index_json != expected["multiplicity_basis_index"]:
        raise AssertionError("multiplicity_basis_index.json is not reproducible")

    if report.get("schema") != "c985.proof_obligation.fusion_multiplicity_typing@1":
        raise AssertionError("C985 fusion multiplicity report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 fusion multiplicity typing is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 fusion multiplicity all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 fusion multiplicity report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 fusion multiplicity report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 fusion multiplicity report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_registry_certified",
        "source_tensor_exists",
        "source_tensor_support_is_1414965",
        "derived_tensor_support_is_1414965",
        "derived_tensor_matches_source_tensor",
        "basis_row_count_matches_coefficient_total",
        "basis_index_row_count_matches_tensor_support",
        "basis_index_counts_sum_to_basis_rows",
        "all_fusion_coefficients_positive_on_support",
        "all_fusion_coefficients_integral",
        "fusion_typing_failure_count_is_zero",
        "source_tensor_matrix_matches_registry",
        "source_target_shape_is_985_by_2",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 fusion multiplicity missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("tensor_support") != 1414965:
        raise AssertionError("C985 tensor support mismatch")
    if witness.get("coefficient_total") != 2537360:
        raise AssertionError("C985 coefficient total mismatch")
    if witness.get("basis_row_count") != 2537360:
        raise AssertionError("C985 multiplicity basis row count mismatch")
    if witness.get("typing_failure_count") != 0:
        raise AssertionError("C985 fusion typing failures present")
    if fusion_tensor.shape != (1414965, 4):
        raise AssertionError("fusion tensor shape mismatch")
    if basis_points.shape != (2537360, 4):
        raise AssertionError("multiplicity basis shape mismatch")
    if basis_index.shape != (1414965, 5):
        raise AssertionError("multiplicity basis index shape mismatch")
    if int(fusion_tensor[:, 3].sum()) != int(basis_index[:, 4].sum()):
        raise AssertionError("fusion coefficient total does not match basis index count total")
    if not np.array_equal(fusion_tensor[:, :3].astype(np.int64), basis_index[:, :3]):
        raise AssertionError("fusion tensor keys do not match basis index keys")
    if not np.array_equal(fusion_tensor[:, 3].astype(np.int64), basis_index[:, 4]):
        raise AssertionError("fusion tensor coefficients do not match basis index counts")
    if "full finite semisimple multi-fusion category status" not in report.get(
        "closure_boundary", {}
    ).get("does_not_certify", []):
        raise AssertionError("fusion certificate no longer records open multi-fusion status")

    assert_file_hash(report.get("inputs", {}).get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(report.get("inputs", {}).get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(report.get("inputs", {}).get("source_tensor", {}), SOURCE_TENSOR_NPZ, "source tensor input")

    if manifest.get("schema") != "c985.proof_obligation.fusion_multiplicity_typing_manifest@1":
        raise AssertionError("C985 fusion multiplicity manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 fusion multiplicity manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 fusion multiplicity manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 fusion multiplicity missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 fusion multiplicity index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 fusion multiplicity index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.fusion_multiplicity_typing@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "tensor_support": witness.get("tensor_support"),
        "coefficient_total": witness.get("coefficient_total"),
        "basis_row_count": witness.get("basis_row_count"),
        "typing_failure_count": witness.get("typing_failure_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_fusion_multiplicity_typing()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
