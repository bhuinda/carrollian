from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_geodesic_order import (
        CARRIER_GEODESIC_COLUMNS,
        GEODESIC_OBSERVABLE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        QUOTIENT_GEOMETRY_CERTIFICATE,
        QUOTIENT_GEOMETRY_JSON,
        QUOTIENT_GEOMETRY_REPORT,
        QUOTIENT_GEOMETRY_TABLES,
        SIGNATURE_GEODESIC_COLUMNS,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SIGNATURE_SUBBOUNDARY_VERTICES,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        SPECTRAL_MASK_SUMMARY,
        SPECTRAL_SIGNATURE_VERTICES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_geodesic_order import (
        CARRIER_GEODESIC_COLUMNS,
        GEODESIC_OBSERVABLE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        QUOTIENT_GEOMETRY_CERTIFICATE,
        QUOTIENT_GEOMETRY_JSON,
        QUOTIENT_GEOMETRY_REPORT,
        QUOTIENT_GEOMETRY_TABLES,
        SIGNATURE_GEODESIC_COLUMNS,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SIGNATURE_SUBBOUNDARY_VERTICES,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        SPECTRAL_MASK_SUMMARY,
        SPECTRAL_SIGNATURE_VERTICES,
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


def validate_c985_d20_signature_geodesic_order() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    geodesic_order = load_json(OUT_DIR / "signature_geodesic_order.json")
    certificate = load_json(OUT_DIR / "signature_geodesic_order_certificate.json")
    carrier_csv = (OUT_DIR / "carrier_geodesic_order.csv").read_text(encoding="utf-8")
    signature_csv = (OUT_DIR / "signature_geodesic_order.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "geodesic_order_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(OUT_DIR / "signature_geodesic_order_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if geodesic_order != expected["signature_geodesic_order"]:
        raise AssertionError("signature geodesic order JSON is not reproducible")
    if carrier_csv != expected["carrier_geodesic_order_csv"]:
        raise AssertionError("carrier geodesic order CSV is not reproducible")
    if signature_csv != expected["signature_geodesic_order_csv"]:
        raise AssertionError("signature geodesic order CSV is not reproducible")
    if observable_csv != expected["geodesic_order_observables_csv"]:
        raise AssertionError("geodesic order observable CSV is not reproducible")
    if certificate != expected["signature_geodesic_order_certificate"]:
        raise AssertionError("signature geodesic order certificate is not reproducible")

    table_names = [
        "carrier_geodesic_table",
        "signature_geodesic_table",
        "geodesic_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature geodesic order table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_geodesic_order@1":
        raise AssertionError("C985 d20 signature geodesic order report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature geodesic order is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature geodesic order all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature geodesic order checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature geodesic order report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature geodesic order report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "quotient_geometry_report_certified",
        "quotient_geometry_certificate_certified",
        "spectral_cut_report_certified",
        "spectral_cut_certificate_certified",
        "signature_subboundary_report_certified",
        "signature_subboundary_certificate_certified",
        "active_atom_count_is_6",
        "carrier_mask_count_is_14",
        "signature_vertex_count_is_221",
        "subboundary_vertex_count_is_221",
        "axis_length_matches_geometry_separation",
        "axis_length_matches_expected",
        "axis_midpoint_matches_expected",
        "best_threshold_matches_expected",
        "zero_threshold_agreement_matches_expected",
        "best_threshold_agreement_matches_expected",
        "best_threshold_is_exhaustive_optimum",
        "best_threshold_misclassification_matches_expected",
        "all_positive_vertices_right_of_best_threshold",
        "only_negative_obstruction_vertices_remain",
        "positive_negative_mean_coordinates_match_expected",
        "weighted_axis_mode_correlation_matches_expected",
        "sign_pair_inversions_match_expected",
        "projection_residuals_match_expected",
        "carrier_table_shape_is_14_by_23",
        "signature_table_shape_is_221_by_15",
        "observable_table_shape_matches_codebook",
        "geometry_tables_available",
        "spectral_cut_tables_available",
        "signature_subboundary_tables_available",
        "geometry_json_schema_available",
        "spectral_cut_json_schema_available",
        "signature_subboundary_json_schema_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 signature geodesic order missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("axis_hyperbolic_length_x1e12") != 171447126521:
        raise AssertionError("signature geodesic axis length mismatch")
    if witness.get("axis_half_length_x1e12") != 85723563261:
        raise AssertionError("signature geodesic axis half length mismatch")
    if witness.get("axis_midpoint_x1e12") != {
        "x": -21920116945,
        "y": -28578291790,
        "radius": 36016805640,
    }:
        raise AssertionError("signature geodesic midpoint mismatch")
    if witness.get("best_threshold_x1e12") != -51543783679:
        raise AssertionError("signature geodesic best threshold mismatch")
    if witness.get("zero_threshold_agreement_count") != 162:
        raise AssertionError("signature geodesic zero threshold count mismatch")
    if witness.get("zero_threshold_agreement_mass_x1e12") != 785660554020:
        raise AssertionError("signature geodesic zero threshold mass mismatch")
    if witness.get("best_threshold_agreement_count") != 192:
        raise AssertionError("signature geodesic best threshold count mismatch")
    if witness.get("best_threshold_agreement_mass_x1e12") != 852128653272:
        raise AssertionError("signature geodesic best threshold mass mismatch")
    if witness.get("best_threshold_misclassified_count") != 29:
        raise AssertionError("signature geodesic obstruction count mismatch")
    if witness.get("best_threshold_misclassified_mass_x1e12") != 147871346728:
        raise AssertionError("signature geodesic obstruction mass mismatch")
    if witness.get("obstruction_mask_class_ids") != [4, 7, 8]:
        raise AssertionError("signature geodesic obstruction mask mismatch")
    if witness.get("positive_mean_axis_coordinate_x1e12") != 85897163407:
        raise AssertionError("signature geodesic positive mean coordinate mismatch")
    if witness.get("negative_mean_axis_coordinate_x1e12") != -85040731263:
        raise AssertionError("signature geodesic negative mean coordinate mismatch")
    if witness.get("weighted_axis_mode_correlation_x1e12") != 827040709152:
        raise AssertionError("signature geodesic axis/mode correlation mismatch")
    if witness.get("sign_pair_inversion_count") != 1980:
        raise AssertionError("signature geodesic inversion count mismatch")
    if witness.get("sign_pair_inversion_count_fraction_x1e12") != 163636363636:
        raise AssertionError("signature geodesic inversion count fraction mismatch")
    if witness.get("sign_pair_inversion_mass_fraction_x1e12") != 131316550327:
        raise AssertionError("signature geodesic inversion mass fraction mismatch")
    if witness.get("stationary_mean_projection_residual_x1e12") != 125701373183:
        raise AssertionError("signature geodesic mean residual mismatch")
    if witness.get("max_projection_residual_x1e12") != 352612226540:
        raise AssertionError("signature geodesic max residual mismatch")
    if witness.get("min_projection_residual_x1e12") != 18830038433:
        raise AssertionError("signature geodesic min residual mismatch")

    carrier_table = np.asarray(tables["carrier_geodesic_table"], dtype=np.int64)
    signature_table = np.asarray(tables["signature_geodesic_table"], dtype=np.int64)
    observable_table = np.asarray(tables["geodesic_observable_table"], dtype=np.int64)

    if carrier_table.shape != (14, len(CARRIER_GEODESIC_COLUMNS)):
        raise AssertionError("signature geodesic carrier table shape mismatch")
    if signature_table.shape != (221, len(SIGNATURE_GEODESIC_COLUMNS)):
        raise AssertionError("signature geodesic signature table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(GEODESIC_OBSERVABLE_COLUMNS)):
        raise AssertionError("signature geodesic observable table shape mismatch")
    if carrier_table[:, 0].tolist() != list(range(14)):
        raise AssertionError("signature geodesic carrier mask order mismatch")
    if signature_table[:, 0].tolist() != list(range(221)):
        raise AssertionError("signature geodesic signature vertex order mismatch")
    if sorted(signature_table[:, 1].tolist()) != signature_table[:, 1].tolist():
        raise AssertionError("signature geodesic signature class order mismatch")
    if int(signature_table[:, 12].sum()) != 162:
        raise AssertionError("signature geodesic zero-threshold match column mismatch")
    if int(signature_table[:, 13].sum()) != 192:
        raise AssertionError("signature geodesic best-threshold match column mismatch")
    if sorted(carrier_table[carrier_table[:, 17] == 0, 0].tolist()) != [4, 7, 8]:
        raise AssertionError("signature geodesic carrier obstruction rows mismatch")
    if int(signature_table[signature_table[:, 13] == 0, 2].max()) != -1:
        raise AssertionError("signature geodesic positive class obstruction found")
    if int(signature_table[signature_table[:, 2] == 1, 8].min()) <= 0:
        raise AssertionError("signature geodesic positive side crosses best threshold")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("signature geodesic observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("quotient_geometry_report", {}),
        QUOTIENT_GEOMETRY_REPORT,
        "quotient geometry report input",
    )
    assert_file_hash(inputs.get("quotient_geometry", {}), QUOTIENT_GEOMETRY_JSON, "quotient geometry JSON input")
    assert_file_hash(
        inputs.get("quotient_geometry_tables", {}),
        QUOTIENT_GEOMETRY_TABLES,
        "quotient geometry tables input",
    )
    assert_file_hash(
        inputs.get("quotient_geometry_certificate", {}),
        QUOTIENT_GEOMETRY_CERTIFICATE,
        "quotient geometry certificate input",
    )
    assert_file_hash(inputs.get("spectral_cut_report", {}), SPECTRAL_CUT_REPORT, "spectral cut report input")
    assert_file_hash(inputs.get("spectral_cut", {}), SPECTRAL_CUT_JSON, "spectral cut JSON input")
    assert_file_hash(inputs.get("spectral_cut_tables", {}), SPECTRAL_CUT_TABLES, "spectral cut tables input")
    assert_file_hash(
        inputs.get("spectral_cut_certificate", {}),
        SPECTRAL_CUT_CERTIFICATE,
        "spectral cut certificate input",
    )
    assert_file_hash(
        inputs.get("spectral_signature_vertices", {}),
        SPECTRAL_SIGNATURE_VERTICES,
        "spectral signature vertex input",
    )
    assert_file_hash(
        inputs.get("spectral_mask_summary", {}),
        SPECTRAL_MASK_SUMMARY,
        "spectral mask summary input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary_report", {}),
        SIGNATURE_SUBBOUNDARY_REPORT,
        "signature subboundary report input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary", {}),
        SIGNATURE_SUBBOUNDARY_JSON,
        "signature subboundary JSON input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary_tables", {}),
        SIGNATURE_SUBBOUNDARY_TABLES,
        "signature subboundary tables input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary_certificate", {}),
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        "signature subboundary certificate input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary_vertices", {}),
        SIGNATURE_SUBBOUNDARY_VERTICES,
        "signature subboundary vertex input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_geodesic_order_manifest@1":
        raise AssertionError("C985 d20 signature geodesic order manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature geodesic order manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature geodesic order manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature geodesic order missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature geodesic order index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature geodesic order index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_geodesic_order@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "axis_hyperbolic_length_x1e12": witness.get("axis_hyperbolic_length_x1e12"),
        "best_threshold_x1e12": witness.get("best_threshold_x1e12"),
        "zero_threshold_agreement": {
            "count": witness.get("zero_threshold_agreement_count"),
            "mass_x1e12": witness.get("zero_threshold_agreement_mass_x1e12"),
        },
        "best_threshold_agreement": {
            "count": witness.get("best_threshold_agreement_count"),
            "mass_x1e12": witness.get("best_threshold_agreement_mass_x1e12"),
        },
        "obstruction": {
            "mask_class_ids": witness.get("obstruction_mask_class_ids"),
            "count": witness.get("best_threshold_misclassified_count"),
            "mass_x1e12": witness.get("best_threshold_misclassified_mass_x1e12"),
        },
        "weighted_axis_mode_correlation_x1e12": witness.get(
            "weighted_axis_mode_correlation_x1e12"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_geodesic_order()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
