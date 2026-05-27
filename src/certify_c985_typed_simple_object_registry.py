from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_typed_simple_object_registry import (
        CORE_A985_JSON,
        INDEX_PATH,
        OBJECT_LABELS,
        OUT_DIR,
        SOURCE_RELATION_NPZ,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_typed_simple_object_registry import (
        CORE_A985_JSON,
        INDEX_PATH,
        OBJECT_LABELS,
        OUT_DIR,
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


def validate_c985_typed_simple_object_registry() -> dict[str, Any]:
    expected = build_payloads()

    objects = load_json(OUT_DIR / "objects.json")
    orbitals = load_json(OUT_DIR / "orbitals.json")
    identity_orbitals = load_json(OUT_DIR / "identity_orbitals.json")
    semisimple = load_json(OUT_DIR / "semisimple_category_certificate.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    index = load_json(INDEX_PATH)
    source_target = np.load(OUT_DIR / "source_target.npy", allow_pickle=False)
    transpose = np.load(OUT_DIR / "transpose.npy", allow_pickle=False)

    if objects != expected["objects"]:
        raise AssertionError("objects.json is not reproducible")
    if orbitals != expected["orbitals"]:
        raise AssertionError("orbitals.json is not reproducible")
    if identity_orbitals != expected["identity_orbitals"]:
        raise AssertionError("identity_orbitals.json is not reproducible")
    if semisimple != expected["semisimple_category_certificate"]:
        raise AssertionError("semisimple_category_certificate.json is not reproducible")
    if not np.array_equal(source_target, expected["source_target"]):
        raise AssertionError("source_target.npy is not reproducible")
    if not np.array_equal(transpose, expected["transpose"]):
        raise AssertionError("transpose.npy is not reproducible")

    if report.get("schema") != "c985.proof_obligation.typed_simple_object_registry@1":
        raise AssertionError("C985 typed registry report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 typed registry is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 typed registry all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 typed registry report checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 typed registry report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 typed registry report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "point_count_is_2576",
        "group_order_is_9216",
        "relation_count_is_985",
        "ordered_pair_partition_covers_points_squared",
        "object_count_is_6",
        "object_sizes_match_core",
        "relation_count_matrix_matches_core_relations",
        "relation_count_matrix_matches_finite_algebra",
        "relation_count_matrix_sums_to_985",
        "segments_are_source_target_typed",
        "transpose_is_involution",
        "transpose_flips_source_target",
        "identity_relation_count_is_6",
        "identity_relations_match_closed_loop_units",
        "semisimple_skeleton_declares_coherence_open",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 typed registry missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("object_labels") != OBJECT_LABELS:
        raise AssertionError("C985 object labels mismatch")
    if witness.get("relation_count") != 985:
        raise AssertionError("C985 relation count mismatch")
    if witness.get("identity_relations") != [6, 163, 227, 349, 618, 893]:
        raise AssertionError("C985 identity relation list mismatch")
    if source_target.shape != (985, 2):
        raise AssertionError("source_target shape mismatch")
    if transpose.shape != (985,):
        raise AssertionError("transpose shape mismatch")
    if orbitals.get("relation_count") != 985 or len(orbitals.get("orbitals", [])) != 985:
        raise AssertionError("orbitals row count mismatch")
    if len(objects.get("objects", [])) != 6:
        raise AssertionError("objects row count mismatch")
    if "full finite semisimple multi-fusion category status" not in semisimple.get(
        "does_not_certify", []
    ):
        raise AssertionError("semisimple boundary no longer records open multi-fusion status")

    assert_file_hash(report.get("inputs", {}).get("relation_memberships", {}), SOURCE_RELATION_NPZ, "relation input")
    assert_file_hash(report.get("inputs", {}).get("core_a985", {}), CORE_A985_JSON, "core A985 input")

    if manifest.get("schema") != "c985.proof_obligation.typed_simple_object_registry_manifest@1":
        raise AssertionError("C985 typed registry manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 typed registry manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 typed registry manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 typed registry missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 typed registry index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 typed registry index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.typed_simple_object_registry@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "relation_count": witness.get("relation_count"),
        "object_labels": witness.get("object_labels"),
        "identity_relations": witness.get("identity_relations"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_typed_simple_object_registry()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
