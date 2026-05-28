from __future__ import annotations

import json
import math
from collections import Counter, deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        CELL_COLUMNS,
        COMPONENT_COLUMNS as SKIP_COMPONENT_COLUMNS,
        LEFT_REPAIR_BOUNDARY_WORD,
        MAX_WORD_LENGTH,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR as SKIP_WINDOW_DIR,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as SKIP_WINDOW_STATUS,
        THEOREM_ID as SKIP_WINDOW_THEOREM_ID,
        WORD_COLUMNS,
        csv_text,
        input_entry,
        load_json,
        one_edit_neighbors,
        padded,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        CELL_COLUMNS,
        COMPONENT_COLUMNS as SKIP_COMPONENT_COLUMNS,
        LEFT_REPAIR_BOUNDARY_WORD,
        MAX_WORD_LENGTH,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR as SKIP_WINDOW_DIR,
        RIGHT_REPAIR_BOUNDARY_WORD,
        STATUS as SKIP_WINDOW_STATUS,
        THEOREM_ID as SKIP_WINDOW_THEOREM_ID,
        WORD_COLUMNS,
        csv_text,
        input_entry,
        load_json,
        one_edit_neighbors,
        padded,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_REPAIRED_AUTOMATON_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SKIP_WINDOW_REPORT = SKIP_WINDOW_DIR / "report.json"
SKIP_WINDOW_CERTIFICATE = (
    SKIP_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate.json"
)
SKIP_WINDOW_TABLES = (
    SKIP_WINDOW_DIR
    / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_tables.npz"
)
SKIP_WINDOW_CELLS = SKIP_WINDOW_DIR / "aperture_closure_tail_skip_window_cells.csv"
SKIP_WINDOW_COMPONENTS = (
    SKIP_WINDOW_DIR / "aperture_closure_tail_skip_window_components.csv"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton.py"
)

SCALE = 10**12
EMBEDDING_RADIUS = 0.85

STATE_COLUMNS = [
    "automaton_state_id",
    "grammar_cell_id",
    "repaired_recurrent_class_id",
    "native_recurrent_class_id",
    "word_length",
    *WORD_COLUMNS,
    "degree",
    "native_neighbor_count",
    "derived_neighbor_count",
    "native_transition_degree",
    "derived_transition_degree",
    "native_repair_flag",
    "derived_repair_flag",
    "derived_only_flag",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
    "merged_recurrent_class_flag",
    "spectral_side_code",
]

TRANSITION_COLUMNS = [
    "transition_id",
    "reverse_transition_id",
    "undirected_edge_id",
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
    "derived_only_transition_flag",
    "boundary_path_edge_flag",
    "spectral_cut_edge_flag",
]

RECURRENT_CLASS_COLUMNS = [
    "repaired_recurrent_class_id",
    "state_count",
    "undirected_edge_count",
    "directed_transition_count",
    "native_state_count",
    "derived_only_state_count",
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
    "repaired_recurrent_class_id",
    "state_count",
    "undirected_edge_count",
    "lambda_2_x1e12",
    "lambda_3_x1e12",
    "spectral_gap_x1e12",
    "cut_edge_count",
    "derived_cut_edge_count",
    "positive_state_count",
    "negative_state_count",
    "positive_volume",
    "negative_volume",
    "cut_conductance_x1e12",
    "left_side_code",
    "gate_side_code",
    "right_side_code",
]

POINCARE_COLUMNS = [
    "poincare_point_id",
    "automaton_state_id",
    "repaired_recurrent_class_id",
    "spectral_side_code",
    "poincare_x_x1e12",
    "poincare_y_x1e12",
    "poincare_radius_x1e12",
    "fiedler_value_x1e12",
    "third_mode_value_x1e12",
    "left_boundary_flag",
    "right_boundary_flag",
    "gate_word_flag",
]

AUTOMATON_OBSERVABLE_CODES = {
    "state_count": 0,
    "undirected_edge_count": 1,
    "directed_transition_count": 2,
    "native_state_count": 3,
    "derived_only_state_count": 4,
    "native_recurrent_class_count": 5,
    "repaired_recurrent_class_count": 6,
    "merged_recurrent_class_size": 7,
    "merged_recurrent_class_edge_count": 8,
    "merged_native_state_count": 9,
    "merged_derived_only_state_count": 10,
    "native_transition_edge_count": 11,
    "derived_transition_edge_count": 12,
    "derived_only_transition_edge_count": 13,
    "boundary_path_edge_count": 14,
    "left_right_same_native_recurrent_class": 15,
    "left_right_same_repaired_recurrent_class": 16,
    "gate_in_merged_recurrent_class": 17,
    "spectral_cut_edge_count": 18,
    "spectral_cut_derived_edge_count": 19,
    "spectral_positive_state_count": 20,
    "spectral_negative_state_count": 21,
    "merged_lambda_2": 22,
    "merged_lambda_3": 23,
    "merged_spectral_gap": 24,
    "merged_cut_conductance": 25,
    "poincare_point_count": 26,
    "poincare_radius_max": 27,
    "poincare_diameter": 28,
    "left_gate_poincare_distance": 29,
    "gate_right_poincare_distance": 30,
    "left_right_poincare_distance": 31,
}

