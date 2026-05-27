from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        OUT_DIR as BOUNDED_BACKTRACK_DIR,
        STATUS as BOUNDED_BACKTRACK_STATUS,
        WALK_CANDIDATE_COLUMNS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking import (
        OUT_DIR as CLOSED_REPAIR_DIR,
        STATUS as CLOSED_REPAIR_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
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
    from derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        OUT_DIR as BOUNDED_BACKTRACK_DIR,
        STATUS as BOUNDED_BACKTRACK_STATUS,
        WALK_CANDIDATE_COLUMNS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking import (
        OUT_DIR as CLOSED_REPAIR_DIR,
        STATUS as CLOSED_REPAIR_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
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


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD3_TRACE_CLASS_QUOTIENT_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

BOUNDED_BACKTRACK_REPORT = BOUNDED_BACKTRACK_DIR / "report.json"
BOUNDED_BACKTRACK_JSON = (
    BOUNDED_BACKTRACK_DIR / "signature_boundary_spine_aperture_bounded_backtrack_search.json"
)
BOUNDED_BACKTRACK_CANDIDATES = (
    BOUNDED_BACKTRACK_DIR / "aperture_bounded_backtrack_candidates.csv"
)
BOUNDED_BACKTRACK_TABLES = (
    BOUNDED_BACKTRACK_DIR
    / "signature_boundary_spine_aperture_bounded_backtrack_search_tables.npz"
)
BOUNDED_BACKTRACK_CERTIFICATE = (
    BOUNDED_BACKTRACK_DIR
    / "signature_boundary_spine_aperture_bounded_backtrack_search_certificate.json"
)

CLOSED_REPAIR_REPORT = CLOSED_REPAIR_DIR / "report.json"
CLOSED_REPAIR_JSON = (
    CLOSED_REPAIR_DIR
    / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking.json"
)
CLOSED_REPAIR_TABLES = (
    CLOSED_REPAIR_DIR
    / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_tables.npz"
)
CLOSED_REPAIR_CERTIFICATE = (
    CLOSED_REPAIR_DIR
    / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient.py"
)

MAX_SYMBOL_LENGTH = 7
MAX_TRACE_NODES = 8
TARGET_OVERHEAD = 3
NODE42_SIGNATURE_UNION = 183
BASELINE_TRACE = (48, 42, 27, 28, 34, 44)
TARGET1_TRACE = (48, 42, 27, 29, 45, 44)
BASELINE_CLOSED_REPAIR_WORD = (2, 1, 4, 5, 2, 5)
TARGET1_CLOSED_REPAIR_WORD = (2, 1, 5, 2, 5, 4, 3)

TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_TRACE_NODES)]
TRACE_SIGNATURE_COLUMNS = [
    f"trace_signature_{index}_count" for index in range(MAX_TRACE_NODES)
]
REPRESENTATIVE_SYMBOL_COLUMNS = [
    f"representative_symbol_{index}_id" for index in range(MAX_SYMBOL_LENGTH)
]

TRACE_CLASS_COLUMNS = [
    "trace_class_id",
    "class_rank_order",
    "candidate_count",
    "rank_min",
    "rank_max",
    "rank_gap_count",
    "rank_interval_contiguous_flag",
    "walk_length_min",
    "walk_length_max",
    "distinct_symbol_word_count",
    "distinct_carrier_path_count",
    "distinct_cell_edge_path_count",
    "distinct_atom_word_count",
    "distinct_trace_signature_count",
    "score_better_candidate_count",
    "score_class_candidate_count",
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    *TRACE_SIGNATURE_COLUMNS,
    "trace_edge_count",
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "trace_min_signature_after_node42",
    "baseline_alias_flag",
    "target1_branch_flag",
    "representative_candidate_id",
    "representative_rank_order",
    "representative_walk_length",
    *REPRESENTATIVE_SYMBOL_COLUMNS,
]

TRACE_NODE_READOUT_COLUMNS = [
    "trace_class_id",
    "trace_rank",
    "node_id",
    "signature_union_count",
    "sector_coverage_count",
    "graph_degree",
    "signature_drop_from_node42",
    "local_valley_flag",
    "baseline_divergent_flag",
    "target1_divergent_flag",
]

TRANSITION_EDIT_COLUMNS = [
    "transition_id",
    "source_trace_class_id",
    "target_trace_class_id",
    "source_baseline_alias_flag",
    "target_target1_branch_flag",
    "common_prefix_node_count",
    "common_suffix_node_count",
    "source_divergent_node_count",
    "target_divergent_node_count",
    "trace_node_edit_distance",
    "trace_edge_edit_distance",
    "trace_ambient_aligned_substitution_cost",
    "symbol_word_min_edit_distance",
    "closed_repair_word_edit_distance",
    "atom_word_min_edit_distance",
    "carrier_path_min_edit_distance",
    "cell_edge_path_min_edit_distance",
    "source_divergent_node_0_id",
    "source_divergent_node_1_id",
    "target_divergent_node_0_id",
    "target_divergent_node_1_id",
    "source_best_symbol_edit_candidate_id",
    "target_best_symbol_edit_candidate_id",
]

