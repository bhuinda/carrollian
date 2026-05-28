from __future__ import annotations

import json
from collections import Counter, deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        CANDIDATE_MOVE_COLUMNS as FLOW_CANDIDATE_MOVE_COLUMNS,
        OUT_DIR as FLOW_WINDOW_DIR,
        STATUS as FLOW_WINDOW_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        OUT_DIR as REPAIRED_AUTOMATON_DIR,
        STATE_COLUMNS as REPAIRED_STATE_COLUMNS,
        STATUS as REPAIRED_AUTOMATON_STATUS,
        TRANSITION_COLUMNS as REPAIRED_TRANSITION_COLUMNS,
        build_edges,
        connected_components,
        edit_descriptor,
        scaled_float,
        spectral_geometry,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        LEFT_REPAIR_BOUNDARY_WORD,
        MAX_SIDE_EDIT_RADIUS,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR as SKIP_WINDOW_DIR,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as SKIP_WINDOW_STATUS,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        derived_spans,
        grammar_rows,
        input_entry,
        load_json,
        one_edit_neighbors,
        padded,
        radius_from,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        PREFIX_SYMBOLS,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        CANDIDATE_MOVE_COLUMNS as FLOW_CANDIDATE_MOVE_COLUMNS,
        OUT_DIR as FLOW_WINDOW_DIR,
        STATUS as FLOW_WINDOW_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        OUT_DIR as REPAIRED_AUTOMATON_DIR,
        STATE_COLUMNS as REPAIRED_STATE_COLUMNS,
        STATUS as REPAIRED_AUTOMATON_STATUS,
        TRANSITION_COLUMNS as REPAIRED_TRANSITION_COLUMNS,
        build_edges,
        connected_components,
        edit_descriptor,
        scaled_float,
        spectral_geometry,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        LEFT_REPAIR_BOUNDARY_WORD,
        MAX_SIDE_EDIT_RADIUS,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR as SKIP_WINDOW_DIR,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as SKIP_WINDOW_STATUS,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        derived_spans,
        grammar_rows,
        input_entry,
        load_json,
        one_edit_neighbors,
        padded,
        radius_from,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        PREFIX_SYMBOLS,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_PROMOTED_WINDOW_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

PROMOTED_BLOCK = (5, 5, 2, 5)
SCALE = 10**12

SKIP_WINDOW_REPORT = SKIP_WINDOW_DIR / "report.json"
SKIP_WINDOW_TABLES = (
    SKIP_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_tables.npz"
)
REPAIRED_AUTOMATON_REPORT = REPAIRED_AUTOMATON_DIR / "report.json"
REPAIRED_AUTOMATON_TABLES = (
    REPAIRED_AUTOMATON_DIR
    / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_tables.npz"
)
FLOW_WINDOW_REPORT = FLOW_WINDOW_DIR / "report.json"
FLOW_WINDOW_TABLES = (
    FLOW_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_flow_window_lift_tables.npz"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window.py"
)

CELL_COLUMNS = [
    "grammar_cell_id",
    "component_id",
    "word_length",
    *WORD_COLUMNS,
    "left_edit_radius",
    "right_edit_radius",
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "native_repair_flag",
    "skip_derived_repair_flag",
    "promoted_window_repair_flag",
    "derived_repair_flag",
    "derived_only_flag",
    "skip_derived_only_flag",
    "promoted_only_flag",
    "first_skip_span_rank",
    "first_skip_block_symbol_0_id",
    "first_skip_block_symbol_1_id",
    "first_skip_block_symbol_2_id",
    "first_skip_block_symbol_3_id",
    "first_promoted_span_rank",
    "first_promoted_block_symbol_0_id",
    "first_promoted_block_symbol_1_id",
    "first_promoted_block_symbol_2_id",
    "first_promoted_block_symbol_3_id",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "all_four_lift_flag",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
]

COMPONENT_COLUMNS = [
    "component_id",
    "cell_count",
    "edge_count",
    "native_cell_count",
    "skip_derived_cell_count",
    "promoted_window_cell_count",
    "derived_only_cell_count",
    "skip_derived_only_cell_count",
    "promoted_only_cell_count",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
    "merged_boundary_flag",
    "min_variation",
    "max_closed_path_count",
]

PATH_COLUMNS = [
    "path_step",
    "grammar_cell_id",
    "word_length",
    *WORD_COLUMNS,
    "native_repair_flag",
    "skip_derived_repair_flag",
    "promoted_window_repair_flag",
    "derived_repair_flag",
    "derived_only_flag",
    "promoted_only_flag",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
]

STATE_COLUMNS = [
    "automaton_state_id",
    "grammar_cell_id",
    "promoted_recurrent_class_id",
    "native_recurrent_class_id",
    "word_length",
    *WORD_COLUMNS,
    "degree",
    "native_neighbor_count",
    "derived_neighbor_count",
    "promoted_neighbor_count",
    "native_transition_degree",
    "derived_transition_degree",
    "promoted_transition_degree",
    "native_repair_flag",
    "skip_derived_repair_flag",
    "promoted_window_repair_flag",
    "derived_repair_flag",
    "derived_only_flag",
    "skip_derived_only_flag",
    "promoted_only_flag",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
    "merged_recurrent_class_flag",
    "spectral_side_code",
]

EDGE_COLUMNS = [
    "automaton_edge_id",
    "source_state_id",
    "target_state_id",
    "source_grammar_cell_id",
    "target_grammar_cell_id",
    "edit_kind_code",
    "edit_position",
    "source_symbol_id",
    "target_symbol_id",
    "native_transition_flag",
    "derived_transition_flag",
    "promoted_transition_flag",
    "promoted_only_transition_flag",
    "old_repaired_edge_flag",
    "old_spectral_cut_edge_flag",
    "new_spectral_cut_edge_flag",
]

RECURRENT_CLASS_COLUMNS = [
    "promoted_recurrent_class_id",
    "state_count",
    "undirected_edge_count",
    "native_state_count",
    "skip_derived_state_count",
    "promoted_window_state_count",
    "derived_only_state_count",
    "skip_derived_only_state_count",
    "promoted_only_state_count",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
    "merged_boundary_flag",
    "spectral_certified_flag",
]

NATIVE_CLASS_COLUMNS = [
    "native_recurrent_class_id",
    "state_count",
    "undirected_edge_count",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
]

SPECTRAL_CUT_COLUMNS = [
    "spectral_cut_id",
    "promoted_recurrent_class_id",
    "state_count",
    "undirected_edge_count",
    "lambda_2_x1e12",
    "lambda_3_x1e12",
    "spectral_gap_x1e12",
    "cut_edge_count",
    "derived_cut_edge_count",
    "promoted_cut_edge_count",
    "promoted_only_cut_edge_count",
    "positive_state_count",
    "negative_state_count",
    "positive_volume",
    "negative_volume",
    "cut_conductance_x1e12",
    "left_side_code",
    "gate_side_code",
    "right_side_code",
    "old_cut_edge_count",
    "old_cut_edge_survival_count",
    "old_cut_edge_still_cut_count",
    "old_cut_edge_same_side_count",
]

