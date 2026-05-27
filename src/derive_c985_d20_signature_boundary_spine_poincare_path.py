from __future__ import annotations

import csv
import json
import math
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_conductance_spine import (
        OUT_DIR as CONDUCTANCE_SPINE_DIR,
    )
    from .derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
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
    from derive_c985_d20_signature_boundary_conductance_spine import (
        OUT_DIR as CONDUCTANCE_SPINE_DIR,
    )
    from derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_poincare_path"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_POINCARE_PATH_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CONDUCTANCE_SPINE_REPORT = CONDUCTANCE_SPINE_DIR / "report.json"
CONDUCTANCE_SPINE_JSON = (
    CONDUCTANCE_SPINE_DIR / "signature_boundary_conductance_spine.json"
)
CONDUCTANCE_SPINE_TABLES = (
    CONDUCTANCE_SPINE_DIR / "signature_boundary_conductance_spine_tables.npz"
)
CONDUCTANCE_SPINE_CERTIFICATE = (
    CONDUCTANCE_SPINE_DIR / "signature_boundary_conductance_spine_certificate.json"
)
CONDUCTANCE_SPINE_EDGES = CONDUCTANCE_SPINE_DIR / "boundary_conductance_spine_edges.csv"

RESIDUAL_CHART_REPORT = RESIDUAL_CHART_DIR / "report.json"
RESIDUAL_CHART_JSON = RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart.json"
RESIDUAL_CHART_TABLES = (
    RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_tables.npz"
)
RESIDUAL_CHART_CERTIFICATE = (
    RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_certificate.json"
)
RESIDUAL_CHART_CARRIER_CSV = RESIDUAL_CHART_DIR / "carrier_residual_chart.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_boundary_spine_poincare_path.py"
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_spine_poincare_path.py"
)

PROBABILITY_SCALE = 1_000_000_000_000

SPINE_POINCARE_EDGE_COLUMNS = [
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "positive_carrier_mask_class_id",
    "negative_carrier_mask_class_id",
    "boundary_partition_code",
    "undirected_stationary_flux_x1e12",
    "total_entropy_contribution_x1e12",
    "positive_center_x_x1e12",
    "positive_center_y_x1e12",
    "negative_center_x_x1e12",
    "negative_center_y_x1e12",
    "positive_axis_coordinate_x1e12",
    "negative_axis_coordinate_x1e12",
    "positive_residual_coordinate_x1e12",
    "negative_residual_coordinate_x1e12",
    "axis_delta_abs_x1e12",
    "residual_delta_abs_x1e12",
    "residual_bend_fraction_x1e12",
    "hyperbolic_edge_length_x1e12",
    "euclidean_edge_length_x1e12",
    "axis_midpoint_x1e12",
    "residual_midpoint_x1e12",
    "residual_excursion_x1e12",
    "axis_dominant_flag",
    "residual_dominant_flag",
]

SPINE_POLYLINE_VERTEX_COLUMNS = [
    "polyline_vertex_rank",
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "midpoint_x_x1e12",
    "midpoint_y_x1e12",
    "axis_midpoint_x1e12",
    "residual_midpoint_x1e12",
    "edge_entropy_contribution_x1e12",
    "cumulative_entropy_contribution_x1e12",
]

SPINE_POLYLINE_TRANSITION_COLUMNS = [
    "polyline_transition_id",
    "from_boundary_spine_rank",
    "to_boundary_spine_rank",
    "from_boundary_mask_edge_id",
    "to_boundary_mask_edge_id",
    "from_midpoint_x_x1e12",
    "from_midpoint_y_x1e12",
    "to_midpoint_x_x1e12",
    "to_midpoint_y_x1e12",
    "axis_transition_abs_x1e12",
    "residual_transition_abs_x1e12",
    "residual_bend_fraction_x1e12",
    "hyperbolic_transition_length_x1e12",
]

SPINE_POINCARE_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "boundary_edge_count": 0,
    "polyline_vertex_count": 1,
    "polyline_transition_count": 2,
    "top_spine_edge_id": 3,
    "top_spine_edge_axis_delta": 4,
    "top_spine_edge_residual_delta": 5,
    "top_spine_edge_bend_fraction": 6,
    "top_spine_edge_hyperbolic_length": 7,
    "top_five_entropy_weighted_axis_delta": 8,
    "top_five_entropy_weighted_residual_delta": 9,
    "top_five_entropy_weighted_bend_fraction": 10,
    "top_five_entropy_weighted_hyperbolic_length": 11,
    "full_entropy_weighted_axis_delta": 12,
    "full_entropy_weighted_residual_delta": 13,
    "full_entropy_weighted_bend_fraction": 14,
    "full_entropy_weighted_hyperbolic_length": 15,
    "residual_dominant_edge_count": 16,
    "residual_dominant_edge_entropy_fraction": 17,
    "polyline_total_axis_travel": 18,
    "polyline_total_residual_travel": 19,
    "polyline_total_bend_fraction": 20,
    "polyline_total_hyperbolic_length": 21,
    "top_five_polyline_axis_travel": 22,
    "top_five_polyline_residual_travel": 23,
    "top_five_polyline_bend_fraction": 24,
    "top_five_polyline_hyperbolic_length": 25,
    "polyline_axis_span": 26,
    "polyline_residual_span": 27,
    "top_five_polyline_axis_span": 28,
    "top_five_polyline_residual_span": 29,
}