PAIRWISE_TRACE_EDIT_COLUMNS = [
    "source_trace_class_id",
    "target_trace_class_id",
    "common_prefix_node_count",
    "common_suffix_node_count",
    "source_divergent_node_count",
    "target_divergent_node_count",
    "trace_node_edit_distance",
    "trace_edge_edit_distance",
    "trace_ambient_aligned_substitution_cost",
    "source_rank_min",
    "target_rank_min",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "overhead3_candidate_count": 0,
    "overhead3_trace_class_count": 1,
    "baseline_alias_candidate_count": 2,
    "baseline_alias_distinct_word_count": 3,
    "target1_branch_candidate_count": 4,
    "target1_branch_distinct_word_count": 5,
    "classes_before_target1_count": 6,
    "candidates_before_target1_count": 7,
    "baseline_to_target_trace_node_edit_distance": 8,
    "baseline_to_target_trace_edge_edit_distance": 9,
    "baseline_to_target_symbol_word_min_edit_distance": 10,
    "baseline_to_target_closed_repair_word_edit_distance": 11,
    "baseline_to_target_ambient_substitution_cost": 12,
    "nonbaseline_overhead3_trace_class_count": 13,
    "largest_score_class_candidate_count": 14,
}


def read_csv_ints(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def padded(values: Sequence[int], size: int) -> list[int]:
    return [*values, *([-1] * (size - len(values)))]


def bounded_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"selected_symbol_{index}_id"])
        for index in range(int(row["walk_length"]))
    )


def bounded_atoms(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"selected_atom_{index}_id"])
        for index in range(int(row["walk_length"]))
    )


def bounded_edges(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"cell_edge_{index}_id"])
        for index in range(int(row["walk_length"]))
    )


def bounded_carriers(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"carrier_{index}_id"])
        for index in range(int(row["walk_length"]) + 1)
    )


def bounded_score(row: dict[str, int]) -> tuple[int, int, int, int]:
    return (
        int(row["trace_detour_overhead"]),
        int(row["signature_valley_depth"]),
        int(row["metric_gromov_delta_twice"]),
        int(row["trace_signature_total_variation"]),
    )


def trace_edges(trace: Sequence[int]) -> tuple[tuple[int, int], ...]:
    return tuple((int(source), int(target)) for source, target in zip(trace, trace[1:]))


def levenshtein(left: Sequence[Any], right: Sequence[Any]) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_value in enumerate(left, start=1):
        current = [left_index, *([0] * len(right))]
        for right_index, right_value in enumerate(right, start=1):
            current[right_index] = min(
                previous[right_index] + 1,
                current[right_index - 1] + 1,
                previous[right_index - 1] + int(left_value != right_value),
            )
        previous = current
    return int(previous[-1])


def common_prefix_suffix(
    left: Sequence[int],
    right: Sequence[int],
) -> tuple[int, int, tuple[int, ...], tuple[int, ...]]:
    prefix = 0
    limit = min(len(left), len(right))
    while prefix < limit and left[prefix] == right[prefix]:
        prefix += 1
    suffix = 0
    remaining = min(len(left) - prefix, len(right) - prefix)
    while (
        suffix < remaining
        and left[len(left) - suffix - 1] == right[len(right) - suffix - 1]
    ):
        suffix += 1
    left_stop = len(left) - suffix if suffix else len(left)
    right_stop = len(right) - suffix if suffix else len(right)
    return (
        prefix,
        suffix,
        tuple(int(value) for value in left[prefix:left_stop]),
        tuple(int(value) for value in right[prefix:right_stop]),
    )


def rewrite_adjacency(
    rewrite_edges: Iterable[dict[str, int]],
) -> dict[int, list[int]]:
    adjacency: dict[int, list[int]] = defaultdict(list)
    for row in rewrite_edges:
        source = int(row["source_node_id"])
        target = int(row["target_node_id"])
        adjacency[source].append(target)
        adjacency[target].append(source)
    return {node: sorted(set(neighbors)) for node, neighbors in adjacency.items()}


def rewrite_distance(adjacency: dict[int, list[int]], source: int, target: int) -> int:
    if source == target:
        return 0
    queue: deque[tuple[int, int]] = deque([(source, 0)])
    seen = {source}
    while queue:
        node, distance = queue.popleft()
        for neighbor in adjacency.get(node, []):
            if neighbor == target:
                return distance + 1
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, distance + 1))
    raise AssertionError(f"rewrite nodes are disconnected: {source}, {target}")


def aligned_ambient_substitution_cost(
    adjacency: dict[int, list[int]],
    left: Sequence[int],
    right: Sequence[int],
) -> int:
    _prefix, _suffix, left_branch, right_branch = common_prefix_suffix(left, right)
    if len(left_branch) != len(right_branch):
        return -1
    return sum(
        rewrite_distance(adjacency, int(source), int(target))
        for source, target in zip(left_branch, right_branch)
    )


