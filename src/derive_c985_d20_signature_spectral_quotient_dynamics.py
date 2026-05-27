from __future__ import annotations

import json
import math
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_boundary_transfer_operator import (
        OUT_DIR as BOUNDARY_TRANSFER_DIR,
    )
    from .derive_c985_d20_signature_subboundary_transfer_operator import (
        OUT_DIR as SIGNATURE_TRANSFER_DIR,
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
    from derive_c985_d20_signature_subboundary_transfer_operator import (
        OUT_DIR as SIGNATURE_TRANSFER_DIR,
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


THEOREM_ID = "c985_d20_signature_spectral_quotient_dynamics"
STATUS = "C985_D20_SIGNATURE_SPECTRAL_QUOTIENT_DYNAMICS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SPECTRAL_CUT_REPORT = SPECTRAL_CUT_DIR / "report.json"
SPECTRAL_CUT_JSON = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut.json"
SPECTRAL_CUT_TABLES = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_tables.npz"
SPECTRAL_CUT_CERTIFICATE = SPECTRAL_CUT_DIR / "signature_transfer_spectral_cut_certificate.json"

SIGNATURE_TRANSFER_REPORT = SIGNATURE_TRANSFER_DIR / "report.json"
SIGNATURE_TRANSFER_JSON = SIGNATURE_TRANSFER_DIR / "signature_transfer_operator.json"
SIGNATURE_TRANSFER_TABLES = SIGNATURE_TRANSFER_DIR / "signature_transfer_tables.npz"
SIGNATURE_TRANSFER_CERTIFICATE = SIGNATURE_TRANSFER_DIR / "signature_transfer_certificate.json"

BOUNDARY_TRANSFER_REPORT = BOUNDARY_TRANSFER_DIR / "report.json"
BOUNDARY_TRANSFER_JSON = BOUNDARY_TRANSFER_DIR / "boundary_transfer_operator.json"
BOUNDARY_TRANSFER_TABLES = BOUNDARY_TRANSFER_DIR / "boundary_transfer_tables.npz"
BOUNDARY_TRANSFER_CERTIFICATE = BOUNDARY_TRANSFER_DIR / "boundary_transfer_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_spectral_quotient_dynamics.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_signature_spectral_quotient_dynamics.py"

PROBABILITY_SCALE = 1_000_000_000_000

QUOTIENT_STATE_COLUMNS = [
    "state_id",
    "nodal_sign",
    "signature_vertex_count",
    "carrier_mask_class_count",
    "stationary_mass_x1e12",
    "self_transition_probability_x1e12",
    "exit_transition_probability_x1e12",
    "self_flow_twice_x1e12",
    "exit_flow_twice_x1e12",
    "within_signature_edge_count",
    "crossing_signature_edge_count",
    "within_mask_edge_count",
    "crossing_mask_edge_count",
]

QUOTIENT_TRANSITION_COLUMNS = [
    "source_state_id",
    "target_state_id",
    "source_nodal_sign",
    "target_nodal_sign",
    "transition_probability_x1e12",
    "stationary_flow_twice_x1e12",
    "is_crossing",
]

QUOTIENT_BASIN_COMPARISON_COLUMNS = [
    "basin_code",
    "core_stationary_mass_x1e12",
    "induced_participation_mass_x1e12",
    "induced_minus_core_x1e12",
    "abs_induced_minus_core_x1e12",
    "positive_side_mass_x1e12",
    "negative_side_mass_x1e12",
    "positive_fraction_x1e12",
    "positive_side_composition_x1e12",
    "negative_side_composition_x1e12",
]

QUOTIENT_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "state_count": 0,
    "positive_stationary_mass": 1,
    "negative_stationary_mass": 2,
    "undirected_cut_flux": 3,
    "directed_cross_flux_twice": 4,
    "positive_to_negative_probability": 5,
    "negative_to_positive_probability": 6,
    "positive_return_probability": 7,
    "negative_return_probability": 8,
    "quotient_lambda_2": 9,
    "quotient_spectral_gap": 10,
    "stationary_stay_probability": 11,
    "signature_lambda_2": 12,
    "signature_lambda_2_minus_quotient_lambda_2": 13,
    "core_induced_basin_tv_twice": 14,
    "core_positive_composition_tv_twice": 15,
    "core_negative_composition_tv_twice": 16,
    "entropy_rate": 17,
    "positive_row_entropy": 18,
    "negative_row_entropy": 19,
    "mask_cut_edge_count": 20,
    "signature_cut_edge_count": 21,
}


def scaled_float(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


def round_fraction(value: Fraction, *, scale: int = PROBABILITY_SCALE) -> int:
    numerator = value.numerator * scale
    quotient, remainder = divmod(numerator, value.denominator)
    if 2 * remainder >= value.denominator:
        quotient += 1
    return int(quotient)


def scaled_probability_row(probabilities: list[Fraction]) -> list[int]:
    floors = [
        (probability.numerator * PROBABILITY_SCALE) // probability.denominator
        for probability in probabilities
    ]
    remainder = PROBABILITY_SCALE - sum(floors)
    residues = [
        Fraction(
            (probability.numerator * PROBABILITY_SCALE) % probability.denominator,
            probability.denominator,
        )
        for probability in probabilities
    ]
    order = sorted(range(len(probabilities)), key=lambda index: (-residues[index], index))
    scaled = floors[:]
    for index in order[:remainder]:
        scaled[index] += 1
    return [int(value) for value in scaled]


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray([[int(row[column]) for column in columns] for row in rows], dtype=np.int64)


def entropy_binary(probability: Fraction) -> float:
    p = float(probability)
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -((1.0 - p) * math.log(1.0 - p) + p * math.log(p))


def tv_twice(left: dict[int, int], right: dict[int, int], keys: list[int]) -> int:
    return int(sum(abs(int(left[key]) - int(right[key])) for key in keys))


def build_payloads() -> dict[str, Any]:
    spectral_report = load_json(SPECTRAL_CUT_REPORT)
    spectral_cut = load_json(SPECTRAL_CUT_JSON)
    spectral_certificate = load_json(SPECTRAL_CUT_CERTIFICATE)
    signature_transfer_report = load_json(SIGNATURE_TRANSFER_REPORT)
    signature_transfer = load_json(SIGNATURE_TRANSFER_JSON)
    signature_transfer_certificate = load_json(SIGNATURE_TRANSFER_CERTIFICATE)
    boundary_transfer_report = load_json(BOUNDARY_TRANSFER_REPORT)
    boundary_transfer = load_json(BOUNDARY_TRANSFER_JSON)
    boundary_transfer_certificate = load_json(BOUNDARY_TRANSFER_CERTIFICATE)
    spectral_tables = np.load(SPECTRAL_CUT_TABLES, allow_pickle=False)
    signature_transfer_tables = np.load(SIGNATURE_TRANSFER_TABLES, allow_pickle=False)
    boundary_transfer_tables = np.load(BOUNDARY_TRANSFER_TABLES, allow_pickle=False)

    vertex_table = np.asarray(spectral_tables["eigenmode_vertex_table"], dtype=np.int64)
    cut_edge_table = np.asarray(spectral_tables["eigenmode_cut_edge_table"], dtype=np.int64)
    mask_table = np.asarray(spectral_tables["mask_eigenmode_table"], dtype=np.int64)
    basin_table = np.asarray(spectral_tables["basin_eigenmode_table"], dtype=np.int64)

    positive_mass = int(vertex_table[vertex_table[:, 2] == 1, 4].sum())
    negative_mass = int(vertex_table[vertex_table[:, 2] == -1, 4].sum())
    cut_flux = int(cut_edge_table[:, 9].sum())
    directed_cross_flux = Fraction(cut_flux, 2)
    positive_exit = directed_cross_flux / positive_mass
    negative_exit = directed_cross_flux / negative_mass
    positive_row = scaled_probability_row([1 - positive_exit, positive_exit])
    negative_row = scaled_probability_row([negative_exit, 1 - negative_exit])
    transition_matrix = np.asarray([positive_row, negative_row], dtype=np.int64)

    quotient_gap = positive_exit + negative_exit
    quotient_lambda_2 = 1 - quotient_gap
    signature_lambda_2 = Fraction(int(spectral_report["witness"]["lambda_2_x1e12"]), PROBABILITY_SCALE)
    stationary_stay = 1 - Fraction(cut_flux, PROBABILITY_SCALE)
    positive_row_entropy = entropy_binary(positive_exit)
    negative_row_entropy = entropy_binary(negative_exit)
    entropy_rate = (
        (positive_mass / PROBABILITY_SCALE) * positive_row_entropy
        + (negative_mass / PROBABILITY_SCALE) * negative_row_entropy
    )

    positive_vertex_count = int(np.count_nonzero(vertex_table[:, 2] == 1))
    negative_vertex_count = int(np.count_nonzero(vertex_table[:, 2] == -1))
    positive_mask_count = int(np.count_nonzero(mask_table[:, 2] == 1))
    negative_mask_count = int(np.count_nonzero(mask_table[:, 2] == -1))
    within_positive_edge_count = int(spectral_report["witness"]["within_positive_edge_count"])
    within_negative_edge_count = int(spectral_report["witness"]["within_negative_edge_count"])
    cut_edge_count = int(spectral_report["witness"]["cut_edge_count"])
    mask_within_positive_edge_count = int(spectral_report["witness"]["mask_within_positive_edge_count"])
    mask_within_negative_edge_count = int(spectral_report["witness"]["mask_within_negative_edge_count"])
    mask_cut_edge_count = int(spectral_report["witness"]["mask_cut_edge_count"])

    state_rows = [
        {
            "state_id": 0,
            "nodal_sign": 1,
            "signature_vertex_count": positive_vertex_count,
            "carrier_mask_class_count": positive_mask_count,
            "stationary_mass_x1e12": positive_mass,
            "self_transition_probability_x1e12": positive_row[0],
            "exit_transition_probability_x1e12": positive_row[1],
            "self_flow_twice_x1e12": 2 * positive_mass - cut_flux,
            "exit_flow_twice_x1e12": cut_flux,
            "within_signature_edge_count": within_positive_edge_count,
            "crossing_signature_edge_count": cut_edge_count,
            "within_mask_edge_count": mask_within_positive_edge_count,
            "crossing_mask_edge_count": mask_cut_edge_count,
        },
        {
            "state_id": 1,
            "nodal_sign": -1,
            "signature_vertex_count": negative_vertex_count,
            "carrier_mask_class_count": negative_mask_count,
            "stationary_mass_x1e12": negative_mass,
            "self_transition_probability_x1e12": negative_row[1],
            "exit_transition_probability_x1e12": negative_row[0],
            "self_flow_twice_x1e12": 2 * negative_mass - cut_flux,
            "exit_flow_twice_x1e12": cut_flux,
            "within_signature_edge_count": within_negative_edge_count,
            "crossing_signature_edge_count": cut_edge_count,
            "within_mask_edge_count": mask_within_negative_edge_count,
            "crossing_mask_edge_count": mask_cut_edge_count,
        },
    ]

    transition_rows = [
        {
            "source_state_id": 0,
            "target_state_id": 0,
            "source_nodal_sign": 1,
            "target_nodal_sign": 1,
            "transition_probability_x1e12": positive_row[0],
            "stationary_flow_twice_x1e12": 2 * positive_mass - cut_flux,
            "is_crossing": 0,
        },
        {
            "source_state_id": 0,
            "target_state_id": 1,
            "source_nodal_sign": 1,
            "target_nodal_sign": -1,
            "transition_probability_x1e12": positive_row[1],
            "stationary_flow_twice_x1e12": cut_flux,
            "is_crossing": 1,
        },
        {
            "source_state_id": 1,
            "target_state_id": 0,
            "source_nodal_sign": -1,
            "target_nodal_sign": 1,
            "transition_probability_x1e12": negative_row[0],
            "stationary_flow_twice_x1e12": cut_flux,
            "is_crossing": 1,
        },
        {
            "source_state_id": 1,
            "target_state_id": 1,
            "source_nodal_sign": -1,
            "target_nodal_sign": -1,
            "transition_probability_x1e12": negative_row[1],
            "stationary_flow_twice_x1e12": 2 * negative_mass - cut_flux,
            "is_crossing": 0,
        },
    ]

    core_basin_masses = {
        10: int(boundary_transfer_report["witness"]["stationary_basin_masses_x1e12"]["10"]),
        43: int(boundary_transfer_report["witness"]["stationary_basin_masses_x1e12"]["43"]),
        0: int(boundary_transfer_report["witness"]["stationary_basin_masses_x1e12"]["boundary"]),
    }
    induced_basin_masses: dict[int, int] = {}
    positive_basin_composition: dict[int, int] = {}
    negative_basin_composition: dict[int, int] = {}
    basin_rows: list[dict[str, int]] = []
    for row in basin_table:
        basin_code = int(row[0])
        induced = int(row[1])
        core = int(core_basin_masses[basin_code])
        induced_basin_masses[basin_code] = induced
        positive_basin_composition[basin_code] = int(row[5])
        negative_basin_composition[basin_code] = int(row[6])
        basin_rows.append(
            {
                "basin_code": basin_code,
                "core_stationary_mass_x1e12": core,
                "induced_participation_mass_x1e12": induced,
                "induced_minus_core_x1e12": induced - core,
                "abs_induced_minus_core_x1e12": abs(induced - core),
                "positive_side_mass_x1e12": int(row[2]),
                "negative_side_mass_x1e12": int(row[3]),
                "positive_fraction_x1e12": int(row[4]),
                "positive_side_composition_x1e12": int(row[5]),
                "negative_side_composition_x1e12": int(row[6]),
            }
        )

    core_induced_tv_twice = tv_twice(core_basin_masses, induced_basin_masses, [10, 43, 0])
    core_positive_tv_twice = tv_twice(core_basin_masses, positive_basin_composition, [10, 43, 0])
    core_negative_tv_twice = tv_twice(core_basin_masses, negative_basin_composition, [10, 43, 0])

    observable_values = {
        "state_count": 2,
        "positive_stationary_mass": positive_mass,
        "negative_stationary_mass": negative_mass,
        "undirected_cut_flux": cut_flux,
        "directed_cross_flux_twice": cut_flux,
        "positive_to_negative_probability": positive_row[1],
        "negative_to_positive_probability": negative_row[0],
        "positive_return_probability": positive_row[0],
        "negative_return_probability": negative_row[1],
        "quotient_lambda_2": round_fraction(quotient_lambda_2),
        "quotient_spectral_gap": round_fraction(quotient_gap),
        "stationary_stay_probability": round_fraction(stationary_stay),
        "signature_lambda_2": int(spectral_report["witness"]["lambda_2_x1e12"]),
        "signature_lambda_2_minus_quotient_lambda_2": int(
            int(spectral_report["witness"]["lambda_2_x1e12"])
            - round_fraction(quotient_lambda_2)
        ),
        "core_induced_basin_tv_twice": core_induced_tv_twice,
        "core_positive_composition_tv_twice": core_positive_tv_twice,
        "core_negative_composition_tv_twice": core_negative_tv_twice,
        "entropy_rate": scaled_float(entropy_rate),
        "positive_row_entropy": scaled_float(positive_row_entropy),
        "negative_row_entropy": scaled_float(negative_row_entropy),
        "mask_cut_edge_count": mask_cut_edge_count,
        "signature_cut_edge_count": cut_edge_count,
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

    state_table = table_from_rows(QUOTIENT_STATE_COLUMNS, state_rows)
    transition_table = table_from_rows(QUOTIENT_TRANSITION_COLUMNS, transition_rows)
    basin_table_out = table_from_rows(QUOTIENT_BASIN_COMPARISON_COLUMNS, basin_rows)
    observable_table = table_from_rows(QUOTIENT_OBSERVABLE_COLUMNS, observable_rows)
    stationary_vector = np.asarray([positive_mass, negative_mass], dtype=np.int64)

    exact_stationary_checks = [
        Fraction(positive_mass, PROBABILITY_SCALE) * (1 - positive_exit)
        + Fraction(negative_mass, PROBABILITY_SCALE) * negative_exit
        == Fraction(positive_mass, PROBABILITY_SCALE),
        Fraction(positive_mass, PROBABILITY_SCALE) * positive_exit
        + Fraction(negative_mass, PROBABILITY_SCALE) * (1 - negative_exit)
        == Fraction(negative_mass, PROBABILITY_SCALE),
    ]

    quotient = {
        "schema": "c985.d20_signature_spectral_quotient_dynamics@1",
        "object": "d20",
        "quotient_rule": {
            "source": "the certified second-eigenmode nodal cut of the 221-state signature transfer operator",
            "states": "positive and negative nodal sides",
            "transition_law": "stationary directed flow across each block divided by the source block stationary mass",
            "rounding_boundary": "crossing flux is odd at scale 1e12, so exact flow is stored as twice-flow integers",
        },
        "states": [
            {
                "state_id": int(row["state_id"]),
                "label": "positive" if int(row["nodal_sign"]) == 1 else "negative",
                **{key: int(value) for key, value in row.items() if key != "state_id"},
            }
            for row in state_rows
        ],
        "transition_matrix_x1e12": transition_matrix.tolist(),
        "stationary_distribution_x1e12": stationary_vector.tolist(),
        "spectral_summary": {
            "quotient_lambda_2_x1e12": observable_values["quotient_lambda_2"],
            "quotient_spectral_gap_x1e12": observable_values["quotient_spectral_gap"],
            "signature_lambda_2_x1e12": observable_values["signature_lambda_2"],
            "signature_lambda_2_minus_quotient_lambda_2_x1e12": observable_values[
                "signature_lambda_2_minus_quotient_lambda_2"
            ],
            "stationary_stay_probability_x1e12": observable_values[
                "stationary_stay_probability"
            ],
            "entropy_rate_x1e12": observable_values["entropy_rate"],
        },
        "flux_summary": {
            "undirected_cut_flux_x1e12": cut_flux,
            "directed_cross_flux_twice_x1e12": cut_flux,
            "positive_to_negative_probability_x1e12": positive_row[1],
            "negative_to_positive_probability_x1e12": negative_row[0],
            "positive_return_probability_x1e12": positive_row[0],
            "negative_return_probability_x1e12": negative_row[1],
        },
        "core_basin_comparison": {
            "core_basin_masses_x1e12": {
                "10": core_basin_masses[10],
                "43": core_basin_masses[43],
                "boundary": core_basin_masses[0],
            },
            "induced_basin_masses_x1e12": {
                "10": induced_basin_masses[10],
                "43": induced_basin_masses[43],
                "boundary": induced_basin_masses[0],
            },
            "core_induced_tv_twice_x1e12": core_induced_tv_twice,
            "core_positive_composition_tv_twice_x1e12": core_positive_tv_twice,
            "core_negative_composition_tv_twice_x1e12": core_negative_tv_twice,
            "basin_rows": basin_rows,
        },
    }

    checks = {
        "spectral_cut_report_certified": spectral_report.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "spectral_cut_certificate_certified": spectral_certificate.get("status")
        == "C985_D20_SIGNATURE_TRANSFER_SPECTRAL_CUT_CERTIFIED",
        "signature_transfer_report_certified": signature_transfer_report.get("status")
        == "C985_D20_SIGNATURE_SUBBOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "signature_transfer_certificate_certified": signature_transfer_certificate.get("status")
        == "C985_D20_SIGNATURE_SUBBOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "boundary_transfer_report_certified": boundary_transfer_report.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "boundary_transfer_certificate_certified": boundary_transfer_certificate.get("status")
        == "C985_D20_BOUNDARY_TRANSFER_OPERATOR_CERTIFIED",
        "state_count_is_2": len(state_rows) == 2,
        "state_masses_sum_to_one": positive_mass + negative_mass == PROBABILITY_SCALE,
        "state_masses_match_spectral_cut": positive_mass
        == int(spectral_report["witness"]["positive_stationary_mass_x1e12"])
        and negative_mass == int(spectral_report["witness"]["negative_stationary_mass_x1e12"]),
        "cut_flux_matches_spectral_cut": cut_flux
        == int(spectral_report["witness"]["undirected_cut_flux_x1e12"]),
        "transition_matrix_matches_expected": transition_matrix.tolist()
        == [[809168073437, 190831926563], [319560035288, 680439964712]],
        "transition_rows_sum_to_one": bool(np.all(transition_matrix.sum(axis=1) == PROBABILITY_SCALE)),
        "exact_stationary_law_holds": all(exact_stationary_checks),
        "quotient_lambda_2_matches_expected": observable_values["quotient_lambda_2"]
        == 489608038149,
        "quotient_spectral_gap_matches_expected": observable_values["quotient_spectral_gap"]
        == 510391961851,
        "stationary_stay_probability_matches_expected": observable_values[
            "stationary_stay_probability"
        ]
        == 761037548611,
        "signature_lambda_2_drop_matches_expected": observable_values[
            "signature_lambda_2_minus_quotient_lambda_2"
        ]
        == 97644498065,
        "positive_exit_probability_matches_expected": positive_row[1] == 190831926563,
        "negative_exit_probability_matches_expected": negative_row[0] == 319560035288,
        "mask_edge_counts_match_spectral_cut": mask_cut_edge_count == 16
        and mask_within_positive_edge_count == 14
        and mask_within_negative_edge_count == 14,
        "signature_edge_counts_match_spectral_cut": cut_edge_count == 4007
        and within_positive_edge_count == 5968
        and within_negative_edge_count == 3060,
        "core_basin_masses_match_boundary_transfer": core_basin_masses
        == {10: 121358270826, 43: 488349486805, 0: 390292242370},
        "induced_basin_masses_match_spectral_cut": induced_basin_masses
        == {10: 200037326277, 43: 406767255209, 0: 393195418514},
        "core_induced_tv_twice_matches_expected": core_induced_tv_twice == 163164463191,
        "core_positive_tv_twice_matches_expected": core_positive_tv_twice == 194971099061,
        "core_negative_tv_twice_matches_expected": core_negative_tv_twice == 158720315577,
        "state_table_shape_is_2_by_13": tuple(state_table.shape)
        == (2, len(QUOTIENT_STATE_COLUMNS)),
        "transition_table_shape_is_4_by_7": tuple(transition_table.shape)
        == (4, len(QUOTIENT_TRANSITION_COLUMNS)),
        "basin_table_shape_is_3_by_10": tuple(basin_table_out.shape)
        == (3, len(QUOTIENT_BASIN_COMPARISON_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(QUOTIENT_OBSERVABLE_COLUMNS)),
        "spectral_cut_json_schema_available": spectral_cut.get("schema")
        == "c985.d20_signature_transfer_spectral_cut@1",
        "signature_transfer_json_schema_available": signature_transfer.get("schema")
        == "c985.d20_signature_subboundary_transfer_operator@1",
        "boundary_transfer_json_schema_available": boundary_transfer.get("schema")
        == "c985.d20_boundary_transfer_operator@1",
        "signature_transfer_tables_available": "signature_transfer_matrix_x1e12"
        in signature_transfer_tables.files,
        "boundary_transfer_tables_available": "stationary_distribution_table"
        in boundary_transfer_tables.files,
    }

    witness = {
        "positive_stationary_mass_x1e12": positive_mass,
        "negative_stationary_mass_x1e12": negative_mass,
        "undirected_cut_flux_x1e12": cut_flux,
        "directed_cross_flux_twice_x1e12": cut_flux,
        "transition_matrix_x1e12": transition_matrix.tolist(),
        "quotient_lambda_2_x1e12": observable_values["quotient_lambda_2"],
        "quotient_spectral_gap_x1e12": observable_values["quotient_spectral_gap"],
        "stationary_stay_probability_x1e12": observable_values[
            "stationary_stay_probability"
        ],
        "positive_to_negative_probability_x1e12": positive_row[1],
        "negative_to_positive_probability_x1e12": negative_row[0],
        "signature_lambda_2_x1e12": observable_values["signature_lambda_2"],
        "signature_lambda_2_minus_quotient_lambda_2_x1e12": observable_values[
            "signature_lambda_2_minus_quotient_lambda_2"
        ],
        "core_basin_masses_x1e12": {
            "10": core_basin_masses[10],
            "43": core_basin_masses[43],
            "boundary": core_basin_masses[0],
        },
        "induced_basin_masses_x1e12": {
            "10": induced_basin_masses[10],
            "43": induced_basin_masses[43],
            "boundary": induced_basin_masses[0],
        },
        "core_induced_tv_twice_x1e12": core_induced_tv_twice,
        "core_positive_composition_tv_twice_x1e12": core_positive_tv_twice,
        "core_negative_composition_tv_twice_x1e12": core_negative_tv_twice,
        "entropy_rate_x1e12": observable_values["entropy_rate"],
        "positive_row_entropy_x1e12": observable_values["positive_row_entropy"],
        "negative_row_entropy_x1e12": observable_values["negative_row_entropy"],
        "quotient_state_table_sha256": sha_array(state_table),
        "quotient_transition_table_sha256": sha_array(transition_table),
        "quotient_basin_table_sha256": sha_array(basin_table_out),
        "quotient_observable_table_sha256": sha_array(observable_table),
        "quotient_transition_matrix_sha256": sha_array(transition_matrix),
        "quotient_stationary_vector_sha256": sha_array(stationary_vector),
    }

    certificate = {
        "schema": "c985.d20_signature_spectral_quotient_dynamics_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_SPECTRAL_QUOTIENT_DYNAMICS_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the pure carrier-mask nodal split collapses to a reversible two-state quotient chain",
            "the quotient transition law is determined by stationary cut flux and side masses",
            "the positive side exits more slowly than the negative side",
            "the quotient spectral gap is larger than the 221-state transfer gap, as expected after coarse graining",
            "the quotient's induced basin participation differs measurably from the original 10/43/boundary core basin masses",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_spectral_quotient_dynamics@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified second-eigenmode nodal cut of the 221-state signature "
            "transfer operator collapses to a verified reversible two-state "
            "quotient dynamics, with exact cut flux, row-stochastic transition "
            "probabilities, and a basin-mass comparison against the original "
            "10/43/boundary core transfer readout."
        ),
        "stage_protocol": {
            "draft": "collapse the 221-state transfer operator along the certified positive/negative spectral cut",
            "witness": "materialize quotient states, transition probabilities, exact twice-flow fluxes, and core-basin comparisons",
            "coherence": "check row sums, exact stationary law, quotient spectrum, cut flux, and basin-distance observables",
            "closure": "certify the two-state quotient without claiming a unique physical coarse graining beyond the declared spectral cut",
            "emit": "emit quotient JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
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
            "signature_transfer_report": input_entry(
                SIGNATURE_TRANSFER_REPORT,
                {
                    "status": signature_transfer_report.get("status"),
                    "certificate_sha256": signature_transfer_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "signature_transfer": input_entry(SIGNATURE_TRANSFER_JSON),
            "signature_transfer_tables": input_entry(SIGNATURE_TRANSFER_TABLES),
            "signature_transfer_certificate": input_entry(SIGNATURE_TRANSFER_CERTIFICATE),
            "boundary_transfer_report": input_entry(
                BOUNDARY_TRANSFER_REPORT,
                {
                    "status": boundary_transfer_report.get("status"),
                    "certificate_sha256": boundary_transfer_report.get(
                        "certificate_sha256"
                    ),
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
            "signature_spectral_quotient_dynamics": relpath(
                OUT_DIR / "signature_spectral_quotient_dynamics.json"
            ),
            "quotient_states_csv": relpath(OUT_DIR / "quotient_states.csv"),
            "quotient_transitions_csv": relpath(OUT_DIR / "quotient_transitions.csv"),
            "quotient_basin_comparison_csv": relpath(
                OUT_DIR / "quotient_basin_comparison.csv"
            ),
            "quotient_observables_csv": relpath(OUT_DIR / "quotient_observables.csv"),
            "signature_spectral_quotient_tables": relpath(
                OUT_DIR / "signature_spectral_quotient_tables.npz"
            ),
            "signature_spectral_quotient_certificate": relpath(
                OUT_DIR / "signature_spectral_quotient_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the two-state Markov quotient induced by the certified nodal cut",
                "exact twice-flow accounting for the odd scaled cut flux",
                "row-stochastic transition probabilities and exact stationary law",
                "quotient spectrum, entropy rate, and return/exit probabilities",
                "comparison between quotient-induced basin participation and the original core transfer basin masses",
            ],
            "does_not_certify_because_not_required": [
                "that this is the only meaningful coarse graining of the 221-state operator",
                "continuum metastability or asymptotic mixing-time bounds",
                "higher-order quotients from eigenmodes beyond the second",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Lift the two-state quotient back into geometry: assign the positive "
            "and negative spectral states to Poincare atom coordinates and certify "
            "their hyperbolic barycenters, separation, and relation to the original "
            "stationary core center."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_spectral_quotient_dynamics_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified spectral cut, signature transfer, and boundary transfer artifacts",
            "collapse positive and negative nodal sides using stationary directed cut flux",
            "emit exact twice-flow accounting for the odd scaled cut flux",
            "verify row-stochastic quotient transitions and exact stationary law",
            "compare quotient-induced basin masses against the original 10/43/boundary core basin masses",
            "check source hashes, artifact reproducibility, and registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_spectral_quotient_dynamics": quotient,
        "quotient_states_csv": csv_text(QUOTIENT_STATE_COLUMNS, state_rows),
        "quotient_transitions_csv": csv_text(
            QUOTIENT_TRANSITION_COLUMNS,
            transition_rows,
        ),
        "quotient_basin_comparison_csv": csv_text(
            QUOTIENT_BASIN_COMPARISON_COLUMNS,
            basin_rows,
        ),
        "quotient_observables_csv": csv_text(QUOTIENT_OBSERVABLE_COLUMNS, observable_rows),
        "quotient_state_table": state_table,
        "quotient_transition_table": transition_table,
        "quotient_basin_table": basin_table_out,
        "quotient_observable_table": observable_table,
        "quotient_transition_matrix": transition_matrix,
        "quotient_stationary_vector": stationary_vector,
        "signature_spectral_quotient_certificate": certificate,
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
        OUT_DIR / "signature_spectral_quotient_dynamics.json",
        payloads["signature_spectral_quotient_dynamics"],
    )
    (OUT_DIR / "quotient_states.csv").write_text(
        payloads["quotient_states_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "quotient_transitions.csv").write_text(
        payloads["quotient_transitions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "quotient_basin_comparison.csv").write_text(
        payloads["quotient_basin_comparison_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "quotient_observables.csv").write_text(
        payloads["quotient_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_spectral_quotient_tables.npz",
        quotient_state_table=payloads["quotient_state_table"],
        quotient_transition_table=payloads["quotient_transition_table"],
        quotient_basin_table=payloads["quotient_basin_table"],
        quotient_observable_table=payloads["quotient_observable_table"],
        quotient_transition_matrix=payloads["quotient_transition_matrix"],
        quotient_stationary_vector=payloads["quotient_stationary_vector"],
    )
    write_json(
        OUT_DIR / "signature_spectral_quotient_certificate.json",
        payloads["signature_spectral_quotient_certificate"],
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
                "transition_matrix_x1e12": witness["transition_matrix_x1e12"],
                "quotient_lambda_2_x1e12": witness["quotient_lambda_2_x1e12"],
                "quotient_spectral_gap_x1e12": witness[
                    "quotient_spectral_gap_x1e12"
                ],
                "core_induced_tv_twice_x1e12": witness[
                    "core_induced_tv_twice_x1e12"
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