POINCARE_COLUMNS = [
    "poincare_point_id",
    "automaton_state_id",
    "promoted_recurrent_class_id",
    "spectral_side_code",
    "poincare_x_x1e12",
    "poincare_y_x1e12",
    "poincare_radius_x1e12",
    "fiedler_value_x1e12",
    "third_mode_value_x1e12",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
    "promoted_window_repair_flag",
    "promoted_only_flag",
]

PROMOTED_OBSERVABLE_CODES = {
    "boundary_union_word_count": 0,
    "trace_failure_word_count": 1,
    "bad_metric_word_count": 2,
    "metric_ok_word_count": 3,
    "closed_positive_metric_word_count": 4,
    "state_count": 5,
    "undirected_edge_count": 6,
    "component_count": 7,
    "native_state_count": 8,
    "skip_derived_state_count": 9,
    "promoted_window_state_count": 10,
    "derived_only_state_count": 11,
    "skip_derived_only_state_count": 12,
    "promoted_only_state_count": 13,
    "new_state_count_vs_skip": 14,
    "new_edge_count_vs_repaired": 15,
    "merged_recurrent_class_size": 16,
    "merged_native_state_count": 17,
    "merged_skip_derived_only_state_count": 18,
    "merged_promoted_only_state_count": 19,
    "left_to_right_path_exists": 20,
    "shortest_path_length": 21,
    "old_cut_edge_count": 22,
    "old_cut_edge_survival_count": 23,
    "old_cut_edge_still_cut_count": 24,
    "spectral_cut_edge_count": 25,
    "spectral_cut_derived_edge_count": 26,
    "spectral_cut_promoted_edge_count": 27,
    "spectral_cut_promoted_only_edge_count": 28,
    "merged_lambda_2": 29,
    "merged_lambda_3": 30,
    "merged_cut_conductance": 31,
    "selected_block_code": 32,
    "flow_selected_candidate_word_count": 33,
}

FLOAT_OBSERVABLES = {
    "merged_lambda_2",
    "merged_lambda_3",
    "merged_cut_conductance",
}


def block_code(block: tuple[int, int, int, int]) -> int:
    return int(block[0] * 1_000 + block[1] * 100 + block[2] * 10 + block[3])


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def word_from_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)