FLOAT_OBSERVABLES = {
    "merged_lambda_2",
    "merged_lambda_3",
    "merged_spectral_gap",
    "merged_cut_conductance",
    "poincare_radius_max",
    "poincare_diameter",
    "left_gate_poincare_distance",
    "gate_right_poincare_distance",
    "left_right_poincare_distance",
}


def scaled_float(value: float) -> int:
    canonical = float(f"{float(value):.9f}")
    return int(round(canonical * SCALE))


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def word_from_cell(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)


def edit_descriptor(
    source: tuple[int, ...],
    target: tuple[int, ...],
) -> tuple[int, int, int, int]:
    if len(source) == len(target):
        diffs = [
            index
            for index, (left, right) in enumerate(zip(source, target))
            if left != right
        ]
        if len(diffs) == 1:
            index = diffs[0]
            return 0, index, source[index], target[index]
    if len(target) == len(source) + 1:
        for index in range(len(target)):
            if target[:index] + target[index + 1 :] == source:
                return 1, index, -1, target[index]
    if len(source) == len(target) + 1:
        for index in range(len(source)):
            if source[:index] + source[index + 1 :] == target:
                return 2, index, source[index], -1
    raise AssertionError(f"not a one-edit transition: {source} -> {target}")


def connected_components(
    nodes: set[int],
    adjacency: dict[int, set[int]],
) -> list[list[int]]:
    seen: set[int] = set()
    components: list[list[int]] = []
    for node in sorted(nodes):
        if node in seen:
            continue
        stack = [node]
        seen.add(node)
        component: list[int] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor in nodes and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda values: (-len(values), values[0]))


def poincare_distance(point_a: np.ndarray, point_b: np.ndarray) -> float:
    distance_squared = float(np.sum((point_a - point_b) ** 2))
    radius_a = float(np.sum(point_a**2))
    radius_b = float(np.sum(point_b**2))
    denominator = (1.0 - radius_a) * (1.0 - radius_b)
    argument = 1.0 + (2.0 * distance_squared / denominator)
    return math.acosh(max(1.0, argument))


def orient_vector(vector: np.ndarray, anchor_index: int) -> np.ndarray:
    if float(vector[anchor_index]) < 0.0:
        return -vector
    if abs(float(vector[anchor_index])) > 1e-14:
        return vector
    largest = int(np.argmax(np.abs(vector)))
    return -vector if float(vector[largest]) < 0.0 else vector


def load_skip_window_rows() -> dict[str, Any]:
    tables = np.load(SKIP_WINDOW_TABLES, allow_pickle=False)
    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    cell_rows = sorted(
        table_rows(cell_table, CELL_COLUMNS),
        key=lambda row: row["grammar_cell_id"],
    )
    component_rows = table_rows(component_table, SKIP_COMPONENT_COLUMNS)
    return {
        "cell_rows": cell_rows,
        "component_rows": component_rows,
        "cell_table": cell_table,
        "component_table": component_table,
    }


def build_edges(
    words: list[tuple[int, ...]],
    cell_id_by_word: dict[tuple[int, ...], int],
) -> tuple[set[tuple[int, int]], dict[int, set[int]]]:
    edge_set: set[tuple[int, int]] = set()
    adjacency: dict[int, set[int]] = {index: set() for index in range(len(words))}
    for word, source_id in cell_id_by_word.items():
        for neighbor in set(one_edit_neighbors(word)):
            target_id = cell_id_by_word.get(neighbor)
            if target_id is None or target_id == source_id:
                continue
            edge = tuple(sorted((source_id, target_id)))
            edge_set.add(edge)
            adjacency[source_id].add(target_id)
            adjacency[target_id].add(source_id)
    return edge_set, adjacency


