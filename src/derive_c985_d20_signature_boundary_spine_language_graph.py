from __future__ import annotations

import itertools
import json
from collections import Counter, deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_gate_automaton import (
        OUT_DIR as GATE_AUTOMATON_DIR,
    )
    from .derive_c985_d20_rewrite_complex_hyperbolicity import (
        OUT_DIR as REWRITE_COMPLEX_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_gate_automaton import (
        OUT_DIR as GATE_AUTOMATON_DIR,
    )
    from derive_c985_d20_rewrite_complex_hyperbolicity import (
        OUT_DIR as REWRITE_COMPLEX_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        popcount,
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_spine_language_graph"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_LANGUAGE_GRAPH_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

GATE_AUTOMATON_REPORT = GATE_AUTOMATON_DIR / "report.json"
GATE_AUTOMATON_JSON = (
    GATE_AUTOMATON_DIR / "signature_boundary_spine_gate_automaton.json"
)
GATE_AUTOMATON_TRANSITIONS = GATE_AUTOMATON_DIR / "gate_automaton_transitions.csv"
GATE_AUTOMATON_BRANCH_WORDS = GATE_AUTOMATON_DIR / "gate_branch_words.csv"
GATE_AUTOMATON_TRIGRAMS = GATE_AUTOMATON_DIR / "gate_trigram_windows.csv"
GATE_AUTOMATON_OBSERVABLES = GATE_AUTOMATON_DIR / "gate_automaton_observables.csv"
GATE_AUTOMATON_TABLES = (
    GATE_AUTOMATON_DIR / "signature_boundary_spine_gate_automaton_tables.npz"
)
GATE_AUTOMATON_CERTIFICATE = (
    GATE_AUTOMATON_DIR / "signature_boundary_spine_gate_automaton_certificate.json"
)

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_JSON = REWRITE_COMPLEX_DIR / "rewrite_complex.json"
REWRITE_COMPLEX_NODE_CSV = REWRITE_COMPLEX_DIR / "rewrite_complex_nodes.csv"
REWRITE_COMPLEX_EDGE_CSV = REWRITE_COMPLEX_DIR / "rewrite_complex_edges.csv"
REWRITE_COMPLEX_TABLES = REWRITE_COMPLEX_DIR / "rewrite_complex_tables.npz"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"

DERIVE_SCRIPT = (
    ROOT / "src" / "derive_c985_d20_signature_boundary_spine_language_graph.py"
)
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_spine_language_graph.py"
)

APERTURE_NODE_ID = 44
APERTURE_NODE_WORD = "x2 x4 x5"
EXPECTED_CANONICAL_SEQUENCE = [20, 5, 1, 8, 23, 32, 32, 51, 51, 51, 51, 48]
EXPECTED_LANGUAGE_PATH_NODES = [20, 5, 1, 8, 23, 32, 51, 48]
EXPECTED_BOUNDARY_ENDPOINTS = [20, 48]
EXPECTED_MISSING_GATE_SYMBOL_BITSET = (1 << 2) | (1 << 4)

LANGUAGE_NODE_COLUMNS = [
    "language_node_rank",
    "rewrite_node_id",
    "canonical_symbol_bitset",
    "language_degree",
    "language_boundary_flag",
    "source_to_branch_window_count",
    "first_window_id",
    "last_window_id",
    "rewrite_complex_degree",
    "sector_coverage_count",
    "signature_union_count",
    "distance_to_aperture_node",
    "nearest_aperture_flag",
    "ambient_eccentricity_within_language",
]

LANGUAGE_EDGE_COLUMNS = [
    "language_edge_id",
    "source_language_node_rank",
    "target_language_node_rank",
    "source_rewrite_node_id",
    "target_rewrite_node_id",
    "transition_count",
    "ambient_rewrite_distance",
    "source_signature_union_count",
    "target_signature_union_count",
    "signature_union_delta_abs",
]

LANGUAGE_TRANSITION_COLUMNS = [
    "language_transition_id",
    "from_window_id",
    "to_window_id",
    "source_rewrite_node_id",
    "target_rewrite_node_id",
    "source_language_node_rank",
    "target_language_node_rank",
    "self_loop_flag",
    "language_edge_metric_flag",
    "ambient_rewrite_distance",
]

LANGUAGE_SHORTCUT_COLUMNS = [
    "shortcut_id",
    "source_language_node_rank",
    "target_language_node_rank",
    "source_rewrite_node_id",
    "target_rewrite_node_id",
    "language_distance",
    "ambient_rewrite_distance",
    "language_minus_ambient_distance",
    "source_signature_union_count",
    "target_signature_union_count",
]

LANGUAGE_APERTURE_COLUMNS = [
    "language_node_rank",
    "rewrite_node_id",
    "aperture_node_id",
    "ambient_rewrite_distance_to_aperture",
    "nearest_aperture_flag",
    "language_boundary_flag",
    "signature_union_count",
    "aperture_signature_union_count",
    "signature_gap_to_aperture",
]

LANGUAGE_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "language_node_count": 0,
    "language_edge_count": 1,
    "language_transition_count": 2,
    "language_self_loop_transition_count": 3,
    "language_boundary_node_count": 4,
    "language_graph_diameter": 5,
    "language_graph_radius": 6,
    "language_gromov_delta_twice": 7,
    "ambient_induced_edge_count": 8,
    "ambient_shortcut_edge_count": 9,
    "max_language_to_ambient_distance_gap": 10,
    "endpoint_language_distance": 11,
    "endpoint_ambient_distance": 12,
    "aperture_node_id": 13,
    "aperture_signature_union_count": 14,
    "observed_signature_union_max": 15,
    "aperture_signature_gap": 16,
    "aperture_min_ambient_distance": 17,
    "observed_gate_symbol_bitset": 18,
    "missing_gate_symbol_bitset": 19,
}


