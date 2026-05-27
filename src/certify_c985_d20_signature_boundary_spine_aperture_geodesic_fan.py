from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_geodesic_fan import (
        FAN_EDGE_COLUMNS,
        FAN_NODE_COLUMNS,
        FAN_OBSERVABLE_COLUMNS,
        GEODESIC_PATH_COLUMNS,
        LANGUAGE_APERTURE_CSV,
        LANGUAGE_GRAPH_CERTIFICATE,
        LANGUAGE_GRAPH_EDGE_CSV,
        LANGUAGE_GRAPH_JSON,
        LANGUAGE_GRAPH_NODE_CSV,
        LANGUAGE_GRAPH_REPORT,
        LANGUAGE_GRAPH_TABLES,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESTORATION_SUMMARY_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGE_CSV,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_NODE_CSV,
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
    from derive_c985_d20_signature_boundary_spine_aperture_geodesic_fan import (
        FAN_EDGE_COLUMNS,
        FAN_NODE_COLUMNS,
        FAN_OBSERVABLE_COLUMNS,
        GEODESIC_PATH_COLUMNS,
        LANGUAGE_APERTURE_CSV,
        LANGUAGE_GRAPH_CERTIFICATE,
        LANGUAGE_GRAPH_EDGE_CSV,
        LANGUAGE_GRAPH_JSON,
        LANGUAGE_GRAPH_NODE_CSV,
        LANGUAGE_GRAPH_REPORT,
        LANGUAGE_GRAPH_TABLES,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESTORATION_SUMMARY_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGE_CSV,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_NODE_CSV,
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


def validate_c985_d20_signature_boundary_spine_aperture_geodesic_fan() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    geodesic_fan = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan.json"
    )
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan_certificate.json"
    )
    nodes_csv = (OUT_DIR / "aperture_geodesic_fan_nodes.csv").read_text(
        encoding="utf-8"
    )
    edges_csv = (OUT_DIR / "aperture_geodesic_fan_edges.csv").read_text(
        encoding="utf-8"
    )
    paths_csv = (OUT_DIR / "aperture_geodesic_paths.csv").read_text(
        encoding="utf-8"
    )
    summary_csv = (OUT_DIR / "aperture_restoration_summary.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "aperture_geodesic_fan_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if geodesic_fan != expected["signature_boundary_spine_aperture_geodesic_fan"]:
        raise AssertionError("aperture geodesic fan JSON is not reproducible")
    if nodes_csv != expected["aperture_geodesic_fan_nodes_csv"]:
        raise AssertionError("aperture geodesic fan node CSV is not reproducible")
    if edges_csv != expected["aperture_geodesic_fan_edges_csv"]:
        raise AssertionError("aperture geodesic fan edge CSV is not reproducible")
    if paths_csv != expected["aperture_geodesic_paths_csv"]:
        raise AssertionError("aperture geodesic path CSV is not reproducible")
    if summary_csv != expected["aperture_restoration_summary_csv"]:
        raise AssertionError("aperture restoration summary CSV is not reproducible")
    if observables_csv != expected["aperture_geodesic_fan_observables_csv"]:
        raise AssertionError("aperture geodesic observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_aperture_geodesic_fan_certificate"]:
        raise AssertionError("aperture geodesic fan certificate is not reproducible")

    table_names = [
        "fan_node_table",
        "fan_edge_table",
        "geodesic_path_table",
        "restoration_summary_table",
        "fan_adjacency",
        "fan_distances",
        "fan_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"aperture geodesic fan table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_geodesic_fan@1":
        raise AssertionError("C985 d20 aperture geodesic fan report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 aperture geodesic fan is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 aperture geodesic fan all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 aperture geodesic fan checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture geodesic fan report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 aperture geodesic fan report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "language_graph_report_certified",
        "language_graph_certificate_certified",
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "language_graph_schema_available",
        "rewrite_complex_schema_available",
        "language_graph_tables_available",
        "rewrite_complex_tables_available",
        "language_node_table_shape_is_8_by_14",
        "language_edge_table_shape_is_7_by_10",
        "language_aperture_table_shape_is_8_by_9",
        "rewrite_node_table_shape_is_56_by_17",
        "rewrite_edge_table_shape_is_315_by_13",
        "language_boundary_endpoints_match_expected",
        "language_aperture_node_matches_expected",
        "aperture_word_is_x2_x4_x5",
        "boundary_endpoints_are_ambient_distance_2",
        "geodesic_paths_match_expected",
        "geodesic_path_count_is_6",
        "fan_node_count_is_9",
        "fan_edge_count_is_12",
        "all_geodesic_paths_have_length_2",
        "all_fan_edges_are_rewrite_complex_edges",
        "all_paths_restore_x2_and_x4_once",
        "x2_first_and_x4_first_paths_are_balanced",
        "full_sector_intermediate_path_count_is_2",
        "high_signature_intermediate_path_count_is_1",
        "strict_full_sector_high_signature_path_count_is_1",
        "strict_path_is_48_42_44",
        "intermediate_signature_range_is_134_183",
        "fan_graph_connected",
        "fan_graph_diameter_is_4",
        "fan_graph_radius_is_2",
        "fan_gromov_delta_is_1",
        "fan_delta_witness_nodes_match_expected",
        "fan_degree_histogram_matches_expected",
        "fan_node_table_shape_is_9_by_17",
        "fan_edge_table_shape_is_12_by_12",
        "geodesic_path_table_shape_is_6_by_17",
        "restoration_summary_table_shape_is_2_by_10",
        "fan_observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 aperture geodesic fan missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("boundary_endpoint_node_ids") != [20, 48]:
        raise AssertionError("aperture geodesic fan boundary endpoints mismatch")
    if witness.get("aperture_node", {}).get("node_id") != 44:
        raise AssertionError("aperture geodesic fan aperture node mismatch")
    if witness.get("aperture_node", {}).get("canonical_word") != "x2 x4 x5":
        raise AssertionError("aperture geodesic fan aperture word mismatch")
    if witness.get("geodesic_path_node_triples") != [
        [20, 14, 44],
        [20, 19, 44],
        [20, 45, 44],
        [20, 54, 44],
        [48, 42, 44],
        [48, 50, 44],
    ]:
        raise AssertionError("aperture geodesic path triples mismatch")
    if witness.get("fan_node_ids") != [20, 48, 14, 19, 42, 45, 50, 54, 44]:
        raise AssertionError("aperture geodesic fan node order mismatch")
    if witness.get("fan_graph_diameter") != 4 or witness.get("fan_graph_radius") != 2:
        raise AssertionError("aperture geodesic fan diameter/radius mismatch")
    if witness.get("fan_gromov_delta") != 1.0 or witness.get("fan_gromov_delta_twice") != 2:
        raise AssertionError("aperture geodesic fan Gromov delta mismatch")
    if witness.get("fan_delta_witness_node_ids") != [20, 48, 14, 19]:
        raise AssertionError("aperture geodesic fan delta witness mismatch")
    if witness.get("strict_full_sector_high_signature_paths") != [[48, 42, 44]]:
        raise AssertionError("aperture geodesic fan strict path mismatch")
    if witness.get("full_sector_intermediate_path_count") != 2:
        raise AssertionError("aperture geodesic fan full-sector path count mismatch")
    if witness.get("high_signature_intermediate_path_count") != 1:
        raise AssertionError("aperture geodesic fan high-signature path count mismatch")
    if witness.get("x2_first_path_count") != 3 or witness.get("x4_first_path_count") != 3:
        raise AssertionError("aperture geodesic fan restoration order count mismatch")
    if witness.get("intermediate_signature_range") != {"min": 134, "max": 183}:
        raise AssertionError("aperture geodesic fan intermediate signature range mismatch")

    fan_node_table = np.asarray(tables["fan_node_table"], dtype=np.int64)
    fan_edge_table = np.asarray(tables["fan_edge_table"], dtype=np.int64)
    path_table = np.asarray(tables["geodesic_path_table"], dtype=np.int64)
    summary_table = np.asarray(tables["restoration_summary_table"], dtype=np.int64)
    adjacency = np.asarray(tables["fan_adjacency"], dtype=np.int8)
    distances = np.asarray(tables["fan_distances"], dtype=np.int64)
    observable_table = np.asarray(tables["fan_observable_table"], dtype=np.int64)

    if fan_node_table.shape != (9, len(FAN_NODE_COLUMNS)):
        raise AssertionError("aperture geodesic fan node table shape mismatch")
    if fan_edge_table.shape != (12, len(FAN_EDGE_COLUMNS)):
        raise AssertionError("aperture geodesic fan edge table shape mismatch")
    if path_table.shape != (6, len(GEODESIC_PATH_COLUMNS)):
        raise AssertionError("aperture geodesic fan path table shape mismatch")
    if summary_table.shape != (2, len(RESTORATION_SUMMARY_COLUMNS)):
        raise AssertionError("aperture restoration summary table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(FAN_OBSERVABLE_COLUMNS)):
        raise AssertionError("aperture geodesic fan observable table shape mismatch")
    if adjacency.shape != (9, 9) or not np.array_equal(adjacency, adjacency.T):
        raise AssertionError("aperture geodesic fan adjacency shape/symmetry mismatch")
    if int(np.sum(adjacency) // 2) != 12:
        raise AssertionError("aperture geodesic fan adjacency edge count mismatch")
    if distances.shape != (9, 9) or int(np.max(distances)) != 4:
        raise AssertionError("aperture geodesic fan distance table mismatch")
    if path_table[:, 1:4].tolist() != [
        [20, 14, 44],
        [20, 19, 44],
        [20, 45, 44],
        [20, 54, 44],
        [48, 42, 44],
        [48, 50, 44],
    ]:
        raise AssertionError("aperture geodesic fan path table triples mismatch")
    if path_table[:, 16].tolist() != [0, 0, 0, 0, 1, 0]:
        raise AssertionError("aperture geodesic fan strict path flags mismatch")
    if summary_table.tolist() != [
        [20, 4, 1, 0, 0, 2, 2, 134, 173, -1],
        [48, 2, 1, 1, 1, 1, 1, 146, 183, 4],
    ]:
        raise AssertionError("aperture restoration summary table mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("language_graph_report", {}),
        LANGUAGE_GRAPH_REPORT,
        "language graph report input",
    )
    assert_file_hash(inputs.get("language_graph", {}), LANGUAGE_GRAPH_JSON, "language graph JSON input")
    assert_file_hash(inputs.get("language_graph_nodes", {}), LANGUAGE_GRAPH_NODE_CSV, "language graph node input")
    assert_file_hash(inputs.get("language_graph_edges", {}), LANGUAGE_GRAPH_EDGE_CSV, "language graph edge input")
    assert_file_hash(
        inputs.get("language_aperture_distances", {}),
        LANGUAGE_APERTURE_CSV,
        "language aperture distance input",
    )
    assert_file_hash(inputs.get("language_graph_tables", {}), LANGUAGE_GRAPH_TABLES, "language graph table input")
    assert_file_hash(
        inputs.get("language_graph_certificate", {}),
        LANGUAGE_GRAPH_CERTIFICATE,
        "language graph certificate input",
    )
    assert_file_hash(
        inputs.get("rewrite_complex_report", {}),
        REWRITE_COMPLEX_REPORT,
        "rewrite complex report input",
    )
    assert_file_hash(inputs.get("rewrite_complex", {}), REWRITE_COMPLEX_JSON, "rewrite complex JSON input")
    assert_file_hash(inputs.get("rewrite_complex_nodes", {}), REWRITE_COMPLEX_NODE_CSV, "rewrite complex node input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGE_CSV, "rewrite complex edge input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex table input")
    assert_file_hash(
        inputs.get("rewrite_complex_certificate", {}),
        REWRITE_COMPLEX_CERTIFICATE,
        "rewrite complex certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_geodesic_fan_manifest@1":
        raise AssertionError("C985 d20 aperture geodesic fan manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture geodesic fan manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 aperture geodesic fan manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 aperture geodesic fan missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture geodesic fan index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 aperture geodesic fan index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_geodesic_fan@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "geodesic_path_count": witness.get("geodesic_path_count"),
        "fan_graph_diameter": witness.get("fan_graph_diameter"),
        "fan_gromov_delta": witness.get("fan_gromov_delta"),
        "strict_full_sector_high_signature_paths": witness.get(
            "strict_full_sector_high_signature_paths"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_geodesic_fan()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
