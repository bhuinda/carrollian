from __future__ import annotations

import json
from collections import Counter, deque
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
        OUT_DIR as BOUNDARY_BRIDGE_DIR,
        REWRITE_COMPLEX_EDGES,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as BOUNDARY_BRIDGE_STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_CLOSED_PATH_COUNT,
        TARGET_DELTA_TWICE,
        TARGET_TEMPLATE_COUNT,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        build_context,
        build_good_graph,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
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
        OUT_DIR as BOUNDARY_BRIDGE_DIR,
        REWRITE_COMPLEX_EDGES,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as BOUNDARY_BRIDGE_STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_CLOSED_PATH_COUNT,
        TARGET_DELTA_TWICE,
        TARGET_TEMPLATE_COUNT,
        TARGET_VARIATION_INCLUSIVE_BOUND,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        build_context,
        build_good_graph,
        build_trace,
        closure_profile,
        contains_undirected_edge,
        csv_text,
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
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_VIRTUAL_GRAFT_BRIDGE_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

BOUNDARY_BRIDGE_REPORT = BOUNDARY_BRIDGE_DIR / "report.json"
BOUNDARY_BRIDGE_CERTIFICATE = (
    BOUNDARY_BRIDGE_DIR
    / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate.json"
)
DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge.py"
)

NATIVE_MODE_CODE = 0
VIRTUAL_31_28_MODE_CODE = 1
VIRTUAL_50_34_MODE_CODE = 2
NATIVE_NODE_KIND_CODE = 0
VIRTUAL_GRAFT_NODE_KIND_CODE = 1

GRAFT_COLUMNS = [
    "virtual_graft_cell_id",
    "word_length",
    *WORD_COLUMNS,
    "left_edit_radius",
    "right_edit_radius",
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
    "virtual_31_28_admissible_flag",
    "virtual_50_34_admissible_flag",
    "adjacent_native_component_count",
    "adjacent_native_component_mask",
    "adjacent_left_component_flag",
    "adjacent_right_component_flag",
    "left_right_bridge_flag",
    "direct_boundary_bridge_flag",
    "closed_ge24_template_ge6_flag",
    "clear_flag",
    "exact24_six_all_four_flag",
]

MODE_COLUMNS = [
    "mode_code",
    "node_count",
    "native_cell_count",
    "virtual_graft_cell_count",
    "edge_count",
    "component_count",
    "left_to_right_path_exists",
    "shortest_left_to_right_path_length",
    "merged_component_size",
    "merged_component_native_cell_count",
    "merged_component_virtual_graft_cell_count",
    "direct_boundary_bridge_count",
    "left_right_graft_bridge_count",
]

PATH_COLUMNS = [
    "path_id",
    "graft_mode_code",
    "path_step",
    "node_kind_code",
    "word_length",
    *WORD_COLUMNS,
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "all_four_lift_flag",
    "tail_entry_13_path_count",
    "native_31_28_flag",
    "native_50_34_flag",
    "virtual_31_28_flag",
    "virtual_50_34_flag",
]

VIRTUAL_GRAFT_OBSERVABLE_CODES = {
    "metric_ok_word_count": 0,
    "native_good_cell_count": 1,
    "native_no_closed_count": 2,
    "virtual_graft_candidate_count": 3,
    "no_repair_no_closed_count": 4,
    "native_good_edge_count": 5,
    "native_good_component_count": 6,
    "native_left_component_size": 7,
    "native_right_component_size": 8,
    "native_left_to_right_path_exists": 9,
    "virtual_graph_node_count": 10,
    "virtual_graph_edge_count": 11,
    "virtual_graph_component_count": 12,
    "virtual_left_to_right_path_exists": 13,
    "virtual_merged_component_size": 14,
    "virtual_merged_native_cell_count": 15,
    "virtual_merged_graft_cell_count": 16,
    "left_right_graft_bridge_candidate_count": 17,
    "direct_boundary_graft_bridge_count": 18,
    "direct_common_neighbor_count": 19,
    "single_31_28_graft_path_exists": 20,
    "single_50_34_graft_path_exists": 21,
    "shortest_graft_path_length": 22,
    "gate_word_variation": 23,
    "gate_word_closed_path_count": 24,
    "gate_word_template_count": 25,
    "exact_virtual_graft_candidate_count": 26,
    "clear_virtual_graft_candidate_count": 27,
    "closed_ge24_template_ge6_graft_candidate_count": 28,
    "min_bridge_candidate_variation": 29,
    "min_virtual_graft_candidate_variation": 30,
}


