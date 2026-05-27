from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_zigzag_identities import (
        ACTION_NPZ,
        ASSOCIATOR_REPORT,
        DUALITY_REPORT,
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PAIR_TRANSPORT_NPZ,
        PENTAGON_REPORT,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        REGISTRY_TRANSPOSE,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        TRIANGLE_REPORT,
        UNIT_RECORDS_NPZ,
        UNIT_REPORT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_zigzag_identities import (
        ACTION_NPZ,
        ASSOCIATOR_REPORT,
        DUALITY_REPORT,
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        INDEX_PATH,
        OUT_DIR,
        PAIR_TRANSPORT_NPZ,
        PENTAGON_REPORT,
        REGISTRY_IDENTITIES,
        REGISTRY_REPORT,
        REGISTRY_SOURCE_TARGET,
        REGISTRY_TRANSPOSE,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        TRIANGLE_REPORT,
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


def validate_c985_zigzag_identities() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    zigzag_certificate = load_json(OUT_DIR / "zigzag_certificate.json")
    coevaluation = np.load(OUT_DIR / "coevaluation_maps.npz", allow_pickle=False)["rows"]
    evaluation = np.load(OUT_DIR / "evaluation_maps.npz", allow_pickle=False)["rows"]
    counts_npz = np.load(OUT_DIR / "zigzag_counts.npz", allow_pickle=False)
    count_rows = counts_npz["count_rows"]
    summary_rows = counts_npz["summary_rows"]
    index = load_json(INDEX_PATH)

    if not np.array_equal(coevaluation, expected["coevaluation_maps"]):
        raise AssertionError("coevaluation_maps.npz is not reproducible")
    if not np.array_equal(evaluation, expected["evaluation_maps"]):
        raise AssertionError("evaluation_maps.npz is not reproducible")
    if not np.array_equal(count_rows, expected["zigzag_count_rows"]):
        raise AssertionError("zigzag count rows are not reproducible")
    if not np.array_equal(summary_rows, expected["zigzag_summary_rows"]):
        raise AssertionError("zigzag summary rows are not reproducible")
    if zigzag_certificate != expected["zigzag_certificate"]:
        raise AssertionError("zigzag_certificate.json is not reproducible")

    if report.get("schema") != "c985.proof_obligation.zigzag_identities@1":
        raise AssertionError("C985 zig-zag report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 zig-zag identities are not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 zig-zag all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 zig-zag report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 zig-zag report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 zig-zag report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_registry_certified",
        "fusion_multiplicity_typing_certified",
        "associator_oracle_certified",
        "unit_tensor_laws_certified",
        "unit_triangle_coherence_certified",
        "duality_support_certified",
        "pentagon_chain_normal_form_certified",
        "all_985_simples_checked",
        "zigzag_failures_are_zero",
        "coevaluation_terms_match_duality_support_total",
        "each_simple_has_evaluation_solution",
        "right_and_left_zigzag_counts_are_nonzero",
        "evaluation_coefficients_are_integral",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 zig-zag missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("simple_count") != 985:
        raise AssertionError("zig-zag simple count mismatch")
    if witness.get("zigzag_failure_count") != 0:
        raise AssertionError("zig-zag failures present")
    if witness.get("coevaluation_nonzero_terms") != 15456:
        raise AssertionError("coevaluation term count mismatch")
    if int(witness.get("solution_terms_min", 0)) <= 0:
        raise AssertionError("missing evaluation solution for some simple")
    if int(witness.get("max_denominator", 0)) != 1:
        raise AssertionError("evaluation coefficients are not integral")
    if coevaluation.shape != (15456, 4):
        raise AssertionError("coevaluation map shape mismatch")
    if evaluation.shape[1] != 4 or evaluation.shape[0] <= 0:
        raise AssertionError("evaluation map shape mismatch")
    if count_rows.shape[1] != 4 or count_rows.shape[0] <= 0:
        raise AssertionError("zig-zag count row shape mismatch")
    if summary_rows.shape != (985, 8):
        raise AssertionError("zig-zag summary row shape mismatch")
    if "zig-zag identities" in report.get("closure_boundary", {}).get("does_not_certify", []):
        raise AssertionError("zig-zag certificate still lists zig-zag identities as open")
    if "full finite semisimple multi-fusion category status" in report.get(
        "closure_boundary", {}
    ).get("does_not_certify", []):
        raise AssertionError("zig-zag certificate should leave final status to final checklist, not as an open zig-zag boundary")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report input")
    assert_file_hash(inputs.get("associator_report", {}), ASSOCIATOR_REPORT, "associator report input")
    assert_file_hash(inputs.get("unit_report", {}), UNIT_REPORT, "unit report input")
    assert_file_hash(inputs.get("triangle_report", {}), TRIANGLE_REPORT, "triangle report input")
    assert_file_hash(inputs.get("duality_report", {}), DUALITY_REPORT, "duality report input")
    assert_file_hash(inputs.get("pentagon_report", {}), PENTAGON_REPORT, "pentagon report input")
    assert_file_hash(inputs.get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(inputs.get("source_target", {}), REGISTRY_SOURCE_TARGET, "source target input")
    assert_file_hash(inputs.get("transpose", {}), REGISTRY_TRANSPOSE, "transpose input")
    assert_file_hash(inputs.get("identity_orbitals", {}), REGISTRY_IDENTITIES, "identity input")
    assert_file_hash(inputs.get("fusion_basis_points", {}), FUSION_BASIS_NPZ, "fusion basis input")
    assert_file_hash(inputs.get("fusion_basis_index", {}), FUSION_INDEX_NPZ, "fusion index input")
    assert_file_hash(inputs.get("pair_transport_section", {}), PAIR_TRANSPORT_NPZ, "transport input")
    assert_file_hash(inputs.get("unit_action_records", {}), UNIT_RECORDS_NPZ, "unit records input")
    assert_file_hash(inputs.get("be3_action", {}), ACTION_NPZ, "Be3 action input")

    if manifest.get("schema") != "c985.proof_obligation.zigzag_identities_manifest@1":
        raise AssertionError("C985 zig-zag manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 zig-zag manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 zig-zag manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 zig-zag missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 zig-zag index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 zig-zag index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.zigzag_identities@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "simple_count": witness.get("simple_count"),
        "zigzag_failures": witness.get("zigzag_failure_count"),
        "evaluation_nonzero_terms": witness.get("evaluation_nonzero_terms"),
        "coevaluation_nonzero_terms": witness.get("coevaluation_nonzero_terms"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_zigzag_identities()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
