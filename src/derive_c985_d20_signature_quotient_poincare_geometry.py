from __future__ import annotations

import csv
import json
import math
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_boundary_transfer_operator import (
        OUT_DIR as BOUNDARY_TRANSFER_DIR,
    )
    from .derive_c985_d20_poincare_embedding import (
        OUT_DIR as POINCARE_DIR,
    )
    from .derive_c985_d20_signature_spectral_quotient_dynamics import (
        OUT_DIR as QUOTIENT_DIR,
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
    from derive_c985_d20_boundary_transfer_operator import (
        OUT_DIR as BOUNDARY_TRANSFER_DIR,
    )
    from derive_c985_d20_poincare_embedding import (
        OUT_DIR as POINCARE_DIR,
    )
    from derive_c985_d20_signature_spectral_quotient_dynamics import (
        OUT_DIR as QUOTIENT_DIR,
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


THEOREM_ID = "c985_d20_signature_quotient_poincare_geometry"
STATUS = "C985_D20_SIGNATURE_QUOTIENT_POINCARE_GEOMETRY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

QUOTIENT_REPORT = QUOTIENT_DIR / "report.json"
QUOTIENT_JSON = QUOTIENT_DIR / "signature_spectral_quotient_dynamics.json"
QUOTIENT_TABLES = QUOTIENT_DIR / "signature_spectral_quotient_tables.npz"
QUOTIENT_CERTIFICATE = QUOTIENT_DIR / "signature_spectral_quotient_certificate.json"

SPECTRAL_CUT_REPORT = SPECTRAL_CUT_DIR / "report.json"
SPECTRAL_CUT_JSON = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut.json"
SPECTRAL_CUT_TABLES = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_tables.npz"
SPECTRAL_CUT_ATOM_CSV = SPECTRAL_CUT_DIR / "atom_eigenmode_summary.csv"
SPECTRAL_CUT_CERTIFICATE = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_certificate.json"

POINCARE_REPORT = POINCARE_DIR / "report.json"
POINCARE_JSON = POINCARE_DIR / "poincare_embedding.json"
POINCARE_TABLES = POINCARE_DIR / "poincare_embedding.npz"
POINCARE_CERTIFICATE = POINCARE_DIR / "embedding_certificate.json"

BOUNDARY_TRANSFER_REPORT = BOUNDARY_TRANSFER_DIR / "report.json"
BOUNDARY_TRANSFER_JSON = BOUNDARY_TRANSFER_DIR / "boundary_transfer_operator.json"
BOUNDARY_TRANSFER_TABLES = BOUNDARY_TRANSFER_DIR / "boundary_transfer_tables.npz"
BOUNDARY_TRANSFER_CERTIFICATE = BOUNDARY_TRANSFER_DIR / "boundary_transfer_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_quotient_poincare_geometry.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_quotient_poincare_geometry.py"

PROBABILITY_SCALE = 1_000_000_000_000

STATE_GEOMETRY_COLUMNS = [
    "state_geometry_id",
    "state_id",
    "nodal_sign",
    "stationary_mass_x1e12",
    "center_x_x1e12",
    "center_y_x1e12",
    "center_radius_x1e12",
    "mean_atom_radius_x1e12",
    "mean_hyperbolic_atom_distance_x1e12",
    "hyperbolic_distance_to_core_center_x1e12",
    "euclidean_distance_to_core_center_x1e12",
    "hyperbolic_distance_to_total_center_x1e12",
    "atom_support_count",
    "top_atom_id",
    "top_atom_mass_x1e12",
]

ATOM_GEOMETRY_COLUMNS = [
    "atom_id",
    "poincare_x_x1e12",
    "poincare_y_x1e12",
    "poincare_radius_x1e12",
    "positive_side_mass_x1e12",
    "negative_side_mass_x1e12",
    "total_participation_mass_x1e12",
    "positive_fraction_x1e12",
    "distance_to_positive_center_x1e12",
    "distance_to_negative_center_x1e12",
    "distance_advantage_to_positive_x1e12",
    "mode_mean_x1e12",
]

GEOMETRY_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "positive_center_x": 0,
    "positive_center_y": 1,
    "positive_center_radius": 2,
    "negative_center_x": 3,
    "negative_center_y": 4,
    "negative_center_radius": 5,
    "total_center_x": 6,
    "total_center_y": 7,
    "total_center_radius": 8,
    "core_center_radius": 9,
    "positive_negative_hyperbolic_separation": 10,
    "positive_negative_euclidean_separation": 11,
    "positive_core_hyperbolic_distance": 12,
    "negative_core_hyperbolic_distance": 13,
    "total_core_hyperbolic_distance": 14,
    "positive_mean_hyperbolic_atom_distance": 15,
    "negative_mean_hyperbolic_atom_distance": 16,
    "total_mean_hyperbolic_atom_distance": 17,
    "positive_total_hyperbolic_distance": 18,
    "negative_total_hyperbolic_distance": 19,
    "negative_core_distance_advantage": 20,
    "recomposition_center_delta_abs_x": 21,
    "recomposition_center_delta_abs_y": 22,
}


def scaled_float(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


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


def read_atom_rows() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with SPECTRAL_CUT_ATOM_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: int(value) for key, value in row.items()})
    return rows


