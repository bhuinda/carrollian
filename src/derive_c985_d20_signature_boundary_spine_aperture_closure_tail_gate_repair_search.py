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
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2 import (
        OUT_DIR as LEVEL2_DIR,
        STATUS as LEVEL2_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
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
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2 import (
        OUT_DIR as LEVEL2_DIR,
        STATUS as LEVEL2_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
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
    "c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_GATE_REPAIR_SEARCH_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

LEVEL2_REPORT = LEVEL2_DIR / "report.json"
LEVEL2_CERTIFICATE = (
    LEVEL2_DIR
    / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate.json"
)
DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search.py"
)

NO_REPAIR_GATE_WORD = (2, 1, 4, 5, 1, 2, 5, 5, 2, 1, 4, 5)
LEFT_REPAIR_BOUNDARY_WORD = (2, 1, 3, 4, 5, 1, 2, 5, 5, 2, 1, 4, 5)
RIGHT_REPAIR_BOUNDARY_WORD = (2, 1, 4, 3, 1, 2, 5, 5, 2, 1, 4, 5)
MAX_GATE_EDIT_RADIUS = 3

CELL_COLUMNS = [
    "gate_repair_cell_id",
    "component_id",
    "gate_edit_radius",
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
    "left_to_right_bridge_flag",
]

BRIDGE_COLUMNS = [
    "bridge_step_index",
    "word_class_code",
    "gate_flag",
    "gate_edit_radius",
    "component_id",
    "word_length",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "repair_chord_flag",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "all_four_lift_flag",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
]

GATE_OBSERVABLE_CODES = {
    "radius0_word_count": 0,
    "radius1_word_count": 1,
    "radius2_word_count": 2,
    "radius3_word_count": 3,
    "gate_neighborhood_total_word_count": 4,
    "trace_valid_word_count": 5,
    "delta2_variation_le223_word_count": 6,
    "repair_chord_candidate_count": 7,
    "no_repair_candidate_count": 8,
    "no_closed_repair_candidate_count": 9,
    "good_cell_count": 10,
    "good_edge_count": 11,
    "good_component_count": 12,
    "left_component_cell_count": 13,
    "right_component_cell_count": 14,
    "target_cell_count": 15,
    "left_component_target_count": 16,
    "right_component_target_count": 17,
    "min_target_variation": 18,
    "clear_cell_count": 19,
    "left_to_right_good_path_exists": 20,
    "one_no_repair_gate_bridge_exists": 21,
    "gate_word_variation": 22,
    "gate_word_closed_paths": 23,
    "gate_word_template_count": 24,
}


def radius_words() -> dict[tuple[int, ...], int]:
    radius_by_word = {NO_REPAIR_GATE_WORD: 0}
    frontier = {NO_REPAIR_GATE_WORD}
    for radius in range(1, MAX_GATE_EDIT_RADIUS + 1):
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


def evaluate_words() -> tuple[dict[tuple[int, ...], dict[str, Any]], dict[str, int]]:
    radius_by_word = radius_words()
    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()
    stats: Counter[str] = Counter()
    for radius in range(MAX_GATE_EDIT_RADIUS + 1):
        stats[f"radius{radius}_word_count"] = sum(
            int(value == radius) for value in radius_by_word.values()
        )
    stats["gate_neighborhood_total_word_count"] = len(radius_by_word)

    rows: dict[tuple[int, ...], dict[str, Any]] = {}
    for word, radius in sorted(radius_by_word.items(), key=lambda item: item[0]):
        row: dict[str, Any] = {"word": word, "gate_edit_radius": radius}
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
        row.update(closure_profile(word, carrier_adjacency))
        if not has_repair:
            stats["no_repair_candidate_count"] += 1
            row["class"] = "no_repair"
            rows[word] = row
            continue
        stats["repair_chord_candidate_count"] += 1
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
    return rows, dict(stats)


def build_good_graph(
    rows: dict[tuple[int, ...], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, int]], dict[tuple[int, ...], int], int]:
    good_words = sorted(
        [word for word, row in rows.items() if row.get("class") == "good"],
        key=lambda word: (
            rows[word]["gate_edit_radius"],
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
                "gate_repair_cell_id": cell_id,
                "component_id": component_id_by_cell[cell_id],
                "gate_edit_radius": row["gate_edit_radius"],
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
            }
        )

    cell_by_id = {row["gate_repair_cell_id"]: row for row in cell_rows}
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
                "left_to_right_bridge_flag": int(left_flag and right_flag),
            }
        )
    return cell_rows, component_rows, cell_id_by_word, edge_count


