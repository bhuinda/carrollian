from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_eta6_truncated_skeleton import (
        APERTURE_POLYGON_REPORT,
        APERTURE_POLYGON_TABLES,
        CELESTIAL_TRACE_REPORT,
        DERIVE_SCRIPT,
        GRAPH_COLUMNS,
        HCYCLE_EDGE_TABLE,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROMOTION_TABLES,
        PUBLIC_BOUNDARY_REPORT,
        STATUS,
        THEOREM_ID,
        TRUNCATED_EDGE_COLUMNS,
        TRUNCATED_FACE_COLUMNS,
        TRUNCATED_VERTEX_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_eta6_truncated_skeleton import (
        APERTURE_POLYGON_REPORT,
        APERTURE_POLYGON_TABLES,
        CELESTIAL_TRACE_REPORT,
        DERIVE_SCRIPT,
        GRAPH_COLUMNS,
        HCYCLE_EDGE_TABLE,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROMOTION_TABLES,
        PUBLIC_BOUNDARY_REPORT,
        STATUS,
        THEOREM_ID,
        TRUNCATED_EDGE_COLUMNS,
        TRUNCATED_FACE_COLUMNS,
        TRUNCATED_VERTEX_COLUMNS,
        VALIDATOR_SCRIPT,
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
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    skeleton = load_json(
        OUT_DIR
        / "eta6_truncated_skeleton.json"
    )
    certificate = load_json(
        OUT_DIR
        / "eta6_truncated_skeleton_certificate.json"
    )
    vertices_csv = (OUT_DIR / "eta6_truncated_icosahedral_vertices.csv").read_text(
        encoding="utf-8"
    )
    edges_csv = (OUT_DIR / "eta6_truncated_icosahedral_edges.csv").read_text(
        encoding="utf-8"
    )
    faces_csv = (OUT_DIR / "eta6_truncated_icosahedral_faces.csv").read_text(
        encoding="utf-8"
    )
    graphs_csv = (OUT_DIR / "eta6_truncated_icosahedral_graphs.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "eta6_truncated_icosahedral_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "eta6_truncated_skeleton_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if skeleton != expected["skeleton"]:
        raise AssertionError("eta6 truncated skeleton JSON is not reproducible")
    if vertices_csv != expected["vertices_csv"]:
        raise AssertionError("eta6 truncated skeleton vertices CSV mismatch")
    if edges_csv != expected["edges_csv"]:
        raise AssertionError("eta6 truncated skeleton edges CSV mismatch")
    if faces_csv != expected["faces_csv"]:
        raise AssertionError("eta6 truncated skeleton faces CSV mismatch")
    if graphs_csv != expected["graphs_csv"]:
        raise AssertionError("eta6 truncated skeleton graphs CSV mismatch")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 truncated skeleton observables CSV mismatch")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 truncated skeleton certificate mismatch")

    for name in [
        "vertex_table",
        "edge_table",
        "face_table",
        "graph_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 truncated skeleton table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton@1"
    ):
        raise AssertionError("eta6 truncated skeleton report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 truncated skeleton report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 truncated skeleton all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 truncated skeleton checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 truncated skeleton report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 truncated skeleton report hash mismatch")

    vertex_table = np.asarray(tables["vertex_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    graph_table = np.asarray(tables["graph_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    expected_shapes = {
        "vertex": (60, len(TRUNCATED_VERTEX_COLUMNS)),
        "edge": (90, len(TRUNCATED_EDGE_COLUMNS)),
        "face": (32, len(TRUNCATED_FACE_COLUMNS)),
        "graph": (4, len(GRAPH_COLUMNS)),
        "observable": (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }
    actual_shapes = {
        "vertex": tuple(vertex_table.shape),
        "edge": tuple(edge_table.shape),
        "face": tuple(face_table.shape),
        "graph": tuple(graph_table.shape),
        "observable": tuple(observable_table.shape),
    }
    if actual_shapes != expected_shapes:
        raise AssertionError(f"eta6 truncated skeleton table shapes: {actual_shapes}")

    graph_rows = table_rows(graph_table, GRAPH_COLUMNS)
    public_row, dual_row, truncated_row, endpoint_row = graph_rows
    if (
        public_row["vertex_count"],
        public_row["edge_count"],
        public_row["face_count"],
        public_row["cubic_flag"],
        public_row["three_vertex_connected_flag"],
        public_row["d20_boundary_graph_flag"],
    ) != (20, 30, 12, 1, 1, 1):
        raise AssertionError("eta6 truncated skeleton public graph mismatch")
    if (
        dual_row["vertex_count"],
        dual_row["edge_count"],
        dual_row["face_count"],
        dual_row["min_degree"],
        dual_row["max_degree"],
        dual_row["dual_icosahedral_graph_flag"],
    ) != (12, 30, 20, 5, 5, 1):
        raise AssertionError("eta6 truncated skeleton dual graph mismatch")
    if (
        truncated_row["vertex_count"],
        truncated_row["edge_count"],
        truncated_row["face_count"],
        truncated_row["min_degree"],
        truncated_row["max_degree"],
        truncated_row["cubic_flag"],
        truncated_row["connected_flag"],
        truncated_row["three_vertex_connected_flag"],
        truncated_row["polyhedral_embedding_flag"],
        truncated_row["truncated_icosahedral_graph_flag"],
        truncated_row["euler_characteristic"],
        truncated_row["girth"],
        truncated_row["diameter"],
    ) != (60, 90, 32, 3, 3, 1, 1, 1, 1, 1, 2, 5, 9):
        raise AssertionError("eta6 truncated skeleton truncated graph mismatch")
    if (
        endpoint_row["vertex_count"],
        endpoint_row["edge_count"],
        endpoint_row["component_count"],
        endpoint_row["connected_flag"],
        endpoint_row["three_vertex_connected_flag"],
        endpoint_row["truncated_icosahedral_graph_flag"],
    ) != (12, 6, 6, 0, 0, 0):
        raise AssertionError("eta6 truncated skeleton endpoint graph mismatch")

    face_rows = table_rows(face_table, TRUNCATED_FACE_COLUMNS)
    if sum(row["face_type_code"] == 0 for row in face_rows) != 12:
        raise AssertionError("eta6 truncated skeleton pentagon count mismatch")
    if sum(row["face_type_code"] == 1 for row in face_rows) != 20:
        raise AssertionError("eta6 truncated skeleton hexagon count mismatch")
    if any(row["face_size"] not in (5, 6) for row in face_rows):
        raise AssertionError("eta6 truncated skeleton bad face size")

    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    required_observables = {
        "public_boundary_vertex_count": 20,
        "public_boundary_edge_count": 30,
        "public_boundary_face_count": 12,
        "dual_icosahedral_vertex_count": 12,
        "dual_icosahedral_edge_count": 30,
        "dual_icosahedral_face_count": 20,
        "truncated_vertex_count": 60,
        "truncated_edge_count": 90,
        "truncated_face_count": 32,
        "truncated_pentagon_face_count": 12,
        "truncated_hexagon_face_count": 20,
        "truncated_cubic_flag": 1,
        "truncated_planar_embedding_flag": 1,
        "truncated_three_vertex_connected_flag": 1,
        "truncated_girth": 5,
        "truncated_diameter": 9,
        "endpoint_cut_vertex_count": 12,
        "endpoint_cut_edge_count": 6,
        "endpoint_cut_component_count": 6,
        "endpoint_cut_truncated_match_flag": 0,
        "midpoint_convex_hull_vertex_count": 3,
        "midpoint_graham_match_flag": 0,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 truncated skeleton observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("public_boundary_report", {}),
        PUBLIC_BOUNDARY_REPORT,
        "public boundary report input",
    )
    assert_file_hash(
        inputs.get("celestial_trace_report", {}),
        CELESTIAL_TRACE_REPORT,
        "celestial trace report input",
    )
    assert_file_hash(
        inputs.get("aperture_polygon_report", {}),
        APERTURE_POLYGON_REPORT,
        "aperture polygon report input",
    )
    assert_file_hash(
        inputs.get("aperture_polygon_tables", {}),
        APERTURE_POLYGON_TABLES,
        "aperture polygon tables input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_tables", {}),
        PROMOTION_TABLES,
        "second-window promotion tables input",
    )
    assert_file_hash(
        inputs.get("hcycle_edge_table", {}),
        HCYCLE_EDGE_TABLE,
        "H-cycle edge table input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton_manifest@1"
    ):
        raise AssertionError("eta6 truncated skeleton manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 truncated skeleton manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6 truncated skeleton manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 truncated skeleton missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 truncated skeleton index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 truncated skeleton index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_truncated_icosahedral_boundary_skeleton()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