def spectral_geometry(
    rows_by_state: dict[int, dict[str, int]],
    words: list[tuple[int, ...]],
    edges: set[tuple[int, int]],
    merged_class_id: int,
    left_id: int,
    gate_id: int,
    right_id: int,
) -> dict[str, Any]:
    component_nodes = sorted(
        state_id
        for state_id, row in rows_by_state.items()
        if row["component_id"] == merged_class_id
    )
    position = {state_id: index for index, state_id in enumerate(component_nodes)}
    node_count = len(component_nodes)
    adjacency = np.zeros((node_count, node_count), dtype=np.float64)
    for source, target in sorted(edges):
        if source not in position or target not in position:
            continue
        i = position[source]
        j = position[target]
        adjacency[i, j] = 1.0
        adjacency[j, i] = 1.0
    degrees = adjacency.sum(axis=1)
    inv_sqrt_degree = np.diag(1.0 / np.sqrt(degrees))
    laplacian = np.eye(node_count) - inv_sqrt_degree @ adjacency @ inv_sqrt_degree
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    order = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    left_position = position[left_id]
    gate_position = position[gate_id]
    right_position = position[right_id]
    fiedler = orient_vector(eigenvectors[:, 1], left_position)
    third_mode = orient_vector(eigenvectors[:, 2], gate_position)
    side_by_state = {
        state_id: (1 if float(fiedler[position[state_id]]) >= 0.0 else -1)
        for state_id in component_nodes
    }

    cut_edges: set[tuple[int, int]] = set()
    derived_cut_edges = 0
    positive_volume = 0
    negative_volume = 0
    for state_id in component_nodes:
        degree = int(degrees[position[state_id]])
        if side_by_state[state_id] == 1:
            positive_volume += degree
        else:
            negative_volume += degree
    for source, target in sorted(edges):
        if source not in position or target not in position:
            continue
        if side_by_state[source] == side_by_state[target]:
            continue
        cut_edges.add((source, target))
        if (
            rows_by_state[source]["derived_only_flag"]
            or rows_by_state[target]["derived_only_flag"]
        ):
            derived_cut_edges += 1

    coordinates = np.column_stack([fiedler, third_mode])
    norms = np.linalg.norm(coordinates, axis=1)
    max_norm = float(np.max(norms))
    if max_norm > 0.0:
        coordinates = coordinates / max_norm * EMBEDDING_RADIUS
    radii = np.linalg.norm(coordinates, axis=1)

    diameter = -1.0
    diameter_pair = (-1, -1)
    for i in range(node_count):
        for j in range(i + 1, node_count):
            distance = poincare_distance(coordinates[i], coordinates[j])
            if distance > diameter:
                diameter = distance
                diameter_pair = (component_nodes[i], component_nodes[j])

    poincare_rows = []
    for point_id, state_id in enumerate(component_nodes):
        index = position[state_id]
        row = rows_by_state[state_id]
        poincare_rows.append(
            {
                "poincare_point_id": point_id,
                "automaton_state_id": state_id,
                "repaired_recurrent_class_id": merged_class_id,
                "spectral_side_code": side_by_state[state_id],
                "poincare_x_x1e12": scaled_float(coordinates[index, 0]),
                "poincare_y_x1e12": scaled_float(coordinates[index, 1]),
                "poincare_radius_x1e12": scaled_float(radii[index]),
                "fiedler_value_x1e12": scaled_float(fiedler[index]),
                "third_mode_value_x1e12": scaled_float(third_mode[index]),
                "left_boundary_flag": row["left_boundary_flag"],
                "right_boundary_flag": row["right_boundary_flag"],
                "gate_word_flag": row["gate_word_flag"],
            }
        )

    return {
        "component_nodes": component_nodes,
        "side_by_state": side_by_state,
        "cut_edges": cut_edges,
        "poincare_rows": poincare_rows,
        "spectral_row": {
            "spectral_cut_id": 0,
            "repaired_recurrent_class_id": merged_class_id,
            "state_count": node_count,
            "undirected_edge_count": int(np.sum(adjacency) // 2),
            "lambda_2_x1e12": scaled_float(eigenvalues[1]),
            "lambda_3_x1e12": scaled_float(eigenvalues[2]),
            "spectral_gap_x1e12": scaled_float(eigenvalues[1]),
            "cut_edge_count": len(cut_edges),
            "derived_cut_edge_count": derived_cut_edges,
            "positive_state_count": sum(
                1 for state_id in component_nodes if side_by_state[state_id] == 1
            ),
            "negative_state_count": sum(
                1 for state_id in component_nodes if side_by_state[state_id] == -1
            ),
            "positive_volume": int(positive_volume),
            "negative_volume": int(negative_volume),
            "cut_conductance_x1e12": scaled_float(
                len(cut_edges) / min(positive_volume, negative_volume)
            ),
            "left_side_code": side_by_state[left_id],
            "gate_side_code": side_by_state[gate_id],
            "right_side_code": side_by_state[right_id],
        },
        "poincare_summary": {
            "poincare_radius_max_x1e12": scaled_float(float(np.max(radii))),
            "poincare_diameter_x1e12": scaled_float(diameter),
            "poincare_diameter_state_ids": [int(value) for value in diameter_pair],
            "left_gate_poincare_distance_x1e12": scaled_float(
                poincare_distance(coordinates[left_position], coordinates[gate_position])
            ),
            "gate_right_poincare_distance_x1e12": scaled_float(
                poincare_distance(coordinates[gate_position], coordinates[right_position])
            ),
            "left_right_poincare_distance_x1e12": scaled_float(
                poincare_distance(coordinates[left_position], coordinates[right_position])
            ),
        },
    }


def build_payload_rows() -> dict[str, Any]:
    skip_rows = load_skip_window_rows()
    cell_rows = skip_rows["cell_rows"]
    component_rows = skip_rows["component_rows"]
    words = [word_from_cell(row) for row in cell_rows]
    cell_id_by_word = {word: index for index, word in enumerate(words)}
    rows_by_state = {row["grammar_cell_id"]: row for row in cell_rows}
    edges, adjacency = build_edges(words, cell_id_by_word)

    left_id = cell_id_by_word[LEFT_REPAIR_BOUNDARY_WORD]
    gate_id = cell_id_by_word[NO_REPAIR_GATE_WORD]
    right_id = cell_id_by_word[RIGHT_REPAIR_BOUNDARY_WORD]
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

    edge_class_counts: Counter[str] = Counter()
    boundary_path_edges = {
        tuple(sorted((left_id, gate_id))),
        tuple(sorted((gate_id, right_id))),
    }
    for source, target in edges:
        source_row = rows_by_state[source]
        target_row = rows_by_state[target]
        if source_row["native_repair_flag"] and target_row["native_repair_flag"]:
            edge_class_counts["native_transition_edge_count"] += 1
        if source_row["derived_only_flag"] or target_row["derived_only_flag"]:
            edge_class_counts["derived_transition_edge_count"] += 1
        if source_row["derived_only_flag"] and target_row["derived_only_flag"]:
            edge_class_counts["derived_only_transition_edge_count"] += 1
        if (source, target) in boundary_path_edges:
            edge_class_counts["boundary_path_edge_count"] += 1

    transition_rows = []
    for edge_id, (source, target) in enumerate(sorted(edges)):
        source_row = rows_by_state[source]
        target_row = rows_by_state[target]
        native_transition = int(
            source_row["native_repair_flag"] and target_row["native_repair_flag"]
        )
        derived_transition = int(
            source_row["derived_only_flag"] or target_row["derived_only_flag"]
        )
        derived_only_transition = int(
            source_row["derived_only_flag"] and target_row["derived_only_flag"]
        )
        boundary_path = int((source, target) in boundary_path_edges)
        spectral_cut = int((source, target) in cut_edges)
        base_transition_id = 2 * edge_id
        for offset, (direct_source, direct_target) in enumerate(
            [(source, target), (target, source)]
        ):
            edit_kind, edit_position, source_symbol, target_symbol = edit_descriptor(
                words[direct_source],
                words[direct_target],
            )
            transition_rows.append(
                {
                    "transition_id": base_transition_id + offset,
                    "reverse_transition_id": base_transition_id + (1 - offset),
                    "undirected_edge_id": edge_id,
                    "source_state_id": direct_source,
                    "target_state_id": direct_target,
                    "source_grammar_cell_id": direct_source,
                    "target_grammar_cell_id": direct_target,
                    "edit_kind_code": edit_kind,
                    "edit_position": edit_position,
                    "source_symbol_id": source_symbol,
                    "target_symbol_id": target_symbol,
                    "native_transition_flag": native_transition,
                    "derived_transition_flag": derived_transition,
                    "derived_only_transition_flag": derived_only_transition,
                    "boundary_path_edge_flag": boundary_path,
                    "spectral_cut_edge_flag": spectral_cut,
                }
            )

    transition_degree = Counter()
    native_transition_degree = Counter()
    derived_transition_degree = Counter()
    native_neighbor_count = Counter()
    derived_neighbor_count = Counter()
    for source, target in sorted(edges):
        for state_id, neighbor_id in [(source, target), (target, source)]:
            transition_degree[state_id] += 1
            if rows_by_state[neighbor_id]["native_repair_flag"]:
                native_neighbor_count[state_id] += 1
            if rows_by_state[neighbor_id]["derived_only_flag"]:
                derived_neighbor_count[state_id] += 1
            if (
                rows_by_state[source]["native_repair_flag"]
                and rows_by_state[target]["native_repair_flag"]
            ):
                native_transition_degree[state_id] += 1
            if (
                rows_by_state[source]["derived_only_flag"]
                or rows_by_state[target]["derived_only_flag"]
            ):
                derived_transition_degree[state_id] += 1

    state_rows = []
    for row in cell_rows:
        state_id = row["grammar_cell_id"]
        word = words[state_id]
        state_rows.append(
            {
                "automaton_state_id": state_id,
                "grammar_cell_id": state_id,
                "repaired_recurrent_class_id": row["component_id"],
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
                "native_transition_degree": native_transition_degree[state_id],
                "derived_transition_degree": derived_transition_degree[state_id],
                "native_repair_flag": row["native_repair_flag"],
                "derived_repair_flag": row["derived_repair_flag"],
                "derived_only_flag": row["derived_only_flag"],
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

    repaired_class_rows = []
    for component in sorted(component_rows, key=lambda row: row["component_id"]):
        class_id = component["component_id"]
        node_set = {
            state_id
            for state_id, row in rows_by_state.items()
            if row["component_id"] == class_id
        }
        edge_count = sum(
            1 for source, target in edges if source in node_set and target in node_set
        )
        repaired_class_rows.append(
            {
                "repaired_recurrent_class_id": class_id,
                "state_count": len(node_set),
                "undirected_edge_count": edge_count,
                "directed_transition_count": 2 * edge_count,
                "native_state_count": sum(
                    rows_by_state[state_id]["native_repair_flag"]
                    for state_id in node_set
                ),
                "derived_only_state_count": sum(
                    rows_by_state[state_id]["derived_only_flag"]
                    for state_id in node_set
                ),
                "left_boundary_flag": int(left_id in node_set),
                "right_boundary_flag": int(right_id in node_set),
                "gate_word_flag": int(gate_id in node_set),
                "merged_boundary_flag": int(left_id in node_set and right_id in node_set),
                "spectral_certified_flag": int(class_id == merged_class_id),
            }
        )

    spectral_row = spectral["spectral_row"]
    poincare_summary = spectral["poincare_summary"]
    observable_values = {
        "state_count": len(state_rows),
        "undirected_edge_count": len(edges),
        "directed_transition_count": len(transition_rows),
        "native_state_count": sum(row["native_repair_flag"] for row in state_rows),
        "derived_only_state_count": sum(row["derived_only_flag"] for row in state_rows),
        "native_recurrent_class_count": len(native_class_rows),
        "repaired_recurrent_class_count": len(repaired_class_rows),
        "merged_recurrent_class_size": spectral_row["state_count"],
        "merged_recurrent_class_edge_count": spectral_row["undirected_edge_count"],
        "merged_native_state_count": next(
            row["native_state_count"]
            for row in repaired_class_rows
            if row["repaired_recurrent_class_id"] == merged_class_id
        ),
        "merged_derived_only_state_count": next(
            row["derived_only_state_count"]
            for row in repaired_class_rows
            if row["repaired_recurrent_class_id"] == merged_class_id
        ),
        "native_transition_edge_count": edge_class_counts[
            "native_transition_edge_count"
        ],
        "derived_transition_edge_count": edge_class_counts[
            "derived_transition_edge_count"
        ],
        "derived_only_transition_edge_count": edge_class_counts[
            "derived_only_transition_edge_count"
        ],
        "boundary_path_edge_count": edge_class_counts["boundary_path_edge_count"],
        "left_right_same_native_recurrent_class": int(
            native_class_id_by_state.get(left_id) == native_class_id_by_state.get(right_id)
        ),
        "left_right_same_repaired_recurrent_class": int(
            rows_by_state[left_id]["component_id"] == rows_by_state[right_id]["component_id"]
        ),
        "gate_in_merged_recurrent_class": int(
            rows_by_state[gate_id]["component_id"] == merged_class_id
        ),
        "spectral_cut_edge_count": spectral_row["cut_edge_count"],
        "spectral_cut_derived_edge_count": spectral_row["derived_cut_edge_count"],
        "spectral_positive_state_count": spectral_row["positive_state_count"],
        "spectral_negative_state_count": spectral_row["negative_state_count"],
        "merged_lambda_2": spectral_row["lambda_2_x1e12"] / SCALE,
        "merged_lambda_3": spectral_row["lambda_3_x1e12"] / SCALE,
        "merged_spectral_gap": spectral_row["spectral_gap_x1e12"] / SCALE,
        "merged_cut_conductance": spectral_row["cut_conductance_x1e12"] / SCALE,
        "poincare_point_count": len(spectral["poincare_rows"]),
        "poincare_radius_max": poincare_summary["poincare_radius_max_x1e12"] / SCALE,
        "poincare_diameter": poincare_summary["poincare_diameter_x1e12"] / SCALE,
        "left_gate_poincare_distance": poincare_summary[
            "left_gate_poincare_distance_x1e12"
        ]
        / SCALE,
        "gate_right_poincare_distance": poincare_summary[
            "gate_right_poincare_distance_x1e12"
        ]
        / SCALE,
        "left_right_poincare_distance": poincare_summary[
            "left_right_poincare_distance_x1e12"
        ]
        / SCALE,
    }
    observable_rows = []
    for observable_id, (key, code) in enumerate(AUTOMATON_OBSERVABLE_CODES.items()):
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
        "state_rows": state_rows,
        "transition_rows": sorted(transition_rows, key=lambda row: row["transition_id"]),
        "repaired_class_rows": repaired_class_rows,
        "native_class_rows": native_class_rows,
        "spectral_rows": [spectral_row],
        "poincare_rows": spectral["poincare_rows"],
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "repaired_class_sizes": [row["state_count"] for row in repaired_class_rows],
        "native_class_sizes": [row["state_count"] for row in native_class_rows],
        "poincare_summary": poincare_summary,
        "left_id": left_id,
        "gate_id": gate_id,
        "right_id": right_id,
        "merged_class_id": merged_class_id,
    }


def build_payloads() -> dict[str, Any]:
    skip_report = load_json(SKIP_WINDOW_REPORT)
    skip_certificate = load_json(SKIP_WINDOW_CERTIFICATE)
    rows = build_payload_rows()

    state_table = table_from_rows(STATE_COLUMNS, rows["state_rows"])
    transition_table = table_from_rows(TRANSITION_COLUMNS, rows["transition_rows"])
    recurrent_class_table = table_from_rows(
        RECURRENT_CLASS_COLUMNS,
        rows["repaired_class_rows"],
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
    poincare_summary = rows["poincare_summary"]
    checks = {
        "skip_window_report_certified": skip_report.get("status")
        == SKIP_WINDOW_STATUS,
        "skip_window_certificate_certified": skip_certificate.get("status")
        == SKIP_WINDOW_STATUS,
        "state_and_transition_counts_are_expected": (
            observable_values["state_count"],
            observable_values["undirected_edge_count"],
            observable_values["directed_transition_count"],
        )
        == (846, 2_549, 5_098),
        "native_and_derived_state_counts_are_expected": (
            observable_values["native_state_count"],
            observable_values["derived_only_state_count"],
            observable_values["merged_native_state_count"],
            observable_values["merged_derived_only_state_count"],
        )
        == (562, 284, 532, 255),
        "derived_transition_counts_are_expected": (
            observable_values["native_transition_edge_count"],
            observable_values["derived_transition_edge_count"],
            observable_values["derived_only_transition_edge_count"],
        )
        == (1_694, 855, 766),
        "recurrent_class_counts_are_expected": (
            observable_values["native_recurrent_class_count"],
            observable_values["repaired_recurrent_class_count"],
            rows["repaired_class_sizes"],
            rows["native_class_sizes"],
        )
        == (
            13,
            22,
            [787, 15, 11, 6, 4, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [347, 185, 15, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1],
        ),
        "derived_automaton_merges_native_boundary_classes": (
            observable_values["left_right_same_native_recurrent_class"],
            observable_values["left_right_same_repaired_recurrent_class"],
            observable_values["gate_in_merged_recurrent_class"],
            observable_values["boundary_path_edge_count"],
        )
        == (0, 1, 1, 2),
        "spectral_cut_is_derived_bottleneck": (
            spectral_row["cut_edge_count"],
            spectral_row["derived_cut_edge_count"],
            spectral_row["positive_state_count"],
            spectral_row["negative_state_count"],
        )
        == (6, 6, 593, 194),
        "spectral_values_are_positive": (
            spectral_row["lambda_2_x1e12"] > 0
            and spectral_row["lambda_3_x1e12"] > spectral_row["lambda_2_x1e12"]
            and spectral_row["cut_conductance_x1e12"] > 0
        ),
        "boundary_path_is_on_one_spectral_side": (
            spectral_row["left_side_code"],
            spectral_row["gate_side_code"],
            spectral_row["right_side_code"],
        )
        == (1, 1, 1),
        "poincare_embedding_is_inside_disk": (
            observable_values["poincare_point_count"] == 787
            and poincare_summary["poincare_radius_max_x1e12"]
            == scaled_float(EMBEDDING_RADIUS)
            and poincare_summary["poincare_diameter_x1e12"] > 0
        ),
        "state_table_shape_matches_codebook": tuple(state_table.shape)
        == (846, len(STATE_COLUMNS)),
        "transition_table_shape_matches_codebook": tuple(transition_table.shape)
        == (5_098, len(TRANSITION_COLUMNS)),
        "recurrent_class_table_shape_matches_codebook": tuple(
            recurrent_class_table.shape
        )
        == (22, len(RECURRENT_CLASS_COLUMNS)),
        "native_recurrent_class_table_shape_matches_codebook": tuple(
            native_recurrent_class_table.shape
        )
        == (13, len(NATIVE_CLASS_COLUMNS)),
        "spectral_cut_table_shape_matches_codebook": tuple(spectral_cut_table.shape)
        == (1, len(SPECTRAL_CUT_COLUMNS)),
        "poincare_table_shape_matches_codebook": tuple(poincare_table.shape)
        == (787, len(POINCARE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(AUTOMATON_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "state_count": observable_values["state_count"],
        "undirected_edge_count": observable_values["undirected_edge_count"],
        "directed_transition_count": observable_values["directed_transition_count"],
        "native_state_count": observable_values["native_state_count"],
        "derived_only_state_count": observable_values["derived_only_state_count"],
        "native_recurrent_class_sizes": rows["native_class_sizes"],
        "repaired_recurrent_class_sizes": rows["repaired_class_sizes"],
        "merged_recurrent_class_id": rows["merged_class_id"],
        "merged_recurrent_class_size": observable_values[
            "merged_recurrent_class_size"
        ],
        "merged_native_state_count": observable_values["merged_native_state_count"],
        "merged_derived_only_state_count": observable_values[
            "merged_derived_only_state_count"
        ],
        "transition_edge_profile": {
            "native": observable_values["native_transition_edge_count"],
            "derived_involving": observable_values["derived_transition_edge_count"],
            "derived_only": observable_values["derived_only_transition_edge_count"],
            "boundary_path": observable_values["boundary_path_edge_count"],
        },
        "boundary_class_profile": {
            "left_state_id": rows["left_id"],
            "gate_state_id": rows["gate_id"],
            "right_state_id": rows["right_id"],
            "left_right_same_native_recurrent_class": observable_values[
                "left_right_same_native_recurrent_class"
            ],
            "left_right_same_repaired_recurrent_class": observable_values[
                "left_right_same_repaired_recurrent_class"
            ],
            "gate_in_merged_recurrent_class": observable_values[
                "gate_in_merged_recurrent_class"
            ],
        },
        "spectral_cut": {
            "lambda_2_x1e12": spectral_row["lambda_2_x1e12"],
            "lambda_3_x1e12": spectral_row["lambda_3_x1e12"],
            "cut_edge_count": spectral_row["cut_edge_count"],
            "derived_cut_edge_count": spectral_row["derived_cut_edge_count"],
            "positive_state_count": spectral_row["positive_state_count"],
            "negative_state_count": spectral_row["negative_state_count"],
            "positive_volume": spectral_row["positive_volume"],
            "negative_volume": spectral_row["negative_volume"],
            "cut_conductance_x1e12": spectral_row["cut_conductance_x1e12"],
        },
        "poincare_geometry": {
            **poincare_summary,
            "point_count": len(rows["poincare_rows"]),
        },
        "state_table_sha256": sha_array(state_table),
        "transition_table_sha256": sha_array(transition_table),
        "recurrent_class_table_sha256": sha_array(recurrent_class_table),
        "native_recurrent_class_table_sha256": sha_array(
            native_recurrent_class_table
        ),
        "spectral_cut_table_sha256": sha_array(spectral_cut_table),
        "poincare_table_sha256": sha_array(poincare_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    automaton = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton@1",
        "object": "d20",
        "parent": SKIP_WINDOW_REPORT.relative_to(ROOT).as_posix(),
        "construction": [
            "states are the 846 grammar-good closed-positive boundary words",
            "directed transitions are the two orientations of each certified one-edit grammar-good edge",
            "native and derived-only repair labels are inherited from the skip-window grammar layer",
            "recurrent classes are strongly connected components of the symmetric transition relation",
            "the merged boundary class receives a normalized-Laplacian spectral cut and two-mode Poincare disk embedding",
        ],
        "edit_kind_codes": {
            "0": "substitution",
            "1": "insertion",
            "2": "deletion",
        },
        "spectral_side_codes": {
            "-1": "negative Fiedler side",
            "0": "outside the merged spectral class",
            "1": "positive Fiedler side",
        },
        "summary": {
            "state_count": observable_values["state_count"],
            "directed_transition_count": observable_values[
                "directed_transition_count"
            ],
            "native_recurrent_class_count": observable_values[
                "native_recurrent_class_count"
            ],
            "repaired_recurrent_class_count": observable_values[
                "repaired_recurrent_class_count"
            ],
            "spectral_cut_edge_count": spectral_row["cut_edge_count"],
            "derived_cut_edge_count": spectral_row["derived_cut_edge_count"],
            "poincare_diameter_x1e12": poincare_summary[
                "poincare_diameter_x1e12"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_REPAIRED_AUTOMATON_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the skip-window grammar compiles to a 846-state repaired boundary automaton",
            "the repaired automaton has 5,098 directed transitions from 2,549 one-edit edges",
            "native repair support splits the left and right boundary cells into different recurrent classes",
            "derived repair support merges them through the gate into a 787-state recurrent class",
            "the dominant spectral cut has six edges and every cut edge touches derived-only support",
            "the dominant recurrent class admits a bounded two-mode Poincare disk readout",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The skip-window grammar compiles into an explicit repaired boundary "
            "automaton with 846 states and 5,098 directed transitions. Native "
            "repair support alone has 13 recurrent classes and keeps the left "
            "and right boundary cells separated; adding derived repair support "
            "produces 22 repaired classes and merges the boundary cells with the "
            "derived gate inside a 787-state dominant class. The dominant class "
            "has normalized-Laplacian lambda_2 "
            f"{spectral_row['lambda_2_x1e12']}/1e12 and a six-edge spectral "
            "cut, all six edges touching derived-only support. The two-mode "
            "Poincare readout stays inside radius 0.85 and gives a finite "
            "hyperbolic diameter witness for the repaired boundary language."
        ),
        "stage_protocol": {
            "draft": "compile grammar-good words into an explicit transition automaton",
            "witness": "emit state, transition, recurrent-class, spectral, and Poincare tables",
            "coherence": "compare native-only recurrence with derived-repaired recurrence",
            "closure": "certify the boundary merge, derived spectral bottleneck, and bounded disk readout",
            "emit": "emit automaton artifacts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "skip_window_report": input_entry(
                SKIP_WINDOW_REPORT,
                {
                    "status": skip_report.get("status"),
                    "certificate_sha256": skip_report.get("certificate_sha256"),
                },
            ),
            "skip_window_certificate": input_entry(SKIP_WINDOW_CERTIFICATE),
            "skip_window_cells": input_entry(SKIP_WINDOW_CELLS),
            "skip_window_components": input_entry(SKIP_WINDOW_COMPONENTS),
            "skip_window_tables": input_entry(SKIP_WINDOW_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_repaired_automaton": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_repaired_automaton.json"
            ),
            "repaired_automaton_states_csv": relpath(
                OUT_DIR / "aperture_closure_tail_repaired_automaton_states.csv"
            ),
            "repaired_automaton_transitions_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_repaired_automaton_transitions.csv"
            ),
            "repaired_automaton_recurrent_classes_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_repaired_automaton_recurrent_classes.csv"
            ),
            "repaired_automaton_native_recurrent_classes_csv": relpath(
                OUT_DIR
                / "aperture_closure_tail_repaired_automaton_native_recurrent_classes.csv"
            ),
            "repaired_automaton_spectral_cut_csv": relpath(
                OUT_DIR / "aperture_closure_tail_repaired_automaton_spectral_cut.csv"
            ),
            "repaired_automaton_poincare_csv": relpath(
                OUT_DIR / "aperture_closure_tail_repaired_automaton_poincare.csv"
            ),
            "repaired_automaton_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_repaired_automaton_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_repaired_automaton_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the explicit 846-state repaired boundary automaton for the certified grammar-good language",
                "native-only and repaired recurrent class decompositions",
                "the dominant repaired recurrent class spectral cut",
                "the two-mode Poincare disk readout of the dominant repaired recurrent class",
            ],
            "does_not_certify_because_not_required": [
                "boundary words outside the certified radius-three side union",
                "multi-window repair closure beyond the skip-window grammar",
                "compiler integration of repaired automaton transitions",
                "optimality of the spectral embedding among all hyperbolic embeddings",
            ],
        },
        "next_highest_yield_item": (
            "Use the repaired automaton as a transfer operator: weight native "
            "and derived transitions, compute the stationary flow over the "
            "dominant recurrent class, and compare its mass center against the "
            "Poincare spectral bottleneck."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified skip-window grammar artifacts",
            "compile grammar-good words into directed one-edit automaton transitions",
            "compare native-only and repaired recurrent classes",
            "measure the dominant class spectral cut and Poincare disk geometry",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_repaired_automaton": automaton,
        "repaired_automaton_states_csv": csv_text(STATE_COLUMNS, rows["state_rows"]),
        "repaired_automaton_transitions_csv": csv_text(
            TRANSITION_COLUMNS,
            rows["transition_rows"],
        ),
        "repaired_automaton_recurrent_classes_csv": csv_text(
            RECURRENT_CLASS_COLUMNS,
            rows["repaired_class_rows"],
        ),
        "repaired_automaton_native_recurrent_classes_csv": csv_text(
            NATIVE_CLASS_COLUMNS,
            rows["native_class_rows"],
        ),
        "repaired_automaton_spectral_cut_csv": csv_text(
            SPECTRAL_CUT_COLUMNS,
            rows["spectral_rows"],
        ),
        "repaired_automaton_poincare_csv": csv_text(
            POINCARE_COLUMNS,
            rows["poincare_rows"],
        ),
        "repaired_automaton_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "state_table": state_table,
        "transition_table": transition_table,
        "recurrent_class_table": recurrent_class_table,
        "native_recurrent_class_table": native_recurrent_class_table,
        "spectral_cut_table": spectral_cut_table,
        "poincare_table": poincare_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_repaired_automaton.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_repaired_automaton"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_repaired_automaton_states.csv").write_text(
        payloads["repaired_automaton_states_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_transitions.csv"
    ).write_text(
        payloads["repaired_automaton_transitions_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR
        / "aperture_closure_tail_repaired_automaton_recurrent_classes.csv"
    ).write_text(
        payloads["repaired_automaton_recurrent_classes_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR
        / "aperture_closure_tail_repaired_automaton_native_recurrent_classes.csv"
    ).write_text(
        payloads["repaired_automaton_native_recurrent_classes_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_spectral_cut.csv"
    ).write_text(
        payloads["repaired_automaton_spectral_cut_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_repaired_automaton_poincare.csv").write_text(
        payloads["repaired_automaton_poincare_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_observables.csv"
    ).write_text(
        payloads["repaired_automaton_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_tables.npz",
        state_table=payloads["state_table"],
        transition_table=payloads["transition_table"],
        recurrent_class_table=payloads["recurrent_class_table"],
        native_recurrent_class_table=payloads["native_recurrent_class_table"],
        spectral_cut_table=payloads["spectral_cut_table"],
        poincare_table=payloads["poincare_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate"
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
