from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_boundary_invariant_atlas import (
        D20_ATOM_DOMAIN_CSV,
        GEOMETRY_REPORT,
        INDEX_PATH,
        OBJECT_SECTOR_CUBES,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        TENSOR_GEOMETRY_SUMMARY,
        TINY_POINTER_REPORT,
        TINY_POINTER_SCHEMA,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_boundary_invariant_atlas import (
        D20_ATOM_DOMAIN_CSV,
        GEOMETRY_REPORT,
        INDEX_PATH,
        OBJECT_SECTOR_CUBES,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        TENSOR_GEOMETRY_SUMMARY,
        TINY_POINTER_REPORT,
        TINY_POINTER_SCHEMA,
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


def validate_c985_d20_boundary_invariant_atlas() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    atlas = load_json(OUT_DIR / "d20_boundary_invariant_atlas.json")
    certificate = load_json(OUT_DIR / "projection_certificate.json")
    atlas_csv = (OUT_DIR / "d20_boundary_invariant_atlas.csv").read_text(encoding="utf-8")
    atlas_npz = np.load(OUT_DIR / "d20_boundary_invariant_atlas.npz", allow_pickle=False)
    atom_table = np.asarray(atlas_npz["atom_table"], dtype=np.int64)
    relation_signature_class_ids = np.asarray(
        atlas_npz["relation_signature_class_ids"],
        dtype=np.int64,
    )
    index = load_json(INDEX_PATH)

    if atlas != expected["atlas"]:
        raise AssertionError("d20 boundary invariant atlas JSON is not reproducible")
    if atlas_csv != expected["atlas_csv"]:
        raise AssertionError("d20 boundary invariant atlas CSV is not reproducible")
    if not np.array_equal(atom_table, expected["atom_numeric"]):
        raise AssertionError("d20 boundary invariant atom table is not reproducible")
    if not np.array_equal(relation_signature_class_ids, expected["relation_signature_class_ids"]):
        raise AssertionError("relation signature class ids are not reproducible")
    if certificate != expected["projection_certificate"]:
        raise AssertionError("d20 boundary projection certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_boundary_invariant_atlas@1":
        raise AssertionError("C985 d20 boundary atlas report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary atlas is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary atlas all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary atlas checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary atlas report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary atlas report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "tensor_geometry_report_certified",
        "tiny_pointer_atom_domain_certified",
        "atom_domain_has_20_rows",
        "atom_domain_is_c_h6_3",
        "atom_ids_are_contiguous",
        "object_sector_cube_shape_is_6_by_6_by_6",
        "relation_records_shape_is_985_by_12",
        "signature_matrix_reproducible",
        "ordered_distinct_path_count_is_6_per_atom",
        "atom_distinct_path_support_sums_match_cube",
        "atom_distinct_path_mass_sums_match_cube",
        "degenerate_and_distinct_support_partition_tensor",
        "degenerate_and_distinct_mass_partition_tensor",
        "relation_atom_incidence_total_matches_source_target_formula",
        "all_relation_signature_classes_seen_by_atoms",
        "all_atoms_have_positive_tensor_support",
        "all_atoms_have_positive_internal_relation_count",
        "complement_pair_count_is_10",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary atlas missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("atom_count") != 20:
        raise AssertionError("d20 atom count mismatch")
    if witness.get("relation_count") != 985:
        raise AssertionError("C985 relation count mismatch")
    if witness.get("signature_class_count") != 233:
        raise AssertionError("C985 relation signature class count mismatch")
    if witness.get("complement_pair_count") != 10:
        raise AssertionError("d20 complement pair count mismatch")
    if atom_table.shape != (20, 15):
        raise AssertionError("d20 atlas atom table shape mismatch")
    if relation_signature_class_ids.shape != (985,):
        raise AssertionError("relation signature class id shape mismatch")
    if int(atom_table[:, 2].min()) != 6 or int(atom_table[:, 2].max()) != 6:
        raise AssertionError("every d20 atom should aggregate six ordered distinct paths")
    if int(atom_table[:, 3].sum()) != witness.get("distinct_object_path_support"):
        raise AssertionError("d20 atom table support total mismatch")
    if int(atom_table[:, 4].sum()) != witness.get("distinct_object_path_coefficient_mass"):
        raise AssertionError("d20 atom table coefficient mass total mismatch")
    if int(atom_table[:, 5].min()) <= 0:
        raise AssertionError("d20 atlas has an atom with no internal relations")
    if int(atom_table[:, 6].min()) <= 0:
        raise AssertionError("d20 atlas has an atom with no signature classes")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("tensor_geometry_report", {}), GEOMETRY_REPORT, "geometry report input")
    assert_file_hash(inputs.get("object_sector_cubes", {}), OBJECT_SECTOR_CUBES, "object sector cube input")
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation signatures input",
    )
    assert_file_hash(
        inputs.get("tensor_geometry_summary", {}),
        TENSOR_GEOMETRY_SUMMARY,
        "tensor summary input",
    )
    assert_file_hash(inputs.get("tiny_pointer_report", {}), TINY_POINTER_REPORT, "tiny pointer report input")
    assert_file_hash(inputs.get("d20_atom_domain", {}), D20_ATOM_DOMAIN_CSV, "d20 atom domain input")
    assert_file_hash(inputs.get("tiny_pointer_schema", {}), TINY_POINTER_SCHEMA, "tiny pointer schema input")

    if manifest.get("schema") != "c985.proof_obligation.d20_boundary_invariant_atlas_manifest@1":
        raise AssertionError("C985 d20 boundary atlas manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary atlas manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary atlas manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 boundary atlas missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary atlas index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary atlas index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_boundary_invariant_atlas@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "atom_count": witness.get("atom_count"),
        "signature_class_count": witness.get("signature_class_count"),
        "distinct_object_path_support": witness.get("distinct_object_path_support"),
        "distinct_object_path_coefficient_mass": witness.get(
            "distinct_object_path_coefficient_mass"
        ),
        "degenerate_object_path_support": witness.get("degenerate_object_path_support"),
        "degenerate_object_path_coefficient_mass": witness.get(
            "degenerate_object_path_coefficient_mass"
        ),
        "atom_tensor_mass_range": [
            witness.get("atom_tensor_mass_min"),
            witness.get("atom_tensor_mass_max"),
        ],
        "atom_signature_class_count_range": [
            witness.get("atom_internal_signature_class_count_min"),
            witness.get("atom_internal_signature_class_count_max"),
        ],
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_boundary_invariant_atlas()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