def scaled_float(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


def rounded_div(numerator: int, denominator: int) -> int:
    quotient, remainder = divmod(int(numerator), int(denominator))
    if 2 * remainder >= int(denominator):
        quotient += 1
    return int(quotient)


def scaled_ratio(numerator: int, denominator: int) -> int:
    return rounded_div(int(numerator) * PROBABILITY_SCALE, int(denominator))


def weighted_average(rows: list[dict[str, int]], metric: str, weight: str) -> int:
    numerator = sum(int(row[metric]) * int(row[weight]) for row in rows)
    denominator = sum(int(row[weight]) for row in rows)
    return rounded_div(numerator, denominator)


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def read_int_csv(path: Any) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def poincare_distance(left: tuple[float, float], right: tuple[float, float]) -> float:
    x1, y1 = left
    x2, y2 = right
    numerator = 2.0 * ((x1 - x2) ** 2 + (y1 - y2) ** 2)
    left_norm = x1 * x1 + y1 * y1
    right_norm = x2 * x2 + y2 * y2
    denominator = (1.0 - left_norm) * (1.0 - right_norm)
    return math.acosh(max(1.0, 1.0 + numerator / denominator))


def euclidean_distance(left: tuple[float, float], right: tuple[float, float]) -> float:
    return math.dist(left, right)


def carrier_point(row: dict[str, int]) -> tuple[float, float]:
    return (
        int(row["carrier_center_x_x1e12"]) / PROBABILITY_SCALE,
        int(row["carrier_center_y_x1e12"]) / PROBABILITY_SCALE,
    )


def build_payloads() -> dict[str, Any]:
    spine_report = load_json(CONDUCTANCE_SPINE_REPORT)
    spine = load_json(CONDUCTANCE_SPINE_JSON)
    spine_certificate = load_json(CONDUCTANCE_SPINE_CERTIFICATE)
    residual_report = load_json(RESIDUAL_CHART_REPORT)
    residual_chart = load_json(RESIDUAL_CHART_JSON)
    residual_certificate = load_json(RESIDUAL_CHART_CERTIFICATE)
    spine_tables = np.load(CONDUCTANCE_SPINE_TABLES, allow_pickle=False)
    residual_tables = np.load(RESIDUAL_CHART_TABLES, allow_pickle=False)

    conductance_rows = read_int_csv(CONDUCTANCE_SPINE_EDGES)
    carrier_rows = {
        int(row["carrier_mask_class_id"]): row
        for row in read_int_csv(RESIDUAL_CHART_CARRIER_CSV)
    }

    edge_rows: list[dict[str, int]] = []
    vertex_rows: list[dict[str, int]] = []
    cumulative_entropy = 0
    for row in conductance_rows:
        positive_carrier = carrier_rows[int(row["positive_carrier_mask_class_id"])]
        negative_carrier = carrier_rows[int(row["negative_carrier_mask_class_id"])]
        positive_point = carrier_point(positive_carrier)
        negative_point = carrier_point(negative_carrier)
        positive_axis = int(positive_carrier["axis_coordinate_x1e12"])
        negative_axis = int(negative_carrier["axis_coordinate_x1e12"])
        positive_residual = int(positive_carrier["signed_residual_coordinate_x1e12"])
        negative_residual = int(negative_carrier["signed_residual_coordinate_x1e12"])
        axis_delta = abs(positive_axis - negative_axis)
        residual_delta = abs(positive_residual - negative_residual)
        residual_bend_fraction = scaled_ratio(
            residual_delta,
            axis_delta + residual_delta,
        )
        edge_entropy = int(row["total_entropy_contribution_x1e12"])
        cumulative_entropy += edge_entropy
        axis_midpoint = (positive_axis + negative_axis) // 2
        residual_midpoint = (positive_residual + negative_residual) // 2
        midpoint_x = (
            int(positive_carrier["carrier_center_x_x1e12"])
            + int(negative_carrier["carrier_center_x_x1e12"])
        ) // 2
        midpoint_y = (
            int(positive_carrier["carrier_center_y_x1e12"])
            + int(negative_carrier["carrier_center_y_x1e12"])
        ) // 2
        edge_rows.append(
            {
                "boundary_spine_rank": int(row["boundary_spine_rank"]),
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "positive_carrier_mask_class_id": int(
                    row["positive_carrier_mask_class_id"]
                ),
                "negative_carrier_mask_class_id": int(
                    row["negative_carrier_mask_class_id"]
                ),
                "boundary_partition_code": int(row["boundary_partition_code"]),
                "undirected_stationary_flux_x1e12": int(
                    row["undirected_stationary_flux_x1e12"]
                ),
                "total_entropy_contribution_x1e12": edge_entropy,
                "positive_center_x_x1e12": int(
                    positive_carrier["carrier_center_x_x1e12"]
                ),
                "positive_center_y_x1e12": int(
                    positive_carrier["carrier_center_y_x1e12"]
                ),
                "negative_center_x_x1e12": int(
                    negative_carrier["carrier_center_x_x1e12"]
                ),
                "negative_center_y_x1e12": int(
                    negative_carrier["carrier_center_y_x1e12"]
                ),
                "positive_axis_coordinate_x1e12": positive_axis,
                "negative_axis_coordinate_x1e12": negative_axis,
                "positive_residual_coordinate_x1e12": positive_residual,
                "negative_residual_coordinate_x1e12": negative_residual,
                "axis_delta_abs_x1e12": axis_delta,
                "residual_delta_abs_x1e12": residual_delta,
                "residual_bend_fraction_x1e12": residual_bend_fraction,
                "hyperbolic_edge_length_x1e12": scaled_float(
                    poincare_distance(positive_point, negative_point)
                ),
                "euclidean_edge_length_x1e12": scaled_float(
                    euclidean_distance(positive_point, negative_point)
                ),
                "axis_midpoint_x1e12": axis_midpoint,
                "residual_midpoint_x1e12": residual_midpoint,
                "residual_excursion_x1e12": max(
                    abs(positive_residual),
                    abs(negative_residual),
                ),
                "axis_dominant_flag": 1 if axis_delta >= residual_delta else 0,
                "residual_dominant_flag": 1 if residual_delta > axis_delta else 0,
            }
        )
        vertex_rows.append(
            {
                "polyline_vertex_rank": len(vertex_rows) + 1,
                "boundary_spine_rank": int(row["boundary_spine_rank"]),
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "midpoint_x_x1e12": midpoint_x,
                "midpoint_y_x1e12": midpoint_y,
                "axis_midpoint_x1e12": axis_midpoint,
                "residual_midpoint_x1e12": residual_midpoint,
                "edge_entropy_contribution_x1e12": edge_entropy,
                "cumulative_entropy_contribution_x1e12": cumulative_entropy,
            }
        )

    transition_rows: list[dict[str, int]] = []
    for index, (left, right) in enumerate(zip(vertex_rows, vertex_rows[1:])):
        left_point = (
            int(left["midpoint_x_x1e12"]) / PROBABILITY_SCALE,
            int(left["midpoint_y_x1e12"]) / PROBABILITY_SCALE,
        )
        right_point = (
            int(right["midpoint_x_x1e12"]) / PROBABILITY_SCALE,
            int(right["midpoint_y_x1e12"]) / PROBABILITY_SCALE,
        )
        axis_transition = abs(
            int(right["axis_midpoint_x1e12"]) - int(left["axis_midpoint_x1e12"])
        )
        residual_transition = abs(
            int(right["residual_midpoint_x1e12"])
            - int(left["residual_midpoint_x1e12"])
        )
        transition_rows.append(
            {
                "polyline_transition_id": index,
                "from_boundary_spine_rank": int(left["boundary_spine_rank"]),
                "to_boundary_spine_rank": int(right["boundary_spine_rank"]),
                "from_boundary_mask_edge_id": int(left["boundary_mask_edge_id"]),
                "to_boundary_mask_edge_id": int(right["boundary_mask_edge_id"]),
                "from_midpoint_x_x1e12": int(left["midpoint_x_x1e12"]),
                "from_midpoint_y_x1e12": int(left["midpoint_y_x1e12"]),
                "to_midpoint_x_x1e12": int(right["midpoint_x_x1e12"]),
                "to_midpoint_y_x1e12": int(right["midpoint_y_x1e12"]),
                "axis_transition_abs_x1e12": axis_transition,
                "residual_transition_abs_x1e12": residual_transition,
                "residual_bend_fraction_x1e12": scaled_ratio(
                    residual_transition,
                    axis_transition + residual_transition,
                ),
                "hyperbolic_transition_length_x1e12": scaled_float(
                    poincare_distance(left_point, right_point)
                ),
            }
        )

    top_five_edges = edge_rows[:5]
    residual_dominant_edges = [
        row for row in edge_rows if int(row["residual_dominant_flag"]) == 1
    ]
    top_five_transitions = transition_rows[:4]

    top_five_axis = weighted_average(
        top_five_edges,
        "axis_delta_abs_x1e12",
        "total_entropy_contribution_x1e12",
    )
    top_five_residual = weighted_average(
        top_five_edges,
        "residual_delta_abs_x1e12",
        "total_entropy_contribution_x1e12",
    )
    full_axis = weighted_average(
        edge_rows,
        "axis_delta_abs_x1e12",
        "total_entropy_contribution_x1e12",
    )
    full_residual = weighted_average(
        edge_rows,
        "residual_delta_abs_x1e12",
        "total_entropy_contribution_x1e12",
    )
    polyline_axis_total = sum(
        int(row["axis_transition_abs_x1e12"]) for row in transition_rows
    )
    polyline_residual_total = sum(
        int(row["residual_transition_abs_x1e12"]) for row in transition_rows
    )
    top_five_polyline_axis_total = sum(
        int(row["axis_transition_abs_x1e12"]) for row in top_five_transitions
    )
    top_five_polyline_residual_total = sum(
        int(row["residual_transition_abs_x1e12"]) for row in top_five_transitions
    )

    observable_values = {
        "boundary_edge_count": len(edge_rows),
        "polyline_vertex_count": len(vertex_rows),
        "polyline_transition_count": len(transition_rows),
        "top_spine_edge_id": int(edge_rows[0]["boundary_mask_edge_id"]),
        "top_spine_edge_axis_delta": int(edge_rows[0]["axis_delta_abs_x1e12"]),
        "top_spine_edge_residual_delta": int(
            edge_rows[0]["residual_delta_abs_x1e12"]
        ),
        "top_spine_edge_bend_fraction": int(
            edge_rows[0]["residual_bend_fraction_x1e12"]
        ),
        "top_spine_edge_hyperbolic_length": int(
            edge_rows[0]["hyperbolic_edge_length_x1e12"]
        ),
        "top_five_entropy_weighted_axis_delta": top_five_axis,
        "top_five_entropy_weighted_residual_delta": top_five_residual,
        "top_five_entropy_weighted_bend_fraction": scaled_ratio(
            top_five_residual,
            top_five_axis + top_five_residual,
        ),
        "top_five_entropy_weighted_hyperbolic_length": weighted_average(
            top_five_edges,
            "hyperbolic_edge_length_x1e12",
            "total_entropy_contribution_x1e12",
        ),
        "full_entropy_weighted_axis_delta": full_axis,
        "full_entropy_weighted_residual_delta": full_residual,
        "full_entropy_weighted_bend_fraction": scaled_ratio(
            full_residual,
            full_axis + full_residual,
        ),
        "full_entropy_weighted_hyperbolic_length": weighted_average(
            edge_rows,
            "hyperbolic_edge_length_x1e12",
            "total_entropy_contribution_x1e12",
        ),
        "residual_dominant_edge_count": len(residual_dominant_edges),
        "residual_dominant_edge_entropy_fraction": scaled_ratio(
            sum(
                int(row["total_entropy_contribution_x1e12"])
                for row in residual_dominant_edges
            ),
            sum(int(row["total_entropy_contribution_x1e12"]) for row in edge_rows),
        ),
        "polyline_total_axis_travel": polyline_axis_total,
        "polyline_total_residual_travel": polyline_residual_total,
        "polyline_total_bend_fraction": scaled_ratio(
            polyline_residual_total,
            polyline_axis_total + polyline_residual_total,
        ),
        "polyline_total_hyperbolic_length": sum(
            int(row["hyperbolic_transition_length_x1e12"])
            for row in transition_rows
        ),
        "top_five_polyline_axis_travel": top_five_polyline_axis_total,
        "top_five_polyline_residual_travel": top_five_polyline_residual_total,
        "top_five_polyline_bend_fraction": scaled_ratio(
            top_five_polyline_residual_total,
            top_five_polyline_axis_total + top_five_polyline_residual_total,
        ),
        "top_five_polyline_hyperbolic_length": sum(
            int(row["hyperbolic_transition_length_x1e12"])
            for row in top_five_transitions
        ),
        "polyline_axis_span": max(int(row["axis_midpoint_x1e12"]) for row in vertex_rows)
        - min(int(row["axis_midpoint_x1e12"]) for row in vertex_rows),
        "polyline_residual_span": max(
            int(row["residual_midpoint_x1e12"]) for row in vertex_rows
        )
        - min(int(row["residual_midpoint_x1e12"]) for row in vertex_rows),
        "top_five_polyline_axis_span": max(
            int(row["axis_midpoint_x1e12"]) for row in vertex_rows[:5]
        )
        - min(int(row["axis_midpoint_x1e12"]) for row in vertex_rows[:5]),
        "top_five_polyline_residual_span": max(
            int(row["residual_midpoint_x1e12"]) for row in vertex_rows[:5]
        )
        - min(int(row["residual_midpoint_x1e12"]) for row in vertex_rows[:5]),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": int(code),
            "value_x1e12": int(observable_values[name]),
            "aux_id": -1,
        }
        for index, (name, code) in enumerate(
            sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
        )
    ]

    edge_table = table_from_rows(SPINE_POINCARE_EDGE_COLUMNS, edge_rows)
    vertex_table = table_from_rows(SPINE_POLYLINE_VERTEX_COLUMNS, vertex_rows)
    transition_table = table_from_rows(
        SPINE_POLYLINE_TRANSITION_COLUMNS,
        transition_rows,
    )
    observable_table = table_from_rows(
        SPINE_POINCARE_OBSERVABLE_COLUMNS,
        observable_rows,
    )

    checks = {
        "conductance_spine_report_certified": spine_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_CONDUCTANCE_SPINE_CERTIFIED",
        "conductance_spine_certificate_certified": spine_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_CONDUCTANCE_SPINE_CERTIFIED",
        "residual_chart_report_certified": residual_report.get("status")
        == "C985_D20_SIGNATURE_GEODESIC_RESIDUAL_CHART_CERTIFIED",
        "residual_chart_certificate_certified": residual_certificate.get("status")
        == "C985_D20_SIGNATURE_GEODESIC_RESIDUAL_CHART_CERTIFIED",
        "boundary_edge_count_is_16": len(edge_rows) == 16,
        "polyline_vertex_count_is_16": len(vertex_rows) == 16,
        "polyline_transition_count_is_15": len(transition_rows) == 15,
        "spine_order_matches_conductance_spine": [
            int(row["boundary_mask_edge_id"]) for row in edge_rows
        ]
        == spine_report["witness"]["spine_order_boundary_mask_edge_ids"],
        "top_spine_edge_axis_dominant": observable_values[
            "top_spine_edge_axis_delta"
        ]
        > observable_values["top_spine_edge_residual_delta"],
        "top_spine_edge_metrics_match_expected": (
            observable_values["top_spine_edge_id"],
            observable_values["top_spine_edge_axis_delta"],
            observable_values["top_spine_edge_residual_delta"],
            observable_values["top_spine_edge_bend_fraction"],
            observable_values["top_spine_edge_hyperbolic_length"],
        )
        == (14, 269936014924, 172424508261, 389782765920, 321097465327),
        "top_five_edge_cloud_axis_dominant": observable_values[
            "top_five_entropy_weighted_axis_delta"
        ]
        > observable_values["top_five_entropy_weighted_residual_delta"],
        "top_five_edge_cloud_metrics_match_expected": (
            observable_values["top_five_entropy_weighted_axis_delta"],
            observable_values["top_five_entropy_weighted_residual_delta"],
            observable_values["top_five_entropy_weighted_bend_fraction"],
            observable_values["top_five_entropy_weighted_hyperbolic_length"],
        )
        == (169799011239, 94652654063, 357920431149, 206224183865),
        "full_edge_cloud_residual_bending": observable_values[
            "full_entropy_weighted_residual_delta"
        ]
        > observable_values["full_entropy_weighted_axis_delta"],
        "full_edge_cloud_metrics_match_expected": (
            observable_values["full_entropy_weighted_axis_delta"],
            observable_values["full_entropy_weighted_residual_delta"],
            observable_values["full_entropy_weighted_bend_fraction"],
            observable_values["full_entropy_weighted_hyperbolic_length"],
        )
        == (127563694032, 159064775410, 554951068607, 228645586683),
        "residual_dominant_edge_set_matches_expected": [
            int(row["boundary_mask_edge_id"]) for row in residual_dominant_edges
        ]
        == [6, 7, 8, 11, 9, 12, 5, 10, 4],
        "residual_dominant_entropy_fraction_matches_expected": observable_values[
            "residual_dominant_edge_entropy_fraction"
        ]
        == 488542794331,
        "entropy_midpoint_polyline_residual_bends": observable_values[
            "polyline_total_residual_travel"
        ]
        > observable_values["polyline_total_axis_travel"],
        "entropy_midpoint_polyline_metrics_match_expected": (
            observable_values["polyline_total_axis_travel"],
            observable_values["polyline_total_residual_travel"],
            observable_values["polyline_total_bend_fraction"],
            observable_values["polyline_total_hyperbolic_length"],
        )
        == (950955396598, 2431519629877, 718858117457, 2701324116998),
        "top_five_midpoint_polyline_residual_bends": observable_values[
            "top_five_polyline_residual_travel"
        ]
        > observable_values["top_five_polyline_axis_travel"],
        "top_five_midpoint_polyline_metrics_match_expected": (
            observable_values["top_five_polyline_axis_travel"],
            observable_values["top_five_polyline_residual_travel"],
            observable_values["top_five_polyline_bend_fraction"],
            observable_values["top_five_polyline_hyperbolic_length"],
        )
        == (261932815628, 480761936246, 647321036042, 548672938221),
        "polyline_spans_match_expected": (
            observable_values["polyline_axis_span"],
            observable_values["polyline_residual_span"],
            observable_values["top_five_polyline_axis_span"],
            observable_values["top_five_polyline_residual_span"],
        )
        == (257126409278, 575309726652, 171860556085, 300700062647),
        "edge_table_shape_is_16_by_25": tuple(edge_table.shape)
        == (16, len(SPINE_POINCARE_EDGE_COLUMNS)),
        "polyline_vertex_table_shape_is_16_by_9": tuple(vertex_table.shape)
        == (16, len(SPINE_POLYLINE_VERTEX_COLUMNS)),
        "polyline_transition_table_shape_is_15_by_13": tuple(transition_table.shape)
        == (15, len(SPINE_POLYLINE_TRANSITION_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(SPINE_POINCARE_OBSERVABLE_COLUMNS)),
        "conductance_spine_json_schema_available": spine.get("schema")
        == "c985.d20_signature_boundary_conductance_spine@1",
        "residual_chart_json_schema_available": residual_chart.get("schema")
        == "c985.d20_signature_geodesic_residual_chart@1",
        "conductance_spine_tables_available": "conductance_spine_edge_table"
        in spine_tables.files,
        "residual_chart_tables_available": "carrier_residual_chart_table"
        in residual_tables.files,
    }

    witness = {
        "boundary_edge_count": len(edge_rows),
        "polyline_vertex_count": len(vertex_rows),
        "polyline_transition_count": len(transition_rows),
        "spine_order_boundary_mask_edge_ids": [
            int(row["boundary_mask_edge_id"]) for row in edge_rows
        ],
        "top_spine_edge": {
            "boundary_mask_edge_id": observable_values["top_spine_edge_id"],
            "axis_delta_abs_x1e12": observable_values["top_spine_edge_axis_delta"],
            "residual_delta_abs_x1e12": observable_values[
                "top_spine_edge_residual_delta"
            ],
            "residual_bend_fraction_x1e12": observable_values[
                "top_spine_edge_bend_fraction"
            ],
            "hyperbolic_edge_length_x1e12": observable_values[
                "top_spine_edge_hyperbolic_length"
            ],
            "axis_dominant": True,
        },
        "top_five_edge_cloud": {
            "boundary_mask_edge_ids": [
                int(row["boundary_mask_edge_id"]) for row in top_five_edges
            ],
            "entropy_weighted_axis_delta_x1e12": observable_values[
                "top_five_entropy_weighted_axis_delta"
            ],
            "entropy_weighted_residual_delta_x1e12": observable_values[
                "top_five_entropy_weighted_residual_delta"
            ],
            "entropy_weighted_bend_fraction_x1e12": observable_values[
                "top_five_entropy_weighted_bend_fraction"
            ],
            "entropy_weighted_hyperbolic_length_x1e12": observable_values[
                "top_five_entropy_weighted_hyperbolic_length"
            ],
            "axis_dominant": True,
        },
        "full_edge_cloud": {
            "entropy_weighted_axis_delta_x1e12": observable_values[
                "full_entropy_weighted_axis_delta"
            ],
            "entropy_weighted_residual_delta_x1e12": observable_values[
                "full_entropy_weighted_residual_delta"
            ],
            "entropy_weighted_bend_fraction_x1e12": observable_values[
                "full_entropy_weighted_bend_fraction"
            ],
            "entropy_weighted_hyperbolic_length_x1e12": observable_values[
                "full_entropy_weighted_hyperbolic_length"
            ],
            "residual_bending": True,
        },
        "residual_dominant_edges": {
            "boundary_mask_edge_ids": [
                int(row["boundary_mask_edge_id"]) for row in residual_dominant_edges
            ],
            "edge_count": len(residual_dominant_edges),
            "entropy_fraction_x1e12": observable_values[
                "residual_dominant_edge_entropy_fraction"
            ],
        },
        "entropy_midpoint_polyline": {
            "axis_travel_x1e12": observable_values["polyline_total_axis_travel"],
            "residual_travel_x1e12": observable_values[
                "polyline_total_residual_travel"
            ],
            "residual_bend_fraction_x1e12": observable_values[
                "polyline_total_bend_fraction"
            ],
            "hyperbolic_length_x1e12": observable_values[
                "polyline_total_hyperbolic_length"
            ],
            "axis_span_x1e12": observable_values["polyline_axis_span"],
            "residual_span_x1e12": observable_values["polyline_residual_span"],
        },
        "top_five_entropy_midpoint_polyline": {
            "axis_travel_x1e12": observable_values["top_five_polyline_axis_travel"],
            "residual_travel_x1e12": observable_values[
                "top_five_polyline_residual_travel"
            ],
            "residual_bend_fraction_x1e12": observable_values[
                "top_five_polyline_bend_fraction"
            ],
            "hyperbolic_length_x1e12": observable_values[
                "top_five_polyline_hyperbolic_length"
            ],
            "axis_span_x1e12": observable_values["top_five_polyline_axis_span"],
            "residual_span_x1e12": observable_values[
                "top_five_polyline_residual_span"
            ],
        },
        "spine_poincare_edge_table_sha256": sha_array(edge_table),
        "spine_polyline_vertex_table_sha256": sha_array(vertex_table),
        "spine_polyline_transition_table_sha256": sha_array(transition_table),
        "spine_poincare_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_poincare_path_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_POINCARE_PATH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the dominant conductance edge 14 is axis-dominant inside the residual chart",
            "the top-five conductance edge cloud is axis-dominant when weighted by edge entropy",
            "the full 16-edge cloud is residual-bending, with residual travel exceeding axis travel",
            "the entropy-ordered midpoint polyline bends strongly through the residual coordinate",
            "the Poincare pushdown preserves the conductance-spine order and certified carrier-mask coordinates",
        ],
    }

    path_readout = {
        "schema": "c985.d20_signature_boundary_spine_poincare_path@1",
        "object": "d20",
        "path_rule": {
            "source": "certified conductance-spine edges and certified residual Poincare carrier coordinates",
            "edge_geometry": "positive-to-negative residual boundary segments in the Poincare disk",
            "polyline_geometry": "entropy-ordered Euclidean midpoints of those boundary segments",
            "axis_test": "compare absolute geodesic-axis displacement with signed perpendicular residual displacement",
            "bend_reading": "top edge and top-five edge cloud track the axis, while the full ranked midpoint path bends through residual coordinate",
        },
        "spine_order_boundary_mask_edge_ids": witness[
            "spine_order_boundary_mask_edge_ids"
        ],
        "top_spine_edge": witness["top_spine_edge"],
        "top_five_edge_cloud": witness["top_five_edge_cloud"],
        "full_edge_cloud": witness["full_edge_cloud"],
        "entropy_midpoint_polyline": witness["entropy_midpoint_polyline"],
        "top_five_entropy_midpoint_polyline": witness[
            "top_five_entropy_midpoint_polyline"
        ],
        "spine_poincare_edges": [
            {key: int(value) for key, value in row.items()} for row in edge_rows
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_poincare_path@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The entropy-ordered conductance spine has a certified Poincare "
            "pushdown: its dominant edge and top-five edge cloud track the "
            "quotient geodesic axis, but the full ordered midpoint polyline "
            "bends through the residual coordinate."
        ),
        "stage_protocol": {
            "draft": "attach conductance-spine edges to certified Poincare carrier-mask centers and residual-chart coordinates",
            "witness": "materialize edge segments, entropy-ordered midpoint vertices, and midpoint transitions",
            "coherence": "check spine order, top-edge/top-five/full-spine axis-residual metrics, and table reproducibility",
            "closure": "certify finite Poincare spine geometry without claiming a continuum geodesic-flow law",
            "emit": "emit Poincare-spine JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "conductance_spine_report": input_entry(
                CONDUCTANCE_SPINE_REPORT,
                {
                    "status": spine_report.get("status"),
                    "certificate_sha256": spine_report.get("certificate_sha256"),
                },
            ),
            "conductance_spine": input_entry(CONDUCTANCE_SPINE_JSON),
            "conductance_spine_tables": input_entry(CONDUCTANCE_SPINE_TABLES),
            "conductance_spine_certificate": input_entry(
                CONDUCTANCE_SPINE_CERTIFICATE
            ),
            "conductance_spine_edges": input_entry(CONDUCTANCE_SPINE_EDGES),
            "residual_chart_report": input_entry(
                RESIDUAL_CHART_REPORT,
                {
                    "status": residual_report.get("status"),
                    "certificate_sha256": residual_report.get("certificate_sha256"),
                },
            ),
            "residual_chart": input_entry(RESIDUAL_CHART_JSON),
            "residual_chart_tables": input_entry(RESIDUAL_CHART_TABLES),
            "residual_chart_certificate": input_entry(RESIDUAL_CHART_CERTIFICATE),
            "residual_chart_carriers": input_entry(RESIDUAL_CHART_CARRIER_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_poincare_path": relpath(
                OUT_DIR / "signature_boundary_spine_poincare_path.json"
            ),
            "boundary_spine_poincare_edges_csv": relpath(
                OUT_DIR / "boundary_spine_poincare_edges.csv"
            ),
            "boundary_spine_poincare_polyline_vertices_csv": relpath(
                OUT_DIR / "boundary_spine_poincare_polyline_vertices.csv"
            ),
            "boundary_spine_poincare_polyline_transitions_csv": relpath(
                OUT_DIR / "boundary_spine_poincare_polyline_transitions.csv"
            ),
            "boundary_spine_poincare_observables_csv": relpath(
                OUT_DIR / "boundary_spine_poincare_observables.csv"
            ),
            "signature_boundary_spine_poincare_path_tables": relpath(
                OUT_DIR / "signature_boundary_spine_poincare_path_tables.npz"
            ),
            "signature_boundary_spine_poincare_path_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_poincare_path_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "Poincare edge geometry for all 16 entropy-ordered residual boundary conductance edges",
                "axis-versus-residual bend metrics for the dominant edge, top-five edge cloud, and full edge cloud",
                "the entropy-ordered midpoint polyline and its residual-bending travel statistics",
                "the distinction between local axis tracking and global residual bending",
            ],
            "does_not_certify_because_not_required": [
                "that the ranked midpoint polyline is a geodesic or flow trajectory",
                "a continuum conductance law, diffusion limit, or mixing-time estimate",
                "higher-eigenmode Poincare spines",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the residual-bending Poincare spine as a routing object: "
            "certify the minimal entropy prefix whose midpoint polyline crosses "
            "from axis-tracking to residual-dominant behavior, then compare that "
            "prefix with the high/central/negative cell-complex regions."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_poincare_path_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified conductance-spine and residual-chart artifacts",
            "attach every conductance edge to Poincare carrier-mask endpoints",
            "compute axis/residual deltas, Poincare edge lengths, and entropy-ordered midpoint polyline transitions",
            "verify local axis tracking and global residual bending observables",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_poincare_path": path_readout,
        "boundary_spine_poincare_edges_csv": csv_text(
            SPINE_POINCARE_EDGE_COLUMNS,
            edge_rows,
        ),
        "boundary_spine_poincare_polyline_vertices_csv": csv_text(
            SPINE_POLYLINE_VERTEX_COLUMNS,
            vertex_rows,
        ),
        "boundary_spine_poincare_polyline_transitions_csv": csv_text(
            SPINE_POLYLINE_TRANSITION_COLUMNS,
            transition_rows,
        ),
        "boundary_spine_poincare_observables_csv": csv_text(
            SPINE_POINCARE_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "spine_poincare_edge_table": edge_table,
        "spine_polyline_vertex_table": vertex_table,
        "spine_polyline_transition_table": transition_table,
        "spine_poincare_observable_table": observable_table,
        "signature_boundary_spine_poincare_path_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_poincare_path.json",
        payloads["signature_boundary_spine_poincare_path"],
    )
    (OUT_DIR / "boundary_spine_poincare_edges.csv").write_text(
        payloads["boundary_spine_poincare_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_spine_poincare_polyline_vertices.csv").write_text(
        payloads["boundary_spine_poincare_polyline_vertices_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_spine_poincare_polyline_transitions.csv").write_text(
        payloads["boundary_spine_poincare_polyline_transitions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_spine_poincare_observables.csv").write_text(
        payloads["boundary_spine_poincare_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_poincare_path_tables.npz",
        spine_poincare_edge_table=payloads["spine_poincare_edge_table"],
        spine_polyline_vertex_table=payloads["spine_polyline_vertex_table"],
        spine_polyline_transition_table=payloads[
            "spine_polyline_transition_table"
        ],
        spine_poincare_observable_table=payloads[
            "spine_poincare_observable_table"
        ],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_poincare_path_certificate.json",
        payloads["signature_boundary_spine_poincare_path_certificate"],
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
                "top_spine_edge": witness["top_spine_edge"],
                "top_five_edge_cloud": witness["top_five_edge_cloud"],
                "full_edge_cloud": witness["full_edge_cloud"],
                "entropy_midpoint_polyline": witness["entropy_midpoint_polyline"],
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