def build_bridge_rows(
    rows: dict[tuple[int, ...], dict[str, Any]],
    cell_id_by_word: dict[tuple[int, ...], int],
    cell_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    component_by_word = {
        tuple(row[column] for column in WORD_COLUMNS if row[column] != -1): row[
            "component_id"
        ]
        for row in cell_rows
    }
    bridge_words = (
        LEFT_REPAIR_BOUNDARY_WORD,
        NO_REPAIR_GATE_WORD,
        RIGHT_REPAIR_BOUNDARY_WORD,
    )
    bridge_rows = []
    for step_index, word in enumerate(bridge_words):
        row = rows[word]
        component_id = component_by_word.get(word, -1)
        bridge_rows.append(
            {
                "bridge_step_index": step_index,
                "word_class_code": 0 if row["class"] == "good" else 1,
                "gate_flag": int(word == NO_REPAIR_GATE_WORD),
                "gate_edit_radius": row["gate_edit_radius"],
                "component_id": component_id,
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
                "repair_chord_flag": row["repair_chord_flag"],
                "first_return_closed_path_count": row[
                    "first_return_closed_path_count"
                ],
                "normalized_tail_template_count": row[
                    "normalized_tail_template_count"
                ],
                "all_four_lift_flag": row["all_four_lift_flag"],
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "tail_entry_13_path_count": row["tail_entry_13_path_count"],
            }
        )
    return bridge_rows


def build_payload_rows() -> dict[str, Any]:
    rows, stats = evaluate_words()
    cell_rows, component_rows, cell_id_by_word, good_edge_count = build_good_graph(rows)
    bridge_rows = build_bridge_rows(rows, cell_id_by_word, cell_rows)

    left_component = next(row for row in component_rows if row["left_boundary_flag"] == 1)
    right_component = next(
        row for row in component_rows if row["right_boundary_flag"] == 1
    )
    target_rows = [row for row in cell_rows if row["exact24_six_all_four_flag"] == 1]
    clear_rows = [row for row in cell_rows if row["clear_flag"] == 1]
    gate_bridge = next(row for row in bridge_rows if row["gate_flag"] == 1)
    observable_values = {
        "radius0_word_count": stats["radius0_word_count"],
        "radius1_word_count": stats["radius1_word_count"],
        "radius2_word_count": stats["radius2_word_count"],
        "radius3_word_count": stats["radius3_word_count"],
        "gate_neighborhood_total_word_count": stats[
            "gate_neighborhood_total_word_count"
        ],
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
        "clear_cell_count": len(clear_rows),
        "left_to_right_good_path_exists": int(
            left_component["component_id"] == right_component["component_id"]
        ),
        "one_no_repair_gate_bridge_exists": 1,
        "gate_word_variation": gate_bridge["trace_signature_total_variation"],
        "gate_word_closed_paths": gate_bridge["first_return_closed_path_count"],
        "gate_word_template_count": gate_bridge[
            "normalized_tail_template_count"
        ],
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": GATE_OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    return {
        "rows": rows,
        "stats": stats,
        "observable_values": observable_values,
        "cell_rows": cell_rows,
        "component_rows": component_rows,
        "bridge_rows": bridge_rows,
        "observable_rows": observable_rows,
    }


def build_payloads() -> dict[str, Any]:
    level2_report = load_json(LEVEL2_REPORT)
    level2_certificate = load_json(LEVEL2_CERTIFICATE)
    payload_rows = build_payload_rows()
    observable_values = payload_rows["observable_values"]
    cell_rows = payload_rows["cell_rows"]
    component_rows = payload_rows["component_rows"]
    bridge_rows = payload_rows["bridge_rows"]
    observable_rows = payload_rows["observable_rows"]

    cell_table = table_from_rows(CELL_COLUMNS, cell_rows)
    component_table = table_from_rows(COMPONENT_COLUMNS, component_rows)
    bridge_table = table_from_rows(BRIDGE_COLUMNS, bridge_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    left_component = next(row for row in component_rows if row["left_boundary_flag"] == 1)
    right_component = next(
        row for row in component_rows if row["right_boundary_flag"] == 1
    )
    checks = {
        "level2_report_certified": level2_report.get("status") == LEVEL2_STATUS,
        "level2_certificate_certified": level2_certificate.get("status")
        == LEVEL2_STATUS,
        "radius_shell_counts_are_expected": [
            observable_values["radius0_word_count"],
            observable_values["radius1_word_count"],
            observable_values["radius2_word_count"],
            observable_values["radius3_word_count"],
        ]
        == [1, 94, 3_971, 101_564],
        "gate_neighborhood_total_word_count_is_105630": observable_values[
            "gate_neighborhood_total_word_count"
        ]
        == 105_630,
        "trace_valid_word_count_is_75925": observable_values[
            "trace_valid_word_count"
        ]
        == 75_925,
        "delta2_variation_le223_count_is_16842": observable_values[
            "delta2_variation_le223_word_count"
        ]
        == 16_842,
        "repair_chord_candidate_count_is_1022": observable_values[
            "repair_chord_candidate_count"
        ]
        == 1_022,
        "no_repair_candidate_count_is_15820": observable_values[
            "no_repair_candidate_count"
        ]
        == 15_820,
        "good_cell_count_is_91": observable_values["good_cell_count"] == 91,
        "good_edge_count_is_189": observable_values["good_edge_count"] == 189,
        "good_components_are_52_35_1_1_1_1": [
            row["cell_count"] for row in component_rows
        ]
        == [52, 35, 1, 1, 1, 1],
        "left_and_right_good_components_are_separate": observable_values[
            "left_to_right_good_path_exists"
        ]
        == 0,
        "targets_are_left_component_only": left_component["target_cell_count"] == 3
        and right_component["target_cell_count"] == 0,
        "min_target_variation_is_195": observable_values["min_target_variation"]
        == 195,
        "bridge_uses_single_no_repair_gate": len(bridge_rows) == 3
        and sum(row["gate_flag"] for row in bridge_rows) == 1
        and bridge_rows[1]["repair_chord_flag"] == 0,
        "gate_profile_is_185_30_9": (
            bridge_rows[1]["trace_signature_total_variation"],
            bridge_rows[1]["first_return_closed_path_count"],
            bridge_rows[1]["normalized_tail_template_count"],
        )
        == (185, 30, 9),
        "cell_table_shape_matches_codebook": tuple(cell_table.shape)
        == (91, len(CELL_COLUMNS)),
        "component_table_shape_matches_codebook": tuple(component_table.shape)
        == (6, len(COMPONENT_COLUMNS)),
        "bridge_table_shape_matches_codebook": tuple(bridge_table.shape)
        == (3, len(BRIDGE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(GATE_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    target_rows = [row for row in cell_rows if row["exact24_six_all_four_flag"] == 1]
    witness = {
        "gate_word": list(NO_REPAIR_GATE_WORD),
        "left_boundary_word": list(LEFT_REPAIR_BOUNDARY_WORD),
        "right_boundary_word": list(RIGHT_REPAIR_BOUNDARY_WORD),
        "radius_shell_counts": [
            observable_values["radius0_word_count"],
            observable_values["radius1_word_count"],
            observable_values["radius2_word_count"],
            observable_values["radius3_word_count"],
        ],
        "good_cell_count": observable_values["good_cell_count"],
        "good_component_sizes": [row["cell_count"] for row in component_rows],
        "target_count": len(target_rows),
        "min_target_variation": observable_values["min_target_variation"],
        "left_component_id": left_component["component_id"],
        "right_component_id": right_component["component_id"],
        "gate_profile": {
            "variation": bridge_rows[1]["trace_signature_total_variation"],
            "closed_paths": bridge_rows[1]["first_return_closed_path_count"],
            "template_count": bridge_rows[1]["normalized_tail_template_count"],
            "endpoint_distribution": {
                "9": bridge_rows[1]["tail_entry_9_path_count"],
                "10": bridge_rows[1]["tail_entry_10_path_count"],
                "11": bridge_rows[1]["tail_entry_11_path_count"],
                "13": bridge_rows[1]["tail_entry_13_path_count"],
            },
        },
        "target_words": [
            [
                row[column] for column in WORD_COLUMNS if row[column] != -1
            ]
            for row in sorted(
                target_rows,
                key=lambda row: (
                    row["trace_signature_total_variation"],
                    row["gate_edit_radius"],
                    row["word_length"],
                    [row[column] for column in WORD_COLUMNS],
                ),
            )
        ],
        "cell_table_sha256": sha_array(cell_table),
        "component_table_sha256": sha_array(component_table),
        "bridge_table_sha256": sha_array(bridge_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    gate_repair = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search@1",
        "object": "d20",
        "comparison_rule": {
            "parent": LEVEL2_REPORT.relative_to(ROOT).as_posix(),
            "gate_word": list(NO_REPAIR_GATE_WORD),
            "gate_suffix": list(NO_REPAIR_GATE_WORD[2:]),
            "radius": MAX_GATE_EDIT_RADIUS,
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
            "target_cell_count": len(target_rows),
            "left_to_right_good_path_exists": observable_values[
                "left_to_right_good_path_exists"
            ],
            "one_no_repair_gate_bridge_exists": observable_values[
                "one_no_repair_gate_bridge_exists"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_GATE_REPAIR_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the radius-three local replacement ball around the no-repair gate has 105630 prefix-valid words",
            "repair support reappears in 1022 delta2 variation<=223 candidates, but only 91 are closed-positive good cells",
            "the good-cell graph has six components, with the left and right repair boundaries in separate components of sizes 52 and 35",
            "all exact 24/six/all-four repaired targets in the radius-three ball remain in the left component, with minimum variation 195",
            "therefore radius-three local replacement does not repair the gate; the only bridge still uses the original no-repair word",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The radius-three gate-repair search around the no-repair word "
            "x2,x1,x4,x5,x1,x2,x5,x5,x2,x1,x4,x5 enumerates 105,630 "
            "prefix-valid local replacements. Repair support reappears in "
            "1,022 delta2 variation<=223 candidates, but only 91 are "
            "closed-positive good cells. Their one-edit graph has 189 edges "
            "and six components of sizes 52, 35, 1, 1, 1, and 1. The left "
            "and right repair-boundary cells remain in separate components. "
            "The three exact 24-closure, six-template, all-four repaired "
            "targets are all in the left component at minimum variation 195. "
            "Thus the no-repair gate is not locally repairable through radius "
            "three by replacing the gate word while preserving the good-cell "
            "criteria."
        ),
        "stage_protocol": {
            "draft": "center the search on the certified no-repair gate word",
            "witness": "enumerate radius-three replacements and evaluate repair support, closures, templates, and good-cell connectivity",
            "coherence": "compare left and right repair-boundary components and exact target locations",
            "closure": "certify that radius-three repaired good cells do not bridge the gate",
            "emit": "emit repaired cells, components, bridge row, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "level2_report": input_entry(
                LEVEL2_REPORT,
                {
                    "status": level2_report.get("status"),
                    "certificate_sha256": level2_report.get("certificate_sha256"),
                },
            ),
            "level2_certificate": input_entry(LEVEL2_CERTIFICATE),
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
            "signature_boundary_spine_aperture_closure_tail_gate_repair_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_gate_repair_search.json"
            ),
            "aperture_closure_tail_gate_repair_cells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_gate_repair_cells.csv"
            ),
            "aperture_closure_tail_gate_repair_components_csv": relpath(
                OUT_DIR / "aperture_closure_tail_gate_repair_components.csv"
            ),
            "aperture_closure_tail_gate_repair_bridge_csv": relpath(
                OUT_DIR / "aperture_closure_tail_gate_repair_bridge.csv"
            ),
            "aperture_closure_tail_gate_repair_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_gate_repair_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_gate_repair_search_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_gate_repair_search_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "radius-three local replacements of the certified no-repair gate word",
                "good cells satisfying delta2, variation <= 223, repair-chord support, and closed positivity in that ball",
                "that repaired exact 24/six/all-four targets exist only on the left repair-boundary side",
                "that no good path connects the left and right repair-boundary components through radius three",
            ],
            "does_not_certify_because_not_required": [
                "radius four or higher around the gate word",
                "paths using no-closed, bad-metric, or trace-failure gates",
                "a global no-go theorem outside the declared gate-repair ball",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Leave single-word gate replacement and search a two-cell bridge: "
            "allow one intermediate word on each side of the no-repair gate, "
            "or equivalently graft a repair chord into the left/right boundary "
            "pair rather than into the gate word alone."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified level-two clear-corridor artifacts",
            "enumerate radius-three replacements around the no-repair gate word",
            "classify good cells and repaired target locations",
            "check left/right good-component separation",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_gate_repair_search": gate_repair,
        "aperture_closure_tail_gate_repair_cells_csv": csv_text(
            CELL_COLUMNS,
            cell_rows,
        ),
        "aperture_closure_tail_gate_repair_components_csv": csv_text(
            COMPONENT_COLUMNS,
            component_rows,
        ),
        "aperture_closure_tail_gate_repair_bridge_csv": csv_text(
            BRIDGE_COLUMNS,
            bridge_rows,
        ),
        "aperture_closure_tail_gate_repair_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "cell_table": cell_table,
        "component_table": component_table,
        "bridge_table": bridge_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_closure_tail_gate_repair_search.json",
        payloads["signature_boundary_spine_aperture_closure_tail_gate_repair_search"],
    )
    (OUT_DIR / "aperture_closure_tail_gate_repair_cells.csv").write_text(
        payloads["aperture_closure_tail_gate_repair_cells_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_gate_repair_components.csv").write_text(
        payloads["aperture_closure_tail_gate_repair_components_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_gate_repair_bridge.csv").write_text(
        payloads["aperture_closure_tail_gate_repair_bridge_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_gate_repair_observables.csv").write_text(
        payloads["aperture_closure_tail_gate_repair_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_gate_repair_search_tables.npz",
        cell_table=payloads["cell_table"],
        component_table=payloads["component_table"],
        bridge_table=payloads["bridge_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate"
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