def edge_word_key(
    source: tuple[int, ...],
    target: tuple[int, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    left, right = sorted((source, target))
    return left, right


def promoted_spans(word: tuple[int, ...]) -> list[tuple[int, tuple[int, int, int, int]]]:
    sequence = tuple(PREFIX_SYMBOLS) + word + word[:2]
    spans = []
    for rank in range(len(sequence) - 3):
        block = tuple(int(value) for value in sequence[rank : rank + 4])
        if block == PROMOTED_BLOCK:
            spans.append((rank, block))
    return spans


def load_flow_selection() -> dict[str, int | tuple[int, int, int, int]]:
    tables = np.load(FLOW_WINDOW_TABLES, allow_pickle=False)
    move_rows = table_rows(
        np.asarray(tables["candidate_move_table"], dtype=np.int64),
        FLOW_CANDIDATE_MOVE_COLUMNS,
    )
    selected = [row for row in move_rows if row["selected_move_flag"] == 1]
    if len(selected) != 1:
        raise AssertionError("flow-window selected move count mismatch")
    row = selected[0]
    block = (
        row["block_symbol_0_id"],
        row["block_symbol_1_id"],
        row["block_symbol_2_id"],
        row["block_symbol_3_id"],
    )
    return {
        "block": block,
        "candidate_word_count": row["candidate_word_count"],
        "same_side_edge_count": row["same_side_edge_count"],
        "negative_side_edge_count": row["negative_side_edge_count"],
        "new_cut_flux_x1e12": row["new_cut_flux_x1e12"],
        "new_weighted_conductance_x1e12": row[
            "new_weighted_conductance_x1e12"
        ],
    }


def load_old_geometry() -> dict[str, Any]:
    tables = np.load(REPAIRED_AUTOMATON_TABLES, allow_pickle=False)
    state_rows = table_rows(
        np.asarray(tables["state_table"], dtype=np.int64),
        REPAIRED_STATE_COLUMNS,
    )
    transition_rows = table_rows(
        np.asarray(tables["transition_table"], dtype=np.int64),
        REPAIRED_TRANSITION_COLUMNS,
    )
    word_by_state = {
        row["automaton_state_id"]: word_from_row(row) for row in state_rows
    }
    old_edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    old_cut_edges: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    seen_undirected_ids: set[int] = set()
    for row in sorted(transition_rows, key=lambda item: item["transition_id"]):
        edge_id = row["undirected_edge_id"]
        if edge_id in seen_undirected_ids:
            continue
        seen_undirected_ids.add(edge_id)
        source_word = word_by_state[row["source_state_id"]]
        target_word = word_by_state[row["target_state_id"]]
        key = edge_word_key(source_word, target_word)
        old_edges.add(key)
        if row["spectral_cut_edge_flag"] == 1:
            old_cut_edges.add(key)
    return {
        "state_count": len(state_rows),
        "edge_count": len(old_edges),
        "old_edges": old_edges,
        "old_cut_edges": old_cut_edges,
    }


def evaluate_language(
    repair_rows_by_block: dict[
        tuple[int, int, int, int],
        list[dict[str, int]],
    ],
) -> dict[str, Any]:
    left_radius = radius_from(LEFT_REPAIR_BOUNDARY_WORD, MAX_SIDE_EDIT_RADIUS)
    right_radius = radius_from(RIGHT_REPAIR_BOUNDARY_WORD, MAX_SIDE_EDIT_RADIUS)
    candidate_words = sorted(set(left_radius) | set(right_radius))
    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()
    stats: Counter[str] = Counter()
    rows_by_word: dict[tuple[int, ...], dict[str, Any]] = {}
    stats["boundary_union_word_count"] = len(candidate_words)

    for word in candidate_words:
        try:
            _raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
        except Exception:
            stats["trace_failure_word_count"] += 1
            continue
        trace = tuple(int(value) for value in trace_nodes)
        variation = int(metrics["trace_signature_total_variation"])
        delta_twice = int(metrics["metric_gromov_delta_twice"])
        if (
            delta_twice != TARGET_DELTA_TWICE
            or variation > TARGET_VARIATION_INCLUSIVE_BOUND
        ):
            stats["bad_metric_word_count"] += 1
            continue
        stats["metric_ok_word_count"] += 1
        native_repair = int(
            contains_undirected_edge(trace, 31, 28)
            or contains_undirected_edge(trace, 50, 34)
        )
        skip_spans = derived_spans(word, repair_rows_by_block)
        promoted = promoted_spans(word)
        skip_repair = int(bool(skip_spans))
        promoted_repair = int(bool(promoted))
        derived_repair = int(skip_repair or promoted_repair)
        if native_repair:
            stats["native_repair_metric_count"] += 1
        if skip_repair:
            stats["skip_derived_repair_metric_count"] += 1
        if promoted_repair:
            stats["promoted_window_repair_metric_count"] += 1
        profile = closure_profile(word, carrier_adjacency)
        if profile["first_return_closed_path_count"] <= 0:
            continue
        stats["closed_positive_metric_word_count"] += 1
        if native_repair:
            stats["native_good_cell_count"] += 1
        if skip_repair:
            stats["skip_derived_closed_cell_count"] += 1
        if promoted_repair:
            stats["promoted_window_closed_cell_count"] += 1
        if not (native_repair or derived_repair):
            continue
        stats["promoted_grammar_good_cell_count"] += 1
        if derived_repair and not native_repair:
            stats["derived_only_closed_cell_count"] += 1
        if skip_repair and not native_repair:
            stats["skip_derived_only_closed_cell_count"] += 1
        if promoted_repair and not (native_repair or skip_repair):
            stats["promoted_only_closed_cell_count"] += 1

        first_skip_rank, first_skip_block, _first_rows = (
            skip_spans[0] if skip_spans else (-1, (-1, -1, -1, -1), [])
        )
        first_promoted_rank, first_promoted_block = (
            promoted[0] if promoted else (-1, (-1, -1, -1, -1))
        )
        rows_by_word[word] = {
            "word": word,
            "left_edit_radius": left_radius.get(word, 99),
            "right_edit_radius": right_radius.get(word, 99),
            "trace": trace,
            "delta_twice": delta_twice,
            "variation": variation,
            "native_repair": native_repair,
            "skip_derived_repair": skip_repair,
            "promoted_window_repair": promoted_repair,
            "derived_repair": derived_repair,
            "derived_only": int(derived_repair and not native_repair),
            "skip_derived_only": int(skip_repair and not native_repair),
            "promoted_only": int(promoted_repair and not (native_repair or skip_repair)),
            "first_skip_span_rank": first_skip_rank,
            "first_skip_block": first_skip_block,
            "first_promoted_span_rank": first_promoted_rank,
            "first_promoted_block": first_promoted_block,
            "profile": profile,
        }

    return {
        "stats": dict(stats),
        "rows_by_word": rows_by_word,
    }


def build_graph(rows_by_word: dict[tuple[int, ...], dict[str, Any]]) -> dict[str, Any]:
    words = sorted(rows_by_word)
    cell_id_by_word = {word: index for index, word in enumerate(words)}
    edge_set, adjacency = build_edges(words, cell_id_by_word)

    components: list[set[int]] = []
    seen: set[int] = set()
    for cell_id in sorted(adjacency):
        if cell_id in seen:
            continue
        stack = [cell_id]
        seen.add(cell_id)
        component: set[int] = set()
        while stack:
            current = stack.pop()
            component.add(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(component)

    def component_sort_key(component: set[int]) -> tuple[int, int, int]:
        component_words = {words[cell_id] for cell_id in component}
        merged = int(
            LEFT_REPAIR_BOUNDARY_WORD in component_words
            and RIGHT_REPAIR_BOUNDARY_WORD in component_words
        )
        gate = int(NO_REPAIR_GATE_WORD in component_words)
        return (-merged, -gate, -len(component))

    components = sorted(components, key=component_sort_key)
    component_id_by_cell: dict[int, int] = {}
    for component_id, component in enumerate(components):
        for cell_id in component:
            component_id_by_cell[cell_id] = component_id

    cell_rows = []
    for word in words:
        row = rows_by_word[word]
        cell_id = cell_id_by_word[word]
        profile = row["profile"]
        cell_rows.append(
            {
                "grammar_cell_id": cell_id,
                "component_id": component_id_by_cell[cell_id],
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        WORD_COLUMNS,
                        padded(word, MAX_WORD_LENGTH),
                    )
                },
                "left_edit_radius": row["left_edit_radius"],
                "right_edit_radius": row["right_edit_radius"],
                "trace_node_count": len(row["trace"]),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(row["trace"], MAX_TRACE_NODES),
                    )
                },
                "metric_gromov_delta_twice": row["delta_twice"],
                "trace_signature_total_variation": row["variation"],
                "native_repair_flag": row["native_repair"],
                "skip_derived_repair_flag": row["skip_derived_repair"],
                "promoted_window_repair_flag": row["promoted_window_repair"],
                "derived_repair_flag": row["derived_repair"],
                "derived_only_flag": row["derived_only"],
                "skip_derived_only_flag": row["skip_derived_only"],
                "promoted_only_flag": row["promoted_only"],
                "first_skip_span_rank": row["first_skip_span_rank"],
                "first_skip_block_symbol_0_id": row["first_skip_block"][0],
                "first_skip_block_symbol_1_id": row["first_skip_block"][1],
                "first_skip_block_symbol_2_id": row["first_skip_block"][2],
                "first_skip_block_symbol_3_id": row["first_skip_block"][3],
                "first_promoted_span_rank": row["first_promoted_span_rank"],
                "first_promoted_block_symbol_0_id": row["first_promoted_block"][0],
                "first_promoted_block_symbol_1_id": row["first_promoted_block"][1],
                "first_promoted_block_symbol_2_id": row["first_promoted_block"][2],
                "first_promoted_block_symbol_3_id": row["first_promoted_block"][3],
                "first_return_closed_path_count": profile[
                    "first_return_closed_path_count"
                ],
                "normalized_tail_template_count": profile[
                    "normalized_tail_template_count"
                ],
                "template_lift_count_min": profile["template_lift_count_min"],
                "template_lift_count_max": profile["template_lift_count_max"],
                "all_four_lift_flag": profile["all_four_lift_flag"],
                "tail_entry_9_path_count": profile["tail_entry_9_path_count"],
                "tail_entry_10_path_count": profile["tail_entry_10_path_count"],
                "tail_entry_11_path_count": profile["tail_entry_11_path_count"],
                "tail_entry_13_path_count": profile["tail_entry_13_path_count"],
                "left_boundary_flag": int(word == LEFT_REPAIR_BOUNDARY_WORD),
                "right_boundary_flag": int(word == RIGHT_REPAIR_BOUNDARY_WORD),
                "gate_word_flag": int(word == NO_REPAIR_GATE_WORD),
            }
        )

    cell_by_id = {row["grammar_cell_id"]: row for row in cell_rows}
    component_rows = []
    for component_id, component in enumerate(components):
        cells = [cell_by_id[cell_id] for cell_id in sorted(component)]
        component_words = {words[cell_id] for cell_id in component}
        component_edge_count = sum(
            int(target in component)
            for source in component
            for target in adjacency[source]
            if source < target
        )
        component_rows.append(
            {
                "component_id": component_id,
                "cell_count": len(cells),
                "edge_count": component_edge_count,
                "native_cell_count": sum(row["native_repair_flag"] for row in cells),
                "skip_derived_cell_count": sum(
                    row["skip_derived_repair_flag"] for row in cells
                ),
                "promoted_window_cell_count": sum(
                    row["promoted_window_repair_flag"] for row in cells
                ),
                "derived_only_cell_count": sum(row["derived_only_flag"] for row in cells),
                "skip_derived_only_cell_count": sum(
                    row["skip_derived_only_flag"] for row in cells
                ),
                "promoted_only_cell_count": sum(
                    row["promoted_only_flag"] for row in cells
                ),
                "left_boundary_flag": int(LEFT_REPAIR_BOUNDARY_WORD in component_words),
                "right_boundary_flag": int(RIGHT_REPAIR_BOUNDARY_WORD in component_words),
                "gate_word_flag": int(NO_REPAIR_GATE_WORD in component_words),
                "merged_boundary_flag": int(
                    LEFT_REPAIR_BOUNDARY_WORD in component_words
                    and RIGHT_REPAIR_BOUNDARY_WORD in component_words
                ),
                "min_variation": min(row["trace_signature_total_variation"] for row in cells),
                "max_closed_path_count": max(
                    row["first_return_closed_path_count"] for row in cells
                ),
            }
        )

    left_id = cell_id_by_word[LEFT_REPAIR_BOUNDARY_WORD]
    right_id = cell_id_by_word[RIGHT_REPAIR_BOUNDARY_WORD]
    parent: dict[int, int | None] = {left_id: None}
    distance: dict[int, int] = {left_id: 0}
    queue: deque[int] = deque([left_id])
    while queue:
        current = queue.popleft()
        if current == right_id:
            break
        for neighbor in sorted(adjacency[current]):
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                parent[neighbor] = current
                queue.append(neighbor)
    path_words = []
    if right_id in distance:
        current: int | None = right_id
        while current is not None:
            path_words.append(words[current])
            current = parent[current]
        path_words.reverse()
    path_rows = []
    for step, word in enumerate(path_words):
        row = rows_by_word[word]
        profile = row["profile"]
        path_rows.append(
            {
                "path_step": step,
                "grammar_cell_id": cell_id_by_word[word],
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        WORD_COLUMNS,
                        padded(word, MAX_WORD_LENGTH),
                    )
                },
                "native_repair_flag": row["native_repair"],
                "skip_derived_repair_flag": row["skip_derived_repair"],
                "promoted_window_repair_flag": row["promoted_window_repair"],
                "derived_repair_flag": row["derived_repair"],
                "derived_only_flag": row["derived_only"],
                "promoted_only_flag": row["promoted_only"],
                "trace_signature_total_variation": row["variation"],
                "first_return_closed_path_count": profile[
                    "first_return_closed_path_count"
                ],
                "normalized_tail_template_count": profile[
                    "normalized_tail_template_count"
                ],
            }
        )

    return {
        "words": words,
        "cell_id_by_word": cell_id_by_word,
        "cell_rows": cell_rows,
        "component_rows": component_rows,
        "path_rows": path_rows,
        "edges": edge_set,
        "adjacency": adjacency,
        "component_sizes": [len(component) for component in components],
        "left_to_right_path_exists": int(right_id in distance),
        "shortest_path_length": distance.get(right_id, -1),
    }


