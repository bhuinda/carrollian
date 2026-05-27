from __future__ import annotations

import itertools
import json
from collections import deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_rewrite_complex_hyperbolicity import (
        OUT_DIR as REWRITE_COMPLEX_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_geodesic_fan import (
        OUT_DIR as APERTURE_FAN_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_language_graph import (
        OUT_DIR as LANGUAGE_GRAPH_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_signature_boundary_spine_x2_x4_aperture_completion import (
        OUT_DIR as APERTURE_COMPLETION_DIR,
    )
    from .derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text
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
    from derive_c985_d20_rewrite_complex_hyperbolicity import (
        OUT_DIR as REWRITE_COMPLEX_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_geodesic_fan import (
        OUT_DIR as APERTURE_FAN_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_language_graph import (
        OUT_DIR as LANGUAGE_GRAPH_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_signature_boundary_spine_x2_x4_aperture_completion import (
        OUT_DIR as APERTURE_COMPLETION_DIR,
    )
    from derive_c985_d20_symbolic_associativity import (
        OUT_DIR as SYMBOLIC_ASSOCIATIVITY_DIR,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_cycle_language"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_LANGUAGE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

APERTURE_COMPLETION_REPORT = APERTURE_COMPLETION_DIR / "report.json"
APERTURE_COMPLETION_JSON = (
    APERTURE_COMPLETION_DIR
    / "signature_boundary_spine_x2_x4_aperture_completion.json"
)
APERTURE_COMPLETION_PATHS = (
    APERTURE_COMPLETION_DIR / "x2_x4_aperture_completion_paths.csv"
)
APERTURE_COMPLETION_TABLES = (
    APERTURE_COMPLETION_DIR
    / "signature_boundary_spine_x2_x4_aperture_completion_tables.npz"
)
APERTURE_COMPLETION_CERTIFICATE = (
    APERTURE_COMPLETION_DIR
    / "signature_boundary_spine_x2_x4_aperture_completion_certificate.json"
)

APERTURE_FAN_REPORT = APERTURE_FAN_DIR / "report.json"
APERTURE_FAN_PATHS = APERTURE_FAN_DIR / "aperture_geodesic_paths.csv"
APERTURE_FAN_TABLES = (
    APERTURE_FAN_DIR / "signature_boundary_spine_aperture_geodesic_fan_tables.npz"
)
APERTURE_FAN_CERTIFICATE = (
    APERTURE_FAN_DIR / "signature_boundary_spine_aperture_geodesic_fan_certificate.json"
)

LANGUAGE_GRAPH_REPORT = LANGUAGE_GRAPH_DIR / "report.json"
LANGUAGE_GRAPH_NODES = LANGUAGE_GRAPH_DIR / "language_graph_nodes.csv"
LANGUAGE_GRAPH_EDGES = LANGUAGE_GRAPH_DIR / "language_graph_edges.csv"
LANGUAGE_GRAPH_TABLES = (
    LANGUAGE_GRAPH_DIR / "signature_boundary_spine_language_graph_tables.npz"
)
LANGUAGE_GRAPH_CERTIFICATE = (
    LANGUAGE_GRAPH_DIR / "signature_boundary_spine_language_graph_certificate.json"
)

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_NODES = REWRITE_COMPLEX_DIR / "rewrite_complex_nodes.csv"
REWRITE_COMPLEX_EDGES = REWRITE_COMPLEX_DIR / "rewrite_complex_edges.csv"
REWRITE_COMPLEX_TABLES = REWRITE_COMPLEX_DIR / "rewrite_complex_tables.npz"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"

SYMBOLIC_ASSOCIATIVITY_REPORT = SYMBOLIC_ASSOCIATIVITY_DIR / "report.json"
SYMBOLIC_ASSOCIATIVITY_CSV = SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity.csv"
SYMBOLIC_ASSOCIATIVITY_TABLES = (
    SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity_tables.npz"
)
SYMBOLIC_ASSOCIATIVITY_CERTIFICATE = (
    SYMBOLIC_ASSOCIATIVITY_DIR / "symbolic_associativity_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_cycle_language.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_cycle_language.py"
)

TRACE_NODE_IDS = [48, 42, 27, 28, 34, 44]
GEODESIC_NODE_IDS = [48, 42, 44]
TRACE_EDGE_NODE_PAIRS = [(48, 42), (42, 27), (27, 28), (28, 34), (34, 44)]
SHORTCUT_EDGE_NODE_PAIR = (42, 44)
COMPLETION_CARRIER_IDS = [12, 3, 8, 13, 12]
COMPLETION_EDGE_IDS = [14, 11, 33, 43]
COMPLETION_SYMBOL_IDS = [2, 1, 4, 5]
APERTURE_WORD = [2, 4, 5]

WINDOW_ROLE_CODES = {
    "observed_language_boundary": 0,
    "inserted_strict_node42": 1,
    "clean_return_valley": 2,
    "x4_lift": 3,
    "x5_lift": 4,
    "cyclic_aperture_node44": 5,
    "completion_subsequence_node44": 6,
}

EDGE_ROLE_CODES = {
    "shared_geodesic_entry": 0,
    "tail_preserving_x1_detour": 1,
    "x4_lift": 2,
    "x5_lift": 3,
    "cyclic_x2_closure": 4,
    "ambient_geodesic_shortcut": 5,
}

WINDOW_COLUMNS = [
    "cycle_window_rank",
    "window_role_code",
    "left_symbol_id",
    "middle_symbol_id",
    "right_symbol_id",
    "triple_id",
    "canonical_triple_id",
    "sector_coverage_count",
    "full_sector_flag",
    "signature_union_count",
    "ambient_geodesic_rank",
    "carrier_trace_rank",
    "cyclic_cycle_window_flag",
    "aperture_completion_word_flag",
    "language_observed_flag",
    "strict_node42_flag",
    "aperture_node44_flag",
]

TRACE_EDGE_COLUMNS = [
    "trace_edge_rank",
    "edge_role_code",
    "source_node_id",
    "target_node_id",
    "rewrite_edge_id",
    "removed_symbol_id",
    "added_symbol_id",
    "source_signature_union_count",
    "target_signature_union_count",
    "signed_signature_delta",
    "absolute_signature_delta",
    "ambient_geodesic_edge_flag",
    "carrier_trace_edge_flag",
    "shortcut_edge_flag",
]

METRIC_NODE_COLUMNS = [
    "metric_node_rank",
    "rewrite_node_id",
    "carrier_trace_rank",
    "ambient_geodesic_rank",
    "signature_union_count",
    "distance_to_node48",
    "distance_to_node42",
    "distance_to_node44",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "carrier_trace_node_count": 0,
    "carrier_trace_edge_count": 1,
    "ambient_geodesic_edge_count": 2,
    "trace_length_48_to_44": 3,
    "ambient_geodesic_length_48_to_44": 4,
    "trace_detour_overhead": 5,
    "trace_signature_total_variation": 6,
    "ambient_signature_total_variation": 7,
    "signature_variation_overhead": 8,
    "trace_min_signature_after_node42": 9,
    "geodesic_min_signature_after_node42": 10,
    "cycle_metric_diameter": 11,
    "cycle_metric_radius": 12,
    "cycle_metric_gromov_delta_twice": 13,
    "node44_trace_rank": 14,
    "node42_trace_rank": 15,
}


def associativity_lookup(
    rows: list[dict[str, int]],
) -> dict[tuple[int, int, int], dict[str, int]]:
    return {
        (
            int(row["left_symbol_id"]),
            int(row["middle_symbol_id"]),
            int(row["right_symbol_id"]),
        ): row
        for row in rows
    }


def edge_key(source: int, target: int) -> tuple[int, int]:
    return tuple(sorted((int(source), int(target))))


def node_symbol_counts(row: dict[str, int]) -> list[int]:
    return [int(row[f"symbol_{symbol_id}_count"]) for symbol_id in range(6)]


def transition_symbols(
    source_node: dict[str, int],
    target_node: dict[str, int],
) -> tuple[int, int]:
    source_counts = node_symbol_counts(source_node)
    target_counts = node_symbol_counts(target_node)
    removed = [i for i in range(6) if source_counts[i] > target_counts[i]]
    added = [i for i in range(6) if target_counts[i] > source_counts[i]]
    if len(removed) != 1 or len(added) != 1:
        raise AssertionError("rewrite transition should replace one symbol")
    return removed[0], added[0]


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
        raise AssertionError("metric witness needs at least four nodes")
    return {
        "delta": float(best_delta_twice / 2.0),
        "delta_twice": int(best_delta_twice),
        "witness_ranks": [int(value) for value in best_witness],
        "four_point_sums": [int(value) for value in best_sums],
    }


def build_payloads() -> dict[str, Any]:
    completion_report = load_json(APERTURE_COMPLETION_REPORT)
    completion = load_json(APERTURE_COMPLETION_JSON)
    completion_certificate = load_json(APERTURE_COMPLETION_CERTIFICATE)
    aperture_report = load_json(APERTURE_FAN_REPORT)
    aperture_certificate = load_json(APERTURE_FAN_CERTIFICATE)
    language_report = load_json(LANGUAGE_GRAPH_REPORT)
    language_certificate = load_json(LANGUAGE_GRAPH_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    completion_tables = np.load(APERTURE_COMPLETION_TABLES, allow_pickle=False)
    aperture_tables = np.load(APERTURE_FAN_TABLES, allow_pickle=False)
    language_tables = np.load(LANGUAGE_GRAPH_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)

    completion_path_table = np.asarray(
        completion_tables["aperture_completion_path_table"], dtype=np.int64
    )
    aperture_path_table = np.asarray(aperture_tables["geodesic_path_table"], dtype=np.int64)
    language_node_table = np.asarray(language_tables["language_node_table"], dtype=np.int64)
    language_edge_table = np.asarray(language_tables["language_edge_table"], dtype=np.int64)
    rewrite_node_table = np.asarray(rewrite_tables["node_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"], dtype=np.int64
    )

    completion_paths = read_int_csv(APERTURE_COMPLETION_PATHS)
    aperture_paths = read_int_csv(APERTURE_FAN_PATHS)
    language_nodes = read_int_csv(LANGUAGE_GRAPH_NODES)
    language_edges = read_int_csv(LANGUAGE_GRAPH_EDGES)
    rewrite_nodes = read_int_csv(REWRITE_COMPLEX_NODES)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)

    assoc_by_word = associativity_lookup(associativity_rows)
    node_by_id = {int(row["node_id"]): row for row in rewrite_nodes}
    edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }
    language_node_ids = {
        int(row["rewrite_node_id"]) for row in language_nodes
    }
    geodesic_rank_by_node = {
        node_id: rank for rank, node_id in enumerate(GEODESIC_NODE_IDS)
    }
    carrier_rank_by_node = {node_id: rank for rank, node_id in enumerate(TRACE_NODE_IDS)}

    window_specs = [
        ("observed_language_boundary", (3, 5, 3), 0, 0, 0, 0),
        ("inserted_strict_node42", (5, 3, 2), 1, 1, 0, 0),
        ("clean_return_valley", (3, 2, 1), 2, 2, 0, 0),
        ("x4_lift", (2, 1, 4), 3, 3, 0, 0),
        ("x5_lift", (1, 4, 5), 4, 4, 0, 0),
        ("cyclic_aperture_node44", (4, 5, 2), 5, 5, 1, 0),
        ("completion_subsequence_node44", (2, 4, 5), 6, -1, 0, 1),
    ]
    window_rows: list[dict[str, int]] = []
    for rank, (role, word, _, trace_rank, cyclic_flag, completion_flag) in enumerate(
        window_specs
    ):
        assoc = assoc_by_word[word]
        node_id = int(assoc["canonical_triple_id"])
        signature = int(assoc["signature_union_count"])
        sector_coverage = int(assoc["sector_coverage_count"])
        window_rows.append(
            {
                "cycle_window_rank": rank,
                "window_role_code": WINDOW_ROLE_CODES[role],
                "left_symbol_id": word[0],
                "middle_symbol_id": word[1],
                "right_symbol_id": word[2],
                "triple_id": int(assoc["triple_id"]),
                "canonical_triple_id": node_id,
                "sector_coverage_count": sector_coverage,
                "full_sector_flag": int(sector_coverage == 6),
                "signature_union_count": signature,
                "ambient_geodesic_rank": geodesic_rank_by_node.get(node_id, -1),
                "carrier_trace_rank": trace_rank,
                "cyclic_cycle_window_flag": cyclic_flag,
                "aperture_completion_word_flag": completion_flag,
                "language_observed_flag": int(node_id in language_node_ids),
                "strict_node42_flag": int(node_id == 42),
                "aperture_node44_flag": int(node_id == 44),
            }
        )

    trace_edge_rows: list[dict[str, int]] = []
    trace_edge_specs = [
        ("shared_geodesic_entry", TRACE_EDGE_NODE_PAIRS[0], 1, 1, 0),
        ("tail_preserving_x1_detour", TRACE_EDGE_NODE_PAIRS[1], 0, 1, 0),
        ("x4_lift", TRACE_EDGE_NODE_PAIRS[2], 0, 1, 0),
        ("x5_lift", TRACE_EDGE_NODE_PAIRS[3], 0, 1, 0),
        ("cyclic_x2_closure", TRACE_EDGE_NODE_PAIRS[4], 0, 1, 0),
        ("ambient_geodesic_shortcut", SHORTCUT_EDGE_NODE_PAIR, 1, 0, 1),
    ]
    for rank, (role, pair, geodesic_flag, trace_flag, shortcut_flag) in enumerate(
        trace_edge_specs
    ):
        source_id, target_id = pair
        edge = edge_by_pair[edge_key(source_id, target_id)]
        removed_symbol, added_symbol = transition_symbols(
            node_by_id[source_id],
            node_by_id[target_id],
        )
        source_signature = int(node_by_id[source_id]["signature_union_count"])
        target_signature = int(node_by_id[target_id]["signature_union_count"])
        trace_edge_rows.append(
            {
                "trace_edge_rank": rank,
                "edge_role_code": EDGE_ROLE_CODES[role],
                "source_node_id": source_id,
                "target_node_id": target_id,
                "rewrite_edge_id": int(edge["edge_id"]),
                "removed_symbol_id": removed_symbol,
                "added_symbol_id": added_symbol,
                "source_signature_union_count": source_signature,
                "target_signature_union_count": target_signature,
                "signed_signature_delta": target_signature - source_signature,
                "absolute_signature_delta": abs(target_signature - source_signature),
                "ambient_geodesic_edge_flag": geodesic_flag,
                "carrier_trace_edge_flag": trace_flag,
                "shortcut_edge_flag": shortcut_flag,
            }
        )

    node_rank = {node_id: rank for rank, node_id in enumerate(TRACE_NODE_IDS)}
    adjacency = np.zeros((len(TRACE_NODE_IDS), len(TRACE_NODE_IDS)), dtype=np.int8)
    for source_id, target_id in [*TRACE_EDGE_NODE_PAIRS, SHORTCUT_EDGE_NODE_PAIR]:
        source_rank = node_rank[source_id]
        target_rank = node_rank[target_id]
        adjacency[source_rank, target_rank] = 1
        adjacency[target_rank, source_rank] = 1
    distances = shortest_paths(adjacency)
    delta = gromov_delta_witness(distances)

    metric_node_rows: list[dict[str, int]] = []
    for rank, node_id in enumerate(TRACE_NODE_IDS):
        metric_node_rows.append(
            {
                "metric_node_rank": rank,
                "rewrite_node_id": node_id,
                "carrier_trace_rank": carrier_rank_by_node.get(node_id, -1),
                "ambient_geodesic_rank": geodesic_rank_by_node.get(node_id, -1),
                "signature_union_count": int(
                    node_by_id[node_id]["signature_union_count"]
                ),
                "distance_to_node48": int(distances[rank, node_rank[48]]),
                "distance_to_node42": int(distances[rank, node_rank[42]]),
                "distance_to_node44": int(distances[rank, node_rank[44]]),
            }
        )

    trace_signature_variation = sum(
        int(row["absolute_signature_delta"])
        for row in trace_edge_rows
        if int(row["carrier_trace_edge_flag"]) == 1
    )
    ambient_signature_variation = (
        abs(int(node_by_id[42]["signature_union_count"]) - int(node_by_id[48]["signature_union_count"]))
        + abs(int(node_by_id[44]["signature_union_count"]) - int(node_by_id[42]["signature_union_count"]))
    )
    trace_signatures_after_node42 = [
        int(node_by_id[node_id]["signature_union_count"])
        for node_id in TRACE_NODE_IDS[1:]
    ]
    geodesic_signatures_after_node42 = [
        int(node_by_id[node_id]["signature_union_count"])
        for node_id in GEODESIC_NODE_IDS[1:]
    ]
    observable_values = {
        "carrier_trace_node_count": len(TRACE_NODE_IDS),
        "carrier_trace_edge_count": len(TRACE_EDGE_NODE_PAIRS),
        "ambient_geodesic_edge_count": len(GEODESIC_NODE_IDS) - 1,
        "trace_length_48_to_44": len(TRACE_EDGE_NODE_PAIRS),
        "ambient_geodesic_length_48_to_44": len(GEODESIC_NODE_IDS) - 1,
        "trace_detour_overhead": len(TRACE_EDGE_NODE_PAIRS) - (len(GEODESIC_NODE_IDS) - 1),
        "trace_signature_total_variation": trace_signature_variation,
        "ambient_signature_total_variation": ambient_signature_variation,
        "signature_variation_overhead": trace_signature_variation
        - ambient_signature_variation,
        "trace_min_signature_after_node42": min(trace_signatures_after_node42),
        "geodesic_min_signature_after_node42": min(geodesic_signatures_after_node42),
        "cycle_metric_diameter": int(np.max(distances)),
        "cycle_metric_radius": int(np.min(np.max(distances, axis=1))),
        "cycle_metric_gromov_delta_twice": int(delta["delta_twice"]),
        "node44_trace_rank": carrier_rank_by_node[44],
        "node42_trace_rank": carrier_rank_by_node[42],
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

    window_table = table_from_rows(WINDOW_COLUMNS, window_rows)
    trace_edge_table = table_from_rows(TRACE_EDGE_COLUMNS, trace_edge_rows)
    metric_node_table = table_from_rows(METRIC_NODE_COLUMNS, metric_node_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    strict_geodesic_path = [
        row
        for row in aperture_paths
        if [
            int(row["source_boundary_node_id"]),
            int(row["intermediate_node_id"]),
            int(row["aperture_node_id"]),
        ]
        == GEODESIC_NODE_IDS
    ]
    if len(strict_geodesic_path) != 1:
        raise AssertionError("strict aperture geodesic path 48-42-44 not unique")

    completion_cycle = completion_report["witness"]["completion_cycle"]
    checks = {
        "aperture_completion_report_certified": completion_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_X4_APERTURE_COMPLETION_CERTIFIED",
        "aperture_completion_certificate_certified": completion_certificate.get(
            "status"
        )
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_X4_APERTURE_COMPLETION_CERTIFIED",
        "aperture_fan_report_certified": aperture_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_GEODESIC_FAN_CERTIFIED",
        "aperture_fan_certificate_certified": aperture_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_GEODESIC_FAN_CERTIFIED",
        "language_graph_report_certified": language_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_LANGUAGE_GRAPH_CERTIFIED",
        "language_graph_certificate_certified": language_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_LANGUAGE_GRAPH_CERTIFIED",
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "symbolic_associativity_report_certified": associativity_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "symbolic_associativity_certificate_certified": associativity_certificate.get(
            "status"
        )
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "aperture_completion_schema_available": completion.get("schema")
        == "c985.d20_signature_boundary_spine_x2_x4_aperture_completion@1",
        "completion_path_table_shape_is_8_by_20": tuple(completion_path_table.shape)
        == (8, 20),
        "aperture_path_table_shape_is_6_by_17": tuple(aperture_path_table.shape)
        == (6, 17),
        "language_node_table_shape_is_8_by_14": tuple(language_node_table.shape)
        == (8, 14),
        "language_edge_table_shape_is_7_by_10": tuple(language_edge_table.shape)
        == (7, 10),
        "rewrite_node_table_shape_is_56_by_17": tuple(rewrite_node_table.shape)
        == (56, 17),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "completion_cycle_carriers_match_expected": completion_cycle["carrier_ids"]
        == COMPLETION_CARRIER_IDS,
        "completion_cycle_edges_match_expected": completion_cycle["cell_edge_ids"]
        == COMPLETION_EDGE_IDS,
        "completion_cycle_symbols_match_expected": completion_cycle["symbol_ids"]
        == COMPLETION_SYMBOL_IDS,
        "strict_ambient_geodesic_is_48_42_44": len(strict_geodesic_path) == 1,
        "strict_ambient_geodesic_restores_x2_then_x4": [
            int(strict_geodesic_path[0]["first_restored_symbol_id"]),
            int(strict_geodesic_path[0]["second_restored_symbol_id"]),
        ]
        == [2, 4],
        "carrier_trace_nodes_match_expected": TRACE_NODE_IDS
        == [48, 42, 27, 28, 34, 44],
        "carrier_trace_edges_exist_in_rewrite_complex": all(
            edge_key(*pair) in edge_by_pair for pair in TRACE_EDGE_NODE_PAIRS
        ),
        "geodesic_shortcut_edge_42_44_exists": edge_key(*SHORTCUT_EDGE_NODE_PAIR)
        in edge_by_pair,
        "trace_first_edge_matches_geodesic_entry": [
            int(trace_edge_rows[0]["source_node_id"]),
            int(trace_edge_rows[0]["target_node_id"]),
        ]
        == [48, 42],
        "trace_terminal_node_is_aperture_44": TRACE_NODE_IDS[-1] == 44,
        "trace_contains_geodesic_nodes_48_42_44": all(
            node_id in TRACE_NODE_IDS for node_id in GEODESIC_NODE_IDS
        ),
        "trace_length_is_5": observable_values["trace_length_48_to_44"] == 5,
        "ambient_geodesic_length_is_2": observable_values[
            "ambient_geodesic_length_48_to_44"
        ]
        == 2,
        "trace_detour_overhead_is_3": observable_values["trace_detour_overhead"] == 3,
        "trace_signature_variation_is_127": trace_signature_variation == 127,
        "ambient_signature_variation_is_53": ambient_signature_variation == 53,
        "signature_variation_overhead_is_74": observable_values[
            "signature_variation_overhead"
        ]
        == 74,
        "trace_min_after_node42_is_146": observable_values[
            "trace_min_signature_after_node42"
        ]
        == 146,
        "geodesic_min_after_node42_is_183": observable_values[
            "geodesic_min_signature_after_node42"
        ]
        == 183,
        "carrier_trace_window_nodes_match_expected": [
            int(row["canonical_triple_id"]) for row in window_rows[:6]
        ]
        == TRACE_NODE_IDS,
        "completion_subsequence_also_realizes_node44": int(
            window_rows[-1]["canonical_triple_id"]
        )
        == 44,
        "carrier_trace_window_signatures_match_expected": [
            int(row["signature_union_count"]) for row in window_rows[:6]
        ]
        == [132, 183, 146, 169, 177, 185],
        "metric_subgraph_diameter_is_3": observable_values["cycle_metric_diameter"]
        == 3,
        "metric_subgraph_radius_is_2": observable_values["cycle_metric_radius"] == 2,
        "metric_subgraph_delta_is_one_half": delta["delta_twice"] == 1,
        "window_table_shape_is_7_by_17": tuple(window_table.shape)
        == (7, len(WINDOW_COLUMNS)),
        "trace_edge_table_shape_is_6_by_14": tuple(trace_edge_table.shape)
        == (6, len(TRACE_EDGE_COLUMNS)),
        "metric_node_table_shape_is_6_by_8": tuple(metric_node_table.shape)
        == (6, len(METRIC_NODE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "ambient_geodesic_nodes": GEODESIC_NODE_IDS,
        "carrier_trace_nodes": TRACE_NODE_IDS,
        "carrier_trace_edges": [
            [int(source), int(target)] for source, target in TRACE_EDGE_NODE_PAIRS
        ],
        "ambient_shortcut_edge": list(SHORTCUT_EDGE_NODE_PAIR),
        "carrier_cycle": {
            "carrier_ids": COMPLETION_CARRIER_IDS,
            "cell_edge_ids": COMPLETION_EDGE_IDS,
            "symbol_ids": COMPLETION_SYMBOL_IDS,
        },
        "carrier_trace_window_nodes": [
            int(row["canonical_triple_id"]) for row in window_rows[:6]
        ],
        "carrier_trace_window_signatures": [
            int(row["signature_union_count"]) for row in window_rows[:6]
        ],
        "completion_subsequence_word": APERTURE_WORD,
        "completion_subsequence_node": int(window_rows[-1]["canonical_triple_id"]),
        "trace_length_48_to_44": observable_values["trace_length_48_to_44"],
        "ambient_geodesic_length_48_to_44": observable_values[
            "ambient_geodesic_length_48_to_44"
        ],
        "trace_detour_overhead": observable_values["trace_detour_overhead"],
        "trace_signature_total_variation": trace_signature_variation,
        "ambient_signature_total_variation": ambient_signature_variation,
        "signature_variation_overhead": observable_values[
            "signature_variation_overhead"
        ],
        "trace_min_signature_after_node42": observable_values[
            "trace_min_signature_after_node42"
        ],
        "geodesic_min_signature_after_node42": observable_values[
            "geodesic_min_signature_after_node42"
        ],
        "cycle_metric_diameter": observable_values["cycle_metric_diameter"],
        "cycle_metric_radius": observable_values["cycle_metric_radius"],
        "cycle_metric_gromov_delta": delta["delta"],
        "cycle_metric_gromov_delta_twice": delta["delta_twice"],
        "cycle_metric_delta_witness_node_ids": [
            TRACE_NODE_IDS[rank] for rank in delta["witness_ranks"]
        ],
        "window_table_sha256": sha_array(window_table),
        "trace_edge_table_sha256": sha_array(trace_edge_table),
        "metric_node_table_sha256": sha_array(metric_node_table),
        "cycle_adjacency_sha256": sha_array(adjacency),
        "cycle_distance_table_sha256": sha_array(distances),
        "observable_table_sha256": sha_array(observable_table),
    }

    cycle_language = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_language@1",
        "object": "d20",
        "cycle_language_rule": {
            "source": "certified origin-returning carrier aperture cycle",
            "carrier_cycle": "12 -> 3 -> 8 -> 13 -> 12",
            "symbol_cycle": "x2,x1,x4,x5",
            "ambient_geodesic": "48 -> 42 -> 44",
            "reading": (
                "the typed carrier cycle expands the ambient aperture geodesic "
                "by inserting a tail-preserving x1 valley and an x5 lift before "
                "closing cyclically at node 44"
            ),
        },
        "cycle_windows": window_rows,
        "trace_edges": trace_edge_rows,
        "metric_nodes": metric_node_rows,
        "summary": {
            "trace_length_48_to_44": observable_values["trace_length_48_to_44"],
            "ambient_geodesic_length_48_to_44": observable_values[
                "ambient_geodesic_length_48_to_44"
            ],
            "trace_detour_overhead": observable_values["trace_detour_overhead"],
            "cycle_metric_gromov_delta": delta["delta"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_language_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_LANGUAGE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the origin-returning carrier cycle expands the ambient geodesic 48-42-44 into the rewrite trace 48-42-27-28-34-44",
            "the trace has length 5 while the ambient geodesic has length 2, so the typed-tail detour overhead is 3",
            "after node 42 the carrier trace drops to signature 146 at node 27, while the geodesic shortcut stays at or above 183",
            "adding the shortcut edge 42-44 to the trace gives a six-node metric subgraph with diameter 3 and exact Gromov delta 0.5",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_language@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The local carrier aperture cycle realizes node 44 as a typed "
            "hyperbolic detour: it expands the ambient geodesic 48 -> 42 -> 44 "
            "into the carrier-trace path 48 -> 42 -> 27 -> 28 -> 34 -> 44, "
            "with exact detour overhead 3 and subgraph Gromov delta 0.5."
        ),
        "stage_protocol": {
            "draft": "read the origin-returning carrier cycle as a cyclic symbolic word",
            "witness": "materialize contiguous and cyclic rewrite windows plus the ambient geodesic shortcut",
            "coherence": "compare trace length, signature variation, metric distances, and Gromov delta against the geodesic 48-42-44",
            "closure": "certify the cycle language geometry without claiming global optimality among all carrier cycles",
            "emit": "emit aperture-cycle language JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "aperture_completion_report": input_entry(
                APERTURE_COMPLETION_REPORT,
                {
                    "status": completion_report.get("status"),
                    "certificate_sha256": completion_report.get("certificate_sha256"),
                },
            ),
            "aperture_completion": input_entry(APERTURE_COMPLETION_JSON),
            "aperture_completion_paths": input_entry(APERTURE_COMPLETION_PATHS),
            "aperture_completion_tables": input_entry(APERTURE_COMPLETION_TABLES),
            "aperture_completion_certificate": input_entry(
                APERTURE_COMPLETION_CERTIFICATE
            ),
            "aperture_fan_report": input_entry(
                APERTURE_FAN_REPORT,
                {
                    "status": aperture_report.get("status"),
                    "certificate_sha256": aperture_report.get("certificate_sha256"),
                },
            ),
            "aperture_fan_paths": input_entry(APERTURE_FAN_PATHS),
            "aperture_fan_tables": input_entry(APERTURE_FAN_TABLES),
            "aperture_fan_certificate": input_entry(APERTURE_FAN_CERTIFICATE),
            "language_graph_report": input_entry(
                LANGUAGE_GRAPH_REPORT,
                {
                    "status": language_report.get("status"),
                    "certificate_sha256": language_report.get("certificate_sha256"),
                },
            ),
            "language_graph_nodes": input_entry(LANGUAGE_GRAPH_NODES),
            "language_graph_edges": input_entry(LANGUAGE_GRAPH_EDGES),
            "language_graph_tables": input_entry(LANGUAGE_GRAPH_TABLES),
            "language_graph_certificate": input_entry(LANGUAGE_GRAPH_CERTIFICATE),
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex_nodes": input_entry(REWRITE_COMPLEX_NODES),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "symbolic_associativity_report": input_entry(
                SYMBOLIC_ASSOCIATIVITY_REPORT,
                {
                    "status": associativity_report.get("status"),
                    "certificate_sha256": associativity_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "symbolic_associativity_csv": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "symbolic_associativity_tables": input_entry(
                SYMBOLIC_ASSOCIATIVITY_TABLES
            ),
            "symbolic_associativity_certificate": input_entry(
                SYMBOLIC_ASSOCIATIVITY_CERTIFICATE
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_cycle_language": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_language.json"
            ),
            "aperture_cycle_trace_windows_csv": relpath(
                OUT_DIR / "aperture_cycle_trace_windows.csv"
            ),
            "aperture_cycle_trace_edges_csv": relpath(
                OUT_DIR / "aperture_cycle_trace_edges.csv"
            ),
            "aperture_cycle_metric_nodes_csv": relpath(
                OUT_DIR / "aperture_cycle_metric_nodes.csv"
            ),
            "aperture_cycle_observables_csv": relpath(
                OUT_DIR / "aperture_cycle_observables.csv"
            ),
            "signature_boundary_spine_aperture_cycle_language_tables": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_language_tables.npz"
            ),
            "signature_boundary_spine_aperture_cycle_language_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_cycle_language_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the rewrite-window trace induced by the origin-returning carrier cycle",
                "the comparison between carrier trace 48-42-27-28-34-44 and ambient geodesic 48-42-44",
                "trace length overhead, signature variation overhead, and the node-27 signature valley",
                "exact metric diameter, radius, and Gromov delta of the trace plus shortcut subgraph",
            ],
            "does_not_certify_because_not_required": [
                "global optimality among all possible carrier cycles",
                "a new typed-tail preservation theorem after the full aperture cycle",
                "new categorical F-symbols, braiding, pivotality, or Drinfeld-center data",
                "that the cognitive/playable interface is complete",
            ],
        },
        "next_highest_yield_item": (
            "Enumerate all origin-returning carrier cycles of comparable length "
            "that realize node 44, then rank them by trace overhead, signature "
            "valley depth, and Gromov delta against the ambient aperture geodesic."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_language_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified aperture completion, aperture fan, language graph, rewrite complex, and symbolic associativity artifacts",
            "materialize the carrier-cycle rewrite-window trace and cyclic aperture window",
            "compare the trace with the ambient geodesic 48-42-44",
            "compute exact metric distances and Gromov hyperbolicity for the trace-plus-shortcut subgraph",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_cycle_language": cycle_language,
        "aperture_cycle_trace_windows_csv": csv_text(WINDOW_COLUMNS, window_rows),
        "aperture_cycle_trace_edges_csv": csv_text(
            TRACE_EDGE_COLUMNS,
            trace_edge_rows,
        ),
        "aperture_cycle_metric_nodes_csv": csv_text(
            METRIC_NODE_COLUMNS,
            metric_node_rows,
        ),
        "aperture_cycle_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "window_table": window_table,
        "trace_edge_table": trace_edge_table,
        "metric_node_table": metric_node_table,
        "cycle_adjacency": adjacency,
        "cycle_distances": distances,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_cycle_language_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_cycle_language.json",
        payloads["signature_boundary_spine_aperture_cycle_language"],
    )
    (OUT_DIR / "aperture_cycle_trace_windows.csv").write_text(
        payloads["aperture_cycle_trace_windows_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cycle_trace_edges.csv").write_text(
        payloads["aperture_cycle_trace_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cycle_metric_nodes.csv").write_text(
        payloads["aperture_cycle_metric_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cycle_observables.csv").write_text(
        payloads["aperture_cycle_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_language_tables.npz",
        window_table=payloads["window_table"],
        trace_edge_table=payloads["trace_edge_table"],
        metric_node_table=payloads["metric_node_table"],
        cycle_adjacency=payloads["cycle_adjacency"],
        cycle_distances=payloads["cycle_distances"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_language_certificate.json",
        payloads["signature_boundary_spine_aperture_cycle_language_certificate"],
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
                "ambient_geodesic_nodes": witness["ambient_geodesic_nodes"],
                "carrier_trace_nodes": witness["carrier_trace_nodes"],
                "trace_detour_overhead": witness["trace_detour_overhead"],
                "cycle_metric_gromov_delta": witness["cycle_metric_gromov_delta"],
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
