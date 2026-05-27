from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_residual_cell_complex import (
        EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_JSON,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_SIGNATURE_CSV,
        RESIDUAL_CHART_TABLES,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        SPECTRAL_MASK_SUMMARY,
        STATUS,
        SUMMARY_COLUMNS,
        THEOREM_ID,
        VERTEX_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_residual_cell_complex import (
        EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_JSON,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_SIGNATURE_CSV,
        RESIDUAL_CHART_TABLES,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        SPECTRAL_MASK_SUMMARY,
        STATUS,
        SUMMARY_COLUMNS,
        THEOREM_ID,
        VERTEX_COLUMNS,
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


def validate_c985_d20_signature_residual_cell_complex() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    complex_json = load_json(OUT_DIR / "signature_residual_cell_complex.json")
    certificate = load_json(OUT_DIR / "signature_residual_cell_complex_certificate.json")
    vertex_csv = (OUT_DIR / "carrier_region_vertices.csv").read_text(encoding="utf-8")
    edge_csv = (OUT_DIR / "carrier_region_edges.csv").read_text(encoding="utf-8")
    summary_csv = (OUT_DIR / "region_boundary_summary.csv").read_text(encoding="utf-8")
    observable_csv = (OUT_DIR / "cell_complex_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(OUT_DIR / "signature_residual_cell_complex_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if complex_json != expected["signature_residual_cell_complex"]:
        raise AssertionError("signature residual cell complex JSON is not reproducible")
    if vertex_csv != expected["carrier_region_vertices_csv"]:
        raise AssertionError("carrier region vertex CSV is not reproducible")
    if edge_csv != expected["carrier_region_edges_csv"]:
        raise AssertionError("carrier region edge CSV is not reproducible")
    if summary_csv != expected["region_boundary_summary_csv"]:
        raise AssertionError("region boundary summary CSV is not reproducible")
    if observable_csv != expected["cell_complex_observables_csv"]:
        raise AssertionError("cell complex observable CSV is not reproducible")
    if certificate != expected["signature_residual_cell_complex_certificate"]:
        raise AssertionError("signature residual cell complex certificate is not reproducible")

    table_names = [
        "carrier_region_vertex_table",
        "carrier_region_edge_table",
        "region_boundary_summary_table",
        "cell_complex_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature residual cell complex table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_residual_cell_complex@1":
        raise AssertionError("C985 d20 signature residual cell complex report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature residual cell complex is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature residual cell complex all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature residual cell complex checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature residual cell complex report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature residual cell complex report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "residual_chart_report_certified",
        "residual_chart_certificate_certified",
        "spectral_cut_report_certified",
        "spectral_cut_certificate_certified",
        "signature_subboundary_report_certified",
        "signature_subboundary_certificate_certified",
        "carrier_vertex_count_is_14",
        "carrier_edge_count_is_44",
        "region_vertex_sets_match_residual_chart",
        "region_masses_match_residual_chart",
        "edge_partition_counts_match_expected",
        "positive_negative_boundary_count_matches_spectral_cut",
        "boundary_degrees_match_spectral_cut",
        "boundary_edge_set_matches_spectral_cut",
        "positive_region_is_connected",
        "negative_region_is_connected",
        "region_adjacency_graph_is_complete_triangle",
        "vertex_table_shape_is_14_by_19",
        "edge_table_shape_is_44_by_13",
        "summary_table_shape_is_4_by_8",
        "observable_table_shape_matches_codebook",
        "residual_chart_tables_available",
        "spectral_cut_tables_available",
        "signature_subboundary_tables_available",
        "residual_chart_json_schema_available",
        "spectral_cut_json_schema_available",
        "signature_subboundary_json_schema_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 signature residual cell complex missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("carrier_vertex_count") != 14:
        raise AssertionError("signature residual cell complex vertex count mismatch")
    if witness.get("carrier_edge_count") != 44:
        raise AssertionError("signature residual cell complex edge count mismatch")
    if witness.get("high_cap_mask_class_ids") != [0, 1]:
        raise AssertionError("signature residual cell complex high ids mismatch")
    if witness.get("central_gate_mask_class_ids") != [2, 3, 10, 11, 12]:
        raise AssertionError("signature residual cell complex central ids mismatch")
    if witness.get("negative_region_mask_class_ids") != [4, 5, 6, 7, 8, 9, 13]:
        raise AssertionError("signature residual cell complex negative ids mismatch")
    if witness.get("positive_region_mask_class_ids") != [0, 1, 2, 3, 10, 11, 12]:
        raise AssertionError("signature residual cell complex positive ids mismatch")
    if witness.get("region_signature_counts") != {
        "high_cap": 24,
        "central_gate": 97,
        "negative_region": 100,
    }:
        raise AssertionError("signature residual cell complex region signature counts mismatch")
    if witness.get("region_stationary_masses_x1e12") != {
        "high_cap": 10418982028,
        "central_gate": 615688126181,
        "negative_region": 373892891791,
    }:
        raise AssertionError("signature residual cell complex region masses mismatch")
    if witness.get("edge_partition_counts") != {
        "high_central": 4,
        "high_negative": 2,
        "central_negative": 14,
        "central_central": 10,
        "negative_negative": 14,
        "high_high": 0,
    }:
        raise AssertionError("signature residual cell complex edge partition mismatch")
    if witness.get("positive_negative_boundary_edge_count") != 16:
        raise AssertionError("signature residual cell complex boundary count mismatch")
    if witness.get("spectral_mask_cut_edge_count") != 16:
        raise AssertionError("signature residual cell complex spectral cut count mismatch")
    if witness.get("boundary_degree_l1_delta") != 0:
        raise AssertionError("signature residual cell complex boundary degree mismatch")
    if witness.get("spectral_boundary_symmetric_difference_count") != 0:
        raise AssertionError("signature residual cell complex boundary set mismatch")
    if witness.get("positive_region_component_count") != 1:
        raise AssertionError("signature residual cell complex positive component mismatch")
    if witness.get("negative_region_component_count") != 1:
        raise AssertionError("signature residual cell complex negative component mismatch")
    if witness.get("region_adjacency_pair_count") != 3:
        raise AssertionError("signature residual cell complex region adjacency mismatch")

    vertex_table = np.asarray(tables["carrier_region_vertex_table"], dtype=np.int64)
    edge_table = np.asarray(tables["carrier_region_edge_table"], dtype=np.int64)
    summary_table = np.asarray(tables["region_boundary_summary_table"], dtype=np.int64)
    observable_table = np.asarray(tables["cell_complex_observable_table"], dtype=np.int64)

    if vertex_table.shape != (14, len(VERTEX_COLUMNS)):
        raise AssertionError("signature residual cell complex vertex table shape mismatch")
    if edge_table.shape != (44, len(EDGE_COLUMNS)):
        raise AssertionError("signature residual cell complex edge table shape mismatch")
    if summary_table.shape != (4, len(SUMMARY_COLUMNS)):
        raise AssertionError("signature residual cell complex summary table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("signature residual cell complex observable table shape mismatch")
    if vertex_table[:, 0].tolist() != list(range(14)):
        raise AssertionError("signature residual cell complex vertex order mismatch")
    if int(edge_table[:, 9].sum()) != 16:
        raise AssertionError("signature residual cell complex edge boundary column mismatch")
    if int(edge_table[:, 10].sum()) != 4:
        raise AssertionError("signature residual cell complex internal positive boundary mismatch")
    if int(vertex_table[:, 8].sum()) != 32:
        raise AssertionError("signature residual cell complex computed boundary degree sum mismatch")
    if not np.array_equal(vertex_table[:, 8], vertex_table[:, 9]):
        raise AssertionError("signature residual cell complex boundary degree columns differ")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("signature residual cell complex observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("residual_chart_report", {}), RESIDUAL_CHART_REPORT, "residual chart report input")
    assert_file_hash(inputs.get("residual_chart", {}), RESIDUAL_CHART_JSON, "residual chart JSON input")
    assert_file_hash(inputs.get("residual_chart_tables", {}), RESIDUAL_CHART_TABLES, "residual chart tables input")
    assert_file_hash(
        inputs.get("residual_chart_certificate", {}),
        RESIDUAL_CHART_CERTIFICATE,
        "residual chart certificate input",
    )
    assert_file_hash(
        inputs.get("residual_chart_carrier_csv", {}),
        RESIDUAL_CHART_CARRIER_CSV,
        "residual chart carrier CSV input",
    )
    assert_file_hash(
        inputs.get("residual_chart_signature_csv", {}),
        RESIDUAL_CHART_SIGNATURE_CSV,
        "residual chart signature CSV input",
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_residual_cell_complex_manifest@1":
        raise AssertionError("C985 d20 signature residual cell complex manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature residual cell complex manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature residual cell complex manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature residual cell complex missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature residual cell complex index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature residual cell complex index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_residual_cell_complex@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "regions": {
            "high_cap": witness.get("high_cap_mask_class_ids"),
            "central_gate": witness.get("central_gate_mask_class_ids"),
            "negative": witness.get("negative_region_mask_class_ids"),
        },
        "edge_partition_counts": witness.get("edge_partition_counts"),
        "positive_negative_boundary_edge_count": witness.get(
            "positive_negative_boundary_edge_count"
        ),
        "spectral_mask_cut_edge_count": witness.get("spectral_mask_cut_edge_count"),
        "boundary_degree_l1_delta": witness.get("boundary_degree_l1_delta"),
        "spectral_boundary_symmetric_difference_count": witness.get(
            "spectral_boundary_symmetric_difference_count"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_residual_cell_complex()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
