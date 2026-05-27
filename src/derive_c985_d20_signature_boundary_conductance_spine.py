from __future__ import annotations

import csv
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
    from .derive_c985_d20_signature_boundary_flux_quotient_rates import (
        OUT_DIR as BOUNDARY_RATE_DIR,
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
    from derive_c985_d20_signature_boundary_flux_quotient_rates import (
        OUT_DIR as BOUNDARY_RATE_DIR,
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


THEOREM_ID = "c985_d20_signature_boundary_conductance_spine"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_CONDUCTANCE_SPINE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

BOUNDARY_FLUX_REPORT = BOUNDARY_FLUX_DIR / "report.json"
BOUNDARY_FLUX_JSON = BOUNDARY_FLUX_DIR / "signature_boundary_flux_cells.json"
BOUNDARY_FLUX_TABLES = BOUNDARY_FLUX_DIR / "signature_boundary_flux_cells_tables.npz"
BOUNDARY_FLUX_CERTIFICATE = (
    BOUNDARY_FLUX_DIR / "signature_boundary_flux_cells_certificate.json"
)
BOUNDARY_MASK_EDGES = BOUNDARY_FLUX_DIR / "boundary_mask_edges.csv"

BOUNDARY_RATE_REPORT = BOUNDARY_RATE_DIR / "report.json"
BOUNDARY_RATE_JSON = BOUNDARY_RATE_DIR / "signature_boundary_flux_quotient_rates.json"
BOUNDARY_RATE_TABLES = (
    BOUNDARY_RATE_DIR / "signature_boundary_flux_quotient_rates_tables.npz"
)
BOUNDARY_RATE_CERTIFICATE = (
    BOUNDARY_RATE_DIR / "signature_boundary_flux_quotient_rates_certificate.json"
)
BOUNDARY_RATE_PARTITIONS = BOUNDARY_RATE_DIR / "boundary_rate_partitions.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_signature_boundary_conductance_spine.py"
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_conductance_spine.py"
)

PROBABILITY_SCALE = 1_000_000_000_000

CONDUCTANCE_SPINE_EDGE_COLUMNS = [
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "positive_carrier_mask_class_id",
    "negative_carrier_mask_class_id",
    "positive_region_code",
    "negative_region_code",
    "boundary_partition_code",
    "signature_cut_edge_count",
    "undirected_stationary_flux_x1e12",
    "flux_fraction_of_total_cut_x1e12",
    "positive_to_negative_probability_x1e12",
    "negative_to_positive_probability_x1e12",
    "positive_entropy_contribution_x1e12",
    "negative_entropy_contribution_x1e12",
    "total_entropy_contribution_x1e12",
    "cumulative_flux_x1e12",
    "cumulative_entropy_contribution_x1e12",
]

CONDUCTANCE_DIRECTED_EDGE_COLUMNS = [
    "directed_edge_id",
    "boundary_spine_rank",
    "boundary_mask_edge_id",
    "source_state_id",
    "target_state_id",
    "source_nodal_sign",
    "target_nodal_sign",
    "source_carrier_mask_class_id",
    "target_carrier_mask_class_id",
    "boundary_partition_code",
    "transition_probability_x1e12",
    "stationary_flow_twice_x1e12",
    "entropy_contribution_x1e12",
]

CONDUCTANCE_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "state_count": 0,
    "boundary_edge_count": 1,
    "directed_boundary_edge_count": 2,
    "total_undirected_cut_flux": 3,
    "top_spine_edge_id": 4,
    "top_spine_edge_flux": 5,
    "top_spine_edge_entropy": 6,
    "top_five_spine_flux": 7,
    "top_five_spine_entropy": 8,
    "top_five_flux_fraction": 9,
    "top_five_entropy_fraction_of_boundary_crossing": 10,
    "high_negative_boundary_edge_count": 11,
    "central_negative_boundary_edge_count": 12,
    "high_negative_edge_entropy": 13,
    "central_negative_edge_entropy": 14,
    "high_negative_entropy_fraction_of_boundary_crossing": 15,
    "central_negative_entropy_fraction_of_boundary_crossing": 16,
    "positive_boundary_probability_sum": 17,
    "negative_boundary_probability_sum": 18,
    "positive_edge_refined_row_entropy": 19,
    "negative_edge_refined_row_entropy": 20,
    "edge_refined_entropy_rate": 21,
    "partition_refined_entropy_rate": 22,
    "quotient_entropy_rate": 23,
    "edge_entropy_surplus_over_partition": 24,
    "edge_entropy_surplus_over_quotient": 25,
    "self_entropy_contribution": 26,
    "boundary_edge_entropy_contribution_sum": 27,
    "entropy_rounding_delta": 28,
}


