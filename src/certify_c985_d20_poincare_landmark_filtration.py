from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_poincare_landmark_filtration import (
        ATLAS_JSON,
        ATLAS_NPZ,
        ATLAS_REPORT,
        FILTRATION_INT_COLUMNS,
        GEOMETRY_REPORT,
        INDEX_PATH,
        OUT_DIR,
        POINCARE_JSON,
        POINCARE_NPZ,
        POINCARE_REPORT,
        RELATION_GEOMETRY_SIGNATURES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_poincare_landmark_filtration import (
        ATLAS_JSON,
        ATLAS_NPZ,
        ATLAS_REPORT,
        FILTRATION_INT_COLUMNS,
        GEOMETRY_REPORT,
        INDEX_PATH,
        OUT_DIR,
        POINCARE_JSON,
        POINCARE_NPZ,
        POINCARE_REPORT,
        RELATION_GEOMETRY_SIGNATURES,
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


def validate_c985_d20_poincare_landmark_filtration() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    filtration = load_json(OUT_DIR / "landmark_filtration.json")
    certificate = load_json(OUT_DIR / "filtration_certificate.json")
    records_csv = (OUT_DIR / "filtration_records.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "filtration_tables.npz", allow_pickle=False)
    filtration_int_table = np.asarray(tables["filtration_int_table"], dtype=np.int64)
    entry_order = np.asarray(tables["entry_order"], dtype=np.int64)
    thresholds = np.asarray(tables["thresholds"], dtype=np.float64)
    novelty_matrix = np.asarray(tables["novelty_matrix"], dtype=np.int64)
    coverage_matrix = np.asarray(tables["coverage_matrix"], dtype=np.int64)
    mass_matrix = np.asarray(tables["mass_matrix"], dtype=np.int64)
    signature_count_sum_matrix = np.asarray(tables["signature_count_sum_matrix"], dtype=np.int64)
    signature_incidence = np.asarray(tables["signature_incidence"], dtype=np.int8)
    index = load_json(INDEX_PATH)

    if filtration != expected["landmark_filtration"]:
        raise AssertionError("Poincare landmark filtration JSON is not reproducible")
    if records_csv != expected["filtration_records_csv"]:
        raise AssertionError("Poincare landmark filtration CSV is not reproducible")
    if not np.array_equal(filtration_int_table, expected["filtration_int_table"]):
        raise AssertionError("Poincare landmark filtration integer table is not reproducible")
    if not np.array_equal(entry_order, expected["entry_order"]):
        raise AssertionError("Poincare landmark filtration entry order is not reproducible")
    if not np.allclose(thresholds, expected["thresholds"], rtol=0.0, atol=1e-12):
        raise AssertionError("Poincare landmark filtration thresholds are not reproducible")
    if not np.array_equal(novelty_matrix, expected["novelty_matrix"]):
        raise AssertionError("Poincare landmark filtration novelty matrix is not reproducible")
    if not np.array_equal(coverage_matrix, expected["coverage_matrix"]):
        raise AssertionError("Poincare landmark filtration coverage matrix is not reproducible")
    if not np.array_equal(mass_matrix, expected["mass_matrix"]):
        raise AssertionError("Poincare landmark filtration mass matrix is not reproducible")
    if not np.array_equal(signature_count_sum_matrix, expected["signature_count_sum_matrix"]):
        raise AssertionError("Poincare landmark signature-count sum matrix is not reproducible")
    if not np.array_equal(signature_incidence, expected["signature_incidence"]):
        raise AssertionError("Poincare landmark signature incidence is not reproducible")
    if certificate != expected["filtration_certificate"]:
        raise AssertionError("Poincare landmark filtration certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_poincare_landmark_filtration@1":
        raise AssertionError("C985 d20 Poincare landmark filtration report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 Poincare landmark filtration is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 Poincare landmark filtration all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 Poincare landmark filtration checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Poincare landmark filtration report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 Poincare landmark filtration report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "poincare_report_certified",
        "boundary_atlas_report_certified",
        "tensor_geometry_report_certified",
        "atom_count_is_20",
        "poincare_distance_matrix_is_20_by_20",
        "relation_signature_class_domain_is_233",
        "stored_relation_signature_classes_match_recomputed",
        "atom_signature_counts_match_atlas",
        "signature_incidence_shape_is_20_by_233",
        "filtration_record_count_is_400",
        "coverage_matrix_shape_is_20_by_20",
        "every_seed_reaches_full_signature_coverage",
        "minimum_full_coverage_ball_size_is_7",
        "no_ball_smaller_than_7_has_full_coverage",
        "minimum_full_coverage_seed_is_11",
        "minimum_full_coverage_radius_is_0_557922089",
        "minimum_full_coverage_ball_count_at_size_7_is_2",
        "minimum_full_coverage_ball_mass_is_below_half_total",
        "minimum_full_coverage_ball_contains_heaviest_atom",
        "minimum_full_coverage_ball_contains_most_central_atom",
        "heaviest_seed_full_coverage_size_is_11",
        "heaviest_seed_full_coverage_radius_is_0_5561031147",
        "richest_signature_seed_full_coverage_size_is_12",
        "heaviest_seed_first_five_covers_203_signature_classes",
        "gateway_seed_first_seven_novelty_sums_to_233",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 Poincare landmark filtration missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("atom_count") != 20:
        raise AssertionError("Poincare landmark filtration atom count mismatch")
    if witness.get("signature_class_count") != 233:
        raise AssertionError("Poincare landmark filtration signature class count mismatch")
    if witness.get("filtration_record_count") != 400:
        raise AssertionError("Poincare landmark filtration record count mismatch")
    if witness.get("minimum_full_coverage_seed") != 11:
        raise AssertionError("Poincare landmark filtration minimum seed mismatch")
    if witness.get("minimum_full_coverage_ball_size") != 7:
        raise AssertionError("Poincare landmark filtration minimum size mismatch")
    if witness.get("minimum_full_coverage_threshold") != 0.557922089:
        raise AssertionError("Poincare landmark filtration threshold mismatch")
    if witness.get("minimum_full_coverage_atom_ids") != [11, 4, 1, 7, 12, 8, 19]:
        raise AssertionError("Poincare landmark filtration minimum atom set mismatch")
    if witness.get("minimum_size_full_coverage_ball_count") != 2:
        raise AssertionError("Poincare landmark filtration minimum full ball count mismatch")
    if witness.get("heaviest_seed") != 19:
        raise AssertionError("Poincare landmark filtration heaviest seed mismatch")
    if witness.get("heaviest_seed_full_coverage_ball_size") != 11:
        raise AssertionError("Poincare landmark filtration heaviest seed coverage size mismatch")
    if witness.get("heaviest_seed_first_five_signature_coverage") != 203:
        raise AssertionError("Poincare landmark filtration heaviest seed pentad coverage mismatch")
    if witness.get("richest_signature_seed") != 9:
        raise AssertionError("Poincare landmark filtration richest signature seed mismatch")
    if witness.get("richest_signature_seed_full_coverage_ball_size") != 12:
        raise AssertionError("Poincare landmark filtration richest signature coverage size mismatch")

    if filtration_int_table.shape != (400, len(FILTRATION_INT_COLUMNS)):
        raise AssertionError("Poincare landmark filtration integer table shape mismatch")
    if entry_order.shape != (20, 20):
        raise AssertionError("Poincare landmark filtration entry order shape mismatch")
    if thresholds.shape != (20, 20):
        raise AssertionError("Poincare landmark filtration threshold shape mismatch")
    if novelty_matrix.shape != (20, 20):
        raise AssertionError("Poincare landmark filtration novelty matrix shape mismatch")
    if coverage_matrix.shape != (20, 20):
        raise AssertionError("Poincare landmark filtration coverage matrix shape mismatch")
    if mass_matrix.shape != (20, 20):
        raise AssertionError("Poincare landmark filtration mass matrix shape mismatch")
    if signature_count_sum_matrix.shape != (20, 20):
        raise AssertionError("Poincare landmark filtration signature sum matrix shape mismatch")
    if signature_incidence.shape != (20, 233):
        raise AssertionError("Poincare landmark filtration signature incidence shape mismatch")
    if int(coverage_matrix[11, 6]) != 233:
        raise AssertionError("Poincare landmark gateway ball does not cover all signatures")
    if int(coverage_matrix[:, :6].max()) >= 233:
        raise AssertionError("Poincare landmark smaller ball unexpectedly covers all signatures")
    if int(novelty_matrix[11, :7].sum()) != 233:
        raise AssertionError("Poincare landmark gateway novelty does not sum to 233")
    if int(coverage_matrix[19, 4]) != 203:
        raise AssertionError("Poincare landmark heaviest pentad coverage mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("poincare_report", {}), POINCARE_REPORT, "Poincare report input")
    assert_file_hash(inputs.get("poincare_embedding", {}), POINCARE_JSON, "Poincare JSON input")
    assert_file_hash(inputs.get("poincare_npz", {}), POINCARE_NPZ, "Poincare NPZ input")
    assert_file_hash(inputs.get("boundary_atlas_report", {}), ATLAS_REPORT, "atlas report input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "atlas JSON input")
    assert_file_hash(inputs.get("boundary_atlas_npz", {}), ATLAS_NPZ, "atlas NPZ input")
    assert_file_hash(inputs.get("tensor_geometry_report", {}), GEOMETRY_REPORT, "geometry report input")
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation signatures input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_poincare_landmark_filtration_manifest@1":
        raise AssertionError("C985 d20 Poincare landmark filtration manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Poincare landmark filtration manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 Poincare landmark filtration manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 Poincare landmark filtration missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Poincare landmark filtration index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 Poincare landmark filtration index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_poincare_landmark_filtration@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "signature_class_count": witness.get("signature_class_count"),
        "minimum_full_coverage_seed": witness.get("minimum_full_coverage_seed"),
        "minimum_full_coverage_seed_label": witness.get("minimum_full_coverage_seed_label"),
        "minimum_full_coverage_ball_size": witness.get("minimum_full_coverage_ball_size"),
        "minimum_full_coverage_threshold": witness.get("minimum_full_coverage_threshold"),
        "minimum_full_coverage_atom_ids": witness.get("minimum_full_coverage_atom_ids"),
        "minimum_full_coverage_mass": witness.get("minimum_full_coverage_mass"),
        "total_tensor_path_coefficient_mass": witness.get("total_tensor_path_coefficient_mass"),
        "smaller_ball_max_signature_coverage": witness.get("smaller_ball_max_signature_coverage"),
        "heaviest_seed_full_coverage_ball_size": witness.get(
            "heaviest_seed_full_coverage_ball_size"
        ),
        "heaviest_seed_first_five_signature_coverage": witness.get(
            "heaviest_seed_first_five_signature_coverage"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_poincare_landmark_filtration()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
