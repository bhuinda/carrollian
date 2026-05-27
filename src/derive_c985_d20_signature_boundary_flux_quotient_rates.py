from __future__ import annotations

import json
import math
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_flux_cells import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        OUT_DIR as BOUNDARY_FLUX_DIR,
    )
    from .derive_c985_d20_signature_spectral_quotient_dynamics import (
        OUT_DIR as QUOTIENT_DIR,
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
    from derive_c985_d20_signature_boundary_flux_cells import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        OUT_DIR as BOUNDARY_FLUX_DIR,
    )
    from derive_c985_d20_signature_spectral_quotient_dynamics import (
        OUT_DIR as QUOTIENT_DIR,
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


THEOREM_ID = "c985_d20_signature_boundary_flux_quotient_rates"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_FLUX_QUOTIENT_RATES_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

BOUNDARY_FLUX_REPORT = BOUNDARY_FLUX_DIR / "report.json"
BOUNDARY_FLUX_JSON = BOUNDARY_FLUX_DIR / "signature_boundary_flux_cells.json"
BOUNDARY_FLUX_TABLES = BOUNDARY_FLUX_DIR / "signature_boundary_flux_cells_tables.npz"
BOUNDARY_FLUX_CERTIFICATE = (
    BOUNDARY_FLUX_DIR / "signature_boundary_flux_cells_certificate.json"
)
BOUNDARY_PARTITION_SUMMARY = BOUNDARY_FLUX_DIR / "boundary_partition_summary.csv"

QUOTIENT_REPORT = QUOTIENT_DIR / "report.json"
QUOTIENT_JSON = QUOTIENT_DIR / "signature_spectral_quotient_dynamics.json"
QUOTIENT_TABLES = QUOTIENT_DIR / "signature_spectral_quotient_tables.npz"
QUOTIENT_CERTIFICATE = QUOTIENT_DIR / "signature_spectral_quotient_certificate.json"
QUOTIENT_STATES = QUOTIENT_DIR / "quotient_states.csv"
QUOTIENT_TRANSITIONS = QUOTIENT_DIR / "quotient_transitions.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_boundary_flux_quotient_rates.py"
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_flux_quotient_rates.py"
)

PROBABILITY_SCALE = 1_000_000_000_000

BOUNDARY_RATE_PARTITION_COLUMNS = [
    "boundary_partition_code",
    "partition_order",
    "mask_edge_count",
    "signature_cut_edge_count",
    "undirected_stationary_flux_x1e12",
    "flux_fraction_of_total_cut_x1e12",
    "positive_to_negative_probability_contribution_x1e12",
    "negative_to_positive_probability_contribution_x1e12",
    "positive_exit_share_x1e12",
    "negative_exit_share_x1e12",
    "positive_entropy_contribution_x1e12",
    "negative_entropy_contribution_x1e12",
    "refined_entropy_contribution_x1e12",
]

BOUNDARY_REFINED_TRANSITION_COLUMNS = [
    "event_id",
    "source_state_id",
    "target_state_id",
    "source_nodal_sign",
    "target_nodal_sign",
    "event_role_code",
    "boundary_partition_code",
    "transition_probability_x1e12",
    "stationary_flow_twice_x1e12",
    "is_crossing",
]

BOUNDARY_ENTROPY_TERM_COLUMNS = [
    "term_id",
    "source_state_id",
    "event_role_code",
    "boundary_partition_code",
    "probability_x1e12",
    "stationary_mass_x1e12",
    "weighted_entropy_contribution_x1e12",
]

BOUNDARY_RATE_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "state_count": 0,
    "boundary_partition_count": 1,
    "positive_stationary_mass": 2,
    "negative_stationary_mass": 3,
    "total_undirected_cut_flux": 4,
    "high_negative_undirected_cut_flux": 5,
    "central_negative_undirected_cut_flux": 6,
    "high_negative_flux_fraction": 7,
    "central_negative_flux_fraction": 8,
    "positive_to_negative_probability": 9,
    "negative_to_positive_probability": 10,
    "positive_high_negative_probability": 11,
    "positive_central_negative_probability": 12,
    "negative_high_negative_probability": 13,
    "negative_central_negative_probability": 14,
    "positive_self_refined_probability": 15,
    "negative_self_refined_probability": 16,
    "central_share_of_positive_exit": 17,
    "central_share_of_negative_exit": 18,
    "quotient_entropy_rate": 19,
    "refined_boundary_entropy_rate": 20,
    "entropy_refinement_surplus": 21,
    "boundary_split_entropy": 22,
    "positive_refined_row_entropy": 23,
    "negative_refined_row_entropy": 24,
    "positive_row_entropy_increase": 25,
    "negative_row_entropy_increase": 26,
    "central_offdiag_entropy_contribution": 27,
    "high_offdiag_entropy_contribution": 28,
    "self_entropy_contribution": 29,
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
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def entropy_row(probabilities: list[Fraction]) -> float:
    entropy = 0.0
    for probability in probabilities:
        p = float(probability)
        if p > 0.0:
            entropy -= p * math.log(p)
    return entropy