def ordered_unique(values: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []
    for value in values:
        if int(value) not in seen:
            seen.add(int(value))
            result.append(int(value))
    return result


def shortest_paths(adjacency: np.ndarray) -> np.ndarray:
    node_count = int(adjacency.shape[0])
    distances = np.full((node_count, node_count), 10**9, dtype=np.int64)
    neighbors = [
        np.flatnonzero(adjacency[node]).astype(np.int64).tolist()
        for node in range(node_count)
    ]
    for source in range(node_count):
        distances[source, source] = 0
        queue: deque[int] = deque([source])
        while queue:
            node = queue.popleft()
            for neighbor in neighbors[node]:
                if distances[source, neighbor] == 10**9:
                    distances[source, neighbor] = distances[source, node] + 1
                    queue.append(neighbor)
    return distances


def gromov_delta_witness(distances: np.ndarray) -> dict[str, Any]:
    best_delta_twice = -1
    best_witness: tuple[int, int, int, int] | None = None
    best_sums: list[int] = []
    for a, b, c, d in itertools.combinations(range(int(distances.shape[0])), 4):
        sums = sorted(
            [
                int(distances[a, b] + distances[c, d]),
                int(distances[a, c] + distances[b, d]),
                int(distances[a, d] + distances[b, c]),
            ]
        )
        delta_twice = sums[2] - sums[1]
        if delta_twice > best_delta_twice:
            best_delta_twice = delta_twice
            best_witness = (a, b, c, d)
            best_sums = sums
    if best_witness is None:
        raise AssertionError("language graph needs at least four nodes")
    return {
        "delta": float(best_delta_twice / 2.0),
        "delta_twice": int(best_delta_twice),
        "witness_language_ranks": [int(x) for x in best_witness],
        "four_point_sums": [int(x) for x in best_sums],
    }


def node_signature(node_by_id: dict[int, dict[str, Any]], node_id: int) -> int:
    return int(node_by_id[int(node_id)]["signature_union_count"])


def node_word(node_by_id: dict[int, dict[str, Any]], node_id: int) -> str:
    return str(node_by_id[int(node_id)]["canonical_word"])


def build_payloads() -> dict[str, Any]:
    gate_report = load_json(GATE_AUTOMATON_REPORT)
    gate_automaton = load_json(GATE_AUTOMATON_JSON)
    gate_certificate = load_json(GATE_AUTOMATON_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)

    gate_tables = np.load(GATE_AUTOMATON_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    gate_transition_table = np.asarray(
        gate_tables["gate_automaton_transition_table"], dtype=np.int64
    )
    gate_branch_word_table = np.asarray(
        gate_tables["gate_branch_word_table"], dtype=np.int64
    )
    gate_trigram_table = np.asarray(
        gate_tables["gate_trigram_window_table"], dtype=np.int64
    )
    rewrite_node_table = np.asarray(rewrite_tables["node_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    rewrite_adjacency = np.asarray(rewrite_tables["adjacency"], dtype=np.int8)
    rewrite_distances = np.asarray(rewrite_tables["graph_distances"], dtype=np.int64)

    trigram_rows = read_int_csv(GATE_AUTOMATON_TRIGRAMS)
    canonical_sequence = [int(row["canonical_triple_id"]) for row in trigram_rows]
    language_path_nodes = ordered_unique(canonical_sequence)
    rank_by_node = {node_id: rank for rank, node_id in enumerate(language_path_nodes)}
    node_by_id = {int(row["node_id"]): row for row in rewrite_complex["nodes"]}
    aperture_node = node_by_id[APERTURE_NODE_ID]
    aperture_signature = node_signature(node_by_id, APERTURE_NODE_ID)

    language_adjacency = np.zeros(
        (len(language_path_nodes), len(language_path_nodes)),
        dtype=np.int8,
    )
    transition_pair_counts = Counter(
        (int(source), int(target))
        for source, target in zip(canonical_sequence, canonical_sequence[1:])
    )
    language_edge_counts: Counter[tuple[int, int]] = Counter()
    language_edge_order: list[tuple[int, int]] = []
    transition_rows: list[dict[str, int]] = []
    for index, (source, target) in enumerate(
        zip(canonical_sequence, canonical_sequence[1:]),
        start=1,
    ):
        source_rank = rank_by_node[int(source)]
        target_rank = rank_by_node[int(target)]
        self_loop = int(source == target)
        if not self_loop:
            key = tuple(sorted((int(source), int(target))))
            if key not in language_edge_counts:
                language_edge_order.append((int(source), int(target)))
            language_edge_counts[key] += 1
            language_adjacency[source_rank, target_rank] = 1
            language_adjacency[target_rank, source_rank] = 1
        transition_rows.append(
            {
                "language_transition_id": index,
                "from_window_id": index,
                "to_window_id": index + 1,
                "source_rewrite_node_id": int(source),
                "target_rewrite_node_id": int(target),
                "source_language_node_rank": source_rank,
                "target_language_node_rank": target_rank,
                "self_loop_flag": self_loop,
                "language_edge_metric_flag": int(not self_loop),
                "ambient_rewrite_distance": int(
                    rewrite_distances[int(source), int(target)]
                ),
            }
        )

    language_distances = shortest_paths(language_adjacency)
    ambient_observed_distances = rewrite_distances[np.ix_(language_path_nodes, language_path_nodes)]
    language_delta = gromov_delta_witness(language_distances)
    language_degrees = np.asarray(language_adjacency.sum(axis=1), dtype=np.int64)
    boundary_endpoint_ids = [
        int(language_path_nodes[index])
        for index, degree in enumerate(language_degrees)
        if int(degree) == 1
    ]

    aperture_distances = [
        int(rewrite_distances[node_id, APERTURE_NODE_ID])
        for node_id in language_path_nodes
    ]
    aperture_min_distance = min(aperture_distances)
    nearest_aperture_ids = [
        int(node_id)
        for node_id, distance in zip(language_path_nodes, aperture_distances)
        if int(distance) == aperture_min_distance
    ]

    window_ids_by_node: dict[int, list[int]] = {}
    symbols_by_node: dict[int, list[int]] = {}
    for row in trigram_rows:
        node_id = int(row["canonical_triple_id"])
        window_ids_by_node.setdefault(node_id, []).append(int(row["window_id"]))
        symbols_by_node[node_id] = [
            int(row["canonical_first_symbol_id"]),
            int(row["canonical_second_symbol_id"]),
            int(row["canonical_third_symbol_id"]),
        ]

    language_node_rows: list[dict[str, int]] = []
    for rank, node_id in enumerate(language_path_nodes):
        windows = window_ids_by_node[int(node_id)]
        node = node_by_id[int(node_id)]
        language_node_rows.append(
            {
                "language_node_rank": rank,
                "rewrite_node_id": int(node_id),
                "canonical_symbol_bitset": bitset(symbols_by_node[int(node_id)]),
                "language_degree": int(language_degrees[rank]),
                "language_boundary_flag": int(language_degrees[rank] == 1),
                "source_to_branch_window_count": len(windows),
                "first_window_id": min(windows),
                "last_window_id": max(windows),
                "rewrite_complex_degree": int(node["graph_degree"]),
                "sector_coverage_count": int(node["sector_coverage_count"]),
                "signature_union_count": int(node["signature_union_count"]),
                "distance_to_aperture_node": int(
                    rewrite_distances[int(node_id), APERTURE_NODE_ID]
                ),
                "nearest_aperture_flag": int(
                    rewrite_distances[int(node_id), APERTURE_NODE_ID]
                    == aperture_min_distance
                ),
                "ambient_eccentricity_within_language": int(
                    np.max(ambient_observed_distances[rank])
                ),
            }
        )

    language_edge_rows: list[dict[str, int]] = []
    for edge_id, (source, target) in enumerate(language_edge_order):
        key = tuple(sorted((int(source), int(target))))
        language_edge_rows.append(
            {
                "language_edge_id": edge_id,
                "source_language_node_rank": rank_by_node[int(source)],
                "target_language_node_rank": rank_by_node[int(target)],
                "source_rewrite_node_id": int(source),
                "target_rewrite_node_id": int(target),
                "transition_count": int(language_edge_counts[key]),
                "ambient_rewrite_distance": int(
                    rewrite_distances[int(source), int(target)]
                ),
                "source_signature_union_count": node_signature(node_by_id, source),
                "target_signature_union_count": node_signature(node_by_id, target),
                "signature_union_delta_abs": abs(
                    node_signature(node_by_id, source)
                    - node_signature(node_by_id, target)
                ),
            }
        )

    observed_node_set = set(language_path_nodes)
    language_undirected_edges = {
        tuple(sorted((int(row["source_rewrite_node_id"]), int(row["target_rewrite_node_id"]))))
        for row in language_edge_rows
    }
    ambient_induced_edges = [
        (source, target)
        for source, target in itertools.combinations(sorted(observed_node_set), 2)
        if int(rewrite_adjacency[source, target]) == 1
    ]
    ambient_shortcuts = [
        edge for edge in ambient_induced_edges if tuple(sorted(edge)) not in language_undirected_edges
    ]
    shortcut_rows: list[dict[str, int]] = []
    for shortcut_id, (left, right) in enumerate(ambient_shortcuts):
        source, target = sorted((left, right), key=lambda node_id: rank_by_node[node_id])
        source_rank = rank_by_node[source]
        target_rank = rank_by_node[target]
        language_distance = int(language_distances[source_rank, target_rank])
        ambient_distance = int(rewrite_distances[source, target])
        shortcut_rows.append(
            {
                "shortcut_id": shortcut_id,
                "source_language_node_rank": source_rank,
                "target_language_node_rank": target_rank,
                "source_rewrite_node_id": int(source),
                "target_rewrite_node_id": int(target),
                "language_distance": language_distance,
                "ambient_rewrite_distance": ambient_distance,
                "language_minus_ambient_distance": language_distance - ambient_distance,
                "source_signature_union_count": node_signature(node_by_id, source),
                "target_signature_union_count": node_signature(node_by_id, target),
            }
        )

    aperture_rows: list[dict[str, int]] = []
    for rank, node_id in enumerate(language_path_nodes):
        signature = node_signature(node_by_id, node_id)
        aperture_rows.append(
            {
                "language_node_rank": rank,
                "rewrite_node_id": int(node_id),
                "aperture_node_id": APERTURE_NODE_ID,
                "ambient_rewrite_distance_to_aperture": int(
                    rewrite_distances[int(node_id), APERTURE_NODE_ID]
                ),
                "nearest_aperture_flag": int(node_id in nearest_aperture_ids),
                "language_boundary_flag": int(node_id in boundary_endpoint_ids),
                "signature_union_count": signature,
                "aperture_signature_union_count": aperture_signature,
                "signature_gap_to_aperture": aperture_signature - signature,
            }
        )

    pair_records: list[dict[str, int]] = []
    for source, target in itertools.combinations(language_path_nodes, 2):
        source_rank = rank_by_node[source]
        target_rank = rank_by_node[target]
        language_distance = int(language_distances[source_rank, target_rank])
        ambient_distance = int(rewrite_distances[source, target])
        pair_records.append(
            {
                "source_rewrite_node_id": int(source),
                "target_rewrite_node_id": int(target),
                "source_language_node_rank": source_rank,
                "target_language_node_rank": target_rank,
                "language_distance": language_distance,
                "ambient_rewrite_distance": ambient_distance,
                "language_minus_ambient_distance": language_distance
                - ambient_distance,
            }
        )
    max_gap = max(
        int(row["language_minus_ambient_distance"]) for row in pair_records
    )
    max_gap_pairs = [
        row
        for row in pair_records
        if int(row["language_minus_ambient_distance"]) == max_gap
    ]
    endpoint_language_distance = int(
        language_distances[
            rank_by_node[EXPECTED_BOUNDARY_ENDPOINTS[0]],
            rank_by_node[EXPECTED_BOUNDARY_ENDPOINTS[1]],
        ]
    )
    endpoint_ambient_distance = int(
        rewrite_distances[EXPECTED_BOUNDARY_ENDPOINTS[0], EXPECTED_BOUNDARY_ENDPOINTS[1]]
    )
    observed_signature_max = max(
        node_signature(node_by_id, node_id) for node_id in language_path_nodes
    )
    source_to_branch_symbols = gate_report["witness"]["gate_symbol_sequence"][:14]
    observed_gate_symbol_bitset = bitset([int(symbol) for symbol in source_to_branch_symbols])
    missing_gate_symbol_bitset = ((1 << 6) - 1) & ~observed_gate_symbol_bitset

    observable_values = {
        "language_node_count": len(language_path_nodes),
        "language_edge_count": len(language_edge_rows),
        "language_transition_count": len(transition_rows),
        "language_self_loop_transition_count": sum(
            int(row["self_loop_flag"]) for row in transition_rows
        ),
        "language_boundary_node_count": len(boundary_endpoint_ids),
        "language_graph_diameter": int(np.max(language_distances)),
        "language_graph_radius": int(np.min(np.max(language_distances, axis=1))),
        "language_gromov_delta_twice": int(language_delta["delta_twice"]),
        "ambient_induced_edge_count": len(ambient_induced_edges),
        "ambient_shortcut_edge_count": len(ambient_shortcuts),
        "max_language_to_ambient_distance_gap": max_gap,
        "endpoint_language_distance": endpoint_language_distance,
        "endpoint_ambient_distance": endpoint_ambient_distance,
        "aperture_node_id": APERTURE_NODE_ID,
        "aperture_signature_union_count": aperture_signature,
        "observed_signature_union_max": observed_signature_max,
        "aperture_signature_gap": aperture_signature - observed_signature_max,
        "aperture_min_ambient_distance": aperture_min_distance,
        "observed_gate_symbol_bitset": observed_gate_symbol_bitset,
        "missing_gate_symbol_bitset": missing_gate_symbol_bitset,
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": code,
            "value_x1e12": int(observable_values[name]),
            "aux_id": 0,
        }
        for index, (name, code) in enumerate(
            sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
        )
    ]

    language_node_table = table_from_rows(LANGUAGE_NODE_COLUMNS, language_node_rows)
    language_edge_table = table_from_rows(LANGUAGE_EDGE_COLUMNS, language_edge_rows)
    language_transition_table = table_from_rows(
        LANGUAGE_TRANSITION_COLUMNS,
        transition_rows,
    )
    language_shortcut_table = table_from_rows(
        LANGUAGE_SHORTCUT_COLUMNS,
        shortcut_rows,
    )
    language_aperture_table = table_from_rows(
        LANGUAGE_APERTURE_COLUMNS,
        aperture_rows,
    )
    language_observable_table = table_from_rows(
        LANGUAGE_OBSERVABLE_COLUMNS,
        observable_rows,
    )

    checks = {
        "gate_automaton_report_certified": gate_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED",
        "gate_automaton_certificate_certified": gate_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_GATE_AUTOMATON_CERTIFIED",
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "gate_automaton_schema_available": gate_automaton.get("schema")
        == "c985.d20_signature_boundary_spine_gate_automaton@1",
        "rewrite_complex_schema_available": rewrite_complex.get("schema")
        == "c985.d20_rewrite_complex_hyperbolicity@1",
        "gate_automaton_tables_available": (
            "gate_automaton_transition_table" in gate_tables.files
            and "gate_trigram_window_table" in gate_tables.files
        ),
        "rewrite_complex_tables_available": (
            "adjacency" in rewrite_tables.files
            and "graph_distances" in rewrite_tables.files
        ),
        "gate_transition_table_shape_is_16_by_16": tuple(gate_transition_table.shape)
        == (16, 16),
        "gate_branch_word_table_shape_is_6_by_14": tuple(gate_branch_word_table.shape)
        == (6, 14),
        "gate_trigram_table_shape_is_12_by_20": tuple(gate_trigram_table.shape)
        == (12, 20),
        "rewrite_node_table_shape_is_56_by_17": tuple(rewrite_node_table.shape)
        == (56, 17),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "canonical_window_sequence_matches_expected": canonical_sequence
        == EXPECTED_CANONICAL_SEQUENCE,
        "language_path_nodes_match_first_occurrence_order": language_path_nodes
        == EXPECTED_LANGUAGE_PATH_NODES,
        "language_node_count_is_8": len(language_path_nodes) == 8,
        "language_edge_count_is_7": len(language_edge_rows) == 7,
        "language_transition_count_is_11": len(transition_rows) == 11,
        "language_self_loop_transition_count_is_4": observable_values[
            "language_self_loop_transition_count"
        ]
        == 4,
        "language_graph_connected": bool(np.all(language_distances < 10**9)),
        "language_graph_diameter_is_7": observable_values["language_graph_diameter"]
        == 7,
        "language_graph_radius_is_4": observable_values["language_graph_radius"]
        == 4,
        "language_gromov_delta_is_0": language_delta["delta_twice"] == 0,
        "language_boundary_endpoints_are_20_48": boundary_endpoint_ids
        == EXPECTED_BOUNDARY_ENDPOINTS,
        "all_language_edges_are_rewrite_complex_edges": all(
            int(row["ambient_rewrite_distance"]) == 1 for row in language_edge_rows
        ),
        "ambient_induced_edge_count_is_10": len(ambient_induced_edges) == 10,
        "ambient_shortcut_edge_count_is_3": len(ambient_shortcuts) == 3,
        "boundary_endpoint_language_distance_is_7": endpoint_language_distance == 7,
        "boundary_endpoint_ambient_distance_is_2": endpoint_ambient_distance == 2,
        "max_language_to_ambient_gap_is_5": max_gap == 5,
        "aperture_node_is_44": APERTURE_NODE_ID == 44
        and node_word(node_by_id, APERTURE_NODE_ID) == APERTURE_NODE_WORD,
        "aperture_absent_from_language_nodes": APERTURE_NODE_ID
        not in set(language_path_nodes),
        "aperture_min_ambient_distance_is_2": aperture_min_distance == 2,
        "nearest_aperture_nodes_match_expected": nearest_aperture_ids
        == [20, 5, 32, 51, 48],
        "observed_max_signature_is_175": observed_signature_max == 175,
        "aperture_signature_is_185": aperture_signature == 185,
        "aperture_signature_gap_is_10": aperture_signature - observed_signature_max
        == 10,
        "source_to_branch_gate_symbols_omit_x2_x4": (
            observed_gate_symbol_bitset,
            missing_gate_symbol_bitset,
        )
        == (43, EXPECTED_MISSING_GATE_SYMBOL_BITSET),
        "language_node_table_shape_is_8_by_14": tuple(language_node_table.shape)
        == (8, len(LANGUAGE_NODE_COLUMNS)),
        "language_edge_table_shape_is_7_by_10": tuple(language_edge_table.shape)
        == (7, len(LANGUAGE_EDGE_COLUMNS)),
        "language_transition_table_shape_is_11_by_10": tuple(
            language_transition_table.shape
        )
        == (11, len(LANGUAGE_TRANSITION_COLUMNS)),
        "language_shortcut_table_shape_is_3_by_10": tuple(
            language_shortcut_table.shape
        )
        == (3, len(LANGUAGE_SHORTCUT_COLUMNS)),
        "language_aperture_table_shape_is_8_by_9": tuple(
            language_aperture_table.shape
        )
        == (8, len(LANGUAGE_APERTURE_COLUMNS)),
        "language_observable_table_shape_matches_codebook": tuple(
            language_observable_table.shape
        )
        == (len(OBSERVABLE_CODES), len(LANGUAGE_OBSERVABLE_COLUMNS)),
    }

    witness = {
        "canonical_window_sequence": canonical_sequence,
        "language_path_node_ids": language_path_nodes,
        "language_path_node_words": [
            node_word(node_by_id, node_id) for node_id in language_path_nodes
        ],
        "language_edge_node_pairs": [
            [
                int(row["source_rewrite_node_id"]),
                int(row["target_rewrite_node_id"]),
            ]
            for row in language_edge_rows
        ],
        "language_self_loop_transition_count": observable_values[
            "language_self_loop_transition_count"
        ],
        "language_transition_pair_multiplicities": [
            {
                "source_rewrite_node_id": int(source),
                "target_rewrite_node_id": int(target),
                "count": int(count),
            }
            for (source, target), count in sorted(transition_pair_counts.items())
        ],
        "language_graph_diameter": observable_values["language_graph_diameter"],
        "language_graph_radius": observable_values["language_graph_radius"],
        "language_gromov_delta": language_delta["delta"],
        "language_gromov_delta_twice": language_delta["delta_twice"],
        "language_delta_witness_ranks": language_delta["witness_language_ranks"],
        "language_boundary_endpoint_node_ids": boundary_endpoint_ids,
        "boundary_endpoint_language_distance": endpoint_language_distance,
        "boundary_endpoint_ambient_distance": endpoint_ambient_distance,
        "ambient_induced_edge_count": len(ambient_induced_edges),
        "ambient_shortcut_edges": [
            {
                "source_rewrite_node_id": int(row["source_rewrite_node_id"]),
                "target_rewrite_node_id": int(row["target_rewrite_node_id"]),
                "language_distance": int(row["language_distance"]),
                "ambient_rewrite_distance": int(row["ambient_rewrite_distance"]),
                "language_minus_ambient_distance": int(
                    row["language_minus_ambient_distance"]
                ),
            }
            for row in shortcut_rows
        ],
        "max_language_to_ambient_gap": max_gap,
        "max_language_to_ambient_gap_pairs": max_gap_pairs,
        "language_distance_histogram": histogram(
            [
                int(language_distances[source, target])
                for source, target in itertools.combinations(
                    range(len(language_path_nodes)),
                    2,
                )
            ]
        ),
        "ambient_observed_distance_histogram": histogram(
            [
                int(ambient_observed_distances[source, target])
                for source, target in itertools.combinations(
                    range(len(language_path_nodes)),
                    2,
                )
            ]
        ),
        "aperture_node": {
            "node_id": APERTURE_NODE_ID,
            "canonical_word": node_word(node_by_id, APERTURE_NODE_ID),
            "canonical_atom_ids": aperture_node["canonical_atom_ids"],
            "signature_union_count": aperture_signature,
            "sector_coverage_count": int(aperture_node["sector_coverage_count"]),
            "graph_degree": int(aperture_node["graph_degree"]),
        },
        "aperture_nearest_language_node_ids": nearest_aperture_ids,
        "aperture_min_ambient_distance": aperture_min_distance,
        "observed_signature_union_max": observed_signature_max,
        "aperture_signature_gap": aperture_signature - observed_signature_max,
        "observed_gate_symbol_bitset": observed_gate_symbol_bitset,
        "missing_gate_symbol_bitset": missing_gate_symbol_bitset,
        "missing_gate_symbol_count": popcount(missing_gate_symbol_bitset),
        "language_node_table_sha256": sha_array(language_node_table),
        "language_edge_table_sha256": sha_array(language_edge_table),
        "language_transition_table_sha256": sha_array(language_transition_table),
        "language_shortcut_table_sha256": sha_array(language_shortcut_table),
        "language_aperture_table_sha256": sha_array(language_aperture_table),
        "language_adjacency_sha256": sha_array(language_adjacency),
        "language_distances_sha256": sha_array(language_distances),
        "ambient_observed_distances_sha256": sha_array(ambient_observed_distances),
        "language_observable_table_sha256": sha_array(language_observable_table),
    }

    language_graph = {
        "schema": "c985.d20_signature_boundary_spine_language_graph@1",
        "object": "d20",
        "language_graph_rule": {
            "source": "certified gate-automaton source-to-branch trigram windows",
            "nodes": "first-occurrence ordered canonical trigram normal forms observed by the gate language",
            "edges": "non-self consecutive canonical trigram transitions in the accepted source-to-branch readout",
            "metric": "unweighted shortest-path metric on the observed finite language graph",
            "ambient_comparison": "restrict the 56-node symbolic rewrite-complex metric to the observed trigram nodes",
            "aperture": "the absent full-sector max-signature rewrite node x2 x4 x5",
        },
        "canonical_window_sequence": canonical_sequence,
        "language_path_node_ids": language_path_nodes,
        "language_boundary_endpoint_node_ids": boundary_endpoint_ids,
        "language_nodes": [
            {
                **row,
                "canonical_word": node_word(node_by_id, row["rewrite_node_id"]),
            }
            for row in language_node_rows
        ],
        "language_edges": [
            {
                **row,
                "source_word": node_word(node_by_id, row["source_rewrite_node_id"]),
                "target_word": node_word(node_by_id, row["target_rewrite_node_id"]),
            }
            for row in language_edge_rows
        ],
        "ambient_shortcuts": [
            {
                **row,
                "source_word": node_word(node_by_id, row["source_rewrite_node_id"]),
                "target_word": node_word(node_by_id, row["target_rewrite_node_id"]),
            }
            for row in shortcut_rows
        ],
        "aperture_distances": [
            {
                **row,
                "canonical_word": node_word(node_by_id, row["rewrite_node_id"]),
            }
            for row in aperture_rows
        ],
        "summary": {
            "language_node_count": len(language_path_nodes),
            "language_edge_count": len(language_edge_rows),
            "language_transition_count": len(transition_rows),
            "language_self_loop_transition_count": observable_values[
                "language_self_loop_transition_count"
            ],
            "language_graph_diameter": observable_values["language_graph_diameter"],
            "language_graph_radius": observable_values["language_graph_radius"],
            "language_gromov_delta": language_delta["delta"],
            "ambient_induced_edge_count": len(ambient_induced_edges),
            "ambient_shortcut_edge_count": len(ambient_shortcuts),
            "boundary_endpoint_language_distance": endpoint_language_distance,
            "boundary_endpoint_ambient_distance": endpoint_ambient_distance,
            "max_language_to_ambient_gap": max_gap,
            "aperture_node": witness["aperture_node"],
            "aperture_nearest_language_node_ids": nearest_aperture_ids,
            "aperture_min_ambient_distance": aperture_min_distance,
            "aperture_signature_gap": aperture_signature - observed_signature_max,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_language_graph_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_LANGUAGE_GRAPH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the source-to-branch gate language induces an eight-node canonical trigram path",
            "the observed language graph is a tree path with exact Gromov delta 0",
            "the two language-boundary endpoints are nodes 20 and 48 at language distance 7",
            "the ambient 56-node rewrite complex compresses that endpoint distance to 2",
            "the absent x2/x4 max-signature aperture node 44 remains two ambient rewrite steps from the observed language",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_language_graph@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The gate automaton's accepted trigram readout forms an eight-node "
            "hyperbolic language path with exact delta 0. Its finite boundary "
            "is compressed by ambient rewrite-complex shortcuts, while the "
            "missing x2/x4 max-signature aperture remains at ambient distance 2."
        ),
        "stage_protocol": {
            "draft": "view accepted gate trigrams as a first-occurrence canonical language graph",
            "witness": "materialize language nodes, transitions, ambient shortcuts, and aperture distances",
            "coherence": "check exact path metric, Gromov delta, ambient restriction, and missing-symbol aperture",
            "closure": "certify the finite observed language graph without claiming arbitrary gate-word recognition",
            "emit": "emit language-graph JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "gate_automaton_report": input_entry(
                GATE_AUTOMATON_REPORT,
                {
                    "status": gate_report.get("status"),
                    "certificate_sha256": gate_report.get("certificate_sha256"),
                },
            ),
            "gate_automaton": input_entry(GATE_AUTOMATON_JSON),
            "gate_automaton_transitions": input_entry(GATE_AUTOMATON_TRANSITIONS),
            "gate_automaton_branch_words": input_entry(GATE_AUTOMATON_BRANCH_WORDS),
            "gate_automaton_trigrams": input_entry(GATE_AUTOMATON_TRIGRAMS),
            "gate_automaton_observables": input_entry(GATE_AUTOMATON_OBSERVABLES),
            "gate_automaton_tables": input_entry(GATE_AUTOMATON_TABLES),
            "gate_automaton_certificate": input_entry(GATE_AUTOMATON_CERTIFICATE),
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex": input_entry(REWRITE_COMPLEX_JSON),
            "rewrite_complex_nodes": input_entry(REWRITE_COMPLEX_NODE_CSV),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGE_CSV),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_language_graph": relpath(
                OUT_DIR / "signature_boundary_spine_language_graph.json"
            ),
            "language_graph_nodes_csv": relpath(
                OUT_DIR / "language_graph_nodes.csv"
            ),
            "language_graph_edges_csv": relpath(
                OUT_DIR / "language_graph_edges.csv"
            ),
            "language_trigram_transitions_csv": relpath(
                OUT_DIR / "language_trigram_transitions.csv"
            ),
            "language_ambient_shortcuts_csv": relpath(
                OUT_DIR / "language_ambient_shortcuts.csv"
            ),
            "language_aperture_distances_csv": relpath(
                OUT_DIR / "language_aperture_distances.csv"
            ),
            "language_graph_observables_csv": relpath(
                OUT_DIR / "language_graph_observables.csv"
            ),
            "signature_boundary_spine_language_graph_tables": relpath(
                OUT_DIR / "signature_boundary_spine_language_graph_tables.npz"
            ),
            "signature_boundary_spine_language_graph_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_language_graph_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the finite language graph induced by observed gate-automaton trigram normal forms",
                "exact shortest-path distances, diameter, radius, and Gromov delta for that language graph",
                "ambient rewrite-complex distances among observed language nodes",
                "the distance-2 missing-symbol aperture at node 44",
                "the signature gap between observed gate language maximum 175 and aperture maximum 185",
            ],
            "does_not_certify_because_not_required": [
                "regular-language recognition for unobserved gate-letter words",
                "minimal deterministic automata for alternative branch rankings",
                "ambient geodesic uniqueness in the 56-node rewrite complex",
                "new associator, pentagon, braiding, center, or tube-algebra data",
            ],
        },
        "next_highest_yield_item": (
            "Enumerate the ambient geodesic fan from the language boundary to "
            "the aperture node 44, then certify which shortest rewrite paths "
            "restore x2/x4 while preserving full-sector coverage and high "
            "signature mass."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_language_graph_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified gate-automaton and rewrite-complex artifacts",
            "project accepted gate trigrams to canonical rewrite nodes",
            "construct the observed language graph and exact shortest-path metric",
            "compare observed distances with ambient rewrite-complex distances",
            "check missing x2/x4 aperture distance, source hashes, and registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_language_graph": language_graph,
        "language_graph_nodes_csv": csv_text(
            LANGUAGE_NODE_COLUMNS,
            language_node_rows,
        ),
        "language_graph_edges_csv": csv_text(
            LANGUAGE_EDGE_COLUMNS,
            language_edge_rows,
        ),
        "language_trigram_transitions_csv": csv_text(
            LANGUAGE_TRANSITION_COLUMNS,
            transition_rows,
        ),
        "language_ambient_shortcuts_csv": csv_text(
            LANGUAGE_SHORTCUT_COLUMNS,
            shortcut_rows,
        ),
        "language_aperture_distances_csv": csv_text(
            LANGUAGE_APERTURE_COLUMNS,
            aperture_rows,
        ),
        "language_graph_observables_csv": csv_text(
            LANGUAGE_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "language_node_table": language_node_table,
        "language_edge_table": language_edge_table,
        "language_transition_table": language_transition_table,
        "language_shortcut_table": language_shortcut_table,
        "language_aperture_table": language_aperture_table,
        "language_adjacency": language_adjacency,
        "language_distances": language_distances,
        "ambient_observed_distances": ambient_observed_distances,
        "language_observable_table": language_observable_table,
        "signature_boundary_spine_language_graph_certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(
        OUT_DIR / "signature_boundary_spine_language_graph.json",
        payloads["signature_boundary_spine_language_graph"],
    )
    (OUT_DIR / "language_graph_nodes.csv").write_text(
        payloads["language_graph_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "language_graph_edges.csv").write_text(
        payloads["language_graph_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "language_trigram_transitions.csv").write_text(
        payloads["language_trigram_transitions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "language_ambient_shortcuts.csv").write_text(
        payloads["language_ambient_shortcuts_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "language_aperture_distances.csv").write_text(
        payloads["language_aperture_distances_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "language_graph_observables.csv").write_text(
        payloads["language_graph_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_language_graph_tables.npz",
        language_node_table=payloads["language_node_table"],
        language_edge_table=payloads["language_edge_table"],
        language_transition_table=payloads["language_transition_table"],
        language_shortcut_table=payloads["language_shortcut_table"],
        language_aperture_table=payloads["language_aperture_table"],
        language_adjacency=payloads["language_adjacency"],
        language_distances=payloads["language_distances"],
        ambient_observed_distances=payloads["ambient_observed_distances"],
        language_observable_table=payloads["language_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_language_graph_certificate.json",
        payloads["signature_boundary_spine_language_graph_certificate"],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "language_path_node_ids": witness["language_path_node_ids"],
                "language_graph_diameter": witness["language_graph_diameter"],
                "language_gromov_delta": witness["language_gromov_delta"],
                "boundary_endpoint_ambient_distance": witness[
                    "boundary_endpoint_ambient_distance"
                ],
                "aperture_min_ambient_distance": witness[
                    "aperture_min_ambient_distance"
                ],
                "aperture_signature_gap": witness["aperture_signature_gap"],
                "next_highest_yield_item": payloads["report"][
                    "next_highest_yield_item"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