def scaled_float(value: float) -> int:
    return int(round(float(value) * PROBABILITY_SCALE))


def scaled_ratio(numerator: int, denominator: int) -> int:
    scaled = int(numerator) * PROBABILITY_SCALE
    quotient, remainder = divmod(scaled, int(denominator))
    if 2 * remainder >= int(denominator):
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


def read_int_csv(path: Any) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({key: int(value) for key, value in row.items()})
    return rows


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


def positive_negative_endpoints(row: dict[str, int]) -> tuple[int, int, int, int]:
    source_region = int(row["source_region_code"])
    target_region = int(row["target_region_code"])
    source_mask = int(row["source_carrier_mask_class_id"])
    target_mask = int(row["target_carrier_mask_class_id"])
    if source_region > 0 and target_region == -1:
        return source_mask, target_mask, source_region, target_region
    if target_region > 0 and source_region == -1:
        return target_mask, source_mask, target_region, source_region
    raise ValueError(
        f"boundary edge {row['boundary_mask_edge_id']} is not positive-negative"
    )


def build_payloads() -> dict[str, Any]:
    boundary_flux_report = load_json(BOUNDARY_FLUX_REPORT)
    boundary_flux = load_json(BOUNDARY_FLUX_JSON)
    boundary_flux_certificate = load_json(BOUNDARY_FLUX_CERTIFICATE)
    boundary_rate_report = load_json(BOUNDARY_RATE_REPORT)
    boundary_rate = load_json(BOUNDARY_RATE_JSON)
    boundary_rate_certificate = load_json(BOUNDARY_RATE_CERTIFICATE)
    boundary_flux_tables = np.load(BOUNDARY_FLUX_TABLES, allow_pickle=False)
    boundary_rate_tables = np.load(BOUNDARY_RATE_TABLES, allow_pickle=False)

    mask_edge_rows_in = read_int_csv(BOUNDARY_MASK_EDGES)
    positive_mass = int(boundary_rate_report["witness"]["positive_stationary_mass_x1e12"])
    negative_mass = int(boundary_rate_report["witness"]["negative_stationary_mass_x1e12"])
    cut_flux = int(sum(row["undirected_stationary_flux_x1e12"] for row in mask_edge_rows_in))

    positive_probabilities = [1 - Fraction(cut_flux, 2 * positive_mass)] + [
        Fraction(row["undirected_stationary_flux_x1e12"], 2 * positive_mass)
        for row in mask_edge_rows_in
    ]
    negative_probabilities = [
        Fraction(row["undirected_stationary_flux_x1e12"], 2 * negative_mass)
        for row in mask_edge_rows_in
    ] + [1 - Fraction(cut_flux, 2 * negative_mass)]
    positive_scaled_row = scaled_probability_row(positive_probabilities)
    negative_scaled_row = scaled_probability_row(negative_probabilities)

    positive_edge_row_entropy = entropy_row(positive_probabilities)
    negative_edge_row_entropy = entropy_row(negative_probabilities)
    edge_refined_entropy_rate = (
        (positive_mass / PROBABILITY_SCALE) * positive_edge_row_entropy
        + (negative_mass / PROBABILITY_SCALE) * negative_edge_row_entropy
    )

    positive_self_entropy = weighted_entropy_term(
        positive_mass,
        positive_probabilities[0],
    )
    negative_self_entropy = weighted_entropy_term(
        negative_mass,
        negative_probabilities[-1],
    )
    self_entropy_contribution = scaled_float(positive_self_entropy) + scaled_float(
        negative_self_entropy
    )

    unranked_edge_rows: list[dict[str, int]] = []
    for source_index, row in enumerate(mask_edge_rows_in):
        edge_flux = int(row["undirected_stationary_flux_x1e12"])
        positive_probability = Fraction(edge_flux, 2 * positive_mass)
        negative_probability = Fraction(edge_flux, 2 * negative_mass)
        positive_entropy = weighted_entropy_term(positive_mass, positive_probability)
        negative_entropy = weighted_entropy_term(negative_mass, negative_probability)
        total_entropy = positive_entropy + negative_entropy
        (
            positive_mask,
            negative_mask,
            positive_region,
            negative_region,
        ) = positive_negative_endpoints(row)
        unranked_edge_rows.append(
            {
                "boundary_spine_rank": -1,
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "source_carrier_mask_class_id": int(
                    row["source_carrier_mask_class_id"]
                ),
                "target_carrier_mask_class_id": int(
                    row["target_carrier_mask_class_id"]
                ),
                "positive_carrier_mask_class_id": positive_mask,
                "negative_carrier_mask_class_id": negative_mask,
                "positive_region_code": positive_region,
                "negative_region_code": negative_region,
                "boundary_partition_code": int(row["boundary_partition_code"]),
                "signature_cut_edge_count": int(row["signature_cut_edge_count"]),
                "undirected_stationary_flux_x1e12": edge_flux,
                "flux_fraction_of_total_cut_x1e12": int(
                    row["flux_fraction_of_total_cut_x1e12"]
                ),
                "positive_to_negative_probability_x1e12": positive_scaled_row[
                    source_index + 1
                ],
                "negative_to_positive_probability_x1e12": negative_scaled_row[
                    source_index
                ],
                "positive_entropy_contribution_x1e12": scaled_float(
                    positive_entropy
                ),
                "negative_entropy_contribution_x1e12": scaled_float(
                    negative_entropy
                ),
                "total_entropy_contribution_x1e12": scaled_float(total_entropy),
                "cumulative_flux_x1e12": 0,
                "cumulative_entropy_contribution_x1e12": 0,
            }
        )

    edge_rows = sorted(
        unranked_edge_rows,
        key=lambda row: (
            -int(row["total_entropy_contribution_x1e12"]),
            -int(row["undirected_stationary_flux_x1e12"]),
            int(row["boundary_mask_edge_id"]),
        ),
    )
    cumulative_flux = 0
    cumulative_entropy = 0
    for index, row in enumerate(edge_rows, start=1):
        cumulative_flux += int(row["undirected_stationary_flux_x1e12"])
        cumulative_entropy += int(row["total_entropy_contribution_x1e12"])
        row["boundary_spine_rank"] = index
        row["cumulative_flux_x1e12"] = cumulative_flux
        row["cumulative_entropy_contribution_x1e12"] = cumulative_entropy

    directed_rows: list[dict[str, int]] = []
    for row in edge_rows:
        rank = int(row["boundary_spine_rank"])
        positive_directed_id = len(directed_rows)
        directed_rows.append(
            {
                "directed_edge_id": positive_directed_id,
                "boundary_spine_rank": rank,
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "source_state_id": 0,
                "target_state_id": 1,
                "source_nodal_sign": 1,
                "target_nodal_sign": -1,
                "source_carrier_mask_class_id": int(
                    row["positive_carrier_mask_class_id"]
                ),
                "target_carrier_mask_class_id": int(
                    row["negative_carrier_mask_class_id"]
                ),
                "boundary_partition_code": int(row["boundary_partition_code"]),
                "transition_probability_x1e12": int(
                    row["positive_to_negative_probability_x1e12"]
                ),
                "stationary_flow_twice_x1e12": int(
                    row["undirected_stationary_flux_x1e12"]
                ),
                "entropy_contribution_x1e12": int(
                    row["positive_entropy_contribution_x1e12"]
                ),
            }
        )
        directed_rows.append(
            {
                "directed_edge_id": positive_directed_id + 1,
                "boundary_spine_rank": rank,
                "boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "source_state_id": 1,
                "target_state_id": 0,
                "source_nodal_sign": -1,
                "target_nodal_sign": 1,
                "source_carrier_mask_class_id": int(
                    row["negative_carrier_mask_class_id"]
                ),
                "target_carrier_mask_class_id": int(
                    row["positive_carrier_mask_class_id"]
                ),
                "boundary_partition_code": int(row["boundary_partition_code"]),
                "transition_probability_x1e12": int(
                    row["negative_to_positive_probability_x1e12"]
                ),
                "stationary_flow_twice_x1e12": int(
                    row["undirected_stationary_flux_x1e12"]
                ),
                "entropy_contribution_x1e12": int(
                    row["negative_entropy_contribution_x1e12"]
                ),
            }
        )

    high_rows = [
        row
        for row in edge_rows
        if int(row["boundary_partition_code"]) == EDGE_HIGH_NEGATIVE
    ]
    central_rows = [
        row
        for row in edge_rows
        if int(row["boundary_partition_code"]) == EDGE_CENTRAL_NEGATIVE
    ]
    top_five_rows = edge_rows[:5]

    boundary_edge_entropy_sum = int(
        sum(int(row["total_entropy_contribution_x1e12"]) for row in edge_rows)
    )
    high_entropy_sum = int(
        sum(int(row["total_entropy_contribution_x1e12"]) for row in high_rows)
    )
    central_entropy_sum = int(
        sum(int(row["total_entropy_contribution_x1e12"]) for row in central_rows)
    )
    top_five_entropy = int(
        sum(int(row["total_entropy_contribution_x1e12"]) for row in top_five_rows)
    )
    top_five_flux = int(
        sum(int(row["undirected_stationary_flux_x1e12"]) for row in top_five_rows)
    )
    partition_entropy_rate = int(
        boundary_rate_report["witness"]["refined_boundary_entropy_rate_x1e12"]
    )
    quotient_entropy_rate = int(
        boundary_rate_report["witness"]["quotient_entropy_rate_x1e12"]
    )
    edge_entropy_rate_scaled = scaled_float(edge_refined_entropy_rate)
    entropy_rounding_delta = abs(
        boundary_edge_entropy_sum
        + self_entropy_contribution
        - edge_entropy_rate_scaled
    )

    observable_values = {
        "state_count": 2,
        "boundary_edge_count": len(edge_rows),
        "directed_boundary_edge_count": len(directed_rows),
        "total_undirected_cut_flux": cut_flux,
        "top_spine_edge_id": int(edge_rows[0]["boundary_mask_edge_id"]),
        "top_spine_edge_flux": int(edge_rows[0]["undirected_stationary_flux_x1e12"]),
        "top_spine_edge_entropy": int(
            edge_rows[0]["total_entropy_contribution_x1e12"]
        ),
        "top_five_spine_flux": top_five_flux,
        "top_five_spine_entropy": top_five_entropy,
        "top_five_flux_fraction": scaled_ratio(top_five_flux, cut_flux),
        "top_five_entropy_fraction_of_boundary_crossing": scaled_ratio(
            top_five_entropy,
            boundary_edge_entropy_sum,
        ),
        "high_negative_boundary_edge_count": len(high_rows),
        "central_negative_boundary_edge_count": len(central_rows),
        "high_negative_edge_entropy": high_entropy_sum,
        "central_negative_edge_entropy": central_entropy_sum,
        "high_negative_entropy_fraction_of_boundary_crossing": scaled_ratio(
            high_entropy_sum,
            boundary_edge_entropy_sum,
        ),
        "central_negative_entropy_fraction_of_boundary_crossing": scaled_ratio(
            central_entropy_sum,
            boundary_edge_entropy_sum,
        ),
        "positive_boundary_probability_sum": int(sum(positive_scaled_row[1:])),
        "negative_boundary_probability_sum": int(sum(negative_scaled_row[:-1])),
        "positive_edge_refined_row_entropy": scaled_float(positive_edge_row_entropy),
        "negative_edge_refined_row_entropy": scaled_float(negative_edge_row_entropy),
        "edge_refined_entropy_rate": edge_entropy_rate_scaled,
        "partition_refined_entropy_rate": partition_entropy_rate,
        "quotient_entropy_rate": quotient_entropy_rate,
        "edge_entropy_surplus_over_partition": edge_entropy_rate_scaled
        - partition_entropy_rate,
        "edge_entropy_surplus_over_quotient": edge_entropy_rate_scaled
        - quotient_entropy_rate,
        "self_entropy_contribution": self_entropy_contribution,
        "boundary_edge_entropy_contribution_sum": boundary_edge_entropy_sum,
        "entropy_rounding_delta": entropy_rounding_delta,
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

    spine_edge_table = table_from_rows(CONDUCTANCE_SPINE_EDGE_COLUMNS, edge_rows)
    directed_edge_table = table_from_rows(
        CONDUCTANCE_DIRECTED_EDGE_COLUMNS,
        directed_rows,
    )
    observable_table = table_from_rows(CONDUCTANCE_OBSERVABLE_COLUMNS, observable_rows)

    spine_order_ids = [int(row["boundary_mask_edge_id"]) for row in edge_rows]
    directed_positive_probability_sum = int(
        sum(
            row["transition_probability_x1e12"]
            for row in directed_rows
            if int(row["source_state_id"]) == 0
        )
    )
    directed_negative_probability_sum = int(
        sum(
            row["transition_probability_x1e12"]
            for row in directed_rows
            if int(row["source_state_id"]) == 1
        )
    )

    checks = {
        "boundary_flux_report_certified": boundary_flux_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_FLUX_CELLS_CERTIFIED",
        "boundary_flux_certificate_certified": boundary_flux_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_FLUX_CELLS_CERTIFIED",
        "boundary_rate_report_certified": boundary_rate_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_FLUX_QUOTIENT_RATES_CERTIFIED",
        "boundary_rate_certificate_certified": boundary_rate_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_FLUX_QUOTIENT_RATES_CERTIFIED",
        "boundary_edge_count_is_16": len(edge_rows) == 16,
        "directed_boundary_edge_count_is_32": len(directed_rows) == 32,
        "total_flux_matches_boundary_rate": cut_flux
        == int(boundary_rate_report["witness"]["total_undirected_cut_flux_x1e12"])
        == 238962451389,
        "spine_order_matches_expected": spine_order_ids
        == [14, 15, 2, 6, 3, 7, 8, 11, 9, 13, 12, 5, 10, 4, 1, 0],
        "top_spine_edge_matches_expected": (
            int(edge_rows[0]["boundary_mask_edge_id"]),
            int(edge_rows[0]["positive_carrier_mask_class_id"]),
            int(edge_rows[0]["negative_carrier_mask_class_id"]),
            int(edge_rows[0]["undirected_stationary_flux_x1e12"]),
            int(edge_rows[0]["total_entropy_contribution_x1e12"]),
        )
        == (14, 11, 13, 43567340880, 135084234325),
        "top_five_spine_matches_expected": (
            [int(row["boundary_mask_edge_id"]) for row in top_five_rows],
            top_five_flux,
            top_five_entropy,
        )
        == ([14, 15, 2, 6, 3], 139072996173, 486096919708),
        "top_five_flux_fraction_matches_expected": observable_values[
            "top_five_flux_fraction"
        ]
        == 581986815772,
        "top_five_entropy_fraction_matches_expected": observable_values[
            "top_five_entropy_fraction_of_boundary_crossing"
        ]
        == 521357092366,
        "high_and_central_edge_counts_match": len(high_rows) == 2
        and len(central_rows) == 14,
        "partition_edge_entropy_totals_match_expected": (
            high_entropy_sum,
            central_entropy_sum,
        )
        == (23221774728, 909146705198),
        "central_entropy_fraction_matches_expected": observable_values[
            "central_negative_entropy_fraction_of_boundary_crossing"
        ]
        == 975093779736,
        "positive_boundary_probabilities_sum_to_upstream_exit": directed_positive_probability_sum
        == int(
            boundary_rate_report["witness"]["positive_boundary_exit_decomposition_x1e12"][
                "high_negative"
            ]
        )
        + int(
            boundary_rate_report["witness"]["positive_boundary_exit_decomposition_x1e12"][
                "central_negative"
            ]
        )
        == 190831926563,
        "negative_boundary_probabilities_sum_to_upstream_exit": directed_negative_probability_sum
        == int(
            boundary_rate_report["witness"]["negative_boundary_exit_decomposition_x1e12"][
                "high_negative"
            ]
        )
        + int(
            boundary_rate_report["witness"]["negative_boundary_exit_decomposition_x1e12"][
                "central_negative"
            ]
        )
        == 319560035288,
        "directed_twice_flows_are_reversible_by_edge": all(
            int(directed_rows[index]["stationary_flow_twice_x1e12"])
            == int(directed_rows[index + 1]["stationary_flow_twice_x1e12"])
            for index in range(0, len(directed_rows), 2)
        ),
        "directed_twice_flow_sum_matches_cut_twice": int(
            sum(row["stationary_flow_twice_x1e12"] for row in directed_rows)
        )
        == 2 * cut_flux,
        "edge_refined_entropy_rate_matches_expected": edge_entropy_rate_scaled
        == 1137598297346,
        "edge_entropy_surplus_over_partition_matches_expected": observable_values[
            "edge_entropy_surplus_over_partition"
        ]
        == 579016158147,
        "edge_entropy_surplus_over_quotient_matches_expected": observable_values[
            "edge_entropy_surplus_over_quotient"
        ]
        == 598158902304,
        "entropy_rounding_delta_within_one": entropy_rounding_delta <= 1,
        "edge_entropy_refines_partition_entropy": edge_entropy_rate_scaled
        > partition_entropy_rate
        > quotient_entropy_rate,
        "spine_edge_table_shape_is_16_by_19": tuple(spine_edge_table.shape)
        == (16, len(CONDUCTANCE_SPINE_EDGE_COLUMNS)),
        "directed_edge_table_shape_is_32_by_13": tuple(directed_edge_table.shape)
        == (32, len(CONDUCTANCE_DIRECTED_EDGE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(CONDUCTANCE_OBSERVABLE_COLUMNS)),
        "boundary_flux_json_schema_available": boundary_flux.get("schema")
        == "c985.d20_signature_boundary_flux_cells@1",
        "boundary_rate_json_schema_available": boundary_rate.get("schema")
        == "c985.d20_signature_boundary_flux_quotient_rates@1",
        "boundary_flux_tables_available": "boundary_mask_edge_table"
        in boundary_flux_tables.files,
        "boundary_rate_tables_available": "boundary_refined_transition_table"
        in boundary_rate_tables.files,
    }

    witness = {
        "boundary_edge_count": len(edge_rows),
        "directed_boundary_edge_count": len(directed_rows),
        "total_undirected_cut_flux_x1e12": cut_flux,
        "spine_order_boundary_mask_edge_ids": spine_order_ids,
        "top_spine_edge": {
            "boundary_mask_edge_id": int(edge_rows[0]["boundary_mask_edge_id"]),
            "positive_carrier_mask_class_id": int(
                edge_rows[0]["positive_carrier_mask_class_id"]
            ),
            "negative_carrier_mask_class_id": int(
                edge_rows[0]["negative_carrier_mask_class_id"]
            ),
            "undirected_stationary_flux_x1e12": int(
                edge_rows[0]["undirected_stationary_flux_x1e12"]
            ),
            "total_entropy_contribution_x1e12": int(
                edge_rows[0]["total_entropy_contribution_x1e12"]
            ),
        },
        "top_five_spine": {
            "boundary_mask_edge_ids": [
                int(row["boundary_mask_edge_id"]) for row in top_five_rows
            ],
            "undirected_stationary_flux_x1e12": top_five_flux,
            "total_entropy_contribution_x1e12": top_five_entropy,
            "flux_fraction_x1e12": observable_values["top_five_flux_fraction"],
            "entropy_fraction_of_boundary_crossing_x1e12": observable_values[
                "top_five_entropy_fraction_of_boundary_crossing"
            ],
        },
        "partition_edge_entropy_x1e12": {
            "high_negative": high_entropy_sum,
            "central_negative": central_entropy_sum,
        },
        "partition_edge_entropy_fraction_x1e12": {
            "high_negative": observable_values[
                "high_negative_entropy_fraction_of_boundary_crossing"
            ],
            "central_negative": observable_values[
                "central_negative_entropy_fraction_of_boundary_crossing"
            ],
        },
        "positive_boundary_probability_sum_x1e12": directed_positive_probability_sum,
        "negative_boundary_probability_sum_x1e12": directed_negative_probability_sum,
        "positive_edge_refined_row_entropy_x1e12": observable_values[
            "positive_edge_refined_row_entropy"
        ],
        "negative_edge_refined_row_entropy_x1e12": observable_values[
            "negative_edge_refined_row_entropy"
        ],
        "edge_refined_entropy_rate_x1e12": edge_entropy_rate_scaled,
        "partition_refined_entropy_rate_x1e12": partition_entropy_rate,
        "quotient_entropy_rate_x1e12": quotient_entropy_rate,
        "edge_entropy_surplus_over_partition_x1e12": observable_values[
            "edge_entropy_surplus_over_partition"
        ],
        "edge_entropy_surplus_over_quotient_x1e12": observable_values[
            "edge_entropy_surplus_over_quotient"
        ],
        "self_entropy_contribution_x1e12": self_entropy_contribution,
        "boundary_edge_entropy_contribution_sum_x1e12": boundary_edge_entropy_sum,
        "entropy_rounding_delta_x1e12": entropy_rounding_delta,
        "conductance_spine_edge_table_sha256": sha_array(spine_edge_table),
        "conductance_directed_edge_table_sha256": sha_array(directed_edge_table),
        "conductance_observable_table_sha256": sha_array(observable_table),
    }

    conductance_spine = {
        "schema": "c985.d20_signature_boundary_conductance_spine@1",
        "object": "d20",
        "spine_rule": {
            "source": "certified residual boundary-cell flux and boundary-rate refinement",
            "vertices": "carrier-mask classes on the positive-negative residual boundary",
            "edges": "the 16 certified residual positive-negative carrier-mask boundary edges",
            "orientation": "positive carrier endpoint to negative carrier endpoint, together with the reversible reverse direction",
            "ordering": "descending edge-level weighted entropy contribution, then descending conductance, then boundary edge id",
            "rate_law": "edge twice-flow divided by twice the source quotient-state stationary mass",
        },
        "spine_order_boundary_mask_edge_ids": spine_order_ids,
        "top_spine_edge": witness["top_spine_edge"],
        "top_five_spine": witness["top_five_spine"],
        "entropy_summary": {
            "edge_refined_entropy_rate_x1e12": edge_entropy_rate_scaled,
            "partition_refined_entropy_rate_x1e12": partition_entropy_rate,
            "quotient_entropy_rate_x1e12": quotient_entropy_rate,
            "edge_entropy_surplus_over_partition_x1e12": observable_values[
                "edge_entropy_surplus_over_partition"
            ],
            "edge_entropy_surplus_over_quotient_x1e12": observable_values[
                "edge_entropy_surplus_over_quotient"
            ],
            "boundary_edge_entropy_contribution_sum_x1e12": boundary_edge_entropy_sum,
            "entropy_rounding_delta_x1e12": entropy_rounding_delta,
        },
        "spine_edges": [
            {key: int(value) for key, value in row.items()} for row in edge_rows
        ],
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_conductance_spine_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_CONDUCTANCE_SPINE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 16 residual positive-negative boundary edges form a directed reversible conductance spine",
            "edge 14, from positive carrier mask 11 to negative carrier mask 13, is the dominant entropy edge",
            "the top five spine edges are [14, 15, 2, 6, 3] and carry 0.581986815772 of cut flux",
            "central-negative boundary edges carry 0.975093779736 of edge-level crossing entropy",
            "refining the boundary-rate alphabet from two contact types to 16 edges raises entropy rate to 1.137598297346",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_conductance_spine@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The high/central boundary-rate alphabet lifts to a certified "
            "directed conductance spine on the 16 residual positive-negative "
            "carrier-mask boundary edges, ordered by edge-level entropy "
            "contribution and preserving reversible twice-flow accounting."
        ),
        "stage_protocol": {
            "draft": "lift the partition-level boundary rates onto individual residual boundary-mask edges",
            "witness": "materialize entropy-ordered spine edges, directed rates, and edge-level entropy observables",
            "coherence": "check row probability sums, reversible edge twice-flows, flux totals, and entropy refinement",
            "closure": "certify the finite conductance spine without claiming continuum conductance geometry",
            "emit": "emit conductance-spine JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "boundary_flux_report": input_entry(
                BOUNDARY_FLUX_REPORT,
                {
                    "status": boundary_flux_report.get("status"),
                    "certificate_sha256": boundary_flux_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "boundary_flux": input_entry(BOUNDARY_FLUX_JSON),
            "boundary_flux_tables": input_entry(BOUNDARY_FLUX_TABLES),
            "boundary_flux_certificate": input_entry(BOUNDARY_FLUX_CERTIFICATE),
            "boundary_mask_edges": input_entry(BOUNDARY_MASK_EDGES),
            "boundary_rate_report": input_entry(
                BOUNDARY_RATE_REPORT,
                {
                    "status": boundary_rate_report.get("status"),
                    "certificate_sha256": boundary_rate_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "boundary_rate": input_entry(BOUNDARY_RATE_JSON),
            "boundary_rate_tables": input_entry(BOUNDARY_RATE_TABLES),
            "boundary_rate_certificate": input_entry(BOUNDARY_RATE_CERTIFICATE),
            "boundary_rate_partitions": input_entry(BOUNDARY_RATE_PARTITIONS),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_conductance_spine": relpath(
                OUT_DIR / "signature_boundary_conductance_spine.json"
            ),
            "boundary_conductance_spine_edges_csv": relpath(
                OUT_DIR / "boundary_conductance_spine_edges.csv"
            ),
            "boundary_conductance_directed_edges_csv": relpath(
                OUT_DIR / "boundary_conductance_directed_edges.csv"
            ),
            "boundary_conductance_observables_csv": relpath(
                OUT_DIR / "boundary_conductance_observables.csv"
            ),
            "signature_boundary_conductance_spine_tables": relpath(
                OUT_DIR / "signature_boundary_conductance_spine_tables.npz"
            ),
            "signature_boundary_conductance_spine_certificate": relpath(
                OUT_DIR / "signature_boundary_conductance_spine_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the 16-edge residual boundary conductance spine ordered by edge entropy contribution",
                "two directed reversible rate rows for every boundary edge",
                "exact cut-flux preservation and source-exit probability sums at quotient scale",
                "entropy refinement from binary quotient to partition contacts to individual boundary edges",
            ],
            "does_not_certify_because_not_required": [
                "a continuum conductance law or diffusion limit",
                "mixing-time bounds from the conductance spine",
                "higher-eigenmode boundary spines",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Push the conductance spine back into the Poincare disk: certify a "
            "geometric spine polyline whose edge order follows entropy mass, "
            "then measure whether the dominant path tracks the quotient "
            "geodesic axis or bends through the residual coordinate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_conductance_spine_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified boundary-flux and boundary-rate artifacts",
            "normalize each residual boundary edge to positive and negative carrier endpoints",
            "compute directed rate rows from edge twice-flow and quotient state masses",
            "order the conductance spine by edge-level entropy contribution",
            "verify flux totals, row probability sums, reversible edge flows, and entropy refinement",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_conductance_spine": conductance_spine,
        "boundary_conductance_spine_edges_csv": csv_text(
            CONDUCTANCE_SPINE_EDGE_COLUMNS,
            edge_rows,
        ),
        "boundary_conductance_directed_edges_csv": csv_text(
            CONDUCTANCE_DIRECTED_EDGE_COLUMNS,
            directed_rows,
        ),
        "boundary_conductance_observables_csv": csv_text(
            CONDUCTANCE_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "conductance_spine_edge_table": spine_edge_table,
        "conductance_directed_edge_table": directed_edge_table,
        "conductance_observable_table": observable_table,
        "signature_boundary_conductance_spine_certificate": certificate,
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
        OUT_DIR / "signature_boundary_conductance_spine.json",
        payloads["signature_boundary_conductance_spine"],
    )
    (OUT_DIR / "boundary_conductance_spine_edges.csv").write_text(
        payloads["boundary_conductance_spine_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_conductance_directed_edges.csv").write_text(
        payloads["boundary_conductance_directed_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "boundary_conductance_observables.csv").write_text(
        payloads["boundary_conductance_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_conductance_spine_tables.npz",
        conductance_spine_edge_table=payloads["conductance_spine_edge_table"],
        conductance_directed_edge_table=payloads["conductance_directed_edge_table"],
        conductance_observable_table=payloads["conductance_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_conductance_spine_certificate.json",
        payloads["signature_boundary_conductance_spine_certificate"],
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
                "top_five_spine": witness["top_five_spine"],
                "edge_refined_entropy_rate_x1e12": witness[
                    "edge_refined_entropy_rate_x1e12"
                ],
                "edge_entropy_surplus_over_partition_x1e12": witness[
                    "edge_entropy_surplus_over_partition_x1e12"
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
