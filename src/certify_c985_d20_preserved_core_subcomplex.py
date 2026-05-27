from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_preserved_core_subcomplex import (
        BOUNDARY_EDGE_COLUMNS,
        CORE_EDGE_COLUMNS,
        CORE_NODE_COLUMNS,
        HIGH_SIGNATURE_THRESHOLD,
        INTERVAL_SHEAF_CERTIFICATE,
        INTERVAL_SHEAF_JSON,
        INTERVAL_SHEAF_REPORT,
        INTERVAL_SHEAF_TABLES,
        OUT_DIR,
        PRESERVED_INTERVAL_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_preserved_core_subcomplex import (
        BOUNDARY_EDGE_COLUMNS,
        CORE_EDGE_COLUMNS,
        CORE_NODE_COLUMNS,
        HIGH_SIGNATURE_THRESHOLD,
        INTERVAL_SHEAF_CERTIFICATE,
        INTERVAL_SHEAF_JSON,
        INTERVAL_SHEAF_REPORT,
        INTERVAL_SHEAF_TABLES,
        OUT_DIR,
        PRESERVED_INTERVAL_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH


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


def validate_c985_d20_preserved_core_subcomplex() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    preserved_core = load_json(OUT_DIR / "preserved_core_subcomplex.json")
    certificate = load_json(OUT_DIR / "preserved_core_certificate.json")
    nodes_csv = (OUT_DIR / "preserved_core_nodes.csv").read_text(encoding="utf-8")
    edges_csv = (OUT_DIR / "preserved_core_edges.csv").read_text(encoding="utf-8")
    boundary_csv = (OUT_DIR / "preserved_core_boundary_edges.csv").read_text(encoding="utf-8")
    intervals_csv = (OUT_DIR / "preserved_core_intervals.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "preserved_core_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if preserved_core != expected["preserved_core_subcomplex"]:
        raise AssertionError("d20 preserved-core subcomplex JSON is not reproducible")
    if nodes_csv != expected["preserved_core_nodes_csv"]:
        raise AssertionError("d20 preserved-core nodes CSV is not reproducible")
    if edges_csv != expected["preserved_core_edges_csv"]:
        raise AssertionError("d20 preserved-core edges CSV is not reproducible")
    if boundary_csv != expected["preserved_core_boundary_edges_csv"]:
        raise AssertionError("d20 preserved-core boundary CSV is not reproducible")
    if intervals_csv != expected["preserved_core_intervals_csv"]:
        raise AssertionError("d20 preserved-core intervals CSV is not reproducible")
    if certificate != expected["preserved_core_certificate"]:
        raise AssertionError("d20 preserved-core certificate is not reproducible")

    table_names = [
        "core_node_table",
        "core_edge_table",
        "boundary_edge_table",
        "core_interval_table",
        "core_interval_incidence",
        "core_nodes",
        "frontier_nodes",
        "boundary_band_nodes",
        "core_adjacency",
        "core_distances",
        "cut_graph_adjacency",
        "cut_graph_distances",
        "boundary_band_adjacency",
        "boundary_band_distances",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"d20 preserved-core table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_preserved_core_subcomplex@1":
        raise AssertionError("C985 d20 preserved-core report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 preserved core is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 preserved core all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 preserved-core checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 preserved-core report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 preserved-core report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "interval_sheaf_report_certified",
        "interval_sheaf_certificate_certified",
        "high_signature_threshold_matches_interval_sheaf",
        "full_high_interval_count_is_46",
        "core_node_count_is_12",
        "full_high_nodes_equal_interval_union",
        "full_high_endpoints_equal_core_nodes",
        "core_node_table_shape_is_12_by_17",
        "core_edge_count_is_31",
        "core_edge_table_shape_is_31_by_10",
        "core_adjacency_shape_is_12_by_12",
        "core_graph_connected",
        "core_graph_diameter_is_3",
        "core_graph_radius_is_2",
        "core_centers_are_19_34_42_44",
        "core_gromov_delta_is_1",
        "core_delta_witness_is_10_13_32_41",
        "core_distance_histogram_matches",
        "core_induced_metric_is_isometric_for_all_78_core_pairs",
        "geodesically_preserved_core_pair_count_is_46",
        "escaping_core_pair_count_is_32",
        "core_boundary_node_count_is_12",
        "core_has_no_interior_nodes",
        "frontier_node_count_is_40",
        "boundary_edge_count_is_108",
        "boundary_edge_table_shape_is_108_by_9",
        "complement_node_count_is_44",
        "complement_connected",
        "exterior_distance_two_nodes_are_0_21_46_55",
        "cut_graph_connected",
        "cut_graph_node_count_is_52",
        "cut_graph_edge_count_is_108",
        "cut_graph_diameter_is_6",
        "cut_graph_gromov_delta_is_2",
        "boundary_band_connected",
        "boundary_band_node_count_is_52",
        "boundary_band_edge_count_is_295",
        "boundary_band_diameter_is_3",
        "boundary_band_gromov_delta_is_1",
        "core_poincare_diameter_pair_is_10_44",
        "core_poincare_diameter_distance_is_0_3697551314",
        "core_interval_incidence_shape_is_46_by_12",
        "core_interval_table_shape_is_46_by_8",
        "core_interval_incidence_counts_match",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 preserved-core missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("high_signature_threshold") != HIGH_SIGNATURE_THRESHOLD:
        raise AssertionError("preserved-core high-signature threshold mismatch")
    if witness.get("full_high_interval_count") != 46:
        raise AssertionError("preserved-core full-high interval count mismatch")
    if witness.get("core_node_count") != 12:
        raise AssertionError("preserved-core node count mismatch")
    if witness.get("core_node_ids") != [10, 13, 17, 19, 28, 32, 34, 38, 41, 42, 43, 44]:
        raise AssertionError("preserved-core node ids mismatch")
    if witness.get("core_edge_count") != 31:
        raise AssertionError("preserved-core edge count mismatch")
    if witness.get("core_component_count") != 1:
        raise AssertionError("preserved-core component count mismatch")
    if witness.get("core_graph_diameter") != 3:
        raise AssertionError("preserved-core diameter mismatch")
    if witness.get("core_graph_radius") != 2:
        raise AssertionError("preserved-core radius mismatch")
    if witness.get("core_center_node_ids") != [19, 34, 42, 44]:
        raise AssertionError("preserved-core centers mismatch")
    if witness.get("core_gromov_delta_twice") != 2:
        raise AssertionError("preserved-core delta mismatch")
    if witness.get("core_gromov_delta_witness_nodes") != [10, 13, 32, 41]:
        raise AssertionError("preserved-core delta witness mismatch")
    if witness.get("core_pair_count") != 78 or witness.get("core_pair_isometric_count") != 78:
        raise AssertionError("preserved-core isometry witness mismatch")
    if witness.get("geodesically_preserved_core_pair_count") != 46:
        raise AssertionError("preserved-core geodesically preserved pair count mismatch")
    if witness.get("escaping_core_pair_count") != 32:
        raise AssertionError("preserved-core escaping pair count mismatch")
    if witness.get("frontier_node_count") != 40:
        raise AssertionError("preserved-core frontier count mismatch")
    if witness.get("boundary_edge_count") != 108:
        raise AssertionError("preserved-core boundary edge count mismatch")
    if witness.get("cut_graph_diameter") != 6 or witness.get("cut_graph_gromov_delta_twice") != 4:
        raise AssertionError("preserved-core cut graph witness mismatch")
    if witness.get("boundary_band_edge_count") != 295:
        raise AssertionError("preserved-core boundary band edge count mismatch")
    if witness.get("boundary_band_diameter") != 3:
        raise AssertionError("preserved-core boundary band diameter mismatch")
    if witness.get("boundary_band_gromov_delta_twice") != 2:
        raise AssertionError("preserved-core boundary band delta mismatch")
    if witness.get("exterior_distance_two_node_ids") != [0, 21, 46, 55]:
        raise AssertionError("preserved-core exterior distance-two nodes mismatch")
    diameter_pair = witness.get("core_poincare_diameter_pair", {})
    if [diameter_pair.get("source_node_id"), diameter_pair.get("target_node_id")] != [10, 44]:
        raise AssertionError("preserved-core Poincare diameter pair mismatch")
    if diameter_pair.get("endpoint_poincare_distance") != 0.3697551314:
        raise AssertionError("preserved-core Poincare diameter distance mismatch")

    core_node_table = np.asarray(tables["core_node_table"], dtype=np.int64)
    core_edge_table = np.asarray(tables["core_edge_table"], dtype=np.int64)
    boundary_edge_table = np.asarray(tables["boundary_edge_table"], dtype=np.int64)
    core_interval_table = np.asarray(tables["core_interval_table"], dtype=np.int64)
    core_interval_incidence = np.asarray(tables["core_interval_incidence"], dtype=np.int8)
    core_adjacency = np.asarray(tables["core_adjacency"], dtype=np.int8)
    core_distances = np.asarray(tables["core_distances"], dtype=np.int64)
    cut_graph_adjacency = np.asarray(tables["cut_graph_adjacency"], dtype=np.int8)
    boundary_band_adjacency = np.asarray(tables["boundary_band_adjacency"], dtype=np.int8)

    if core_node_table.shape != (12, len(CORE_NODE_COLUMNS)):
        raise AssertionError("preserved-core node table shape mismatch")
    if core_edge_table.shape != (31, len(CORE_EDGE_COLUMNS)):
        raise AssertionError("preserved-core edge table shape mismatch")
    if boundary_edge_table.shape != (108, len(BOUNDARY_EDGE_COLUMNS)):
        raise AssertionError("preserved-core boundary edge table shape mismatch")
    if core_interval_table.shape != (46, len(PRESERVED_INTERVAL_COLUMNS)):
        raise AssertionError("preserved-core interval table shape mismatch")
    if core_interval_incidence.shape != (46, 12):
        raise AssertionError("preserved-core interval incidence shape mismatch")
    if not np.array_equal(np.sum(core_interval_incidence, axis=1), core_interval_table[:, 4]):
        raise AssertionError("preserved-core interval incidence count mismatch")
    if not np.array_equal(core_adjacency, core_adjacency.T):
        raise AssertionError("preserved-core adjacency is not symmetric")
    if not np.array_equal(cut_graph_adjacency, cut_graph_adjacency.T):
        raise AssertionError("preserved-core cut graph adjacency is not symmetric")
    if not np.array_equal(boundary_band_adjacency, boundary_band_adjacency.T):
        raise AssertionError("preserved-core boundary band adjacency is not symmetric")
    if int(np.max(core_distances)) != 3:
        raise AssertionError("preserved-core distance table diameter mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("rewrite_complex_report", {}),
        REWRITE_COMPLEX_REPORT,
        "rewrite complex report input",
    )
    assert_file_hash(inputs.get("rewrite_complex", {}), REWRITE_COMPLEX_JSON, "rewrite complex input")
    assert_file_hash(
        inputs.get("rewrite_complex_tables", {}),
        REWRITE_COMPLEX_TABLES,
        "rewrite complex tables input",
    )
    assert_file_hash(
        inputs.get("rewrite_complex_certificate", {}),
        REWRITE_COMPLEX_CERTIFICATE,
        "rewrite complex certificate input",
    )
    assert_file_hash(
        inputs.get("interval_sheaf_report", {}),
        INTERVAL_SHEAF_REPORT,
        "interval sheaf report input",
    )
    assert_file_hash(inputs.get("interval_sheaf", {}), INTERVAL_SHEAF_JSON, "interval sheaf input")
    assert_file_hash(
        inputs.get("interval_sheaf_tables", {}),
        INTERVAL_SHEAF_TABLES,
        "interval sheaf tables input",
    )
    assert_file_hash(
        inputs.get("interval_sheaf_certificate", {}),
        INTERVAL_SHEAF_CERTIFICATE,
        "interval sheaf certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_preserved_core_subcomplex_manifest@1":
        raise AssertionError("C985 d20 preserved-core manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 preserved-core manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 preserved-core manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 preserved-core missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 preserved-core index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 preserved-core index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_preserved_core_subcomplex@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "core_node_count": witness.get("core_node_count"),
        "core_node_ids": witness.get("core_node_ids"),
        "full_high_interval_count": witness.get("full_high_interval_count"),
        "core_edge_count": witness.get("core_edge_count"),
        "core_graph_diameter": witness.get("core_graph_diameter"),
        "core_gromov_delta": witness.get("core_gromov_delta"),
        "core_pair_isometric_count": witness.get("core_pair_isometric_count"),
        "geodesically_preserved_core_pair_count": witness.get(
            "geodesically_preserved_core_pair_count"
        ),
        "escaping_core_pair_count": witness.get("escaping_core_pair_count"),
        "frontier_node_count": witness.get("frontier_node_count"),
        "boundary_edge_count": witness.get("boundary_edge_count"),
        "cut_graph_gromov_delta": witness.get("cut_graph_gromov_delta"),
        "boundary_band_edge_count": witness.get("boundary_band_edge_count"),
        "boundary_band_gromov_delta": witness.get("boundary_band_gromov_delta"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_preserved_core_subcomplex()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
