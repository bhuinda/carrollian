from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CELL_COMPLEX_VERTICES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        ROUTING_PREFIX_OBSERVABLE_COLUMNS,
        ROUTING_PREFIX_REGION_COLUMNS,
        ROUTING_PREFIX_SUMMARY_COLUMNS,
        SPINE_PATH_CERTIFICATE,
        SPINE_PATH_EDGES,
        SPINE_PATH_JSON,
        SPINE_PATH_REPORT,
        SPINE_PATH_TABLES,
        SPINE_PATH_TRANSITIONS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CELL_COMPLEX_VERTICES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        ROUTING_PREFIX_OBSERVABLE_COLUMNS,
        ROUTING_PREFIX_REGION_COLUMNS,
        ROUTING_PREFIX_SUMMARY_COLUMNS,
        SPINE_PATH_CERTIFICATE,
        SPINE_PATH_EDGES,
        SPINE_PATH_JSON,
        SPINE_PATH_REPORT,
        SPINE_PATH_TABLES,
        SPINE_PATH_TRANSITIONS,
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


def validate_c985_d20_signature_boundary_spine_routing_prefix() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    routing = load_json(OUT_DIR / "signature_boundary_spine_routing_prefix.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_routing_prefix_certificate.json"
    )
    summary_csv = (OUT_DIR / "routing_prefix_summary.csv").read_text(
        encoding="utf-8"
    )
    region_csv = (OUT_DIR / "routing_prefix_region_coverage.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "routing_prefix_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_routing_prefix_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if routing != expected["signature_boundary_spine_routing_prefix"]:
        raise AssertionError("boundary spine routing prefix JSON is not reproducible")
    if summary_csv != expected["routing_prefix_summary_csv"]:
        raise AssertionError("boundary spine routing prefix summary CSV is not reproducible")
    if region_csv != expected["routing_prefix_region_coverage_csv"]:
        raise AssertionError("boundary spine routing prefix region CSV is not reproducible")
    if observable_csv != expected["routing_prefix_observables_csv"]:
        raise AssertionError("boundary spine routing prefix observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_routing_prefix_certificate"]:
        raise AssertionError("boundary spine routing prefix certificate is not reproducible")

    table_names = [
        "routing_prefix_summary_table",
        "routing_prefix_region_table",
        "routing_prefix_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"boundary spine routing prefix table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_routing_prefix@1":
        raise AssertionError("C985 d20 boundary spine routing prefix report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary spine routing prefix is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary spine routing prefix all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary spine routing prefix checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine routing prefix report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary spine routing prefix report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "spine_path_report_certified",
        "spine_path_certificate_certified",
        "cell_complex_report_certified",
        "cell_complex_certificate_certified",
        "summary_prefix_count_is_16",
        "region_coverage_rows_are_12",
        "edge_cloud_crossing_prefix_matches_expected",
        "edge_cloud_crossing_metrics_match_expected",
        "edge_cloud_predecessor_is_axis_tracking",
        "midpoint_polyline_crossing_prefix_matches_expected",
        "midpoint_polyline_crossing_metrics_match_expected",
        "edge_prefix_is_all_central_negative",
        "edge_prefix_region_bitsets_match_expected",
        "polyline_prefix_region_bitsets_match_expected",
        "edge_prefix_boundary_active_region_coverage_matches_expected",
        "polyline_prefix_boundary_active_region_coverage_matches_expected",
        "summary_table_shape_is_16_by_21",
        "region_table_shape_is_12_by_13",
        "observable_table_shape_matches_codebook",
        "spine_path_json_schema_available",
        "cell_complex_json_schema_available",
        "spine_path_tables_available",
        "cell_complex_tables_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary spine routing prefix missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("edge_cloud_crossing_prefix") != {
        "prefix_length": 8,
        "last_boundary_mask_edge_id": 11,
        "boundary_mask_edge_ids": [14, 15, 2, 6, 3, 7, 8, 11],
        "entropy_fraction_x1e12": 728568451090,
        "flux_fraction_x1e12": 777936948054,
        "axis_delta_x1e12": 141037638590,
        "residual_delta_x1e12": 144281755223,
        "bend_fraction_x1e12": 505685061554,
        "hyperbolic_length_x1e12": 228204173309,
        "central_negative_edge_count": 8,
        "high_negative_edge_count": 0,
    }:
        raise AssertionError("routing prefix edge-cloud crossing mismatch")
    if witness.get("midpoint_polyline_crossing_prefix") != {
        "prefix_length": 2,
        "last_boundary_mask_edge_id": 15,
        "boundary_mask_edge_ids": [14, 15],
        "entropy_fraction_x1e12": 262985778341,
        "flux_fraction_x1e12": 318011852725,
        "axis_travel_x1e12": 35307583361,
        "residual_travel_x1e12": 72277973546,
        "bend_fraction_x1e12": 671818556542,
        "hyperbolic_length_x1e12": 80649159853,
    }:
        raise AssertionError("routing prefix midpoint crossing mismatch")
    if witness.get("edge_cloud_crossing_predecessor") != {
        "prefix_length": 7,
        "last_boundary_mask_edge_id": 8,
        "bend_fraction_x1e12": 469550522968,
        "residual_dominant": False,
    }:
        raise AssertionError("routing prefix predecessor mismatch")
    if witness.get("edge_prefix_region_coverage") != {
        "positive_central_boundary_active_fraction_x1e12": 750000000000,
        "negative_boundary_active_fraction_x1e12": 666666666667,
        "positive_high_boundary_active_fraction_x1e12": 0,
        "touched_boundary_active_fraction_x1e12": 583333333333,
        "positive_central_carrier_bitset": 6152,
        "negative_carrier_bitset": 9088,
    }:
        raise AssertionError("routing prefix edge region coverage mismatch")
    if witness.get("polyline_prefix_region_coverage") != {
        "positive_central_boundary_active_fraction_x1e12": 500000000000,
        "negative_boundary_active_fraction_x1e12": 166666666667,
        "touched_boundary_active_fraction_x1e12": 250000000000,
        "positive_central_carrier_bitset": 6144,
        "negative_carrier_bitset": 8192,
    }:
        raise AssertionError("routing prefix polyline region coverage mismatch")

    summary_table = np.asarray(tables["routing_prefix_summary_table"], dtype=np.int64)
    region_table = np.asarray(tables["routing_prefix_region_table"], dtype=np.int64)
    observable_table = np.asarray(tables["routing_prefix_observable_table"], dtype=np.int64)

    if summary_table.shape != (16, len(ROUTING_PREFIX_SUMMARY_COLUMNS)):
        raise AssertionError("routing prefix summary table shape mismatch")
    if region_table.shape != (12, len(ROUTING_PREFIX_REGION_COLUMNS)):
        raise AssertionError("routing prefix region table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(ROUTING_PREFIX_OBSERVABLE_COLUMNS)):
        raise AssertionError("routing prefix observable table shape mismatch")
    if summary_table[7, 0] != 8 or summary_table[7, 10] != 1:
        raise AssertionError("routing prefix edge crossing table row mismatch")
    if summary_table[6, 10] != 0:
        raise AssertionError("routing prefix predecessor table row mismatch")
    if summary_table[1, 15] != 1:
        raise AssertionError("routing prefix polyline crossing table row mismatch")
    if int(region_table[:, 8].sum()) != 20:
        raise AssertionError("routing prefix region coverage total mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("routing prefix observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("spine_path_report", {}), SPINE_PATH_REPORT, "spine path report input")
    assert_file_hash(inputs.get("spine_path", {}), SPINE_PATH_JSON, "spine path JSON input")
    assert_file_hash(inputs.get("spine_path_tables", {}), SPINE_PATH_TABLES, "spine path tables input")
    assert_file_hash(
        inputs.get("spine_path_certificate", {}),
        SPINE_PATH_CERTIFICATE,
        "spine path certificate input",
    )
    assert_file_hash(inputs.get("spine_path_edges", {}), SPINE_PATH_EDGES, "spine path edge input")
    assert_file_hash(
        inputs.get("spine_path_transitions", {}),
        SPINE_PATH_TRANSITIONS,
        "spine path transition input",
    )
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex", {}), CELL_COMPLEX_JSON, "cell complex JSON input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(
        inputs.get("cell_complex_certificate", {}),
        CELL_COMPLEX_CERTIFICATE,
        "cell complex certificate input",
    )
    assert_file_hash(inputs.get("cell_complex_vertices", {}), CELL_COMPLEX_VERTICES, "cell complex vertices input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_routing_prefix_manifest@1":
        raise AssertionError("C985 d20 boundary spine routing prefix manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine routing prefix manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary spine routing prefix manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 boundary spine routing prefix missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine routing prefix index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary spine routing prefix index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_routing_prefix@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "edge_cloud_crossing_prefix": witness.get("edge_cloud_crossing_prefix"),
        "midpoint_polyline_crossing_prefix": witness.get(
            "midpoint_polyline_crossing_prefix"
        ),
        "edge_prefix_region_coverage": witness.get("edge_prefix_region_coverage"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_routing_prefix()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
