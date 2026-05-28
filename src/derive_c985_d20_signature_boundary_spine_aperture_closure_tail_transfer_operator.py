from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        OUT_DIR as REPAIRED_AUTOMATON_DIR,
        OBSERVABLE_COLUMNS,
        POINCARE_COLUMNS,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS as REPAIRED_AUTOMATON_STATUS,
        TRANSITION_COLUMNS,
        csv_text,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        OUT_DIR as REPAIRED_AUTOMATON_DIR,
        OBSERVABLE_COLUMNS,
        POINCARE_COLUMNS,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS as REPAIRED_AUTOMATON_STATUS,
        TRANSITION_COLUMNS,
        csv_text,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_TRANSFER_OPERATOR_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REPAIRED_AUTOMATON_REPORT = REPAIRED_AUTOMATON_DIR / "report.json"
REPAIRED_AUTOMATON_CERTIFICATE = (
    REPAIRED_AUTOMATON_DIR
    / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate.json"
)
REPAIRED_AUTOMATON_TABLES = (
    REPAIRED_AUTOMATON_DIR
    / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_tables.npz"
)
REPAIRED_AUTOMATON_STATES = (
    REPAIRED_AUTOMATON_DIR / "aperture_closure_tail_repaired_automaton_states.csv"
)
REPAIRED_AUTOMATON_TRANSITIONS = (
    REPAIRED_AUTOMATON_DIR
    / "aperture_closure_tail_repaired_automaton_transitions.csv"
)
REPAIRED_AUTOMATON_POINCARE = (
    REPAIRED_AUTOMATON_DIR / "aperture_closure_tail_repaired_automaton_poincare.csv"
)
REPAIRED_AUTOMATON_SPECTRAL_CUT = (
    REPAIRED_AUTOMATON_DIR
    / "aperture_closure_tail_repaired_automaton_spectral_cut.csv"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator.py"
)

SCALE = 10**12
NATIVE_EDGE_WEIGHT = 3
DERIVED_EDGE_WEIGHT = 1

TRANSFER_STATE_COLUMNS = [
    "transfer_state_id",
    "automaton_state_id",
    "spectral_side_code",
    "stationary_mass_x1e12",
    "weighted_degree",
    "native_weighted_degree",
    "derived_weighted_degree",
    "cut_weighted_degree",
    "boundary_path_weighted_degree",
    "stationary_rank",
    "poincare_x_x1e12",
    "poincare_y_x1e12",
    "poincare_radius_x1e12",
    "distance_to_flow_center_x1e12",
    "native_repair_flag",
    "derived_only_flag",
    "left_boundary_flag",
    "gate_word_flag",
    "right_boundary_flag",
]

TRANSFER_EDGE_COLUMNS = [
    "transfer_edge_id",
    "source_state_id",
    "target_state_id",
    "edge_weight",
    "native_transition_flag",
    "derived_transition_flag",
    "derived_only_transition_flag",
    "spectral_cut_edge_flag",
    "boundary_path_edge_flag",
    "undirected_stationary_flux_x1e12",
    "source_to_target_probability_x1e12",
    "target_to_source_probability_x1e12",
    "source_stationary_mass_x1e12",
    "target_stationary_mass_x1e12",
]

SIDE_FLOW_COLUMNS = [
    "side_flow_id",
    "spectral_side_code",
    "state_count",
    "weighted_volume",
    "stationary_mass_x1e12",
    "cut_edge_count",
    "cut_weight",
    "cut_flux_x1e12",
    "center_x_x1e12",
    "center_y_x1e12",
    "center_radius_x1e12",
    "distance_to_flow_center_x1e12",
]

CENTER_COLUMNS = [
    "center_id",
    "center_code",
    "support_state_count",
    "support_mass_x1e12",
    "center_x_x1e12",
    "center_y_x1e12",
    "center_radius_x1e12",
    "distance_to_flow_center_x1e12",
    "distance_to_cut_center_x1e12",
    "distance_to_left_boundary_x1e12",
    "distance_to_gate_x1e12",
    "distance_to_right_boundary_x1e12",
]

TRANSFER_OBSERVABLE_CODES = {
    "transfer_state_count": 0,
    "transfer_edge_count": 1,
    "total_edge_weight": 2,
    "total_weighted_degree": 3,
    "native_edge_count": 4,
    "derived_edge_count": 5,
    "derived_only_edge_count": 6,
    "native_edge_weight": 7,
    "derived_edge_weight": 8,
    "spectral_cut_edge_count": 9,
    "spectral_cut_weight": 10,
    "spectral_cut_flux": 11,
    "weighted_cut_conductance": 12,
    "positive_side_mass": 13,
    "negative_side_mass": 14,
    "flow_center_radius": 15,
    "flow_to_cut_center_distance": 16,
    "flow_to_left_boundary_distance": 17,
    "flow_to_gate_distance": 18,
    "flow_to_right_boundary_distance": 19,
    "left_boundary_stationary_mass": 20,
    "gate_stationary_mass": 21,
    "right_boundary_stationary_mass": 22,
    "top_stationary_mass": 23,
    "top_stationary_state_id": 24,
}

