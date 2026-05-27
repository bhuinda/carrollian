from __future__ import annotations

import csv
import json
import math
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
    )
    from .derive_c985_d20_signature_quotient_poincare_geometry import (
        OUT_DIR as QUOTIENT_GEOMETRY_DIR,
    )
    from .derive_c985_d20_signature_transfer_spectral_cut import (
        OUT_DIR as SPECTRAL_CUT_DIR,
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
    from derive_c985_d20_recurrent_signature_subboundary import (
        OUT_DIR as SIGNATURE_SUBBOUNDARY_DIR,
    )
    from derive_c985_d20_signature_quotient_poincare_geometry import (
        OUT_DIR as QUOTIENT_GEOMETRY_DIR,
    )
    from derive_c985_d20_signature_transfer_spectral_cut import (
        OUT_DIR as SPECTRAL_CUT_DIR,
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


THEOREM_ID = "c985_d20_signature_geodesic_order"
STATUS = "C985_D20_SIGNATURE_GEODESIC_ORDER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

QUOTIENT_GEOMETRY_REPORT = QUOTIENT_GEOMETRY_DIR / "report.json"
QUOTIENT_GEOMETRY_JSON = (
    QUOTIENT_GEOMETRY_DIR / "signature_quotient_poincare_geometry.json"
)
QUOTIENT_GEOMETRY_TABLES = (
    QUOTIENT_GEOMETRY_DIR / "signature_quotient_poincare_geometry_tables.npz"
)
QUOTIENT_GEOMETRY_CERTIFICATE = (
    QUOTIENT_GEOMETRY_DIR / "signature_quotient_poincare_geometry_certificate.json"
)

SPECTRAL_CUT_REPORT = SPECTRAL_CUT_DIR / "report.json"
SPECTRAL_CUT_JSON = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut.json"
SPECTRAL_CUT_TABLES = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_tables.npz"
SPECTRAL_CUT_CERTIFICATE = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_certificate.json"
SPECTRAL_SIGNATURE_VERTICES = SPECTRAL_CUT_DIR / "signature_eigenmode_vertices.csv"
SPECTRAL_MASK_SUMMARY = SPECTRAL_CUT_DIR / "carrier_mask_eigenmode_summary.csv"

SIGNATURE_SUBBOUNDARY_REPORT = SIGNATURE_SUBBOUNDARY_DIR / "report.json"
SIGNATURE_SUBBOUNDARY_JSON = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary.json"
)
SIGNATURE_SUBBOUNDARY_TABLES = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_tables.npz"
)
SIGNATURE_SUBBOUNDARY_CERTIFICATE = (
    SIGNATURE_SUBBOUNDARY_DIR / "recurrent_signature_subboundary_certificate.json"
)
SIGNATURE_SUBBOUNDARY_VERTICES = (
    SIGNATURE_SUBBOUNDARY_DIR / "signature_subboundary_vertices.csv"
)

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_geodesic_order.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_geodesic_order.py"

PROBABILITY_SCALE = 1_000_000_000_000

CARRIER_GEODESIC_COLUMNS = [
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "nodal_sign",
    "signature_class_count",
    "stationary_mass_x1e12",
    "active_atom_count",
    "carrier_center_x_x1e12",
    "carrier_center_y_x1e12",
    "carrier_center_radius_x1e12",
    "axis_coordinate_x1e12",
    "coordinate_minus_best_threshold_x1e12",
    "projected_x_x1e12",
    "projected_y_x1e12",
    "projection_residual_x1e12",
    "zero_threshold_prediction",
    "best_threshold_prediction",
    "zero_threshold_matches_nodal",
    "best_threshold_matches_nodal",
    "axis_order_rank",
    "carrier_atom_id_0",
    "carrier_atom_id_1",
    "carrier_atom_id_2",
    "carrier_atom_id_3",
]

SIGNATURE_GEODESIC_COLUMNS = [
    "signature_vertex_id",
    "signature_class_id",
    "nodal_sign",
    "stationary_mass_x1e12",
    "second_eigenfunction_x1e12",
    "carrier_mask_class_id",
    "carrier_atom_mask",
    "axis_coordinate_x1e12",
    "coordinate_minus_best_threshold_x1e12",
    "projection_residual_x1e12",
    "zero_threshold_prediction",
    "best_threshold_prediction",
    "zero_threshold_matches_nodal",
    "best_threshold_matches_nodal",
    "axis_order_rank",
]

GEODESIC_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "axis_hyperbolic_length": 0,
    "axis_half_length": 1,
    "axis_midpoint_x": 2,
    "axis_midpoint_y": 3,
    "axis_midpoint_radius": 4,
    "positive_endpoint_axis_coordinate": 5,
    "negative_endpoint_axis_coordinate": 6,
    "best_threshold": 7,
    "candidate_threshold_count": 8,
    "zero_threshold_agreement_count": 9,
    "zero_threshold_agreement_mass": 10,
    "zero_threshold_agreement_fraction": 11,
    "best_threshold_agreement_count": 12,
    "best_threshold_agreement_mass": 13,
    "best_threshold_agreement_fraction": 14,
    "best_threshold_misclassified_count": 15,
    "best_threshold_misclassified_mass": 16,
    "positive_mean_axis_coordinate": 17,
    "negative_mean_axis_coordinate": 18,
    "weighted_axis_mode_correlation": 19,
    "sign_pair_inversion_count_fraction": 20,
    "sign_pair_inversion_mass_fraction": 21,
    "stationary_mean_projection_residual": 22,
    "max_projection_residual": 23,
    "min_projection_residual": 24,
    "obstruction_mask_class_count": 25,
}


