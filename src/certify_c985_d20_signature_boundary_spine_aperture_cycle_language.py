from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_language import (
        APERTURE_COMPLETION_CERTIFICATE,
        APERTURE_COMPLETION_JSON,
        APERTURE_COMPLETION_PATHS,
        APERTURE_COMPLETION_REPORT,
        APERTURE_COMPLETION_TABLES,
        APERTURE_FAN_CERTIFICATE,
        APERTURE_FAN_PATHS,
        APERTURE_FAN_REPORT,
        APERTURE_FAN_TABLES,
        LANGUAGE_GRAPH_CERTIFICATE,
        LANGUAGE_GRAPH_EDGES,
        LANGUAGE_GRAPH_NODES,
        LANGUAGE_GRAPH_REPORT,
        LANGUAGE_GRAPH_TABLES,
        METRIC_NODE_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_EDGE_COLUMNS,
        WINDOW_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_language import (
        APERTURE_COMPLETION_CERTIFICATE,
        APERTURE_COMPLETION_JSON,
        APERTURE_COMPLETION_PATHS,
        APERTURE_COMPLETION_REPORT,
        APERTURE_COMPLETION_TABLES,
        APERTURE_FAN_CERTIFICATE,
        APERTURE_FAN_PATHS,
        APERTURE_FAN_REPORT,
        APERTURE_FAN_TABLES,
        LANGUAGE_GRAPH_CERTIFICATE,
        LANGUAGE_GRAPH_EDGES,
        LANGUAGE_GRAPH_NODES,
        LANGUAGE_GRAPH_REPORT,
        LANGUAGE_GRAPH_TABLES,
        METRIC_NODE_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_EDGE_COLUMNS,
        WINDOW_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_cycle_language() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cycle_language = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_language.json"
    )
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_language_certificate.json"
    )
    windows_csv = (OUT_DIR / "aperture_cycle_trace_windows.csv").read_text(
        encoding="utf-8"
    )
    edges_csv = (OUT_DIR / "aperture_cycle_trace_edges.csv").read_text(
        encoding="utf-8"
    )
    metric_nodes_csv = (OUT_DIR / "aperture_cycle_metric_nodes.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "aperture_cycle_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_language_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if cycle_language != expected["signature_boundary_spine_aperture_cycle_language"]:
        raise AssertionError("aperture cycle language JSON is not reproducible")
    if windows_csv != expected["aperture_cycle_trace_windows_csv"]:
        raise AssertionError("aperture cycle window CSV is not reproducible")
    if edges_csv != expected["aperture_cycle_trace_edges_csv"]:
        raise AssertionError("aperture cycle edge CSV is not reproducible")
    if metric_nodes_csv != expected["aperture_cycle_metric_nodes_csv"]:
        raise AssertionError("aperture cycle metric-node CSV is not reproducible")
    if observables_csv != expected["aperture_cycle_observables_csv"]:
        raise AssertionError("aperture cycle observable CSV is not reproducible")
    if (
        certificate
        != expected["signature_boundary_spine_aperture_cycle_language_certificate"]
    ):
        raise AssertionError("aperture cycle language certificate is not reproducible")

    table_names = [
        "window_table",
        "trace_edge_table",
        "metric_node_table",
        "cycle_adjacency",
        "cycle_distances",
        "observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"aperture cycle table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_language@1":
        raise AssertionError("C985 d20 aperture cycle report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 aperture cycle language is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 aperture cycle all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 aperture cycle checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 aperture cycle report is not reproducible")

    checks = report.get("checks", {})
    missing = sorted(
        key for key in expected["report"]["checks"] if checks.get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 aperture cycle missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("ambient_geodesic_nodes") != [48, 42, 44]:
        raise AssertionError("aperture cycle ambient geodesic mismatch")
    if witness.get("carrier_trace_nodes") != [48, 42, 27, 28, 34, 44]:
        raise AssertionError("aperture cycle carrier trace mismatch")
    if witness.get("carrier_trace_window_nodes") != [48, 42, 27, 28, 34, 44]:
        raise AssertionError("aperture cycle window node mismatch")
    if witness.get("carrier_trace_window_signatures") != [132, 183, 146, 169, 177, 185]:
        raise AssertionError("aperture cycle signature trace mismatch")
    if witness.get("completion_subsequence_word") != [2, 4, 5]:
        raise AssertionError("aperture cycle completion word mismatch")
    if witness.get("completion_subsequence_node") != 44:
        raise AssertionError("aperture cycle completion node mismatch")
    if witness.get("trace_length_48_to_44") != 5:
        raise AssertionError("aperture cycle trace length mismatch")
    if witness.get("ambient_geodesic_length_48_to_44") != 2:
        raise AssertionError("aperture cycle geodesic length mismatch")
    if witness.get("trace_detour_overhead") != 3:
        raise AssertionError("aperture cycle detour overhead mismatch")
    if witness.get("trace_signature_total_variation") != 127:
        raise AssertionError("aperture cycle trace signature variation mismatch")
    if witness.get("ambient_signature_total_variation") != 53:
        raise AssertionError("aperture cycle geodesic signature variation mismatch")
    if witness.get("signature_variation_overhead") != 74:
        raise AssertionError("aperture cycle signature overhead mismatch")
    if witness.get("trace_min_signature_after_node42") != 146:
        raise AssertionError("aperture cycle trace valley mismatch")
    if witness.get("geodesic_min_signature_after_node42") != 183:
        raise AssertionError("aperture cycle geodesic floor mismatch")
    if witness.get("cycle_metric_diameter") != 3:
        raise AssertionError("aperture cycle diameter mismatch")
    if witness.get("cycle_metric_radius") != 2:
        raise AssertionError("aperture cycle radius mismatch")
    if witness.get("cycle_metric_gromov_delta") != 0.5:
        raise AssertionError("aperture cycle Gromov delta mismatch")
    if witness.get("cycle_metric_gromov_delta_twice") != 1:
        raise AssertionError("aperture cycle Gromov delta twice mismatch")

    window_table = np.asarray(tables["window_table"], dtype=np.int64)
    trace_edge_table = np.asarray(tables["trace_edge_table"], dtype=np.int64)
    metric_node_table = np.asarray(tables["metric_node_table"], dtype=np.int64)
    adjacency = np.asarray(tables["cycle_adjacency"], dtype=np.int8)
    distances = np.asarray(tables["cycle_distances"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if window_table.shape != (7, len(WINDOW_COLUMNS)):
        raise AssertionError("aperture cycle window table shape mismatch")
    if trace_edge_table.shape != (6, len(TRACE_EDGE_COLUMNS)):
        raise AssertionError("aperture cycle edge table shape mismatch")
    if metric_node_table.shape != (6, len(METRIC_NODE_COLUMNS)):
        raise AssertionError("aperture cycle metric-node table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("aperture cycle observable table shape mismatch")
    if adjacency.shape != (6, 6) or not np.array_equal(adjacency, adjacency.T):
        raise AssertionError("aperture cycle adjacency shape/symmetry mismatch")
    if int(np.sum(adjacency) // 2) != 6:
        raise AssertionError("aperture cycle adjacency edge count mismatch")
    if distances.shape != (6, 6) or int(np.max(distances)) != 3:
        raise AssertionError("aperture cycle distance table mismatch")
    if window_table.tolist() != [
        [0, 0, 3, 5, 3, 141, 48, 5, 0, 132, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 5, 3, 2, 200, 42, 6, 1, 183, 1, 1, 0, 0, 0, 1, 0],
        [2, 2, 3, 2, 1, 121, 27, 5, 0, 146, -1, 2, 0, 0, 0, 0, 0],
        [3, 3, 2, 1, 4, 82, 28, 6, 1, 169, -1, 3, 0, 0, 0, 0, 0],
        [4, 4, 1, 4, 5, 65, 34, 6, 1, 177, -1, 4, 0, 0, 0, 0, 0],
        [5, 5, 4, 5, 2, 176, 44, 6, 1, 185, 2, 5, 1, 0, 0, 0, 1],
        [6, 6, 2, 4, 5, 101, 44, 6, 1, 185, 2, -1, 0, 1, 0, 0, 1],
    ]:
        raise AssertionError("aperture cycle window table rows mismatch")
    if trace_edge_table.tolist() != [
        [0, 0, 48, 42, 283, 3, 2, 132, 183, 51, 51, 1, 1, 0],
        [1, 1, 42, 27, 206, 5, 1, 183, 146, -37, 37, 0, 1, 0],
        [2, 2, 27, 28, 198, 3, 4, 146, 169, 23, 23, 0, 1, 0],
        [3, 3, 28, 34, 210, 2, 5, 169, 177, 8, 8, 0, 1, 0],
        [4, 4, 34, 44, 247, 1, 2, 177, 185, 8, 8, 0, 1, 0],
        [5, 5, 42, 44, 281, 3, 4, 183, 185, 2, 2, 1, 0, 1],
    ]:
        raise AssertionError("aperture cycle edge table rows mismatch")
    if metric_node_table.tolist() != [
        [0, 48, 0, 0, 132, 0, 1, 2],
        [1, 42, 1, 1, 183, 1, 0, 1],
        [2, 27, 2, -1, 146, 2, 1, 2],
        [3, 28, 3, -1, 169, 3, 2, 2],
        [4, 34, 4, -1, 177, 3, 2, 1],
        [5, 44, 5, 2, 185, 2, 1, 0],
    ]:
        raise AssertionError("aperture cycle metric-node table rows mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("aperture_completion_report", {}), APERTURE_COMPLETION_REPORT, "aperture completion report input")
    assert_file_hash(inputs.get("aperture_completion", {}), APERTURE_COMPLETION_JSON, "aperture completion JSON input")
    assert_file_hash(inputs.get("aperture_completion_paths", {}), APERTURE_COMPLETION_PATHS, "aperture completion paths input")
    assert_file_hash(inputs.get("aperture_completion_tables", {}), APERTURE_COMPLETION_TABLES, "aperture completion table input")
    assert_file_hash(inputs.get("aperture_completion_certificate", {}), APERTURE_COMPLETION_CERTIFICATE, "aperture completion certificate input")
    assert_file_hash(inputs.get("aperture_fan_report", {}), APERTURE_FAN_REPORT, "aperture fan report input")
    assert_file_hash(inputs.get("aperture_fan_paths", {}), APERTURE_FAN_PATHS, "aperture fan paths input")
    assert_file_hash(inputs.get("aperture_fan_tables", {}), APERTURE_FAN_TABLES, "aperture fan table input")
    assert_file_hash(inputs.get("aperture_fan_certificate", {}), APERTURE_FAN_CERTIFICATE, "aperture fan certificate input")
    assert_file_hash(inputs.get("language_graph_report", {}), LANGUAGE_GRAPH_REPORT, "language graph report input")
    assert_file_hash(inputs.get("language_graph_nodes", {}), LANGUAGE_GRAPH_NODES, "language graph nodes input")
    assert_file_hash(inputs.get("language_graph_edges", {}), LANGUAGE_GRAPH_EDGES, "language graph edges input")
    assert_file_hash(inputs.get("language_graph_tables", {}), LANGUAGE_GRAPH_TABLES, "language graph table input")
    assert_file_hash(inputs.get("language_graph_certificate", {}), LANGUAGE_GRAPH_CERTIFICATE, "language graph certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_nodes", {}), REWRITE_COMPLEX_NODES, "rewrite complex nodes input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex table input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity table input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_language_manifest@1":
        raise AssertionError("C985 d20 aperture cycle manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 aperture cycle manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 aperture cycle missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 aperture cycle index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_cycle_language@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "ambient_geodesic_nodes": witness.get("ambient_geodesic_nodes"),
        "carrier_trace_nodes": witness.get("carrier_trace_nodes"),
        "trace_detour_overhead": witness.get("trace_detour_overhead"),
        "trace_signature_total_variation": witness.get(
            "trace_signature_total_variation"
        ),
        "cycle_metric_gromov_delta": witness.get("cycle_metric_gromov_delta"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_cycle_language()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
