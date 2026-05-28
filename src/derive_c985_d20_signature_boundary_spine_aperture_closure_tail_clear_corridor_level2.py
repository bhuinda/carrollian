from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path
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
        ANCHOR_WORDS,
        CELL_COMPLEX_EDGES,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        MIN_WORD_LENGTH,
        OBSERVABLE_COLUMNS,
        OUT_DIR as CLEAR_CORRIDOR_DIR,
        PREFIX_FIXED,
        REWRITE_COMPLEX_EDGES,
        STATUS as CLEAR_CORRIDOR_STATUS,
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
        ANCHOR_WORDS,
        CELL_COMPLEX_EDGES,
        MAX_TRACE_NODES,
        MAX_WORD_LENGTH,
        MIN_WORD_LENGTH,
        OBSERVABLE_COLUMNS,
        OUT_DIR as CLEAR_CORRIDOR_DIR,
        PREFIX_FIXED,
        REWRITE_COMPLEX_EDGES,
        STATUS as CLEAR_CORRIDOR_STATUS,
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
    "c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CLEAR_CORRIDOR_LEVEL2_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CLEAR_CORRIDOR_REPORT = CLEAR_CORRIDOR_DIR / "report.json"
CLEAR_CORRIDOR_CERTIFICATE = (
    CLEAR_CORRIDOR_DIR
    / "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate.json"
)
DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2.py"
)

MAX_ANCHOR_EDIT_RADIUS = 2
CLASS_GOOD = 0
CLASS_NO_REPAIR_GATE = 1

CELL_COLUMNS = [
    "level2_cell_id",
    "component_id",
    "anchor_edit_radius",
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
    "anchor_selected_flag",
    "anchor_oversplitter_flag",
    "gate_path_flag",
]

COMPONENT_COLUMNS = [
    "component_id",
    "component_kind_code",
    "cell_count",
    "edge_count",
    "selected_anchor_flag",
    "oversplitter_anchor_count",
    "target_cell_count",
    "clear_cell_count",
    "endpoint13_heavy_cell_count",
    "min_variation",
    "max_endpoint13_path_count",
    "selected_to_oversplitter_bridge_flag",
]