def scaled_float(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


def scaled_ratio(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("non-positive denominator")
    scaled = int(numerator) * PROBABILITY_SCALE
    quotient, remainder = divmod(scaled, int(denominator))
    if 2 * remainder >= int(denominator):
        quotient += 1
    return int(quotient)


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def hyperboloid(point: tuple[float, float]) -> tuple[float, float, float]:
    x, y = point
    radius_sq = x * x + y * y
    denominator = 1.0 - radius_sq
    return (
        (1.0 + radius_sq) / denominator,
        2.0 * x / denominator,
        2.0 * y / denominator,
    )


def disk_point(hyperbolic_point: tuple[float, float, float]) -> tuple[float, float]:
    return (
        hyperbolic_point[1] / (hyperbolic_point[0] + 1.0),
        hyperbolic_point[2] / (hyperbolic_point[0] + 1.0),
    )


def minkowski_dot(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> float:
    return -left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def timelike_unit(
    vector: tuple[float, float, float],
) -> tuple[float, float, float]:
    norm_sq = minkowski_dot(vector, vector)
    return tuple(value / math.sqrt(abs(norm_sq)) for value in vector)  # type: ignore[return-value]


def hyperbolic_distance_from_models(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> float:
    return math.acosh(max(1.0, -minkowski_dot(left, right)))


def geodesic_frame(
    positive_center: tuple[float, float],
    negative_center: tuple[float, float],
) -> dict[str, Any]:
    positive = hyperboloid(positive_center)
    negative = hyperboloid(negative_center)
    axis_length = hyperbolic_distance_from_models(positive, negative)
    midpoint = timelike_unit(tuple(positive[index] + negative[index] for index in range(3)))
    direction_to_positive = tuple(
        (positive[index] - math.cosh(axis_length / 2.0) * midpoint[index])
        / math.sinh(axis_length / 2.0)
        for index in range(3)
    )
    return {
        "positive": positive,
        "negative": negative,
        "midpoint": midpoint,
        "direction_to_positive": direction_to_positive,
        "axis_length": axis_length,
        "midpoint_disk": disk_point(midpoint),
    }


def project_to_axis(
    point: tuple[float, float],
    frame: dict[str, Any],
) -> dict[str, Any]:
    model = hyperboloid(point)
    midpoint = frame["midpoint"]
    direction = frame["direction_to_positive"]
    ratio = minkowski_dot(model, direction) / (-minkowski_dot(model, midpoint))
    ratio = max(-0.999999999999, min(0.999999999999, ratio))
    coordinate = math.atanh(ratio)
    projected_model = tuple(
        math.cosh(coordinate) * midpoint[index]
        + math.sinh(coordinate) * direction[index]
        for index in range(3)
    )
    projected_point = disk_point(projected_model)
    residual = hyperbolic_distance_from_models(model, projected_model)
    return {
        "axis_coordinate": coordinate,
        "projected_point": projected_point,
        "projection_residual": residual,
    }


def read_int_csv(path: Any) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def active_atom_ids(row: dict[str, int]) -> list[int]:
    return [
        int(row[f"carrier_atom_id_{index}"])
        for index in range(4)
        if int(row[f"carrier_atom_id_{index}"]) >= 0
    ]


def prediction(axis_coordinate: float, threshold: float) -> int:
    return 1 if axis_coordinate > threshold else -1


def weighted_correlation(
    rows: list[dict[str, Any]],
    left_key: str,
    right_key: str,
    weight_key: str,
) -> float:
    total = sum(int(row[weight_key]) for row in rows)
    left_mean = sum(float(row[left_key]) * int(row[weight_key]) for row in rows) / total
    right_mean = sum(float(row[right_key]) * int(row[weight_key]) for row in rows) / total
    covariance = (
        sum(
            int(row[weight_key])
            * (float(row[left_key]) - left_mean)
            * (float(row[right_key]) - right_mean)
            for row in rows
        )
        / total
    )
    left_variance = (
        sum(
            int(row[weight_key]) * (float(row[left_key]) - left_mean) ** 2
            for row in rows
        )
        / total
    )
    right_variance = (
        sum(
            int(row[weight_key]) * (float(row[right_key]) - right_mean) ** 2
            for row in rows
        )
        / total
    )
    return covariance / math.sqrt(left_variance * right_variance)


def build_payloads() -> dict[str, Any]:
    geometry_report = load_json(QUOTIENT_GEOMETRY_REPORT)
    geometry = load_json(QUOTIENT_GEOMETRY_JSON)
    geometry_certificate = load_json(QUOTIENT_GEOMETRY_CERTIFICATE)
    spectral_report = load_json(SPECTRAL_CUT_REPORT)
    spectral_cut = load_json(SPECTRAL_CUT_JSON)
    spectral_certificate = load_json(SPECTRAL_CUT_CERTIFICATE)
    subboundary_report = load_json(SIGNATURE_SUBBOUNDARY_REPORT)
    subboundary = load_json(SIGNATURE_SUBBOUNDARY_JSON)
    subboundary_certificate = load_json(SIGNATURE_SUBBOUNDARY_CERTIFICATE)
    geometry_tables = np.load(QUOTIENT_GEOMETRY_TABLES, allow_pickle=False)
    spectral_tables = np.load(SPECTRAL_CUT_TABLES, allow_pickle=False)
    subboundary_tables = np.load(SIGNATURE_SUBBOUNDARY_TABLES, allow_pickle=False)

    states = {
        str(row["label"]): row
        for row in geometry["state_geometry"]
    }
    positive_center = (
        int(states["positive"]["center_x_x1e12"]) / PROBABILITY_SCALE,
        int(states["positive"]["center_y_x1e12"]) / PROBABILITY_SCALE,
    )
    negative_center = (
        int(states["negative"]["center_x_x1e12"]) / PROBABILITY_SCALE,
        int(states["negative"]["center_y_x1e12"]) / PROBABILITY_SCALE,
    )
    atom_coordinates = {
        int(row["atom_id"]): (
            int(row["poincare_x_x1e12"]) / PROBABILITY_SCALE,
            int(row["poincare_y_x1e12"]) / PROBABILITY_SCALE,
        )
        for row in geometry["atom_geometry"]
    }

    frame = geodesic_frame(positive_center, negative_center)
    mask_source_rows = read_int_csv(SPECTRAL_MASK_SUMMARY)
    vertex_source_rows = read_int_csv(SPECTRAL_SIGNATURE_VERTICES)
    subboundary_vertex_rows = read_int_csv(SIGNATURE_SUBBOUNDARY_VERTICES)

    mask_projection_rows: list[dict[str, Any]] = []
    for row in mask_source_rows:
        atoms = active_atom_ids(row)
        center = (
            sum(atom_coordinates[atom_id][0] for atom_id in atoms) / len(atoms),
            sum(atom_coordinates[atom_id][1] for atom_id in atoms) / len(atoms),
        )
        projection = project_to_axis(center, frame)
        mask_projection_rows.append(
            {
                **row,
                "carrier_atom_ids": atoms,
                "carrier_center": center,
                "axis_coordinate": float(projection["axis_coordinate"]),
                "projected_point": projection["projected_point"],
                "projection_residual": float(projection["projection_residual"]),
            }
        )

    unique_coordinates = sorted(
        {float(row["axis_coordinate"]) for row in mask_projection_rows}
    )
    threshold_candidates = [unique_coordinates[0] - 0.000001]
    threshold_candidates.extend(
        (left + right) / 2.0
        for left, right in zip(unique_coordinates, unique_coordinates[1:])
    )
    threshold_candidates.append(unique_coordinates[-1] + 0.000001)

    mask_by_class = {
        int(row["carrier_mask_class_id"]): row for row in mask_projection_rows
    }
    vertex_projection_rows: list[dict[str, Any]] = []
    for row in vertex_source_rows:
        mask_row = mask_by_class[int(row["carrier_mask_class_id"])]
        vertex_projection_rows.append(
            {
                **row,
                "axis_coordinate": float(mask_row["axis_coordinate"]),
                "projection_residual": float(mask_row["projection_residual"]),
                "eigenfunction": int(row["second_eigenfunction_x1e12"])
                / PROBABILITY_SCALE,
            }
        )

    threshold_records: list[dict[str, Any]] = []
    for threshold in threshold_candidates:
        matches = [
            row
            for row in vertex_projection_rows
            if prediction(float(row["axis_coordinate"]), threshold)
            == int(row["nodal_sign"])
        ]
        threshold_records.append(
            {
                "threshold": threshold,
                "agreement_count": len(matches),
                "agreement_mass_x1e12": int(
                    sum(int(row["stationary_mass_x1e12"]) for row in matches)
                ),
            }
        )
    best_threshold = max(
        threshold_records,
        key=lambda row: (
            int(row["agreement_mass_x1e12"]),
            int(row["agreement_count"]),
            -abs(float(row["threshold"])),
            float(row["threshold"]),
        ),
    )
    threshold = float(best_threshold["threshold"])

    for row in mask_projection_rows:
        zero_prediction = prediction(float(row["axis_coordinate"]), 0.0)
        best_prediction = prediction(float(row["axis_coordinate"]), threshold)
        row["zero_threshold_prediction"] = zero_prediction
        row["best_threshold_prediction"] = best_prediction
        row["zero_threshold_matches_nodal"] = int(
            zero_prediction == int(row["nodal_sign"])
        )
        row["best_threshold_matches_nodal"] = int(
            best_prediction == int(row["nodal_sign"])
        )

    mask_order = {
        int(row["carrier_mask_class_id"]): rank
        for rank, row in enumerate(
            sorted(
                mask_projection_rows,
                key=lambda item: (
                    -float(item["axis_coordinate"]),
                    int(item["carrier_mask_class_id"]),
                ),
            ),
            start=1,
        )
    }

    carrier_rows: list[dict[str, int]] = []
    for row in sorted(mask_projection_rows, key=lambda item: int(item["carrier_mask_class_id"])):
        atoms = list(row["carrier_atom_ids"])
        projected_x, projected_y = row["projected_point"]
        carrier_rows.append(
            {
                "carrier_mask_class_id": int(row["carrier_mask_class_id"]),
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
                "nodal_sign": int(row["nodal_sign"]),
                "signature_class_count": int(row["signature_class_count"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "active_atom_count": len(atoms),
                "carrier_center_x_x1e12": scaled_float(row["carrier_center"][0]),
                "carrier_center_y_x1e12": scaled_float(row["carrier_center"][1]),
                "carrier_center_radius_x1e12": scaled_float(
                    math.hypot(*row["carrier_center"])
                ),
                "axis_coordinate_x1e12": scaled_float(row["axis_coordinate"]),
                "coordinate_minus_best_threshold_x1e12": scaled_float(
                    row["axis_coordinate"] - threshold
                ),
                "projected_x_x1e12": scaled_float(projected_x),
                "projected_y_x1e12": scaled_float(projected_y),
                "projection_residual_x1e12": scaled_float(row["projection_residual"]),
                "zero_threshold_prediction": int(row["zero_threshold_prediction"]),
                "best_threshold_prediction": int(row["best_threshold_prediction"]),
                "zero_threshold_matches_nodal": int(row["zero_threshold_matches_nodal"]),
                "best_threshold_matches_nodal": int(row["best_threshold_matches_nodal"]),
                "axis_order_rank": int(mask_order[int(row["carrier_mask_class_id"])]),
                "carrier_atom_id_0": atoms[0] if len(atoms) > 0 else -1,
                "carrier_atom_id_1": atoms[1] if len(atoms) > 1 else -1,
                "carrier_atom_id_2": atoms[2] if len(atoms) > 2 else -1,
                "carrier_atom_id_3": atoms[3] if len(atoms) > 3 else -1,
            }
        )

    signature_order = {
        int(row["signature_class_id"]): rank
        for rank, row in enumerate(
            sorted(
                vertex_projection_rows,
                key=lambda item: (
                    -float(item["axis_coordinate"]),
                    int(item["signature_class_id"]),
                ),
            ),
            start=1,
        )
    }
    signature_rows: list[dict[str, int]] = []
    for row in vertex_projection_rows:
        zero_prediction = prediction(float(row["axis_coordinate"]), 0.0)
        best_prediction = prediction(float(row["axis_coordinate"]), threshold)
        signature_rows.append(
            {
                "signature_vertex_id": int(row["signature_vertex_id"]),
                "signature_class_id": int(row["signature_class_id"]),
                "nodal_sign": int(row["nodal_sign"]),
                "stationary_mass_x1e12": int(row["stationary_mass_x1e12"]),
                "second_eigenfunction_x1e12": int(row["second_eigenfunction_x1e12"]),
                "carrier_mask_class_id": int(row["carrier_mask_class_id"]),
                "carrier_atom_mask": int(row["carrier_atom_mask"]),
                "axis_coordinate_x1e12": scaled_float(row["axis_coordinate"]),
                "coordinate_minus_best_threshold_x1e12": scaled_float(
                    float(row["axis_coordinate"]) - threshold
                ),
                "projection_residual_x1e12": scaled_float(row["projection_residual"]),
                "zero_threshold_prediction": zero_prediction,
                "best_threshold_prediction": best_prediction,
                "zero_threshold_matches_nodal": int(
                    zero_prediction == int(row["nodal_sign"])
                ),
                "best_threshold_matches_nodal": int(
                    best_prediction == int(row["nodal_sign"])
                ),
                "axis_order_rank": int(signature_order[int(row["signature_class_id"])]),
            }
        )

    positive_vertices = [row for row in vertex_projection_rows if int(row["nodal_sign"]) == 1]
    negative_vertices = [row for row in vertex_projection_rows if int(row["nodal_sign"]) == -1]
    zero_matches = [
        row
        for row in vertex_projection_rows
        if prediction(float(row["axis_coordinate"]), 0.0) == int(row["nodal_sign"])
    ]
    best_matches = [
        row
        for row in vertex_projection_rows
        if prediction(float(row["axis_coordinate"]), threshold) == int(row["nodal_sign"])
    ]
    best_misses = [
        row
        for row in vertex_projection_rows
        if prediction(float(row["axis_coordinate"]), threshold) != int(row["nodal_sign"])
    ]
    obstruction_mask_ids = sorted(
        {int(row["carrier_mask_class_id"]) for row in best_misses}
    )
    positive_mass = sum(int(row["stationary_mass_x1e12"]) for row in positive_vertices)
    negative_mass = sum(int(row["stationary_mass_x1e12"]) for row in negative_vertices)
    positive_mean_axis = (
        sum(int(row["stationary_mass_x1e12"]) * float(row["axis_coordinate"]) for row in positive_vertices)
        / positive_mass
    )
    negative_mean_axis = (
        sum(int(row["stationary_mass_x1e12"]) * float(row["axis_coordinate"]) for row in negative_vertices)
        / negative_mass
    )
    weighted_axis_mode_correlation = weighted_correlation(
        vertex_projection_rows,
        "axis_coordinate",
        "eigenfunction",
        "stationary_mass_x1e12",
    )

    total_pair_count = len(positive_vertices) * len(negative_vertices)
    inversion_pair_count = sum(
        1
        for positive in positive_vertices
        for negative in negative_vertices
        if float(positive["axis_coordinate"]) <= float(negative["axis_coordinate"])
    )
    total_pair_mass = sum(
        int(positive["stationary_mass_x1e12"]) * int(negative["stationary_mass_x1e12"])
        for positive in positive_vertices
        for negative in negative_vertices
    )
    inversion_pair_mass = sum(
        int(positive["stationary_mass_x1e12"]) * int(negative["stationary_mass_x1e12"])
        for positive in positive_vertices
        for negative in negative_vertices
        if float(positive["axis_coordinate"]) <= float(negative["axis_coordinate"])
    )

    stationary_mean_residual = (
        sum(
            int(row["stationary_mass_x1e12"]) * float(row["projection_residual"])
            for row in vertex_projection_rows
        )
        / PROBABILITY_SCALE
    )
    residuals = [float(row["projection_residual"]) for row in mask_projection_rows]
    midpoint_x, midpoint_y = frame["midpoint_disk"]

    observable_values = {
        "axis_hyperbolic_length": scaled_float(frame["axis_length"]),
        "axis_half_length": scaled_float(frame["axis_length"] / 2.0),
        "axis_midpoint_x": scaled_float(midpoint_x),
        "axis_midpoint_y": scaled_float(midpoint_y),
        "axis_midpoint_radius": scaled_float(math.hypot(midpoint_x, midpoint_y)),
        "positive_endpoint_axis_coordinate": scaled_float(frame["axis_length"] / 2.0),
        "negative_endpoint_axis_coordinate": -scaled_float(frame["axis_length"] / 2.0),
        "best_threshold": scaled_float(threshold),
        "candidate_threshold_count": len(threshold_candidates),
        "zero_threshold_agreement_count": len(zero_matches),
        "zero_threshold_agreement_mass": int(
            sum(int(row["stationary_mass_x1e12"]) for row in zero_matches)
        ),
        "zero_threshold_agreement_fraction": scaled_ratio(len(zero_matches), len(vertex_projection_rows)),
        "best_threshold_agreement_count": len(best_matches),
        "best_threshold_agreement_mass": int(
            sum(int(row["stationary_mass_x1e12"]) for row in best_matches)
        ),
        "best_threshold_agreement_fraction": scaled_ratio(len(best_matches), len(vertex_projection_rows)),
        "best_threshold_misclassified_count": len(best_misses),
        "best_threshold_misclassified_mass": int(
            sum(int(row["stationary_mass_x1e12"]) for row in best_misses)
        ),
        "positive_mean_axis_coordinate": scaled_float(positive_mean_axis),
        "negative_mean_axis_coordinate": scaled_float(negative_mean_axis),
        "weighted_axis_mode_correlation": scaled_float(weighted_axis_mode_correlation),
        "sign_pair_inversion_count_fraction": scaled_ratio(inversion_pair_count, total_pair_count),
        "sign_pair_inversion_mass_fraction": scaled_ratio(inversion_pair_mass, total_pair_mass),
        "stationary_mean_projection_residual": scaled_float(stationary_mean_residual),
        "max_projection_residual": scaled_float(max(residuals)),
        "min_projection_residual": scaled_float(min(residuals)),
        "obstruction_mask_class_count": len(obstruction_mask_ids),
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

    carrier_table = table_from_rows(CARRIER_GEODESIC_COLUMNS, carrier_rows)
    signature_table = table_from_rows(SIGNATURE_GEODESIC_COLUMNS, signature_rows)
    observable_table = table_from_rows(GEODESIC_OBSERVABLE_COLUMNS, observable_rows)

    geodesic_order = {
        "schema": "c985.d20_signature_geodesic_order@1",
        "object": "d20",
        "axis_rule": {
            "source": "certified positive and negative quotient weighted Poincare centers",
            "model": "Poincare disk points lifted to the hyperboloid model",
            "coordinate": "signed orthogonal projection to the complete geodesic through the two quotient centers",
            "orientation": "positive coordinates point toward the positive spectral quotient center",
            "carrier_point": "Euclidean barycenter of a signature carrier mask's active Poincare atoms",
        },
        "axis": {
            "positive_center_x1e12": {
                "x": int(states["positive"]["center_x_x1e12"]),
                "y": int(states["positive"]["center_y_x1e12"]),
            },
            "negative_center_x1e12": {
                "x": int(states["negative"]["center_x_x1e12"]),
                "y": int(states["negative"]["center_y_x1e12"]),
            },
            "axis_hyperbolic_length_x1e12": observable_values["axis_hyperbolic_length"],
            "axis_half_length_x1e12": observable_values["axis_half_length"],
            "axis_midpoint_x1e12": {
                "x": observable_values["axis_midpoint_x"],
                "y": observable_values["axis_midpoint_y"],
                "radius": observable_values["axis_midpoint_radius"],
            },
        },
        "threshold_summary": {
            "zero_threshold_agreement_count": observable_values["zero_threshold_agreement_count"],
            "zero_threshold_agreement_mass_x1e12": observable_values[
                "zero_threshold_agreement_mass"
            ],
            "best_threshold_x1e12": observable_values["best_threshold"],
            "best_threshold_agreement_count": observable_values[
                "best_threshold_agreement_count"
            ],
            "best_threshold_agreement_mass_x1e12": observable_values[
                "best_threshold_agreement_mass"
            ],
            "best_threshold_misclassified_count": observable_values[
                "best_threshold_misclassified_count"
            ],
            "best_threshold_misclassified_mass_x1e12": observable_values[
                "best_threshold_misclassified_mass"
            ],
            "obstruction_mask_class_ids": obstruction_mask_ids,
        },
        "carrier_geodesic_order": [
            {key: int(value) for key, value in row.items()} for row in carrier_rows
        ],
        "signature_geodesic_order": [
            {key: int(value) for key, value in row.items()} for row in signature_rows
        ],
    }

    positive_wrong = [
        row for row in best_misses if int(row["nodal_sign"]) == 1
    ]
    negative_wrong = [
        row for row in best_misses if int(row["nodal_sign"]) == -1
    ]
    checks = {
        "quotient_geometry_report_certified": geometry_report.get("status")
        == "C985_D20_SIGNATURE_QUOTIENT_POINCARE_GEOMETRY_CERTIFIED",
        "quotient_geometry_certificate_certified": geometry_certificate.get("status")
        == "C985_D20_SIGNATURE_QUOTIENT_POINCARE_GEOMETRY_CERTIFIED",
        "spectral_cut_report_certified": spectral_report.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "spectral_cut_certificate_certified": spectral_certificate.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "signature_subboundary_report_certified": subboundary_report.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "signature_subboundary_certificate_certified": subboundary_certificate.get("status")
        == "C985_D20_RECURRENT_SIGNATURE_SUBBOUNDARY_CERTIFIED",
        "active_atom_count_is_6": len(atom_coordinates) == 6,
        "carrier_mask_count_is_14": len(mask_projection_rows) == 14,
        "signature_vertex_count_is_221": len(vertex_projection_rows) == 221,
        "subboundary_vertex_count_is_221": len(subboundary_vertex_rows) == 221,
        "axis_length_matches_geometry_separation": observable_values["axis_hyperbolic_length"]
        == int(geometry["separation_summary"]["positive_negative_hyperbolic_separation_x1e12"]),
        "axis_length_matches_expected": observable_values["axis_hyperbolic_length"]
        == 171447126521,
        "axis_midpoint_matches_expected": (
            observable_values["axis_midpoint_x"],
            observable_values["axis_midpoint_y"],
            observable_values["axis_midpoint_radius"],
        )
        == (-21920116945, -28578291790, 36016805640),
        "best_threshold_matches_expected": observable_values["best_threshold"]
        == -51543783679,
        "zero_threshold_agreement_matches_expected": (
            observable_values["zero_threshold_agreement_count"],
            observable_values["zero_threshold_agreement_mass"],
        )
        == (162, 785660554020),
        "best_threshold_agreement_matches_expected": (
            observable_values["best_threshold_agreement_count"],
            observable_values["best_threshold_agreement_mass"],
        )
        == (192, 852128653272),
        "best_threshold_is_exhaustive_optimum": (
            int(best_threshold["agreement_count"]),
            int(best_threshold["agreement_mass_x1e12"]),
        )
        == (192, 852128653272),
        "best_threshold_misclassification_matches_expected": (
            observable_values["best_threshold_misclassified_count"],
            observable_values["best_threshold_misclassified_mass"],
            obstruction_mask_ids,
        )
        == (29, 147871346728, [4, 7, 8]),
        "all_positive_vertices_right_of_best_threshold": len(positive_wrong) == 0,
        "only_negative_obstruction_vertices_remain": len(negative_wrong) == 29,
        "positive_negative_mean_coordinates_match_expected": (
            observable_values["positive_mean_axis_coordinate"],
            observable_values["negative_mean_axis_coordinate"],
        )
        == (85897163407, -85040731263),
        "weighted_axis_mode_correlation_matches_expected": observable_values[
            "weighted_axis_mode_correlation"
        ]
        == 827040709152,
        "sign_pair_inversions_match_expected": (
            inversion_pair_count,
            observable_values["sign_pair_inversion_count_fraction"],
            observable_values["sign_pair_inversion_mass_fraction"],
        )
        == (1980, 163636363636, 131316550327),
        "projection_residuals_match_expected": (
            observable_values["stationary_mean_projection_residual"],
            observable_values["max_projection_residual"],
            observable_values["min_projection_residual"],
        )
        == (125701373183, 352612226540, 18830038433),
        "carrier_table_shape_is_14_by_23": tuple(carrier_table.shape)
        == (14, len(CARRIER_GEODESIC_COLUMNS)),
        "signature_table_shape_is_221_by_15": tuple(signature_table.shape)
        == (221, len(SIGNATURE_GEODESIC_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(GEODESIC_OBSERVABLE_COLUMNS)),
        "geometry_tables_available": "atom_geometry_table" in geometry_tables.files,
        "spectral_cut_tables_available": "eigenmode_vertex_table" in spectral_tables.files,
        "signature_subboundary_tables_available": "signature_vertex_table"
        in subboundary_tables.files,
        "geometry_json_schema_available": geometry.get("schema")
        == "c985.d20_signature_quotient_poincare_geometry@1",
        "spectral_cut_json_schema_available": spectral_cut.get("schema")
        == "c985.d20_signature_transfer_spectral_cut@1",
        "signature_subboundary_json_schema_available": subboundary.get("schema")
        == "c985.d20_recurrent_signature_subboundary@1",
    }

    witness = {
        "axis_hyperbolic_length_x1e12": observable_values["axis_hyperbolic_length"],
        "axis_half_length_x1e12": observable_values["axis_half_length"],
        "axis_midpoint_x1e12": {
            "x": observable_values["axis_midpoint_x"],
            "y": observable_values["axis_midpoint_y"],
            "radius": observable_values["axis_midpoint_radius"],
        },
        "best_threshold_x1e12": observable_values["best_threshold"],
        "zero_threshold_agreement_count": observable_values["zero_threshold_agreement_count"],
        "zero_threshold_agreement_mass_x1e12": observable_values[
            "zero_threshold_agreement_mass"
        ],
        "best_threshold_agreement_count": observable_values["best_threshold_agreement_count"],
        "best_threshold_agreement_mass_x1e12": observable_values[
            "best_threshold_agreement_mass"
        ],
        "best_threshold_misclassified_count": observable_values[
            "best_threshold_misclassified_count"
        ],
        "best_threshold_misclassified_mass_x1e12": observable_values[
            "best_threshold_misclassified_mass"
        ],
        "obstruction_mask_class_ids": obstruction_mask_ids,
        "positive_mean_axis_coordinate_x1e12": observable_values[
            "positive_mean_axis_coordinate"
        ],
        "negative_mean_axis_coordinate_x1e12": observable_values[
            "negative_mean_axis_coordinate"
        ],
        "weighted_axis_mode_correlation_x1e12": observable_values[
            "weighted_axis_mode_correlation"
        ],
        "sign_pair_inversion_count": inversion_pair_count,
        "sign_pair_inversion_count_fraction_x1e12": observable_values[
            "sign_pair_inversion_count_fraction"
        ],
        "sign_pair_inversion_mass_fraction_x1e12": observable_values[
            "sign_pair_inversion_mass_fraction"
        ],
        "stationary_mean_projection_residual_x1e12": observable_values[
            "stationary_mean_projection_residual"
        ],
        "max_projection_residual_x1e12": observable_values["max_projection_residual"],
        "min_projection_residual_x1e12": observable_values["min_projection_residual"],
        "carrier_geodesic_table_sha256": sha_array(carrier_table),
        "signature_geodesic_table_sha256": sha_array(signature_table),
        "geodesic_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_geodesic_order_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_GEODESIC_ORDER_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the quotient centers define a reproducible oriented hyperbolic geodesic axis",
            "every recurrent signature class receives a signed projection coordinate through its carrier-mask atom barycenter",
            "the zero point is not the spectral sign boundary; this mismatch is explicitly measured",
            "the exhaustive best one-dimensional threshold agrees with 192 of 221 signature classes and 0.852128653272 stationary mass",
            "all positive nodal signatures lie on the positive side of the best threshold; the remaining obstruction is exactly negative carrier-mask classes 4, 7, and 8",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_geodesic_order@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified positive-negative quotient centers induce an oriented "
            "Poincare geodesic axis on which recurrent signature classes have a "
            "reproducible signed order; the best threshold along this axis "
            "captures all positive nodal classes and isolates the exact negative "
            "carrier-mask obstruction."
        ),
        "stage_protocol": {
            "draft": "lift the quotient centers and carrier-mask barycenters to the hyperboloid model",
            "witness": "project each carrier mask and recurrent signature class onto the oriented quotient geodesic",
            "coherence": "exhaust all one-dimensional thresholds and check agreement, obstruction, correlation, and inversion observables",
            "closure": "certify a signed geodesic order while exposing the nonzero obstruction to perfect spectral separation",
            "emit": "emit geodesic-order JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "quotient_geometry_report": input_entry(
                QUOTIENT_GEOMETRY_REPORT,
                {
                    "status": geometry_report.get("status"),
                    "certificate_sha256": geometry_report.get("certificate_sha256"),
                },
            ),
            "quotient_geometry": input_entry(QUOTIENT_GEOMETRY_JSON),
            "quotient_geometry_tables": input_entry(QUOTIENT_GEOMETRY_TABLES),
            "quotient_geometry_certificate": input_entry(QUOTIENT_GEOMETRY_CERTIFICATE),
            "spectral_cut_report": input_entry(
                SPECTRAL_CUT_REPORT,
                {
                    "status": spectral_report.get("status"),
                    "certificate_sha256": spectral_report.get("certificate_sha256"),
                },
            ),
            "spectral_cut": input_entry(SPECTRAL_CUT_JSON),
            "spectral_cut_tables": input_entry(SPECTRAL_CUT_TABLES),
            "spectral_cut_certificate": input_entry(SPECTRAL_CUT_CERTIFICATE),
            "spectral_signature_vertices": input_entry(SPECTRAL_SIGNATURE_VERTICES),
            "spectral_mask_summary": input_entry(SPECTRAL_MASK_SUMMARY),
            "signature_subboundary_report": input_entry(
                SIGNATURE_SUBBOUNDARY_REPORT,
                {
                    "status": subboundary_report.get("status"),
                    "certificate_sha256": subboundary_report.get("certificate_sha256"),
                },
            ),
            "signature_subboundary": input_entry(SIGNATURE_SUBBOUNDARY_JSON),
            "signature_subboundary_tables": input_entry(SIGNATURE_SUBBOUNDARY_TABLES),
            "signature_subboundary_certificate": input_entry(
                SIGNATURE_SUBBOUNDARY_CERTIFICATE
            ),
            "signature_subboundary_vertices": input_entry(SIGNATURE_SUBBOUNDARY_VERTICES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_geodesic_order": relpath(OUT_DIR / "signature_geodesic_order.json"),
            "carrier_geodesic_order_csv": relpath(OUT_DIR / "carrier_geodesic_order.csv"),
            "signature_geodesic_order_csv": relpath(OUT_DIR / "signature_geodesic_order.csv"),
            "geodesic_order_observables_csv": relpath(OUT_DIR / "geodesic_order_observables.csv"),
            "signature_geodesic_order_tables": relpath(
                OUT_DIR / "signature_geodesic_order_tables.npz"
            ),
            "signature_geodesic_order_certificate": relpath(
                OUT_DIR / "signature_geodesic_order_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the oriented geodesic axis through the positive and negative quotient centers",
                "carrier-mask barycenter projections onto that axis",
                "signature-class inherited signed coordinates and order ranks",
                "the exhaustive best threshold agreement with the spectral nodal split",
                "the exact carrier-mask obstruction to perfect one-dimensional geometric separation",
            ],
            "does_not_certify_because_not_required": [
                "that the geodesic axis is a perfect classifier for the spectral cut",
                "a unique geometric coordinate for every possible signature embedding",
                "Karcher/Frechet barycenter projections",
                "continuum boundary dynamics or asymptotic mixing theory",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Resolve the three negative obstruction carrier masks geometrically: "
            "build the perpendicular residual coordinate to the quotient geodesic, "
            "then certify whether a two-coordinate hyperbolic chart separates the "
            "spectral nodal split without collapsing the active atom carriers."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_geodesic_order_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified quotient-geometry, spectral-cut, and recurrent-subboundary artifacts",
            "construct the positive-negative hyperbolic geodesic axis",
            "project carrier-mask barycenters and recurrent signature classes to signed axis coordinates",
            "exhaust one-dimensional thresholds and certify agreement plus obstruction observables",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_geodesic_order": geodesic_order,
        "carrier_geodesic_order_csv": csv_text(CARRIER_GEODESIC_COLUMNS, carrier_rows),
        "signature_geodesic_order_csv": csv_text(SIGNATURE_GEODESIC_COLUMNS, signature_rows),
        "geodesic_order_observables_csv": csv_text(
            GEODESIC_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "carrier_geodesic_table": carrier_table,
        "signature_geodesic_table": signature_table,
        "geodesic_observable_table": observable_table,
        "signature_geodesic_order_certificate": certificate,
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
    write_json(OUT_DIR / "signature_geodesic_order.json", payloads["signature_geodesic_order"])
    (OUT_DIR / "carrier_geodesic_order.csv").write_text(
        payloads["carrier_geodesic_order_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "signature_geodesic_order.csv").write_text(
        payloads["signature_geodesic_order_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "geodesic_order_observables.csv").write_text(
        payloads["geodesic_order_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_geodesic_order_tables.npz",
        carrier_geodesic_table=payloads["carrier_geodesic_table"],
        signature_geodesic_table=payloads["signature_geodesic_table"],
        geodesic_observable_table=payloads["geodesic_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_geodesic_order_certificate.json",
        payloads["signature_geodesic_order_certificate"],
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
                "axis_hyperbolic_length_x1e12": witness[
                    "axis_hyperbolic_length_x1e12"
                ],
                "best_threshold_x1e12": witness["best_threshold_x1e12"],
                "best_threshold_agreement_count": witness[
                    "best_threshold_agreement_count"
                ],
                "best_threshold_agreement_mass_x1e12": witness[
                    "best_threshold_agreement_mass_x1e12"
                ],
                "obstruction_mask_class_ids": witness["obstruction_mask_class_ids"],
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