def build_automaton_rows(
    graph: dict[str, Any],
    old_geometry: dict[str, Any],
) -> dict[str, Any]:
    words = graph["words"]
    rows_by_state = {row["grammar_cell_id"]: row for row in graph["cell_rows"]}
    edges = graph["edges"]
    adjacency = graph["adjacency"]
    left_id = graph["cell_id_by_word"][LEFT_REPAIR_BOUNDARY_WORD]
    gate_id = graph["cell_id_by_word"][NO_REPAIR_GATE_WORD]
    right_id = graph["cell_id_by_word"][RIGHT_REPAIR_BOUNDARY_WORD]
    merged_class_id = rows_by_state[left_id]["component_id"]

    native_nodes = {
        state_id
        for state_id, row in rows_by_state.items()
        if row["native_repair_flag"] == 1
    }
    native_components = connected_components(native_nodes, adjacency)
    native_class_id_by_state: dict[int, int] = {}
    native_class_rows = []
    for class_id, nodes in enumerate(native_components):
        node_set = set(nodes)
        for state_id in nodes:
            native_class_id_by_state[state_id] = class_id
        edge_count = sum(
            1 for source, target in edges if source in node_set and target in node_set
        )
        native_class_rows.append(
            {
                "native_recurrent_class_id": class_id,
                "state_count": len(nodes),
                "undirected_edge_count": edge_count,
                "left_boundary_flag": int(left_id in node_set),
                "right_boundary_flag": int(right_id in node_set),
                "gate_word_flag": int(gate_id in node_set),
            }
        )

    spectral = spectral_geometry(
        rows_by_state,
        words,
        edges,
        merged_class_id,
        left_id,
        gate_id,
        right_id,
    )
    side_by_state = spectral["side_by_state"]
    cut_edges = spectral["cut_edges"]
    old_edges = old_geometry["old_edges"]
    old_cut_edges = old_geometry["old_cut_edges"]
    edge_word_keys = {
        edge_word_key(words[source], words[target]): (source, target)
        for source, target in edges
    }
    new_cut_word_keys = {
        edge_word_key(words[source], words[target]) for source, target in cut_edges
    }
    old_cut_survivors = old_cut_edges & set(edge_word_keys)
    old_cut_still_cut = old_cut_edges & new_cut_word_keys

    edge_rows = []
    transition_degree = Counter()
    native_transition_degree = Counter()
    derived_transition_degree = Counter()
    promoted_transition_degree = Counter()
    native_neighbor_count = Counter()
    derived_neighbor_count = Counter()
    promoted_neighbor_count = Counter()
    for edge_id, (source, target) in enumerate(sorted(edges)):
        source_row = rows_by_state[source]
        target_row = rows_by_state[target]
        key = edge_word_key(words[source], words[target])
        native_transition = int(
            source_row["native_repair_flag"] and target_row["native_repair_flag"]
        )
        derived_transition = int(
            source_row["derived_only_flag"] or target_row["derived_only_flag"]
        )
        promoted_transition = int(
            source_row["promoted_window_repair_flag"]
            or target_row["promoted_window_repair_flag"]
        )
        promoted_only_transition = int(
            source_row["promoted_only_flag"] or target_row["promoted_only_flag"]
        )
        edit_kind, edit_position, source_symbol, target_symbol = edit_descriptor(
            words[source],
            words[target],
        )
        edge_rows.append(
            {
                "automaton_edge_id": edge_id,
                "source_state_id": source,
                "target_state_id": target,
                "source_grammar_cell_id": source,
                "target_grammar_cell_id": target,
                "edit_kind_code": edit_kind,
                "edit_position": edit_position,
                "source_symbol_id": source_symbol,
                "target_symbol_id": target_symbol,
                "native_transition_flag": native_transition,
                "derived_transition_flag": derived_transition,
                "promoted_transition_flag": promoted_transition,
                "promoted_only_transition_flag": promoted_only_transition,
                "old_repaired_edge_flag": int(key in old_edges),
                "old_spectral_cut_edge_flag": int(key in old_cut_edges),
                "new_spectral_cut_edge_flag": int((source, target) in cut_edges),
            }
        )
        for state_id, neighbor_id in [(source, target), (target, source)]:
            transition_degree[state_id] += 1
            if rows_by_state[neighbor_id]["native_repair_flag"]:
                native_neighbor_count[state_id] += 1
            if rows_by_state[neighbor_id]["derived_only_flag"]:
                derived_neighbor_count[state_id] += 1
            if rows_by_state[neighbor_id]["promoted_window_repair_flag"]:
                promoted_neighbor_count[state_id] += 1
            native_transition_degree[state_id] += native_transition
            derived_transition_degree[state_id] += derived_transition
            promoted_transition_degree[state_id] += promoted_transition

    state_rows = []
    for row in graph["cell_rows"]:
        state_id = row["grammar_cell_id"]
        word = words[state_id]
        state_rows.append(
            {
                "automaton_state_id": state_id,
                "grammar_cell_id": state_id,
                "promoted_recurrent_class_id": row["component_id"],
                "native_recurrent_class_id": native_class_id_by_state.get(state_id, -1),
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        WORD_COLUMNS,
                        padded(word, MAX_WORD_LENGTH),
                    )
                },
                "degree": transition_degree[state_id],
                "native_neighbor_count": native_neighbor_count[state_id],
                "derived_neighbor_count": derived_neighbor_count[state_id],
                "promoted_neighbor_count": promoted_neighbor_count[state_id],
                "native_transition_degree": native_transition_degree[state_id],
                "derived_transition_degree": derived_transition_degree[state_id],
                "promoted_transition_degree": promoted_transition_degree[state_id],
                "native_repair_flag": row["native_repair_flag"],
                "skip_derived_repair_flag": row["skip_derived_repair_flag"],
                "promoted_window_repair_flag": row["promoted_window_repair_flag"],
                "derived_repair_flag": row["derived_repair_flag"],
                "derived_only_flag": row["derived_only_flag"],
                "skip_derived_only_flag": row["skip_derived_only_flag"],
                "promoted_only_flag": row["promoted_only_flag"],
                "trace_signature_total_variation": row[
                    "trace_signature_total_variation"
                ],
                "first_return_closed_path_count": row[
                    "first_return_closed_path_count"
                ],
                "normalized_tail_template_count": row[
                    "normalized_tail_template_count"
                ],
                "left_boundary_flag": row["left_boundary_flag"],
                "right_boundary_flag": row["right_boundary_flag"],
                "gate_word_flag": row["gate_word_flag"],
                "merged_recurrent_class_flag": int(row["component_id"] == merged_class_id),
                "spectral_side_code": side_by_state.get(state_id, 0),
            }
        )

    class_rows = []
    for component in sorted(graph["component_rows"], key=lambda row: row["component_id"]):
        class_id = component["component_id"]
        node_set = {
            state_id
            for state_id, row in rows_by_state.items()
            if row["component_id"] == class_id
        }
        edge_count = sum(
            1 for source, target in edges if source in node_set and target in node_set
        )
        class_rows.append(
            {
                "promoted_recurrent_class_id": class_id,
                "state_count": len(node_set),
                "undirected_edge_count": edge_count,
                "native_state_count": sum(
                    rows_by_state[state_id]["native_repair_flag"]
                    for state_id in node_set
                ),
                "skip_derived_state_count": sum(
                    rows_by_state[state_id]["skip_derived_repair_flag"]
                    for state_id in node_set
                ),
                "promoted_window_state_count": sum(
                    rows_by_state[state_id]["promoted_window_repair_flag"]
                    for state_id in node_set
                ),
                "derived_only_state_count": sum(
                    rows_by_state[state_id]["derived_only_flag"]
                    for state_id in node_set
                ),
                "skip_derived_only_state_count": sum(
                    rows_by_state[state_id]["skip_derived_only_flag"]
                    for state_id in node_set
                ),
                "promoted_only_state_count": sum(
                    rows_by_state[state_id]["promoted_only_flag"]
                    for state_id in node_set
                ),
                "left_boundary_flag": int(left_id in node_set),
                "right_boundary_flag": int(right_id in node_set),
                "gate_word_flag": int(gate_id in node_set),
                "merged_boundary_flag": int(left_id in node_set and right_id in node_set),
                "spectral_certified_flag": int(class_id == merged_class_id),
            }
        )

    base_spectral_row = spectral["spectral_row"]
    promoted_cut_edges = sum(
        int(
            rows_by_state[source]["promoted_window_repair_flag"]
            or rows_by_state[target]["promoted_window_repair_flag"]
        )
        for source, target in cut_edges
    )
    promoted_only_cut_edges = sum(
        int(
            rows_by_state[source]["promoted_only_flag"]
            or rows_by_state[target]["promoted_only_flag"]
        )
        for source, target in cut_edges
    )
    spectral_row = {
        "spectral_cut_id": 0,
        "promoted_recurrent_class_id": merged_class_id,
        "state_count": base_spectral_row["state_count"],
        "undirected_edge_count": base_spectral_row["undirected_edge_count"],
        "lambda_2_x1e12": base_spectral_row["lambda_2_x1e12"],
        "lambda_3_x1e12": base_spectral_row["lambda_3_x1e12"],
        "spectral_gap_x1e12": base_spectral_row["spectral_gap_x1e12"],
        "cut_edge_count": base_spectral_row["cut_edge_count"],
        "derived_cut_edge_count": base_spectral_row["derived_cut_edge_count"],
        "promoted_cut_edge_count": promoted_cut_edges,
        "promoted_only_cut_edge_count": promoted_only_cut_edges,
        "positive_state_count": base_spectral_row["positive_state_count"],
        "negative_state_count": base_spectral_row["negative_state_count"],
        "positive_volume": base_spectral_row["positive_volume"],
        "negative_volume": base_spectral_row["negative_volume"],
        "cut_conductance_x1e12": base_spectral_row["cut_conductance_x1e12"],
        "left_side_code": base_spectral_row["left_side_code"],
        "gate_side_code": base_spectral_row["gate_side_code"],
        "right_side_code": base_spectral_row["right_side_code"],
        "old_cut_edge_count": len(old_cut_edges),
        "old_cut_edge_survival_count": len(old_cut_survivors),
        "old_cut_edge_still_cut_count": len(old_cut_still_cut),
        "old_cut_edge_same_side_count": len(old_cut_survivors) - len(old_cut_still_cut),
    }
    poincare_rows = []
    for row in spectral["poincare_rows"]:
        state_id = row["automaton_state_id"]
        state_row = rows_by_state[state_id]
        poincare_rows.append(
            {
                "poincare_point_id": row["poincare_point_id"],
                "automaton_state_id": state_id,
                "promoted_recurrent_class_id": merged_class_id,
                "spectral_side_code": row["spectral_side_code"],
                "poincare_x_x1e12": row["poincare_x_x1e12"],
                "poincare_y_x1e12": row["poincare_y_x1e12"],
                "poincare_radius_x1e12": row["poincare_radius_x1e12"],
                "fiedler_value_x1e12": row["fiedler_value_x1e12"],
                "third_mode_value_x1e12": row["third_mode_value_x1e12"],
                "left_boundary_flag": row["left_boundary_flag"],
                "right_boundary_flag": row["right_boundary_flag"],
                "gate_word_flag": row["gate_word_flag"],
                "promoted_window_repair_flag": state_row[
                    "promoted_window_repair_flag"
                ],
                "promoted_only_flag": state_row["promoted_only_flag"],
            }
        )

    return {
        "state_rows": state_rows,
        "edge_rows": edge_rows,
        "class_rows": class_rows,
        "native_class_rows": native_class_rows,
        "spectral_rows": [spectral_row],
        "poincare_rows": poincare_rows,
        "component_sizes": [row["state_count"] for row in class_rows],
        "native_class_sizes": [row["state_count"] for row in native_class_rows],
        "merged_class_id": merged_class_id,
        "left_id": left_id,
        "gate_id": gate_id,
        "right_id": right_id,
    }