def min_pair_distance(
    left_rows: list[dict[str, int]],
    right_rows: list[dict[str, int]],
    extractor: Callable[[dict[str, int]], tuple[int, ...]],
) -> tuple[int, int, int]:
    best_distance = 10**9
    best_left = -1
    best_right = -1
    for left in left_rows:
        left_values = extractor(left)
        for right in right_rows:
            distance = levenshtein(left_values, extractor(right))
            if distance < best_distance:
                best_distance = distance
                best_left = int(left["walk_candidate_id"])
                best_right = int(right["walk_candidate_id"])
    return int(best_distance), best_left, best_right


def build_transition_row(
    transition_id: int,
    source: dict[str, Any],
    target: dict[str, Any],
    rewrite_graph: dict[int, list[int]],
) -> dict[str, int]:
    source_trace = tuple(int(value) for value in source["trace_nodes"])
    target_trace = tuple(int(value) for value in target["trace_nodes"])
    prefix, suffix, source_branch, target_branch = common_prefix_suffix(
        source_trace,
        target_trace,
    )
    symbol_distance, source_symbol_id, target_symbol_id = min_pair_distance(
        source["rows"],
        target["rows"],
        bounded_word,
    )
    atom_distance, _source_atom_id, _target_atom_id = min_pair_distance(
        source["rows"],
        target["rows"],
        bounded_atoms,
    )
    carrier_distance, _source_carrier_id, _target_carrier_id = min_pair_distance(
        source["rows"],
        target["rows"],
        bounded_carriers,
    )
    edge_distance, _source_edge_id, _target_edge_id = min_pair_distance(
        source["rows"],
        target["rows"],
        bounded_edges,
    )
    return {
        "transition_id": transition_id,
        "source_trace_class_id": int(source["trace_class_id"]),
        "target_trace_class_id": int(target["trace_class_id"]),
        "source_baseline_alias_flag": int(source_trace == BASELINE_TRACE),
        "target_target1_branch_flag": int(target_trace == TARGET1_TRACE),
        "common_prefix_node_count": prefix,
        "common_suffix_node_count": suffix,
        "source_divergent_node_count": len(source_branch),
        "target_divergent_node_count": len(target_branch),
        "trace_node_edit_distance": levenshtein(source_trace, target_trace),
        "trace_edge_edit_distance": levenshtein(
            trace_edges(source_trace),
            trace_edges(target_trace),
        ),
        "trace_ambient_aligned_substitution_cost": aligned_ambient_substitution_cost(
            rewrite_graph,
            source_trace,
            target_trace,
        ),
        "symbol_word_min_edit_distance": symbol_distance,
        "closed_repair_word_edit_distance": levenshtein(
            BASELINE_CLOSED_REPAIR_WORD,
            TARGET1_CLOSED_REPAIR_WORD,
        ),
        "atom_word_min_edit_distance": atom_distance,
        "carrier_path_min_edit_distance": carrier_distance,
        "cell_edge_path_min_edit_distance": edge_distance,
        "source_divergent_node_0_id": source_branch[0] if len(source_branch) > 0 else -1,
        "source_divergent_node_1_id": source_branch[1] if len(source_branch) > 1 else -1,
        "target_divergent_node_0_id": target_branch[0] if len(target_branch) > 0 else -1,
        "target_divergent_node_1_id": target_branch[1] if len(target_branch) > 1 else -1,
        "source_best_symbol_edit_candidate_id": source_symbol_id,
        "target_best_symbol_edit_candidate_id": target_symbol_id,
    }


def build_pairwise_row(
    source: dict[str, Any],
    target: dict[str, Any],
    rewrite_graph: dict[int, list[int]],
) -> dict[str, int]:
    source_trace = tuple(int(value) for value in source["trace_nodes"])
    target_trace = tuple(int(value) for value in target["trace_nodes"])
    prefix, suffix, source_branch, target_branch = common_prefix_suffix(
        source_trace,
        target_trace,
    )
    return {
        "source_trace_class_id": int(source["trace_class_id"]),
        "target_trace_class_id": int(target["trace_class_id"]),
        "common_prefix_node_count": prefix,
        "common_suffix_node_count": suffix,
        "source_divergent_node_count": len(source_branch),
        "target_divergent_node_count": len(target_branch),
        "trace_node_edit_distance": levenshtein(source_trace, target_trace),
        "trace_edge_edit_distance": levenshtein(
            trace_edges(source_trace),
            trace_edges(target_trace),
        ),
        "trace_ambient_aligned_substitution_cost": aligned_ambient_substitution_cost(
            rewrite_graph,
            source_trace,
            target_trace,
        ),
        "source_rank_min": int(source["rank_min"]),
        "target_rank_min": int(target["rank_min"]),
    }


