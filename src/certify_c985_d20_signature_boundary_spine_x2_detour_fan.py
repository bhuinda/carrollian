from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DETOUR_EDGE_COLUMNS,
        DETOUR_NODE_COLUMNS,
        DETOUR_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RETURN_PATH_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        THEOREM_ID,
        X2_SPLICE_CERTIFICATE,
        X2_SPLICE_JSON,
        X2_SPLICE_NEAR_MISSES,
        X2_SPLICE_REPORT,
        X2_SPLICE_TABLES,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DETOUR_EDGE_COLUMNS,
        DETOUR_NODE_COLUMNS,
        DETOUR_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RETURN_PATH_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        THEOREM_ID,
        X2_SPLICE_CERTIFICATE,
        X2_SPLICE_JSON,
        X2_SPLICE_NEAR_MISSES,
        X2_SPLICE_REPORT,
        X2_SPLICE_TABLES,
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


def validate_c985_d20_signature_boundary_spine_x2_detour_fan() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    detour_fan = load_json(OUT_DIR / "signature_boundary_spine_x2_detour_fan.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_x2_detour_fan_certificate.json"
    )
    nodes_csv = (OUT_DIR / "x2_detour_nodes.csv").read_text(encoding="utf-8")
    edges_csv = (OUT_DIR / "x2_detour_edges.csv").read_text(encoding="utf-8")
    returns_csv = (OUT_DIR / "x2_detour_return_paths.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "x2_detour_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_x2_detour_fan_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if detour_fan != expected["signature_boundary_spine_x2_detour_fan"]:
        raise AssertionError("x2 detour fan JSON is not reproducible")
    if nodes_csv != expected["x2_detour_nodes_csv"]:
        raise AssertionError("x2 detour node CSV is not reproducible")
    if edges_csv != expected["x2_detour_edges_csv"]:
        raise AssertionError("x2 detour edge CSV is not reproducible")
    if returns_csv != expected["x2_detour_return_paths_csv"]:
        raise AssertionError("x2 detour return path CSV is not reproducible")
    if observables_csv != expected["x2_detour_observables_csv"]:
        raise AssertionError("x2 detour observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_x2_detour_fan_certificate"]:
        raise AssertionError("x2 detour fan certificate is not reproducible")

    table_names = [
        "node_table",
        "edge_table",
        "return_path_table",
        "adjacency",
        "distances",
        "observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"x2 detour fan table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_detour_fan@1":
        raise AssertionError("C985 d20 x2 detour fan report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 x2 detour fan is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 x2 detour fan all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 x2 detour fan checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 detour fan report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 x2 detour fan report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "x2_splice_report_certified",
        "x2_splice_certificate_certified",
        "cell_complex_report_certified",
        "cell_complex_certificate_certified",
        "x2_splice_schema_available",
        "cell_complex_schema_available",
        "x2_splice_near_miss_table_shape_is_10_by_14",
        "cell_complex_edge_table_shape_is_44_by_13",
        "origin_carrier_is_12",
        "slot_negative_carrier_is_4",
        "incident_x2_detour_edges_match_expected",
        "detour_target_carriers_match_expected",
        "detour_node_count_is_10",
        "detour_edge_count_is_13",
        "x2_detour_edge_count_is_4",
        "boundary_return_edge_count_is_8",
        "return_path_count_is_8",
        "clean_single_x2_return_path_count_is_2",
        "mixed_x2_return_path_count_is_6",
        "dead_end_x2_detour_edge_is_9",
        "clean_single_x2_return_paths_use_edge_14",
        "mixed_x2_return_paths_use_edges_39_41",
        "return_negative_carriers_match_expected",
        "detour_graph_connected",
        "detour_graph_diameter_is_3",
        "detour_graph_radius_is_2",
        "detour_gromov_delta_is_1",
        "detour_delta_witness_carriers_match_expected",
        "all_return_paths_realize_node42_context",
        "node_table_shape_is_10_by_12",
        "edge_table_shape_is_13_by_15",
        "return_path_table_shape_is_8_by_13",
        "observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 x2 detour fan missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("origin_carrier_id") != 12:
        raise AssertionError("x2 detour fan origin carrier mismatch")
    if witness.get("slot_negative_carrier_id") != 4:
        raise AssertionError("x2 detour fan slot negative carrier mismatch")
    if witness.get("x2_detour_edge_ids") != [9, 14, 39, 41]:
        raise AssertionError("x2 detour fan edge ids mismatch")
    if witness.get("x2_detour_target_ids") != [2, 3, 10, 11]:
        raise AssertionError("x2 detour fan target ids mismatch")
    if witness.get("return_negative_carrier_ids") != [7, 8, 9, 13]:
        raise AssertionError("x2 detour fan return negative ids mismatch")
    if witness.get("return_path_count") != 8:
        raise AssertionError("x2 detour fan return path count mismatch")
    if witness.get("clean_single_x2_return_paths") != [[14, 10], [14, 11]]:
        raise AssertionError("x2 detour fan clean return paths mismatch")
    if witness.get("mixed_x2_return_paths") != [
        [39, 34],
        [39, 40],
        [41, 28],
        [41, 31],
        [41, 35],
        [41, 42],
    ]:
        raise AssertionError("x2 detour fan mixed return paths mismatch")
    if witness.get("dead_end_x2_detour_edge_ids") != [9]:
        raise AssertionError("x2 detour fan dead-end mismatch")
    if witness.get("detour_graph_diameter") != 3 or witness.get("detour_graph_radius") != 2:
        raise AssertionError("x2 detour fan diameter/radius mismatch")
    if witness.get("detour_gromov_delta") != 1.0 or witness.get("detour_gromov_delta_twice") != 2:
        raise AssertionError("x2 detour fan delta mismatch")
    if witness.get("detour_delta_witness_carrier_ids") != [12, 3, 11, 7]:
        raise AssertionError("x2 detour fan delta witness mismatch")

    node_table = np.asarray(tables["node_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    return_path_table = np.asarray(tables["return_path_table"], dtype=np.int64)
    adjacency = np.asarray(tables["adjacency"], dtype=np.int8)
    distances = np.asarray(tables["distances"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if node_table.shape != (10, len(DETOUR_NODE_COLUMNS)):
        raise AssertionError("x2 detour node table shape mismatch")
    if edge_table.shape != (13, len(DETOUR_EDGE_COLUMNS)):
        raise AssertionError("x2 detour edge table shape mismatch")
    if return_path_table.shape != (8, len(RETURN_PATH_COLUMNS)):
        raise AssertionError("x2 detour return path table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(DETOUR_OBSERVABLE_COLUMNS)):
        raise AssertionError("x2 detour observable table shape mismatch")
    if adjacency.shape != (10, 10) or not np.array_equal(adjacency, adjacency.T):
        raise AssertionError("x2 detour adjacency shape/symmetry mismatch")
    if int(np.sum(adjacency) // 2) != 13:
        raise AssertionError("x2 detour adjacency edge count mismatch")
    if distances.shape != (10, 10) or int(np.max(distances)) != 3:
        raise AssertionError("x2 detour distance table mismatch")
    if edge_table[:, 1].tolist() != [18, 9, 14, 39, 41, 10, 11, 34, 40, 28, 31, 35, 42]:
        raise AssertionError("x2 detour edge table cell ids mismatch")
    if return_path_table[:, 1:6].tolist() != [
        [14, 12, 3, 10, 7],
        [14, 12, 3, 11, 8],
        [39, 12, 10, 34, 9],
        [39, 12, 10, 40, 13],
        [41, 12, 11, 28, 7],
        [41, 12, 11, 31, 8],
        [41, 12, 11, 35, 9],
        [41, 12, 11, 42, 13],
    ]:
        raise AssertionError("x2 detour return path table mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("x2_splice_report", {}), X2_SPLICE_REPORT, "x2 splice report input")
    assert_file_hash(inputs.get("x2_splice_obstruction", {}), X2_SPLICE_JSON, "x2 splice JSON input")
    assert_file_hash(inputs.get("x2_splice_near_misses", {}), X2_SPLICE_NEAR_MISSES, "x2 splice near miss input")
    assert_file_hash(inputs.get("x2_splice_tables", {}), X2_SPLICE_TABLES, "x2 splice table input")
    assert_file_hash(inputs.get("x2_splice_certificate", {}), X2_SPLICE_CERTIFICATE, "x2 splice certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex", {}), CELL_COMPLEX_JSON, "cell complex JSON input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edge input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex table input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("residual_chart_carriers", {}), RESIDUAL_CHART_CARRIER_CSV, "residual chart carrier input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_detour_fan_manifest@1":
        raise AssertionError("C985 d20 x2 detour fan manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 detour fan manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 x2 detour fan manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 x2 detour fan missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 detour fan index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 x2 detour fan index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_x2_detour_fan@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "return_path_count": witness.get("return_path_count"),
        "clean_single_x2_return_paths": witness.get("clean_single_x2_return_paths"),
        "dead_end_x2_detour_edge_ids": witness.get("dead_end_x2_detour_edge_ids"),
        "detour_gromov_delta": witness.get("detour_gromov_delta"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_x2_detour_fan()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