GATE_PATH_COLUMNS = [
    "gate_path_id",
    "path_step_index",
    "word_class_code",
    "gate_flag",
    "anchor_edit_radius",
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

LEVEL2_OBSERVABLE_CODES = {
    "radius0_word_count": 0,
    "radius1_word_count": 1,
    "radius2_word_count": 2,
    "radius2_total_word_count": 3,
    "trace_valid_word_count": 4,
    "delta2_variation_le223_word_count": 5,
    "repair_chord_candidate_count": 6,
    "no_repair_gate_candidate_count": 7,
    "no_closed_repair_candidate_count": 8,
    "good_cell_count": 9,
    "good_edge_count": 10,
    "good_component_count": 11,
    "selected_component_cell_count": 12,
    "oversplitter_component_cell_count": 13,
    "target_cell_count": 14,
    "radius2_new_target_count": 15,
    "clear_cell_count": 16,
    "oversplitter_component_target_count": 17,
    "selected_to_oversplitter_good_path_exists": 18,
    "no_repair_one_gate_path_count": 19,
    "no_repair_gate_path_length_edges": 20,
    "no_repair_gate_word_variation": 21,
    "no_repair_gate_word_closed_paths": 22,
    "no_repair_gate_word_template_count": 23,
}


def radius_words() -> dict[tuple[int, ...], int]:
    radius_by_word = {word: 0 for word in ANCHOR_WORDS}
    frontier = set(radius_by_word)
    for radius in range(1, MAX_ANCHOR_EDIT_RADIUS + 1):
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


def metric_context() -> tuple[dict[int, int], Any, dict[tuple[int, int], dict[str, int]], Any]:
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
    return atom_to_symbol, carrier_adjacency, rewrite_edge_by_pair, assoc_by_word


def closure_profile(
    word: tuple[int, ...],
    carrier_adjacency: Any,
) -> dict[str, int]:
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
    _atom_to_symbol, carrier_adjacency, rewrite_edge_by_pair, assoc_by_word = (
        metric_context()
    )
    stats: Counter[str] = Counter()
    for radius in range(MAX_ANCHOR_EDIT_RADIUS + 1):
        stats[f"radius{radius}_word_count"] = sum(
            int(value == radius) for value in radius_by_word.values()
        )
    stats["radius2_total_word_count"] = len(radius_by_word)

    rows: dict[tuple[int, ...], dict[str, Any]] = {}
    for word, radius in sorted(radius_by_word.items(), key=lambda item: item[0]):
        row: dict[str, Any] = {
            "word": word,
            "anchor_edit_radius": radius,
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
        has_31_28 = contains_undirected_edge(trace, 31, 28)
        has_50_34 = contains_undirected_edge(trace, 50, 34)
        row.update(
            {
                "trace": trace,
                "trace_signature_total_variation": variation,
                "metric_gromov_delta_twice": delta_twice,
                "has_repair_chord_flag": int(has_31_28 or has_50_34),
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
        if not (has_31_28 or has_50_34):
            stats["no_repair_gate_candidate_count"] += 1
            row.update(closure_profile(word, carrier_adjacency))
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
        stats["good_cell_count"] += 1
        row["class"] = "good"
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
        rows[word] = row
    return rows, dict(stats)


def build_good_graph(
    rows: dict[tuple[int, ...], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[set[int]], dict[tuple[int, ...], int], int]:
    good_words = sorted(
        [word for word, row in rows.items() if row.get("class") == "good"],
        key=lambda word: (
            rows[word]["anchor_edit_radius"],
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
        if ANCHOR_WORDS[0] in words:
            kind = 0
        elif any(word in words for word in ANCHOR_WORDS[1:]):
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
                "level2_cell_id": cell_id,
                "component_id": component_id_by_cell[cell_id],
                "anchor_edit_radius": row["anchor_edit_radius"],
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
                "anchor_selected_flag": int(word == ANCHOR_WORDS[0]),
                "anchor_oversplitter_flag": int(word in ANCHOR_WORDS[1:]),
                "gate_path_flag": 0,
            }
        )

    return cell_rows, components, cell_id_by_word, edge_count


def one_gate_path(
    rows: dict[tuple[int, ...], dict[str, Any]],
    target: tuple[int, ...],
) -> list[tuple[int, ...]]:
    allowed = {
        word
        for word, row in rows.items()
        if row.get("class") in {"good", "no_repair"}
    }
    start = ANCHOR_WORDS[0]
    queue = deque([(start, 0)])
    previous: dict[tuple[tuple[int, ...], int], tuple[tuple[int, ...], int] | None] = {
        (start, 0): None
    }
    found: tuple[tuple[int, ...], int] | None = None
    while queue:
        word, gate_count = queue.popleft()
        if word == target:
            found = (word, gate_count)
            break
        for neighbor in sorted(one_edit_neighbors(word), key=lambda value: (len(value), value)):
            if neighbor not in allowed:
                continue
            cost = 0 if rows[neighbor]["class"] == "good" else 1
            next_gate_count = gate_count + cost
            key = (neighbor, next_gate_count)
            if next_gate_count <= 1 and key not in previous:
                previous[key] = (word, gate_count)
                queue.append(key)
    if found is None:
        return []
    path = []
    current: tuple[tuple[int, ...], int] | None = found
    while current is not None:
        path.append(current[0])
        current = previous[current]
    return list(reversed(path))


def build_payload_rows() -> dict[str, Any]:
    rows, stats = evaluate_words()
    cell_rows, components, cell_id_by_word, good_edge_count = build_good_graph(rows)
    component_id_by_cell = {
        row["level2_cell_id"]: row["component_id"] for row in cell_rows
    }
    cell_by_id = {row["level2_cell_id"]: row for row in cell_rows}

    gate_paths = [one_gate_path(rows, ANCHOR_WORDS[1]), one_gate_path(rows, ANCHOR_WORDS[2])]
    gate_path_words = {word for path in gate_paths for word in path}
    for row in cell_rows:
        word = tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)
        if word in gate_path_words:
            row["gate_path_flag"] = 1

    component_rows = []
    for component_id, component in enumerate(components):
        cells = [cell_by_id[cell_id] for cell_id in sorted(component)]
        words = {
            tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)
            for row in cells
        }
        selected_flag = int(ANCHOR_WORDS[0] in words)
        oversplitter_count = sum(int(word in words) for word in ANCHOR_WORDS[1:])
        if selected_flag:
            kind = 0
        elif oversplitter_count:
            kind = 1
        else:
            kind = 2
        edge_count = 0
        word_set = set(words)
        for word in word_set:
            for neighbor in one_edit_neighbors(word):
                if neighbor in word_set and word < neighbor:
                    edge_count += 1
        component_rows.append(
            {
                "component_id": component_id,
                "component_kind_code": kind,
                "cell_count": len(cells),
                "edge_count": edge_count,
                "selected_anchor_flag": selected_flag,
                "oversplitter_anchor_count": oversplitter_count,
                "target_cell_count": sum(
                    row["exact24_six_all_four_flag"] for row in cells
                ),
                "clear_cell_count": sum(row["clear_flag"] for row in cells),
                "endpoint13_heavy_cell_count": sum(
                    int(row["tail_entry_13_path_count"] > 0) for row in cells
                ),
                "min_variation": min(
                    row["trace_signature_total_variation"] for row in cells
                ),
                "max_endpoint13_path_count": max(
                    row["tail_entry_13_path_count"] for row in cells
                ),
                "selected_to_oversplitter_bridge_flag": int(
                    selected_flag and oversplitter_count > 0
                ),
            }
        )

    path_rows = []
    for path_id, path in enumerate(gate_paths):
        for step_index, word in enumerate(path):
            row = rows[word]
            class_code = CLASS_GOOD if row["class"] == "good" else CLASS_NO_REPAIR_GATE
            component_id = -1
            if word in cell_id_by_word:
                component_id = component_id_by_cell[cell_id_by_word[word]]
            path_rows.append(
                {
                    "gate_path_id": path_id,
                    "path_step_index": step_index,
                    "word_class_code": class_code,
                    "gate_flag": int(class_code == CLASS_NO_REPAIR_GATE),
                    "anchor_edit_radius": row["anchor_edit_radius"],
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
                    "repair_chord_flag": row["has_repair_chord_flag"],
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

    selected_component = next(
        row for row in component_rows if row["selected_anchor_flag"] == 1
    )
    oversplitter_component = next(
        row for row in component_rows if row["oversplitter_anchor_count"] == 2
    )
    target_rows = [row for row in cell_rows if row["exact24_six_all_four_flag"] == 1]
    gate_rows = [row for row in path_rows if row["gate_flag"] == 1]
    observable_values = {
        "radius0_word_count": stats["radius0_word_count"],
        "radius1_word_count": stats["radius1_word_count"],
        "radius2_word_count": stats["radius2_word_count"],
        "radius2_total_word_count": stats["radius2_total_word_count"],
        "trace_valid_word_count": stats["trace_valid_word_count"],
        "delta2_variation_le223_word_count": stats[
            "delta2_variation_le223_word_count"
        ],
        "repair_chord_candidate_count": stats["repair_chord_candidate_count"],
        "no_repair_gate_candidate_count": stats["no_repair_gate_candidate_count"],
        "no_closed_repair_candidate_count": stats[
            "no_closed_repair_candidate_count"
        ],
        "good_cell_count": len(cell_rows),
        "good_edge_count": good_edge_count,
        "good_component_count": len(component_rows),
        "selected_component_cell_count": selected_component["cell_count"],
        "oversplitter_component_cell_count": oversplitter_component["cell_count"],
        "target_cell_count": len(target_rows),
        "radius2_new_target_count": sum(
            int(row["anchor_edit_radius"] == 2) for row in target_rows
        ),
        "clear_cell_count": sum(row["clear_flag"] for row in cell_rows),
        "oversplitter_component_target_count": oversplitter_component[
            "target_cell_count"
        ],
        "selected_to_oversplitter_good_path_exists": int(
            selected_component["component_id"] == oversplitter_component["component_id"]
        ),
        "no_repair_one_gate_path_count": len(gate_paths),
        "no_repair_gate_path_length_edges": len(gate_paths[0]) - 1,
        "no_repair_gate_word_variation": gate_rows[0][
            "trace_signature_total_variation"
        ],
        "no_repair_gate_word_closed_paths": gate_rows[0][
            "first_return_closed_path_count"
        ],
        "no_repair_gate_word_template_count": gate_rows[0][
            "normalized_tail_template_count"
        ],
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": LEVEL2_OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    return {
        "stats": stats,
        "observable_values": observable_values,
        "cell_rows": cell_rows,
        "component_rows": component_rows,
        "gate_path_rows": path_rows,
        "observable_rows": observable_rows,
        "gate_paths": gate_paths,
    }


def build_payloads() -> dict[str, Any]:
    clear_report = load_json(CLEAR_CORRIDOR_REPORT)
    clear_certificate = load_json(CLEAR_CORRIDOR_CERTIFICATE)
    payload_rows = build_payload_rows()
    cell_rows = payload_rows["cell_rows"]
    component_rows = payload_rows["component_rows"]
    gate_path_rows = payload_rows["gate_path_rows"]
    observable_rows = payload_rows["observable_rows"]
    observable_values = payload_rows["observable_values"]

    cell_table = table_from_rows(CELL_COLUMNS, cell_rows)
    component_table = table_from_rows(COMPONENT_COLUMNS, component_rows)
    gate_path_table = table_from_rows(GATE_PATH_COLUMNS, gate_path_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    selected_component = next(
        row for row in component_rows if row["selected_anchor_flag"] == 1
    )
    oversplitter_component = next(
        row for row in component_rows if row["oversplitter_anchor_count"] == 2
    )
    target_rows = [row for row in cell_rows if row["exact24_six_all_four_flag"] == 1]
    gate_rows = [row for row in gate_path_rows if row["gate_flag"] == 1]
    checks = {
        "clear_corridor_report_certified": clear_report.get("status")
        == CLEAR_CORRIDOR_STATUS,
        "clear_corridor_certificate_certified": clear_certificate.get("status")
        == CLEAR_CORRIDOR_STATUS,
        "radius2_total_word_count_is_12754": observable_values[
            "radius2_total_word_count"
        ]
        == 12_754,
        "radius_shell_counts_are_expected": [
            observable_values["radius0_word_count"],
            observable_values["radius1_word_count"],
            observable_values["radius2_word_count"],
        ]
        == [3, 288, 12_463],
        "trace_valid_word_count_is_9625": observable_values[
            "trace_valid_word_count"
        ]
        == 9_625,
        "delta2_variation_le223_word_count_is_1436": observable_values[
            "delta2_variation_le223_word_count"
        ]
        == 1_436,
        "good_cell_count_is_138": len(cell_rows) == 138,
        "good_edge_count_is_377": observable_values["good_edge_count"] == 377,
        "good_components_are_81_55_1_1": [
            row["cell_count"] for row in component_rows
        ]
        == [81, 55, 1, 1],
        "selected_and_oversplitter_good_components_are_separate": observable_values[
            "selected_to_oversplitter_good_path_exists"
        ]
        == 0,
        "selected_component_has_all_targets": selected_component[
            "target_cell_count"
        ]
        == 9
        and oversplitter_component["target_cell_count"] == 0,
        "radius_two_adds_eight_exact_targets": observable_values[
            "radius2_new_target_count"
        ]
        == 8,
        "min_target_variation_is_137": min(
            row["trace_signature_total_variation"] for row in target_rows
        )
        == 137,
        "one_no_repair_gate_path_reaches_each_oversplitter": observable_values[
            "no_repair_one_gate_path_count"
        ]
        == 2
        and all(row["gate_flag"] == 1 for row in gate_rows)
        and len(gate_rows) == 2,
        "no_repair_gate_profile_is_185_30_9": (
            gate_rows[0]["trace_signature_total_variation"],
            gate_rows[0]["first_return_closed_path_count"],
            gate_rows[0]["normalized_tail_template_count"],
        )
        == (185, 30, 9),
        "cell_table_shape_matches_codebook": tuple(cell_table.shape)
        == (138, len(CELL_COLUMNS)),
        "component_table_shape_matches_codebook": tuple(component_table.shape)
        == (4, len(COMPONENT_COLUMNS)),
        "gate_path_table_shape_matches_codebook": tuple(gate_path_table.shape)
        == (10, len(GATE_PATH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(LEVEL2_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "radius_shell_counts": [
            observable_values["radius0_word_count"],
            observable_values["radius1_word_count"],
            observable_values["radius2_word_count"],
        ],
        "good_cell_count": len(cell_rows),
        "good_component_sizes": [row["cell_count"] for row in component_rows],
        "target_count": len(target_rows),
        "radius2_new_target_count": observable_values["radius2_new_target_count"],
        "min_target_variation": min(
            row["trace_signature_total_variation"] for row in target_rows
        ),
        "selected_component_id": selected_component["component_id"],
        "oversplitter_component_id": oversplitter_component["component_id"],
        "no_repair_gate_word": [
            gate_rows[0][column] for column in WORD_COLUMNS if gate_rows[0][column] != -1
        ],
        "no_repair_gate_profile": {
            "variation": gate_rows[0]["trace_signature_total_variation"],
            "closed_paths": gate_rows[0]["first_return_closed_path_count"],
            "template_count": gate_rows[0]["normalized_tail_template_count"],
            "endpoint_distribution": {
                "9": gate_rows[0]["tail_entry_9_path_count"],
                "10": gate_rows[0]["tail_entry_10_path_count"],
                "11": gate_rows[0]["tail_entry_11_path_count"],
                "13": gate_rows[0]["tail_entry_13_path_count"],
            },
        },
        "cell_table_sha256": sha_array(cell_table),
        "component_table_sha256": sha_array(component_table),
        "gate_path_table_sha256": sha_array(gate_path_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    level2 = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2@1",
        "object": "d20",
        "comparison_rule": {
            "parent": CLEAR_CORRIDOR_REPORT.relative_to(ROOT).as_posix(),
            "anchor_words": [list(word) for word in ANCHOR_WORDS],
            "radius": MAX_ANCHOR_EDIT_RADIUS,
            "good_cell_filters": [
                "word starts with x2,x1",
                "8 <= word_length <= 16",
                "metric_gromov_delta_twice = 2",
                "trace_signature_total_variation <= 223",
                "trace contains repair chord 31--28 or 50--34",
                "first_return_closed_path_count > 0",
            ],
            "gate_rule": [
                "allow at most one no-repair gate",
                "gate must keep delta2 and variation <= 223",
                "gate may lose repair-chord support",
            ],
        },
        "summary": {
            "good_cell_count": len(cell_rows),
            "good_component_count": len(component_rows),
            "target_cell_count": len(target_rows),
            "radius2_new_target_count": observable_values[
                "radius2_new_target_count"
            ],
            "selected_to_oversplitter_good_path_exists": observable_values[
                "selected_to_oversplitter_good_path_exists"
            ],
            "no_repair_one_gate_path_count": observable_values[
                "no_repair_one_gate_path_count"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CLEAR_CORRIDOR_LEVEL2_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "radius two around the three aperture anchors contains 12754 prefix-valid words and 138 good cells",
            "the good cell graph has four components; the selected component has 81 cells and the oversplitter component has 55",
            "radius two adds eight new exact 24-closure six-template all-four targets, all in the selected component at minimum variation 137",
            "no good path connects the selected component to the oversplitters",
            "one no-repair gate connects the selected component to each oversplitter, exposing the repair-chord seam rather than a certified good corridor",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The level-two clear-corridor search expands the three aperture "
            "anchors to 12,754 prefix-valid words. Under the good-cell filters "
            "there are 138 closed-positive delta2 repair-chord cells and 377 "
            "good edges. The good graph has four components of sizes 81, 55, "
            "1, and 1; the selected-lift component and oversplitter component "
            "remain separate. Radius two adds eight new exact 24-closure, "
            "six-template, all-four targets at minimum variation 137, all in "
            "the selected component. A one-gate graph that allows a single "
            "delta2 variation<=223 no-repair word connects the selected side "
            "to each oversplitter, with gate profile variation 185, 30 closures, "
            "and 9 templates. The seam is therefore the repair-chord support, "
            "not lack of exact targets on the selected side."
        ),
        "stage_protocol": {
            "draft": "expand the three clear-corridor anchors to radius two",
            "witness": "evaluate trace metrics, repair support, closures, templates, good cells, and no-repair gate paths",
            "coherence": "compare good components, exact targets, and one-gate connectivity",
            "closure": "certify radius-two exact targets and the remaining no-good-path separation from oversplitters",
            "emit": "emit level-two cells, components, gate paths, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "clear_corridor_report": input_entry(
                CLEAR_CORRIDOR_REPORT,
                {
                    "status": clear_report.get("status"),
                    "certificate_sha256": clear_report.get("certificate_sha256"),
                },
            ),
            "clear_corridor_certificate": input_entry(CLEAR_CORRIDOR_CERTIFICATE),
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
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2.json"
            ),
            "aperture_closure_tail_clear_corridor_level2_cells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_clear_corridor_level2_cells.csv"
            ),
            "aperture_closure_tail_clear_corridor_level2_components_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_clear_corridor_level2_components.csv"
            ),
            "aperture_closure_tail_clear_corridor_level2_gate_paths_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_clear_corridor_level2_gate_paths.csv"
            ),
            "aperture_closure_tail_clear_corridor_level2_observables_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_clear_corridor_level2_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "radius-two edits around the selected lift and two oversplitters",
                "all good cells satisfying delta2, variation <= 223, repair-chord support, and closed positivity in that radius",
                "that exact 24/six/all-four targets exist at variation 137 in the selected component",
                "that no good path reaches either oversplitter from the selected component",
                "that a one no-repair-gate path reaches each oversplitter",
            ],
            "does_not_certify_because_not_required": [
                "radius three or higher from the three-anchor set",
                "paths using no-closed, bad-metric, or trace-failure gates",
                "repairing the no-repair gate into a good cell",
                "global optimality outside the declared level-two corridor",
            ],
        },
        "next_highest_yield_item": (
            "Repair the no-repair gate: search local replacements of "
            "x4,x5,x1,x2,x5,x5,x2,x1,x4,x5 that restore repair-chord support "
            "while keeping the level-two variation-137 exact targets in view."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified radius-one clear-corridor artifacts",
            "enumerate radius-two aperture words around the three anchors",
            "classify good cells and no-repair gates",
            "check good-component separation and one-gate paths",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2": level2,
        "aperture_closure_tail_clear_corridor_level2_cells_csv": csv_text(
            CELL_COLUMNS,
            cell_rows,
        ),
        "aperture_closure_tail_clear_corridor_level2_components_csv": csv_text(
            COMPONENT_COLUMNS,
            component_rows,
        ),
        "aperture_closure_tail_clear_corridor_level2_gate_paths_csv": csv_text(
            GATE_PATH_COLUMNS,
            gate_path_rows,
        ),
        "aperture_closure_tail_clear_corridor_level2_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "cell_table": cell_table,
        "component_table": component_table,
        "gate_path_table": gate_path_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_clear_corridor_level2_cells.csv").write_text(
        payloads["aperture_closure_tail_clear_corridor_level2_cells_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_clear_corridor_level2_components.csv"
    ).write_text(
        payloads["aperture_closure_tail_clear_corridor_level2_components_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_clear_corridor_level2_gate_paths.csv").write_text(
        payloads["aperture_closure_tail_clear_corridor_level2_gate_paths_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_clear_corridor_level2_observables.csv"
    ).write_text(
        payloads["aperture_closure_tail_clear_corridor_level2_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_tables.npz",
        cell_table=payloads["cell_table"],
        component_table=payloads["component_table"],
        gate_path_table=payloads["gate_path_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate"
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