def build_payload_rows() -> dict[str, Any]:
    _repair_rows, grammar_stats, repair_rows_by_block = grammar_rows()
    language = evaluate_language(repair_rows_by_block)
    graph = build_graph(language["rows_by_word"])
    old_geometry = load_old_geometry()
    automaton = build_automaton_rows(graph, old_geometry)
    flow_selection = load_flow_selection()
    stats = Counter(language["stats"])
    merged_component = next(
        row for row in graph["component_rows"] if row["merged_boundary_flag"] == 1
    )
    spectral_row = automaton["spectral_rows"][0]
    observable_values = {
        "boundary_union_word_count": stats["boundary_union_word_count"],
        "trace_failure_word_count": stats["trace_failure_word_count"],
        "bad_metric_word_count": stats["bad_metric_word_count"],
        "metric_ok_word_count": stats["metric_ok_word_count"],
        "closed_positive_metric_word_count": stats[
            "closed_positive_metric_word_count"
        ],
        "state_count": len(automaton["state_rows"]),
        "undirected_edge_count": len(automaton["edge_rows"]),
        "component_count": len(automaton["class_rows"]),
        "native_state_count": sum(
            row["native_repair_flag"] for row in automaton["state_rows"]
        ),
        "skip_derived_state_count": sum(
            row["skip_derived_repair_flag"] for row in automaton["state_rows"]
        ),
        "promoted_window_state_count": sum(
            row["promoted_window_repair_flag"] for row in automaton["state_rows"]
        ),
        "derived_only_state_count": sum(
            row["derived_only_flag"] for row in automaton["state_rows"]
        ),
        "skip_derived_only_state_count": sum(
            row["skip_derived_only_flag"] for row in automaton["state_rows"]
        ),
        "promoted_only_state_count": sum(
            row["promoted_only_flag"] for row in automaton["state_rows"]
        ),
        "new_state_count_vs_skip": len(automaton["state_rows"])
        - old_geometry["state_count"],
        "new_edge_count_vs_repaired": len(automaton["edge_rows"])
        - old_geometry["edge_count"],
        "merged_recurrent_class_size": spectral_row["state_count"],
        "merged_native_state_count": merged_component["native_cell_count"],
        "merged_skip_derived_only_state_count": merged_component[
            "skip_derived_only_cell_count"
        ],
        "merged_promoted_only_state_count": merged_component[
            "promoted_only_cell_count"
        ],
        "left_to_right_path_exists": graph["left_to_right_path_exists"],
        "shortest_path_length": graph["shortest_path_length"],
        "old_cut_edge_count": spectral_row["old_cut_edge_count"],
        "old_cut_edge_survival_count": spectral_row["old_cut_edge_survival_count"],
        "old_cut_edge_still_cut_count": spectral_row["old_cut_edge_still_cut_count"],
        "spectral_cut_edge_count": spectral_row["cut_edge_count"],
        "spectral_cut_derived_edge_count": spectral_row["derived_cut_edge_count"],
        "spectral_cut_promoted_edge_count": spectral_row["promoted_cut_edge_count"],
        "spectral_cut_promoted_only_edge_count": spectral_row[
            "promoted_only_cut_edge_count"
        ],
        "merged_lambda_2": spectral_row["lambda_2_x1e12"] / SCALE,
        "merged_lambda_3": spectral_row["lambda_3_x1e12"] / SCALE,
        "merged_cut_conductance": spectral_row["cut_conductance_x1e12"] / SCALE,
        "selected_block_code": block_code(PROMOTED_BLOCK),
        "flow_selected_candidate_word_count": int(
            flow_selection["candidate_word_count"]
        ),
    }
    observable_rows = []
    for observable_id, (key, code) in enumerate(PROMOTED_OBSERVABLE_CODES.items()):
        value = observable_values[key]
        scaled = scaled_float(value) if key in FLOAT_OBSERVABLES else int(value) * SCALE
        observable_rows.append(
            {
                "observable_id": observable_id,
                "observable_code": code,
                "value_x1e12": scaled,
                "aux_id": -1,
            }
        )
    return {
        **graph,
        **automaton,
        "grammar_stats": grammar_stats,
        "language_stats": dict(stats),
        "old_geometry": old_geometry,
        "flow_selection": flow_selection,
        "observable_values": observable_values,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    skip_report = load_json(SKIP_WINDOW_REPORT)
    repaired_report = load_json(REPAIRED_AUTOMATON_REPORT)
    flow_report = load_json(FLOW_WINDOW_REPORT)
    rows = build_payload_rows()

    cell_table = table_from_rows(CELL_COLUMNS, rows["cell_rows"])
    component_table = table_from_rows(COMPONENT_COLUMNS, rows["component_rows"])
    path_table = table_from_rows(PATH_COLUMNS, rows["path_rows"])
    state_table = table_from_rows(STATE_COLUMNS, rows["state_rows"])
    edge_table = table_from_rows(EDGE_COLUMNS, rows["edge_rows"])
    recurrent_class_table = table_from_rows(
        RECURRENT_CLASS_COLUMNS,
        rows["class_rows"],
    )
    native_recurrent_class_table = table_from_rows(
        NATIVE_CLASS_COLUMNS,
        rows["native_class_rows"],
    )
    spectral_cut_table = table_from_rows(SPECTRAL_CUT_COLUMNS, rows["spectral_rows"])
    poincare_table = table_from_rows(POINCARE_COLUMNS, rows["poincare_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])

    observable_values = rows["observable_values"]
    spectral_row = rows["spectral_rows"][0]
    selected_block = rows["flow_selection"]["block"]
    checks = {
        "skip_window_report_certified": skip_report.get("status")
        == SKIP_WINDOW_STATUS,
        "repaired_automaton_report_certified": repaired_report.get("status")
        == REPAIRED_AUTOMATON_STATUS,
        "flow_window_report_certified": flow_report.get("status")
        == FLOW_WINDOW_STATUS,
        "selected_flow_window_block_is_promoted": selected_block == PROMOTED_BLOCK,
        "boundary_language_counts_are_expected": (
            observable_values["boundary_union_word_count"],
            observable_values["trace_failure_word_count"],
            observable_values["bad_metric_word_count"],
            observable_values["metric_ok_word_count"],
            observable_values["closed_positive_metric_word_count"],
        )
        == (234_678, 68_103, 140_378, 26_197, 984),
        "promotion_extends_skip_language_by_nine_cells": (
            observable_values["state_count"],
            observable_values["promoted_window_state_count"],
            observable_values["promoted_only_state_count"],
            observable_values["new_state_count_vs_skip"],
        )
        == (855, 89, 9, 9),
        "boundary_pair_remains_merged": (
            observable_values["left_to_right_path_exists"],
            observable_values["shortest_path_length"],
            spectral_row["left_side_code"],
            spectral_row["gate_side_code"],
            spectral_row["right_side_code"],
        )
        == (1, 2, 1, 1, 1),
        "old_cut_lineage_is_tracked": (
            observable_values["old_cut_edge_count"],
            observable_values["old_cut_edge_survival_count"],
        )
        == (6, 6),
        "spectral_values_are_positive": (
            spectral_row["lambda_2_x1e12"] > 0
            and spectral_row["lambda_3_x1e12"] > spectral_row["lambda_2_x1e12"]
            and spectral_row["cut_conductance_x1e12"] > 0
        ),
        "new_spectral_cut_is_not_empty": spectral_row["cut_edge_count"] > 0,
        "table_shapes_match_codebooks": (
            tuple(cell_table.shape) == (observable_values["state_count"], len(CELL_COLUMNS))
            and tuple(component_table.shape)
            == (observable_values["component_count"], len(COMPONENT_COLUMNS))
            and tuple(path_table.shape) == (3, len(PATH_COLUMNS))
            and tuple(state_table.shape) == (observable_values["state_count"], len(STATE_COLUMNS))
            and tuple(edge_table.shape)
            == (observable_values["undirected_edge_count"], len(EDGE_COLUMNS))
            and tuple(recurrent_class_table.shape)
            == (observable_values["component_count"], len(RECURRENT_CLASS_COLUMNS))
            and tuple(native_recurrent_class_table.shape)[1]
            == len(NATIVE_CLASS_COLUMNS)
            and tuple(spectral_cut_table.shape) == (1, len(SPECTRAL_CUT_COLUMNS))
            and tuple(poincare_table.shape)[1] == len(POINCARE_COLUMNS)
            and tuple(observable_table.shape)
            == (len(PROMOTED_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS))
        ),
    }

    witness = {
        "promoted_block": list(PROMOTED_BLOCK),
        "flow_selection": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in rows["flow_selection"].items()
        },
        "language_stats": rows["language_stats"],
        "state_count": observable_values["state_count"],
        "undirected_edge_count": observable_values["undirected_edge_count"],
        "component_sizes": rows["component_sizes"],
        "native_class_sizes": rows["native_class_sizes"],
        "promotion_profile": {
            "promoted_window_state_count": observable_values[
                "promoted_window_state_count"
            ],
            "promoted_only_state_count": observable_values[
                "promoted_only_state_count"
            ],
            "new_state_count_vs_skip": observable_values["new_state_count_vs_skip"],
            "new_edge_count_vs_repaired": observable_values[
                "new_edge_count_vs_repaired"
            ],
        },
        "old_cut_lineage": {
            "old_cut_edge_count": spectral_row["old_cut_edge_count"],
            "old_cut_edge_survival_count": spectral_row[
                "old_cut_edge_survival_count"
            ],
            "old_cut_edge_still_cut_count": spectral_row[
                "old_cut_edge_still_cut_count"
            ],
            "old_cut_edge_same_side_count": spectral_row[
                "old_cut_edge_same_side_count"
            ],
        },
        "spectral_cut": {
            "lambda_2_x1e12": spectral_row["lambda_2_x1e12"],
            "lambda_3_x1e12": spectral_row["lambda_3_x1e12"],
            "cut_edge_count": spectral_row["cut_edge_count"],
            "derived_cut_edge_count": spectral_row["derived_cut_edge_count"],
            "promoted_cut_edge_count": spectral_row["promoted_cut_edge_count"],
            "promoted_only_cut_edge_count": spectral_row[
                "promoted_only_cut_edge_count"
            ],
            "positive_state_count": spectral_row["positive_state_count"],
            "negative_state_count": spectral_row["negative_state_count"],
            "positive_volume": spectral_row["positive_volume"],
            "negative_volume": spectral_row["negative_volume"],
            "cut_conductance_x1e12": spectral_row["cut_conductance_x1e12"],
        },
        "cell_table_sha256": sha_array(cell_table),
        "component_table_sha256": sha_array(component_table),
        "path_table_sha256": sha_array(path_table),
        "state_table_sha256": sha_array(state_table),
        "edge_table_sha256": sha_array(edge_table),
        "recurrent_class_table_sha256": sha_array(recurrent_class_table),
        "native_recurrent_class_table_sha256": sha_array(
            native_recurrent_class_table
        ),
        "spectral_cut_table_sha256": sha_array(spectral_cut_table),
        "poincare_table_sha256": sha_array(poincare_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    promoted_window = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_promoted_window@1",
        "object": "d20",
        "parents": {
            "skip_window": SKIP_WINDOW_REPORT.relative_to(ROOT).as_posix(),
            "repaired_automaton": REPAIRED_AUTOMATON_REPORT.relative_to(ROOT).as_posix(),
            "flow_window": FLOW_WINDOW_REPORT.relative_to(ROOT).as_posix(),
        },
        "promotion_rule": {
            "block": list(PROMOTED_BLOCK),
            "source": "selected clean flow-window move",
            "language_test": [
                "use the certified radius-three boundary-pair word union",
                "filter to delta_twice=2, variation<=223, and closed positivity",
                "admit native repair words, skip-derived repair words, or words containing the promoted 5,5,2,5 window",
            ],
        },
        "summary": {
            "state_count": observable_values["state_count"],
            "promoted_only_state_count": observable_values[
                "promoted_only_state_count"
            ],
            "undirected_edge_count": observable_values["undirected_edge_count"],
            "spectral_cut_edge_count": spectral_row["cut_edge_count"],
            "old_cut_edge_still_cut_count": spectral_row[
                "old_cut_edge_still_cut_count"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_promoted_window_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_PROMOTED_WINDOW_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the selected 5,5,2,5 flow-window move is promoted to a global window admission rule",
            "the promoted grammar adds exactly nine closed-positive cells beyond the skip-window grammar",
            "the boundary pair remains merged through the existing gate path",
            "the promoted automaton rebuild tracks every old six-edge spectral cut edge through the new graph",
            "the dominant promoted recurrent class has a fresh normalized-Laplacian spectral cut and Poincare readout",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_promoted_window@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The selected flow-window block 5,5,2,5 can be promoted into the "
            "closed-positive boundary language without blowing up the grammar: "
            "it adds exactly nine new admitted cells beyond the 846-cell "
            "skip-window grammar, giving a 855-state promoted automaton. The "
            "rebuild preserves the left -> gate -> right length-two boundary "
            "path and tracks all six old spectral cut edges inside the new "
            "graph. The promoted dominant class has normalized-Laplacian "
            f"lambda_2 {spectral_row['lambda_2_x1e12']}/1e12 and a "
            f"{spectral_row['cut_edge_count']}-edge spectral cut; "
            f"{spectral_row['old_cut_edge_still_cut_count']} of the six old "
            "cut edges remain on the fresh Fiedler cut."
        ),
        "stage_protocol": {
            "draft": "promote the flow-selected four-symbol window into the grammar admission rule",
            "witness": "enumerate promoted cells and rebuild the one-edit automaton",
            "coherence": "compare promoted cells, old repaired edges, and old cut lineage",
            "closure": "certify the boundary merge and fresh spectral/Poincare geometry",
            "emit": "emit promoted grammar, automaton, spectral, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "skip_window_report": input_entry(
                SKIP_WINDOW_REPORT,
                {
                    "status": skip_report.get("status"),
                    "certificate_sha256": skip_report.get("certificate_sha256"),
                },
            ),
            "skip_window_tables": input_entry(SKIP_WINDOW_TABLES),
            "repaired_automaton_report": input_entry(
                REPAIRED_AUTOMATON_REPORT,
                {
                    "status": repaired_report.get("status"),
                    "certificate_sha256": repaired_report.get("certificate_sha256"),
                },
            ),
            "repaired_automaton_tables": input_entry(REPAIRED_AUTOMATON_TABLES),
            "flow_window_report": input_entry(
                FLOW_WINDOW_REPORT,
                {
                    "status": flow_report.get("status"),
                    "certificate_sha256": flow_report.get("certificate_sha256"),
                },
            ),
            "flow_window_tables": input_entry(FLOW_WINDOW_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_promoted_window": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_promoted_window.json"
            ),
            "promoted_window_cells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_cells.csv"
            ),
            "promoted_window_components_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_components.csv"
            ),
            "promoted_window_path_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_path.csv"
            ),
            "promoted_window_states_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_states.csv"
            ),
            "promoted_window_edges_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_edges.csv"
            ),
            "promoted_window_recurrent_classes_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_promoted_window_recurrent_classes.csv"
            ),
            "promoted_window_native_recurrent_classes_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_promoted_window_native_recurrent_classes.csv"
            ),
            "promoted_window_spectral_cut_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_spectral_cut.csv"
            ),
            "promoted_window_poincare_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_poincare.csv"
            ),
            "promoted_window_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_promoted_window_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_promoted_window_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_promoted_window_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected 5,5,2,5 promoted-window rule over the certified radius-three boundary-pair union",
                "the promoted grammar cell/component decomposition",
                "the promoted one-edit automaton and native recurrent classes",
                "old spectral cut lineage under the promoted automaton",
                "the fresh spectral cut and two-mode Poincare disk readout of the promoted dominant class",
            ],
            "does_not_certify_because_not_required": [
                "boundary words outside the certified radius-three side union",
                "multi-block promotion closure beyond the single selected window",
                "normal JSON compiler wiring for C985 objects",
                "optimality of the promoted rule among all possible flow-window promotions",
            ],
        },
        "next_highest_yield_item": (
            "Run the native-biased transfer operator on the promoted-window "
            "automaton and compare stationary flow against the new Fiedler "
            "cut, especially the surviving old-cut edges that still carry "
            "bottleneck mass."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_promoted_window_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified skip-window, repaired-automaton, and flow-window artifacts",
            "promote the selected 5,5,2,5 window through the boundary-pair word union",
            "rebuild grammar components and the one-edit promoted automaton",
            "track old spectral cut lineage and recompute fresh spectral/Poincare geometry",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_promoted_window": promoted_window,
        "promoted_window_cells_csv": csv_text(CELL_COLUMNS, rows["cell_rows"]),
        "promoted_window_components_csv": csv_text(
            COMPONENT_COLUMNS,
            rows["component_rows"],
        ),
        "promoted_window_path_csv": csv_text(PATH_COLUMNS, rows["path_rows"]),
        "promoted_window_states_csv": csv_text(STATE_COLUMNS, rows["state_rows"]),
        "promoted_window_edges_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "promoted_window_recurrent_classes_csv": csv_text(
            RECURRENT_CLASS_COLUMNS,
            rows["class_rows"],
        ),
        "promoted_window_native_recurrent_classes_csv": csv_text(
            NATIVE_CLASS_COLUMNS,
            rows["native_class_rows"],
        ),
        "promoted_window_spectral_cut_csv": csv_text(
            SPECTRAL_CUT_COLUMNS,
            rows["spectral_rows"],
        ),
        "promoted_window_poincare_csv": csv_text(
            POINCARE_COLUMNS,
            rows["poincare_rows"],
        ),
        "promoted_window_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "cell_table": cell_table,
        "component_table": component_table,
        "path_table": path_table,
        "state_table": state_table,
        "edge_table": edge_table,
        "recurrent_class_table": recurrent_class_table,
        "native_recurrent_class_table": native_recurrent_class_table,
        "spectral_cut_table": spectral_cut_table,
        "poincare_table": poincare_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_promoted_window.json",
        payloads["signature_boundary_spine_aperture_closure_tail_promoted_window"],
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_cells.csv").write_text(
        payloads["promoted_window_cells_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_components.csv").write_text(
        payloads["promoted_window_components_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_path.csv").write_text(
        payloads["promoted_window_path_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_states.csv").write_text(
        payloads["promoted_window_states_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_edges.csv").write_text(
        payloads["promoted_window_edges_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_promoted_window_recurrent_classes.csv"
    ).write_text(
        payloads["promoted_window_recurrent_classes_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_promoted_window_native_recurrent_classes.csv"
    ).write_text(
        payloads["promoted_window_native_recurrent_classes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_spectral_cut.csv").write_text(
        payloads["promoted_window_spectral_cut_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_poincare.csv").write_text(
        payloads["promoted_window_poincare_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_promoted_window_observables.csv").write_text(
        payloads["promoted_window_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_window_tables.npz",
        cell_table=payloads["cell_table"],
        component_table=payloads["component_table"],
        path_table=payloads["path_table"],
        state_table=payloads["state_table"],
        edge_table=payloads["edge_table"],
        recurrent_class_table=payloads["recurrent_class_table"],
        native_recurrent_class_table=payloads["native_recurrent_class_table"],
        spectral_cut_table=payloads["spectral_cut_table"],
        poincare_table=payloads["poincare_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate"
        ],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
