from __future__ import annotations

import csv
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_poincare_path import (
        OUT_DIR as SPINE_PATH_DIR,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        OUT_DIR as CELL_COMPLEX_DIR,
        REGION_CENTRAL,
        REGION_HIGH,
        REGION_NEGATIVE,
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
    from derive_c985_d20_signature_boundary_spine_poincare_path import (
        OUT_DIR as SPINE_PATH_DIR,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        OUT_DIR as CELL_COMPLEX_DIR,
        REGION_CENTRAL,
        REGION_HIGH,
        REGION_NEGATIVE,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_routing_prefix"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_ROUTING_PREFIX_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SPINE_PATH_REPORT = SPINE_PATH_DIR / "report.json"
SPINE_PATH_JSON = SPINE_PATH_DIR / "signature_boundary_spine_poincare_path.json"
SPINE_PATH_TABLES = SPINE_PATH_DIR / "signature_boundary_spine_poincare_path_tables.npz"
SPINE_PATH_CERTIFICATE = (
    SPINE_PATH_DIR / "signature_boundary_spine_poincare_path_certificate.json"
)
SPINE_PATH_EDGES = SPINE_PATH_DIR / "boundary_spine_poincare_edges.csv"
SPINE_PATH_TRANSITIONS = (
    SPINE_PATH_DIR / "boundary_spine_poincare_polyline_transitions.csv"
)

CELL_COMPLEX_REPORT = CELL_COMPLEX_DIR / "report.json"
CELL_COMPLEX_JSON = CELL_COMPLEX_DIR / "signature_residual_cell_complex.json"
CELL_COMPLEX_TABLES = CELL_COMPLEX_DIR / "signature_residual_cell_complex_tables.npz"
CELL_COMPLEX_CERTIFICATE = CELL_COMPLEX_DIR / "signature_residual_cell_complex_certificate.json"
CELL_COMPLEX_VERTICES = CELL_COMPLEX_DIR / "carrier_region_vertices.csv"
CELL_COMPLEX_EDGES = CELL_COMPLEX_DIR / "carrier_region_edges.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_boundary_spine_routing_prefix.py"
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_spine_routing_prefix.py"
)

PROBABILITY_SCALE = 1_000_000_000_000

PREFIX_KIND_EDGE_CLOUD = 1
PREFIX_KIND_MIDPOINT_POLYLINE = 2
REGION_SCOPE_FULL = 0
REGION_SCOPE_BOUNDARY_ACTIVE = 1

ROUTING_PREFIX_SUMMARY_COLUMNS = [
    "prefix_length",
    "last_boundary_mask_edge_id",
    "cumulative_entropy_x1e12",
    "entropy_fraction_of_boundary_crossing_x1e12",
    "cumulative_flux_x1e12",
    "flux_fraction_of_cut_x1e12",
    "edge_entropy_weighted_axis_delta_x1e12",
    "edge_entropy_weighted_residual_delta_x1e12",
    "edge_cloud_bend_fraction_x1e12",
    "edge_entropy_weighted_hyperbolic_length_x1e12",
    "edge_cloud_residual_dominant_flag",
    "polyline_axis_travel_x1e12",
    "polyline_residual_travel_x1e12",
    "polyline_bend_fraction_x1e12",
    "polyline_hyperbolic_length_x1e12",
    "polyline_residual_dominant_flag",
    "central_negative_edge_count",
    "high_negative_edge_count",
    "positive_high_carrier_bitset",
    "positive_central_carrier_bitset",
    "negative_carrier_bitset",
]

ROUTING_PREFIX_REGION_COLUMNS = [
    "prefix_kind_code",
    "prefix_length",
    "region_code",
    "region_scope_code",
    "region_total_carrier_count",
    "region_total_carrier_bitset",
    "prefix_region_carrier_count",
    "prefix_region_carrier_bitset",
    "covered_carrier_count",
    "covered_carrier_bitset",
    "coverage_fraction_x1e12",
    "missing_carrier_count",
    "missing_carrier_bitset",
]

ROUTING_PREFIX_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "edge_cloud_crossing_prefix_length": 0,
    "edge_cloud_crossing_last_edge_id": 1,
    "edge_cloud_crossing_entropy_fraction": 2,
    "edge_cloud_crossing_flux_fraction": 3,
    "edge_cloud_crossing_axis_delta": 4,
    "edge_cloud_crossing_residual_delta": 5,
    "edge_cloud_crossing_bend_fraction": 6,
    "edge_cloud_crossing_hyperbolic_length": 7,
    "midpoint_polyline_crossing_prefix_length": 8,
    "midpoint_polyline_crossing_last_edge_id": 9,
    "midpoint_polyline_crossing_entropy_fraction": 10,
    "midpoint_polyline_crossing_flux_fraction": 11,
    "midpoint_polyline_crossing_axis_travel": 12,
    "midpoint_polyline_crossing_residual_travel": 13,
    "midpoint_polyline_crossing_bend_fraction": 14,
    "midpoint_polyline_crossing_hyperbolic_length": 15,
    "edge_prefix_central_negative_edge_count": 16,
    "edge_prefix_high_negative_edge_count": 17,
    "edge_prefix_positive_central_boundary_active_coverage": 18,
    "edge_prefix_negative_boundary_active_coverage": 19,
    "edge_prefix_positive_high_boundary_active_coverage": 20,
    "edge_prefix_touched_boundary_active_coverage": 21,
    "polyline_prefix_positive_central_boundary_active_coverage": 22,
    "polyline_prefix_negative_boundary_active_coverage": 23,
    "polyline_prefix_touched_boundary_active_coverage": 24,
    "edge_cloud_crossing_predecessor_prefix_length": 25,
    "edge_cloud_crossing_predecessor_bend_fraction": 26,
}