def coordinate_map(poincare: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(row["atom_id"]): row for row in poincare["coordinates"]}


def weighted_center(
    atom_rows: list[dict[str, int]],
    coords: dict[int, dict[str, Any]],
    weight_column: str,
) -> dict[str, Any]:
    total = int(sum(int(row[weight_column]) for row in atom_rows))
    if total <= 0:
        raise ValueError(f"empty weight column: {weight_column}")
    x = sum(int(row[weight_column]) * float(coords[int(row["atom_id"])]["x"]) for row in atom_rows) / total
    y = sum(int(row[weight_column]) * float(coords[int(row["atom_id"])]["y"]) for row in atom_rows) / total
    radius = math.hypot(x, y)
    mean_atom_radius = (
        sum(int(row[weight_column]) * float(coords[int(row["atom_id"])]["radius"]) for row in atom_rows)
        / total
    )
    center = (x, y)
    mean_hyperbolic_atom_distance = (
        sum(
            int(row[weight_column])
            * poincare_distance(
                (float(coords[int(row["atom_id"])]["x"]), float(coords[int(row["atom_id"])]["y"])),
                center,
            )
            for row in atom_rows
        )
        / total
    )
    top_atom = max(
        atom_rows,
        key=lambda row: (int(row[weight_column]), -int(row["atom_id"])),
    )
    return {
        "total_mass_x1e12": total,
        "x": x,
        "y": y,
        "radius": radius,
        "mean_atom_radius": mean_atom_radius,
        "mean_hyperbolic_atom_distance": mean_hyperbolic_atom_distance,
        "center": center,
        "top_atom_id": int(top_atom["atom_id"]),
        "top_atom_mass_x1e12": int(top_atom[weight_column]),
        "support_count": sum(1 for row in atom_rows if int(row[weight_column]) > 0),
    }


def state_row(
    geometry_id: int,
    state_id: int,
    nodal_sign: int,
    summary: dict[str, Any],
    core_center: tuple[float, float],
    total_center: tuple[float, float],
) -> dict[str, int]:
    return {
        "state_geometry_id": geometry_id,
        "state_id": state_id,
        "nodal_sign": nodal_sign,
        "stationary_mass_x1e12": int(summary["total_mass_x1e12"]),
        "center_x_x1e12": scaled_float(summary["x"]),
        "center_y_x1e12": scaled_float(summary["y"]),
        "center_radius_x1e12": scaled_float(summary["radius"]),
        "mean_atom_radius_x1e12": scaled_float(summary["mean_atom_radius"]),
        "mean_hyperbolic_atom_distance_x1e12": scaled_float(
            summary["mean_hyperbolic_atom_distance"]
        ),
        "hyperbolic_distance_to_core_center_x1e12": scaled_float(
            poincare_distance(summary["center"], core_center)
        ),
        "euclidean_distance_to_core_center_x1e12": scaled_float(
            euclidean_distance(summary["center"], core_center)
        ),
        "hyperbolic_distance_to_total_center_x1e12": scaled_float(
            poincare_distance(summary["center"], total_center)
        ),
        "atom_support_count": int(summary["support_count"]),
        "top_atom_id": int(summary["top_atom_id"]),
        "top_atom_mass_x1e12": int(summary["top_atom_mass_x1e12"]),
    }


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray([[int(row[column]) for column in columns] for row in rows], dtype=np.int64)