def weighted_entropy_term(stationary_mass: int, probability: Fraction) -> float:
    p = float(probability)
    if p <= 0.0:
        return 0.0
    return float(Fraction(stationary_mass, PROBABILITY_SCALE)) * (-(p * math.log(p)))


def build_payloads() -> dict[str, Any]:
    boundary_report = load_json(BOUNDARY_FLUX_REPORT)
    boundary_flux = load_json(BOUNDARY_FLUX_JSON)
    boundary_certificate = load_json(BOUNDARY_FLUX_CERTIFICATE)
    quotient_report = load_json(QUOTIENT_REPORT)
    quotient = load_json(QUOTIENT_JSON)
    quotient_certificate = load_json(QUOTIENT_CERTIFICATE)
    boundary_tables = np.load(BOUNDARY_FLUX_TABLES, allow_pickle=False)
    quotient_tables = np.load(QUOTIENT_TABLES, allow_pickle=False)

    partition_rows_in = {
        int(row["boundary_partition_code"]): row
        for row in boundary_flux["partition_summary"]
    }
    high_partition = partition_rows_in[EDGE_HIGH_NEGATIVE]
    central_partition = partition_rows_in[EDGE_CENTRAL_NEGATIVE]

    high_flux = int(high_partition["undirected_stationary_flux_x1e12"])
    central_flux = int(central_partition["undirected_stationary_flux_x1e12"])
    cut_flux = high_flux + central_flux

    positive_mass = int(quotient_report["witness"]["positive_stationary_mass_x1e12"])
    negative_mass = int(quotient_report["witness"]["negative_stationary_mass_x1e12"])
    positive_exit = Fraction(cut_flux, 2 * positive_mass)
    negative_exit = Fraction(cut_flux, 2 * negative_mass)
    positive_high = Fraction(high_flux, 2 * positive_mass)
    positive_central = Fraction(central_flux, 2 * positive_mass)
    negative_high = Fraction(high_flux, 2 * negative_mass)
    negative_central = Fraction(central_flux, 2 * negative_mass)

    positive_binary_row = scaled_probability_row([1 - positive_exit, positive_exit])
    negative_binary_row = scaled_probability_row([negative_exit, 1 - negative_exit])
    positive_refined_row = scaled_probability_row(
        [1 - positive_high - positive_central, positive_high, positive_central]
    )
    negative_refined_row = scaled_probability_row(
        [negative_high, negative_central, 1 - negative_high - negative_central]
    )

    high_fraction = Fraction(high_flux, cut_flux)
    central_fraction = Fraction(central_flux, cut_flux)

    positive_binary_entropy = entropy_row([1 - positive_exit, positive_exit])
    negative_binary_entropy = entropy_row([negative_exit, 1 - negative_exit])
    positive_refined_entropy = entropy_row(
        [1 - positive_high - positive_central, positive_high, positive_central]
    )
    negative_refined_entropy = entropy_row(
        [negative_high, negative_central, 1 - negative_high - negative_central]
    )
    quotient_entropy_rate = (
        (positive_mass / PROBABILITY_SCALE) * positive_binary_entropy
        + (negative_mass / PROBABILITY_SCALE) * negative_binary_entropy
    )
    refined_entropy_rate = (
        (positive_mass / PROBABILITY_SCALE) * positive_refined_entropy
        + (negative_mass / PROBABILITY_SCALE) * negative_refined_entropy
    )
    boundary_split_entropy = entropy_row([high_fraction, central_fraction])
    entropy_refinement_surplus = (
        (cut_flux / PROBABILITY_SCALE) * boundary_split_entropy
    )

    positive_self_entropy = weighted_entropy_term(
        positive_mass,
        1 - positive_high - positive_central,
    )
    positive_high_entropy = weighted_entropy_term(positive_mass, positive_high)
    positive_central_entropy = weighted_entropy_term(positive_mass, positive_central)
    negative_high_entropy = weighted_entropy_term(negative_mass, negative_high)
    negative_central_entropy = weighted_entropy_term(negative_mass, negative_central)
    negative_self_entropy = weighted_entropy_term(
        negative_mass,
        1 - negative_high - negative_central,
    )

    high_entropy_contribution = positive_high_entropy + negative_high_entropy
    central_entropy_contribution = positive_central_entropy + negative_central_entropy
    self_entropy_contribution = positive_self_entropy + negative_self_entropy

    partition_rows = [
        {
            "boundary_partition_code": EDGE_HIGH_NEGATIVE,
            "partition_order": 0,
            "mask_edge_count": int(high_partition["mask_edge_count"]),
            "signature_cut_edge_count": int(high_partition["signature_cut_edge_count"]),
            "undirected_stationary_flux_x1e12": high_flux,
            "flux_fraction_of_total_cut_x1e12": round_fraction(high_fraction),
            "positive_to_negative_probability_contribution_x1e12": positive_refined_row[1],
            "negative_to_positive_probability_contribution_x1e12": negative_refined_row[0],
            "positive_exit_share_x1e12": round_fraction(high_fraction),
            "negative_exit_share_x1e12": round_fraction(high_fraction),
            "positive_entropy_contribution_x1e12": scaled_float(positive_high_entropy),
            "negative_entropy_contribution_x1e12": scaled_float(negative_high_entropy),
            "refined_entropy_contribution_x1e12": scaled_float(high_entropy_contribution),
        },
        {
            "boundary_partition_code": EDGE_CENTRAL_NEGATIVE,
            "partition_order": 1,
            "mask_edge_count": int(central_partition["mask_edge_count"]),
            "signature_cut_edge_count": int(
                central_partition["signature_cut_edge_count"]
            ),
            "undirected_stationary_flux_x1e12": central_flux,
            "flux_fraction_of_total_cut_x1e12": round_fraction(central_fraction),
            "positive_to_negative_probability_contribution_x1e12": positive_refined_row[2],
            "negative_to_positive_probability_contribution_x1e12": negative_refined_row[1],
            "positive_exit_share_x1e12": round_fraction(central_fraction),
            "negative_exit_share_x1e12": round_fraction(central_fraction),
            "positive_entropy_contribution_x1e12": scaled_float(
                positive_central_entropy
            ),
            "negative_entropy_contribution_x1e12": scaled_float(
                negative_central_entropy
            ),
            "refined_entropy_contribution_x1e12": scaled_float(
                central_entropy_contribution
            ),
        },
    ]

    transition_rows = [
        {
            "event_id": 0,
            "source_state_id": 0,
            "target_state_id": 0,
            "source_nodal_sign": 1,
            "target_nodal_sign": 1,
            "event_role_code": 0,
            "boundary_partition_code": -1,
            "transition_probability_x1e12": positive_refined_row[0],
            "stationary_flow_twice_x1e12": 2 * positive_mass - cut_flux,
            "is_crossing": 0,
        },
        {
            "event_id": 1,
            "source_state_id": 0,
            "target_state_id": 1,
            "source_nodal_sign": 1,
            "target_nodal_sign": -1,
            "event_role_code": EDGE_HIGH_NEGATIVE,
            "boundary_partition_code": EDGE_HIGH_NEGATIVE,
            "transition_probability_x1e12": positive_refined_row[1],
            "stationary_flow_twice_x1e12": high_flux,
            "is_crossing": 1,
        },
        {
            "event_id": 2,
            "source_state_id": 0,
            "target_state_id": 1,
            "source_nodal_sign": 1,
            "target_nodal_sign": -1,
            "event_role_code": EDGE_CENTRAL_NEGATIVE,
            "boundary_partition_code": EDGE_CENTRAL_NEGATIVE,
            "transition_probability_x1e12": positive_refined_row[2],
            "stationary_flow_twice_x1e12": central_flux,
            "is_crossing": 1,
        },
        {
            "event_id": 3,
            "source_state_id": 1,
            "target_state_id": 0,
            "source_nodal_sign": -1,
            "target_nodal_sign": 1,
            "event_role_code": EDGE_HIGH_NEGATIVE,
            "boundary_partition_code": EDGE_HIGH_NEGATIVE,
            "transition_probability_x1e12": negative_refined_row[0],
            "stationary_flow_twice_x1e12": high_flux,
            "is_crossing": 1,
        },
        {
            "event_id": 4,
            "source_state_id": 1,
            "target_state_id": 0,
            "source_nodal_sign": -1,
            "target_nodal_sign": 1,
            "event_role_code": EDGE_CENTRAL_NEGATIVE,
            "boundary_partition_code": EDGE_CENTRAL_NEGATIVE,
            "transition_probability_x1e12": negative_refined_row[1],
            "stationary_flow_twice_x1e12": central_flux,
            "is_crossing": 1,
        },
        {
            "event_id": 5,
            "source_state_id": 1,
            "target_state_id": 1,
            "source_nodal_sign": -1,
            "target_nodal_sign": -1,
            "event_role_code": 0,
            "boundary_partition_code": -1,
            "transition_probability_x1e12": negative_refined_row[2],
            "stationary_flow_twice_x1e12": 2 * negative_mass - cut_flux,
            "is_crossing": 0,
        },
    ]

    entropy_rows = [
        {
            "term_id": 0,
            "source_state_id": 0,
            "event_role_code": 0,
            "boundary_partition_code": -1,
            "probability_x1e12": positive_refined_row[0],
            "stationary_mass_x1e12": positive_mass,
            "weighted_entropy_contribution_x1e12": scaled_float(positive_self_entropy),
        },
        {
            "term_id": 1,
            "source_state_id": 0,
            "event_role_code": EDGE_HIGH_NEGATIVE,
            "boundary_partition_code": EDGE_HIGH_NEGATIVE,
            "probability_x1e12": positive_refined_row[1],
            "stationary_mass_x1e12": positive_mass,
            "weighted_entropy_contribution_x1e12": scaled_float(positive_high_entropy),
        },
        {
            "term_id": 2,
            "source_state_id": 0,
            "event_role_code": EDGE_CENTRAL_NEGATIVE,
            "boundary_partition_code": EDGE_CENTRAL_NEGATIVE,
            "probability_x1e12": positive_refined_row[2],
            "stationary_mass_x1e12": positive_mass,
            "weighted_entropy_contribution_x1e12": scaled_float(
                positive_central_entropy
            ),
        },
        {
            "term_id": 3,
            "source_state_id": 1,
            "event_role_code": EDGE_HIGH_NEGATIVE,
            "boundary_partition_code": EDGE_HIGH_NEGATIVE,
            "probability_x1e12": negative_refined_row[0],
            "stationary_mass_x1e12": negative_mass,
            "weighted_entropy_contribution_x1e12": scaled_float(negative_high_entropy),
        },
        {
            "term_id": 4,
            "source_state_id": 1,
            "event_role_code": EDGE_CENTRAL_NEGATIVE,
            "boundary_partition_code": EDGE_CENTRAL_NEGATIVE,
            "probability_x1e12": negative_refined_row[1],
            "stationary_mass_x1e12": negative_mass,
            "weighted_entropy_contribution_x1e12": scaled_float(
                negative_central_entropy
            ),
        },
        {
            "term_id": 5,
            "source_state_id": 1,
            "event_role_code": 0,
            "boundary_partition_code": -1,
            "probability_x1e12": negative_refined_row[2],
            "stationary_mass_x1e12": negative_mass,
            "weighted_entropy_contribution_x1e12": scaled_float(negative_self_entropy),
        },
    ]

    observable_values = {
        "state_count": 2,
        "boundary_partition_count": len(partition_rows),
        "positive_stationary_mass": positive_mass,
        "negative_stationary_mass": negative_mass,
        "total_undirected_cut_flux": cut_flux,
        "high_negative_undirected_cut_flux": high_flux,
        "central_negative_undirected_cut_flux": central_flux,
        "high_negative_flux_fraction": round_fraction(high_fraction),
        "central_negative_flux_fraction": round_fraction(central_fraction),
        "positive_to_negative_probability": positive_binary_row[1],
        "negative_to_positive_probability": negative_binary_row[0],
        "positive_high_negative_probability": positive_refined_row[1],
        "positive_central_negative_probability": positive_refined_row[2],
        "negative_high_negative_probability": negative_refined_row[0],
        "negative_central_negative_probability": negative_refined_row[1],
        "positive_self_refined_probability": positive_refined_row[0],
        "negative_self_refined_probability": negative_refined_row[2],
        "central_share_of_positive_exit": round_fraction(central_fraction),
        "central_share_of_negative_exit": round_fraction(central_fraction),
        "quotient_entropy_rate": scaled_float(quotient_entropy_rate),
        "refined_boundary_entropy_rate": scaled_float(refined_entropy_rate),
        "entropy_refinement_surplus": scaled_float(entropy_refinement_surplus),
        "boundary_split_entropy": scaled_float(boundary_split_entropy),
        "positive_refined_row_entropy": scaled_float(positive_refined_entropy),
        "negative_refined_row_entropy": scaled_float(negative_refined_entropy),
        "positive_row_entropy_increase": scaled_float(
            positive_refined_entropy - positive_binary_entropy
        ),
        "negative_row_entropy_increase": scaled_float(
            negative_refined_entropy - negative_binary_entropy
        ),
        "central_offdiag_entropy_contribution": scaled_float(
            central_entropy_contribution
        ),
        "high_offdiag_entropy_contribution": scaled_float(high_entropy_contribution),
        "self_entropy_contribution": scaled_float(self_entropy_contribution),
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

    partition_table = table_from_rows(BOUNDARY_RATE_PARTITION_COLUMNS, partition_rows)
    refined_transition_table = table_from_rows(
        BOUNDARY_REFINED_TRANSITION_COLUMNS,
        transition_rows,
    )
    entropy_term_table = table_from_rows(BOUNDARY_ENTROPY_TERM_COLUMNS, entropy_rows)
    observable_table = table_from_rows(BOUNDARY_RATE_OBSERVABLE_COLUMNS, observable_rows)

    exact_partition_reversibility = [
        Fraction(positive_mass, PROBABILITY_SCALE) * Fraction(flux, 2 * positive_mass)
        == Fraction(negative_mass, PROBABILITY_SCALE)
        * Fraction(flux, 2 * negative_mass)
        == Fraction(flux, 2 * PROBABILITY_SCALE)
        for flux in (high_flux, central_flux)
    ]
    positive_row_flow_sum = (
        int(transition_rows[0]["stationary_flow_twice_x1e12"])
        + int(transition_rows[1]["stationary_flow_twice_x1e12"])
        + int(transition_rows[2]["stationary_flow_twice_x1e12"])
    )
    negative_row_flow_sum = (
        int(transition_rows[3]["stationary_flow_twice_x1e12"])
        + int(transition_rows[4]["stationary_flow_twice_x1e12"])
        + int(transition_rows[5]["stationary_flow_twice_x1e12"])
    )

    rate_readout = {
        "schema": "c985.d20_signature_boundary_flux_quotient_rates@1",
        "object": "d20",
        "rate_rule": {
            "source": "certified boundary flux cells over the certified two-state spectral quotient",
            "states": "positive and negative nodal sides",
            "refinement": "split each off-diagonal quotient transition into high-negative and central-negative boundary contacts",
            "transition_law": "partition twice-flow divided by twice the source stationary mass",
            "rounding_boundary": "per-source refined rows use largest-remainder allocation so rows sum exactly to 1e12",
            "entropy_comparison": "compare the original two-outcome quotient row entropy with the refined self/high/central row entropy",
        },
        "stationary_distribution_x1e12": [positive_mass, negative_mass],
        "boundary_partition_rates": [
            {key: int(value) for key, value in row.items()} for row in partition_rows
        ],
        "refined_transition_rows": [
            {key: int(value) for key, value in row.items()} for row in transition_rows
        ],
        "entropy_summary": {
            "quotient_entropy_rate_x1e12": observable_values["quotient_entropy_rate"],
            "refined_boundary_entropy_rate_x1e12": observable_values[
                "refined_boundary_entropy_rate"
            ],
            "entropy_refinement_surplus_x1e12": observable_values[
                "entropy_refinement_surplus"
            ],
            "boundary_split_entropy_x1e12": observable_values[
                "boundary_split_entropy"
            ],
            "positive_refined_row_entropy_x1e12": observable_values[
                "positive_refined_row_entropy"
            ],
            "negative_refined_row_entropy_x1e12": observable_values[
                "negative_refined_row_entropy"
            ],
            "central_offdiag_entropy_contribution_x1e12": observable_values[
                "central_offdiag_entropy_contribution"
            ],
            "high_offdiag_entropy_contribution_x1e12": observable_values[
                "high_offdiag_entropy_contribution"
            ],
            "self_entropy_contribution_x1e12": observable_values[
                "self_entropy_contribution"
            ],
        },
    }

    checks = {
        "boundary_flux_report_certified": boundary_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_FLUX_CELLS_CERTIFIED",
        "boundary_flux_certificate_certified": boundary_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_FLUX_CELLS_CERTIFIED",
        "quotient_report_certified": quotient_report.get("status")
        == "C985_D20_SIGNATURE_SPECTRAL_QUOTIENT_DYNAMICS_CERTIFIED",
        "quotient_certificate_certified": quotient_certificate.get("status")
        == "C985_D20_SIGNATURE_SPECTRAL_QUOTIENT_DYNAMICS_CERTIFIED",
        "state_count_is_2": len(quotient["states"]) == 2,
        "boundary_partition_count_is_2": len(partition_rows) == 2,
        "boundary_flux_total_matches_quotient_cut_flux": cut_flux
        == int(quotient_report["witness"]["undirected_cut_flux_x1e12"])
        == 238962451389,
        "boundary_partition_codes_match_expected": [row["boundary_partition_code"] for row in partition_rows]
        == [EDGE_HIGH_NEGATIVE, EDGE_CENTRAL_NEGATIVE],
        "high_negative_flux_matches_expected": high_flux == 3712054656,
        "central_negative_flux_matches_expected": central_flux == 235250396733,
        "boundary_flux_fractions_match_expected": (
            observable_values["high_negative_flux_fraction"],
            observable_values["central_negative_flux_fraction"],
        )
        == (15534049950, 984465950050),
        "positive_refined_row_sums_to_one": sum(positive_refined_row)
        == PROBABILITY_SCALE,
        "negative_refined_row_sums_to_one": sum(negative_refined_row)
        == PROBABILITY_SCALE,
        "positive_partition_exits_sum_to_quotient_exit": positive_refined_row[1]
        + positive_refined_row[2]
        == positive_binary_row[1]
        == 190831926563,
        "negative_partition_exits_sum_to_quotient_exit": negative_refined_row[0]
        + negative_refined_row[1]
        == negative_binary_row[0]
        == 319560035288,
        "refined_self_probabilities_match_quotient_returns": positive_refined_row[0]
        == positive_binary_row[0]
        == 809168073437
        and negative_refined_row[2] == negative_binary_row[1] == 680439964712,
        "central_accounts_for_same_share_both_directions": observable_values[
            "central_share_of_positive_exit"
        ]
        == observable_values["central_share_of_negative_exit"]
        == 984465950050,
        "partition_flow_reversibility_holds_exactly": all(
            exact_partition_reversibility
        ),
        "refined_twice_flows_sum_to_source_twice_masses": positive_row_flow_sum
        == 2 * positive_mass
        and negative_row_flow_sum == 2 * negative_mass,
        "quotient_entropy_rate_matches_upstream": observable_values[
            "quotient_entropy_rate"
        ]
        == int(quotient_report["witness"]["entropy_rate_x1e12"])
        == 539439395042,
        "refined_entropy_rate_matches_expected": observable_values[
            "refined_boundary_entropy_rate"
        ]
        == 558582139199,
        "entropy_refinement_surplus_matches_split_formula": observable_values[
            "entropy_refinement_surplus"
        ]
        == 19142744157,
        "refined_entropy_exceeds_quotient_entropy": observable_values[
            "refined_boundary_entropy_rate"
        ]
        > observable_values["quotient_entropy_rate"],
        "partition_table_shape_is_2_by_13": tuple(partition_table.shape)
        == (2, len(BOUNDARY_RATE_PARTITION_COLUMNS)),
        "refined_transition_table_shape_is_6_by_10": tuple(
            refined_transition_table.shape
        )
        == (6, len(BOUNDARY_REFINED_TRANSITION_COLUMNS)),
        "entropy_term_table_shape_is_6_by_7": tuple(entropy_term_table.shape)
        == (6, len(BOUNDARY_ENTROPY_TERM_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(BOUNDARY_RATE_OBSERVABLE_COLUMNS)),
        "boundary_flux_json_schema_available": boundary_flux.get("schema")
        == "c985.d20_signature_boundary_flux_cells@1",
        "quotient_json_schema_available": quotient.get("schema")
        == "c985.d20_signature_spectral_quotient_dynamics@1",
        "boundary_flux_tables_available": "boundary_partition_table"
        in boundary_tables.files,
        "quotient_tables_available": "quotient_transition_table"
        in quotient_tables.files,
    }

    witness = {
        "positive_stationary_mass_x1e12": positive_mass,
        "negative_stationary_mass_x1e12": negative_mass,
        "total_undirected_cut_flux_x1e12": cut_flux,
        "high_negative_undirected_cut_flux_x1e12": high_flux,
        "central_negative_undirected_cut_flux_x1e12": central_flux,
        "high_negative_flux_fraction_x1e12": observable_values[
            "high_negative_flux_fraction"
        ],
        "central_negative_flux_fraction_x1e12": observable_values[
            "central_negative_flux_fraction"
        ],
        "positive_boundary_exit_decomposition_x1e12": {
            "self": positive_refined_row[0],
            "high_negative": positive_refined_row[1],
            "central_negative": positive_refined_row[2],
        },
        "negative_boundary_exit_decomposition_x1e12": {
            "high_negative": negative_refined_row[0],
            "central_negative": negative_refined_row[1],
            "self": negative_refined_row[2],
        },
        "central_negative_transition_share_x1e12": observable_values[
            "central_share_of_positive_exit"
        ],
        "quotient_entropy_rate_x1e12": observable_values["quotient_entropy_rate"],
        "refined_boundary_entropy_rate_x1e12": observable_values[
            "refined_boundary_entropy_rate"
        ],
        "entropy_refinement_surplus_x1e12": observable_values[
            "entropy_refinement_surplus"
        ],
        "boundary_split_entropy_x1e12": observable_values["boundary_split_entropy"],
        "positive_refined_row_entropy_x1e12": observable_values[
            "positive_refined_row_entropy"
        ],
        "negative_refined_row_entropy_x1e12": observable_values[
            "negative_refined_row_entropy"
        ],
        "central_offdiag_entropy_contribution_x1e12": observable_values[
            "central_offdiag_entropy_contribution"
        ],
        "high_offdiag_entropy_contribution_x1e12": observable_values[
            "high_offdiag_entropy_contribution"
        ],
        "self_entropy_contribution_x1e12": observable_values[
            "self_entropy_contribution"
        ],
        "boundary_rate_partition_table_sha256": sha_array(partition_table),
        "boundary_refined_transition_table_sha256": sha_array(
            refined_transition_table
        ),
        "boundary_entropy_term_table_sha256": sha_array(entropy_term_table),
        "boundary_rate_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_flux_quotient_rates_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_FLUX_QUOTIENT_RATES_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the boundary flux partitions refine the quotient off-diagonal transitions without changing the self probabilities",
            "central-negative contacts account for 0.984465950050 of both positive-to-negative and negative-to-positive exit probability",
            "the central-negative rate contributions are 0.187867533884 from positive to negative and 0.314595973738 from negative to positive",
            "the high-negative rate contributions are 0.002964392679 from positive to negative and 0.004964061550 from negative to positive",
            "refining the quotient crossing event by boundary contact raises entropy rate from 0.539439395042 to 0.558582139199",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_flux_quotient_rates@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified residual boundary flux refines the two-state spectral "
            "quotient transitions: central-negative conductance supplies almost "
            "all off-diagonal rate in both directions, while the refined "
            "self/high/central event alphabet adds a measured entropy surplus "
            "over the binary quotient."
        ),
        "stage_protocol": {
            "draft": "split quotient off-diagonal transitions by certified high-negative and central-negative boundary flux",
            "witness": "materialize refined transition rows, partition rate contributions, and entropy terms",
            "coherence": "check row sums, exact partition reversibility, upstream cut flux, and entropy comparison",
            "closure": "certify the finite boundary-rate refinement without claiming a continuum transition mechanism",
            "emit": "emit boundary-rate JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "boundary_flux_report": input_entry(
                BOUNDARY_FLUX_REPORT,
                {
                    "status": boundary_report.get("status"),
                    "certificate_sha256": boundary_report.get("certificate_sha256"),
                },
            ),
            "boundary_flux": input_entry(BOUNDARY_FLUX_JSON),
            "boundary_flux_tables": input_entry(BOUNDARY_FLUX_TABLES),
            "boundary_flux_certificate": input_entry(BOUNDARY_FLUX_CERTIFICATE),
            "boundary_partition_summary": input_entry(BOUNDARY_PARTITION_SUMMARY),
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
            "quotient_states": input_entry(QUOTIENT_STATES),
            "quotient_transitions": input_entry(QUOTIENT_TRANSITIONS),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_flux_quotient_rates": relpath(
                OUT_DIR / "signature_boundary_flux_quotient_rates.json"
            ),
            "boundary_rate_partitions_csv": relpath(
                OUT_DIR / "boundary_rate_partitions.csv"
            ),
            "boundary_refined_transition_rows_csv": relpath(
                OUT_DIR / "boundary_refined_transition_rows.csv"
            ),
            "boundary_entropy_terms_csv": relpath(
                OUT_DIR / "boundary_entropy_terms.csv"
            ),
            "boundary_rate_observables_csv": relpath(
                OUT_DIR / "boundary_rate_observables.csv"
            ),
            "signature_boundary_flux_quotient_rates_tables": relpath(
                OUT_DIR / "signature_boundary_flux_quotient_rates_tables.npz"
            ),
            "signature_boundary_flux_quotient_rates_certificate": relpath(
                OUT_DIR / "signature_boundary_flux_quotient_rates_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "rate decomposition of both quotient off-diagonal transitions by residual boundary partition",
                "exact stationarity/reversibility of each partition flow at twice-flow scale",
                "that central-negative flux supplies the same 0.984465950050 share of both directional exit rates",
                "entropy comparison between the binary quotient and the refined boundary-contact event alphabet",
            ],
            "does_not_certify_because_not_required": [
                "a continuum conductance equation or mixing-time bound",
                "that high-negative and central-negative contacts are the only meaningful refinements outside this certified residual chart",
                "higher-eigenmode rate decompositions",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the refined boundary-rate alphabet as the next geometric read: "
            "lift high-negative and central-negative rate mass back onto the "
            "residual cell-complex edges and certify a directed conductance "
            "spine ordered by entropy contribution."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_flux_quotient_rates_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified boundary-flux and two-state quotient artifacts",
            "split quotient off-diagonal transition probabilities by certified boundary flux partitions",
            "verify exact partition reversibility and row-stochastic refined transitions",
            "compare binary quotient entropy with refined self/high/central boundary-contact entropy",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_flux_quotient_rates": rate_readout,
        "boundary_rate_partitions_csv": csv_text(
            BOUNDARY_RATE_PARTITION_COLUMNS,
            partition_rows,
        ),
        "boundary_refined_transition_rows_csv": csv_text(
            BOUNDARY_REFINED_TRANSITION_COLUMNS,
            transition_rows,
        ),
        "boundary_entropy_terms_csv": csv_text(
            BOUNDARY_ENTROPY_TERM_COLUMNS,
            entropy_rows,
        ),
        "boundary_rate_observables_csv": csv_text(
            BOUNDARY_RATE_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "boundary_rate_partition_table": partition_table,
        "boundary_refined_transition_table": refined_transition_table,
        "boundary_entropy_term_table": entropy_term_table,
        "boundary_rate_observable_table": observable_table,
        "signature_boundary_flux_quotient_rates_certificate": certificate,
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
        OUT_DIR / "signature_boundary_flux_quotient_rates.json",
        payloads["signature_boundary_flux_quotient_rates"],
    )
    (OUT_DIR / "boundary_rate_partitions.csv").write_text(
        payloads["boundary_rate_partitions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_refined_transition_rows.csv").write_text(
        payloads["boundary_refined_transition_rows_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_entropy_terms.csv").write_text(
        payloads["boundary_entropy_terms_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_rate_observables.csv").write_text(
        payloads["boundary_rate_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_flux_quotient_rates_tables.npz",
        boundary_rate_partition_table=payloads["boundary_rate_partition_table"],
        boundary_refined_transition_table=payloads[
            "boundary_refined_transition_table"
        ],
        boundary_entropy_term_table=payloads["boundary_entropy_term_table"],
        boundary_rate_observable_table=payloads["boundary_rate_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_flux_quotient_rates_certificate.json",
        payloads["signature_boundary_flux_quotient_rates_certificate"],
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
                "positive_boundary_exit_decomposition_x1e12": witness[
                    "positive_boundary_exit_decomposition_x1e12"
                ],
                "negative_boundary_exit_decomposition_x1e12": witness[
                    "negative_boundary_exit_decomposition_x1e12"
                ],
                "refined_boundary_entropy_rate_x1e12": witness[
                    "refined_boundary_entropy_rate_x1e12"
                ],
                "entropy_refinement_surplus_x1e12": witness[
                    "entropy_refinement_surplus_x1e12"
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
