from __future__ import annotations

import csv
import json
import math
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_geodesic_order import (
        OUT_DIR as GEODESIC_ORDER_DIR,
        disk_point,
        geodesic_frame,
        hyperboloid,
        minkowski_dot,
        scaled_float,
        scaled_ratio,
        table_from_rows,
        timelike_unit,
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
    from derive_c985_d20_signature_geodesic_order import (
        OUT_DIR as GEODESIC_ORDER_DIR,
        disk_point,
        geodesic_frame,
        hyperboloid,
        minkowski_dot,
        scaled_float,
        scaled_ratio,
        table_from_rows,
        timelike_unit,
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


THEOREM_ID = "c985_d20_signature_geodesic_residual_chart"
STATUS = "C985_D20_SIGNATURE_GEODESIC_RESIDUAL_CHART_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

GEODESIC_ORDER_REPORT = GEODESIC_ORDER_DIR / "report.json"
GEODESIC_ORDER_JSON = GEODESIC_ORDER_DIR / "signature_geodesic_order.json"
GEODESIC_ORDER_TABLES = GEODESIC_ORDER_DIR / "signature_geodesic_order_tables.npz"
GEODESIC_ORDER_CERTIFICATE = GEODESIC_ORDER_DIR / "signature_geodesic_order_certificate.json"
GEODESIC_ORDER_CARRIER_CSV = GEODESIC_ORDER_DIR / "carrier_geodesic_order.csv"
GEODESIC_ORDER_SIGNATURE_CSV = GEODESIC_ORDER_DIR / "signature_geodesic_order.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_geodesic_residual_chart.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_geodesic_residual_chart.py"

PROBABILITY_SCALE = 1_000_000_000_000

CARRIER_RESIDUAL_COLUMNS = [
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "nodal_sign",
    "signature_class_count",
    "stationary_mass_x1e12",
    "active_atom_count",
    "axis_coordinate_x1e12",
    "signed_residual_coordinate_x1e12",
    "abs_residual_coordinate_x1e12",
    "low_axis_margin_x1e12",
    "residual_gate_margin_x1e12",
    "high_axis_margin_x1e12",
    "elbow_region_code",
    "elbow_prediction",
    "elbow_matches_nodal",
    "carrier_center_x_x1e12",
    "carrier_center_y_x1e12",
    "projected_x_x1e12",
    "projected_y_x1e12",
    "axis_order_rank",
    "residual_order_rank",
    "carrier_atom_id_0",
    "carrier_atom_id_1",
    "carrier_atom_id_2",
    "carrier_atom_id_3",
]

SIGNATURE_RESIDUAL_COLUMNS = [
    "signature_vertex_id",
    "signature_class_id",
    "nodal_sign",
    "stationary_mass_x1e12",
    "second_eigenfunction_x1e12",
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "axis_coordinate_x1e12",
    "signed_residual_coordinate_x1e12",
    "low_axis_margin_x1e12",
    "residual_gate_margin_x1e12",
    "high_axis_margin_x1e12",
    "elbow_region_code",
    "elbow_prediction",
    "elbow_matches_nodal",
    "chart_order_rank",
]

RESIDUAL_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "low_axis_threshold": 0,
    "residual_gate_threshold": 1,
    "high_axis_threshold": 2,
    "one_dimensional_agreement_count": 3,
    "one_dimensional_agreement_mass": 4,
    "elbow_agreement_count": 5,
    "elbow_agreement_mass": 6,
    "elbow_misclassified_count": 7,
    "elbow_misclassified_mass": 8,
    "high_cap_mask_count": 9,
    "high_cap_signature_count": 10,
    "high_cap_stationary_mass": 11,
    "central_gate_mask_count": 12,
    "central_gate_signature_count": 13,
    "central_gate_stationary_mass": 14,
    "negative_region_mask_count": 15,
    "negative_region_signature_count": 16,
    "negative_region_stationary_mass": 17,
    "previous_obstruction_mask_count": 18,
    "previous_obstruction_signature_count": 19,
    "previous_obstruction_stationary_mass": 20,
    "distinct_chart_coordinate_count": 21,
    "carrier_coordinate_collision_count": 22,
    "perpendicular_direction_t_component": 23,
    "perpendicular_direction_x_component": 24,
    "perpendicular_direction_y_component": 25,
}


def read_int_csv(path: Any) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def lorentz_cross(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> tuple[float, float, float]:
    w0 = left[1] * right[2] - left[2] * right[1]
    w1 = left[2] * right[0] - left[0] * right[2]
    w2 = left[0] * right[1] - left[1] * right[0]
    return (-w0, w1, w2)


def signed_residual_coordinate(
    point: tuple[float, float],
    perpendicular_direction: tuple[float, float, float],
) -> float:
    return math.asinh(minkowski_dot(hyperboloid(point), perpendicular_direction))


def elbow_prediction(
    axis_coordinate: int,
    signed_residual: int,
    low_axis_threshold: int,
    residual_gate_threshold: int,
    high_axis_threshold: int,
) -> tuple[int, int]:
    if axis_coordinate > high_axis_threshold:
        return 1, 2
    if axis_coordinate > low_axis_threshold and signed_residual > residual_gate_threshold:
        return 1, 1
    return -1, -1


def midpoint_candidates(values: list[int]) -> list[int]:
    sorted_values = sorted(set(int(value) for value in values))
    candidates = [sorted_values[0] - 1]
    candidates.extend(
        (left + right) // 2 for left, right in zip(sorted_values, sorted_values[1:])
    )
    candidates.append(sorted_values[-1] + 1)
    return candidates


def build_payloads() -> dict[str, Any]:
    geodesic_report = load_json(GEODESIC_ORDER_REPORT)
    geodesic_order = load_json(GEODESIC_ORDER_JSON)
    geodesic_certificate = load_json(GEODESIC_ORDER_CERTIFICATE)
    geodesic_tables = np.load(GEODESIC_ORDER_TABLES, allow_pickle=False)
    source_carrier_rows = read_int_csv(GEODESIC_ORDER_CARRIER_CSV)
    source_signature_rows = read_int_csv(GEODESIC_ORDER_SIGNATURE_CSV)

    positive_center = (
        int(geodesic_order["axis"]["positive_center_x1e12"]["x"]) / PROBABILITY_SCALE,
        int(geodesic_order["axis"]["positive_center_x1e12"]["y"]) / PROBABILITY_SCALE,
    )
    negative_center = (
        int(geodesic_order["axis"]["negative_center_x1e12"]["x"]) / PROBABILITY_SCALE,
        int(geodesic_order["axis"]["negative_center_x1e12"]["y"]) / PROBABILITY_SCALE,
    )
    frame = geodesic_frame(positive_center, negative_center)
    perpendicular_direction = timelike_unit(
        lorentz_cross(frame["midpoint"], frame["direction_to_positive"])
    )

    carrier_signed: dict[int, int] = {}
    for row in source_carrier_rows:
        point = (
            int(row["carrier_center_x_x1e12"]) / PROBABILITY_SCALE,
            int(row["carrier_center_y_x1e12"]) / PROBABILITY_SCALE,
        )
        signed = scaled_float(signed_residual_coordinate(point, perpendicular_direction))
        carrier_signed[int(row["carrier_mask_class_id"])] = signed

    low_axis_threshold = int(geodesic_report["witness"]["best_threshold_x1e12"])
    previous_obstruction_mask_ids = [
        int(value) for value in geodesic_report["witness"]["obstruction_mask_class_ids"]
    ]
    residual_candidates = midpoint_candidates(list(carrier_signed.values()))
    high_axis_candidates = midpoint_candidates(
        [int(row["axis_coordinate_x1e12"]) for row in source_carrier_rows]
    )
    best_rule: dict[str, Any] | None = None
    for high_axis_threshold in high_axis_candidates:
        if high_axis_threshold <= low_axis_threshold:
            continue
        for residual_gate_threshold in residual_candidates:
            matching_rows = []
            for row in source_carrier_rows:
                prediction, _ = elbow_prediction(
                    int(row["axis_coordinate_x1e12"]),
                    carrier_signed[int(row["carrier_mask_class_id"])],
                    low_axis_threshold,
                    residual_gate_threshold,
                    high_axis_threshold,
                )
                if prediction == int(row["nodal_sign"]):
                    matching_rows.append(row)
            candidate = {
                "high_axis_threshold": int(high_axis_threshold),
                "residual_gate_threshold": int(residual_gate_threshold),
                "agreement_count": int(
                    sum(int(row["signature_class_count"]) for row in matching_rows)
                ),
                "agreement_mass_x1e12": int(
                    sum(int(row["stationary_mass_x1e12"]) for row in matching_rows)
                ),
            }
            if best_rule is None or (
                candidate["agreement_mass_x1e12"],
                candidate["agreement_count"],
                -abs(candidate["high_axis_threshold"]),
                -abs(candidate["residual_gate_threshold"]),
            ) > (
                best_rule["agreement_mass_x1e12"],
                best_rule["agreement_count"],
                -abs(best_rule["high_axis_threshold"]),
                -abs(best_rule["residual_gate_threshold"]),
            ):
                best_rule = candidate
    if best_rule is None:
        raise ValueError("no elbow rule candidates")
    high_axis_threshold = int(best_rule["high_axis_threshold"])
    residual_gate_threshold = int(best_rule["residual_gate_threshold"])

    residual_rank = {
        int(row["carrier_mask_class_id"]): rank
        for rank, row in enumerate(
            sorted(
                source_carrier_rows,
                key=lambda item: (
                    -carrier_signed[int(item["carrier_mask_class_id"])],
                    int(item["carrier_mask_class_id"]),
                ),
            ),
            start=1,
        )
    }

    carrier_rows: list[dict[str, int]] = []
    for row in source_carrier_rows:
        carrier_id = int(row["carrier_mask_class_id"])
        signed = carrier_signed[carrier_id]
        prediction, region_code = elbow_prediction(
            int(row["axis_coordinate_x1e12"]),
            signed,
            low_axis_threshold,
            residual_gate_threshold,
            high_axis_threshold,
        )
        carrier_rows.append(
            {
                "carrier_mask_class_id": carrier_id,
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
                "nodal_sign": int(row["nodal_sign"]),
                "signature_class_count": int(row["signature_class_count"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "active_atom_count": int(row["active_atom_count"]),
                "axis_coordinate_x1e12": int(row["axis_coordinate_x1e12"]),
                "signed_residual_coordinate_x1e12": signed,
                "abs_residual_coordinate_x1e12": abs(signed),
                "low_axis_margin_x1e12": int(row["axis_coordinate_x1e12"])
                - low_axis_threshold,
                "residual_gate_margin_x1e12": signed - residual_gate_threshold,
                "high_axis_margin_x1e12": int(row["axis_coordinate_x1e12"])
                - high_axis_threshold,
                "elbow_region_code": region_code,
                "elbow_prediction": prediction,
                "elbow_matches_nodal": int(prediction == int(row["nodal_sign"])),
                "carrier_center_x_x1e12": int(row["carrier_center_x_x1e12"]),
                "carrier_center_y_x1e12": int(row["carrier_center_y_x1e12"]),
                "projected_x_x1e12": int(row["projected_x_x1e12"]),
                "projected_y_x1e12": int(row["projected_y_x1e12"]),
                "axis_order_rank": int(row["axis_order_rank"]),
                "residual_order_rank": int(residual_rank[carrier_id]),
                "carrier_atom_id_0": int(row["carrier_atom_id_0"]),
                "carrier_atom_id_1": int(row["carrier_atom_id_1"]),
                "carrier_atom_id_2": int(row["carrier_atom_id_2"]),
                "carrier_atom_id_3": int(row["carrier_atom_id_3"]),
            }
        )

    carrier_by_id = {int(row["carrier_mask_class_id"]): row for row in carrier_rows}
    signature_chart_order = {
        int(row["signature_class_id"]): rank
        for rank, row in enumerate(
            sorted(
                source_signature_rows,
                key=lambda item: (
                    -int(item["axis_coordinate_x1e12"]),
                    -carrier_signed[int(item["carrier_mask_class_id"])],
                    int(item["signature_class_id"]),
                ),
            ),
            start=1,
        )
    }
    signature_rows: list[dict[str, int]] = []
    for row in source_signature_rows:
        carrier = carrier_by_id[int(row["carrier_mask_class_id"])]
        signature_rows.append(
            {
                "signature_vertex_id": int(row["signature_vertex_id"]),
                "signature_class_id": int(row["signature_class_id"]),
                "nodal_sign": int(row["nodal_sign"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "second_eigenfunction_x1e12": int(row["second_eigenfunction_x1e12"]),
                "carrier_mask_class_id": int(row["carrier_mask_class_id"]),
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
                "axis_coordinate_x1e12": int(row["axis_coordinate_x1e12"]),
                "signed_residual_coordinate_x1e12": int(
                    carrier["signed_residual_coordinate_x1e12"]
                ),
                "low_axis_margin_x1e12": int(carrier["low_axis_margin_x1e12"]),
                "residual_gate_margin_x1e12": int(
                    carrier["residual_gate_margin_x1e12"]
                ),
                "high_axis_margin_x1e12": int(carrier["high_axis_margin_x1e12"]),
                "elbow_region_code": int(carrier["elbow_region_code"]),
                "elbow_prediction": int(carrier["elbow_prediction"]),
                "elbow_matches_nodal": int(
                    int(carrier["elbow_prediction"]) == int(row["nodal_sign"])
                ),
                "chart_order_rank": int(signature_chart_order[int(row["signature_class_id"])]),
            }
        )

    high_cap_rows = [row for row in carrier_rows if int(row["elbow_region_code"]) == 2]
    central_gate_rows = [row for row in carrier_rows if int(row["elbow_region_code"]) == 1]
    negative_region_rows = [row for row in carrier_rows if int(row["elbow_region_code"]) == -1]
    previous_obstruction_rows = [
        row
        for row in carrier_rows
        if int(row["carrier_mask_class_id"]) in previous_obstruction_mask_ids
    ]
    elbow_matches = [row for row in signature_rows if int(row["elbow_matches_nodal"]) == 1]
    elbow_misses = [row for row in signature_rows if int(row["elbow_matches_nodal"]) == 0]
    coordinate_pairs = {
        (
            int(row["axis_coordinate_x1e12"]),
            int(row["signed_residual_coordinate_x1e12"]),
        )
        for row in carrier_rows
    }

    observable_values = {
        "low_axis_threshold": low_axis_threshold,
        "residual_gate_threshold": residual_gate_threshold,
        "high_axis_threshold": high_axis_threshold,
        "one_dimensional_agreement_count": int(
            geodesic_report["witness"]["best_threshold_agreement_count"]
        ),
        "one_dimensional_agreement_mass": int(
            geodesic_report["witness"]["best_threshold_agreement_mass_x1e12"]
        ),
        "elbow_agreement_count": int(len(elbow_matches)),
        "elbow_agreement_mass": int(
            sum(int(row["stationary_mass_x1e12"]) for row in elbow_matches)
        ),
        "elbow_misclassified_count": int(len(elbow_misses)),
        "elbow_misclassified_mass": int(
            sum(int(row["stationary_mass_x1e12"]) for row in elbow_misses)
        ),
        "high_cap_mask_count": len(high_cap_rows),
        "high_cap_signature_count": sum(
            int(row["signature_class_count"]) for row in high_cap_rows
        ),
        "high_cap_stationary_mass": sum(
            int(row["stationary_mass_x1e12"]) for row in high_cap_rows
        ),
        "central_gate_mask_count": len(central_gate_rows),
        "central_gate_signature_count": sum(
            int(row["signature_class_count"]) for row in central_gate_rows
        ),
        "central_gate_stationary_mass": sum(
            int(row["stationary_mass_x1e12"]) for row in central_gate_rows
        ),
        "negative_region_mask_count": len(negative_region_rows),
        "negative_region_signature_count": sum(
            int(row["signature_class_count"]) for row in negative_region_rows
        ),
        "negative_region_stationary_mass": sum(
            int(row["stationary_mass_x1e12"]) for row in negative_region_rows
        ),
        "previous_obstruction_mask_count": len(previous_obstruction_rows),
        "previous_obstruction_signature_count": sum(
            int(row["signature_class_count"]) for row in previous_obstruction_rows
        ),
        "previous_obstruction_stationary_mass": sum(
            int(row["stationary_mass_x1e12"]) for row in previous_obstruction_rows
        ),
        "distinct_chart_coordinate_count": len(coordinate_pairs),
        "carrier_coordinate_collision_count": len(carrier_rows) - len(coordinate_pairs),
        "perpendicular_direction_t_component": scaled_float(perpendicular_direction[0]),
        "perpendicular_direction_x_component": scaled_float(perpendicular_direction[1]),
        "perpendicular_direction_y_component": scaled_float(perpendicular_direction[2]),
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

    carrier_table = table_from_rows(CARRIER_RESIDUAL_COLUMNS, carrier_rows)
    signature_table = table_from_rows(SIGNATURE_RESIDUAL_COLUMNS, signature_rows)
    observable_table = table_from_rows(RESIDUAL_OBSERVABLE_COLUMNS, observable_rows)

    chart = {
        "schema": "c985.d20_signature_geodesic_residual_chart@1",
        "object": "d20",
        "chart_rule": {
            "source": "certified quotient-center geodesic order",
            "coordinates": [
                "signed axis coordinate along the positive-negative quotient-center geodesic",
                "signed perpendicular hyperbolic residual coordinate in the quotient-center geodesic frame",
            ],
            "elbow_classifier": (
                "positive iff axis > high_axis_threshold, or "
                "axis > low_axis_threshold and residual > residual_gate_threshold"
            ),
            "orientation": "positive residual is fixed by the Lorentz cross product of midpoint and positive-axis direction",
        },
        "thresholds_x1e12": {
            "low_axis": low_axis_threshold,
            "residual_gate": residual_gate_threshold,
            "high_axis": high_axis_threshold,
        },
        "perpendicular_direction_x1e12": {
            "t": observable_values["perpendicular_direction_t_component"],
            "x": observable_values["perpendicular_direction_x_component"],
            "y": observable_values["perpendicular_direction_y_component"],
        },
        "region_summary": {
            "high_axis_cap": {
                "mask_class_ids": [int(row["carrier_mask_class_id"]) for row in high_cap_rows],
                "signature_class_count": observable_values["high_cap_signature_count"],
                "stationary_mass_x1e12": observable_values["high_cap_stationary_mass"],
            },
            "central_residual_gate": {
                "mask_class_ids": [
                    int(row["carrier_mask_class_id"]) for row in central_gate_rows
                ],
                "signature_class_count": observable_values["central_gate_signature_count"],
                "stationary_mass_x1e12": observable_values["central_gate_stationary_mass"],
            },
            "negative_region": {
                "mask_class_ids": [
                    int(row["carrier_mask_class_id"]) for row in negative_region_rows
                ],
                "signature_class_count": observable_values["negative_region_signature_count"],
                "stationary_mass_x1e12": observable_values["negative_region_stationary_mass"],
            },
        },
        "carrier_residual_chart": [
            {key: int(value) for key, value in row.items()} for row in carrier_rows
        ],
        "signature_residual_chart": [
            {key: int(value) for key, value in row.items()} for row in signature_rows
        ],
    }

    high_cap_ids = [int(row["carrier_mask_class_id"]) for row in high_cap_rows]
    central_gate_ids = [int(row["carrier_mask_class_id"]) for row in central_gate_rows]
    negative_region_ids = [int(row["carrier_mask_class_id"]) for row in negative_region_rows]

    checks = {
        "geodesic_order_report_certified": geodesic_report.get("status")
        == "C985_D20_SIGNATURE_GEODESIC_ORDER_CERTIFIED",
        "geodesic_order_certificate_certified": geodesic_certificate.get("status")
        == "C985_D20_SIGNATURE_GEODESIC_ORDER_CERTIFIED",
        "carrier_count_is_14": len(carrier_rows) == 14,
        "signature_count_is_221": len(signature_rows) == 221,
        "low_axis_threshold_matches_geodesic_best": low_axis_threshold
        == -51543783679,
        "residual_gate_threshold_matches_expected": residual_gate_threshold
        == -149928684557,
        "high_axis_threshold_matches_expected": high_axis_threshold == 178625198443,
        "elbow_threshold_search_is_perfect": (
            int(best_rule["agreement_count"]),
            int(best_rule["agreement_mass_x1e12"]),
        )
        == (221, PROBABILITY_SCALE),
        "elbow_classifier_separates_all_carriers": all(
            int(row["elbow_matches_nodal"]) == 1 for row in carrier_rows
        ),
        "elbow_classifier_separates_all_signatures": (
            observable_values["elbow_agreement_count"],
            observable_values["elbow_agreement_mass"],
            observable_values["elbow_misclassified_count"],
            observable_values["elbow_misclassified_mass"],
        )
        == (221, PROBABILITY_SCALE, 0, 0),
        "previous_obstruction_resolved_by_residual_gate": (
            previous_obstruction_mask_ids,
            [
                int(row["carrier_mask_class_id"])
                for row in previous_obstruction_rows
                if int(row["elbow_region_code"]) == -1
            ],
        )
        == ([4, 7, 8], [4, 7, 8]),
        "region_ids_match_expected": (
            high_cap_ids,
            central_gate_ids,
            negative_region_ids,
        )
        == ([0, 1], [2, 3, 10, 11, 12], [4, 5, 6, 7, 8, 9, 13]),
        "region_masses_match_expected": (
            observable_values["high_cap_signature_count"],
            observable_values["high_cap_stationary_mass"],
            observable_values["central_gate_signature_count"],
            observable_values["central_gate_stationary_mass"],
            observable_values["negative_region_signature_count"],
            observable_values["negative_region_stationary_mass"],
        )
        == (24, 10418982028, 97, 615688126181, 100, 373892891791),
        "previous_obstruction_mass_matches_expected": (
            observable_values["previous_obstruction_signature_count"],
            observable_values["previous_obstruction_stationary_mass"],
        )
        == (29, 147871346728),
        "signed_residuals_match_axis_residual_magnitudes": all(
            abs(int(row["signed_residual_coordinate_x1e12"]))
            == int(row["abs_residual_coordinate_x1e12"])
            for row in carrier_rows
        ),
        "carrier_coordinates_are_distinct": (
            observable_values["distinct_chart_coordinate_count"],
            observable_values["carrier_coordinate_collision_count"],
        )
        == (14, 0),
        "perpendicular_direction_matches_expected": (
            observable_values["perpendicular_direction_t_component"],
            observable_values["perpendicular_direction_x_component"],
            observable_values["perpendicular_direction_y_component"],
        )
        == (-61701506611, 111067537516, 995726407216),
        "carrier_table_shape_is_14_by_25": tuple(carrier_table.shape)
        == (14, len(CARRIER_RESIDUAL_COLUMNS)),
        "signature_table_shape_is_221_by_16": tuple(signature_table.shape)
        == (221, len(SIGNATURE_RESIDUAL_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(RESIDUAL_OBSERVABLE_COLUMNS)),
        "geodesic_order_tables_available": "carrier_geodesic_table"
        in geodesic_tables.files,
        "geodesic_order_json_schema_available": geodesic_order.get("schema")
        == "c985.d20_signature_geodesic_order@1",
    }

    witness = {
        "low_axis_threshold_x1e12": low_axis_threshold,
        "residual_gate_threshold_x1e12": residual_gate_threshold,
        "high_axis_threshold_x1e12": high_axis_threshold,
        "one_dimensional_agreement_count": observable_values[
            "one_dimensional_agreement_count"
        ],
        "one_dimensional_agreement_mass_x1e12": observable_values[
            "one_dimensional_agreement_mass"
        ],
        "elbow_agreement_count": observable_values["elbow_agreement_count"],
        "elbow_agreement_mass_x1e12": observable_values["elbow_agreement_mass"],
        "elbow_misclassified_count": observable_values["elbow_misclassified_count"],
        "elbow_misclassified_mass_x1e12": observable_values[
            "elbow_misclassified_mass"
        ],
        "high_cap_mask_class_ids": high_cap_ids,
        "central_gate_mask_class_ids": central_gate_ids,
        "negative_region_mask_class_ids": negative_region_ids,
        "previous_obstruction_mask_class_ids": previous_obstruction_mask_ids,
        "previous_obstruction_signature_count": observable_values[
            "previous_obstruction_signature_count"
        ],
        "previous_obstruction_stationary_mass_x1e12": observable_values[
            "previous_obstruction_stationary_mass"
        ],
        "distinct_chart_coordinate_count": observable_values[
            "distinct_chart_coordinate_count"
        ],
        "carrier_coordinate_collision_count": observable_values[
            "carrier_coordinate_collision_count"
        ],
        "perpendicular_direction_x1e12": chart["perpendicular_direction_x1e12"],
        "carrier_residual_chart_table_sha256": sha_array(carrier_table),
        "signature_residual_chart_table_sha256": sha_array(signature_table),
        "residual_chart_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_geodesic_residual_chart_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_GEODESIC_RESIDUAL_CHART_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the perpendicular residual coordinate resolves the three negative obstruction carrier masks from the one-dimensional geodesic order",
            "a two-coordinate elbow rule separates all 221 recurrent signature classes by spectral nodal sign",
            "the high-axis cap recovers positive carrier masks 0 and 1 while the central residual gate recovers masks 2, 3, 10, 11, and 12",
            "the negative region is exactly carrier-mask classes 4, 5, 6, 7, 8, 9, and 13",
            "all 14 carrier masks retain distinct chart coordinates, so this separation does not collapse the carrier structure",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_geodesic_residual_chart@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Adding the signed perpendicular residual coordinate to the certified "
            "quotient-center geodesic gives a two-coordinate hyperbolic chart "
            "whose elbow rule separates the spectral nodal split exactly while "
            "preserving all 14 active carrier-mask coordinates."
        ),
        "stage_protocol": {
            "draft": "construct the perpendicular Lorentz-frame coordinate to the quotient-center geodesic",
            "witness": "materialize carrier-mask and signature-class two-coordinate chart records",
            "coherence": "search residual/high-axis thresholds and prove exact elbow separation with no carrier-coordinate collisions",
            "closure": "certify two-coordinate separation without claiming a linear separator or continuum boundary",
            "emit": "emit residual-chart JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "geodesic_order_report": input_entry(
                GEODESIC_ORDER_REPORT,
                {
                    "status": geodesic_report.get("status"),
                    "certificate_sha256": geodesic_report.get("certificate_sha256"),
                },
            ),
            "geodesic_order": input_entry(GEODESIC_ORDER_JSON),
            "geodesic_order_tables": input_entry(GEODESIC_ORDER_TABLES),
            "geodesic_order_certificate": input_entry(GEODESIC_ORDER_CERTIFICATE),
            "geodesic_order_carrier_csv": input_entry(GEODESIC_ORDER_CARRIER_CSV),
            "geodesic_order_signature_csv": input_entry(GEODESIC_ORDER_SIGNATURE_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_geodesic_residual_chart": relpath(
                OUT_DIR / "signature_geodesic_residual_chart.json"
            ),
            "carrier_residual_chart_csv": relpath(OUT_DIR / "carrier_residual_chart.csv"),
            "signature_residual_chart_csv": relpath(
                OUT_DIR / "signature_residual_chart.csv"
            ),
            "residual_chart_observables_csv": relpath(
                OUT_DIR / "residual_chart_observables.csv"
            ),
            "signature_geodesic_residual_chart_tables": relpath(
                OUT_DIR / "signature_geodesic_residual_chart_tables.npz"
            ),
            "signature_geodesic_residual_chart_certificate": relpath(
                OUT_DIR / "signature_geodesic_residual_chart_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "signed perpendicular residual coordinates for the carrier-mask and signature geodesic chart",
                "the unique fixed-low-axis elbow rule with perfect nodal-sign agreement",
                "exact resolution of the one-dimensional obstruction masks 4, 7, and 8",
                "distinct two-coordinate chart positions for all 14 carrier masks",
            ],
            "does_not_certify_because_not_required": [
                "a linear separator in the two-coordinate chart",
                "uniqueness among all possible nonlinear finite classifiers",
                "Karcher/Frechet barycenter coordinates",
                "continuum boundary dynamics or asymptotic mixing theory",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Promote the exact two-coordinate chart into a finite cell complex: "
            "certify the adjacency of the high-cap, central-gate, and negative "
            "regions, then compare its boundary cells with the 16 carrier-mask "
            "crossing edges from the spectral cut."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_geodesic_residual_chart_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified signature geodesic-order artifacts",
            "construct the perpendicular Lorentz-frame residual coordinate",
            "search high-axis and residual-gate thresholds with fixed one-dimensional low-axis threshold",
            "prove exact elbow-rule separation of all recurrent signature classes",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_geodesic_residual_chart": chart,
        "carrier_residual_chart_csv": csv_text(CARRIER_RESIDUAL_COLUMNS, carrier_rows),
        "signature_residual_chart_csv": csv_text(
            SIGNATURE_RESIDUAL_COLUMNS,
            signature_rows,
        ),
        "residual_chart_observables_csv": csv_text(
            RESIDUAL_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "carrier_residual_chart_table": carrier_table,
        "signature_residual_chart_table": signature_table,
        "residual_chart_observable_table": observable_table,
        "signature_geodesic_residual_chart_certificate": certificate,
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
        OUT_DIR / "signature_geodesic_residual_chart.json",
        payloads["signature_geodesic_residual_chart"],
    )
    (OUT_DIR / "carrier_residual_chart.csv").write_text(
        payloads["carrier_residual_chart_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_residual_chart.csv").write_text(
        payloads["signature_residual_chart_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "residual_chart_observables.csv").write_text(
        payloads["residual_chart_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_geodesic_residual_chart_tables.npz",
        carrier_residual_chart_table=payloads["carrier_residual_chart_table"],
        signature_residual_chart_table=payloads["signature_residual_chart_table"],
        residual_chart_observable_table=payloads["residual_chart_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_geodesic_residual_chart_certificate.json",
        payloads["signature_geodesic_residual_chart_certificate"],
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
                "low_axis_threshold_x1e12": witness["low_axis_threshold_x1e12"],
                "residual_gate_threshold_x1e12": witness[
                    "residual_gate_threshold_x1e12"
                ],
                "high_axis_threshold_x1e12": witness["high_axis_threshold_x1e12"],
                "elbow_agreement_count": witness["elbow_agreement_count"],
                "elbow_agreement_mass_x1e12": witness[
                    "elbow_agreement_mass_x1e12"
                ],
                "previous_obstruction_mask_class_ids": witness[
                    "previous_obstruction_mask_class_ids"
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