def build_payloads() -> dict[str, Any]:
    quotient_report = load_json(QUOTIENT_REPORT)
    quotient = load_json(QUOTIENT_JSON)
    quotient_certificate = load_json(QUOTIENT_CERTIFICATE)
    spectral_report = load_json(SPECTRAL_CUT_REPORT)
    spectral_cut = load_json(SPECTRAL_CUT_JSON)
    spectral_certificate = load_json(SPECTRAL_CUT_CERTIFICATE)
    poincare_report = load_json(POINCARE_REPORT)
    poincare = load_json(POINCARE_JSON)
    poincare_certificate = load_json(POINCARE_CERTIFICATE)
    boundary_report = load_json(BOUNDARY_TRANSFER_REPORT)
    boundary_transfer = load_json(BOUNDARY_TRANSFER_JSON)
    boundary_certificate = load_json(BOUNDARY_TRANSFER_CERTIFICATE)
    quotient_tables = np.load(QUOTIENT_TABLES, allow_pickle=False)
    spectral_tables = np.load(SPECTRAL_CUT_TABLES, allow_pickle=False)
    poincare_tables = np.load(POINCARE_TABLES, allow_pickle=False)
    boundary_tables = np.load(BOUNDARY_TRANSFER_TABLES, allow_pickle=False)

    atom_rows_source = read_atom_rows()
    coords = coordinate_map(poincare)
    core = boundary_report["witness"]["geometric_observables"]["weighted_poincare_center"]
    core_center = (float(core["x"]), float(core["y"]))

    positive = weighted_center(atom_rows_source, coords, "positive_side_mass_x1e12")
    negative = weighted_center(atom_rows_source, coords, "negative_side_mass_x1e12")
    total = weighted_center(atom_rows_source, coords, "stationary_participation_mass_x1e12")
    recomposed_center = (
        (
            int(positive["total_mass_x1e12"]) * float(positive["x"])
            + int(negative["total_mass_x1e12"]) * float(negative["x"])
        )
        / PROBABILITY_SCALE,
        (
            int(positive["total_mass_x1e12"]) * float(positive["y"])
            + int(negative["total_mass_x1e12"]) * float(negative["y"])
        )
        / PROBABILITY_SCALE,
    )

    state_rows = [
        state_row(0, 0, 1, positive, core_center, total["center"]),
        state_row(1, 1, -1, negative, core_center, total["center"]),
        state_row(2, 2, 0, total, core_center, total["center"]),
    ]

    atom_rows: list[dict[str, int]] = []
    for row in atom_rows_source:
        atom_id = int(row["atom_id"])
        point = (float(coords[atom_id]["x"]), float(coords[atom_id]["y"]))
        distance_positive = scaled_float(poincare_distance(point, positive["center"]))
        distance_negative = scaled_float(poincare_distance(point, negative["center"]))
        atom_rows.append(
            {
                "atom_id": atom_id,
                "poincare_x_x1e12": scaled_float(float(coords[atom_id]["x"])),
                "poincare_y_x1e12": scaled_float(float(coords[atom_id]["y"])),
                "poincare_radius_x1e12": scaled_float(float(coords[atom_id]["radius"])),
                "positive_side_mass_x1e12": int(row["positive_side_mass_x1e12"]),
                "negative_side_mass_x1e12": int(row["negative_side_mass_x1e12"]),
                "total_participation_mass_x1e12": int(row["stationary_participation_mass_x1e12"]),
                "positive_fraction_x1e12": int(row["positive_fraction_x1e12"]),
                "distance_to_positive_center_x1e12": distance_positive,
                "distance_to_negative_center_x1e12": distance_negative,
                "distance_advantage_to_positive_x1e12": distance_negative - distance_positive,
                "mode_mean_x1e12": int(row["mode_mean_x1e12"]),
            }
        )

    positive_negative_hyperbolic = scaled_float(
        poincare_distance(positive["center"], negative["center"])
    )
    positive_negative_euclidean = scaled_float(
        euclidean_distance(positive["center"], negative["center"])
    )
    positive_core = scaled_float(poincare_distance(positive["center"], core_center))
    negative_core = scaled_float(poincare_distance(negative["center"], core_center))
    total_core = scaled_float(poincare_distance(total["center"], core_center))
    positive_total = scaled_float(poincare_distance(positive["center"], total["center"]))
    negative_total = scaled_float(poincare_distance(negative["center"], total["center"]))
    recomposition_delta_x = abs(scaled_float(recomposed_center[0]) - scaled_float(total["x"]))
    recomposition_delta_y = abs(scaled_float(recomposed_center[1]) - scaled_float(total["y"]))

    observable_values = {
        "positive_center_x": scaled_float(positive["x"]),
        "positive_center_y": scaled_float(positive["y"]),
        "positive_center_radius": scaled_float(positive["radius"]),
        "negative_center_x": scaled_float(negative["x"]),
        "negative_center_y": scaled_float(negative["y"]),
        "negative_center_radius": scaled_float(negative["radius"]),
        "total_center_x": scaled_float(total["x"]),
        "total_center_y": scaled_float(total["y"]),
        "total_center_radius": scaled_float(total["radius"]),
        "core_center_radius": int(core["radius_x1e12"]),
        "positive_negative_hyperbolic_separation": positive_negative_hyperbolic,
        "positive_negative_euclidean_separation": positive_negative_euclidean,
        "positive_core_hyperbolic_distance": positive_core,
        "negative_core_hyperbolic_distance": negative_core,
        "total_core_hyperbolic_distance": total_core,
        "positive_mean_hyperbolic_atom_distance": scaled_float(
            positive["mean_hyperbolic_atom_distance"]
        ),
        "negative_mean_hyperbolic_atom_distance": scaled_float(
            negative["mean_hyperbolic_atom_distance"]
        ),
        "total_mean_hyperbolic_atom_distance": scaled_float(
            total["mean_hyperbolic_atom_distance"]
        ),
        "positive_total_hyperbolic_distance": positive_total,
        "negative_total_hyperbolic_distance": negative_total,
        "negative_core_distance_advantage": positive_core - negative_core,
        "recomposition_center_delta_abs_x": recomposition_delta_x,
        "recomposition_center_delta_abs_y": recomposition_delta_y,
    }

    observable_rows: list[dict[str, int]] = []
    for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1]):
        observable_rows.append(
            {
                "observable_id": len(observable_rows),
                "observable_code": int(code),
                "value_x1e12": int(observable_values[name]),
                "aux_id": -1,
            }
        )

    state_table = table_from_rows(STATE_GEOMETRY_COLUMNS, state_rows)
    atom_table = table_from_rows(ATOM_GEOMETRY_COLUMNS, atom_rows)
    observable_table = table_from_rows(GEOMETRY_OBSERVABLE_COLUMNS, observable_rows)

    geometry = {
        "schema": "c985.d20_signature_quotient_poincare_geometry@1",
        "object": "d20",
        "geometry_rule": {
            "source": "the certified two-state spectral quotient and second-eigenmode atom participation masses",
            "coordinates": "the certified 20-atom Poincare disk embedding",
            "center": "weighted Euclidean center in the Poincare disk, matching prior transfer-center convention",
            "separation": "Poincare disk hyperbolic distance between weighted centers",
        },
        "state_geometry": [
            {
                "state_id": int(row["state_id"]),
                "label": "positive" if int(row["nodal_sign"]) == 1 else "negative" if int(row["nodal_sign"]) == -1 else "total",
                **{key: int(value) for key, value in row.items() if key != "state_id"},
            }
            for row in state_rows
        ],
        "separation_summary": {
            "positive_negative_hyperbolic_separation_x1e12": positive_negative_hyperbolic,
            "positive_negative_euclidean_separation_x1e12": positive_negative_euclidean,
            "positive_core_hyperbolic_distance_x1e12": positive_core,
            "negative_core_hyperbolic_distance_x1e12": negative_core,
            "total_core_hyperbolic_distance_x1e12": total_core,
            "negative_core_distance_advantage_x1e12": positive_core - negative_core,
        },
        "recomposition": {
            "weighted_state_center_x_x1e12": scaled_float(recomposed_center[0]),
            "weighted_state_center_y_x1e12": scaled_float(recomposed_center[1]),
            "total_center_x_x1e12": scaled_float(total["x"]),
            "total_center_y_x1e12": scaled_float(total["y"]),
            "delta_abs_x_x1e12": recomposition_delta_x,
            "delta_abs_y_x1e12": recomposition_delta_y,
        },
        "atom_geometry": [
            {
                **{key: int(value) for key, value in row.items()},
                "atom_label": str(coords[int(row["atom_id"])]["atom_label"]),
            }
            for row in atom_rows
        ],
        "core_center": {
            "x_x1e12": int(core["x_x1e12"]),
            "y_x1e12": int(core["y_x1e12"]),
            "radius_x1e12": int(core["radius_x1e12"]),
        },
    }

    checks = {
        "quotient_report_certified": quotient_report.get("status")
        == "C985_D20_SIGNATURE_SPECTRAL_QUOTIENT_DYNAMICS_CERTIFIED",
        "quotient_certificate_certified": quotient_certificate.get("status")
        == "C985_D20_SIGNATURE_SPECTRAL_QUOTIENT_DYNAMICS_CERTIFIED",
        "spectral_cut_report_certified": spectral_report.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "spectral_cut_certificate_certified": spectral_certificate.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "poincare_report_certified": poincare_report.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "poincare_certificate_certified": poincare_certificate.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "boundary_transfer_report_certified": boundary_report.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "boundary_transfer_certificate_certified": boundary_certificate.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "active_atom_count_is_6": len(atom_rows_source) == 6,
        "state_geometry_table_shape_is_3_by_15": tuple(state_table.shape)
        == (3, len(STATE_GEOMETRY_COLUMNS)),
        "atom_geometry_table_shape_is_6_by_12": tuple(atom_table.shape)
        == (6, len(ATOM_GEOMETRY_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(GEOMETRY_OBSERVABLE_COLUMNS)),
        "positive_center_matches_expected": (
            observable_values["positive_center_x"],
            observable_values["positive_center_y"],
            observable_values["positive_center_radius"],
        )
        == (20629332981, -33331853999, 39199258542),
        "negative_center_matches_expected": (
            observable_values["negative_center_x"],
            observable_values["negative_center_y"],
            observable_values["negative_center_radius"],
        )
        == (-64414008159, -23944469697, 68720463300),
        "total_center_matches_expected": (
            observable_values["total_center_x"],
            observable_values["total_center_y"],
            observable_values["total_center_radius"],
        )
        == (-11167767766, -29821977736, 31844456235),
        "positive_negative_separation_matches_expected": positive_negative_hyperbolic
        == 171447126521,
        "positive_core_distance_matches_expected": positive_core == 154209412933,
        "negative_core_distance_matches_expected": negative_core == 50625248627,
        "total_core_distance_matches_expected": total_core == 94762246226,
        "negative_center_is_closer_to_core_than_positive": negative_core < positive_core,
        "mean_hyperbolic_atom_distances_match_expected": (
            observable_values["positive_mean_hyperbolic_atom_distance"],
            observable_values["negative_mean_hyperbolic_atom_distance"],
            observable_values["total_mean_hyperbolic_atom_distance"],
        )
        == (305140715396, 286772503879, 311069149257),
        "recomposition_center_matches_total_center": recomposition_delta_x == 0
        and recomposition_delta_y == 0,
        "state_masses_match_quotient": (
            int(state_rows[0]["stationary_mass_x1e12"]),
            int(state_rows[1]["stationary_mass_x1e12"]),
        )
        == (
            int(quotient_report["witness"]["positive_stationary_mass_x1e12"]),
            int(quotient_report["witness"]["negative_stationary_mass_x1e12"]),
        ),
        "top_atoms_match_spectral_cut_reading": (
            int(state_rows[0]["top_atom_id"]),
            int(state_rows[1]["top_atom_id"]),
            int(state_rows[2]["top_atom_id"]),
        )
        == (7, 12, 19),
        "core_center_matches_boundary_transfer": (
            int(core["x_x1e12"]),
            int(core["y_x1e12"]),
            int(core["radius_x1e12"]),
        )
        == (-50213137809, -3098360902, 50308637915),
        "poincare_coordinate_count_is_20": len(poincare["coordinates"]) == 20,
        "poincare_tables_available": "coordinate_table" in poincare_tables.files,
        "quotient_tables_available": "quotient_stationary_vector" in quotient_tables.files,
        "spectral_cut_tables_available": "atom_eigenmode_table" in spectral_tables.files,
        "boundary_transfer_tables_available": "stationary_distribution_table"
        in boundary_tables.files,
        "quotient_json_schema_available": quotient.get("schema")
        == "c985.d20_signature_spectral_quotient_dynamics@1",
        "spectral_cut_json_schema_available": spectral_cut.get("schema")
        == "c985.d20_signature_transfer_spectral_cut@1",
        "poincare_json_schema_available": poincare.get("schema")
        == "c985.d20_poincare_embedding@1",
        "boundary_transfer_json_schema_available": boundary_transfer.get("schema")
        == "c985.d20_boundary_transfer_operator@1",
    }

    witness = {
        "positive_center_x1e12": {
            "x": observable_values["positive_center_x"],
            "y": observable_values["positive_center_y"],
            "radius": observable_values["positive_center_radius"],
        },
        "negative_center_x1e12": {
            "x": observable_values["negative_center_x"],
            "y": observable_values["negative_center_y"],
            "radius": observable_values["negative_center_radius"],
        },
        "total_center_x1e12": {
            "x": observable_values["total_center_x"],
            "y": observable_values["total_center_y"],
            "radius": observable_values["total_center_radius"],
        },
        "core_center_x1e12": {
            "x": int(core["x_x1e12"]),
            "y": int(core["y_x1e12"]),
            "radius": int(core["radius_x1e12"]),
        },
        "positive_negative_hyperbolic_separation_x1e12": positive_negative_hyperbolic,
        "positive_negative_euclidean_separation_x1e12": positive_negative_euclidean,
        "positive_core_hyperbolic_distance_x1e12": positive_core,
        "negative_core_hyperbolic_distance_x1e12": negative_core,
        "total_core_hyperbolic_distance_x1e12": total_core,
        "negative_core_distance_advantage_x1e12": positive_core - negative_core,
        "positive_mean_hyperbolic_atom_distance_x1e12": observable_values[
            "positive_mean_hyperbolic_atom_distance"
        ],
        "negative_mean_hyperbolic_atom_distance_x1e12": observable_values[
            "negative_mean_hyperbolic_atom_distance"
        ],
        "total_mean_hyperbolic_atom_distance_x1e12": observable_values[
            "total_mean_hyperbolic_atom_distance"
        ],
        "positive_top_atom_id": int(state_rows[0]["top_atom_id"]),
        "negative_top_atom_id": int(state_rows[1]["top_atom_id"]),
        "total_top_atom_id": int(state_rows[2]["top_atom_id"]),
        "recomposition_delta_abs_x_x1e12": recomposition_delta_x,
        "recomposition_delta_abs_y_x1e12": recomposition_delta_y,
        "state_geometry_table_sha256": sha_array(state_table),
        "atom_geometry_table_sha256": sha_array(atom_table),
        "geometry_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_quotient_poincare_geometry_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_QUOTIENT_POINCARE_GEOMETRY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the two spectral quotient states have reproducible weighted Poincare disk centers",
            "the positive and negative quotient centers have certified hyperbolic separation",
            "the negative spectral center lies closer to the original stationary core center than the positive center",
            "the quotient-state weighted recomposition gives the total signature-transfer atom center",
            "this certifies disk-center geometry, not a Karcher or Frechet barycenter construction",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_quotient_poincare_geometry@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified two-state spectral quotient lifts to the certified "
            "Poincare atom embedding as two weighted disk centers whose "
            "hyperbolic separation, distance to the original stationary core "
            "center, and recomposition center are reproducible."
        ),
        "stage_protocol": {
            "draft": "assign positive, negative, and total quotient atom participation masses to certified Poincare atom coordinates",
            "witness": "materialize state centers, atom distances to centers, hyperbolic separations, and core-center distances",
            "coherence": "check expected centers, separation, recomposition, top atoms, and source artifact certification",
            "closure": "certify quotient Poincare geometry without claiming a continuum or Karcher barycenter",
            "emit": "emit geometry JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "quotient_report": input_entry(
                QUOTIENT_REPORT,
                {
                    "status": quotient_report.get("status"),
                    "certificate_sha256": quotient_report.get("certificate_sha256"),
                },
            ),
            "quotient": input_entry(QUOTIENT_JSON),
            "quotient_tables": input_entry(QUOTIENT_TABLES),
            "quotient_certificate": input_entry(QUOTIENT_CERTIFICATE),
            "spectral_cut_report": input_entry(
                SPECTRAL_CUT_REPORT,
                {
                    "status": spectral_report.get("status"),
                    "certificate_sha256": spectral_report.get("certificate_sha256"),
                },
            ),
            "spectral_cut": input_entry(SPECTRAL_CUT_JSON),
            "spectral_cut_tables": input_entry(SPECTRAL_CUT_TABLES),
            "spectral_cut_atom_summary": input_entry(SPECTRAL_CUT_ATOM_CSV),
            "spectral_cut_certificate": input_entry(SPECTRAL_CUT_CERTIFICATE),
            "poincare_report": input_entry(
                POINCARE_REPORT,
                {
                    "status": poincare_report.get("status"),
                    "certificate_sha256": poincare_report.get("certificate_sha256"),
                },
            ),
            "poincare_embedding": input_entry(POINCARE_JSON),
            "poincare_tables": input_entry(POINCARE_TABLES),
            "poincare_certificate": input_entry(POINCARE_CERTIFICATE),
            "boundary_transfer_report": input_entry(
                BOUNDARY_TRANSFER_REPORT,
                {
                    "status": boundary_report.get("status"),
                    "certificate_sha256": boundary_report.get("certificate_sha256"),
                },
            ),
            "boundary_transfer": input_entry(BOUNDARY_TRANSFER_JSON),
            "boundary_transfer_tables": input_entry(BOUNDARY_TRANSFER_TABLES),
            "boundary_transfer_certificate": input_entry(BOUNDARY_TRANSFER_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_quotient_poincare_geometry": relpath(
                OUT_DIR / "signature_quotient_poincare_geometry.json"
            ),
            "quotient_state_geometry_csv": relpath(OUT_DIR / "quotient_state_geometry.csv"),
            "quotient_atom_geometry_csv": relpath(OUT_DIR / "quotient_atom_geometry.csv"),
            "quotient_geometry_observables_csv": relpath(
                OUT_DIR / "quotient_geometry_observables.csv"
            ),
            "signature_quotient_poincare_geometry_tables": relpath(
                OUT_DIR / "signature_quotient_poincare_geometry_tables.npz"
            ),
            "signature_quotient_poincare_geometry_certificate": relpath(
                OUT_DIR / "signature_quotient_poincare_geometry_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "weighted Poincare disk centers for positive, negative, and total spectral quotient atom participation",
                "Poincare hyperbolic separation between positive and negative quotient centers",
                "distance of each quotient center to the original stationary core center",
                "atom-level distances to both quotient centers",
                "exact recomposition of the total atom center from positive and negative quotient centers",
            ],
            "does_not_certify_because_not_required": [
                "Karcher/Frechet barycenters in the hyperbolic metric",
                "a continuum boundary or asymptotic visual measure",
                "a unique physical interpretation of the quotient states",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the certified quotient centers as poles for a signed hyperbolic "
            "coordinate on the active atoms: project each recurrent signature "
            "class onto the positive-negative center geodesic and certify a "
            "one-dimensional order compatible with the spectral nodal signs."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_quotient_poincare_geometry_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified quotient, spectral-cut, Poincare, and boundary-transfer artifacts",
            "assign quotient atom participation masses to Poincare atom coordinates",
            "compute weighted disk centers and Poincare hyperbolic center distances",
            "verify center coordinates, separation, top atoms, and recomposition",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_quotient_poincare_geometry": geometry,
        "quotient_state_geometry_csv": csv_text(STATE_GEOMETRY_COLUMNS, state_rows),
        "quotient_atom_geometry_csv": csv_text(ATOM_GEOMETRY_COLUMNS, atom_rows),
        "quotient_geometry_observables_csv": csv_text(
            GEOMETRY_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "state_geometry_table": state_table,
        "atom_geometry_table": atom_table,
        "geometry_observable_table": observable_table,
        "signature_quotient_poincare_geometry_certificate": certificate,
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
        OUT_DIR / "signature_quotient_poincare_geometry.json",
        payloads["signature_quotient_poincare_geometry"],
    )
    (OUT_DIR / "quotient_state_geometry.csv").write_text(
        payloads["quotient_state_geometry_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "quotient_atom_geometry.csv").write_text(
        payloads["quotient_atom_geometry_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "quotient_geometry_observables.csv").write_text(
        payloads["quotient_geometry_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_quotient_poincare_geometry_tables.npz",
        state_geometry_table=payloads["state_geometry_table"],
        atom_geometry_table=payloads["atom_geometry_table"],
        geometry_observable_table=payloads["geometry_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_quotient_poincare_geometry_certificate.json",
        payloads["signature_quotient_poincare_geometry_certificate"],
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
                "positive_center_x1e12": witness["positive_center_x1e12"],
                "negative_center_x1e12": witness["negative_center_x1e12"],
                "positive_negative_hyperbolic_separation_x1e12": witness[
                    "positive_negative_hyperbolic_separation_x1e12"
                ],
                "negative_core_distance_advantage_x1e12": witness[
                    "negative_core_distance_advantage_x1e12"
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
