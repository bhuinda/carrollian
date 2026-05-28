from __future__ import annotations

import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        contains_undirected_edge,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor import (
        CELL_COMPLEX_EDGES,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        MIN_WORD_LENGTH,
        OBSERVABLE_COLUMNS,
        PREFIX_FIXED,
        REWRITE_COMPLEX_EDGES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_CLOSED_PATH_COUNT,
        TARGET_DELTA_TWICE,
        TARGET_TEMPLATE_COUNT,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        endpoint_counts,
        load_json,
        padded,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search import (
        LEFT_REPAIR_BOUNDARY_WORD,
        NO_REPAIR_GATE_WORD,
        OUT_DIR as GATE_REPAIR_DIR,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as GATE_REPAIR_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        associativity_lookup,
        build_trace,
        csv_text,
        edge_key,
        read_int_csv,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search import (
        one_edit_neighbors,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        contains_undirected_edge,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor import (
        CELL_COMPLEX_EDGES,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        MIN_WORD_LENGTH,
        OBSERVABLE_COLUMNS,
        PREFIX_FIXED,
        REWRITE_COMPLEX_EDGES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_CLOSED_PATH_COUNT,
        TARGET_DELTA_TWICE,
        TARGET_TEMPLATE_COUNT,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        endpoint_counts,
        load_json,
        padded,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search import (
        LEFT_REPAIR_BOUNDARY_WORD,
        NO_REPAIR_GATE_WORD,
        OUT_DIR as GATE_REPAIR_DIR,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as GATE_REPAIR_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        associativity_lookup,
        build_trace,
        csv_text,
        edge_key,
        read_int_csv,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search import (
        one_edit_neighbors,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_BOUNDARY_BRIDGE_SEARCH_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

GATE_REPAIR_REPORT = GATE_REPAIR_DIR / "report.json"
GATE_REPAIR_CERTIFICATE = (
    GATE_REPAIR_DIR
    / "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate.json"
)
DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search.py"
)

MAX_SIDE_EDIT_RADIUS = 3

CELL_COLUMNS = [
    "boundary_bridge_cell_id",
    "component_id",
    "left_edit_radius",
    "right_edit_radius",
    "word_length",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "all_four_lift_flag",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
    "clear_flag",
    "exact24_six_all_four_flag",
    "left_boundary_flag",
    "right_boundary_flag",
    "left_neighbor_flag",
    "right_neighbor_flag",
]

COMPONENT_COLUMNS = [
    "component_id",
    "component_kind_code",
    "cell_count",
    "edge_count",
    "left_boundary_flag",
    "right_boundary_flag",
    "target_cell_count",
    "clear_cell_count",
    "endpoint13_heavy_cell_count",
    "min_variation",
    "min_target_variation",
    "max_endpoint13_path_count",
    "min_left_edit_radius",
    "min_right_edit_radius",
    "left_to_right_bridge_flag",
]

STRICT_COLUMNS = [
    "strict_candidate_id",
    "left_cell_id",
    "right_cell_id",
    "left_variation",
    "right_variation",
    "left_closed_path_count",
    "right_closed_path_count",
    "left_template_count",
    "right_template_count",
]

BRIDGE_OBSERVABLE_CODES = {
    "left_radius0_word_count": 0,
    "left_radius1_word_count": 1,
    "left_radius2_word_count": 2,
    "left_radius3_word_count": 3,
    "right_radius0_word_count": 4,
    "right_radius1_word_count": 5,
    "right_radius2_word_count": 6,
    "right_radius3_word_count": 7,
    "left_total_word_count": 8,
    "right_total_word_count": 9,
    "union_word_count": 10,
    "intersection_word_count": 11,
    "trace_valid_word_count": 12,
    "delta2_variation_le223_word_count": 13,
    "repair_chord_candidate_count": 14,
    "no_repair_candidate_count": 15,
    "no_closed_repair_candidate_count": 16,
    "good_cell_count": 17,
    "good_edge_count": 18,
    "good_component_count": 19,
    "left_component_cell_count": 20,
    "right_component_cell_count": 21,
    "target_cell_count": 22,
    "left_component_target_count": 23,
    "right_component_target_count": 24,
    "min_target_variation": 25,
    "clear_cell_count": 26,
    "left_neighbor_good_count": 27,
    "right_neighbor_good_count": 28,
    "strict_two_cell_bridge_count": 29,
    "left_to_right_good_path_exists": 30,
}


def radius_from(seed: tuple[int, ...], max_radius: int) -> dict[tuple[int, ...], int]:
    radius_by_word = {seed: 0}
    frontier = {seed}
    for radius in range(1, max_radius + 1):
        next_frontier = set()
        for word in frontier:
            for neighbor in one_edit_neighbors(word):
                if (
                    MIN_WORD_LENGTH <= len(neighbor) <= MAX_WORD_LENGTH
                    and neighbor[: len(PREFIX_FIXED)] == PREFIX_FIXED
                    and neighbor not in radius_by_word
                ):
                    radius_by_word[neighbor] = radius
                    next_frontier.add(neighbor)
        frontier = next_frontier
    return radius_by_word


def build_context() -> tuple[Any, Any, Any]:
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    carrier_adjacency, _carriers = build_carrier_adjacency(
        read_int_csv(CELL_COMPLEX_EDGES),
        atom_to_symbol,
    )
    assoc_by_word = associativity_lookup(read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV))
    rewrite_edge_by_pair = {
        edge_key(row["source_node_id"], row["target_node_id"]): row
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }
    return carrier_adjacency, assoc_by_word, rewrite_edge_by_pair


def closure_profile(word: tuple[int, ...], carrier_adjacency: Any) -> dict[str, int]:
    states = carrier_paths(word, carrier_adjacency)
    closed_states = first_return_closed(states)
    if not closed_states:
        return {
            "first_return_closed_path_count": 0,
            "normalized_tail_template_count": 0,
            "template_lift_count_min": 0,
            "template_lift_count_max": 0,
            "all_four_lift_flag": 0,
            "tail_entry_9_path_count": 0,
            "tail_entry_10_path_count": 0,
            "tail_entry_11_path_count": 0,
            "tail_entry_13_path_count": 0,
        }
    templates = Counter(tail_slices(state, max(0, len(word) - 5)) for state in closed_states)
    lift_counts = sorted(int(value) for value in templates.values())
    endpoints = endpoint_counts(templates)
    return {
        "first_return_closed_path_count": len(closed_states),
        "normalized_tail_template_count": len(templates),
        "template_lift_count_min": min(lift_counts),
        "template_lift_count_max": max(lift_counts),
        "all_four_lift_flag": int(all(value == 4 for value in lift_counts)),
        "tail_entry_9_path_count": endpoints[9],
        "tail_entry_10_path_count": endpoints[10],
        "tail_entry_11_path_count": endpoints[11],
        "tail_entry_13_path_count": endpoints[13],
    }


def evaluate_words() -> tuple[
    dict[tuple[int, ...], dict[str, Any]],
    dict[str, int],
    dict[tuple[int, ...], int],
    dict[tuple[int, ...], int],
]:
    left_radius = radius_from(LEFT_REPAIR_BOUNDARY_WORD, MAX_SIDE_EDIT_RADIUS)
    right_radius = radius_from(RIGHT_REPAIR_BOUNDARY_WORD, MAX_SIDE_EDIT_RADIUS)
    candidate_words = set(left_radius) | set(right_radius)
    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()

    stats: Counter[str] = Counter()
    for radius in range(MAX_SIDE_EDIT_RADIUS + 1):
        stats[f"left_radius{radius}_word_count"] = sum(
            int(value == radius) for value in left_radius.values()
        )
        stats[f"right_radius{radius}_word_count"] = sum(
            int(value == radius) for value in right_radius.values()
        )
    stats["left_total_word_count"] = len(left_radius)
    stats["right_total_word_count"] = len(right_radius)
    stats["union_word_count"] = len(candidate_words)
    stats["intersection_word_count"] = len(set(left_radius) & set(right_radius))

    rows: dict[tuple[int, ...], dict[str, Any]] = {}
    for word in sorted(candidate_words):
        row: dict[str, Any] = {
            "word": word,
            "left_edit_radius": left_radius.get(word, 99),
            "right_edit_radius": right_radius.get(word, 99),
        }
        try:
            _raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
        except Exception:
            stats["trace_failure_count"] += 1
            row["class"] = "trace_failure"
            rows[word] = row
            continue
        stats["trace_valid_word_count"] += 1
        trace = tuple(int(value) for value in trace_nodes)
        variation = int(metrics["trace_signature_total_variation"])
        delta_twice = int(metrics["metric_gromov_delta_twice"])
        has_repair = contains_undirected_edge(
            trace,
            31,
            28,
        ) or contains_undirected_edge(trace, 50, 34)
        row.update(
            {
                "trace": trace,
                "trace_signature_total_variation": variation,
                "metric_gromov_delta_twice": delta_twice,
                "repair_chord_flag": int(has_repair),
            }
        )
        if (
            delta_twice != TARGET_DELTA_TWICE
            or variation > TARGET_VARIATION_INCLUSIVE_BOUND
        ):
            stats["bad_metric_word_count"] += 1
            row["class"] = "bad_metric"
            rows[word] = row
            continue
        stats["delta2_variation_le223_word_count"] += 1
        if not has_repair:
            stats["no_repair_candidate_count"] += 1
            row["class"] = "no_repair"
            rows[word] = row
            continue
        stats["repair_chord_candidate_count"] += 1
        row.update(closure_profile(word, carrier_adjacency))
        if row["first_return_closed_path_count"] == 0:
            stats["no_closed_repair_candidate_count"] += 1
            row["class"] = "no_closed"
            rows[word] = row
            continue
        row["exact24_six_all_four_flag"] = int(
            row["first_return_closed_path_count"] == TARGET_CLOSED_PATH_COUNT
            and row["normalized_tail_template_count"] == TARGET_TEMPLATE_COUNT
            and row["all_four_lift_flag"] == 1
            and row["tail_entry_13_path_count"] == 0
        )
        row["clear_flag"] = int(
            row["all_four_lift_flag"] == 1
            and row["tail_entry_13_path_count"] == 0
            and row["first_return_closed_path_count"] >= TARGET_CLOSED_PATH_COUNT
        )
        stats["good_cell_count"] += 1
        row["class"] = "good"
        rows[word] = row
    return rows, dict(stats), left_radius, right_radius


def build_good_graph(
    rows: dict[tuple[int, ...], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, int]], dict[tuple[int, ...], int], int]:
    good_words = sorted(
        [word for word, row in rows.items() if row.get("class") == "good"],
        key=lambda word: (
            min(rows[word]["left_edit_radius"], rows[word]["right_edit_radius"]),
            rows[word]["trace_signature_total_variation"],
            len(word),
            word,
        ),
    )
    cell_id_by_word = {word: index for index, word in enumerate(good_words)}
    adjacency: dict[int, set[int]] = {index: set() for index in range(len(good_words))}
    edge_count = 0
    seen_edges = set()
    for word in good_words:
        source_id = cell_id_by_word[word]
        for neighbor in one_edit_neighbors(word):
            target_id = cell_id_by_word.get(neighbor)
            if target_id is None:
                continue
            edge = tuple(sorted((source_id, target_id)))
            if edge not in seen_edges:
                seen_edges.add(edge)
                edge_count += 1
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

    def component_sort_key(component: set[int]) -> tuple[int, int, int]:
        words = {good_words[cell_id] for cell_id in component}
        if LEFT_REPAIR_BOUNDARY_WORD in words:
            kind = 0
        elif RIGHT_REPAIR_BOUNDARY_WORD in words:
            kind = 1
        else:
            kind = 2
        min_variation = min(
            rows[good_words[cell_id]]["trace_signature_total_variation"]
            for cell_id in component
        )
        return (kind, -len(component), min_variation)

    components = sorted(components, key=component_sort_key)
    component_id_by_cell: dict[int, int] = {}
    for component_id, component in enumerate(components):
        for cell_id in component:
            component_id_by_cell[cell_id] = component_id

    cell_rows = []
    for word in good_words:
        cell_id = cell_id_by_word[word]
        row = rows[word]
        cell_rows.append(
            {
                "boundary_bridge_cell_id": cell_id,
                "component_id": component_id_by_cell[cell_id],
                "left_edit_radius": row["left_edit_radius"],
                "right_edit_radius": row["right_edit_radius"],
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        WORD_COLUMNS,
                        padded(word, MAX_WORD_LENGTH),
                    )
                },
                "trace_node_count": len(row["trace"]),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(row["trace"], MAX_TRACE_NODES),
                    )
                },
                "metric_gromov_delta_twice": row["metric_gromov_delta_twice"],
                "trace_signature_total_variation": row[
                    "trace_signature_total_variation"
                ],
                "first_return_closed_path_count": row[
                    "first_return_closed_path_count"
                ],
                "normalized_tail_template_count": row[
                    "normalized_tail_template_count"
                ],
                "template_lift_count_min": row["template_lift_count_min"],
                "template_lift_count_max": row["template_lift_count_max"],
                "all_four_lift_flag": row["all_four_lift_flag"],
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "tail_entry_13_path_count": row["tail_entry_13_path_count"],
                "clear_flag": row["clear_flag"],
                "exact24_six_all_four_flag": row["exact24_six_all_four_flag"],
                "left_boundary_flag": int(word == LEFT_REPAIR_BOUNDARY_WORD),
                "right_boundary_flag": int(word == RIGHT_REPAIR_BOUNDARY_WORD),
                "left_neighbor_flag": int(
                    word != NO_REPAIR_GATE_WORD
                    and word in set(one_edit_neighbors(LEFT_REPAIR_BOUNDARY_WORD))
                ),
                "right_neighbor_flag": int(
                    word != NO_REPAIR_GATE_WORD
                    and word in set(one_edit_neighbors(RIGHT_REPAIR_BOUNDARY_WORD))
                ),
            }
        )

    cell_by_id = {row["boundary_bridge_cell_id"]: row for row in cell_rows}
    component_rows = []
    for component_id, component in enumerate(components):
        cells = [cell_by_id[cell_id] for cell_id in sorted(component)]
        words = {
            tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)
            for row in cells
        }
        left_flag = int(LEFT_REPAIR_BOUNDARY_WORD in words)
        right_flag = int(RIGHT_REPAIR_BOUNDARY_WORD in words)
        if left_flag:
            kind = 0
        elif right_flag:
            kind = 1
        else:
            kind = 2
        edge_count_in_component = 0
        for word in words:
            for neighbor in one_edit_neighbors(word):
                if neighbor in words and word < neighbor:
                    edge_count_in_component += 1
        target_rows = [row for row in cells if row["exact24_six_all_four_flag"] == 1]
        component_rows.append(
            {
                "component_id": component_id,
                "component_kind_code": kind,
                "cell_count": len(cells),
                "edge_count": edge_count_in_component,
                "left_boundary_flag": left_flag,
                "right_boundary_flag": right_flag,
                "target_cell_count": len(target_rows),
                "clear_cell_count": sum(row["clear_flag"] for row in cells),
                "endpoint13_heavy_cell_count": sum(
                    int(row["tail_entry_13_path_count"] > 0) for row in cells
                ),
                "min_variation": min(
                    row["trace_signature_total_variation"] for row in cells
                ),
                "min_target_variation": min(
                    [row["trace_signature_total_variation"] for row in target_rows]
                    or [-1]
                ),
                "max_endpoint13_path_count": max(
                    row["tail_entry_13_path_count"] for row in cells
                ),
                "min_left_edit_radius": min(row["left_edit_radius"] for row in cells),
                "min_right_edit_radius": min(row["right_edit_radius"] for row in cells),
                "left_to_right_bridge_flag": int(left_flag and right_flag),
            }
        )
    return cell_rows, component_rows, cell_id_by_word, edge_count