def build_payloads() -> dict[str, Any]:
    bounded_report = load_json(BOUNDED_BACKTRACK_REPORT)
    bounded_search = load_json(BOUNDED_BACKTRACK_JSON)
    bounded_certificate = load_json(BOUNDED_BACKTRACK_CERTIFICATE)
    closed_report = load_json(CLOSED_REPAIR_REPORT)
    closed_repair = load_json(CLOSED_REPAIR_JSON)
    closed_certificate = load_json(CLOSED_REPAIR_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    bounded_tables = np.load(BOUNDED_BACKTRACK_TABLES, allow_pickle=False)
    closed_tables = np.load(CLOSED_REPAIR_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)

    bounded_candidate_table = np.asarray(
        bounded_tables["candidate_table"],
        dtype=np.int64,
    )
    closed_repair_class_table = np.asarray(
        closed_tables["repair_class_table"],
        dtype=np.int64,
    )
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_node_table = np.asarray(rewrite_tables["node_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    bounded_rows = read_csv_ints(BOUNDED_BACKTRACK_CANDIDATES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    rewrite_nodes = read_int_csv(REWRITE_COMPLEX_NODES)

    assoc_by_word = associativity_lookup(associativity_rows)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }
    rewrite_graph = rewrite_adjacency(rewrite_edges)
    rewrite_node_by_id = {int(row["node_id"]): row for row in rewrite_nodes}
    score_histogram: Counter[tuple[int, int, int, int]] = Counter(
        bounded_score(row) for row in bounded_rows
    )

    class_accumulator: dict[tuple[int, ...], dict[str, Any]] = {}
    metric_recompute_mismatches = 0
    for row in bounded_rows:
        if int(row["trace_detour_overhead"]) != TARGET_OVERHEAD:
            continue
        raw_windows, trace_nodes, trace_signatures, metrics = build_trace(
            bounded_word(row),
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        expected_score = bounded_score(row)
        recomputed_score = (
            int(metrics["trace_detour_overhead"]),
            int(metrics["signature_valley_depth"]),
            int(metrics["metric_gromov_delta_twice"]),
            int(metrics["trace_signature_total_variation"]),
        )
        if recomputed_score != expected_score:
            metric_recompute_mismatches += 1
        trace = tuple(int(value) for value in trace_nodes)
        accumulator = class_accumulator.setdefault(
            trace,
            {
                "trace_nodes": trace,
                "trace_signatures": tuple(int(value) for value in trace_signatures),
                "metrics": {key: int(value) for key, value in metrics.items()},
                "rows": [],
            },
        )
        accumulator["rows"].append(row)

    class_payloads = sorted(
        class_accumulator.values(),
        key=lambda payload: (
            min(int(row["rank_order"]) for row in payload["rows"]),
            payload["trace_nodes"],
        ),
    )

    trace_class_rows: list[dict[str, int]] = []
    node_readout_rows: list[dict[str, int]] = []
    trace_class_payloads: list[dict[str, Any]] = []
    for class_index, payload in enumerate(class_payloads):
        rows = sorted(payload["rows"], key=lambda row: int(row["rank_order"]))
        ranks = [int(row["rank_order"]) for row in rows]
        walk_lengths = [int(row["walk_length"]) for row in rows]
        symbol_words = Counter(bounded_word(row) for row in rows)
        carrier_paths = {bounded_carriers(row) for row in rows}
        cell_edge_paths = {bounded_edges(row) for row in rows}
        atom_words = {bounded_atoms(row) for row in rows}
        signature_sequences = {
            tuple(
                int(value)
                for value in build_trace(
                    bounded_word(row),
                    assoc_by_word,
                    rewrite_edge_by_pair,
                )[2]
            )
            for row in rows
        }
        trace = tuple(int(value) for value in payload["trace_nodes"])
        trace_signatures = tuple(int(value) for value in payload["trace_signatures"])
        metrics = payload["metrics"]
        representative = rows[0]
        score = bounded_score(representative)
        rank_min = min(ranks)
        rank_max = max(ranks)
        class_payload = {
            **payload,
            "trace_class_id": class_index,
            "rank_min": rank_min,
            "rank_max": rank_max,
            "rows": rows,
        }
        trace_class_payloads.append(class_payload)
        trace_class_rows.append(
            {
                "trace_class_id": class_index,
                "class_rank_order": class_index + 1,
                "candidate_count": len(rows),
                "rank_min": rank_min,
                "rank_max": rank_max,
                "rank_gap_count": rank_max - rank_min + 1 - len(rows),
                "rank_interval_contiguous_flag": int(
                    rank_max - rank_min + 1 == len(rows)
                ),
                "walk_length_min": min(walk_lengths),
                "walk_length_max": max(walk_lengths),
                "distinct_symbol_word_count": len(symbol_words),
                "distinct_carrier_path_count": len(carrier_paths),
                "distinct_cell_edge_path_count": len(cell_edge_paths),
                "distinct_atom_word_count": len(atom_words),
                "distinct_trace_signature_count": len(signature_sequences),
                "score_better_candidate_count": sum(
                    count
                    for other_score, count in score_histogram.items()
                    if other_score < score
                ),
                "score_class_candidate_count": int(score_histogram[score]),
                "trace_node_count": len(trace),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(trace, MAX_TRACE_NODES),
                    )
                },
                **{
                    column: value
                    for column, value in zip(
                        TRACE_SIGNATURE_COLUMNS,
                        padded(trace_signatures, MAX_TRACE_NODES),
                    )
                },
                "trace_edge_count": int(metrics["trace_edge_count"]),
                "trace_detour_overhead": int(metrics["trace_detour_overhead"]),
                "signature_valley_depth": int(metrics["signature_valley_depth"]),
                "metric_gromov_delta_twice": int(
                    metrics["metric_gromov_delta_twice"]
                ),
                "trace_signature_total_variation": int(
                    metrics["trace_signature_total_variation"]
                ),
                "trace_min_signature_after_node42": int(
                    metrics["trace_min_signature_after_node42"]
                ),
                "baseline_alias_flag": int(trace == BASELINE_TRACE),
                "target1_branch_flag": int(trace == TARGET1_TRACE),
                "representative_candidate_id": int(
                    representative["walk_candidate_id"]
                ),
                "representative_rank_order": int(representative["rank_order"]),
                "representative_walk_length": int(representative["walk_length"]),
                **{
                    column: value
                    for column, value in zip(
                        REPRESENTATIVE_SYMBOL_COLUMNS,
                        padded(bounded_word(representative), MAX_SYMBOL_LENGTH),
                    )
                },
            }
        )
        for trace_rank, node_id in enumerate(trace):
            node = rewrite_node_by_id[int(node_id)]
            signature = int(node["signature_union_count"])
            node_readout_rows.append(
                {
                    "trace_class_id": class_index,
                    "trace_rank": trace_rank,
                    "node_id": int(node_id),
                    "signature_union_count": signature,
                    "sector_coverage_count": int(node["sector_coverage_count"]),
                    "graph_degree": int(node["graph_degree"]),
                    "signature_drop_from_node42": max(
                        0,
                        NODE42_SIGNATURE_UNION - signature,
                    ),
                    "local_valley_flag": int(
                        trace_rank >= 2 and signature < NODE42_SIGNATURE_UNION
                    ),
                    "baseline_divergent_flag": int(
                        trace == BASELINE_TRACE and trace_rank in (3, 4)
                    ),
                    "target1_divergent_flag": int(
                        trace == TARGET1_TRACE and trace_rank in (3, 4)
                    ),
                }
            )

    class_by_trace = {
        tuple(payload["trace_nodes"]): payload for payload in trace_class_payloads
    }
    baseline_payload = class_by_trace[BASELINE_TRACE]
    target1_payload = class_by_trace[TARGET1_TRACE]
    transition_rows = [
        build_transition_row(
            0,
            baseline_payload,
            target1_payload,
            rewrite_graph,
        )
    ]
    pairwise_rows = [
        build_pairwise_row(left, right, rewrite_graph)
        for left_index, left in enumerate(trace_class_payloads)
        for right in trace_class_payloads[left_index + 1 :]
    ]

    observable_values = {
        "overhead3_candidate_count": sum(len(payload["rows"]) for payload in class_payloads),
        "overhead3_trace_class_count": len(class_payloads),
        "baseline_alias_candidate_count": len(baseline_payload["rows"]),
        "baseline_alias_distinct_word_count": len(
            {bounded_word(row) for row in baseline_payload["rows"]}
        ),
        "target1_branch_candidate_count": len(target1_payload["rows"]),
        "target1_branch_distinct_word_count": len(
            {bounded_word(row) for row in target1_payload["rows"]}
        ),
        "classes_before_target1_count": int(target1_payload["trace_class_id"]),
        "candidates_before_target1_count": int(target1_payload["rank_min"]) - 1,
        "baseline_to_target_trace_node_edit_distance": transition_rows[0][
            "trace_node_edit_distance"
        ],
        "baseline_to_target_trace_edge_edit_distance": transition_rows[0][
            "trace_edge_edit_distance"
        ],
        "baseline_to_target_symbol_word_min_edit_distance": transition_rows[0][
            "symbol_word_min_edit_distance"
        ],
        "baseline_to_target_closed_repair_word_edit_distance": transition_rows[0][
            "closed_repair_word_edit_distance"
        ],
        "baseline_to_target_ambient_substitution_cost": transition_rows[0][
            "trace_ambient_aligned_substitution_cost"
        ],
        "nonbaseline_overhead3_trace_class_count": len(class_payloads) - 1,
        "largest_score_class_candidate_count": max(score_histogram.values()),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]

    trace_class_table = table_from_rows(TRACE_CLASS_COLUMNS, trace_class_rows)
    node_readout_table = table_from_rows(
        TRACE_NODE_READOUT_COLUMNS,
        node_readout_rows,
    )
    transition_table = table_from_rows(TRANSITION_EDIT_COLUMNS, transition_rows)
    pairwise_table = table_from_rows(PAIRWISE_TRACE_EDIT_COLUMNS, pairwise_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    class_counts = [int(row["candidate_count"]) for row in trace_class_rows]
    rank_mins = [int(row["rank_min"]) for row in trace_class_rows]
    rank_maxes = [int(row["rank_max"]) for row in trace_class_rows]
    checks = {
        "bounded_backtrack_report_certified": bounded_report.get("status")
        == BOUNDED_BACKTRACK_STATUS,
        "bounded_backtrack_certificate_certified": bounded_certificate.get("status")
        == BOUNDED_BACKTRACK_STATUS,
        "bounded_backtrack_schema_available": bounded_search.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1",
        "closed_repair_report_certified": closed_report.get("status")
        == CLOSED_REPAIR_STATUS,
        "closed_repair_certificate_certified": closed_certificate.get("status")
        == CLOSED_REPAIR_STATUS,
        "closed_repair_schema_available": closed_repair.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking@1",
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
        "bounded_candidate_table_shape_is_1287_by_codebook": tuple(
            bounded_candidate_table.shape
        )
        == (1287, len(WALK_CANDIDATE_COLUMNS)),
        "closed_repair_class_table_has_two_rows": tuple(
            closed_repair_class_table.shape
        )[0]
        == 2,
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_node_table_shape_is_56_by_17": tuple(rewrite_node_table.shape)
        == (56, 17),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "overhead3_candidate_count_is_240": observable_values[
            "overhead3_candidate_count"
        ]
        == 240,
        "overhead3_trace_class_count_is_7": observable_values[
            "overhead3_trace_class_count"
        ]
        == 7,
        "trace_class_counts_match": class_counts == [103, 18, 3, 9, 51, 35, 21],
        "trace_class_rank_mins_match": rank_mins
        == [1, 104, 122, 125, 134, 137, 150],
        "trace_class_rank_maxes_match": rank_maxes
        == [103, 121, 124, 133, 233, 240, 205],
        "all_overhead3_metrics_recompute": metric_recompute_mismatches == 0,
        "all_trace_classes_share_forced_prefix_and_aperture": all(
            tuple(payload["trace_nodes"][:3]) == (48, 42, 27)
            and int(payload["trace_nodes"][-1]) == 44
            for payload in trace_class_payloads
        ),
        "baseline_class_is_first_and_broad": int(baseline_payload["trace_class_id"])
        == 0
        and len(baseline_payload["rows"]) == 103
        and len({bounded_word(row) for row in baseline_payload["rows"]}) == 14,
        "target1_class_is_third_and_small": int(target1_payload["trace_class_id"])
        == 2
        and len(target1_payload["rows"]) == 3
        and len({bounded_word(row) for row in target1_payload["rows"]}) == 1,
        "target1_rank_interval_is_122_to_124": target1_payload["rank_min"] == 122
        and target1_payload["rank_max"] == 124,
        "baseline_to_target_trace_edit_is_two": transition_rows[0][
            "trace_node_edit_distance"
        ]
        == 2,
        "baseline_to_target_edge_edit_is_three": transition_rows[0][
            "trace_edge_edit_distance"
        ]
        == 3,
        "baseline_to_target_symbol_edit_is_three": transition_rows[0][
            "symbol_word_min_edit_distance"
        ]
        == 3,
        "baseline_to_target_closed_repair_edit_is_three": transition_rows[0][
            "closed_repair_word_edit_distance"
        ]
        == 3,
        "baseline_to_target_ambient_substitution_cost_is_three": transition_rows[0][
            "trace_ambient_aligned_substitution_cost"
        ]
        == 3,
        "trace_class_table_shape_matches_codebook": tuple(trace_class_table.shape)
        == (7, len(TRACE_CLASS_COLUMNS)),
        "node_readout_table_shape_matches_codebook": tuple(node_readout_table.shape)
        == (42, len(TRACE_NODE_READOUT_COLUMNS)),
        "transition_table_shape_matches_codebook": tuple(transition_table.shape)
        == (1, len(TRANSITION_EDIT_COLUMNS)),
        "pairwise_trace_edit_table_shape_matches_codebook": tuple(pairwise_table.shape)
        == (21, len(PAIRWISE_TRACE_EDIT_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    trace_classes_witness = {
        str(row["trace_class_id"]): {
            "candidate_count": row["candidate_count"],
            "rank_interval": [row["rank_min"], row["rank_max"]],
            "rank_gap_count": row["rank_gap_count"],
            "distinct_symbol_word_count": row["distinct_symbol_word_count"],
            "trace_nodes": [
                value
                for value in [row[column] for column in TRACE_NODE_COLUMNS]
                if value >= 0
            ],
            "trace_signatures": [
                value
                for value in [row[column] for column in TRACE_SIGNATURE_COLUMNS]
                if value >= 0
            ],
            "score": {
                "trace_detour_overhead": row["trace_detour_overhead"],
                "signature_valley_depth": row["signature_valley_depth"],
                "metric_gromov_delta_twice": row["metric_gromov_delta_twice"],
                "trace_signature_total_variation": row[
                    "trace_signature_total_variation"
                ],
            },
            "baseline_alias": bool(row["baseline_alias_flag"]),
            "target1_branch": bool(row["target1_branch_flag"]),
            "representative_word": [
                value
                for value in [
                    row[column] for column in REPRESENTATIVE_SYMBOL_COLUMNS
                ]
                if value >= 0
            ],
        }
        for row in trace_class_rows
    }
    transition_witness = {
        key: transition_rows[0][key]
        for key in [
            "common_prefix_node_count",
            "common_suffix_node_count",
            "source_divergent_node_count",
            "target_divergent_node_count",
            "trace_node_edit_distance",
            "trace_edge_edit_distance",
            "trace_ambient_aligned_substitution_cost",
            "symbol_word_min_edit_distance",
            "closed_repair_word_edit_distance",
            "atom_word_min_edit_distance",
            "carrier_path_min_edit_distance",
            "cell_edge_path_min_edit_distance",
            "source_divergent_node_0_id",
            "source_divergent_node_1_id",
            "target_divergent_node_0_id",
            "target_divergent_node_1_id",
            "source_best_symbol_edit_candidate_id",
            "target_best_symbol_edit_candidate_id",
        ]
    }

    witness = {
        "trace_class_count": len(trace_class_rows),
        "overhead3_candidate_count": observable_values["overhead3_candidate_count"],
        "trace_classes": trace_classes_witness,
        "baseline_to_target1_transition": transition_witness,
        "trace_class_table_sha256": sha_array(trace_class_table),
        "node_readout_table_sha256": sha_array(node_readout_table),
        "transition_table_sha256": sha_array(transition_table),
        "pairwise_trace_edit_table_sha256": sha_array(pairwise_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    quotient = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient@1",
        "object": "d20",
        "quotient_rule": {
            "source_space": "the 240 bounded candidates with trace_detour_overhead = 3",
            "class_key": "collapsed anchored rewrite trace node sequence up to first node44",
            "transition_metric": "unit Levenshtein edit on trace nodes, plus ambient rewrite distance for aligned divergent substitutions",
            "repair_transition": "baseline closed repair word x2,x1,x4,x5,x2,x5 versus target1 closed repair word x2,x1,x5,x2,x5,x4,x3",
        },
        "summary": {
            "overhead3_candidate_count": observable_values["overhead3_candidate_count"],
            "trace_class_count": len(trace_class_rows),
            "baseline_trace_class": trace_classes_witness[
                str(baseline_payload["trace_class_id"])
            ],
            "target1_trace_class": trace_classes_witness[
                str(target1_payload["trace_class_id"])
            ],
            "baseline_to_target1_transition": transition_witness,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD3_TRACE_CLASS_QUOTIENT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 240 overhead-3 bounded first-return candidates collapse to seven anchored trace-node classes",
            "the baseline alias class is first, has 103 candidates, and has 14 distinct selected-symbol words",
            "the target1 repair branch is the third overhead-3 trace class, has 3 candidates, and has a single selected-symbol word",
            "baseline-to-target1 transition preserves prefix 48->42->27 and final node44, replacing branch nodes 28,34 by 29,45",
            "the baseline-to-target1 trace edit distance is 2, the trace-edge edit distance is 3, the closed repair symbol edit distance is 3, and the aligned ambient rewrite substitution cost is 3",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The bounded overhead-3 search has seven trace classes. The "
            "baseline alias is a broad 103-candidate basin, while the closed "
            "target1 repair is a small three-candidate branch reached from "
            "the baseline trace by two node substitutions over a shared "
            "48->42->27 prefix and node44 endpoint."
        ),
        "stage_protocol": {
            "draft": "quotient all bounded overhead-3 candidates by collapsed anchored trace nodes",
            "witness": "materialize trace class counts, rank intervals, node signatures, and pairwise trace edits",
            "coherence": "separate the broad baseline alias basin from the small target1 repair branch",
            "closure": "certify the minimal baseline-to-target1 trace and selected-symbol transition edits inside the bounded quotient",
            "emit": "emit trace-class quotient JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "bounded_backtrack_report": input_entry(
                BOUNDED_BACKTRACK_REPORT,
                {
                    "status": bounded_report.get("status"),
                    "certificate_sha256": bounded_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "bounded_backtrack_json": input_entry(BOUNDED_BACKTRACK_JSON),
            "bounded_backtrack_candidates": input_entry(BOUNDED_BACKTRACK_CANDIDATES),
            "bounded_backtrack_tables": input_entry(BOUNDED_BACKTRACK_TABLES),
            "bounded_backtrack_certificate": input_entry(BOUNDED_BACKTRACK_CERTIFICATE),
            "closed_repair_report": input_entry(
                CLOSED_REPAIR_REPORT,
                {
                    "status": closed_report.get("status"),
                    "certificate_sha256": closed_report.get("certificate_sha256"),
                },
            ),
            "closed_repair_json": input_entry(CLOSED_REPAIR_JSON),
            "closed_repair_tables": input_entry(CLOSED_REPAIR_TABLES),
            "closed_repair_certificate": input_entry(CLOSED_REPAIR_CERTIFICATE),
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
            "symbolic_associativity_tables": input_entry(SYMBOLIC_ASSOCIATIVITY_TABLES),
            "symbolic_associativity_certificate": input_entry(
                SYMBOLIC_ASSOCIATIVITY_CERTIFICATE
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_overhead3_trace_class_quotient": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_trace_class_quotient.json"
            ),
            "aperture_overhead3_trace_classes_csv": relpath(
                OUT_DIR / "aperture_overhead3_trace_classes.csv"
            ),
            "aperture_overhead3_trace_node_readout_csv": relpath(
                OUT_DIR / "aperture_overhead3_trace_node_readout.csv"
            ),
            "aperture_overhead3_transition_edits_csv": relpath(
                OUT_DIR / "aperture_overhead3_transition_edits.csv"
            ),
            "aperture_overhead3_pairwise_trace_edits_csv": relpath(
                OUT_DIR / "aperture_overhead3_pairwise_trace_edits.csv"
            ),
            "aperture_overhead3_trace_quotient_observables_csv": relpath(
                OUT_DIR / "aperture_overhead3_trace_quotient_observables.csv"
            ),
            "signature_boundary_spine_aperture_overhead3_trace_class_quotient_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_tables.npz"
            ),
            "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the trace-node quotient of bounded overhead-3 candidates",
                "rank intervals, symbol-word breadth, and node-signature readouts for each trace class",
                "the baseline-to-target1 transition edit inside this quotient",
                "that the target1 closed repair is a distinct overhead-3 trace branch rather than a baseline alias",
            ],
            "does_not_certify_because_not_required": [
                "bounded candidates with overhead other than 3",
                "walks longer than the already-certified bounded search",
                "why the rank-104 nonbaseline class is not a closed repair target",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Audit the rank-104 nonbaseline valley-37 class "
            "48->42->27->31->50->44: it beats the target1 branch by rank and "
            "variation, but did not appear in the closed repair classes. Test "
            "whether it is outside the overhead-2 target language or exposes a "
            "new repair family."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified bounded-backtrack, closed-repair, cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "recompute anchored rewrite traces for all bounded overhead-3 candidates",
            "quotient candidates by collapsed trace-node sequence",
            "materialize trace-class node signatures and pairwise trace edits",
            "compute baseline-to-target1 transition edits at trace, symbol, atom, carrier, and cell-edge levels",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_overhead3_trace_class_quotient": quotient,
        "aperture_overhead3_trace_classes_csv": csv_text(
            TRACE_CLASS_COLUMNS,
            trace_class_rows,
        ),
        "aperture_overhead3_trace_node_readout_csv": csv_text(
            TRACE_NODE_READOUT_COLUMNS,
            node_readout_rows,
        ),
        "aperture_overhead3_transition_edits_csv": csv_text(
            TRANSITION_EDIT_COLUMNS,
            transition_rows,
        ),
        "aperture_overhead3_pairwise_trace_edits_csv": csv_text(
            PAIRWISE_TRACE_EDIT_COLUMNS,
            pairwise_rows,
        ),
        "aperture_overhead3_trace_quotient_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "trace_class_table": trace_class_table,
        "node_readout_table": node_readout_table,
        "transition_table": transition_table,
        "pairwise_trace_edit_table": pairwise_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_overhead3_trace_class_quotient.json",
        payloads["signature_boundary_spine_aperture_overhead3_trace_class_quotient"],
    )
    (OUT_DIR / "aperture_overhead3_trace_classes.csv").write_text(
        payloads["aperture_overhead3_trace_classes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_trace_node_readout.csv").write_text(
        payloads["aperture_overhead3_trace_node_readout_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_transition_edits.csv").write_text(
        payloads["aperture_overhead3_transition_edits_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_pairwise_trace_edits.csv").write_text(
        payloads["aperture_overhead3_pairwise_trace_edits_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_trace_quotient_observables.csv").write_text(
        payloads["aperture_overhead3_trace_quotient_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_tables.npz",
        trace_class_table=payloads["trace_class_table"],
        node_readout_table=payloads["node_readout_table"],
        transition_table=payloads["transition_table"],
        pairwise_trace_edit_table=payloads["pairwise_trace_edit_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate"
        ],
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
                "trace_class_count": witness["trace_class_count"],
                "overhead3_candidate_count": witness["overhead3_candidate_count"],
                "baseline_to_target1_transition": witness[
                    "baseline_to_target1_transition"
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