FLOAT_OBSERVABLES = {
    "spectral_cut_flux",
    "weighted_cut_conductance",
    "positive_side_mass",
    "negative_side_mass",
    "flow_center_radius",
    "flow_to_cut_center_distance",
    "flow_to_left_boundary_distance",
    "flow_to_gate_distance",
    "flow_to_right_boundary_distance",
    "left_boundary_stationary_mass",
    "gate_stationary_mass",
    "right_boundary_stationary_mass",
    "top_stationary_mass",
}


def round_div(numerator: int, denominator: int) -> int:
    if numerator >= 0:
        return int((2 * numerator + denominator) // (2 * denominator))
    return -int((2 * (-numerator) + denominator) // (2 * denominator))


def scaled_float(value: float) -> int:
    canonical = float(f"{float(value):.9f}")
    return int(round(canonical * SCALE))


def scale_rational_vector(numerators: list[int], denominator: int) -> list[int]:
    floors = [(int(value) * SCALE) // int(denominator) for value in numerators]
    remainder = SCALE - sum(floors)
    residues = [
        (int(value) * SCALE) % int(denominator)
        for value in numerators
    ]
    order = sorted(range(len(numerators)), key=lambda index: (-residues[index], index))
    scaled = floors[:]
    for index in order[:remainder]:
        scaled[index] += 1
    return [int(value) for value in scaled]


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def poincare_distance_scaled(
    left_x: int,
    left_y: int,
    right_x: int,
    right_y: int,
) -> int:
    left = np.asarray([left_x / SCALE, left_y / SCALE], dtype=np.float64)
    right = np.asarray([right_x / SCALE, right_y / SCALE], dtype=np.float64)
    distance_squared = float(np.sum((left - right) ** 2))
    radius_left = float(np.sum(left**2))
    radius_right = float(np.sum(right**2))
    denominator = (1.0 - radius_left) * (1.0 - radius_right)
    argument = 1.0 + (2.0 * distance_squared / denominator)
    return scaled_float(math.acosh(max(1.0, argument)))


def center_from_states(
    state_ids: list[int],
    masses: dict[int, int],
    point_by_state: dict[int, dict[str, int]],
) -> tuple[int, int, int]:
    mass_total = sum(masses[state_id] for state_id in state_ids)
    if mass_total <= 0:
        raise AssertionError("center support must have positive mass")
    x = round_div(
        sum(
            masses[state_id] * point_by_state[state_id]["poincare_x_x1e12"]
            for state_id in state_ids
        ),
        mass_total,
    )
    y = round_div(
        sum(
            masses[state_id] * point_by_state[state_id]["poincare_y_x1e12"]
            for state_id in state_ids
        ),
        mass_total,
    )
    radius = scaled_float(math.hypot(x / SCALE, y / SCALE))
    return x, y, radius


def center_from_cut_edges(
    edges: list[dict[str, int]],
    point_by_state: dict[int, dict[str, int]],
) -> tuple[int, int, int]:
    cut_edges = [edge for edge in edges if edge["spectral_cut_edge_flag"] == 1]
    weight_total = sum(edge["edge_weight"] for edge in cut_edges)
    if weight_total <= 0:
        raise AssertionError("cut center needs positive cut weight")
    x = round_div(
        sum(
            edge["edge_weight"]
            * (
                point_by_state[edge["source_state_id"]]["poincare_x_x1e12"]
                + point_by_state[edge["target_state_id"]]["poincare_x_x1e12"]
            )
            for edge in cut_edges
        ),
        2 * weight_total,
    )
    y = round_div(
        sum(
            edge["edge_weight"]
            * (
                point_by_state[edge["source_state_id"]]["poincare_y_x1e12"]
                + point_by_state[edge["target_state_id"]]["poincare_y_x1e12"]
            )
            for edge in cut_edges
        ),
        2 * weight_total,
    )
    radius = scaled_float(math.hypot(x / SCALE, y / SCALE))
    return x, y, radius


def load_repaired_rows() -> dict[str, Any]:
    tables = np.load(REPAIRED_AUTOMATON_TABLES, allow_pickle=False)
    state_rows = table_rows(np.asarray(tables["state_table"]), STATE_COLUMNS)
    transition_rows = table_rows(
        np.asarray(tables["transition_table"]),
        TRANSITION_COLUMNS,
    )
    poincare_rows = table_rows(np.asarray(tables["poincare_table"]), POINCARE_COLUMNS)
    spectral_cut_rows = table_rows(
        np.asarray(tables["spectral_cut_table"]),
        SPECTRAL_CUT_COLUMNS,
    )
    return {
        "state_rows": state_rows,
        "transition_rows": transition_rows,
        "poincare_rows": poincare_rows,
        "spectral_cut_rows": spectral_cut_rows,
    }


def build_payload_rows() -> dict[str, Any]:
    repaired = load_repaired_rows()
    state_by_id = {
        row["automaton_state_id"]: row
        for row in repaired["state_rows"]
        if row["merged_recurrent_class_flag"] == 1
    }
    point_by_state = {
        row["automaton_state_id"]: row
        for row in repaired["poincare_rows"]
    }
    state_ids = sorted(state_by_id)
    edge_rows: list[dict[str, int]] = []
    native_edge_count = 0
    derived_edge_count = 0
    derived_only_edge_count = 0
    for row in repaired["transition_rows"]:
        source = row["source_state_id"]
        target = row["target_state_id"]
        if source >= target or source not in state_by_id or target not in state_by_id:
            continue
        edge_weight = (
            NATIVE_EDGE_WEIGHT
            if row["native_transition_flag"] == 1
            else DERIVED_EDGE_WEIGHT
        )
        native_edge_count += row["native_transition_flag"]
        derived_edge_count += row["derived_transition_flag"]
        derived_only_edge_count += row["derived_only_transition_flag"]
        edge_rows.append(
            {
                "transfer_edge_id": len(edge_rows),
                "source_state_id": source,
                "target_state_id": target,
                "edge_weight": edge_weight,
                "native_transition_flag": row["native_transition_flag"],
                "derived_transition_flag": row["derived_transition_flag"],
                "derived_only_transition_flag": row["derived_only_transition_flag"],
                "spectral_cut_edge_flag": row["spectral_cut_edge_flag"],
                "boundary_path_edge_flag": row["boundary_path_edge_flag"],
            }
        )

    weighted_degree: Counter[int] = Counter()
    native_weighted_degree: Counter[int] = Counter()
    derived_weighted_degree: Counter[int] = Counter()
    cut_weighted_degree: Counter[int] = Counter()
    boundary_weighted_degree: Counter[int] = Counter()
    outgoing: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for edge in edge_rows:
        source = edge["source_state_id"]
        target = edge["target_state_id"]
        weight = edge["edge_weight"]
        for state_id in (source, target):
            weighted_degree[state_id] += weight
            if edge["native_transition_flag"]:
                native_weighted_degree[state_id] += weight
            if edge["derived_transition_flag"]:
                derived_weighted_degree[state_id] += weight
            if edge["spectral_cut_edge_flag"]:
                cut_weighted_degree[state_id] += weight
            if edge["boundary_path_edge_flag"]:
                boundary_weighted_degree[state_id] += weight
        outgoing[source].append((edge["transfer_edge_id"], target, weight))
        outgoing[target].append((edge["transfer_edge_id"], source, weight))

    total_edge_weight = sum(edge["edge_weight"] for edge in edge_rows)
    total_weighted_degree = sum(weighted_degree.values())
    stationary_scaled = dict(
        zip(
            state_ids,
            scale_rational_vector(
                [weighted_degree[state_id] for state_id in state_ids],
                total_weighted_degree,
            ),
        )
    )
    edge_flux_scaled = dict(
        zip(
            [edge["transfer_edge_id"] for edge in edge_rows],
            scale_rational_vector(
                [edge["edge_weight"] for edge in edge_rows],
                total_edge_weight,
            ),
        )
    )
    transition_probability: dict[tuple[int, int], int] = {}
    for source, entries in outgoing.items():
        entries = sorted(entries, key=lambda item: (item[1], item[0]))
        scaled = scale_rational_vector(
            [weight for _edge_id, _target, weight in entries],
            weighted_degree[source],
        )
        for (_edge_id, target, _weight), probability in zip(entries, scaled):
            transition_probability[(source, target)] = probability

    ranks = {
        state_id: rank
        for rank, state_id in enumerate(
            sorted(
                state_ids,
                key=lambda value: (-stationary_scaled[value], value),
            ),
            start=1,
        )
    }

    flow_center = center_from_states(state_ids, stationary_scaled, point_by_state)
    cut_center = center_from_cut_edges(edge_rows, point_by_state)
    left_id = next(
        state_id
        for state_id, row in state_by_id.items()
        if row["left_boundary_flag"] == 1
    )
    gate_id = next(
        state_id
        for state_id, row in state_by_id.items()
        if row["gate_word_flag"] == 1
    )
    right_id = next(
        state_id
        for state_id, row in state_by_id.items()
        if row["right_boundary_flag"] == 1
    )
    landmark_points = {
        "flow": flow_center,
        "cut": cut_center,
        "left": (
            point_by_state[left_id]["poincare_x_x1e12"],
            point_by_state[left_id]["poincare_y_x1e12"],
            point_by_state[left_id]["poincare_radius_x1e12"],
        ),
        "gate": (
            point_by_state[gate_id]["poincare_x_x1e12"],
            point_by_state[gate_id]["poincare_y_x1e12"],
            point_by_state[gate_id]["poincare_radius_x1e12"],
        ),
        "right": (
            point_by_state[right_id]["poincare_x_x1e12"],
            point_by_state[right_id]["poincare_y_x1e12"],
            point_by_state[right_id]["poincare_radius_x1e12"],
        ),
    }

    transfer_state_rows = []
    for state_id in state_ids:
        state = state_by_id[state_id]
        point = point_by_state[state_id]
        transfer_state_rows.append(
            {
                "transfer_state_id": len(transfer_state_rows),
                "automaton_state_id": state_id,
                "spectral_side_code": state["spectral_side_code"],
                "stationary_mass_x1e12": stationary_scaled[state_id],
                "weighted_degree": weighted_degree[state_id],
                "native_weighted_degree": native_weighted_degree[state_id],
                "derived_weighted_degree": derived_weighted_degree[state_id],
                "cut_weighted_degree": cut_weighted_degree[state_id],
                "boundary_path_weighted_degree": boundary_weighted_degree[state_id],
                "stationary_rank": ranks[state_id],
                "poincare_x_x1e12": point["poincare_x_x1e12"],
                "poincare_y_x1e12": point["poincare_y_x1e12"],
                "poincare_radius_x1e12": point["poincare_radius_x1e12"],
                "distance_to_flow_center_x1e12": poincare_distance_scaled(
                    point["poincare_x_x1e12"],
                    point["poincare_y_x1e12"],
                    flow_center[0],
                    flow_center[1],
                ),
                "native_repair_flag": state["native_repair_flag"],
                "derived_only_flag": state["derived_only_flag"],
                "left_boundary_flag": state["left_boundary_flag"],
                "gate_word_flag": state["gate_word_flag"],
                "right_boundary_flag": state["right_boundary_flag"],
            }
        )

    enriched_edge_rows = []
    for edge in edge_rows:
        source = edge["source_state_id"]
        target = edge["target_state_id"]
        enriched_edge_rows.append(
            {
                **edge,
                "undirected_stationary_flux_x1e12": edge_flux_scaled[
                    edge["transfer_edge_id"]
                ],
                "source_to_target_probability_x1e12": transition_probability[
                    (source, target)
                ],
                "target_to_source_probability_x1e12": transition_probability[
                    (target, source)
                ],
                "source_stationary_mass_x1e12": stationary_scaled[source],
                "target_stationary_mass_x1e12": stationary_scaled[target],
            }
        )

    side_rows = []
    for side_id, side_code in enumerate([-1, 1]):
        side_states = [
            state_id
            for state_id in state_ids
            if state_by_id[state_id]["spectral_side_code"] == side_code
        ]
        side_center = center_from_states(side_states, stationary_scaled, point_by_state)
        cut_edges = [
            edge
            for edge in enriched_edge_rows
            if edge["spectral_cut_edge_flag"] == 1
            and (
                state_by_id[edge["source_state_id"]]["spectral_side_code"] == side_code
                or state_by_id[edge["target_state_id"]]["spectral_side_code"]
                == side_code
            )
        ]
        side_rows.append(
            {
                "side_flow_id": side_id,
                "spectral_side_code": side_code,
                "state_count": len(side_states),
                "weighted_volume": sum(weighted_degree[state_id] for state_id in side_states),
                "stationary_mass_x1e12": sum(
                    stationary_scaled[state_id] for state_id in side_states
                ),
                "cut_edge_count": len(cut_edges),
                "cut_weight": sum(edge["edge_weight"] for edge in cut_edges),
                "cut_flux_x1e12": sum(
                    edge["undirected_stationary_flux_x1e12"] for edge in cut_edges
                ),
                "center_x_x1e12": side_center[0],
                "center_y_x1e12": side_center[1],
                "center_radius_x1e12": side_center[2],
                "distance_to_flow_center_x1e12": poincare_distance_scaled(
                    side_center[0],
                    side_center[1],
                    flow_center[0],
                    flow_center[1],
                ),
            }
        )

    center_specs = [
        (0, 0, state_ids, sum(stationary_scaled.values()), flow_center),
        (
            1,
            -1,
            [
                state_id
                for state_id in state_ids
                if state_by_id[state_id]["spectral_side_code"] == -1
            ],
            next(row["stationary_mass_x1e12"] for row in side_rows if row["spectral_side_code"] == -1),
            center_from_states(
                [
                    state_id
                    for state_id in state_ids
                    if state_by_id[state_id]["spectral_side_code"] == -1
                ],
                stationary_scaled,
                point_by_state,
            ),
        ),
        (
            2,
            1,
            [
                state_id
                for state_id in state_ids
                if state_by_id[state_id]["spectral_side_code"] == 1
            ],
            next(row["stationary_mass_x1e12"] for row in side_rows if row["spectral_side_code"] == 1),
            center_from_states(
                [
                    state_id
                    for state_id in state_ids
                    if state_by_id[state_id]["spectral_side_code"] == 1
                ],
                stationary_scaled,
                point_by_state,
            ),
        ),
        (3, 2, [], 0, cut_center),
    ]
    center_rows = []
    for center_id, center_code, support_states, support_mass, center in center_specs:
        center_rows.append(
            {
                "center_id": center_id,
                "center_code": center_code,
                "support_state_count": len(support_states),
                "support_mass_x1e12": support_mass,
                "center_x_x1e12": center[0],
                "center_y_x1e12": center[1],
                "center_radius_x1e12": center[2],
                "distance_to_flow_center_x1e12": poincare_distance_scaled(
                    center[0],
                    center[1],
                    landmark_points["flow"][0],
                    landmark_points["flow"][1],
                ),
                "distance_to_cut_center_x1e12": poincare_distance_scaled(
                    center[0],
                    center[1],
                    landmark_points["cut"][0],
                    landmark_points["cut"][1],
                ),
                "distance_to_left_boundary_x1e12": poincare_distance_scaled(
                    center[0],
                    center[1],
                    landmark_points["left"][0],
                    landmark_points["left"][1],
                ),
                "distance_to_gate_x1e12": poincare_distance_scaled(
                    center[0],
                    center[1],
                    landmark_points["gate"][0],
                    landmark_points["gate"][1],
                ),
                "distance_to_right_boundary_x1e12": poincare_distance_scaled(
                    center[0],
                    center[1],
                    landmark_points["right"][0],
                    landmark_points["right"][1],
                ),
            }
        )

    side_mass_by_code = {
        row["spectral_side_code"]: row["stationary_mass_x1e12"]
        for row in side_rows
    }
    top_state_id = min(
        state_ids,
        key=lambda state_id: (-stationary_scaled[state_id], state_id),
    )
    cut_flux = sum(
        edge["undirected_stationary_flux_x1e12"]
        for edge in enriched_edge_rows
        if edge["spectral_cut_edge_flag"] == 1
    )
    cut_weight = sum(
        edge["edge_weight"]
        for edge in enriched_edge_rows
        if edge["spectral_cut_edge_flag"] == 1
    )
    positive_volume = next(
        row["weighted_volume"] for row in side_rows if row["spectral_side_code"] == 1
    )
    negative_volume = next(
        row["weighted_volume"] for row in side_rows if row["spectral_side_code"] == -1
    )
    observable_values = {
        "transfer_state_count": len(transfer_state_rows),
        "transfer_edge_count": len(enriched_edge_rows),
        "total_edge_weight": total_edge_weight,
        "total_weighted_degree": total_weighted_degree,
        "native_edge_count": native_edge_count,
        "derived_edge_count": derived_edge_count,
        "derived_only_edge_count": derived_only_edge_count,
        "native_edge_weight": sum(
            edge["edge_weight"]
            for edge in enriched_edge_rows
            if edge["native_transition_flag"] == 1
        ),
        "derived_edge_weight": sum(
            edge["edge_weight"]
            for edge in enriched_edge_rows
            if edge["derived_transition_flag"] == 1
        ),
        "spectral_cut_edge_count": sum(
            edge["spectral_cut_edge_flag"] for edge in enriched_edge_rows
        ),
        "spectral_cut_weight": cut_weight,
        "spectral_cut_flux": cut_flux / SCALE,
        "weighted_cut_conductance": cut_weight / min(positive_volume, negative_volume),
        "positive_side_mass": side_mass_by_code[1] / SCALE,
        "negative_side_mass": side_mass_by_code[-1] / SCALE,
        "flow_center_radius": flow_center[2] / SCALE,
        "flow_to_cut_center_distance": next(
            row["distance_to_cut_center_x1e12"]
            for row in center_rows
            if row["center_code"] == 0
        )
        / SCALE,
        "flow_to_left_boundary_distance": next(
            row["distance_to_left_boundary_x1e12"]
            for row in center_rows
            if row["center_code"] == 0
        )
        / SCALE,
        "flow_to_gate_distance": next(
            row["distance_to_gate_x1e12"]
            for row in center_rows
            if row["center_code"] == 0
        )
        / SCALE,
        "flow_to_right_boundary_distance": next(
            row["distance_to_right_boundary_x1e12"]
            for row in center_rows
            if row["center_code"] == 0
        )
        / SCALE,
        "left_boundary_stationary_mass": stationary_scaled[left_id] / SCALE,
        "gate_stationary_mass": stationary_scaled[gate_id] / SCALE,
        "right_boundary_stationary_mass": stationary_scaled[right_id] / SCALE,
        "top_stationary_mass": stationary_scaled[top_state_id] / SCALE,
        "top_stationary_state_id": top_state_id,
    }
    observable_rows = []
    for observable_id, (key, code) in enumerate(TRANSFER_OBSERVABLE_CODES.items()):
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
        "state_rows": transfer_state_rows,
        "edge_rows": enriched_edge_rows,
        "side_rows": side_rows,
        "center_rows": center_rows,
        "observable_rows": observable_rows,
        "observable_values": observable_values,
        "left_id": left_id,
        "gate_id": gate_id,
        "right_id": right_id,
        "top_state_id": top_state_id,
        "total_edge_weight": total_edge_weight,
        "total_weighted_degree": total_weighted_degree,
        "cut_flux_x1e12": cut_flux,
        "cut_weight": cut_weight,
    }


def build_payloads() -> dict[str, Any]:
    repaired_report = load_json(REPAIRED_AUTOMATON_REPORT)
    repaired_certificate = load_json(REPAIRED_AUTOMATON_CERTIFICATE)
    rows = build_payload_rows()

    state_table = table_from_rows(TRANSFER_STATE_COLUMNS, rows["state_rows"])
    edge_table = table_from_rows(TRANSFER_EDGE_COLUMNS, rows["edge_rows"])
    side_table = table_from_rows(SIDE_FLOW_COLUMNS, rows["side_rows"])
    center_table = table_from_rows(CENTER_COLUMNS, rows["center_rows"])
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, rows["observable_rows"])

    observable_values = rows["observable_values"]
    checks = {
        "repaired_automaton_report_certified": repaired_report.get("status")
        == REPAIRED_AUTOMATON_STATUS,
        "repaired_automaton_certificate_certified": repaired_certificate.get("status")
        == REPAIRED_AUTOMATON_STATUS,
        "transfer_counts_are_expected": (
            observable_values["transfer_state_count"],
            observable_values["transfer_edge_count"],
            observable_values["total_edge_weight"],
            observable_values["total_weighted_degree"],
        )
        == (787, 2_501, 5_837, 11_674),
        "transition_weight_profile_is_expected": (
            observable_values["native_edge_count"],
            observable_values["derived_edge_count"],
            observable_values["derived_only_edge_count"],
            observable_values["native_edge_weight"],
            observable_values["derived_edge_weight"],
        )
        == (1_668, 833, 746, 5_004, 833),
        "spectral_cut_flux_is_expected": (
            observable_values["spectral_cut_edge_count"],
            observable_values["spectral_cut_weight"],
            rows["cut_flux_x1e12"],
        )
        == (6, 6, 1_027_925_304),
        "stationary_mass_sums_to_one": int(np.sum(state_table[:, 3])) == SCALE,
        "edge_flux_sums_to_one": int(np.sum(edge_table[:, 9])) == SCALE,
        "side_masses_are_expected": (
            next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == 1
            ),
            next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == -1
            ),
        )
        == (884_872_365_946, 115_127_634_054),
        "boundary_masses_are_expected": (
            int(
                next(
                    row["stationary_mass_x1e12"]
                    for row in rows["state_rows"]
                    if row["left_boundary_flag"] == 1
                )
            ),
            int(
                next(
                    row["stationary_mass_x1e12"]
                    for row in rows["state_rows"]
                    if row["gate_word_flag"] == 1
                )
            ),
            int(
                next(
                    row["stationary_mass_x1e12"]
                    for row in rows["state_rows"]
                    if row["right_boundary_flag"] == 1
                )
            ),
        )
        == (2_141_511_051, 770_943_978, 1_627_548_398),
        "flow_center_is_inside_disk": (
            next(
                row["center_radius_x1e12"]
                for row in rows["center_rows"]
                if row["center_code"] == 0
            )
            < SCALE
        ),
        "flow_center_is_closer_to_right_than_gate": (
            observable_values["flow_to_right_boundary_distance"]
            < observable_values["flow_to_gate_distance"]
        ),
        "flow_center_is_away_from_cut_center": (
            observable_values["flow_to_cut_center_distance"]
            > observable_values["flow_to_left_boundary_distance"]
        ),
        "state_table_shape_matches_codebook": tuple(state_table.shape)
        == (787, len(TRANSFER_STATE_COLUMNS)),
        "edge_table_shape_matches_codebook": tuple(edge_table.shape)
        == (2_501, len(TRANSFER_EDGE_COLUMNS)),
        "side_table_shape_matches_codebook": tuple(side_table.shape)
        == (2, len(SIDE_FLOW_COLUMNS)),
        "center_table_shape_matches_codebook": tuple(center_table.shape)
        == (4, len(CENTER_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(TRANSFER_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "transfer_state_count": observable_values["transfer_state_count"],
        "transfer_edge_count": observable_values["transfer_edge_count"],
        "total_edge_weight": observable_values["total_edge_weight"],
        "total_weighted_degree": observable_values["total_weighted_degree"],
        "weight_rule": {
            "native_edge_weight": NATIVE_EDGE_WEIGHT,
            "derived_edge_weight": DERIVED_EDGE_WEIGHT,
        },
        "edge_profile": {
            "native_edge_count": observable_values["native_edge_count"],
            "derived_edge_count": observable_values["derived_edge_count"],
            "derived_only_edge_count": observable_values["derived_only_edge_count"],
            "native_edge_weight": observable_values["native_edge_weight"],
            "derived_edge_weight": observable_values["derived_edge_weight"],
        },
        "spectral_cut_flow": {
            "cut_edge_count": observable_values["spectral_cut_edge_count"],
            "cut_weight": observable_values["spectral_cut_weight"],
            "cut_flux_x1e12": rows["cut_flux_x1e12"],
            "weighted_cut_conductance_x1e12": scaled_float(
                observable_values["weighted_cut_conductance"]
            ),
        },
        "side_masses": {
            str(row["spectral_side_code"]): row["stationary_mass_x1e12"]
            for row in rows["side_rows"]
        },
        "boundary_masses": {
            "left_state_id": rows["left_id"],
            "left_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["state_rows"]
                if row["left_boundary_flag"] == 1
            ),
            "gate_state_id": rows["gate_id"],
            "gate_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["state_rows"]
                if row["gate_word_flag"] == 1
            ),
            "right_state_id": rows["right_id"],
            "right_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["state_rows"]
                if row["right_boundary_flag"] == 1
            ),
        },
        "mass_center": next(
            row for row in rows["center_rows"] if row["center_code"] == 0
        ),
        "cut_center": next(
            row for row in rows["center_rows"] if row["center_code"] == 2
        ),
        "top_stationary_state_id": rows["top_state_id"],
        "top_stationary_mass_x1e12": next(
            row["stationary_mass_x1e12"]
            for row in rows["state_rows"]
            if row["automaton_state_id"] == rows["top_state_id"]
        ),
        "state_table_sha256": sha_array(state_table),
        "edge_table_sha256": sha_array(edge_table),
        "side_table_sha256": sha_array(side_table),
        "center_table_sha256": sha_array(center_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    transfer_operator = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator@1",
        "object": "d20",
        "parent": REPAIRED_AUTOMATON_REPORT.relative_to(ROOT).as_posix(),
        "weight_rule": {
            "native_transition_edge_weight": NATIVE_EDGE_WEIGHT,
            "derived_involving_transition_edge_weight": DERIVED_EDGE_WEIGHT,
            "rationale": "native support is favored three-to-one, so derived bottleneck flow is measured under a conservative native-biased kernel",
        },
        "stationary_rule": [
            "restrict to the certified 787-state dominant repaired recurrent class",
            "make the one-edit transition graph reversible with the declared edge weights",
            "stationary mass is proportional to weighted degree",
            "undirected edge flux is proportional to edge weight",
            "compare the stationary Poincare mass center with the spectral cut midpoint and the left/gate/right boundary landmarks",
        ],
        "summary": {
            "state_count": observable_values["transfer_state_count"],
            "edge_count": observable_values["transfer_edge_count"],
            "cut_flux_x1e12": rows["cut_flux_x1e12"],
            "positive_side_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == 1
            ),
            "negative_side_mass_x1e12": next(
                row["stationary_mass_x1e12"]
                for row in rows["side_rows"]
                if row["spectral_side_code"] == -1
            ),
        },
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_TRANSFER_OPERATOR_PROVISIONAL",
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The repaired boundary automaton carries a native-biased reversible "
            "transfer operator on its 787-state dominant recurrent class. Native "
            "edges receive weight 3 and derived-involving edges receive weight 1, "
            "giving total edge weight 5,837 and total weighted degree 11,674. "
            "The six-edge spectral bottleneck carries undirected stationary flux "
            "1027925304/1e12. Stationary mass is concentrated on the positive "
            "spectral side at 884872365946/1e12, while the negative side carries "
            "115127634054/1e12. The Poincare mass center remains near the disk "
            "core and is closer to the right boundary than to the derived gate, "
            "while still separated from the cut midpoint."
        ),
        "stage_protocol": {
            "draft": "weight native and derived transitions on the repaired automaton",
            "witness": "emit transfer-state, transfer-edge, side-flow, center, and observable tables",
            "coherence": "check stationary mass, flux, side mass, and boundary landmark consistency",
            "closure": "certify the native-biased stationary flow and its Poincare relation to the spectral bottleneck",
            "emit": "emit transfer operator artifacts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "repaired_automaton_report": input_entry(
                REPAIRED_AUTOMATON_REPORT,
                {
                    "status": repaired_report.get("status"),
                    "certificate_sha256": repaired_report.get("certificate_sha256"),
                },
            ),
            "repaired_automaton_certificate": input_entry(
                REPAIRED_AUTOMATON_CERTIFICATE
            ),
            "repaired_automaton_states": input_entry(REPAIRED_AUTOMATON_STATES),
            "repaired_automaton_transitions": input_entry(
                REPAIRED_AUTOMATON_TRANSITIONS
            ),
            "repaired_automaton_poincare": input_entry(REPAIRED_AUTOMATON_POINCARE),
            "repaired_automaton_spectral_cut": input_entry(
                REPAIRED_AUTOMATON_SPECTRAL_CUT
            ),
            "repaired_automaton_tables": input_entry(REPAIRED_AUTOMATON_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_transfer_operator": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_transfer_operator.json"
            ),
            "transfer_states_csv": relpath(
                OUT_DIR / "aperture_closure_tail_transfer_states.csv"
            ),
            "transfer_edges_csv": relpath(
                OUT_DIR / "aperture_closure_tail_transfer_edges.csv"
            ),
            "transfer_side_flow_csv": relpath(
                OUT_DIR / "aperture_closure_tail_transfer_side_flow.csv"
            ),
            "transfer_centers_csv": relpath(
                OUT_DIR / "aperture_closure_tail_transfer_centers.csv"
            ),
            "transfer_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_transfer_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_transfer_operator_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_transfer_operator_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the native-biased reversible transfer operator on the dominant repaired recurrent class",
                "the exact integer-scaled stationary distribution and undirected edge fluxes",
                "the spectral-side stationary mass split and cut flux",
                "the Poincare mass center comparison against cut, left, gate, and right landmarks",
            ],
            "does_not_certify_because_not_required": [
                "alternative edge-weight schedules",
                "stationary flow on smaller repaired recurrent classes",
                "multi-window repair transitions outside the certified automaton",
                "compiler integration of transfer-operator weights",
            ],
        },
        "next_highest_yield_item": (
            "Lift the transfer flow back to symbolic windows: identify the "
            "highest-mass recurrent windows and cut-edge windows, then search "
            "for the next local grammar move that reduces bottleneck flux "
            "without losing the left/right boundary merge."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the dominant repaired recurrent class supports a reversible native-biased transfer operator",
            "the stationary distribution is exactly reproducible from weighted degrees",
            "the spectral bottleneck carries small but nonzero derived flux",
            "the flow center sits near the disk core and is pulled toward the right boundary side",
        ],
    }

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified repaired-automaton artifacts",
            "build the native-biased reversible transfer operator",
            "check stationary mass, edge flux, side masses, and boundary masses",
            "compare the stationary Poincare center against the spectral cut midpoint and boundary landmarks",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_transfer_operator": transfer_operator,
        "transfer_states_csv": csv_text(TRANSFER_STATE_COLUMNS, rows["state_rows"]),
        "transfer_edges_csv": csv_text(TRANSFER_EDGE_COLUMNS, rows["edge_rows"]),
        "transfer_side_flow_csv": csv_text(SIDE_FLOW_COLUMNS, rows["side_rows"]),
        "transfer_centers_csv": csv_text(CENTER_COLUMNS, rows["center_rows"]),
        "transfer_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            rows["observable_rows"],
        ),
        "state_table": state_table,
        "edge_table": edge_table,
        "side_table": side_table,
        "center_table": center_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_transfer_operator.json",
        payloads["signature_boundary_spine_aperture_closure_tail_transfer_operator"],
    )
    (OUT_DIR / "aperture_closure_tail_transfer_states.csv").write_text(
        payloads["transfer_states_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_transfer_edges.csv").write_text(
        payloads["transfer_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_transfer_side_flow.csv").write_text(
        payloads["transfer_side_flow_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_transfer_centers.csv").write_text(
        payloads["transfer_centers_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_transfer_observables.csv").write_text(
        payloads["transfer_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_transfer_operator_tables.npz",
        state_table=payloads["state_table"],
        edge_table=payloads["edge_table"],
        side_table=payloads["side_table"],
        center_table=payloads["center_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate"
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
