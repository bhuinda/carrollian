from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_associator_rebracketing_oracle import (
        ACTION_NPZ,
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        FUSION_TENSOR_NPZ,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_REPORT,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_associator_rebracketing_oracle import (
        ACTION_NPZ,
        FUSION_BASIS_NPZ,
        FUSION_INDEX_NPZ,
        FUSION_REPORT,
        FUSION_TENSOR_NPZ,
        INDEX_PATH,
        OUT_DIR,
        REGISTRY_REPORT,
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


def validate_c985_associator_rebracketing_oracle() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    oracle = load_json(OUT_DIR / "associator_oracle.json")
    associator_certificate = load_json(OUT_DIR / "associator_certificate.json")
    index = load_json(INDEX_PATH)
    section = np.load(OUT_DIR / "pair_transport_section.npz", allow_pickle=False)[
        "pair_transport_group_index"
    ]
    sample_npz = np.load(OUT_DIR / "associator_sample_witnesses.npz", allow_pickle=False)
    samples = {key: np.asarray(sample_npz[key]) for key in sample_npz.files}

    if not np.array_equal(section, expected["pair_transport_section"]):
        raise AssertionError("pair_transport_section.npz is not reproducible")
    for key, expected_array in expected["associator_sample_witnesses"].items():
        if key not in samples:
            raise AssertionError(f"associator sample witness missing array: {key}")
        if not np.array_equal(samples[key], expected_array):
            raise AssertionError(f"associator sample witness array is not reproducible: {key}")
    if oracle != expected["associator_oracle"]:
        raise AssertionError("associator_oracle.json is not reproducible")
    if associator_certificate != expected["associator_certificate"]:
        raise AssertionError("associator_certificate.json is not reproducible")

    if report.get("schema") != "c985.proof_obligation.associator_rebracketing_oracle@1":
        raise AssertionError("C985 associator oracle report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 associator oracle is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 associator oracle all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 associator oracle report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 associator oracle report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 associator oracle report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_registry_certified",
        "fusion_multiplicity_typing_certified",
        "action_shape_is_9216_by_2576",
        "transport_section_covers_all_ordered_pairs",
        "transport_orbits_match_all_985_relations",
        "transport_sends_representatives_to_every_ordered_pair",
        "left_and_right_support_address_counts_match",
        "left_and_right_multiplicity_basis_counts_match",
        "known_full_left_support_address_rows_match",
        "known_full_associator_basis_vectors_match",
        "sample_rebracketing_failures_are_zero",
        "sample_rebracketing_count_is_1970",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 associator oracle missing true checks: {missing}")

    witness = report.get("witness", {})
    address_counts = witness.get("address_counts", {})
    sample_summary = witness.get("sample_summary", {})
    transport_summary = witness.get("transport_section_summary", {})
    transport_verification = witness.get("transport_section_verification", {})
    if address_counts.get("left_multiplicity_basis_vectors") != 6536239360:
        raise AssertionError("left associator basis vector count mismatch")
    if address_counts.get("right_multiplicity_basis_vectors") != 6536239360:
        raise AssertionError("right associator basis vector count mismatch")
    if address_counts.get("left_support_address_rows") != 2367375223:
        raise AssertionError("left associator support row count mismatch")
    if address_counts.get("right_support_address_rows") != 2367375223:
        raise AssertionError("right associator support row count mismatch")
    if transport_summary.get("transport_section_unfilled_pairs") != 0:
        raise AssertionError("transport section has unfilled ordered pairs")
    if transport_summary.get("orbit_mismatch_count") != 0:
        raise AssertionError("transport orbit mismatch present")
    if transport_verification.get("checked_ordered_pairs") != 2576 * 2576:
        raise AssertionError("transport verification did not cover all ordered pairs")
    if transport_verification.get("transport_failures") != 0:
        raise AssertionError("transport verification failures present")
    if sample_summary.get("sample_count") != 1970:
        raise AssertionError("associator sample count mismatch")
    if sample_summary.get("sample_failure_count") != 0:
        raise AssertionError("associator sample failures present")
    if section.shape != (2576 * 2576,):
        raise AssertionError("transport section shape mismatch")
    if int(section.min()) < 0 or int(section.max()) >= 9216:
        raise AssertionError("transport section group index range mismatch")
    if samples["left_records"].shape != (1970, 7):
        raise AssertionError("left sample shape mismatch")
    if samples["chain_records"].shape != (1970, 4):
        raise AssertionError("chain sample shape mismatch")
    if samples["right_records"].shape != (1970, 7):
        raise AssertionError("right sample shape mismatch")
    if samples["transport_groups"].shape != (1970, 2):
        raise AssertionError("transport group sample shape mismatch")
    if "full finite semisimple multi-fusion category status" not in report.get(
        "closure_boundary", {}
    ).get("does_not_certify", []):
        raise AssertionError("associator certificate no longer records open multi-fusion status")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("typed_registry_report", {}), REGISTRY_REPORT, "registry report input")
    assert_file_hash(inputs.get("fusion_report", {}), FUSION_REPORT, "fusion report input")
    assert_file_hash(inputs.get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(inputs.get("be3_action", {}), ACTION_NPZ, "Be3 action input")
    assert_file_hash(inputs.get("fusion_basis_points", {}), FUSION_BASIS_NPZ, "fusion basis input")
    assert_file_hash(inputs.get("fusion_basis_index", {}), FUSION_INDEX_NPZ, "fusion index input")
    assert_file_hash(inputs.get("fusion_tensor", {}), FUSION_TENSOR_NPZ, "fusion tensor input")

    if manifest.get("schema") != "c985.proof_obligation.associator_rebracketing_oracle_manifest@1":
        raise AssertionError("C985 associator oracle manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 associator oracle manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 associator oracle manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 associator oracle missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 associator oracle index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 associator oracle index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.associator_rebracketing_oracle@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "left_associator_basis_vectors": address_counts.get("left_multiplicity_basis_vectors"),
        "right_associator_basis_vectors": address_counts.get("right_multiplicity_basis_vectors"),
        "support_address_rows": address_counts.get("left_support_address_rows"),
        "transport_checked_ordered_pairs": transport_verification.get("checked_ordered_pairs"),
        "sample_count": sample_summary.get("sample_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_associator_rebracketing_oracle()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