def exact24_six_all_four(row: dict[str, int]) -> int:
    return int(
        row["first_return_closed_path_count"] == TARGET_CLOSED_PATH_COUNT
        and row["normalized_tail_template_count"] == TARGET_TEMPLATE_COUNT
        and row["all_four_lift_flag"] == 1
        and row["tail_entry_13_path_count"] == 0
    )


def clear24(row: dict[str, int]) -> int:
    return int(
        row["first_return_closed_path_count"] >= TARGET_CLOSED_PATH_COUNT
        and row["all_four_lift_flag"] == 1
        and row["tail_entry_13_path_count"] == 0
    )


def evaluate_words() -> tuple[dict[tuple[int, ...], dict[str, Any]], dict[str, int]]:
    left_radius = radius_from(LEFT_REPAIR_BOUNDARY_WORD, MAX_SIDE_EDIT_RADIUS)
    right_radius = radius_from(RIGHT_REPAIR_BOUNDARY_WORD, MAX_SIDE_EDIT_RADIUS)
    candidate_words = set(left_radius) | set(right_radius)
    carrier_adjacency, assoc_by_word, rewrite_edge_by_pair = build_context()
    rows: dict[tuple[int, ...], dict[str, Any]] = {}
    stats: Counter[str] = Counter()

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

        trace = tuple(int(value) for value in trace_nodes)
        variation = int(metrics["trace_signature_total_variation"])
        delta_twice = int(metrics["metric_gromov_delta_twice"])
        row.update(
            {
                "trace": trace,
                "trace_signature_total_variation": variation,
                "metric_gromov_delta_twice": delta_twice,
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

        stats["metric_ok_word_count"] += 1
        native_31 = contains_undirected_edge(trace, 31, 28)
        native_50 = contains_undirected_edge(trace, 50, 34)
        native_repair = native_31 or native_50
        row.update(
            {
                "native_31_28_flag": int(native_31),
                "native_50_34_flag": int(native_50),
                "repair_chord_flag": int(native_repair),
            }
        )
        row.update(closure_profile(word, carrier_adjacency))
        row["exact24_six_all_four_flag"] = exact24_six_all_four(row)
        row["clear_flag"] = clear24(row)
        row["closed_ge24_template_ge6_flag"] = int(
            row["first_return_closed_path_count"] >= TARGET_CLOSED_PATH_COUNT
            and row["normalized_tail_template_count"] >= TARGET_TEMPLATE_COUNT
        )
        if native_repair and row["first_return_closed_path_count"] > 0:
            stats["native_good_cell_count"] += 1
            row["class"] = "native_good"
        elif native_repair:
            stats["native_no_closed_count"] += 1
            row["class"] = "native_no_closed"
        elif row["first_return_closed_path_count"] > 0:
            stats["virtual_graft_candidate_count"] += 1
            row["class"] = "virtual_graft_candidate"
        else:
            stats["no_repair_no_closed_count"] += 1
            row["class"] = "no_repair_no_closed"
        rows[word] = row
    return rows, dict(stats)


def native_components(
    rows: dict[tuple[int, ...], dict[str, Any]]
) -> tuple[list[dict[str, int]], dict[tuple[int, ...], int], int]:
    native_rows = {}
    for word, row in rows.items():
        native_row = dict(row)
        if row.get("class") == "native_good":
            native_row["class"] = "good"
        native_rows[word] = native_row
    cell_rows, component_rows, _cell_id_by_word, edge_count = build_good_graph(
        native_rows
    )
    word_to_component = {
        tuple(row[column] for column in WORD_COLUMNS if row[column] != -1): row[
            "component_id"
        ]
        for row in cell_rows
    }
    return component_rows, word_to_component, edge_count


def build_active_graph(
    rows: dict[tuple[int, ...], dict[str, Any]],
) -> tuple[dict[str, Any], list[tuple[int, ...]]]:
    active_words = sorted(
        word
        for word, row in rows.items()
        if row.get("class") in {"native_good", "virtual_graft_candidate"}
    )
    word_id = {word: index for index, word in enumerate(active_words)}
    adjacency: dict[int, set[int]] = {index: set() for index in range(len(active_words))}
    edge_set: set[tuple[int, int]] = set()
    for word, source_id in word_id.items():
        for neighbor in set(one_edit_neighbors(word)):
            target_id = word_id.get(neighbor)
            if target_id is None:
                continue
            edge = tuple(sorted((source_id, target_id)))
            if edge[0] != edge[1]:
                edge_set.add(edge)
            adjacency[source_id].add(target_id)
            adjacency[target_id].add(source_id)

    seen: set[int] = set()
    components: list[list[int]] = []
    for cell_id in sorted(adjacency):
        if cell_id in seen:
            continue
        stack = [cell_id]
        seen.add(cell_id)
        component: list[int] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(component)

    left_id = word_id[LEFT_REPAIR_BOUNDARY_WORD]
    right_id = word_id[RIGHT_REPAIR_BOUNDARY_WORD]
    merged_component = next(component for component in components if left_id in component)
    right_in_merged = int(right_id in merged_component)

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

    path_words: list[tuple[int, ...]] = []
    if right_id in parent:
        current: int | None = right_id
        while current is not None:
            path_words.append(active_words[current])
            current = parent[current]
        path_words.reverse()

    return (
        {
            "node_count": len(active_words),
            "edge_count": len(edge_set),
            "component_count": len(components),
            "component_sizes": sorted((len(component) for component in components), reverse=True),
            "left_to_right_path_exists": right_in_merged,
            "shortest_path_length": distance.get(right_id, -1),
            "merged_component_size": len(merged_component),
            "merged_component_native_count": sum(
                int(rows[active_words[cell_id]]["class"] == "native_good")
                for cell_id in merged_component
            ),
            "merged_component_graft_count": sum(
                int(rows[active_words[cell_id]]["class"] == "virtual_graft_candidate")
                for cell_id in merged_component
            ),
            "path_words": path_words,
        },
        active_words,
    )


def build_graft_rows(
    rows: dict[tuple[int, ...], dict[str, Any]],
    word_to_component: dict[tuple[int, ...], int],
) -> list[dict[str, int]]:
    left_neighbors = set(one_edit_neighbors(LEFT_REPAIR_BOUNDARY_WORD))
    right_neighbors = set(one_edit_neighbors(RIGHT_REPAIR_BOUNDARY_WORD))
    graft_words = sorted(
        (
            word
            for word, row in rows.items()
            if row.get("class") == "virtual_graft_candidate"
        ),
        key=lambda word: (
            int(not (word in left_neighbors and word in right_neighbors)),
            rows[word]["trace_signature_total_variation"],
            len(word),
            word,
        ),
    )
    graft_rows: list[dict[str, int]] = []
    for graft_id, word in enumerate(graft_words):
        row = rows[word]
        adjacent_components = sorted(
            {
                word_to_component[neighbor]
                for neighbor in set(one_edit_neighbors(word))
                if neighbor in word_to_component
            }
        )
        component_mask = sum(1 << component_id for component_id in adjacent_components)
        graft_rows.append(
            {
                "virtual_graft_cell_id": graft_id,
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
                "virtual_31_28_admissible_flag": 1,
                "virtual_50_34_admissible_flag": 1,
                "adjacent_native_component_count": len(adjacent_components),
                "adjacent_native_component_mask": component_mask,
                "adjacent_left_component_flag": int(0 in adjacent_components),
                "adjacent_right_component_flag": int(1 in adjacent_components),
                "left_right_bridge_flag": int(
                    0 in adjacent_components and 1 in adjacent_components
                ),
                "direct_boundary_bridge_flag": int(
                    word in left_neighbors and word in right_neighbors
                ),
                "closed_ge24_template_ge6_flag": row[
                    "closed_ge24_template_ge6_flag"
                ],
                "clear_flag": row["clear_flag"],
                "exact24_six_all_four_flag": row["exact24_six_all_four_flag"],
            }
        )
    return graft_rows


def path_rows(
    rows: dict[tuple[int, ...], dict[str, Any]],
    path_words: list[tuple[int, ...]],
) -> list[dict[str, int]]:
    result = []
    for path_id, mode_code in enumerate(
        [VIRTUAL_31_28_MODE_CODE, VIRTUAL_50_34_MODE_CODE]
    ):
        for step, word in enumerate(path_words):
            row = rows[word]
            is_graft = int(row["class"] == "virtual_graft_candidate")
            result.append(
                {
                    "path_id": path_id,
                    "graft_mode_code": mode_code,
                    "path_step": step,
                    "node_kind_code": VIRTUAL_GRAFT_NODE_KIND_CODE
                    if is_graft
                    else NATIVE_NODE_KIND_CODE,
                    "word_length": len(word),
                    **{
                        column: value
                        for column, value in zip(
                            WORD_COLUMNS,
                            padded(word, MAX_WORD_LENGTH),
                        )
                    },
                    "trace_signature_total_variation": row[
                        "trace_signature_total_variation"
                    ],
                    "first_return_closed_path_count": row[
                        "first_return_closed_path_count"
                    ],
                    "normalized_tail_template_count": row[
                        "normalized_tail_template_count"
                    ],
                    "all_four_lift_flag": row["all_four_lift_flag"],
                    "tail_entry_13_path_count": row["tail_entry_13_path_count"],
                    "native_31_28_flag": row["native_31_28_flag"],
                    "native_50_34_flag": row["native_50_34_flag"],
                    "virtual_31_28_flag": int(
                        is_graft and mode_code == VIRTUAL_31_28_MODE_CODE
                    ),
                    "virtual_50_34_flag": int(
                        is_graft and mode_code == VIRTUAL_50_34_MODE_CODE
                    ),
                }
            )
    return result


def mode_rows(
    native_component_rows: list[dict[str, int]],
    native_edge_count: int,
    virtual_graph: dict[str, Any],
    graft_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    left_component = next(
        row for row in native_component_rows if row["left_boundary_flag"] == 1
    )
    right_component = next(
        row for row in native_component_rows if row["right_boundary_flag"] == 1
    )
    graft_count = len(graft_rows)
    native_count = sum(row["cell_count"] for row in native_component_rows)
    direct_bridge_count = sum(row["direct_boundary_bridge_flag"] for row in graft_rows)
    left_right_bridge_count = sum(row["left_right_bridge_flag"] for row in graft_rows)
    native_row = {
        "mode_code": NATIVE_MODE_CODE,
        "node_count": native_count,
        "native_cell_count": native_count,
        "virtual_graft_cell_count": 0,
        "edge_count": native_edge_count,
        "component_count": len(native_component_rows),
        "left_to_right_path_exists": int(
            left_component["component_id"] == right_component["component_id"]
        ),
        "shortest_left_to_right_path_length": -1,
        "merged_component_size": left_component["cell_count"],
        "merged_component_native_cell_count": left_component["cell_count"],
        "merged_component_virtual_graft_cell_count": 0,
        "direct_boundary_bridge_count": 0,
        "left_right_graft_bridge_count": 0,
    }
    graft_template = {
        "node_count": virtual_graph["node_count"],
        "native_cell_count": native_count,
        "virtual_graft_cell_count": graft_count,
        "edge_count": virtual_graph["edge_count"],
        "component_count": virtual_graph["component_count"],
        "left_to_right_path_exists": virtual_graph["left_to_right_path_exists"],
        "shortest_left_to_right_path_length": virtual_graph["shortest_path_length"],
        "merged_component_size": virtual_graph["merged_component_size"],
        "merged_component_native_cell_count": virtual_graph[
            "merged_component_native_count"
        ],
        "merged_component_virtual_graft_cell_count": virtual_graph[
            "merged_component_graft_count"
        ],
        "direct_boundary_bridge_count": direct_bridge_count,
        "left_right_graft_bridge_count": left_right_bridge_count,
    }
    return [
        native_row,
        {"mode_code": VIRTUAL_31_28_MODE_CODE, **graft_template},
        {"mode_code": VIRTUAL_50_34_MODE_CODE, **graft_template},
    ]


def build_payload_rows() -> dict[str, Any]:
    rows, stats = evaluate_words()
    native_component_rows, word_to_component, native_edge_count = native_components(rows)
    graft_rows = build_graft_rows(rows, word_to_component)
    virtual_graph, _active_words = build_active_graph(rows)
    bridge_path_rows = path_rows(rows, virtual_graph["path_words"])
    graph_mode_rows = mode_rows(
        native_component_rows,
        native_edge_count,
        virtual_graph,
        graft_rows,
    )

    direct_common_neighbors = set(one_edit_neighbors(LEFT_REPAIR_BOUNDARY_WORD)) & set(
        one_edit_neighbors(RIGHT_REPAIR_BOUNDARY_WORD)
    )
    bridge_candidates = [row for row in graft_rows if row["left_right_bridge_flag"] == 1]
    gate_row = rows[NO_REPAIR_GATE_WORD]
    left_component = next(
        row for row in native_component_rows if row["left_boundary_flag"] == 1
    )
    right_component = next(
        row for row in native_component_rows if row["right_boundary_flag"] == 1
    )
    observable_values = {
        "metric_ok_word_count": stats["metric_ok_word_count"],
        "native_good_cell_count": stats["native_good_cell_count"],
        "native_no_closed_count": stats["native_no_closed_count"],
        "virtual_graft_candidate_count": stats["virtual_graft_candidate_count"],
        "no_repair_no_closed_count": stats["no_repair_no_closed_count"],
        "native_good_edge_count": native_edge_count,
        "native_good_component_count": len(native_component_rows),
        "native_left_component_size": left_component["cell_count"],
        "native_right_component_size": right_component["cell_count"],
        "native_left_to_right_path_exists": int(
            left_component["component_id"] == right_component["component_id"]
        ),
        "virtual_graph_node_count": virtual_graph["node_count"],
        "virtual_graph_edge_count": virtual_graph["edge_count"],
        "virtual_graph_component_count": virtual_graph["component_count"],
        "virtual_left_to_right_path_exists": virtual_graph[
            "left_to_right_path_exists"
        ],
        "virtual_merged_component_size": virtual_graph["merged_component_size"],
        "virtual_merged_native_cell_count": virtual_graph[
            "merged_component_native_count"
        ],
        "virtual_merged_graft_cell_count": virtual_graph[
            "merged_component_graft_count"
        ],
        "left_right_graft_bridge_candidate_count": len(bridge_candidates),
        "direct_boundary_graft_bridge_count": sum(
            row["direct_boundary_bridge_flag"] for row in graft_rows
        ),
        "direct_common_neighbor_count": len(direct_common_neighbors),
        "single_31_28_graft_path_exists": int(
            graph_mode_rows[1]["left_to_right_path_exists"] == 1
        ),
        "single_50_34_graft_path_exists": int(
            graph_mode_rows[2]["left_to_right_path_exists"] == 1
        ),
        "shortest_graft_path_length": virtual_graph["shortest_path_length"],
        "gate_word_variation": gate_row["trace_signature_total_variation"],
        "gate_word_closed_path_count": gate_row["first_return_closed_path_count"],
        "gate_word_template_count": gate_row["normalized_tail_template_count"],
        "exact_virtual_graft_candidate_count": sum(
            row["exact24_six_all_four_flag"] for row in graft_rows
        ),
        "clear_virtual_graft_candidate_count": sum(row["clear_flag"] for row in graft_rows),
        "closed_ge24_template_ge6_graft_candidate_count": sum(
            row["closed_ge24_template_ge6_flag"] for row in graft_rows
        ),
        "min_bridge_candidate_variation": min(
            row["trace_signature_total_variation"] for row in bridge_candidates
        ),
        "min_virtual_graft_candidate_variation": min(
            row["trace_signature_total_variation"] for row in graft_rows
        ),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": VIRTUAL_GRAFT_OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    return {
        "rows": rows,
        "observable_values": observable_values,
        "graft_rows": graft_rows,
        "mode_rows": graph_mode_rows,
        "path_rows": bridge_path_rows,
        "observable_rows": observable_rows,
        "native_component_rows": native_component_rows,
        "virtual_graph": virtual_graph,
    }


def build_payloads() -> dict[str, Any]:
    boundary_report = load_json(BOUNDARY_BRIDGE_REPORT)
    boundary_certificate = load_json(BOUNDARY_BRIDGE_CERTIFICATE)
    payload_rows = build_payload_rows()
    observable_values = payload_rows["observable_values"]
    graft_rows = payload_rows["graft_rows"]
    graph_mode_rows = payload_rows["mode_rows"]
    bridge_path_rows = payload_rows["path_rows"]
    observable_rows = payload_rows["observable_rows"]
    native_component_rows = payload_rows["native_component_rows"]
    virtual_graph = payload_rows["virtual_graph"]

    graft_table = table_from_rows(GRAFT_COLUMNS, graft_rows)
    mode_table = table_from_rows(MODE_COLUMNS, graph_mode_rows)
    path_table = table_from_rows(PATH_COLUMNS, bridge_path_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "boundary_bridge_report_certified": boundary_report.get("status")
        == BOUNDARY_BRIDGE_STATUS,
        "boundary_bridge_certificate_certified": boundary_certificate.get("status")
        == BOUNDARY_BRIDGE_STATUS,
        "native_graph_still_separate": observable_values[
            "native_left_to_right_path_exists"
        ]
        == 0,
        "virtual_graft_graph_connects_boundaries": observable_values[
            "virtual_left_to_right_path_exists"
        ]
        == 1,
        "single_graft_modes_both_connect": (
            observable_values["single_31_28_graft_path_exists"],
            observable_values["single_50_34_graft_path_exists"],
        )
        == (1, 1),
        "metric_ok_word_count_is_26197": observable_values["metric_ok_word_count"]
        == 26_197,
        "native_good_cell_count_is_562": observable_values["native_good_cell_count"]
        == 562,
        "virtual_graft_candidate_count_is_422": observable_values[
            "virtual_graft_candidate_count"
        ]
        == 422,
        "native_no_closed_count_is_11075": observable_values["native_no_closed_count"]
        == 11_075,
        "no_repair_no_closed_count_is_14138": observable_values[
            "no_repair_no_closed_count"
        ]
        == 14_138,
        "native_edges_and_components_are_expected": (
            observable_values["native_good_edge_count"],
            observable_values["native_good_component_count"],
            observable_values["native_left_component_size"],
            observable_values["native_right_component_size"],
        )
        == (1_694, 13, 347, 185),
        "virtual_graph_counts_are_expected": (
            observable_values["virtual_graph_node_count"],
            observable_values["virtual_graph_edge_count"],
            observable_values["virtual_graph_component_count"],
            observable_values["virtual_merged_component_size"],
        )
        == (984, 3_134, 23, 925),
        "merged_component_composition_is_expected": (
            observable_values["virtual_merged_native_cell_count"],
            observable_values["virtual_merged_graft_cell_count"],
        )
        == (534, 391),
        "bridge_candidate_counts_are_expected": (
            observable_values["left_right_graft_bridge_candidate_count"],
            observable_values["direct_boundary_graft_bridge_count"],
            observable_values["direct_common_neighbor_count"],
        )
        == (25, 1, 2),
        "shortest_path_is_direct_gate_graft": observable_values[
            "shortest_graft_path_length"
        ]
        == 2
        and [tuple(row[column] for column in WORD_COLUMNS if row[column] != -1) for row in bridge_path_rows[:3]]
        == [
            LEFT_REPAIR_BOUNDARY_WORD,
            NO_REPAIR_GATE_WORD,
            RIGHT_REPAIR_BOUNDARY_WORD,
        ],
        "gate_profile_preserves_closed_template_mass": (
            observable_values["gate_word_variation"],
            observable_values["gate_word_closed_path_count"],
            observable_values["gate_word_template_count"],
        )
        == (185, 30, 9),
        "graft_candidate_target_counts_are_expected": (
            observable_values["exact_virtual_graft_candidate_count"],
            observable_values["clear_virtual_graft_candidate_count"],
            observable_values["closed_ge24_template_ge6_graft_candidate_count"],
        )
        == (1, 4, 249),
        "min_variations_are_expected": (
            observable_values["min_bridge_candidate_variation"],
            observable_values["min_virtual_graft_candidate_variation"],
        )
        == (143, 143),
        "graft_table_shape_matches_codebook": tuple(graft_table.shape)
        == (422, len(GRAFT_COLUMNS)),
        "mode_table_shape_matches_codebook": tuple(mode_table.shape)
        == (3, len(MODE_COLUMNS)),
        "path_table_shape_matches_codebook": tuple(path_table.shape)
        == (6, len(PATH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(VIRTUAL_GRAFT_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "native_component_sizes": [row["cell_count"] for row in native_component_rows],
        "virtual_component_sizes": virtual_graph["component_sizes"],
        "virtual_graft_candidate_count": observable_values[
            "virtual_graft_candidate_count"
        ],
        "left_right_graft_bridge_candidate_count": observable_values[
            "left_right_graft_bridge_candidate_count"
        ],
        "shortest_path_words": [
            list(tuple(row[column] for column in WORD_COLUMNS if row[column] != -1))
            for row in bridge_path_rows[:3]
        ],
        "shortest_graft_path_length": observable_values["shortest_graft_path_length"],
        "gate_profile": {
            "word": list(NO_REPAIR_GATE_WORD),
            "variation": observable_values["gate_word_variation"],
            "closed_paths": observable_values["gate_word_closed_path_count"],
            "templates": observable_values["gate_word_template_count"],
        },
        "graft_table_sha256": sha_array(graft_table),
        "mode_table_sha256": sha_array(mode_table),
        "path_table_sha256": sha_array(path_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    graft = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge@1",
        "object": "d20",
        "comparison_rule": {
            "parent": BOUNDARY_BRIDGE_REPORT.relative_to(ROOT).as_posix(),
            "native_good_cell_filter": [
                "delta2 and variation <= 223",
                "native trace contains 31--28 or 50--34",
                "first_return_closed_path_count > 0",
            ],
            "virtual_graft_cell_filter": [
                "delta2 and variation <= 223",
                "native trace contains neither 31--28 nor 50--34",
                "first_return_closed_path_count > 0",
                "admit exactly one virtual repair edge, either 31--28 or 50--34",
            ],
        },
        "summary": {
            "native_left_to_right_path_exists": observable_values[
                "native_left_to_right_path_exists"
            ],
            "virtual_left_to_right_path_exists": observable_values[
                "virtual_left_to_right_path_exists"
            ],
            "virtual_graft_candidate_count": observable_values[
                "virtual_graft_candidate_count"
            ],
            "left_right_graft_bridge_candidate_count": observable_values[
                "left_right_graft_bridge_candidate_count"
            ],
            "shortest_path_length": observable_values["shortest_graft_path_length"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_VIRTUAL_GRAFT_BRIDGE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "native repaired closed-positive cells remain separated between the left and right boundary components",
            "closed-positive no-repair cells provide 422 admissible virtual graft carriers",
            "adding either a single virtual 31--28 or a single virtual 50--34 repair edge merges the boundary components",
            "the shortest merger is the three-word path left boundary, no-repair gate, right boundary",
            "the gate word preserves closed/template mass with 30 closed paths and 9 normalized templates",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The virtual-graft bridge layer keeps the certified boundary-pair "
            "native graph fixed, then admits only no-repair words that still "
            "satisfy delta2, variation <= 223, and closed positivity. There "
            "are 422 such virtual graft carriers. The native repaired graph "
            "has 562 cells, 1,694 edges, and separated left/right components "
            "of sizes 347 and 185. Adding either one virtual 31--28 repair "
            "edge or one virtual 50--34 repair edge to the closed-positive "
            "no-repair carriers yields a 984-node graph with 3,134 edges and "
            "23 components; the boundary components merge into a 925-cell "
            "component. The shortest certified graft path is left boundary -> "
            "no-repair gate -> right boundary, and the gate preserves 30 "
            "closed paths and 9 normalized tail templates."
        ),
        "stage_protocol": {
            "draft": "hold the boundary-pair native graph fixed and add only virtual repair-edge carriers",
            "witness": "enumerate closed-positive no-repair cells and one-edit adjacency to native components",
            "coherence": "compare native separation with single-edge 31--28 and 50--34 graft modes",
            "closure": "certify that each single virtual repair edge mode merges the boundary pair through a closed/template-preserving gate",
            "emit": "emit graft cells, mode table, path table, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "boundary_bridge_report": input_entry(
                BOUNDARY_BRIDGE_REPORT,
                {
                    "status": boundary_report.get("status"),
                    "certificate_sha256": boundary_report.get("certificate_sha256"),
                },
            ),
            "boundary_bridge_certificate": input_entry(BOUNDARY_BRIDGE_CERTIFICATE),
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
            "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge.json"
            ),
            "aperture_closure_tail_virtual_graft_cells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_virtual_graft_cells.csv"
            ),
            "aperture_closure_tail_virtual_graft_modes_csv": relpath(
                OUT_DIR / "aperture_closure_tail_virtual_graft_modes.csv"
            ),
            "aperture_closure_tail_virtual_graft_paths_csv": relpath(
                OUT_DIR / "aperture_closure_tail_virtual_graft_paths.csv"
            ),
            "aperture_closure_tail_virtual_graft_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_virtual_graft_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all virtual graft carriers inside the certified radius-three boundary-pair union",
                "single virtual repair-edge modes 31--28 and 50--34",
                "left/right component merger after virtual graft admission",
                "closed/template preservation on the shortest gate bridge",
            ],
            "does_not_certify_because_not_required": [
                "that virtual grafting is an actual native rewrite edge",
                "all-four or endpoint-13-free exactness on the shortest gate",
                "multi-graft optimization outside the declared radius-three side union",
                "compiler lowering behavior",
            ],
        },
        "next_highest_yield_item": (
            "Realize the virtual repair edge natively: search a minimal "
            "word-level or rewrite-complex patch that turns the gate's virtual "
            "31--28/50--34 support into an actual trace edge while retaining "
            "the 30-closure, 9-template gate profile."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified boundary-bridge artifacts",
            "reclassify radius-three side-neighborhood words under native and virtual-graft filters",
            "compare native, virtual-31--28, and virtual-50--34 component connectivity",
            "check the shortest graft path and gate closure/template profile",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge": graft,
        "aperture_closure_tail_virtual_graft_cells_csv": csv_text(
            GRAFT_COLUMNS,
            graft_rows,
        ),
        "aperture_closure_tail_virtual_graft_modes_csv": csv_text(
            MODE_COLUMNS,
            graph_mode_rows,
        ),
        "aperture_closure_tail_virtual_graft_paths_csv": csv_text(
            PATH_COLUMNS,
            bridge_path_rows,
        ),
        "aperture_closure_tail_virtual_graft_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "graft_table": graft_table,
        "mode_table": mode_table,
        "path_table": path_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge.json",
        payloads["signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge"],
    )
    (OUT_DIR / "aperture_closure_tail_virtual_graft_cells.csv").write_text(
        payloads["aperture_closure_tail_virtual_graft_cells_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_virtual_graft_modes.csv").write_text(
        payloads["aperture_closure_tail_virtual_graft_modes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_virtual_graft_paths.csv").write_text(
        payloads["aperture_closure_tail_virtual_graft_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_virtual_graft_observables.csv").write_text(
        payloads["aperture_closure_tail_virtual_graft_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_tables.npz",
        graft_table=payloads["graft_table"],
        mode_table=payloads["mode_table"],
        path_table=payloads["path_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate"
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