def strict_bridge_rows(
    cell_rows: list[dict[str, int]],
    cell_id_by_word: dict[tuple[int, ...], int],
) -> list[dict[str, int]]:
    rows_by_word = {
        tuple(row[column] for column in WORD_COLUMNS if row[column] != -1): row
        for row in cell_rows
    }
    left_neighbor_words = [
        word
        for word, row in rows_by_word.items()
        if row["left_neighbor_flag"] == 1
    ]
    right_neighbor_words = {
        word
        for word, row in rows_by_word.items()
        if row["right_neighbor_flag"] == 1
    }
    rows = []
    for left_word in left_neighbor_words:
        for right_word in one_edit_neighbors(left_word):
            if right_word not in right_neighbor_words:
                continue
            left_row = rows_by_word[left_word]
            right_row = rows_by_word[right_word]
            rows.append(
                {
                    "strict_candidate_id": len(rows),
                    "left_cell_id": cell_id_by_word[left_word],
                    "right_cell_id": cell_id_by_word[right_word],
                    "left_variation": left_row["trace_signature_total_variation"],
                    "right_variation": right_row["trace_signature_total_variation"],
                    "left_closed_path_count": left_row[
                        "first_return_closed_path_count"
                    ],
                    "right_closed_path_count": right_row[
                        "first_return_closed_path_count"
                    ],
                    "left_template_count": left_row[
                        "normalized_tail_template_count"
                    ],
                    "right_template_count": right_row[
                        "normalized_tail_template_count"
                    ],
                }
            )
    return rows


