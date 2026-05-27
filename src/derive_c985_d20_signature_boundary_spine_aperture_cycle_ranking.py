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
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_language import (
        OUT_DIR as APERTURE_CYCLE_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        SYMBOLIC_ALPHABET_CSV,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        OUT_DIR as CELL_COMPLEX_DIR,
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
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_language import (
        OUT_DIR as APERTURE_CYCLE_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        SYMBOLIC_ALPHABET_CSV,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        OUT_DIR as CELL_COMPLEX_DIR,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_cycle_ranking"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

APERTURE_CYCLE_REPORT = APERTURE_CYCLE_DIR / "report.json"
APERTURE_CYCLE_JSON = (
    APERTURE_CYCLE_DIR / "signature_boundary_spine_aperture_cycle_language.json"
)
APERTURE_CYCLE_TABLES = (
    APERTURE_CYCLE_DIR / "signature_boundary_spine_aperture_cycle_language_tables.npz"
)
APERTURE_CYCLE_CERTIFICATE = (
    APERTURE_CYCLE_DIR
    / "signature_boundary_spine_aperture_cycle_language_certificate.json"
)

CELL_COMPLEX_REPORT = CELL_COMPLEX_DIR / "report.json"
CELL_COMPLEX_EDGES = CELL_COMPLEX_DIR / "carrier_region_edges.csv"
CELL_COMPLEX_TABLES = CELL_COMPLEX_DIR / "signature_residual_cell_complex_tables.npz"
CELL_COMPLEX_CERTIFICATE = CELL_COMPLEX_DIR / "signature_residual_cell_complex_certificate.json"

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
    / "derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_cycle_ranking.py"
)

ORIGIN_CARRIER_ID = 12
INSERTED_SYMBOL_ID = 2
OBSERVED_BOUNDARY_NODE_ID = 48
STRICT_INTERMEDIATE_NODE_ID = 42
APERTURE_NODE_ID = 44
GEODESIC_NODE_IDS = [48, 42, 44]
PREFIX_SYMBOLS = [5, 3]
SELECTED_CYCLE_EDGE_IDS = [14, 11, 33, 43]
SELECTED_CYCLE_CARRIERS = [12, 3, 8, 13, 12]
SELECTED_CYCLE_SYMBOLS = [2, 1, 4, 5]
GEODESIC_MIN_AFTER_NODE42 = 183

CANDIDATE_COLUMNS = [
    "candidate_id",
    "rank_order",
    "carrier_0_id",
    "carrier_1_id",
    "carrier_2_id",
    "carrier_3_id",
    "carrier_4_id",
    "cell_edge_0_id",
    "cell_edge_1_id",
    "cell_edge_2_id",
    "cell_edge_3_id",
    "symbol_0_id",
    "symbol_1_id",
    "symbol_2_id",
    "symbol_3_id",
    "cycle_window_node_0_id",
    "cycle_window_node_1_id",
    "cycle_window_node_2_id",
    "cycle_window_node_3_id",
    "trace_node_count",
    "trace_edge_count",
    "trace_detour_overhead",
    "trace_signature_total_variation",
    "signature_valley_depth",
    "trace_min_signature_after_node42",
    "metric_gromov_delta_twice",
    "metric_diameter",
    "metric_radius",
    "first_node44_trace_rank",
    "geodesic_equivalent_flag",
    "x1_tail_preserving_flag",
    "x0_tail_flag",
    "selected_tail_cycle_flag",
    "best_rank_flag",
]

TRACE_WINDOW_COLUMNS = [
    "candidate_id",
    "trace_window_rank",
    "left_symbol_id",
    "middle_symbol_id",
    "right_symbol_id",
    "canonical_triple_id",
    "sector_coverage_count",
    "signature_union_count",
    "collapsed_trace_rank",
    "first_node44_stop_flag",
    "duplicate_of_previous_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "rooted_x2_cycle_count": 0,
    "distinct_symbol_cycle_count": 1,
    "node44_realizing_cycle_count": 2,
    "geodesic_equivalent_cycle_count": 3,
    "tail_preserving_cycle_count": 4,
    "selected_tail_cycle_rank_order": 5,
    "selected_tail_cycle_trace_overhead": 6,
    "best_trace_overhead": 7,
    "best_signature_valley_depth": 8,
    "best_gromov_delta_twice": 9,
    "max_signature_valley_depth": 10,
    "candidate_table_row_count": 11,
    "trace_window_table_row_count": 12,
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


def shared_symbol_ids(edge: dict[str, int], atom_to_symbol: dict[int, int]) -> list[int]:
    shared_atom_bitset = int(edge["source_carrier_atom_mask"]) & int(
        edge["target_carrier_atom_mask"]
    )
    return sorted(
        {
            atom_to_symbol[atom_id]
            for atom_id in range(64)
            if shared_atom_bitset & (1 << atom_id)
        }
    )


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


def gromov_delta_twice(distances: np.ndarray) -> int:
    node_count = int(distances.shape[0])
    if node_count < 4:
        return 0
    best = 0
    for a, b, c, d in itertools.combinations(range(node_count), 4):
        sums = sorted(
            [
                int(distances[a, b] + distances[c, d]),
                int(distances[a, c] + distances[b, d]),
                int(distances[a, d] + distances[b, c]),
            ]
        )
        best = max(best, sums[2] - sums[1])
    return int(best)


def node_symbol_counts(row: dict[str, int]) -> list[int]:
    return [int(row[f"symbol_{symbol_id}_count"]) for symbol_id in range(6)]


def transition_edge_exists(
    source: int,
    target: int,
    rewrite_edge_by_pair: dict[tuple[int, int], dict[str, int]],
) -> bool:
    return source == target or edge_key(source, target) in rewrite_edge_by_pair


def build_trace(
    symbols: tuple[int, int, int, int],
    assoc_by_word: dict[tuple[int, int, int], dict[str, int]],
    rewrite_edge_by_pair: dict[tuple[int, int], dict[str, int]],
) -> tuple[list[dict[str, int]], list[int], list[int], dict[str, int]]:
    sequence = [*PREFIX_SYMBOLS, *symbols, symbols[0], symbols[1]]
    raw_windows: list[dict[str, int]] = []
    collapsed_nodes = [OBSERVED_BOUNDARY_NODE_ID]
    collapsed_signatures = [132]
    first_node44_trace_rank = -1
    for window_rank in range(len(sequence) - 2):
        word = tuple(sequence[window_rank : window_rank + 3])
        assoc = assoc_by_word[word]
        node_id = int(assoc["canonical_triple_id"])
        signature = int(assoc["signature_union_count"])
        duplicate = int(collapsed_nodes[-1] == node_id)
        if not duplicate:
            collapsed_nodes.append(node_id)
            collapsed_signatures.append(signature)
        raw_windows.append(
            {
                "trace_window_rank": window_rank,
                "left_symbol_id": word[0],
                "middle_symbol_id": word[1],
                "right_symbol_id": word[2],
                "canonical_triple_id": node_id,
                "sector_coverage_count": int(assoc["sector_coverage_count"]),
                "signature_union_count": signature,
                "collapsed_trace_rank": len(collapsed_nodes) - 1,
                "first_node44_stop_flag": 0,
                "duplicate_of_previous_flag": duplicate,
            }
        )
        if node_id == APERTURE_NODE_ID and len(collapsed_nodes) > 2:
            first_node44_trace_rank = len(collapsed_nodes) - 1
            raw_windows[-1]["first_node44_stop_flag"] = 1
            break
    if collapsed_nodes[-1] != APERTURE_NODE_ID:
        raise AssertionError("candidate did not reach aperture node 44")
    for source, target in zip(collapsed_nodes, collapsed_nodes[1:]):
        if not transition_edge_exists(source, target, rewrite_edge_by_pair):
            raise AssertionError(f"missing rewrite edge {source}->{target}")

    trace_edges = list(zip(collapsed_nodes, collapsed_nodes[1:]))
    all_nodes: list[int] = []
    for node_id in [*GEODESIC_NODE_IDS, *collapsed_nodes]:
        if node_id not in all_nodes:
            all_nodes.append(node_id)
    rank_by_node = {node_id: rank for rank, node_id in enumerate(all_nodes)}
    adjacency = np.zeros((len(all_nodes), len(all_nodes)), dtype=np.int8)
    for source, target in [*trace_edges, (STRICT_INTERMEDIATE_NODE_ID, APERTURE_NODE_ID)]:
        if source == target:
            continue
        adjacency[rank_by_node[source], rank_by_node[target]] = 1
        adjacency[rank_by_node[target], rank_by_node[source]] = 1
    distances = shortest_paths(adjacency)
    trace_variation = sum(
        abs(collapsed_signatures[index + 1] - collapsed_signatures[index])
        for index in range(len(collapsed_signatures) - 1)
    )
    min_after_node42 = min(collapsed_signatures[2:])
    metrics = {
        "trace_edge_count": len(trace_edges),
        "trace_detour_overhead": len(trace_edges) - 2,
        "trace_signature_total_variation": trace_variation,
        "trace_min_signature_after_node42": min_after_node42,
        "signature_valley_depth": max(0, GEODESIC_MIN_AFTER_NODE42 - min_after_node42),
        "metric_gromov_delta_twice": gromov_delta_twice(distances),
        "metric_diameter": int(np.max(distances)),
        "metric_radius": int(np.min(np.max(distances, axis=1))),
        "first_node44_trace_rank": first_node44_trace_rank,
    }
    return raw_windows, collapsed_nodes, collapsed_signatures, metrics


def build_payloads() -> dict[str, Any]:
    aperture_cycle_report = load_json(APERTURE_CYCLE_REPORT)
    aperture_cycle = load_json(APERTURE_CYCLE_JSON)
    aperture_cycle_certificate = load_json(APERTURE_CYCLE_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    aperture_cycle_tables = np.load(APERTURE_CYCLE_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    aperture_cycle_window_table = np.asarray(
        aperture_cycle_tables["window_table"], dtype=np.int64
    )
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_node_table = np.asarray(rewrite_tables["node_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"], dtype=np.int64
    )

    cell_edges = read_int_csv(CELL_COMPLEX_EDGES)
    rewrite_nodes = read_int_csv(REWRITE_COMPLEX_NODES)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)

    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    assoc_by_word = associativity_lookup(associativity_rows)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }
    carrier_edge_by_pair = {
        edge_key(
            int(row["source_carrier_mask_class_id"]),
            int(row["target_carrier_mask_class_id"]),
        ): row
        for row in cell_edges
    }
    carrier_adjacency: dict[int, list[int]] = {}
    for row in cell_edges:
        source = int(row["source_carrier_mask_class_id"])
        target = int(row["target_carrier_mask_class_id"])
        carrier_adjacency.setdefault(source, []).append(target)
        carrier_adjacency.setdefault(target, []).append(source)

    candidate_rows: list[dict[str, int]] = []
    trace_window_rows: list[dict[str, int]] = []
    candidate_payloads: list[dict[str, Any]] = []

    for carrier_1 in sorted(carrier_adjacency[ORIGIN_CARRIER_ID]):
        for carrier_2 in sorted(carrier_adjacency.get(carrier_1, [])):
            if carrier_2 in (ORIGIN_CARRIER_ID, carrier_1):
                continue
            for carrier_3 in sorted(carrier_adjacency.get(carrier_2, [])):
                if carrier_3 in (ORIGIN_CARRIER_ID, carrier_1, carrier_2):
                    continue
                if ORIGIN_CARRIER_ID not in carrier_adjacency.get(carrier_3, []):
                    continue
                carriers = [
                    ORIGIN_CARRIER_ID,
                    carrier_1,
                    carrier_2,
                    carrier_3,
                    ORIGIN_CARRIER_ID,
                ]
                edge_rows = [
                    carrier_edge_by_pair[edge_key(source, target)]
                    for source, target in zip(carriers, carriers[1:])
                ]
                edge_ids = [int(row["cell_edge_id"]) for row in edge_rows]
                symbol_options = [
                    shared_symbol_ids(row, atom_to_symbol) for row in edge_rows
                ]
                for symbols in itertools.product(*symbol_options):
                    if symbols[0] != INSERTED_SYMBOL_ID:
                        continue
                    cycle_windows = [
                        assoc_by_word[tuple(symbols[index:] + symbols[:index])[:3]]
                        for index in range(4)
                    ]
                    if not any(
                        int(row["canonical_triple_id"]) == APERTURE_NODE_ID
                        for row in cycle_windows
                    ):
                        continue
                    raw_windows, trace_nodes, trace_signatures, metrics = build_trace(
                        symbols,
                        assoc_by_word,
                        rewrite_edge_by_pair,
                    )
                    candidate_payloads.append(
                        {
                            "carriers": carriers,
                            "edge_ids": edge_ids,
                            "symbols": list(symbols),
                            "cycle_window_nodes": [
                                int(row["canonical_triple_id"])
                                for row in cycle_windows
                            ],
                            "trace_nodes": trace_nodes,
                            "trace_signatures": trace_signatures,
                            "metrics": metrics,
                            "raw_windows": raw_windows,
                        }
                    )

    candidate_payloads = sorted(
        candidate_payloads,
        key=lambda row: (
            int(row["metrics"]["trace_detour_overhead"]),
            int(row["metrics"]["signature_valley_depth"]),
            int(row["metrics"]["metric_gromov_delta_twice"]),
            int(row["metrics"]["trace_signature_total_variation"]),
            row["edge_ids"],
        ),
    )

    best_score = None
    for rank_order, payload in enumerate(candidate_payloads, start=1):
        metrics = payload["metrics"]
        score = (
            int(metrics["trace_detour_overhead"]),
            int(metrics["signature_valley_depth"]),
            int(metrics["metric_gromov_delta_twice"]),
            int(metrics["trace_signature_total_variation"]),
        )
        if best_score is None:
            best_score = score
        candidate_id = len(candidate_rows)
        carriers = payload["carriers"]
        edge_ids = payload["edge_ids"]
        symbols = payload["symbols"]
        cycle_nodes = payload["cycle_window_nodes"]
        selected = int(
            carriers == SELECTED_CYCLE_CARRIERS
            and edge_ids == SELECTED_CYCLE_EDGE_IDS
            and symbols == SELECTED_CYCLE_SYMBOLS
        )
        row = {
            "candidate_id": candidate_id,
            "rank_order": rank_order,
            "carrier_0_id": carriers[0],
            "carrier_1_id": carriers[1],
            "carrier_2_id": carriers[2],
            "carrier_3_id": carriers[3],
            "carrier_4_id": carriers[4],
            "cell_edge_0_id": edge_ids[0],
            "cell_edge_1_id": edge_ids[1],
            "cell_edge_2_id": edge_ids[2],
            "cell_edge_3_id": edge_ids[3],
            "symbol_0_id": symbols[0],
            "symbol_1_id": symbols[1],
            "symbol_2_id": symbols[2],
            "symbol_3_id": symbols[3],
            "cycle_window_node_0_id": cycle_nodes[0],
            "cycle_window_node_1_id": cycle_nodes[1],
            "cycle_window_node_2_id": cycle_nodes[2],
            "cycle_window_node_3_id": cycle_nodes[3],
            "trace_node_count": len(payload["trace_nodes"]),
            "trace_edge_count": int(metrics["trace_edge_count"]),
            "trace_detour_overhead": int(metrics["trace_detour_overhead"]),
            "trace_signature_total_variation": int(
                metrics["trace_signature_total_variation"]
            ),
            "signature_valley_depth": int(metrics["signature_valley_depth"]),
            "trace_min_signature_after_node42": int(
                metrics["trace_min_signature_after_node42"]
            ),
            "metric_gromov_delta_twice": int(metrics["metric_gromov_delta_twice"]),
            "metric_diameter": int(metrics["metric_diameter"]),
            "metric_radius": int(metrics["metric_radius"]),
            "first_node44_trace_rank": int(metrics["first_node44_trace_rank"]),
            "geodesic_equivalent_flag": int(metrics["trace_detour_overhead"] == 0),
            "x1_tail_preserving_flag": int(symbols[1] == 1),
            "x0_tail_flag": int(symbols[1] == 0),
            "selected_tail_cycle_flag": selected,
            "best_rank_flag": int(score == best_score),
        }
        candidate_rows.append(row)
        for raw_window in payload["raw_windows"]:
            trace_window_rows.append({"candidate_id": candidate_id, **raw_window})

    selected_candidate = [
        row for row in candidate_rows if int(row["selected_tail_cycle_flag"]) == 1
    ]
    if len(selected_candidate) != 1:
        raise AssertionError("selected tail-preserving cycle should be unique")
    selected_candidate_row = selected_candidate[0]
    distinct_symbol_cycles = sorted(
        {tuple(row["symbols"]) for row in candidate_payloads}
    )
    observable_values = {
        "rooted_x2_cycle_count": len(candidate_rows),
        "distinct_symbol_cycle_count": len(distinct_symbol_cycles),
        "node44_realizing_cycle_count": len(candidate_rows),
        "geodesic_equivalent_cycle_count": sum(
            int(row["geodesic_equivalent_flag"]) for row in candidate_rows
        ),
        "tail_preserving_cycle_count": sum(
            int(row["x1_tail_preserving_flag"]) for row in candidate_rows
        ),
        "selected_tail_cycle_rank_order": int(selected_candidate_row["rank_order"]),
        "selected_tail_cycle_trace_overhead": int(
            selected_candidate_row["trace_detour_overhead"]
        ),
        "best_trace_overhead": min(
            int(row["trace_detour_overhead"]) for row in candidate_rows
        ),
        "best_signature_valley_depth": min(
            int(row["signature_valley_depth"]) for row in candidate_rows
        ),
        "best_gromov_delta_twice": min(
            int(row["metric_gromov_delta_twice"]) for row in candidate_rows
        ),
        "max_signature_valley_depth": max(
            int(row["signature_valley_depth"]) for row in candidate_rows
        ),
        "candidate_table_row_count": len(candidate_rows),
        "trace_window_table_row_count": len(trace_window_rows),
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

    candidate_table = table_from_rows(CANDIDATE_COLUMNS, candidate_rows)
    trace_window_table = table_from_rows(TRACE_WINDOW_COLUMNS, trace_window_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "aperture_cycle_report_certified": aperture_cycle_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_LANGUAGE_CERTIFIED",
        "aperture_cycle_certificate_certified": aperture_cycle_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_LANGUAGE_CERTIFIED",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
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
        "aperture_cycle_schema_available": aperture_cycle.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_cycle_language@1",
        "aperture_cycle_window_table_shape_is_7_by_17": tuple(
            aperture_cycle_window_table.shape
        )
        == (7, 17),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_node_table_shape_is_56_by_17": tuple(rewrite_node_table.shape)
        == (56, 17),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "rooted_x2_cycle_count_is_10": len(candidate_rows) == 10,
        "distinct_symbol_cycle_count_is_3": len(distinct_symbol_cycles) == 3,
        "all_candidates_realize_node44": all(
            APERTURE_NODE_ID
            in [
                int(row["cycle_window_node_0_id"]),
                int(row["cycle_window_node_1_id"]),
                int(row["cycle_window_node_2_id"]),
                int(row["cycle_window_node_3_id"]),
            ]
            for row in candidate_rows
        ),
        "geodesic_equivalent_cycle_count_is_6": observable_values[
            "geodesic_equivalent_cycle_count"
        ]
        == 6,
        "tail_preserving_cycle_count_is_2": observable_values[
            "tail_preserving_cycle_count"
        ]
        == 2,
        "selected_tail_cycle_rank_order_is_7": observable_values[
            "selected_tail_cycle_rank_order"
        ]
        == 7,
        "selected_tail_cycle_overhead_is_3": observable_values[
            "selected_tail_cycle_trace_overhead"
        ]
        == 3,
        "best_cycles_have_zero_overhead": observable_values["best_trace_overhead"] == 0,
        "best_cycles_have_zero_valley_depth": observable_values[
            "best_signature_valley_depth"
        ]
        == 0,
        "best_cycles_have_zero_delta": observable_values["best_gromov_delta_twice"]
        == 0,
        "selected_cycle_matches_prior_edges": [
            int(selected_candidate_row[f"cell_edge_{index}_id"]) for index in range(4)
        ]
        == SELECTED_CYCLE_EDGE_IDS,
        "selected_cycle_matches_prior_carriers": [
            int(selected_candidate_row[f"carrier_{index}_id"]) for index in range(5)
        ]
        == SELECTED_CYCLE_CARRIERS,
        "selected_cycle_matches_prior_symbols": [
            int(selected_candidate_row[f"symbol_{index}_id"]) for index in range(4)
        ]
        == SELECTED_CYCLE_SYMBOLS,
        "selected_cycle_valley_depth_is_37": int(
            selected_candidate_row["signature_valley_depth"]
        )
        == 37,
        "selected_cycle_delta_is_one_half": int(
            selected_candidate_row["metric_gromov_delta_twice"]
        )
        == 1,
        "worst_valley_depth_is_41": observable_values["max_signature_valley_depth"]
        == 41,
        "candidate_table_shape_is_10_by_34": tuple(candidate_table.shape)
        == (10, len(CANDIDATE_COLUMNS)),
        "trace_window_table_has_38_rows": tuple(trace_window_table.shape)
        == (38, len(TRACE_WINDOW_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    best_candidates = [
        row for row in candidate_rows if int(row["best_rank_flag"]) == 1
    ]
    witness = {
        "rooted_x2_cycle_count": len(candidate_rows),
        "distinct_symbol_cycles": [list(row) for row in distinct_symbol_cycles],
        "best_candidate_count": len(best_candidates),
        "best_candidate_edge_cycles": [
            [int(row[f"cell_edge_{index}_id"]) for index in range(4)]
            for row in best_candidates
        ],
        "best_candidate_symbol_cycle": [
            int(best_candidates[0][f"symbol_{index}_id"]) for index in range(4)
        ],
        "selected_tail_cycle_rank_order": int(selected_candidate_row["rank_order"]),
        "selected_tail_cycle_metrics": {
            "trace_detour_overhead": int(
                selected_candidate_row["trace_detour_overhead"]
            ),
            "signature_valley_depth": int(
                selected_candidate_row["signature_valley_depth"]
            ),
            "metric_gromov_delta": float(
                int(selected_candidate_row["metric_gromov_delta_twice"]) / 2.0
            ),
            "trace_signature_total_variation": int(
                selected_candidate_row["trace_signature_total_variation"]
            ),
        },
        "ranking_key": [
            "trace_detour_overhead",
            "signature_valley_depth",
            "metric_gromov_delta_twice",
            "trace_signature_total_variation",
            "cell_edge_ids",
        ],
        "candidate_table_sha256": sha_array(candidate_table),
        "trace_window_table_sha256": sha_array(trace_window_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    ranking = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_ranking@1",
        "object": "d20",
        "ranking_rule": {
            "carrier_scope": "simple four-edge carrier cycles rooted at carrier 12",
            "symbol_scope": "edge-label choices whose first symbol is x2 and whose cyclic windows realize node 44",
            "trace_anchor": "fixed boundary prefix x5,x3, so the first x2 window is node 42",
            "ranking": "lexicographic by trace overhead, signature valley depth, Gromov delta twice, signature variation, then edge ids",
        },
        "ranked_candidates": candidate_rows,
        "summary": {
            "rooted_x2_cycle_count": len(candidate_rows),
            "geodesic_equivalent_cycle_count": observable_values[
                "geodesic_equivalent_cycle_count"
            ],
            "tail_preserving_cycle_count": observable_values[
                "tail_preserving_cycle_count"
            ],
            "selected_tail_cycle_rank_order": observable_values[
                "selected_tail_cycle_rank_order"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_ranking_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "there are 10 x2-rooted simple four-edge carrier cycles from carrier 12 that realize aperture node 44",
            "six cycles collapse to the ambient geodesic 48-42-44 with zero overhead, zero valley depth, and zero delta",
            "the certified tail-preserving cycle 12-3-8-13-12 ranks seventh globally because its x1 tail preservation creates a signature valley at node 27",
            "the worst valley depth among comparable cycles is 41, from the x0-tail cycle family",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_ranking@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Among all x2-rooted simple four-edge origin-returning carrier "
            "cycles that realize aperture node 44, six collapse to the ambient "
            "geodesic with zero overhead; the previously certified "
            "tail-preserving cycle is the best x1-tail family member but ranks "
            "seventh globally because it pays a node-27 signature valley."
        ),
        "stage_protocol": {
            "draft": "enumerate simple carrier cycles rooted at carrier 12 with first label x2",
            "witness": "materialize each cycle, edge-label word, anchored rewrite trace, and node-44 hit",
            "coherence": "rank by trace overhead, signature valley depth, Gromov delta, and signature variation",
            "closure": "certify the finite comparable-cycle ranking without claiming longer-cycle optimality",
            "emit": "emit aperture-cycle ranking JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "aperture_cycle_report": input_entry(
                APERTURE_CYCLE_REPORT,
                {
                    "status": aperture_cycle_report.get("status"),
                    "certificate_sha256": aperture_cycle_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "aperture_cycle_language": input_entry(APERTURE_CYCLE_JSON),
            "aperture_cycle_tables": input_entry(APERTURE_CYCLE_TABLES),
            "aperture_cycle_certificate": input_entry(APERTURE_CYCLE_CERTIFICATE),
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_report.get("status"),
                    "certificate_sha256": cell_report.get("certificate_sha256"),
                },
            ),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
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
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_cycle_ranking": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking.json"
            ),
            "aperture_cycle_ranked_candidates_csv": relpath(
                OUT_DIR / "aperture_cycle_ranked_candidates.csv"
            ),
            "aperture_cycle_candidate_trace_windows_csv": relpath(
                OUT_DIR / "aperture_cycle_candidate_trace_windows.csv"
            ),
            "aperture_cycle_ranking_observables_csv": relpath(
                OUT_DIR / "aperture_cycle_ranking_observables.csv"
            ),
            "signature_boundary_spine_aperture_cycle_ranking_tables": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking_tables.npz"
            ),
            "signature_boundary_spine_aperture_cycle_ranking_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_cycle_ranking_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all x2-rooted simple four-edge carrier cycles from carrier 12 that realize node 44",
                "the anchored rewrite trace and node-44 hit for each candidate",
                "cycle ranking by trace overhead, signature valley depth, Gromov delta, and signature variation",
                "the global rank of the previously certified tail-preserving cycle within this comparable class",
            ],
            "does_not_certify_because_not_required": [
                "cycles longer than four carrier edges",
                "cycles not rooted at carrier 12 or not anchored by the x2 insertion",
                "global optimality across arbitrary mixed-symbol disambiguations outside this finite class",
                "new categorical F-symbols, braiding, pivotality, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Separate the six zero-overhead mixed cycles by typed-boundary cost: "
            "audit which require mixed x2/x5 contacts or abandon the certified "
            "x1 tail, then certify the Pareto frontier of geodesic optimality "
            "versus typed-tail preservation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_ranking_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified aperture-cycle, residual cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "enumerate simple x2-rooted four-edge cycles from carrier 12",
            "filter to cycles whose cyclic windows realize node 44",
            "rank each anchored rewrite trace against the ambient aperture geodesic",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_cycle_ranking": ranking,
        "aperture_cycle_ranked_candidates_csv": csv_text(
            CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_cycle_candidate_trace_windows_csv": csv_text(
            TRACE_WINDOW_COLUMNS,
            trace_window_rows,
        ),
        "aperture_cycle_ranking_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "trace_window_table": trace_window_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_cycle_ranking_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking.json",
        payloads["signature_boundary_spine_aperture_cycle_ranking"],
    )
    (OUT_DIR / "aperture_cycle_ranked_candidates.csv").write_text(
        payloads["aperture_cycle_ranked_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cycle_candidate_trace_windows.csv").write_text(
        payloads["aperture_cycle_candidate_trace_windows_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cycle_ranking_observables.csv").write_text(
        payloads["aperture_cycle_ranking_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking_tables.npz",
        candidate_table=payloads["candidate_table"],
        trace_window_table=payloads["trace_window_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking_certificate.json",
        payloads["signature_boundary_spine_aperture_cycle_ranking_certificate"],
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
                "rooted_x2_cycle_count": witness["rooted_x2_cycle_count"],
                "best_candidate_count": witness["best_candidate_count"],
                "best_candidate_symbol_cycle": witness["best_candidate_symbol_cycle"],
                "selected_tail_cycle_rank_order": witness[
                    "selected_tail_cycle_rank_order"
                ],
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
