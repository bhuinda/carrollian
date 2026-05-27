from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_quotient_poincare_geometry import (
        ATOM_GEOMETRY_COLUMNS,
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        GEOMETRY_OBSERVABLE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        POINCARE_CERTIFICATE,
        POINCARE_JSON,
        POINCARE_REPORT,
        POINCARE_TABLES,
        QUOTIENT_CERTIFICATE,
        QUOTIENT_JSON,
        QUOTIENT_REPORT,
        QUOTIENT_TABLES,
        SPECTRAL_CUT_ATOM_CSV,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        STATE_GEOMETRY_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_quotient_poincare_geometry import (
        ATOM_GEOMETRY_COLUMNS,
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        GEOMETRY_OBSERVABLE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        POINCARE_CERTIFICATE,
        POINCARE_JSON,
        POINCARE_REPORT,
        POINCARE_TABLES,
        QUOTIENT_CERTIFICATE,
        QUOTIENT_JSON,
        QUOTIENT_REPORT,
        QUOTIENT_TABLES,
        SPECTRAL_CUT_ATOM_CSV,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        STATE_GEOMETRY_COLUMNS,
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


def validate_c985_d20_signature_quotient_poincare_geometry() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    geometry = load_json(OUT_DIR / "signature_quotient_poincare_geometry.json")
    certificate = load_json(
        OUT_DIR / "signature_quotient_poincare_geometry_certificate.json"
    )
    state_csv = (OUT_DIR / "quotient_state_geometry.csv").read_text(encoding="utf-8")
    atom_csv = (OUT_DIR / "quotient_atom_geometry.csv").read_text(encoding="utf-8")
    observable_csv = (OUT_DIR / "quotient_geometry_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_quotient_poincare_geometry_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if geometry != expected["signature_quotient_poincare_geometry"]:
        raise AssertionError("signature quotient Poincare geometry JSON is not reproducible")
    if state_csv != expected["quotient_state_geometry_csv"]:
        raise AssertionError("signature quotient state geometry CSV is not reproducible")
    if atom_csv != expected["quotient_atom_geometry_csv"]:
        raise AssertionError("signature quotient atom geometry CSV is not reproducible")
    if observable_csv != expected["quotient_geometry_observables_csv"]:
        raise AssertionError("signature quotient observable CSV is not reproducible")
    if certificate != expected["signature_quotient_poincare_geometry_certificate"]:
        raise AssertionError("signature quotient Poincare geometry certificate is not reproducible")

    table_names = [
        "state_geometry_table",
        "atom_geometry_table",
        "geometry_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature quotient Poincare table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_quotient_poincare_geometry@1":
        raise AssertionError("C985 d20 signature quotient Poincare geometry report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature quotient Poincare geometry is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature quotient Poincare geometry all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature quotient Poincare geometry checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature quotient Poincare geometry report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature quotient Poincare geometry report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "quotient_report_certified",
        "quotient_certificate_certified",
        "spectral_cut_report_certified",
        "spectral_cut_certificate_certified",
        "poincare_report_certified",
        "poincare_certificate_certified",
        "boundary_transfer_report_certified",
        "boundary_transfer_certificate_certified",
        "active_atom_count_is_6",
        "state_geometry_table_shape_is_3_by_15",
        "atom_geometry_table_shape_is_6_by_12",
        "observable_table_shape_matches_codebook",
        "positive_center_matches_expected",
        "negative_center_matches_expected",
        "total_center_matches_expected",
        "positive_negative_separation_matches_expected",
        "positive_core_distance_matches_expected",
        "negative_core_distance_matches_expected",
        "total_core_distance_matches_expected",
        "negative_center_is_closer_to_core_than_positive",
        "mean_hyperbolic_atom_distances_match_expected",
        "recomposition_center_matches_total_center",
        "state_masses_match_quotient",
        "top_atoms_match_spectral_cut_reading",
        "core_center_matches_boundary_transfer",
        "poincare_coordinate_count_is_20",
        "poincare_tables_available",
        "quotient_tables_available",
        "spectral_cut_tables_available",
        "boundary_transfer_tables_available",
        "quotient_json_schema_available",
        "spectral_cut_json_schema_available",
        "poincare_json_schema_available",
        "boundary_transfer_json_schema_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(
            f"C985 d20 signature quotient Poincare geometry missing true checks: {missing}"
        )

    witness = report.get("witness", {})
    if witness.get("positive_center_x1e12") != {
        "x": 20629332981,
        "y": -33331853999,
        "radius": 39199258542,
    }:
        raise AssertionError("signature quotient positive center mismatch")
    if witness.get("negative_center_x1e12") != {
        "x": -64414008159,
        "y": -23944469697,
        "radius": 68720463300,
    }:
        raise AssertionError("signature quotient negative center mismatch")
    if witness.get("total_center_x1e12") != {
        "x": -11167767766,
        "y": -29821977736,
        "radius": 31844456235,
    }:
        raise AssertionError("signature quotient total center mismatch")
    if witness.get("core_center_x1e12") != {
        "x": -50213137809,
        "y": -3098360902,
        "radius": 50308637915,
    }:
        raise AssertionError("signature quotient core center mismatch")
    if witness.get("positive_negative_hyperbolic_separation_x1e12") != 171447126521:
        raise AssertionError("signature quotient center separation mismatch")
    if witness.get("positive_negative_euclidean_separation_x1e12") != 85559878776:
        raise AssertionError("signature quotient Euclidean separation mismatch")
    if witness.get("positive_core_hyperbolic_distance_x1e12") != 154209412933:
        raise AssertionError("signature quotient positive-core distance mismatch")
    if witness.get("negative_core_hyperbolic_distance_x1e12") != 50625248627:
        raise AssertionError("signature quotient negative-core distance mismatch")
    if witness.get("total_core_hyperbolic_distance_x1e12") != 94762246226:
        raise AssertionError("signature quotient total-core distance mismatch")
    if witness.get("negative_core_distance_advantage_x1e12") != 103584164306:
        raise AssertionError("signature quotient core distance advantage mismatch")
    if witness.get("positive_mean_hyperbolic_atom_distance_x1e12") != 305140715396:
        raise AssertionError("signature quotient positive mean atom distance mismatch")
    if witness.get("negative_mean_hyperbolic_atom_distance_x1e12") != 286772503879:
        raise AssertionError("signature quotient negative mean atom distance mismatch")
    if witness.get("total_mean_hyperbolic_atom_distance_x1e12") != 311069149257:
        raise AssertionError("signature quotient total mean atom distance mismatch")
    if (
        witness.get("positive_top_atom_id"),
        witness.get("negative_top_atom_id"),
        witness.get("total_top_atom_id"),
    ) != (7, 12, 19):
        raise AssertionError("signature quotient top atom mismatch")
    if witness.get("recomposition_delta_abs_x_x1e12") != 0:
        raise AssertionError("signature quotient recomposition x mismatch")
    if witness.get("recomposition_delta_abs_y_x1e12") != 0:
        raise AssertionError("signature quotient recomposition y mismatch")

    state_table = np.asarray(tables["state_geometry_table"], dtype=np.int64)
    atom_table = np.asarray(tables["atom_geometry_table"], dtype=np.int64)
    observable_table = np.asarray(tables["geometry_observable_table"], dtype=np.int64)

    if state_table.shape != (3, len(STATE_GEOMETRY_COLUMNS)):
        raise AssertionError("signature quotient state geometry table shape mismatch")
    if atom_table.shape != (6, len(ATOM_GEOMETRY_COLUMNS)):
        raise AssertionError("signature quotient atom geometry table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(GEOMETRY_OBSERVABLE_COLUMNS)):
        raise AssertionError("signature quotient observable table shape mismatch")
    if state_table[:, 3].tolist() != [626107108209, 373892891791, 1000000000000]:
        raise AssertionError("signature quotient state masses mismatch")
    if state_table[:, 13].tolist() != [7, 12, 19]:
        raise AssertionError("signature quotient state top atoms mismatch")
    if state_table[0, 9] <= state_table[1, 9]:
        raise AssertionError("signature quotient negative center is not closer to core")
    if atom_table[:, 0].tolist() != [1, 4, 7, 11, 12, 19]:
        raise AssertionError("signature quotient active atom order mismatch")
    if atom_table[:, 7].tolist() != [
        814767137249,
        865065168895,
        1000000000000,
        395702925816,
        0,
        557732426600,
    ]:
        raise AssertionError("signature quotient atom positive fractions mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("signature quotient observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("quotient_report", {}), QUOTIENT_REPORT, "quotient report input")
    assert_file_hash(inputs.get("quotient", {}), QUOTIENT_JSON, "quotient JSON input")
    assert_file_hash(inputs.get("quotient_tables", {}), QUOTIENT_TABLES, "quotient tables input")
    assert_file_hash(
        inputs.get("quotient_certificate", {}),
        QUOTIENT_CERTIFICATE,
        "quotient certificate input",
    )
    assert_file_hash(inputs.get("spectral_cut_report", {}), SPECTRAL_CUT_REPORT, "spectral cut report input")
    assert_file_hash(inputs.get("spectral_cut", {}), SPECTRAL_CUT_JSON, "spectral cut JSON input")
    assert_file_hash(inputs.get("spectral_cut_tables", {}), SPECTRAL_CUT_TABLES, "spectral cut tables input")
    assert_file_hash(
        inputs.get("spectral_cut_atom_summary", {}),
        SPECTRAL_CUT_ATOM_CSV,
        "spectral cut atom summary input",
    )
    assert_file_hash(
        inputs.get("spectral_cut_certificate", {}),
        SPECTRAL_CUT_CERTIFICATE,
        "spectral cut certificate input",
    )
    assert_file_hash(inputs.get("poincare_report", {}), POINCARE_REPORT, "Poincare report input")
    assert_file_hash(inputs.get("poincare_embedding", {}), POINCARE_JSON, "Poincare JSON input")
    assert_file_hash(inputs.get("poincare_tables", {}), POINCARE_TABLES, "Poincare tables input")
    assert_file_hash(
        inputs.get("poincare_certificate", {}),
        POINCARE_CERTIFICATE,
        "Poincare certificate input",
    )
    assert_file_hash(
        inputs.get("boundary_transfer_report", {}),
        BOUNDARY_TRANSFER_REPORT,
        "boundary transfer report input",
    )
    assert_file_hash(
        inputs.get("boundary_transfer", {}),
        BOUNDARY_TRANSFER_JSON,
        "boundary transfer JSON input",
    )
    assert_file_hash(
        inputs.get("boundary_transfer_tables", {}),
        BOUNDARY_TRANSFER_TABLES,
        "boundary transfer tables input",
    )
    assert_file_hash(
        inputs.get("boundary_transfer_certificate", {}),
        BOUNDARY_TRANSFER_CERTIFICATE,
        "boundary transfer certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_quotient_poincare_geometry_manifest@1":
        raise AssertionError("C985 d20 signature quotient Poincare geometry manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature quotient Poincare geometry manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature quotient Poincare geometry manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature quotient Poincare geometry missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature quotient Poincare geometry index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature quotient Poincare geometry index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_quotient_poincare_geometry@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "positive_center_x1e12": witness.get("positive_center_x1e12"),
        "negative_center_x1e12": witness.get("negative_center_x1e12"),
        "total_center_x1e12": witness.get("total_center_x1e12"),
        "core_center_x1e12": witness.get("core_center_x1e12"),
        "positive_negative_hyperbolic_separation_x1e12": witness.get(
            "positive_negative_hyperbolic_separation_x1e12"
        ),
        "positive_core_hyperbolic_distance_x1e12": witness.get(
            "positive_core_hyperbolic_distance_x1e12"
        ),
        "negative_core_hyperbolic_distance_x1e12": witness.get(
            "negative_core_hyperbolic_distance_x1e12"
        ),
        "negative_core_distance_advantage_x1e12": witness.get(
            "negative_core_distance_advantage_x1e12"
        ),
        "top_atoms": {
            "positive": witness.get("positive_top_atom_id"),
            "negative": witness.get("negative_top_atom_id"),
            "total": witness.get("total_top_atom_id"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_quotient_poincare_geometry()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
