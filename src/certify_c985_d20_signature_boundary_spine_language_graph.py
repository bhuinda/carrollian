from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_language_graph import (
        GATE_AUTOMATON_BRANCH_WORDS,
        GATE_AUTOMATON_CERTIFICATE,
        GATE_AUTOMATON_JSON,
        GATE_AUTOMATON_OBSERVABLES,
        GATE_AUTOMATON_REPORT,
        GATE_AUTOMATON_TABLES,
        GATE_AUTOMATON_TRANSITIONS,
        GATE_AUTOMATON_TRIGRAMS,
        LANGUAGE_APERTURE_COLUMNS,
        LANGUAGE_EDGE_COLUMNS,
        LANGUAGE_NODE_COLUMNS,
        LANGUAGE_OBSERVABLE_COLUMNS,
        LANGUAGE_SHORTCUT_COLUMNS,
        LANGUAGE_TRANSITION_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
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
    from derive_c985_d20_signature_boundary_spine_language_graph import (
        GATE_AUTOMATON_BRANCH_WORDS,
        GATE_AUTOMATON_CERTIFICATE,
        GATE_AUTOMATON_JSON,
        GATE_AUTOMATON_OBSERVABLES,
        GATE_AUTOMATON_REPORT,
        GATE_AUTOMATON_TABLES,
        GATE_AUTOMATON_TRANSITIONS,
        GATE_AUTOMATON_TRIGRAMS,
        LANGUAGE_APERTURE_COLUMNS,
        LANGUAGE_EDGE_COLUMNS,
        LANGUAGE_NODE_COLUMNS,
        LANGUAGE_OBSERVABLE_COLUMNS,
        LANGUAGE_SHORTCUT_COLUMNS,
        LANGUAGE_TRANSITION_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
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


def validate_c985_d20_signature_boundary_spine_language_graph() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    language_graph = load_json(OUT_DIR / "signature_boundary_spine_language_graph.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_language_graph_certificate.json"
    )
    nodes_csv = (OUT_DIR / "language_graph_nodes.csv").read_text(encoding="utf-8")
    edges_csv = (OUT_DIR / "language_graph_edges.csv").read_text(encoding="utf-8")
    transitions_csv = (OUT_DIR / "language_trigram_transitions.csv").read_text(
        encoding="utf-8"
    )
    shortcuts_csv = (OUT_DIR / "language_ambient_shortcuts.csv").read_text(
        encoding="utf-8"
    )
    aperture_csv = (OUT_DIR / "language_aperture_distances.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "language_graph_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_language_graph_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if language_graph != expected["signature_boundary_spine_language_graph"]:
        raise AssertionError("boundary spine language graph JSON is not reproducible")
    if nodes_csv != expected["language_graph_nodes_csv"]:
        raise AssertionError("language graph node CSV is not reproducible")
    if edges_csv != expected["language_graph_edges_csv"]:
        raise AssertionError("language graph edge CSV is not reproducible")
    if transitions_csv != expected["language_trigram_transitions_csv"]:
        raise AssertionError("language trigram transition CSV is not reproducible")
    if shortcuts_csv != expected["language_ambient_shortcuts_csv"]:
        raise AssertionError("language ambient shortcut CSV is not reproducible")
    if aperture_csv != expected["language_aperture_distances_csv"]:
        raise AssertionError("language aperture distance CSV is not reproducible")
    if observables_csv != expected["language_graph_observables_csv"]:
        raise AssertionError("language graph observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_language_graph_certificate"]:
        raise AssertionError("language graph certificate is not reproducible")

    table_names = [
        "language_node_table",
        "language_edge_table",
        "language_transition_table",
        "language_shortcut_table",
        "language_aperture_table",
        "language_adjacency",
        "language_distances",
        "ambient_observed_distances",
        "language_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"language graph table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_language_graph@1":
        raise AssertionError("C985 d20 boundary spine language graph report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary spine language graph is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary spine language graph all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary spine language graph checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine language graph report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary spine language graph report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "gate_automaton_report_certified",
        "gate_automaton_certificate_certified",
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "gate_automaton_schema_available",
        "rewrite_complex_schema_available",
        "gate_automaton_tables_available",
        "rewrite_complex_tables_available",
        "gate_transition_table_shape_is_16_by_16",
        "gate_branch_word_table_shape_is_6_by_14",
        "gate_trigram_table_shape_is_12_by_20",
        "rewrite_node_table_shape_is_56_by_17",
        "rewrite_edge_table_shape_is_315_by_13",
        "canonical_window_sequence_matches_expected",
        "language_path_nodes_match_first_occurrence_order",
        "language_node_count_is_8",
        "language_edge_count_is_7",
        "language_transition_count_is_11",
        "language_self_loop_transition_count_is_4",
        "language_graph_connected",
        "language_graph_diameter_is_7",
        "language_graph_radius_is_4",
        "language_gromov_delta_is_0",
        "language_boundary_endpoints_are_20_48",
        "all_language_edges_are_rewrite_complex_edges",
        "ambient_induced_edge_count_is_10",
        "ambient_shortcut_edge_count_is_3",
        "boundary_endpoint_language_distance_is_7",
        "boundary_endpoint_ambient_distance_is_2",
        "max_language_to_ambient_gap_is_5",
        "aperture_node_is_44",
        "aperture_absent_from_language_nodes",
        "aperture_min_ambient_distance_is_2",
        "nearest_aperture_nodes_match_expected",
        "observed_max_signature_is_175",
        "aperture_signature_is_185",
        "aperture_signature_gap_is_10",
        "source_to_branch_gate_symbols_omit_x2_x4",
        "language_node_table_shape_is_8_by_14",
        "language_edge_table_shape_is_7_by_10",
        "language_transition_table_shape_is_11_by_10",
        "language_shortcut_table_shape_is_3_by_10",
        "language_aperture_table_shape_is_8_by_9",
        "language_observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary spine language graph missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("canonical_window_sequence") != [
        20,
        5,
        1,
        8,
        23,
        32,
        32,
        51,
        51,
        51,
        51,
        48,
    ]:
        raise AssertionError("language graph canonical sequence mismatch")
    if witness.get("language_path_node_ids") != [20, 5, 1, 8, 23, 32, 51, 48]:
        raise AssertionError("language graph path node order mismatch")
    if witness.get("language_edge_node_pairs") != [
        [20, 5],
        [5, 1],
        [1, 8],
        [8, 23],
        [23, 32],
        [32, 51],
        [51, 48],
    ]:
        raise AssertionError("language graph edge path mismatch")
    if witness.get("language_self_loop_transition_count") != 4:
        raise AssertionError("language graph self-loop count mismatch")
    if witness.get("language_graph_diameter") != 7 or witness.get("language_graph_radius") != 4:
        raise AssertionError("language graph diameter/radius mismatch")
    if witness.get("language_gromov_delta") != 0.0 or witness.get("language_gromov_delta_twice") != 0:
        raise AssertionError("language graph Gromov delta mismatch")
    if witness.get("language_boundary_endpoint_node_ids") != [20, 48]:
        raise AssertionError("language graph boundary endpoints mismatch")
    if witness.get("boundary_endpoint_language_distance") != 7:
        raise AssertionError("language graph boundary language distance mismatch")
    if witness.get("boundary_endpoint_ambient_distance") != 2:
        raise AssertionError("language graph boundary ambient distance mismatch")
    if witness.get("ambient_induced_edge_count") != 10:
        raise AssertionError("language graph ambient induced edge count mismatch")
    if witness.get("max_language_to_ambient_gap") != 5:
        raise AssertionError("language graph max ambient gap mismatch")
    if witness.get("aperture_node", {}).get("node_id") != 44:
        raise AssertionError("language graph aperture node mismatch")
    if witness.get("aperture_node", {}).get("canonical_word") != "x2 x4 x5":
        raise AssertionError("language graph aperture word mismatch")
    if witness.get("aperture_nearest_language_node_ids") != [20, 5, 32, 51, 48]:
        raise AssertionError("language graph nearest aperture nodes mismatch")
    if witness.get("aperture_min_ambient_distance") != 2:
        raise AssertionError("language graph aperture distance mismatch")
    if witness.get("observed_signature_union_max") != 175:
        raise AssertionError("language graph observed signature max mismatch")
    if witness.get("aperture_signature_gap") != 10:
        raise AssertionError("language graph aperture signature gap mismatch")
    if witness.get("missing_gate_symbol_bitset") != 20:
        raise AssertionError("language graph missing symbol bitset mismatch")

    node_table = np.asarray(tables["language_node_table"], dtype=np.int64)
    edge_table = np.asarray(tables["language_edge_table"], dtype=np.int64)
    transition_table = np.asarray(tables["language_transition_table"], dtype=np.int64)
    shortcut_table = np.asarray(tables["language_shortcut_table"], dtype=np.int64)
    aperture_table = np.asarray(tables["language_aperture_table"], dtype=np.int64)
    adjacency = np.asarray(tables["language_adjacency"], dtype=np.int8)
    distances = np.asarray(tables["language_distances"], dtype=np.int64)
    ambient_distances = np.asarray(tables["ambient_observed_distances"], dtype=np.int64)
    observable_table = np.asarray(tables["language_observable_table"], dtype=np.int64)

    if node_table.shape != (8, len(LANGUAGE_NODE_COLUMNS)):
        raise AssertionError("language graph node table shape mismatch")
    if edge_table.shape != (7, len(LANGUAGE_EDGE_COLUMNS)):
        raise AssertionError("language graph edge table shape mismatch")
    if transition_table.shape != (11, len(LANGUAGE_TRANSITION_COLUMNS)):
        raise AssertionError("language graph transition table shape mismatch")
    if shortcut_table.shape != (3, len(LANGUAGE_SHORTCUT_COLUMNS)):
        raise AssertionError("language graph shortcut table shape mismatch")
    if aperture_table.shape != (8, len(LANGUAGE_APERTURE_COLUMNS)):
        raise AssertionError("language graph aperture table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(LANGUAGE_OBSERVABLE_COLUMNS)):
        raise AssertionError("language graph observable table shape mismatch")
    if adjacency.shape != (8, 8) or not np.array_equal(adjacency, adjacency.T):
        raise AssertionError("language graph adjacency shape/symmetry mismatch")
    if int(np.sum(adjacency) // 2) != 7:
        raise AssertionError("language graph adjacency edge count mismatch")
    if distances.shape != (8, 8) or int(np.max(distances)) != 7:
        raise AssertionError("language graph distance table mismatch")
    if ambient_distances.shape != (8, 8) or int(np.max(ambient_distances)) != 3:
        raise AssertionError("language graph ambient observed distance table mismatch")
    if int(ambient_distances[0, 7]) != 2:
        raise AssertionError("language graph endpoint ambient distance table mismatch")
    if transition_table[:, 7].tolist().count(1) != 4:
        raise AssertionError("language graph transition self-loop flags mismatch")
    if shortcut_table[:, 7].tolist() != [1, 5, 1]:
        raise AssertionError("language graph shortcut compression mismatch")
    if aperture_table[:, 3].tolist() != [2, 2, 3, 3, 3, 2, 2, 2]:
        raise AssertionError("language graph aperture distance row mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("gate_automaton_report", {}),
        GATE_AUTOMATON_REPORT,
        "gate automaton report input",
    )
    assert_file_hash(inputs.get("gate_automaton", {}), GATE_AUTOMATON_JSON, "gate automaton JSON input")
    assert_file_hash(
        inputs.get("gate_automaton_transitions", {}),
        GATE_AUTOMATON_TRANSITIONS,
        "gate automaton transition input",
    )
    assert_file_hash(
        inputs.get("gate_automaton_branch_words", {}),
        GATE_AUTOMATON_BRANCH_WORDS,
        "gate automaton branch word input",
    )
    assert_file_hash(inputs.get("gate_automaton_trigrams", {}), GATE_AUTOMATON_TRIGRAMS, "gate automaton trigram input")
    assert_file_hash(
        inputs.get("gate_automaton_observables", {}),
        GATE_AUTOMATON_OBSERVABLES,
        "gate automaton observable input",
    )
    assert_file_hash(inputs.get("gate_automaton_tables", {}), GATE_AUTOMATON_TABLES, "gate automaton table input")
    assert_file_hash(
        inputs.get("gate_automaton_certificate", {}),
        GATE_AUTOMATON_CERTIFICATE,
        "gate automaton certificate input",
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_language_graph_manifest@1":
        raise AssertionError("C985 d20 boundary spine language graph manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine language graph manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary spine language graph manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 boundary spine language graph missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine language graph index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary spine language graph index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_language_graph@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "language_path_node_ids": witness.get("language_path_node_ids"),
        "language_graph_diameter": witness.get("language_graph_diameter"),
        "language_gromov_delta": witness.get("language_gromov_delta"),
        "boundary_endpoint_ambient_distance": witness.get(
            "boundary_endpoint_ambient_distance"
        ),
        "aperture_node": witness.get("aperture_node"),
        "aperture_min_ambient_distance": witness.get("aperture_min_ambient_distance"),
        "aperture_signature_gap": witness.get("aperture_signature_gap"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_language_graph()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
