from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Sequence

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STRICT_INTERMEDIATE_NODE_ID,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability import (
        advance_states,
        build_carrier_adjacency,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        selected_prefix_consumed,
        target_match_indices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap import (
        OUT_DIR as STRONGIFICATION_GAP_DIR,
        STATUS as STRONGIFICATION_GAP_STATUS,
        first_return_closed,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BASELINE_TRACE,
        TARGET1_CLOSED_REPAIR_WORD,
        TARGET1_TRACE,
        TRACE_CLASS_COLUMNS,
        TRACE_NODE_COLUMNS as QUOTIENT_TRACE_NODE_COLUMNS,
        OUT_DIR as TRACE_QUOTIENT_DIR,
        STATUS as TRACE_QUOTIENT_STATUS,
        common_prefix_suffix,
        levenshtein,
        padded,
        trace_edges,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit import (
        RANK104_TRACE,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        SYMBOLIC_ALPHABET_CSV,
        shared_atoms,
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
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STRICT_INTERMEDIATE_NODE_ID,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability import (
        advance_states,
        build_carrier_adjacency,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        selected_prefix_consumed,
        target_match_indices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap import (
        OUT_DIR as STRONGIFICATION_GAP_DIR,
        STATUS as STRONGIFICATION_GAP_STATUS,
        first_return_closed,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BASELINE_TRACE,
        TARGET1_CLOSED_REPAIR_WORD,
        TARGET1_TRACE,
        TRACE_CLASS_COLUMNS,
        TRACE_NODE_COLUMNS as QUOTIENT_TRACE_NODE_COLUMNS,
        OUT_DIR as TRACE_QUOTIENT_DIR,
        STATUS as TRACE_QUOTIENT_STATUS,
        common_prefix_suffix,
        levenshtein,
        padded,
        trace_edges,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit import (
        RANK104_TRACE,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        SYMBOLIC_ALPHABET_CSV,
        shared_atoms,
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
    "c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_RANK104_STRONGIFICATION_BRANCH_GEOMETRY_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

STRONGIFICATION_GAP_REPORT = STRONGIFICATION_GAP_DIR / "report.json"
STRONGIFICATION_GAP_JSON = (
    STRONGIFICATION_GAP_DIR
    / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap.json"
)
STRONGIFICATION_GAP_WITNESSES = (
    STRONGIFICATION_GAP_DIR / "aperture_overhead3_strongification_witnesses.csv"
)
STRONGIFICATION_GAP_TABLES = (
    STRONGIFICATION_GAP_DIR
    / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_tables.npz"
)
STRONGIFICATION_GAP_CERTIFICATE = (
    STRONGIFICATION_GAP_DIR
    / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate.json"
)

TRACE_QUOTIENT_REPORT = TRACE_QUOTIENT_DIR / "report.json"
TRACE_QUOTIENT_CLASSES = TRACE_QUOTIENT_DIR / "aperture_overhead3_trace_classes.csv"
TRACE_QUOTIENT_TABLES = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_tables.npz"
)
TRACE_QUOTIENT_CERTIFICATE = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry.py"
)

TARGET1_BRANCH_ID = 0
RANK104_STRONG_BRANCH_ID = 1
RANK104_BEST_STRONG_WORD = (2, 1, 3, 4, 1, 5, 2, 1, 4, 5)

MAX_WORD_LENGTH = 10
MAX_TRACE_NODES = 12
MAX_SKIPPED_NODES = 8
ANCHOR_NODE_IDS = (28, 29, 31, 34, 45, 50)

WORD_COLUMNS = [f"symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_TRACE_NODES)]
TRACE_SIGNATURE_COLUMNS = [
    f"trace_signature_{index}_count" for index in range(MAX_TRACE_NODES)
]
SKIPPED_NODE_COLUMNS = [
    f"geodesic_skipped_node_{index}_id" for index in range(MAX_SKIPPED_NODES)
]

BRANCH_PROFILE_COLUMNS = [
    "branch_id",
    "branch_code",
    "target_word_id",
    "word_length",
    *WORD_COLUMNS,
    "target_last_symbol_rank",
    "first_node44_consumed_symbol_count",
    "strong_first_hit_flag",
    "closed_path_count",
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    *TRACE_SIGNATURE_COLUMNS,
    "trace_edge_count",
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "trace_min_signature_after_node42",
    "metric_diameter",
    "metric_radius",
    "shortcut_start_node_id",
    "shortcut_end_node_id",
    "shortcut_trace_segment_edge_count",
    "shortcut_ambient_distance",
    "shortcut_saved_edge_count",
    "geodesic_skipped_node_count",
    *SKIPPED_NODE_COLUMNS,
]

COMPARISON_COLUMNS = [
    "comparison_id",
    "source_branch_id",
    "target_branch_id",
    "common_prefix_node_count",
    "common_suffix_node_count",
    "source_divergent_node_count",
    "target_divergent_node_count",
    "trace_node_edit_distance",
    "trace_edge_edit_distance",
    "target_extra_trace_edge_count",
    "target_overhead_gap",
    "target_variation_advantage",
    "same_valley_depth_flag",
    "same_gromov_delta_flag",
    "target_closed_path_advantage",
    "source_divergent_node_0_id",
    "source_divergent_node_1_id",
    "target_divergent_node_0_id",
    "target_divergent_node_1_id",
    "target_divergent_node_2_id",
    "target_divergent_node_3_id",
    "target_divergent_node_4_id",
]

ANCHOR_NODE_COLUMNS = [
    "anchor_node_id",
    "baseline_divergent_flag",
    "target1_divergent_flag",
    "rank104_original_divergent_flag",
    "rank104_strong_occurrence_count",
    "target1_occurrence_count",
    "node_role_code",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "branch_count": 0,
    "target1_trace_overhead": 1,
    "rank104_strong_trace_overhead": 2,
    "rank104_overhead_gap": 3,
    "target1_variation": 4,
    "rank104_strong_variation": 5,
    "rank104_variation_advantage": 6,
    "same_valley_depth_flag": 7,
    "same_gromov_delta_flag": 8,
    "target1_closed_path_count": 9,
    "rank104_closed_path_count": 10,
    "rank104_closed_path_advantage": 11,
    "target1_skipped_node_count": 12,
    "rank104_skipped_node_count": 13,
    "rank104_hybrid_anchor_node_count": 14,
}


def witness_rows(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def carrier_paths(
    word: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    states = [(12, (12,), (), ())]
    for symbol_id in word:
        states = advance_states(states, symbol_id, adjacency)
        if not states:
            break
    return states


def rewrite_adjacency(edges: list[dict[str, int]]) -> dict[int, list[int]]:
    graph: dict[int, set[int]] = defaultdict(set)  # type: ignore[name-defined]
    for row in edges:
        source = int(row["source_node_id"])
        target = int(row["target_node_id"])
        graph[source].add(target)
        graph[target].add(source)
    return {node: sorted(neighbors) for node, neighbors in graph.items()}


def rewrite_distance(graph: dict[int, list[int]], source: int, target: int) -> int:
    if source == target:
        return 0
    queue: deque[tuple[int, int]] = deque([(source, 0)])
    seen = {source}
    while queue:
        node, distance = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor == target:
                return distance + 1
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, distance + 1))
    raise AssertionError(f"disconnected rewrite nodes: {source}, {target}")


def branch_profile(
    branch_id: int,
    branch_code: int,
    target_word_id: int,
    word: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
    assoc_by_word: dict[tuple[int, ...], dict[str, int]],
    rewrite_edge_by_pair: dict[tuple[int, int], dict[str, int]],
    rewrite_graph: dict[int, list[int]],
) -> dict[str, int]:
    raw_windows, trace_nodes, trace_signatures, metrics = build_trace(
        word,
        assoc_by_word,
        rewrite_edge_by_pair,
    )
    consumed_count, _raw_rank = selected_prefix_consumed(raw_windows, len(word))
    target_indices = target_match_indices(
        word,
        tuple(int(value) for value in LOWER_OVERHEAD_TAIL_WORDS[target_word_id]),
    )
    closed_paths = first_return_closed(carrier_paths(word, adjacency))
    skipped_nodes = tuple(int(value) for value in trace_nodes[2:-1])
    shortcut_segment_edges = len(trace_nodes) - 2
    shortcut_distance = rewrite_distance(
        rewrite_graph,
        STRICT_INTERMEDIATE_NODE_ID,
        APERTURE_NODE_ID,
    )
    return {
        "branch_id": branch_id,
        "branch_code": branch_code,
        "target_word_id": target_word_id,
        "word_length": len(word),
        **{
            column: value
            for column, value in zip(WORD_COLUMNS, padded(word, MAX_WORD_LENGTH))
        },
        "target_last_symbol_rank": target_indices[-1] if target_indices else -1,
        "first_node44_consumed_symbol_count": consumed_count,
        "strong_first_hit_flag": int(
            bool(target_indices) and consumed_count >= 0 and target_indices[-1] < consumed_count
        ),
        "closed_path_count": len(closed_paths),
        "trace_node_count": len(trace_nodes),
        **{
            column: value
            for column, value in zip(
                TRACE_NODE_COLUMNS,
                padded(trace_nodes, MAX_TRACE_NODES),
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
        "metric_gromov_delta_twice": int(metrics["metric_gromov_delta_twice"]),
        "trace_signature_total_variation": int(
            metrics["trace_signature_total_variation"]
        ),
        "trace_min_signature_after_node42": int(
            metrics["trace_min_signature_after_node42"]
        ),
        "metric_diameter": int(metrics["metric_diameter"]),
        "metric_radius": int(metrics["metric_radius"]),
        "shortcut_start_node_id": STRICT_INTERMEDIATE_NODE_ID,
        "shortcut_end_node_id": APERTURE_NODE_ID,
        "shortcut_trace_segment_edge_count": shortcut_segment_edges,
        "shortcut_ambient_distance": shortcut_distance,
        "shortcut_saved_edge_count": shortcut_segment_edges - shortcut_distance,
        "geodesic_skipped_node_count": len(skipped_nodes),
        **{
            column: value
            for column, value in zip(
                SKIPPED_NODE_COLUMNS,
                padded(skipped_nodes, MAX_SKIPPED_NODES),
            )
        },
    }


def row_trace(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in TRACE_NODE_COLUMNS[: row["trace_node_count"]])


def comparison_row(source: dict[str, int], target: dict[str, int]) -> dict[str, int]:
    source_trace = row_trace(source)
    target_trace = row_trace(target)
    prefix, suffix, source_divergent, target_divergent = common_prefix_suffix(
        source_trace,
        target_trace,
    )
    return {
        "comparison_id": 0,
        "source_branch_id": source["branch_id"],
        "target_branch_id": target["branch_id"],
        "common_prefix_node_count": prefix,
        "common_suffix_node_count": suffix,
        "source_divergent_node_count": len(source_divergent),
        "target_divergent_node_count": len(target_divergent),
        "trace_node_edit_distance": levenshtein(source_trace, target_trace),
        "trace_edge_edit_distance": levenshtein(
            trace_edges(source_trace),
            trace_edges(target_trace),
        ),
        "target_extra_trace_edge_count": target["trace_edge_count"]
        - source["trace_edge_count"],
        "target_overhead_gap": target["trace_detour_overhead"]
        - source["trace_detour_overhead"],
        "target_variation_advantage": source["trace_signature_total_variation"]
        - target["trace_signature_total_variation"],
        "same_valley_depth_flag": int(
            target["signature_valley_depth"] == source["signature_valley_depth"]
        ),
        "same_gromov_delta_flag": int(
            target["metric_gromov_delta_twice"] == source["metric_gromov_delta_twice"]
        ),
        "target_closed_path_advantage": target["closed_path_count"]
        - source["closed_path_count"],
        "source_divergent_node_0_id": source_divergent[0]
        if len(source_divergent) > 0
        else -1,
        "source_divergent_node_1_id": source_divergent[1]
        if len(source_divergent) > 1
        else -1,
        "target_divergent_node_0_id": target_divergent[0]
        if len(target_divergent) > 0
        else -1,
        "target_divergent_node_1_id": target_divergent[1]
        if len(target_divergent) > 1
        else -1,
        "target_divergent_node_2_id": target_divergent[2]
        if len(target_divergent) > 2
        else -1,
        "target_divergent_node_3_id": target_divergent[3]
        if len(target_divergent) > 3
        else -1,
        "target_divergent_node_4_id": target_divergent[4]
        if len(target_divergent) > 4
        else -1,
    }


def anchor_rows(rank104_strong_trace: Sequence[int], target1_trace: Sequence[int]) -> list[dict[str, int]]:
    baseline_divergent = set(common_prefix_suffix(BASELINE_TRACE, TARGET1_TRACE)[2])
    target1_divergent = set(common_prefix_suffix(BASELINE_TRACE, TARGET1_TRACE)[3])
    rank104_divergent = set(common_prefix_suffix(BASELINE_TRACE, RANK104_TRACE)[3])
    strong_counts = Counter(rank104_strong_trace)
    target1_counts = Counter(target1_trace)
    rows = []
    for node_id in ANCHOR_NODE_IDS:
        if node_id == 31:
            role_code = 0
        elif node_id == 29:
            role_code = 1
        elif node_id in (28, 34):
            role_code = 2
        elif node_id == 45:
            role_code = 3
        else:
            role_code = 4
        rows.append(
            {
                "anchor_node_id": node_id,
                "baseline_divergent_flag": int(node_id in baseline_divergent),
                "target1_divergent_flag": int(node_id in target1_divergent),
                "rank104_original_divergent_flag": int(node_id in rank104_divergent),
                "rank104_strong_occurrence_count": int(strong_counts[node_id]),
                "target1_occurrence_count": int(target1_counts[node_id]),
                "node_role_code": role_code,
            }
        )
    return rows


def build_payloads() -> dict[str, Any]:
    gap_report = load_json(STRONGIFICATION_GAP_REPORT)
    gap_json = load_json(STRONGIFICATION_GAP_JSON)
    gap_certificate = load_json(STRONGIFICATION_GAP_CERTIFICATE)
    trace_report = load_json(TRACE_QUOTIENT_REPORT)
    trace_certificate = load_json(TRACE_QUOTIENT_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    gap_tables = np.load(STRONGIFICATION_GAP_TABLES, allow_pickle=False)
    trace_tables = np.load(TRACE_QUOTIENT_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    gap_witness_table = np.asarray(
        gap_tables["strongification_witness_table"],
        dtype=np.int64,
    )
    trace_class_table = np.asarray(trace_tables["trace_class_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    adjacency, _carriers = build_carrier_adjacency(
        read_int_csv(CELL_COMPLEX_EDGES),
        atom_to_symbol,
    )
    assoc_by_word = associativity_lookup(read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV))
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }
    rewrite_graph = rewrite_adjacency(rewrite_edges)

    gap_witnesses = witness_rows(STRONGIFICATION_GAP_WITNESSES)
    rank104_best_witness = next(
        row
        for row in gap_witnesses
        if row["prefix_class_id"] == 1 and row["best_score_flag"] == 1
    )
    rank104_word = tuple(
        rank104_best_witness[f"strong_word_symbol_{index}_id"]
        for index in range(rank104_best_witness["strong_word_length"])
    )

    branch_rows = [
        branch_profile(
            TARGET1_BRANCH_ID,
            0,
            1,
            tuple(TARGET1_CLOSED_REPAIR_WORD),
            adjacency,
            assoc_by_word,
            rewrite_edge_by_pair,
            rewrite_graph,
        ),
        branch_profile(
            RANK104_STRONG_BRANCH_ID,
            1,
            0,
            rank104_word,
            adjacency,
            assoc_by_word,
            rewrite_edge_by_pair,
            rewrite_graph,
        ),
    ]
    comparison_rows = [comparison_row(branch_rows[0], branch_rows[1])]
    anchor_node_rows = anchor_rows(row_trace(branch_rows[1]), row_trace(branch_rows[0]))

    branch_table = table_from_rows(BRANCH_PROFILE_COLUMNS, branch_rows)
    comparison_table = table_from_rows(COMPARISON_COLUMNS, comparison_rows)
    anchor_table = table_from_rows(ANCHOR_NODE_COLUMNS, anchor_node_rows)
    observable_values = {
        "branch_count": len(branch_rows),
        "target1_trace_overhead": branch_rows[0]["trace_detour_overhead"],
        "rank104_strong_trace_overhead": branch_rows[1]["trace_detour_overhead"],
        "rank104_overhead_gap": comparison_rows[0]["target_overhead_gap"],
        "target1_variation": branch_rows[0]["trace_signature_total_variation"],
        "rank104_strong_variation": branch_rows[1][
            "trace_signature_total_variation"
        ],
        "rank104_variation_advantage": comparison_rows[0][
            "target_variation_advantage"
        ],
        "same_valley_depth_flag": comparison_rows[0]["same_valley_depth_flag"],
        "same_gromov_delta_flag": comparison_rows[0]["same_gromov_delta_flag"],
        "target1_closed_path_count": branch_rows[0]["closed_path_count"],
        "rank104_closed_path_count": branch_rows[1]["closed_path_count"],
        "rank104_closed_path_advantage": comparison_rows[0][
            "target_closed_path_advantage"
        ],
        "target1_skipped_node_count": branch_rows[0]["geodesic_skipped_node_count"],
        "rank104_skipped_node_count": branch_rows[1]["geodesic_skipped_node_count"],
        "rank104_hybrid_anchor_node_count": sum(
            1 for row in anchor_node_rows if row["rank104_strong_occurrence_count"] > 0
        ),
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
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "strongification_gap_report_certified": gap_report.get("status")
        == STRONGIFICATION_GAP_STATUS,
        "strongification_gap_certificate_certified": gap_certificate.get("status")
        == STRONGIFICATION_GAP_STATUS,
        "strongification_gap_schema_available": gap_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap@1",
        "trace_quotient_report_certified": trace_report.get("status")
        == TRACE_QUOTIENT_STATUS,
        "trace_quotient_certificate_certified": trace_certificate.get("status")
        == TRACE_QUOTIENT_STATUS,
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
        "gap_witness_table_shape_is_24": tuple(gap_witness_table.shape)[0] == 24,
        "trace_class_table_shape_is_7_by_codebook": tuple(trace_class_table.shape)
        == (7, len(TRACE_CLASS_COLUMNS)),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "branch_table_shape_matches_codebook": tuple(branch_table.shape)
        == (2, len(BRANCH_PROFILE_COLUMNS)),
        "comparison_table_shape_matches_codebook": tuple(comparison_table.shape)
        == (1, len(COMPARISON_COLUMNS)),
        "anchor_table_shape_matches_codebook": tuple(anchor_table.shape)
        == (len(ANCHOR_NODE_IDS), len(ANCHOR_NODE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "rank104_word_matches_gap_best_witness": rank104_word
        == RANK104_BEST_STRONG_WORD,
        "target1_trace_matches_quotient_branch": row_trace(branch_rows[0])
        == TARGET1_TRACE,
        "rank104_strong_trace_matches_expected": row_trace(branch_rows[1])
        == (48, 42, 27, 31, 34, 29, 28, 34, 44),
        "both_branches_are_strong_and_closed": all(
            row["strong_first_hit_flag"] == 1 and row["closed_path_count"] > 0
            for row in branch_rows
        ),
        "shortcut_savings_equal_trace_overheads": all(
            row["shortcut_saved_edge_count"] == row["trace_detour_overhead"]
            for row in branch_rows
        ),
        "rank104_pays_three_extra_edges": comparison_rows[0][
            "target_overhead_gap"
        ]
        == 3
        and comparison_rows[0]["target_extra_trace_edge_count"] == 3,
        "rank104_gains_twenty_six_variation": comparison_rows[0][
            "target_variation_advantage"
        ]
        == 26,
        "rank104_preserves_valley_and_delta": comparison_rows[0][
            "same_valley_depth_flag"
        ]
        == 1
        and comparison_rows[0]["same_gromov_delta_flag"] == 1,
        "rank104_has_five_more_closed_paths": comparison_rows[0][
            "target_closed_path_advantage"
        ]
        == 5,
        "branch_transition_edit_shape_matches": comparison_rows[0][
            "common_prefix_node_count"
        ]
        == 3
        and comparison_rows[0]["common_suffix_node_count"] == 1
        and comparison_rows[0]["trace_node_edit_distance"] == 4
        and comparison_rows[0]["trace_edge_edit_distance"] == 6,
        "rank104_strong_is_hybrid_anchor_trace": {
            row["anchor_node_id"]: row["rank104_strong_occurrence_count"]
            for row in anchor_node_rows
        }
        == {28: 1, 29: 1, 31: 1, 34: 2, 45: 0, 50: 0},
    }

    witness = {
        "target1_branch": {
            "word": list(TARGET1_CLOSED_REPAIR_WORD),
            "trace": list(row_trace(branch_rows[0])),
            "score": [
                branch_rows[0]["trace_detour_overhead"],
                branch_rows[0]["signature_valley_depth"],
                branch_rows[0]["metric_gromov_delta_twice"],
                branch_rows[0]["trace_signature_total_variation"],
            ],
            "closed_path_count": branch_rows[0]["closed_path_count"],
            "shortcut_skipped_nodes": [
                branch_rows[0][column]
                for column in SKIPPED_NODE_COLUMNS
                if branch_rows[0][column] >= 0
            ],
        },
        "rank104_strongification_branch": {
            "word": list(rank104_word),
            "trace": list(row_trace(branch_rows[1])),
            "score": [
                branch_rows[1]["trace_detour_overhead"],
                branch_rows[1]["signature_valley_depth"],
                branch_rows[1]["metric_gromov_delta_twice"],
                branch_rows[1]["trace_signature_total_variation"],
            ],
            "closed_path_count": branch_rows[1]["closed_path_count"],
            "shortcut_skipped_nodes": [
                branch_rows[1][column]
                for column in SKIPPED_NODE_COLUMNS
                if branch_rows[1][column] >= 0
            ],
        },
        "comparison": comparison_rows[0],
        "anchor_node_occurrences": {
            str(row["anchor_node_id"]): row["rank104_strong_occurrence_count"]
            for row in anchor_node_rows
        },
        "branch_table_sha256": sha_array(branch_table),
        "comparison_table_sha256": sha_array(comparison_table),
        "anchor_table_sha256": sha_array(anchor_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    geometry = {
        "schema": "c985.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry@1",
        "object": "d20",
        "comparison_rule": {
            "source_branch": "original certified target1 closed branch x2,x1,x5,x2,x5,x4,x3",
            "target_branch": "rank-104 best cost-three strongification word from the pre-node44 gap layer",
            "shortcut_rule": "compare each trace against the ambient rewrite geodesic shortcut 48->42->44, using 42->44 to measure skipped detour edges",
            "hybrid_readout": "count baseline, target1, and original rank104 divergent trace nodes inside the rank104 strongification trace",
        },
        "summary": {
            "target1_score": witness["target1_branch"]["score"],
            "rank104_strongification_score": witness[
                "rank104_strongification_branch"
            ]["score"],
            "rank104_overhead_gap": comparison_rows[0]["target_overhead_gap"],
            "rank104_variation_advantage": comparison_rows[0][
                "target_variation_advantage"
            ],
            "rank104_hybrid_anchor_occurrences": witness[
                "anchor_node_occurrences"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_RANK104_STRONGIFICATION_BRANCH_GEOMETRY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the rank-104 best strongification word traces 48->42->27->31->34->29->28->34->44",
            "relative to target1, rank104 strongification pays three extra trace edges but lowers signature variation by 26",
            "both branches have valley depth 37 and Gromov delta_twice 1",
            "the ambient 42->44 shortcut skips three nodes in target1 and six nodes in rank104 strongification",
            "the rank104 strongification branch is hybrid: it keeps rank104 node31, imports target1 node29, loops through baseline nodes28 and34, and drops target1 node45 and original rank104 node50",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The rank-104 best strongification word is a genuine new branch "
            "rather than a disguised target1 replay. It pays three additional "
            "trace edges compared with target1, but keeps the same valley depth "
            "and delta while lowering signature variation by 26 and increasing "
            "first-return closed carrier witnesses from 3 to 8. Its detour is "
            "hybrid: rank104 node31, target1 node29, and baseline nodes28/34 "
            "all occur before the final aperture."
        ),
        "stage_protocol": {
            "draft": "read the rank-104 best strongification word from the pre-node44 gap layer",
            "witness": "materialize target1 and rank104 branch traces, scores, shortcuts, and hybrid anchor-node occurrences",
            "coherence": "compare both traces against the same ambient 48->42->44 geodesic shortcut",
            "closure": "certify the overhead/variation tradeoff and hybrid branch-node composition",
            "emit": "emit branch-geometry JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "strongification_gap_report": input_entry(
                STRONGIFICATION_GAP_REPORT,
                {
                    "status": gap_report.get("status"),
                    "certificate_sha256": gap_report.get("certificate_sha256"),
                },
            ),
            "strongification_gap_json": input_entry(STRONGIFICATION_GAP_JSON),
            "strongification_gap_witnesses": input_entry(
                STRONGIFICATION_GAP_WITNESSES
            ),
            "strongification_gap_tables": input_entry(STRONGIFICATION_GAP_TABLES),
            "strongification_gap_certificate": input_entry(
                STRONGIFICATION_GAP_CERTIFICATE
            ),
            "trace_quotient_report": input_entry(
                TRACE_QUOTIENT_REPORT,
                {
                    "status": trace_report.get("status"),
                    "certificate_sha256": trace_report.get("certificate_sha256"),
                },
            ),
            "trace_quotient_classes": input_entry(TRACE_QUOTIENT_CLASSES),
            "trace_quotient_tables": input_entry(TRACE_QUOTIENT_TABLES),
            "trace_quotient_certificate": input_entry(TRACE_QUOTIENT_CERTIFICATE),
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
            "signature_boundary_spine_aperture_rank104_strongification_branch_geometry": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry.json"
            ),
            "aperture_rank104_strongification_branch_profiles_csv": relpath(
                OUT_DIR / "aperture_rank104_strongification_branch_profiles.csv"
            ),
            "aperture_rank104_strongification_branch_comparison_csv": relpath(
                OUT_DIR / "aperture_rank104_strongification_branch_comparison.csv"
            ),
            "aperture_rank104_strongification_anchor_nodes_csv": relpath(
                OUT_DIR / "aperture_rank104_strongification_anchor_nodes.csv"
            ),
            "aperture_rank104_strongification_observables_csv": relpath(
                OUT_DIR / "aperture_rank104_strongification_observables.csv"
            ),
            "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_tables.npz"
            ),
            "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the trace and score of the rank-104 best strongification branch",
                "the branch comparison against the original target1 branch",
                "the shared ambient 42->44 shortcut savings for each branch",
                "the rank104 overhead/variation tradeoff",
                "the hybrid anchor-node composition of the rank104 strongification trace",
            ],
            "does_not_certify_because_not_required": [
                "all cost-three strongification witnesses beyond the already-certified gap table",
                "bounded first-return ranking for the length-ten strongification word",
                "deletions or moving the final promoted x5 suffix",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Rank all 24 cost-three strongification witnesses by this same "
            "branch-geometry score to see whether rank-104's best word is a "
            "global Pareto point or merely the best representative of its prefix class."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified pre-node44 strongification gap, overhead3 trace quotient, carrier cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "recompute target1 and rank104 strongification traces and carrier closure counts",
            "compare both traces against the same ambient 42->44 shortcut",
            "materialize branch comparison and hybrid anchor-node occurrence tables",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_rank104_strongification_branch_geometry": geometry,
        "aperture_rank104_strongification_branch_profiles_csv": csv_text(
            BRANCH_PROFILE_COLUMNS,
            branch_rows,
        ),
        "aperture_rank104_strongification_branch_comparison_csv": csv_text(
            COMPARISON_COLUMNS,
            comparison_rows,
        ),
        "aperture_rank104_strongification_anchor_nodes_csv": csv_text(
            ANCHOR_NODE_COLUMNS,
            anchor_node_rows,
        ),
        "aperture_rank104_strongification_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "branch_profile_table": branch_table,
        "comparison_table": comparison_table,
        "anchor_node_table": anchor_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate": certificate,
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
        OUT_DIR
        / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry.json",
        payloads[
            "signature_boundary_spine_aperture_rank104_strongification_branch_geometry"
        ],
    )
    (OUT_DIR / "aperture_rank104_strongification_branch_profiles.csv").write_text(
        payloads["aperture_rank104_strongification_branch_profiles_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_rank104_strongification_branch_comparison.csv").write_text(
        payloads["aperture_rank104_strongification_branch_comparison_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_rank104_strongification_anchor_nodes.csv").write_text(
        payloads["aperture_rank104_strongification_anchor_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_rank104_strongification_observables.csv").write_text(
        payloads["aperture_rank104_strongification_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_tables.npz",
        branch_profile_table=payloads["branch_profile_table"],
        comparison_table=payloads["comparison_table"],
        anchor_node_table=payloads["anchor_node_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate"
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
                "target1_score": witness["target1_branch"]["score"],
                "rank104_strongification_score": witness[
                    "rank104_strongification_branch"
                ]["score"],
                "comparison": witness["comparison"],
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
