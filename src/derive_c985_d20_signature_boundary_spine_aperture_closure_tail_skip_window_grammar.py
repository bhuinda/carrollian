from __future__ import annotations

import json
from collections import Counter, deque
from itertools import combinations, product
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search import (
        CELL_COMPLEX_EDGES,
        LEFT_REPAIR_BOUNDARY_WORD,
        MAX_SIDE_EDIT_RADIUS,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        PREFIX_FIXED,
        REWRITE_COMPLEX_EDGES,
        RIGHT_REPAIR_BOUNDARY_WORD,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        input_entry,
        load_json,
        one_edit_neighbors,
        padded,
        radius_from,
        read_int_csv,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        edge_key,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement import (
        OUT_DIR as SYMBOLIC_WINDOW_DIR,
        STATUS as SYMBOLIC_WINDOW_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        PREFIX_SYMBOLS,
        REWRITE_COMPLEX_NODES,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search import (
        CELL_COMPLEX_EDGES,
        LEFT_REPAIR_BOUNDARY_WORD,
        MAX_SIDE_EDIT_RADIUS,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        PREFIX_FIXED,
        REWRITE_COMPLEX_EDGES,
        RIGHT_REPAIR_BOUNDARY_WORD,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_DELTA_TWICE,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        build_context,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
        input_entry,
        load_json,
        one_edit_neighbors,
        padded,
        radius_from,
        read_int_csv,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        edge_key,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement import (
        OUT_DIR as SYMBOLIC_WINDOW_DIR,
        STATUS as SYMBOLIC_WINDOW_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        PREFIX_SYMBOLS,
        REWRITE_COMPLEX_NODES,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SKIP_WINDOW_GRAMMAR_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SYMBOLIC_WINDOW_REPORT = SYMBOLIC_WINDOW_DIR / "report.json"
SYMBOLIC_WINDOW_CERTIFICATE = (
    SYMBOLIC_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate.json"
)
DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar.py"
)

REPAIR_SPLIT_COLUMNS = [
    "repair_split_id",
    "block_symbol_0_id",
    "block_symbol_1_id",
    "block_symbol_2_id",
    "block_symbol_3_id",
    "split_index_code",
    "source_node_id",
    "inserted_node_id",
    "target_node_id",
    "split_first_symbol_id",
    "split_second_symbol_id",
    "split_third_symbol_id",
    "repair_31_28_flag",
    "repair_50_34_flag",
    "variation_preserving_flag",
    "direct_variation",
    "split_variation",
    "source_to_insert_edge_flag",
    "insert_to_target_edge_flag",
]

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
    "derived_repair_flag",
    "derived_only_flag",
    "first_derived_span_rank",
    "first_derived_block_symbol_0_id",
    "first_derived_block_symbol_1_id",
    "first_derived_block_symbol_2_id",
    "first_derived_block_symbol_3_id",
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
    "derived_only_cell_count",
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
    "derived_repair_flag",
    "derived_only_flag",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
]

SKIP_WINDOW_OBSERVABLE_CODES = {
    "alphabet_size": 0,
    "four_symbol_block_count": 1,
    "valid_split_count": 2,
    "valid_split_block_count": 3,
    "valid_variation_preserving_split_count": 4,
    "repair_split_count": 5,
    "repair_split_block_count": 6,
    "repair_31_28_split_count": 7,
    "repair_50_34_split_count": 8,
    "repair_variation_preserving_split_count": 9,
    "boundary_union_word_count": 10,
    "trace_failure_word_count": 11,
    "bad_metric_word_count": 12,
    "metric_ok_word_count": 13,
    "native_repair_metric_count": 14,
    "derived_repair_metric_count": 15,
    "native_good_cell_count": 16,
    "derived_closed_cell_count": 17,
    "grammar_good_cell_count": 18,
    "derived_only_closed_cell_count": 19,
    "virtual_candidate_count": 20,
    "grammar_graph_edge_count": 21,
    "grammar_component_count": 22,
    "merged_component_size": 23,
    "merged_native_cell_count": 24,
    "merged_derived_only_cell_count": 25,
    "left_to_right_path_exists": 26,
    "shortest_path_length": 27,
    "gate_native_repair_flag": 28,
    "gate_derived_repair_flag": 29,
    "gate_closed_path_count": 30,
    "gate_template_count": 31,
}


def triple(row: dict[str, int]) -> tuple[int, int, int]:
    return (
        int(row["left_symbol_id"]),
        int(row["middle_symbol_id"]),
        int(row["right_symbol_id"]),
    )


def repair_edge_flag(source: int, inserted: int, target: int) -> tuple[int, int]:
    first = edge_key(source, inserted)
    second = edge_key(inserted, target)
    return (
        int(first == edge_key(31, 28) or second == edge_key(31, 28)),
        int(first == edge_key(50, 34) or second == edge_key(50, 34)),
    )


def grammar_rows() -> tuple[list[dict[str, int]], dict[str, int], dict[tuple[int, int, int, int], list[dict[str, int]]]]:
    assoc_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    assoc_by_triple = {triple(row): row for row in assoc_rows}
    alphabet = sorted(
        {
            int(row["left_symbol_id"])
            for row in assoc_rows
        }
    )
    node_signatures = {
        int(row["node_id"]): int(row["signature_union_count"])
        for row in read_int_csv(REWRITE_COMPLEX_NODES)
    }
    rewrite_edges = {
        edge_key(row["source_node_id"], row["target_node_id"])
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }
    valid_split_blocks: set[tuple[int, int, int, int]] = set()
    repair_split_blocks: set[tuple[int, int, int, int]] = set()
    repair_rows: list[dict[str, int]] = []
    repair_rows_by_block: dict[tuple[int, int, int, int], list[dict[str, int]]] = {}
    valid_split_count = 0
    valid_variation_preserving_split_count = 0

    for block in product(alphabet, repeat=4):
        subwindows = [
            tuple(block[index] for index in indices)
            for indices in combinations(range(4), 3)
        ]
        nodes = [
            int(assoc_by_triple[subwindow]["canonical_triple_id"])
            for subwindow in subwindows
        ]
        source = nodes[0]
        target = nodes[3]
        direct_variation = abs(node_signatures[target] - node_signatures[source])
        for split_index, inserted in [(1, nodes[1]), (2, nodes[2])]:
            source_to_insert = edge_key(source, inserted) in rewrite_edges
            insert_to_target = edge_key(inserted, target) in rewrite_edges
            if not (source_to_insert and insert_to_target):
                continue
            valid_split_count += 1
            valid_split_blocks.add(block)
            split_variation = abs(node_signatures[inserted] - node_signatures[source]) + abs(
                node_signatures[target] - node_signatures[inserted]
            )
            variation_preserving = int(split_variation == direct_variation)
            valid_variation_preserving_split_count += variation_preserving
            repair_31, repair_50 = repair_edge_flag(source, inserted, target)
            if not (repair_31 or repair_50):
                continue
            repair_split_blocks.add(block)
            row = {
                "repair_split_id": len(repair_rows),
                "block_symbol_0_id": block[0],
                "block_symbol_1_id": block[1],
                "block_symbol_2_id": block[2],
                "block_symbol_3_id": block[3],
                "split_index_code": split_index,
                "source_node_id": source,
                "inserted_node_id": inserted,
                "target_node_id": target,
                "split_first_symbol_id": subwindows[split_index][0],
                "split_second_symbol_id": subwindows[split_index][1],
                "split_third_symbol_id": subwindows[split_index][2],
                "repair_31_28_flag": repair_31,
                "repair_50_34_flag": repair_50,
                "variation_preserving_flag": variation_preserving,
                "direct_variation": direct_variation,
                "split_variation": split_variation,
                "source_to_insert_edge_flag": int(source_to_insert),
                "insert_to_target_edge_flag": int(insert_to_target),
            }
            repair_rows.append(row)
            repair_rows_by_block.setdefault(block, []).append(row)

    stats = {
        "alphabet_size": len(alphabet),
        "four_symbol_block_count": len(alphabet) ** 4,
        "valid_split_count": valid_split_count,
        "valid_split_block_count": len(valid_split_blocks),
        "valid_variation_preserving_split_count": valid_variation_preserving_split_count,
        "repair_split_count": len(repair_rows),
        "repair_split_block_count": len(repair_split_blocks),
        "repair_31_28_split_count": sum(row["repair_31_28_flag"] for row in repair_rows),
        "repair_50_34_split_count": sum(row["repair_50_34_flag"] for row in repair_rows),
        "repair_variation_preserving_split_count": sum(
            row["variation_preserving_flag"] for row in repair_rows
        ),
    }
    return repair_rows, stats, repair_rows_by_block


def derived_spans(
    word: tuple[int, ...],
    repair_rows_by_block: dict[tuple[int, int, int, int], list[dict[str, int]]],
) -> list[tuple[int, tuple[int, int, int, int], list[dict[str, int]]]]:
    sequence = (*PREFIX_SYMBOLS, *word, *word[:2])
    spans = []
    for rank in range(len(sequence) - 3):
        block = tuple(int(value) for value in sequence[rank : rank + 4])
        rows = repair_rows_by_block.get(block)
        if rows:
            spans.append((rank, block, rows))
    return spans


def evaluate_language(
    repair_rows_by_block: dict[tuple[int, int, int, int], list[dict[str, int]]],
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
        spans = derived_spans(word, repair_rows_by_block)
        derived_repair = int(bool(spans))
        if native_repair:
            stats["native_repair_metric_count"] += 1
        if derived_repair:
            stats["derived_repair_metric_count"] += 1
        profile = closure_profile(word, carrier_adjacency)
        if profile["first_return_closed_path_count"] <= 0:
            continue
        if native_repair:
            stats["native_good_cell_count"] += 1
        if derived_repair:
            stats["derived_closed_cell_count"] += 1
        if not native_repair:
            stats["virtual_candidate_count"] += 1
        if not (native_repair or derived_repair):
            continue
        stats["grammar_good_cell_count"] += 1
        if derived_repair and not native_repair:
            stats["derived_only_closed_cell_count"] += 1
        first_span_rank, first_block, _first_rows = spans[0] if spans else (-1, (-1, -1, -1, -1), [])
        rows_by_word[word] = {
            "word": word,
            "left_edit_radius": left_radius.get(word, 99),
            "right_edit_radius": right_radius.get(word, 99),
            "trace": trace,
            "delta_twice": delta_twice,
            "variation": variation,
            "native_repair": native_repair,
            "derived_repair": derived_repair,
            "derived_only": int(derived_repair and not native_repair),
            "first_span_rank": first_span_rank,
            "first_block": first_block,
            "profile": profile,
        }

    return {
        "stats": dict(stats),
        "rows_by_word": rows_by_word,
    }


def build_graph(rows_by_word: dict[tuple[int, ...], dict[str, Any]]) -> dict[str, Any]:
    words = sorted(rows_by_word)
    cell_id_by_word = {word: index for index, word in enumerate(words)}
    adjacency: dict[int, set[int]] = {index: set() for index in range(len(words))}
    edge_set: set[tuple[int, int]] = set()
    for word, source_id in cell_id_by_word.items():
        for neighbor in set(one_edit_neighbors(word)):
            target_id = cell_id_by_word.get(neighbor)
            if target_id is None:
                continue
            edge = tuple(sorted((source_id, target_id)))
            if edge[0] != edge[1]:
                edge_set.add(edge)
            adjacency[source_id].add(target_id)
            adjacency[target_id].add(source_id)

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

    def component_sort_key(component: set[int]) -> tuple[int, int]:
        component_words = {words[cell_id] for cell_id in component}
        merged = int(
            LEFT_REPAIR_BOUNDARY_WORD in component_words
            and RIGHT_REPAIR_BOUNDARY_WORD in component_words
        )
        return (-merged, -len(component))

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
                "derived_repair_flag": row["derived_repair"],
                "derived_only_flag": row["derived_only"],
                "first_derived_span_rank": row["first_span_rank"],
                "first_derived_block_symbol_0_id": row["first_block"][0],
                "first_derived_block_symbol_1_id": row["first_block"][1],
                "first_derived_block_symbol_2_id": row["first_block"][2],
                "first_derived_block_symbol_3_id": row["first_block"][3],
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
                "derived_only_cell_count": sum(row["derived_only_flag"] for row in cells),
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
                "derived_repair_flag": row["derived_repair"],
                "derived_only_flag": row["derived_only"],
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
        "cell_rows": cell_rows,
        "component_rows": component_rows,
        "path_rows": path_rows,
        "edge_count": len(edge_set),
        "component_sizes": [len(component) for component in components],
        "left_to_right_path_exists": int(right_id in components[component_id_by_cell[left_id]]),
        "shortest_path_length": distance[right_id],
    }


def build_payload_rows() -> dict[str, Any]:
    repair_rows, grammar_stats, repair_rows_by_block = grammar_rows()
    language = evaluate_language(repair_rows_by_block)
    graph = build_graph(language["rows_by_word"])
    stats = dict(language["stats"])
    merged_component = next(
        row for row in graph["component_rows"] if row["merged_boundary_flag"] == 1
    )
    gate_cell = next(row for row in graph["cell_rows"] if row["gate_word_flag"] == 1)
    observable_values = {
        **grammar_stats,
        "boundary_union_word_count": stats["boundary_union_word_count"],
        "trace_failure_word_count": stats["trace_failure_word_count"],
        "bad_metric_word_count": stats["bad_metric_word_count"],
        "metric_ok_word_count": stats["metric_ok_word_count"],
        "native_repair_metric_count": stats["native_repair_metric_count"],
        "derived_repair_metric_count": stats["derived_repair_metric_count"],
        "native_good_cell_count": stats["native_good_cell_count"],
        "derived_closed_cell_count": stats["derived_closed_cell_count"],
        "grammar_good_cell_count": stats["grammar_good_cell_count"],
        "derived_only_closed_cell_count": stats["derived_only_closed_cell_count"],
        "virtual_candidate_count": stats["virtual_candidate_count"],
        "grammar_graph_edge_count": graph["edge_count"],
        "grammar_component_count": len(graph["component_rows"]),
        "merged_component_size": merged_component["cell_count"],
        "merged_native_cell_count": merged_component["native_cell_count"],
        "merged_derived_only_cell_count": merged_component["derived_only_cell_count"],
        "left_to_right_path_exists": graph["left_to_right_path_exists"],
        "shortest_path_length": graph["shortest_path_length"],
        "gate_native_repair_flag": gate_cell["native_repair_flag"],
        "gate_derived_repair_flag": gate_cell["derived_repair_flag"],
        "gate_closed_path_count": gate_cell["first_return_closed_path_count"],
        "gate_template_count": gate_cell["normalized_tail_template_count"],
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": SKIP_WINDOW_OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    return {
        "repair_rows": repair_rows,
        "cell_rows": graph["cell_rows"],
        "component_rows": graph["component_rows"],
        "path_rows": graph["path_rows"],
        "component_sizes": graph["component_sizes"],
        "observable_values": observable_values,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    symbolic_report = load_json(SYMBOLIC_WINDOW_REPORT)
    symbolic_certificate = load_json(SYMBOLIC_WINDOW_CERTIFICATE)
    payload_rows = build_payload_rows()
    repair_rows = payload_rows["repair_rows"]
    cell_rows = payload_rows["cell_rows"]
    component_rows = payload_rows["component_rows"]
    path_rows = payload_rows["path_rows"]
    component_sizes = payload_rows["component_sizes"]
    observable_values = payload_rows["observable_values"]
    observable_rows = payload_rows["observable_rows"]

    repair_split_table = table_from_rows(REPAIR_SPLIT_COLUMNS, repair_rows)
    cell_table = table_from_rows(CELL_COLUMNS, cell_rows)
    component_table = table_from_rows(COMPONENT_COLUMNS, component_rows)
    path_table = table_from_rows(PATH_COLUMNS, path_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)
    path_words = [
        tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)
        for row in path_rows
    ]

    checks = {
        "symbolic_window_report_certified": symbolic_report.get("status")
        == SYMBOLIC_WINDOW_STATUS,
        "symbolic_window_certificate_certified": symbolic_certificate.get("status")
        == SYMBOLIC_WINDOW_STATUS,
        "global_grammar_counts_are_expected": (
            observable_values["four_symbol_block_count"],
            observable_values["valid_split_count"],
            observable_values["valid_split_block_count"],
            observable_values["valid_variation_preserving_split_count"],
            observable_values["repair_split_count"],
            observable_values["repair_split_block_count"],
        )
        == (1_296, 1_800, 1_170, 556, 32, 32),
        "repair_splits_are_balanced": (
            observable_values["repair_31_28_split_count"],
            observable_values["repair_50_34_split_count"],
            observable_values["repair_variation_preserving_split_count"],
        )
        == (16, 16, 4),
        "boundary_language_counts_are_expected": (
            observable_values["boundary_union_word_count"],
            observable_values["trace_failure_word_count"],
            observable_values["bad_metric_word_count"],
            observable_values["metric_ok_word_count"],
        )
        == (234_678, 68_103, 140_378, 26_197),
        "grammar_good_counts_are_expected": (
            observable_values["native_repair_metric_count"],
            observable_values["derived_repair_metric_count"],
            observable_values["native_good_cell_count"],
            observable_values["derived_closed_cell_count"],
            observable_values["grammar_good_cell_count"],
            observable_values["derived_only_closed_cell_count"],
            observable_values["virtual_candidate_count"],
        )
        == (11_637, 20_744, 562, 846, 846, 284, 422),
        "grammar_graph_counts_are_expected": (
            observable_values["grammar_graph_edge_count"],
            observable_values["grammar_component_count"],
            observable_values["merged_component_size"],
            observable_values["merged_native_cell_count"],
            observable_values["merged_derived_only_cell_count"],
        )
        == (2_549, 22, 787, 532, 255),
        "grammar_path_closes_boundary_pair": (
            observable_values["left_to_right_path_exists"],
            observable_values["shortest_path_length"],
            path_words,
        )
        == (
            1,
            2,
            [
                LEFT_REPAIR_BOUNDARY_WORD,
                NO_REPAIR_GATE_WORD,
                RIGHT_REPAIR_BOUNDARY_WORD,
            ],
        ),
        "gate_is_derived_only_closed_positive": (
            observable_values["gate_native_repair_flag"],
            observable_values["gate_derived_repair_flag"],
            observable_values["gate_closed_path_count"],
            observable_values["gate_template_count"],
        )
        == (0, 1, 30, 9),
        "component_sizes_are_expected": component_sizes
        == [787, 15, 11, 6, 4, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "repair_split_table_shape_matches_codebook": tuple(repair_split_table.shape)
        == (32, len(REPAIR_SPLIT_COLUMNS)),
        "cell_table_shape_matches_codebook": tuple(cell_table.shape)
        == (846, len(CELL_COLUMNS)),
        "component_table_shape_matches_codebook": tuple(component_table.shape)
        == (22, len(COMPONENT_COLUMNS)),
        "path_table_shape_matches_codebook": tuple(path_table.shape)
        == (3, len(PATH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(SKIP_WINDOW_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "repair_split_count": observable_values["repair_split_count"],
        "repair_31_28_split_count": observable_values["repair_31_28_split_count"],
        "repair_50_34_split_count": observable_values["repair_50_34_split_count"],
        "repair_variation_preserving_split_count": observable_values[
            "repair_variation_preserving_split_count"
        ],
        "grammar_good_cell_count": observable_values["grammar_good_cell_count"],
        "derived_only_closed_cell_count": observable_values[
            "derived_only_closed_cell_count"
        ],
        "component_sizes": component_sizes,
        "shortest_path_words": [list(word) for word in path_words],
        "gate_profile": {
            "word": list(NO_REPAIR_GATE_WORD),
            "native_repair": observable_values["gate_native_repair_flag"],
            "derived_repair": observable_values["gate_derived_repair_flag"],
            "closed_paths": observable_values["gate_closed_path_count"],
            "templates": observable_values["gate_template_count"],
        },
        "repair_split_table_sha256": sha_array(repair_split_table),
        "cell_table_sha256": sha_array(cell_table),
        "component_table_sha256": sha_array(component_table),
        "path_table_sha256": sha_array(path_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    grammar = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar@1",
        "object": "d20",
        "comparison_rule": {
            "parent": SYMBOLIC_WINDOW_REPORT.relative_to(ROOT).as_posix(),
            "global_rule": [
                "enumerate every four-symbol block over the six-symbol alphabet",
                "let endpoint windows be indices 012 and 123",
                "let skip windows be indices 013 and 023",
                "accept a repair split when both rewrite edges endpoint->skip->endpoint exist and one split edge is 31--28 or 50--34",
            ],
            "language_test": [
                "use the certified radius-three boundary-pair word union",
                "filter to delta_twice=2, variation<=223, and closed positivity",
                "admit native repair words or words containing a derived repair split",
            ],
        },
        "summary": {
            "repair_split_count": observable_values["repair_split_count"],
            "grammar_good_cell_count": observable_values["grammar_good_cell_count"],
            "left_to_right_path_exists": observable_values[
                "left_to_right_path_exists"
            ],
            "shortest_path_length": observable_values["shortest_path_length"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_SKIP_WINDOW_GRAMMAR_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the local skip-window repair is promoted to a 32-split global grammar over all four-symbol blocks",
            "the grammar has balanced 31--28 and 50--34 repair support",
            "on the boundary-pair union the grammar admits 846 closed-positive cells",
            "284 closed-positive cells are derived-only, including the no-repair gate",
            "the grammar-good graph reconnects the left and right boundary cells through the gate word",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The skip-window grammar layer promotes the local 3,2,1,4 "
            "repair into a global four-symbol rule. Across all 1,296 "
            "four-symbol blocks there are 1,800 valid skip-window splits and "
            "32 repair splits, balanced as 16 for 31--28 and 16 for 50--34. "
            "Applying this grammar to the certified radius-three boundary-pair "
            "word union leaves 26,197 metric-valid words and admits 846 "
            "closed-positive grammar cells. Of these, 284 are derived-only. "
            "The grammar-good graph has 846 cells, 2,549 edges, and 22 "
            "components; the left and right boundary cells merge into a "
            "787-cell component through the shortest path left boundary -> "
            "gate -> right boundary. The gate remains native-repair-free but "
            "is grammar-derived, with 30 closed paths and 9 templates."
        ),
        "stage_protocol": {
            "draft": "globalize the local skip-window repair into a four-symbol grammar",
            "witness": "enumerate repair split rows and apply them to the boundary-pair word union",
            "coherence": "compare native repair support, derived repair support, and boundary graph connectivity",
            "closure": "certify that the grammar closes the boundary path language through the derived gate",
            "emit": "emit grammar, cell, component, path, observable tables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "symbolic_window_report": input_entry(
                SYMBOLIC_WINDOW_REPORT,
                {
                    "status": symbolic_report.get("status"),
                    "certificate_sha256": symbolic_report.get("certificate_sha256"),
                },
            ),
            "symbolic_window_certificate": input_entry(SYMBOLIC_WINDOW_CERTIFICATE),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "symbolic_associativity": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "rewrite_complex_nodes": input_entry(REWRITE_COMPLEX_NODES),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_skip_window_grammar": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar.json"
            ),
            "aperture_closure_tail_skip_window_repair_splits_csv": relpath(
                OUT_DIR / "aperture_closure_tail_skip_window_repair_splits.csv"
            ),
            "aperture_closure_tail_skip_window_cells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_skip_window_cells.csv"
            ),
            "aperture_closure_tail_skip_window_components_csv": relpath(
                OUT_DIR / "aperture_closure_tail_skip_window_components.csv"
            ),
            "aperture_closure_tail_skip_window_path_csv": relpath(
                OUT_DIR / "aperture_closure_tail_skip_window_path.csv"
            ),
            "aperture_closure_tail_skip_window_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_skip_window_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all four-symbol blocks over the six-symbol alphabet",
                "all repair-bearing skip-window splits",
                "the grammar-good cells in the certified radius-three boundary-pair union",
                "left/right boundary reconnection under the derived-window grammar",
            ],
            "does_not_certify_because_not_required": [
                "boundary words outside the declared radius-three side union",
                "compiler implementation of derived-window rules",
                "multi-window closure beyond one repair split per span",
                "global optimality of the derived grammar",
            ],
        },
        "next_highest_yield_item": (
            "Compile the skip-window grammar into an explicit automaton: add "
            "derived repair transitions to the symbolic language graph and "
            "measure the new recurrent classes, spectral cut, and Poincare "
            "geometry of the repaired boundary language."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified symbolic-window artifacts",
            "enumerate all repair-bearing four-symbol skip-window splits",
            "apply grammar to radius-three boundary-pair word union",
            "check grammar-good graph connectivity and gate path",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_skip_window_grammar": grammar,
        "aperture_closure_tail_skip_window_repair_splits_csv": csv_text(
            REPAIR_SPLIT_COLUMNS,
            repair_rows,
        ),
        "aperture_closure_tail_skip_window_cells_csv": csv_text(
            CELL_COLUMNS,
            cell_rows,
        ),
        "aperture_closure_tail_skip_window_components_csv": csv_text(
            COMPONENT_COLUMNS,
            component_rows,
        ),
        "aperture_closure_tail_skip_window_path_csv": csv_text(
            PATH_COLUMNS,
            path_rows,
        ),
        "aperture_closure_tail_skip_window_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "repair_split_table": repair_split_table,
        "cell_table": cell_table,
        "component_table": component_table,
        "path_table": path_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_skip_window_grammar"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_skip_window_repair_splits.csv").write_text(
        payloads["aperture_closure_tail_skip_window_repair_splits_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_skip_window_cells.csv").write_text(
        payloads["aperture_closure_tail_skip_window_cells_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_skip_window_components.csv").write_text(
        payloads["aperture_closure_tail_skip_window_components_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_skip_window_path.csv").write_text(
        payloads["aperture_closure_tail_skip_window_path_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_skip_window_observables.csv").write_text(
        payloads["aperture_closure_tail_skip_window_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_tables.npz",
        repair_split_table=payloads["repair_split_table"],
        cell_table=payloads["cell_table"],
        component_table=payloads["component_table"],
        path_table=payloads["path_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate"
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
