from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_rewrite_complex_hyperbolicity import (
        ASSOCIATIVITY_REPORT,
        EDGE_COLUMNS,
        NODE_COLUMNS,
        OUT_DIR,
        POINCARE_JSON,
        POINCARE_NPZ,
        POINCARE_REPORT,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_JSON,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_rewrite_complex_hyperbolicity import (
        ASSOCIATIVITY_REPORT,
        EDGE_COLUMNS,
        NODE_COLUMNS,
        OUT_DIR,
        POINCARE_JSON,
        POINCARE_NPZ,
        POINCARE_REPORT,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_JSON,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
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


def validate_c985_d20_rewrite_complex_hyperbolicity() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    rewrite_complex = load_json(OUT_DIR / "rewrite_complex.json")
    certificate = load_json(OUT_DIR / "rewrite_complex_certificate.json")
    nodes_csv = (OUT_DIR / "rewrite_complex_nodes.csv").read_text(encoding="utf-8")
    edges_csv = (OUT_DIR / "rewrite_complex_edges.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "rewrite_complex_tables.npz", allow_pickle=False)
    node_table = np.asarray(tables["node_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    adjacency = np.asarray(tables["adjacency"], dtype=np.int8)
    graph_distances = np.asarray(tables["graph_distances"], dtype=np.int64)
    node_coordinates = np.asarray(tables["node_poincare_coordinates"], dtype=np.float64)
    node_poincare_distances = np.asarray(tables["node_poincare_distances"], dtype=np.float64)
    index = load_json(INDEX_PATH)

    if rewrite_complex != expected["rewrite_complex"]:
        raise AssertionError("d20 rewrite complex JSON is not reproducible")
    if nodes_csv != expected["rewrite_complex_nodes_csv"]:
        raise AssertionError("d20 rewrite complex node CSV is not reproducible")
    if edges_csv != expected["rewrite_complex_edges_csv"]:
        raise AssertionError("d20 rewrite complex edge CSV is not reproducible")
    if not np.array_equal(node_table, expected["node_table"]):
        raise AssertionError("d20 rewrite complex node table is not reproducible")
    if not np.array_equal(edge_table, expected["edge_table"]):
        raise AssertionError("d20 rewrite complex edge table is not reproducible")
    if not np.array_equal(adjacency, expected["adjacency"]):
        raise AssertionError("d20 rewrite complex adjacency table is not reproducible")
    if not np.array_equal(graph_distances, expected["graph_distances"]):
        raise AssertionError("d20 rewrite complex graph distances are not reproducible")
    if not np.allclose(node_coordinates, expected["node_poincare_coordinates"], atol=0.0, rtol=0.0):
        raise AssertionError("d20 rewrite complex Poincare coordinates are not reproducible")
    if not np.allclose(
        node_poincare_distances,
        expected["node_poincare_distances"],
        atol=0.0,
        rtol=0.0,
    ):
        raise AssertionError("d20 rewrite complex Poincare distances are not reproducible")
    if certificate != expected["rewrite_complex_certificate"]:
        raise AssertionError("d20 rewrite complex certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_rewrite_complex_hyperbolicity@1":
        raise AssertionError("C985 d20 rewrite complex report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 rewrite complex hyperbolicity is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 rewrite complex all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 rewrite complex checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 rewrite complex report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 rewrite complex report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "symbolic_associativity_report_certified",
        "symbolic_associativity_certificate_certified",
        "poincare_embedding_report_certified",
        "symbolic_associativity_table_shape_is_216_by_27",
        "poincare_coordinate_table_shape_is_20_by_10",
        "poincare_distance_matrix_shape_is_20_by_20",
        "rewrite_complex_node_count_is_56",
        "rewrite_complex_edge_count_is_315",
        "rewrite_complex_degree_histogram_is_6_five_30_ten_20_fifteen",
        "rewrite_complex_connected",
        "rewrite_complex_graph_diameter_is_3",
        "rewrite_complex_graph_radius_is_3",
        "rewrite_complex_gromov_delta_is_1",
        "rewrite_complex_delta_witness_is_0_6_22_36",
        "rewrite_complex_full_sector_node_count_is_14",
        "rewrite_complex_sector_coverage_histogram_is_6_three_10_four_26_five_14_six",
        "rewrite_complex_signature_union_max_is_185",
        "rewrite_complex_signature_union_min_is_53",
        "rewrite_complex_max_signature_node_is_44",
        "rewrite_complex_min_signature_node_is_46",
        "all_poincare_barycenters_inside_open_disk",
        "poincare_central_node_is_14",
        "poincare_outermost_node_is_0",
        "poincare_barycenter_metric_diameter_is_0_7423247109",
        "poincare_diameter_pair_is_0_55",
        "poincare_diameter_pair_is_graph_diameter",
        "top_20_poincare_pairs_are_graph_diameter",
        "graph_poincare_distance_correlation_is_0_4851736825",
        "max_edge_poincare_barycenter_distance_is_0_2509641633",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 rewrite complex missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("node_count") != 56:
        raise AssertionError("rewrite complex node count mismatch")
    if witness.get("edge_count") != 315:
        raise AssertionError("rewrite complex edge count mismatch")
    if witness.get("graph_diameter") != 3 or witness.get("graph_radius") != 3:
        raise AssertionError("rewrite complex graph diameter/radius mismatch")
    if witness.get("graph_gromov_delta") != 1.0 or witness.get("graph_gromov_delta_twice") != 2:
        raise AssertionError("rewrite complex Gromov delta mismatch")
    if witness.get("graph_delta_witness_nodes") != [0, 6, 22, 36]:
        raise AssertionError("rewrite complex delta witness mismatch")
    if witness.get("full_sector_node_count") != 14:
        raise AssertionError("rewrite complex full-sector node count mismatch")
    if witness.get("signature_union_count_max") != 185:
        raise AssertionError("rewrite complex max signature count mismatch")
    if witness.get("signature_union_count_min") != 53:
        raise AssertionError("rewrite complex min signature count mismatch")
    if witness.get("poincare_central_node_id") != 14:
        raise AssertionError("rewrite complex Poincare central node mismatch")
    if witness.get("poincare_outermost_node_id") != 0:
        raise AssertionError("rewrite complex Poincare outermost node mismatch")
    if witness.get("poincare_diameter_pair_node_ids") != [0, 55]:
        raise AssertionError("rewrite complex Poincare diameter pair mismatch")
    if witness.get("poincare_diameter_pair_graph_distance") != 3:
        raise AssertionError("rewrite complex Poincare diameter graph distance mismatch")
    if witness.get("top_20_poincare_pairs_graph_distance_histogram") != [{"value": 3, "count": 20}]:
        raise AssertionError("rewrite complex top Poincare pair graph-distance histogram mismatch")
    if witness.get("graph_poincare_distance_correlation") != 0.4851736825:
        raise AssertionError("rewrite complex graph/Poincare correlation mismatch")

    if node_table.shape != (56, len(NODE_COLUMNS)):
        raise AssertionError("rewrite complex node table shape mismatch")
    if edge_table.shape != (315, len(EDGE_COLUMNS)):
        raise AssertionError("rewrite complex edge table shape mismatch")
    if adjacency.shape != (56, 56):
        raise AssertionError("rewrite complex adjacency shape mismatch")
    if int(np.sum(adjacency) // 2) != 315:
        raise AssertionError("rewrite complex adjacency edge count mismatch")
    if not np.array_equal(adjacency, adjacency.T):
        raise AssertionError("rewrite complex adjacency is not symmetric")
    if graph_distances.shape != (56, 56):
        raise AssertionError("rewrite complex graph distance shape mismatch")
    if int(np.max(graph_distances)) != 3:
        raise AssertionError("rewrite complex graph distance diameter mismatch")
    if node_coordinates.shape != (56, 7):
        raise AssertionError("rewrite complex Poincare coordinate shape mismatch")
    if node_poincare_distances.shape != (56, 56):
        raise AssertionError("rewrite complex Poincare distance shape mismatch")
    if not np.allclose(node_poincare_distances, node_poincare_distances.T, atol=0.0, rtol=0.0):
        raise AssertionError("rewrite complex Poincare distances are not symmetric")
    if float(np.max(node_coordinates[:, 3])) >= 1.0:
        raise AssertionError("rewrite complex Poincare barycenter outside disk")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("symbolic_associativity_report", {}),
        ASSOCIATIVITY_REPORT,
        "symbolic associativity report input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity", {}),
        SYMBOLIC_ASSOCIATIVITY_JSON,
        "symbolic associativity input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity_tables", {}),
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        "symbolic associativity tables input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity_certificate", {}),
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        "symbolic associativity certificate input",
    )
    assert_file_hash(inputs.get("poincare_report", {}), POINCARE_REPORT, "Poincare report input")
    assert_file_hash(inputs.get("poincare_embedding", {}), POINCARE_JSON, "Poincare embedding input")
    assert_file_hash(inputs.get("poincare_embedding_npz", {}), POINCARE_NPZ, "Poincare embedding NPZ input")

    if manifest.get("schema") != "c985.proof_obligation.d20_rewrite_complex_hyperbolicity_manifest@1":
        raise AssertionError("C985 d20 rewrite complex manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 rewrite complex manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 rewrite complex manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 rewrite complex missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 rewrite complex index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 rewrite complex index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_rewrite_complex_hyperbolicity@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "node_count": witness.get("node_count"),
        "edge_count": witness.get("edge_count"),
        "graph_diameter": witness.get("graph_diameter"),
        "graph_gromov_delta": witness.get("graph_gromov_delta"),
        "graph_delta_witness_nodes": witness.get("graph_delta_witness_nodes"),
        "full_sector_node_count": witness.get("full_sector_node_count"),
        "signature_union_count_max": witness.get("signature_union_count_max"),
        "poincare_diameter_pair_node_ids": witness.get("poincare_diameter_pair_node_ids"),
        "poincare_diameter_pair_graph_distance": witness.get("poincare_diameter_pair_graph_distance"),
        "graph_poincare_distance_correlation": witness.get("graph_poincare_distance_correlation"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_rewrite_complex_hyperbolicity()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
