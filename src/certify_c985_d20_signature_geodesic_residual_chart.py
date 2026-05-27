from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_geodesic_residual_chart import (
        CARRIER_RESIDUAL_COLUMNS,
        GEODESIC_ORDER_CARRIER_CSV,
        GEODESIC_ORDER_CERTIFICATE,
        GEODESIC_ORDER_JSON,
        GEODESIC_ORDER_REPORT,
        GEODESIC_ORDER_SIGNATURE_CSV,
        GEODESIC_ORDER_TABLES,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_OBSERVABLE_COLUMNS,
        SIGNATURE_RESIDUAL_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_geodesic_residual_chart import (
        CARRIER_RESIDUAL_COLUMNS,
        GEODESIC_ORDER_CARRIER_CSV,
        GEODESIC_ORDER_CERTIFICATE,
        GEODESIC_ORDER_JSON,
        GEODESIC_ORDER_REPORT,
        GEODESIC_ORDER_SIGNATURE_CSV,
        GEODESIC_ORDER_TABLES,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_OBSERVABLE_COLUMNS,
        SIGNATURE_RESIDUAL_COLUMNS,
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


def validate_c985_d20_signature_geodesic_residual_chart() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    chart = load_json(OUT_DIR / "signature_geodesic_residual_chart.json")
    certificate = load_json(
        OUT_DIR / "signature_geodesic_residual_chart_certificate.json"
    )
    carrier_csv = (OUT_DIR / "carrier_residual_chart.csv").read_text(encoding="utf-8")
    signature_csv = (OUT_DIR / "signature_residual_chart.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "residual_chart_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_geodesic_residual_chart_tables.npz",
        allow_pickle=False,
    )
    index = load_json(Path(OUT_DIR).parents[0] / "index.json")

    if chart != expected["signature_geodesic_residual_chart"]:
        raise AssertionError("signature geodesic residual chart JSON is not reproducible")
    if carrier_csv != expected["carrier_residual_chart_csv"]:
        raise AssertionError("carrier residual chart CSV is not reproducible")
    if signature_csv != expected["signature_residual_chart_csv"]:
        raise AssertionError("signature residual chart CSV is not reproducible")
    if observable_csv != expected["residual_chart_observables_csv"]:
        raise AssertionError("residual chart observable CSV is not reproducible")
    if certificate != expected["signature_geodesic_residual_chart_certificate"]:
        raise AssertionError("signature geodesic residual chart certificate is not reproducible")

    table_names = [
        "carrier_residual_chart_table",
        "signature_residual_chart_table",
        "residual_chart_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature residual chart table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_geodesic_residual_chart@1":
        raise AssertionError("C985 d20 signature residual chart report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature residual chart is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature residual chart all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature residual chart checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature residual chart report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature residual chart report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "geodesic_order_report_certified",
        "geodesic_order_certificate_certified",
        "carrier_count_is_14",
        "signature_count_is_221",
        "low_axis_threshold_matches_geodesic_best",
        "residual_gate_threshold_matches_expected",
        "high_axis_threshold_matches_expected",
        "elbow_threshold_search_is_perfect",
        "elbow_classifier_separates_all_carriers",
        "elbow_classifier_separates_all_signatures",
        "previous_obstruction_resolved_by_residual_gate",
        "region_ids_match_expected",
        "region_masses_match_expected",
        "previous_obstruction_mass_matches_expected",
        "signed_residuals_match_axis_residual_magnitudes",
        "carrier_coordinates_are_distinct",
        "perpendicular_direction_matches_expected",
        "carrier_table_shape_is_14_by_25",
        "signature_table_shape_is_221_by_16",
        "observable_table_shape_matches_codebook",
        "geodesic_order_tables_available",
        "geodesic_order_json_schema_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 signature residual chart missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("low_axis_threshold_x1e12") != -51543783679:
        raise AssertionError("signature residual chart low-axis threshold mismatch")
    if witness.get("residual_gate_threshold_x1e12") != -149928684557:
        raise AssertionError("signature residual chart residual threshold mismatch")
    if witness.get("high_axis_threshold_x1e12") != 178625198443:
        raise AssertionError("signature residual chart high-axis threshold mismatch")
    if witness.get("one_dimensional_agreement_count") != 192:
        raise AssertionError("signature residual chart one-dimensional count mismatch")
    if witness.get("one_dimensional_agreement_mass_x1e12") != 852128653272:
        raise AssertionError("signature residual chart one-dimensional mass mismatch")
    if witness.get("elbow_agreement_count") != 221:
        raise AssertionError("signature residual chart elbow count mismatch")
    if witness.get("elbow_agreement_mass_x1e12") != 1_000_000_000_000:
        raise AssertionError("signature residual chart elbow mass mismatch")
    if witness.get("elbow_misclassified_count") != 0:
        raise AssertionError("signature residual chart elbow miss count mismatch")
    if witness.get("elbow_misclassified_mass_x1e12") != 0:
        raise AssertionError("signature residual chart elbow miss mass mismatch")
    if witness.get("high_cap_mask_class_ids") != [0, 1]:
        raise AssertionError("signature residual chart high cap ids mismatch")
    if witness.get("central_gate_mask_class_ids") != [2, 3, 10, 11, 12]:
        raise AssertionError("signature residual chart central gate ids mismatch")
    if witness.get("negative_region_mask_class_ids") != [4, 5, 6, 7, 8, 9, 13]:
        raise AssertionError("signature residual chart negative region ids mismatch")
    if witness.get("previous_obstruction_mask_class_ids") != [4, 7, 8]:
        raise AssertionError("signature residual chart previous obstruction ids mismatch")
    if witness.get("previous_obstruction_signature_count") != 29:
        raise AssertionError("signature residual chart previous obstruction count mismatch")
    if witness.get("previous_obstruction_stationary_mass_x1e12") != 147871346728:
        raise AssertionError("signature residual chart previous obstruction mass mismatch")
    if witness.get("distinct_chart_coordinate_count") != 14:
        raise AssertionError("signature residual chart distinct coordinate count mismatch")
    if witness.get("carrier_coordinate_collision_count") != 0:
        raise AssertionError("signature residual chart coordinate collision mismatch")
    if witness.get("perpendicular_direction_x1e12") != {
        "t": -61701506611,
        "x": 111067537516,
        "y": 995726407216,
    }:
        raise AssertionError("signature residual chart perpendicular direction mismatch")

    carrier_table = np.asarray(tables["carrier_residual_chart_table"], dtype=np.int64)
    signature_table = np.asarray(tables["signature_residual_chart_table"], dtype=np.int64)
    observable_table = np.asarray(tables["residual_chart_observable_table"], dtype=np.int64)

    if carrier_table.shape != (14, len(CARRIER_RESIDUAL_COLUMNS)):
        raise AssertionError("signature residual chart carrier table shape mismatch")
    if signature_table.shape != (221, len(SIGNATURE_RESIDUAL_COLUMNS)):
        raise AssertionError("signature residual chart signature table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(RESIDUAL_OBSERVABLE_COLUMNS)):
        raise AssertionError("signature residual chart observable table shape mismatch")
    if carrier_table[:, 0].tolist() != list(range(14)):
        raise AssertionError("signature residual chart carrier order mismatch")
    if int(carrier_table[:, 14].sum()) != 14:
        raise AssertionError("signature residual chart carrier match column mismatch")
    if int(signature_table[:, 14].sum()) != 221:
        raise AssertionError("signature residual chart signature match column mismatch")
    if sorted(carrier_table[carrier_table[:, 12] == 2, 0].tolist()) != [0, 1]:
        raise AssertionError("signature residual chart high cap row mismatch")
    if sorted(carrier_table[carrier_table[:, 12] == 1, 0].tolist()) != [2, 3, 10, 11, 12]:
        raise AssertionError("signature residual chart central gate row mismatch")
    if sorted(carrier_table[carrier_table[:, 12] == -1, 0].tolist()) != [4, 5, 6, 7, 8, 9, 13]:
        raise AssertionError("signature residual chart negative region row mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("signature residual chart observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("geodesic_order_report", {}),
        GEODESIC_ORDER_REPORT,
        "geodesic order report input",
    )
    assert_file_hash(inputs.get("geodesic_order", {}), GEODESIC_ORDER_JSON, "geodesic order JSON input")
    assert_file_hash(
        inputs.get("geodesic_order_tables", {}),
        GEODESIC_ORDER_TABLES,
        "geodesic order tables input",
    )
    assert_file_hash(
        inputs.get("geodesic_order_certificate", {}),
        GEODESIC_ORDER_CERTIFICATE,
        "geodesic order certificate input",
    )
    assert_file_hash(
        inputs.get("geodesic_order_carrier_csv", {}),
        GEODESIC_ORDER_CARRIER_CSV,
        "geodesic order carrier CSV input",
    )
    assert_file_hash(
        inputs.get("geodesic_order_signature_csv", {}),
        GEODESIC_ORDER_SIGNATURE_CSV,
        "geodesic order signature CSV input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_geodesic_residual_chart_manifest@1":
        raise AssertionError("C985 d20 signature residual chart manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature residual chart manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature residual chart manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature residual chart missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature residual chart index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature residual chart index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_geodesic_residual_chart@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "thresholds_x1e12": {
            "low_axis": witness.get("low_axis_threshold_x1e12"),
            "residual_gate": witness.get("residual_gate_threshold_x1e12"),
            "high_axis": witness.get("high_axis_threshold_x1e12"),
        },
        "one_dimensional_agreement": {
            "count": witness.get("one_dimensional_agreement_count"),
            "mass_x1e12": witness.get("one_dimensional_agreement_mass_x1e12"),
        },
        "elbow_agreement": {
            "count": witness.get("elbow_agreement_count"),
            "mass_x1e12": witness.get("elbow_agreement_mass_x1e12"),
        },
        "regions": {
            "high_cap": witness.get("high_cap_mask_class_ids"),
            "central_gate": witness.get("central_gate_mask_class_ids"),
            "negative": witness.get("negative_region_mask_class_ids"),
        },
        "previous_obstruction_mask_class_ids": witness.get(
            "previous_obstruction_mask_class_ids"
        ),
        "carrier_coordinate_collision_count": witness.get(
            "carrier_coordinate_collision_count"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_geodesic_residual_chart()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