def rounded_div(numerator: int, denominator: int) -> int:
    quotient, remainder = divmod(int(numerator), int(denominator))
    if 2 * remainder >= int(denominator):
        quotient += 1
    return int(quotient)


def scaled_ratio(numerator: int, denominator: int) -> int:
    if int(denominator) == 0:
        return 0
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


def bitset(values: set[int] | list[int]) -> int:
    result = 0
    for value in values:
        result |= 1 << int(value)
    return int(result)


def popcount(value: int) -> int:
    return int(int(value).bit_count())


def prefix_carrier_bitsets(rows: list[dict[str, int]]) -> dict[str, int]:
    high = {
        int(row["positive_carrier_mask_class_id"])
        for row in rows
        if int(row["boundary_partition_code"]) == EDGE_HIGH_NEGATIVE
    }
    central = {
        int(row["positive_carrier_mask_class_id"])
        for row in rows
        if int(row["boundary_partition_code"]) == EDGE_CENTRAL_NEGATIVE
    }
    negative = {int(row["negative_carrier_mask_class_id"]) for row in rows}
    return {
        "high": bitset(high),
        "central": bitset(central),
        "negative": bitset(negative),
    }


def build_prefix_summary(
    edge_rows: list[dict[str, int]],
    transition_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    total_entropy = sum(int(row["total_entropy_contribution_x1e12"]) for row in edge_rows)
    total_flux = sum(int(row["undirected_stationary_flux_x1e12"]) for row in edge_rows)
    summary_rows: list[dict[str, int]] = []
    for prefix_length in range(1, len(edge_rows) + 1):
        edge_prefix = edge_rows[:prefix_length]
        transition_prefix = transition_rows[: max(0, prefix_length - 1)]
        weighted_axis = weighted_average(
            edge_prefix,
            "axis_delta_abs_x1e12",
            "total_entropy_contribution_x1e12",
        )
        weighted_residual = weighted_average(
            edge_prefix,
            "residual_delta_abs_x1e12",
            "total_entropy_contribution_x1e12",
        )
        polyline_axis = sum(
            int(row["axis_transition_abs_x1e12"]) for row in transition_prefix
        )
        polyline_residual = sum(
            int(row["residual_transition_abs_x1e12"]) for row in transition_prefix
        )
        carriers = prefix_carrier_bitsets(edge_prefix)
        cumulative_entropy = sum(
            int(row["total_entropy_contribution_x1e12"]) for row in edge_prefix
        )
        cumulative_flux = sum(
            int(row["undirected_stationary_flux_x1e12"]) for row in edge_prefix
        )
        summary_rows.append(
            {
                "prefix_length": prefix_length,
                "last_boundary_mask_edge_id": int(edge_prefix[-1]["boundary_mask_edge_id"]),
                "cumulative_entropy_x1e12": cumulative_entropy,
                "entropy_fraction_of_boundary_crossing_x1e12": scaled_ratio(
                    cumulative_entropy,
                    total_entropy,
                ),
                "cumulative_flux_x1e12": cumulative_flux,
                "flux_fraction_of_cut_x1e12": scaled_ratio(cumulative_flux, total_flux),
                "edge_entropy_weighted_axis_delta_x1e12": weighted_axis,
                "edge_entropy_weighted_residual_delta_x1e12": weighted_residual,
                "edge_cloud_bend_fraction_x1e12": scaled_ratio(
                    weighted_residual,
                    weighted_axis + weighted_residual,
                ),
                "edge_entropy_weighted_hyperbolic_length_x1e12": weighted_average(
                    edge_prefix,
                    "hyperbolic_edge_length_x1e12",
                    "total_entropy_contribution_x1e12",
                ),
                "edge_cloud_residual_dominant_flag": 1
                if weighted_residual > weighted_axis
                else 0,
                "polyline_axis_travel_x1e12": polyline_axis,
                "polyline_residual_travel_x1e12": polyline_residual,
                "polyline_bend_fraction_x1e12": scaled_ratio(
                    polyline_residual,
                    polyline_axis + polyline_residual,
                ),
                "polyline_hyperbolic_length_x1e12": sum(
                    int(row["hyperbolic_transition_length_x1e12"])
                    for row in transition_prefix
                ),
                "polyline_residual_dominant_flag": 1
                if polyline_residual > polyline_axis
                else 0,
                "central_negative_edge_count": sum(
                    1
                    for row in edge_prefix
                    if int(row["boundary_partition_code"]) == EDGE_CENTRAL_NEGATIVE
                ),
                "high_negative_edge_count": sum(
                    1
                    for row in edge_prefix
                    if int(row["boundary_partition_code"]) == EDGE_HIGH_NEGATIVE
                ),
                "positive_high_carrier_bitset": carriers["high"],
                "positive_central_carrier_bitset": carriers["central"],
                "negative_carrier_bitset": carriers["negative"],
            }
        )
    return summary_rows


def region_coverage_row(
    prefix_kind: int,
    prefix_length: int,
    region_code: int,
    region_scope_code: int,
    region_bitset: int,
    prefix_region_bitset: int,
) -> dict[str, int]:
    covered = int(region_bitset) & int(prefix_region_bitset)
    missing = int(region_bitset) & ~int(prefix_region_bitset)
    region_count = popcount(region_bitset)
    covered_count = popcount(covered)
    return {
        "prefix_kind_code": int(prefix_kind),
        "prefix_length": int(prefix_length),
        "region_code": int(region_code),
        "region_scope_code": int(region_scope_code),
        "region_total_carrier_count": region_count,
        "region_total_carrier_bitset": int(region_bitset),
        "prefix_region_carrier_count": popcount(prefix_region_bitset),
        "prefix_region_carrier_bitset": int(prefix_region_bitset),
        "covered_carrier_count": covered_count,
        "covered_carrier_bitset": covered,
        "coverage_fraction_x1e12": scaled_ratio(covered_count, region_count),
        "missing_carrier_count": popcount(missing),
        "missing_carrier_bitset": missing,
    }


def build_payloads() -> dict[str, Any]:
    spine_path_report = load_json(SPINE_PATH_REPORT)
    spine_path = load_json(SPINE_PATH_JSON)
    spine_path_certificate = load_json(SPINE_PATH_CERTIFICATE)
    cell_complex_report = load_json(CELL_COMPLEX_REPORT)
    cell_complex = load_json(CELL_COMPLEX_JSON)
    cell_complex_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    spine_path_tables = np.load(SPINE_PATH_TABLES, allow_pickle=False)
    cell_complex_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)

    edge_rows = read_int_csv(SPINE_PATH_EDGES)
    transition_rows = read_int_csv(SPINE_PATH_TRANSITIONS)
    cell_vertex_rows = read_int_csv(CELL_COMPLEX_VERTICES)
    cell_edge_rows = read_int_csv(CELL_COMPLEX_EDGES)

    summary_rows = build_prefix_summary(edge_rows, transition_rows)
    edge_crossing = next(
        row for row in summary_rows if int(row["edge_cloud_residual_dominant_flag"]) == 1
    )
    polyline_crossing = next(
        row for row in summary_rows if int(row["polyline_residual_dominant_flag"]) == 1
    )
    edge_predecessor = summary_rows[int(edge_crossing["prefix_length"]) - 2]

    full_region_bitsets = {
        REGION_HIGH: bitset(
            [
                int(row["carrier_mask_class_id"])
                for row in cell_vertex_rows
                if int(row["elbow_region_code"]) == REGION_HIGH
            ]
        ),
        REGION_CENTRAL: bitset(
            [
                int(row["carrier_mask_class_id"])
                for row in cell_vertex_rows
                if int(row["elbow_region_code"]) == REGION_CENTRAL
            ]
        ),
        REGION_NEGATIVE: bitset(
            [
                int(row["carrier_mask_class_id"])
                for row in cell_vertex_rows
                if int(row["elbow_region_code"]) == REGION_NEGATIVE
            ]
        ),
    }
    boundary_active_bitsets = {
        REGION_HIGH: bitset(
            {
                int(row["source_carrier_mask_class_id"])
                if int(row["source_region_code"]) == REGION_HIGH
                else int(row["target_carrier_mask_class_id"])
                for row in cell_edge_rows
                if int(row["edge_partition_code"]) == EDGE_HIGH_NEGATIVE
            }
        ),
        REGION_CENTRAL: bitset(
            {
                int(row["source_carrier_mask_class_id"])
                if int(row["source_region_code"]) == REGION_CENTRAL
                else int(row["target_carrier_mask_class_id"])
                for row in cell_edge_rows
                if int(row["edge_partition_code"]) == EDGE_CENTRAL_NEGATIVE
            }
        ),
        REGION_NEGATIVE: bitset(
            {
                int(row["source_carrier_mask_class_id"])
                if int(row["source_region_code"]) == REGION_NEGATIVE
                else int(row["target_carrier_mask_class_id"])
                for row in cell_edge_rows
                if int(row["edge_partition_code"])
                in (EDGE_HIGH_NEGATIVE, EDGE_CENTRAL_NEGATIVE)
            }
        ),
    }

    def prefix_region_rows(prefix_kind: int, prefix_row: dict[str, int]) -> list[dict[str, int]]:
        carriers = {
            REGION_HIGH: int(prefix_row["positive_high_carrier_bitset"]),
            REGION_CENTRAL: int(prefix_row["positive_central_carrier_bitset"]),
            REGION_NEGATIVE: int(prefix_row["negative_carrier_bitset"]),
        }
        rows: list[dict[str, int]] = []
        for scope_code, region_bitsets in (
            (REGION_SCOPE_FULL, full_region_bitsets),
            (REGION_SCOPE_BOUNDARY_ACTIVE, boundary_active_bitsets),
        ):
            for region_code in (REGION_HIGH, REGION_CENTRAL, REGION_NEGATIVE):
                rows.append(
                    region_coverage_row(
                        prefix_kind,
                        int(prefix_row["prefix_length"]),
                        region_code,
                        scope_code,
                        region_bitsets[region_code],
                        carriers[region_code],
                    )
                )
        return rows

    region_rows = []
    region_rows.extend(
        prefix_region_rows(PREFIX_KIND_EDGE_CLOUD, edge_crossing)
    )
    region_rows.extend(
        prefix_region_rows(PREFIX_KIND_MIDPOINT_POLYLINE, polyline_crossing)
    )

    edge_prefix_region_rows = [
        row
        for row in region_rows
        if int(row["prefix_kind_code"]) == PREFIX_KIND_EDGE_CLOUD
        and int(row["region_scope_code"]) == REGION_SCOPE_BOUNDARY_ACTIVE
    ]
    polyline_prefix_region_rows = [
        row
        for row in region_rows
        if int(row["prefix_kind_code"]) == PREFIX_KIND_MIDPOINT_POLYLINE
        and int(row["region_scope_code"]) == REGION_SCOPE_BOUNDARY_ACTIVE
    ]
    edge_boundary_active_union = (
        boundary_active_bitsets[REGION_HIGH]
        | boundary_active_bitsets[REGION_CENTRAL]
        | boundary_active_bitsets[REGION_NEGATIVE]
    )
    edge_prefix_union = (
        int(edge_crossing["positive_high_carrier_bitset"])
        | int(edge_crossing["positive_central_carrier_bitset"])
        | int(edge_crossing["negative_carrier_bitset"])
    )
    polyline_prefix_union = (
        int(polyline_crossing["positive_high_carrier_bitset"])
        | int(polyline_crossing["positive_central_carrier_bitset"])
        | int(polyline_crossing["negative_carrier_bitset"])
    )

    observable_values = {
        "edge_cloud_crossing_prefix_length": int(edge_crossing["prefix_length"]),
        "edge_cloud_crossing_last_edge_id": int(edge_crossing["last_boundary_mask_edge_id"]),
        "edge_cloud_crossing_entropy_fraction": int(
            edge_crossing["entropy_fraction_of_boundary_crossing_x1e12"]
        ),
        "edge_cloud_crossing_flux_fraction": int(edge_crossing["flux_fraction_of_cut_x1e12"]),
        "edge_cloud_crossing_axis_delta": int(
            edge_crossing["edge_entropy_weighted_axis_delta_x1e12"]
        ),
        "edge_cloud_crossing_residual_delta": int(
            edge_crossing["edge_entropy_weighted_residual_delta_x1e12"]
        ),
        "edge_cloud_crossing_bend_fraction": int(
            edge_crossing["edge_cloud_bend_fraction_x1e12"]
        ),
        "edge_cloud_crossing_hyperbolic_length": int(
            edge_crossing["edge_entropy_weighted_hyperbolic_length_x1e12"]
        ),
        "midpoint_polyline_crossing_prefix_length": int(polyline_crossing["prefix_length"]),
        "midpoint_polyline_crossing_last_edge_id": int(
            polyline_crossing["last_boundary_mask_edge_id"]
        ),
        "midpoint_polyline_crossing_entropy_fraction": int(
            polyline_crossing["entropy_fraction_of_boundary_crossing_x1e12"]
        ),
        "midpoint_polyline_crossing_flux_fraction": int(
            polyline_crossing["flux_fraction_of_cut_x1e12"]
        ),
        "midpoint_polyline_crossing_axis_travel": int(
            polyline_crossing["polyline_axis_travel_x1e12"]
        ),
        "midpoint_polyline_crossing_residual_travel": int(
            polyline_crossing["polyline_residual_travel_x1e12"]
        ),
        "midpoint_polyline_crossing_bend_fraction": int(
            polyline_crossing["polyline_bend_fraction_x1e12"]
        ),
        "midpoint_polyline_crossing_hyperbolic_length": int(
            polyline_crossing["polyline_hyperbolic_length_x1e12"]
        ),
        "edge_prefix_central_negative_edge_count": int(
            edge_crossing["central_negative_edge_count"]
        ),
        "edge_prefix_high_negative_edge_count": int(
            edge_crossing["high_negative_edge_count"]
        ),
        "edge_prefix_positive_central_boundary_active_coverage": next(
            row
            for row in edge_prefix_region_rows
            if int(row["region_code"]) == REGION_CENTRAL
        )["coverage_fraction_x1e12"],
        "edge_prefix_negative_boundary_active_coverage": next(
            row
            for row in edge_prefix_region_rows
            if int(row["region_code"]) == REGION_NEGATIVE
        )["coverage_fraction_x1e12"],
        "edge_prefix_positive_high_boundary_active_coverage": next(
            row
            for row in edge_prefix_region_rows
            if int(row["region_code"]) == REGION_HIGH
        )["coverage_fraction_x1e12"],
        "edge_prefix_touched_boundary_active_coverage": scaled_ratio(
            popcount(edge_boundary_active_union & edge_prefix_union),
            popcount(edge_boundary_active_union),
        ),
        "polyline_prefix_positive_central_boundary_active_coverage": next(
            row
            for row in polyline_prefix_region_rows
            if int(row["region_code"]) == REGION_CENTRAL
        )["coverage_fraction_x1e12"],
        "polyline_prefix_negative_boundary_active_coverage": next(
            row
            for row in polyline_prefix_region_rows
            if int(row["region_code"]) == REGION_NEGATIVE
        )["coverage_fraction_x1e12"],
        "polyline_prefix_touched_boundary_active_coverage": scaled_ratio(
            popcount(edge_boundary_active_union & polyline_prefix_union),
            popcount(edge_boundary_active_union),
        ),
        "edge_cloud_crossing_predecessor_prefix_length": int(
            edge_predecessor["prefix_length"]
        ),
        "edge_cloud_crossing_predecessor_bend_fraction": int(
            edge_predecessor["edge_cloud_bend_fraction_x1e12"]
        ),
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

    summary_table = table_from_rows(ROUTING_PREFIX_SUMMARY_COLUMNS, summary_rows)
    region_table = table_from_rows(ROUTING_PREFIX_REGION_COLUMNS, region_rows)
    observable_table = table_from_rows(
        ROUTING_PREFIX_OBSERVABLE_COLUMNS,
        observable_rows,
    )

    checks = {
        "spine_path_report_certified": spine_path_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_POINCARE_PATH_CERTIFIED",
        "spine_path_certificate_certified": spine_path_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_POINCARE_PATH_CERTIFIED",
        "cell_complex_report_certified": cell_complex_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_complex_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "summary_prefix_count_is_16": len(summary_rows) == 16,
        "region_coverage_rows_are_12": len(region_rows) == 12,
        "edge_cloud_crossing_prefix_matches_expected": (
            int(edge_crossing["prefix_length"]),
            int(edge_crossing["last_boundary_mask_edge_id"]),
            int(edge_crossing["entropy_fraction_of_boundary_crossing_x1e12"]),
            int(edge_crossing["flux_fraction_of_cut_x1e12"]),
        )
        == (8, 11, 728568451090, 777936948054),
        "edge_cloud_crossing_metrics_match_expected": (
            int(edge_crossing["edge_entropy_weighted_axis_delta_x1e12"]),
            int(edge_crossing["edge_entropy_weighted_residual_delta_x1e12"]),
            int(edge_crossing["edge_cloud_bend_fraction_x1e12"]),
            int(edge_crossing["edge_entropy_weighted_hyperbolic_length_x1e12"]),
        )
        == (141037638590, 144281755223, 505685061554, 228204173309),
        "edge_cloud_predecessor_is_axis_tracking": int(
            edge_predecessor["edge_cloud_residual_dominant_flag"]
        )
        == 0
        and int(edge_predecessor["prefix_length"]) == 7
        and int(edge_predecessor["edge_cloud_bend_fraction_x1e12"])
        == 469550522968,
        "midpoint_polyline_crossing_prefix_matches_expected": (
            int(polyline_crossing["prefix_length"]),
            int(polyline_crossing["last_boundary_mask_edge_id"]),
            int(polyline_crossing["entropy_fraction_of_boundary_crossing_x1e12"]),
            int(polyline_crossing["flux_fraction_of_cut_x1e12"]),
        )
        == (2, 15, 262985778341, 318011852725),
        "midpoint_polyline_crossing_metrics_match_expected": (
            int(polyline_crossing["polyline_axis_travel_x1e12"]),
            int(polyline_crossing["polyline_residual_travel_x1e12"]),
            int(polyline_crossing["polyline_bend_fraction_x1e12"]),
            int(polyline_crossing["polyline_hyperbolic_length_x1e12"]),
        )
        == (35307583361, 72277973546, 671818556542, 80649159853),
        "edge_prefix_is_all_central_negative": int(
            edge_crossing["central_negative_edge_count"]
        )
        == 8
        and int(edge_crossing["high_negative_edge_count"]) == 0,
        "edge_prefix_region_bitsets_match_expected": (
            int(edge_crossing["positive_high_carrier_bitset"]),
            int(edge_crossing["positive_central_carrier_bitset"]),
            int(edge_crossing["negative_carrier_bitset"]),
        )
        == (0, 6152, 9088),
        "polyline_prefix_region_bitsets_match_expected": (
            int(polyline_crossing["positive_high_carrier_bitset"]),
            int(polyline_crossing["positive_central_carrier_bitset"]),
            int(polyline_crossing["negative_carrier_bitset"]),
        )
        == (0, 6144, 8192),
        "edge_prefix_boundary_active_region_coverage_matches_expected": (
            observable_values["edge_prefix_positive_central_boundary_active_coverage"],
            observable_values["edge_prefix_negative_boundary_active_coverage"],
            observable_values["edge_prefix_positive_high_boundary_active_coverage"],
            observable_values["edge_prefix_touched_boundary_active_coverage"],
        )
        == (750000000000, 666666666667, 0, 583333333333),
        "polyline_prefix_boundary_active_region_coverage_matches_expected": (
            observable_values[
                "polyline_prefix_positive_central_boundary_active_coverage"
            ],
            observable_values["polyline_prefix_negative_boundary_active_coverage"],
            observable_values["polyline_prefix_touched_boundary_active_coverage"],
        )
        == (500000000000, 166666666667, 250000000000),
        "summary_table_shape_is_16_by_21": tuple(summary_table.shape)
        == (16, len(ROUTING_PREFIX_SUMMARY_COLUMNS)),
        "region_table_shape_is_12_by_13": tuple(region_table.shape)
        == (12, len(ROUTING_PREFIX_REGION_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(ROUTING_PREFIX_OBSERVABLE_COLUMNS)),
        "spine_path_json_schema_available": spine_path.get("schema")
        == "c985.d20_signature_boundary_spine_poincare_path@1",
        "cell_complex_json_schema_available": cell_complex.get("schema")
        == "c985.d20_signature_residual_cell_complex@1",
        "spine_path_tables_available": "spine_poincare_edge_table"
        in spine_path_tables.files,
        "cell_complex_tables_available": "carrier_region_edge_table"
        in cell_complex_tables.files,
    }

    witness = {
        "edge_cloud_crossing_prefix": {
            "prefix_length": int(edge_crossing["prefix_length"]),
            "last_boundary_mask_edge_id": int(edge_crossing["last_boundary_mask_edge_id"]),
            "boundary_mask_edge_ids": [
                int(row["boundary_mask_edge_id"])
                for row in edge_rows[: int(edge_crossing["prefix_length"])]
            ],
            "entropy_fraction_x1e12": int(
                edge_crossing["entropy_fraction_of_boundary_crossing_x1e12"]
            ),
            "flux_fraction_x1e12": int(edge_crossing["flux_fraction_of_cut_x1e12"]),
            "axis_delta_x1e12": int(
                edge_crossing["edge_entropy_weighted_axis_delta_x1e12"]
            ),
            "residual_delta_x1e12": int(
                edge_crossing["edge_entropy_weighted_residual_delta_x1e12"]
            ),
            "bend_fraction_x1e12": int(edge_crossing["edge_cloud_bend_fraction_x1e12"]),
            "hyperbolic_length_x1e12": int(
                edge_crossing["edge_entropy_weighted_hyperbolic_length_x1e12"]
            ),
            "central_negative_edge_count": int(
                edge_crossing["central_negative_edge_count"]
            ),
            "high_negative_edge_count": int(edge_crossing["high_negative_edge_count"]),
        },
        "midpoint_polyline_crossing_prefix": {
            "prefix_length": int(polyline_crossing["prefix_length"]),
            "last_boundary_mask_edge_id": int(
                polyline_crossing["last_boundary_mask_edge_id"]
            ),
            "boundary_mask_edge_ids": [
                int(row["boundary_mask_edge_id"])
                for row in edge_rows[: int(polyline_crossing["prefix_length"])]
            ],
            "entropy_fraction_x1e12": int(
                polyline_crossing["entropy_fraction_of_boundary_crossing_x1e12"]
            ),
            "flux_fraction_x1e12": int(polyline_crossing["flux_fraction_of_cut_x1e12"]),
            "axis_travel_x1e12": int(polyline_crossing["polyline_axis_travel_x1e12"]),
            "residual_travel_x1e12": int(
                polyline_crossing["polyline_residual_travel_x1e12"]
            ),
            "bend_fraction_x1e12": int(polyline_crossing["polyline_bend_fraction_x1e12"]),
            "hyperbolic_length_x1e12": int(
                polyline_crossing["polyline_hyperbolic_length_x1e12"]
            ),
        },
        "edge_cloud_crossing_predecessor": {
            "prefix_length": int(edge_predecessor["prefix_length"]),
            "last_boundary_mask_edge_id": int(
                edge_predecessor["last_boundary_mask_edge_id"]
            ),
            "bend_fraction_x1e12": int(edge_predecessor["edge_cloud_bend_fraction_x1e12"]),
            "residual_dominant": False,
        },
        "edge_prefix_region_coverage": {
            "positive_central_boundary_active_fraction_x1e12": observable_values[
                "edge_prefix_positive_central_boundary_active_coverage"
            ],
            "negative_boundary_active_fraction_x1e12": observable_values[
                "edge_prefix_negative_boundary_active_coverage"
            ],
            "positive_high_boundary_active_fraction_x1e12": observable_values[
                "edge_prefix_positive_high_boundary_active_coverage"
            ],
            "touched_boundary_active_fraction_x1e12": observable_values[
                "edge_prefix_touched_boundary_active_coverage"
            ],
            "positive_central_carrier_bitset": int(
                edge_crossing["positive_central_carrier_bitset"]
            ),
            "negative_carrier_bitset": int(edge_crossing["negative_carrier_bitset"]),
        },
        "polyline_prefix_region_coverage": {
            "positive_central_boundary_active_fraction_x1e12": observable_values[
                "polyline_prefix_positive_central_boundary_active_coverage"
            ],
            "negative_boundary_active_fraction_x1e12": observable_values[
                "polyline_prefix_negative_boundary_active_coverage"
            ],
            "touched_boundary_active_fraction_x1e12": observable_values[
                "polyline_prefix_touched_boundary_active_coverage"
            ],
            "positive_central_carrier_bitset": int(
                polyline_crossing["positive_central_carrier_bitset"]
            ),
            "negative_carrier_bitset": int(polyline_crossing["negative_carrier_bitset"]),
        },
        "routing_prefix_summary_table_sha256": sha_array(summary_table),
        "routing_prefix_region_table_sha256": sha_array(region_table),
        "routing_prefix_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_routing_prefix_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_ROUTING_PREFIX_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the entropy-ordered midpoint polyline becomes residual-dominant at prefix length 2",
            "the entropy-weighted edge cloud remains axis-tracking through prefix 7 and flips at prefix 8",
            "the prefix-8 edge cloud is entirely central-negative and contains no high-negative contact",
            "prefix 8 covers three of four boundary-active central carriers and four of six boundary-active negative carriers",
            "the high-cap contact is absent from the residual-dominant crossing prefix",
        ],
    }

    routing_prefix = {
        "schema": "c985.d20_signature_boundary_spine_routing_prefix@1",
        "object": "d20",
        "routing_rule": {
            "source": "certified Poincare conductance-spine path and residual cell complex",
            "edge_cloud_crossing": "first ranked edge prefix whose entropy-weighted residual displacement exceeds entropy-weighted axis displacement",
            "midpoint_polyline_crossing": "first ranked midpoint-polyline prefix whose residual travel exceeds axis travel",
            "region_comparison": "compare crossing-prefix carrier bitsets with full and boundary-active high/central/negative residual cell regions",
        },
        "edge_cloud_crossing_prefix": witness["edge_cloud_crossing_prefix"],
        "midpoint_polyline_crossing_prefix": witness[
            "midpoint_polyline_crossing_prefix"
        ],
        "edge_prefix_region_coverage": witness["edge_prefix_region_coverage"],
        "polyline_prefix_region_coverage": witness[
            "polyline_prefix_region_coverage"
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_routing_prefix@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The residual-bending Poincare spine has two certified routing "
            "thresholds: the ordered midpoint route bends residual immediately "
            "at prefix 2, while cumulative conductance remains axis-tracking "
            "until the all-central-negative prefix 8."
        ),
        "stage_protocol": {
            "draft": "scan ranked Poincare-spine prefixes for residual-dominant crossings",
            "witness": "materialize cumulative prefix metrics and high/central/negative region coverage",
            "coherence": "check minimal crossing indices, predecessor behavior, and cell-region bitset coverage",
            "closure": "certify finite routing-prefix thresholds without claiming a continuum flow route",
            "emit": "emit routing-prefix JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "spine_path_report": input_entry(
                SPINE_PATH_REPORT,
                {
                    "status": spine_path_report.get("status"),
                    "certificate_sha256": spine_path_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "spine_path": input_entry(SPINE_PATH_JSON),
            "spine_path_tables": input_entry(SPINE_PATH_TABLES),
            "spine_path_certificate": input_entry(SPINE_PATH_CERTIFICATE),
            "spine_path_edges": input_entry(SPINE_PATH_EDGES),
            "spine_path_transitions": input_entry(SPINE_PATH_TRANSITIONS),
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_complex_report.get("status"),
                    "certificate_sha256": cell_complex_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "cell_complex": input_entry(CELL_COMPLEX_JSON),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
            "cell_complex_vertices": input_entry(CELL_COMPLEX_VERTICES),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_routing_prefix": relpath(
                OUT_DIR / "signature_boundary_spine_routing_prefix.json"
            ),
            "routing_prefix_summary_csv": relpath(
                OUT_DIR / "routing_prefix_summary.csv"
            ),
            "routing_prefix_region_coverage_csv": relpath(
                OUT_DIR / "routing_prefix_region_coverage.csv"
            ),
            "routing_prefix_observables_csv": relpath(
                OUT_DIR / "routing_prefix_observables.csv"
            ),
            "signature_boundary_spine_routing_prefix_tables": relpath(
                OUT_DIR / "signature_boundary_spine_routing_prefix_tables.npz"
            ),
            "signature_boundary_spine_routing_prefix_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_routing_prefix_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "minimal midpoint-polyline and edge-cloud residual-dominant prefix lengths",
                "the axis-tracking predecessor to the edge-cloud crossing prefix",
                "high/central/negative cell-region carrier coverage for both routing prefixes",
                "that the cumulative conductance crossing happens before any high-negative edge enters the prefix",
            ],
            "does_not_certify_because_not_required": [
                "that these prefixes are unique under alternative edge orderings",
                "a continuum route, geodesic-flow law, or mixing-time estimate",
                "higher-eigenmode routing prefixes",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Turn the prefix threshold into a branching law: certify which "
            "negative carrier masks enter before and after the prefix-8 "
            "residual flip, and compare that branch order with the original "
            "one-dimensional obstruction masks [4, 7, 8]."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_routing_prefix_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified Poincare-spine path and residual cell-complex artifacts",
            "scan ranked prefixes for residual-dominant edge-cloud and midpoint-polyline crossings",
            "verify the predecessor prefix remains axis-tracking",
            "compare crossing-prefix carriers with full and boundary-active cell-region bitsets",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_routing_prefix": routing_prefix,
        "routing_prefix_summary_csv": csv_text(
            ROUTING_PREFIX_SUMMARY_COLUMNS,
            summary_rows,
        ),
        "routing_prefix_region_coverage_csv": csv_text(
            ROUTING_PREFIX_REGION_COLUMNS,
            region_rows,
        ),
        "routing_prefix_observables_csv": csv_text(
            ROUTING_PREFIX_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "routing_prefix_summary_table": summary_table,
        "routing_prefix_region_table": region_table,
        "routing_prefix_observable_table": observable_table,
        "signature_boundary_spine_routing_prefix_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_routing_prefix.json",
        payloads["signature_boundary_spine_routing_prefix"],
    )
    (OUT_DIR / "routing_prefix_summary.csv").write_text(
        payloads["routing_prefix_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "routing_prefix_region_coverage.csv").write_text(
        payloads["routing_prefix_region_coverage_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "routing_prefix_observables.csv").write_text(
        payloads["routing_prefix_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_routing_prefix_tables.npz",
        routing_prefix_summary_table=payloads["routing_prefix_summary_table"],
        routing_prefix_region_table=payloads["routing_prefix_region_table"],
        routing_prefix_observable_table=payloads["routing_prefix_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_routing_prefix_certificate.json",
        payloads["signature_boundary_spine_routing_prefix_certificate"],
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
                "edge_cloud_crossing_prefix": witness[
                    "edge_cloud_crossing_prefix"
                ],
                "midpoint_polyline_crossing_prefix": witness[
                    "midpoint_polyline_crossing_prefix"
                ],
                "edge_prefix_region_coverage": witness[
                    "edge_prefix_region_coverage"
                ],
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