def build_payload_rows() -> dict[str, Any]:
    rows, stats, left_radius, right_radius = evaluate_words()
    cell_rows, component_rows, cell_id_by_word, good_edge_count = build_good_graph(rows)
    strict_rows = strict_bridge_rows(cell_rows, cell_id_by_word)
    left_component = next(row for row in component_rows if row["left_boundary_flag"] == 1)
    right_component = next(
        row for row in component_rows if row["right_boundary_flag"] == 1
    )
    target_rows = [row for row in cell_rows if row["exact24_six_all_four_flag"] == 1]
    observable_values = {
        "left_radius0_word_count": sum(int(value == 0) for value in left_radius.values()),
        "left_radius1_word_count": sum(int(value == 1) for value in left_radius.values()),
        "left_radius2_word_count": sum(int(value == 2) for value in left_radius.values()),
        "left_radius3_word_count": sum(int(value == 3) for value in left_radius.values()),
        "right_radius0_word_count": sum(int(value == 0) for value in right_radius.values()),
        "right_radius1_word_count": sum(int(value == 1) for value in right_radius.values()),
        "right_radius2_word_count": sum(int(value == 2) for value in right_radius.values()),
        "right_radius3_word_count": sum(int(value == 3) for value in right_radius.values()),
        "left_total_word_count": stats["left_total_word_count"],
        "right_total_word_count": stats["right_total_word_count"],
        "union_word_count": stats["union_word_count"],
        "intersection_word_count": stats["intersection_word_count"],
        "trace_valid_word_count": stats["trace_valid_word_count"],
        "delta2_variation_le223_word_count": stats[
            "delta2_variation_le223_word_count"
        ],
        "repair_chord_candidate_count": stats["repair_chord_candidate_count"],
        "no_repair_candidate_count": stats["no_repair_candidate_count"],
        "no_closed_repair_candidate_count": stats[
            "no_closed_repair_candidate_count"
        ],
        "good_cell_count": len(cell_rows),
        "good_edge_count": good_edge_count,
        "good_component_count": len(component_rows),
        "left_component_cell_count": left_component["cell_count"],
        "right_component_cell_count": right_component["cell_count"],
        "target_cell_count": len(target_rows),
        "left_component_target_count": left_component["target_cell_count"],
        "right_component_target_count": right_component["target_cell_count"],
        "min_target_variation": min(
            row["trace_signature_total_variation"] for row in target_rows
        ),
        "clear_cell_count": sum(row["clear_flag"] for row in cell_rows),
        "left_neighbor_good_count": sum(row["left_neighbor_flag"] for row in cell_rows),
        "right_neighbor_good_count": sum(row["right_neighbor_flag"] for row in cell_rows),
        "strict_two_cell_bridge_count": len(strict_rows),
        "left_to_right_good_path_exists": int(
            left_component["component_id"] == right_component["component_id"]
        ),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": BRIDGE_OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    return {
        "observable_values": observable_values,
        "cell_rows": cell_rows,
        "component_rows": component_rows,
        "strict_rows": strict_rows,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    gate_report = load_json(GATE_REPAIR_REPORT)
    gate_certificate = load_json(GATE_REPAIR_CERTIFICATE)
    payload_rows = build_payload_rows()
    observable_values = payload_rows["observable_values"]
    cell_rows = payload_rows["cell_rows"]
    component_rows = payload_rows["component_rows"]
    strict_rows = payload_rows["strict_rows"]
    observable_rows = payload_rows["observable_rows"]

    cell_table = table_from_rows(CELL_COLUMNS, cell_rows)
    component_table = table_from_rows(COMPONENT_COLUMNS, component_rows)
    strict_table = (
        table_from_rows(STRICT_COLUMNS, strict_rows)
        if strict_rows
        else np.empty((0, len(STRICT_COLUMNS)), dtype=np.int64)
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    left_component = next(row for row in component_rows if row["left_boundary_flag"] == 1)
    right_component = next(
        row for row in component_rows if row["right_boundary_flag"] == 1
    )
    checks = {
        "gate_repair_report_certified": gate_report.get("status")
        == GATE_REPAIR_STATUS,
        "gate_repair_certificate_certified": gate_certificate.get("status")
        == GATE_REPAIR_STATUS,
        "left_shell_counts_are_expected": [
            observable_values["left_radius0_word_count"],
            observable_values["left_radius1_word_count"],
            observable_values["left_radius2_word_count"],
            observable_values["left_radius3_word_count"],
        ]
        == [1, 103, 4_810, 136_869],
        "right_shell_counts_are_expected": [
            observable_values["right_radius0_word_count"],
            observable_values["right_radius1_word_count"],
            observable_values["right_radius2_word_count"],
            observable_values["right_radius3_word_count"],
        ]
        == [1, 94, 3_971, 101_567],
        "union_and_intersection_counts_are_expected": (
            observable_values["left_total_word_count"],
            observable_values["right_total_word_count"],
            observable_values["union_word_count"],
            observable_values["intersection_word_count"],
        )
        == (141_783, 105_633, 234_678, 12_738),
        "trace_valid_word_count_is_166575": observable_values[
            "trace_valid_word_count"
        ]
        == 166_575,
        "delta2_variation_le223_word_count_is_26197": observable_values[
            "delta2_variation_le223_word_count"
        ]
        == 26_197,
        "repair_chord_candidate_count_is_11637": observable_values[
            "repair_chord_candidate_count"
        ]
        == 11_637,
        "good_cell_count_is_562": observable_values["good_cell_count"] == 562,
        "good_edge_count_is_1694": observable_values["good_edge_count"] == 1_694,
        "good_components_are_expected": [
            row["cell_count"] for row in component_rows
        ]
        == [347, 185, 15, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1],
        "left_and_right_components_are_separate": observable_values[
            "left_to_right_good_path_exists"
        ]
        == 0,
        "strict_two_cell_bridge_count_is_zero": len(strict_rows) == 0,
        "neighbor_counts_are_8_and_6": (
            observable_values["left_neighbor_good_count"],
            observable_values["right_neighbor_good_count"],
        )
        == (8, 6),
        "targets_are_left_component_except_one_orphan": observable_values[
            "target_cell_count"
        ]
        == 19
        and left_component["target_cell_count"] == 18
        and right_component["target_cell_count"] == 0,
        "min_target_variation_is_137": observable_values["min_target_variation"]
        == 137,
        "cell_table_shape_matches_codebook": tuple(cell_table.shape)
        == (562, len(CELL_COLUMNS)),
        "component_table_shape_matches_codebook": tuple(component_table.shape)
        == (13, len(COMPONENT_COLUMNS)),
        "strict_table_shape_matches_codebook": tuple(strict_table.shape)
        == (0, len(STRICT_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(BRIDGE_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    target_rows = [row for row in cell_rows if row["exact24_six_all_four_flag"] == 1]
    witness = {
        "left_boundary_word": list(LEFT_REPAIR_BOUNDARY_WORD),
        "right_boundary_word": list(RIGHT_REPAIR_BOUNDARY_WORD),
        "left_shell_counts": [
            observable_values["left_radius0_word_count"],
            observable_values["left_radius1_word_count"],
            observable_values["left_radius2_word_count"],
            observable_values["left_radius3_word_count"],
        ],
        "right_shell_counts": [
            observable_values["right_radius0_word_count"],
            observable_values["right_radius1_word_count"],
            observable_values["right_radius2_word_count"],
            observable_values["right_radius3_word_count"],
        ],
        "union_word_count": observable_values["union_word_count"],
        "intersection_word_count": observable_values["intersection_word_count"],
        "good_cell_count": observable_values["good_cell_count"],
        "good_component_sizes": [row["cell_count"] for row in component_rows],
        "left_component_id": left_component["component_id"],
        "right_component_id": right_component["component_id"],
        "strict_two_cell_bridge_count": len(strict_rows),
        "target_count": len(target_rows),
        "left_component_target_count": left_component["target_cell_count"],
        "right_component_target_count": right_component["target_cell_count"],
        "min_target_variation": observable_values["min_target_variation"],
        "cell_table_sha256": sha_array(cell_table),
        "component_table_sha256": sha_array(component_table),
        "strict_table_sha256": sha_array(strict_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    bridge = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search@1",
        "object": "d20",
        "comparison_rule": {
            "parent": GATE_REPAIR_REPORT.relative_to(ROOT).as_posix(),
            "left_boundary_word": list(LEFT_REPAIR_BOUNDARY_WORD),
            "right_boundary_word": list(RIGHT_REPAIR_BOUNDARY_WORD),
            "radius": MAX_SIDE_EDIT_RADIUS,
            "strict_two_cell_bridge": [
                "left boundary -> repaired left neighbor",
                "repaired left neighbor -> repaired right neighbor",
                "repaired right neighbor -> right boundary",
            ],
            "good_cell_filters": [
                "word starts with x2,x1",
                "8 <= word_length <= 16",
                "metric_gromov_delta_twice = 2",
                "trace_signature_total_variation <= 223",
                "trace contains repair chord 31--28 or 50--34",
                "first_return_closed_path_count > 0",
            ],
        },
        "summary": {
            "good_cell_count": observable_values["good_cell_count"],
            "good_component_count": len(component_rows),
            "strict_two_cell_bridge_count": len(strict_rows),
            "target_cell_count": len(target_rows),
            "left_to_right_good_path_exists": observable_values[
                "left_to_right_good_path_exists"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_BOUNDARY_BRIDGE_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "radius-three side neighborhoods around the left and right repair boundaries cover 234678 union words",
            "562 words are closed-positive good cells after delta2, variation<=223, and repair-chord filters",
            "the good-cell graph has 13 components; the left and right boundary components have sizes 347 and 185",
            "there is no strict two-cell good bridge from the left boundary to the right boundary",
            "exact 24/six/all-four targets remain on the left side except for one orphan target, and none occur in the right boundary component",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The boundary-pair bridge search expands radius-three side "
            "neighborhoods around the left and right repair-boundary words. "
            "The union contains 234,678 prefix-valid words, including 562 "
            "closed-positive good cells and 1,694 good edges. The good graph "
            "has 13 components; the left and right boundary components have "
            "sizes 347 and 185 and remain separate. The strict two-cell bridge "
            "left -> A -> B -> right has zero good realizations, despite 8 "
            "good left-neighbor cells and 6 good right-neighbor cells. There "
            "are 19 exact 24-closure, six-template, all-four targets at "
            "minimum variation 137, but 18 lie in the left component and none "
            "lie in the right component."
        ),
        "stage_protocol": {
            "draft": "expand side neighborhoods around the left and right repair-boundary words",
            "witness": "evaluate good cells, strict two-cell candidates, components, and exact target locations",
            "coherence": "compare left and right boundary components and neighbor bridge candidates",
            "closure": "certify no strict two-cell good bridge and no left/right good-component merger through radius three",
            "emit": "emit bridge cells, components, strict bridge table, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "gate_repair_report": input_entry(
                GATE_REPAIR_REPORT,
                {
                    "status": gate_report.get("status"),
                    "certificate_sha256": gate_report.get("certificate_sha256"),
                },
            ),
            "gate_repair_certificate": input_entry(GATE_REPAIR_CERTIFICATE),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "symbolic_associativity": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search.json"
            ),
            "aperture_closure_tail_boundary_bridge_cells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_boundary_bridge_cells.csv"
            ),
            "aperture_closure_tail_boundary_bridge_components_csv": relpath(
                OUT_DIR / "aperture_closure_tail_boundary_bridge_components.csv"
            ),
            "aperture_closure_tail_boundary_bridge_strict_candidates_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_boundary_bridge_strict_candidates.csv"
            ),
            "aperture_closure_tail_boundary_bridge_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_boundary_bridge_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "radius-three side neighborhoods around both repair-boundary words",
                "all good cells satisfying delta2, variation <= 223, repair-chord support, and closed positivity in the side-neighborhood union",
                "that no strict two-cell good bridge exists between the boundary words",
                "that no good path connects the left and right boundary components through radius three",
            ],
            "does_not_certify_because_not_required": [
                "side radius four or higher",
                "bridges using no-repair, no-closed, bad-metric, or trace-failure gates",
                "multi-cell grafts longer than the declared strict two-cell bridge",
                "global optimality outside the declared boundary-pair search",
            ],
        },
        "next_highest_yield_item": (
            "Move from word edits to explicit chord grafting: add a virtual "
            "31--28 or 50--34 repair edge to the boundary-pair traces and test "
            "which graft changes component membership without destroying "
            "closed-path/template counts."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified gate-repair artifacts",
            "enumerate radius-three side neighborhoods around both repair-boundary words",
            "classify good cells, strict bridge candidates, and connected components",
            "check left/right separation and exact target locations",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search": bridge,
        "aperture_closure_tail_boundary_bridge_cells_csv": csv_text(
            CELL_COLUMNS,
            cell_rows,
        ),
        "aperture_closure_tail_boundary_bridge_components_csv": csv_text(
            COMPONENT_COLUMNS,
            component_rows,
        ),
        "aperture_closure_tail_boundary_bridge_strict_candidates_csv": csv_text(
            STRICT_COLUMNS,
            strict_rows,
        ),
        "aperture_closure_tail_boundary_bridge_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "cell_table": cell_table,
        "component_table": component_table,
        "strict_table": strict_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_boundary_bridge_cells.csv").write_text(
        payloads["aperture_closure_tail_boundary_bridge_cells_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_boundary_bridge_components.csv").write_text(
        payloads["aperture_closure_tail_boundary_bridge_components_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_boundary_bridge_strict_candidates.csv"
    ).write_text(
        payloads["aperture_closure_tail_boundary_bridge_strict_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_boundary_bridge_observables.csv").write_text(
        payloads["aperture_closure_tail_boundary_bridge_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_tables.npz",
        cell_table=payloads["cell_table"],
        component_table=payloads["component_table"],
        strict_table=payloads["strict_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate"
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
