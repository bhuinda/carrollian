from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from typing import Any

import numpy as np

try:
    from .derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        table_from_rows,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        table_from_rows,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_measure"
STATUS = "LONG_MEASURE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_PATHS_REPORT = PROOF_ROOT / "long_paths" / "report.json"
LONG_PATHS_COMPONENT = PROOF_ROOT / "long_paths" / "component.csv"
LONG_PATHS_FIBER = PROOF_ROOT / "long_paths" / "fiber.csv"
LONG_PATHS_HORIZON = PROOF_ROOT / "long_paths" / "horizon.csv"
LONG_PATHS_TABLES = PROOF_ROOT / "long_paths" / "tables.npz"
LONG_RAW_REPORT = PROOF_ROOT / "long_raw" / "report.json"
LONG_RAW_TABLES = PROOF_ROOT / "long_raw" / "tables.npz"
LONG_PROB_REPORT = PROOF_ROOT / "long_prob" / "report.json"
LONG_PROB_TABLES = PROOF_ROOT / "long_prob" / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_measure.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_measure.py"

MEASURE_TEXT_HASH = "2ae41770d26da8de66d7d6f50a2981ee195981b375bce0716d4a3e322b0822c7"
DIST_TEXT_HASH = "3adc079fb9278e84114582870dff318bd28cc72dcfaa76323132ec7f16b96d68"
MOMENT_TEXT_HASH = "c2c8c89e1431744be74e085d38e30182e50ce82e3b2fb726003cb2b17c0c1f44"
DECOMP_TEXT_HASH = "11c9ef69d0515777ed65a778107403f2c23020bcb4b2ecdb5207b5f0d5d8169f"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

FRACTION_FIELDS = [
    "num_digits",
    "den_digits",
    "num_mod_1000000007",
    "den_mod_1000000007",
    "num_mod_1000000009",
    "den_mod_1000000009",
]


def prefixed_fraction_columns(prefix: str) -> list[str]:
    return [f"{prefix}_{field}" for field in FRACTION_FIELDS]


MEASURE_COLUMNS = [
    "measure_id",
    "measure_code",
    "component_row_count",
    "active_weight_total",
    "full_raw_weight_total",
    "inactive_weight_total",
    "inactive_gap_flag",
    "mixed_weight_total_digits",
    "mixed_weight_total_mod_1000000007",
    "mixed_weight_total_mod_1000000009",
    "distribution_row_count",
    "moment_row_count",
    "decomp_row_count",
    "normalized_active_scope_flag",
    "full_raw_measure_certified_flag",
    "full_raw_scope_gap_flag",
    "next_target_code",
]
DIST_COLUMNS = [
    "measure_id",
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "average_num",
    "average_den",
    "weight_digits",
    "weight_mod_1000000007",
    "weight_mod_1000000009",
    "conditional_total_digits",
    "conditional_total_mod_1000000007",
    "conditional_total_mod_1000000009",
    "mixed_total_digits",
    "mixed_total_mod_1000000007",
    "mixed_total_mod_1000000009",
    *prefixed_fraction_columns("conditional_prob"),
    *prefixed_fraction_columns("mixed_prob"),
]
MOMENT_COLUMNS = [
    "measure_id",
    "sample_count",
    "fiber_count",
    "sum_value_min",
    "sum_value_max",
    "weight_total_digits",
    "weight_total_mod_1000000007",
    "weight_total_mod_1000000009",
    "conditional_normalization_flag",
    *prefixed_fraction_columns("mean_sum"),
    *prefixed_fraction_columns("variance_sum"),
    *prefixed_fraction_columns("mean_average"),
    *prefixed_fraction_columns("variance_average"),
    *prefixed_fraction_columns("variance_shrink_gap"),
    "variance_shrink_from_prev_flag",
]
DECOMP_COLUMNS = [
    "measure_id",
    "path_count",
    "weight_total_digits",
    "weight_total_mod_1000000007",
    "weight_total_mod_1000000009",
    *prefixed_fraction_columns("global_mean_average"),
    *prefixed_fraction_columns("global_variance_average"),
    *prefixed_fraction_columns("within_variance_average"),
    *prefixed_fraction_columns("between_variance_average"),
    *prefixed_fraction_columns("variance_decomp_gap"),
    "variance_decomp_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "measure_row_count",
    "distribution_row_count",
    "moment_row_count",
    "decomp_row_count",
    "fiber_row_count",
    "horizon_row_count",
    "component_row_count",
    "support_component_weight_sum",
    "coeff_component_weight_sum",
    "raw_tensor_support_count",
    "raw_tensor_coeff_sum",
    "inactive_raw_support_count",
    "inactive_raw_coeff_sum",
    "conditional_normalization_flag_count",
    "variance_shrink_flag_count",
    "variance_decomp_flag_count",
    "support_mixed_weight_total_digits",
    "coeff_mixed_weight_total_digits",
    "support_mixed_weight_total_mod_1000000007",
    "coeff_mixed_weight_total_mod_1000000007",
    "scoped_probability_law_flag",
    "full_raw_measure_certified_flag",
    "full_raw_scope_gap_flag",
    "materialized_raw_path_family_flag",
    "exact_composable_raw_path_family_flag",
    "next_target_code",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

MEASURES = [
    {
        "measure_id": 0,
        "measure_code": 0,
        "name": "active_raw_support_count",
        "component_key": "raw_support_count",
        "full_key": "raw_tensor_support_count",
        "inactive_key": "inactive_raw_support_count",
    },
    {
        "measure_id": 1,
        "measure_code": 1,
        "name": "active_raw_coeff_mass",
        "component_key": "raw_coeff_sum",
        "full_key": "raw_tensor_coeff_sum",
        "inactive_key": "inactive_raw_coeff_sum",
    },
]


def certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


def digits(value: int) -> int:
    return len(str(abs(value)))


def mod_pair(value: int) -> tuple[int, int]:
    return value % MOD_PRIMES[0], value % MOD_PRIMES[1]


def fraction_record(value: Fraction) -> dict[str, int]:
    return {
        "num_digits": digits(value.numerator),
        "den_digits": digits(value.denominator),
        "num_mod_1000000007": value.numerator % MOD_PRIMES[0],
        "den_mod_1000000007": value.denominator % MOD_PRIMES[0],
        "num_mod_1000000009": value.numerator % MOD_PRIMES[1],
        "den_mod_1000000009": value.denominator % MOD_PRIMES[1],
    }


def prefixed_fraction_fields(prefix: str, value: Fraction) -> dict[str, int]:
    record = fraction_record(value)
    return {f"{prefix}_{key}": int(record[key]) for key in FRACTION_FIELDS}


def weighted_coefficients(weights: list[int], max_horizon: int) -> dict[int, list[int]]:
    coeffs = {0: [1]}
    for sample_count in range(1, max_horizon + 1):
        previous = coeffs[sample_count - 1]
        current = [0 for _ in range(len(previous) + len(weights) - 1)]
        for index, value in enumerate(previous):
            for add_value, weight in enumerate(weights):
                current[index + add_value] += value * weight
        coeffs[sample_count] = current
    return coeffs


def load_inputs() -> dict[str, Any]:
    return {
        "paths_report": load_json(LONG_PATHS_REPORT),
        "raw_report": load_json(LONG_RAW_REPORT),
        "prob_report": load_json(LONG_PROB_REPORT),
        "component_rows": int_rows(read_csv_rows(LONG_PATHS_COMPONENT)),
        "fiber_rows": int_rows(read_csv_rows(LONG_PATHS_FIBER)),
        "horizon_rows": int_rows(read_csv_rows(LONG_PATHS_HORIZON)),
    }


def raw_totals(raw_report: dict[str, Any]) -> dict[str, int]:
    active = raw_report.get("witness", {}).get("active_components", {})
    owner = raw_report.get("witness", {}).get("raw_owner_assignment", {})
    return {
        "raw_tensor_support_count": int(owner.get("raw_tensor_support_count", 0)),
        "raw_tensor_coeff_sum": int(owner.get("raw_tensor_coeff_sum", 0)),
        "inactive_raw_support_count": int(active.get("inactive_raw_support_count", 0)),
        "inactive_raw_coeff_sum": int(active.get("inactive_raw_coeff_sum", 0)),
    }


def build_distribution_rows(
    measure_id: int,
    active_total: int,
    mixed_total: int,
    coeffs: dict[int, list[int]],
    fiber_rows: list[dict[str, int]],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    mixed_mod0, mixed_mod1 = mod_pair(mixed_total)
    for fiber in fiber_rows:
        sample_count = fiber["sample_count"]
        sum_value = fiber["sum_value"]
        weight = coeffs[sample_count][sum_value]
        conditional_total = active_total**sample_count
        conditional_mod0, conditional_mod1 = mod_pair(conditional_total)
        weight_mod0, weight_mod1 = mod_pair(weight)
        row = {
            "measure_id": measure_id,
            "fiber_row_id": fiber["fiber_row_id"],
            "sample_count": sample_count,
            "sum_value": sum_value,
            "average_num": sum_value,
            "average_den": sample_count,
            "weight_digits": digits(weight),
            "weight_mod_1000000007": weight_mod0,
            "weight_mod_1000000009": weight_mod1,
            "conditional_total_digits": digits(conditional_total),
            "conditional_total_mod_1000000007": conditional_mod0,
            "conditional_total_mod_1000000009": conditional_mod1,
            "mixed_total_digits": digits(mixed_total),
            "mixed_total_mod_1000000007": mixed_mod0,
            "mixed_total_mod_1000000009": mixed_mod1,
        }
        row.update(
            prefixed_fraction_fields(
                "conditional_prob", Fraction(weight, conditional_total)
            )
        )
        row.update(prefixed_fraction_fields("mixed_prob", Fraction(weight, mixed_total)))
        rows.append(row)
    return rows


def build_moment_rows(
    measure_id: int,
    active_total: int,
    coeffs: dict[int, list[int]],
    max_horizon: int,
) -> tuple[list[dict[str, int]], dict[int, dict[str, Any]]]:
    rows: list[dict[str, int]] = []
    records: dict[int, dict[str, Any]] = {}
    previous_variance_average = Fraction(0)
    for sample_count in range(1, max_horizon + 1):
        weights = coeffs[sample_count]
        weight_total = active_total**sample_count
        weighted_sum = sum(index * weight for index, weight in enumerate(weights))
        weighted_square = sum(
            index * index * weight for index, weight in enumerate(weights)
        )
        mean_sum = Fraction(weighted_sum, weight_total)
        variance_sum = Fraction(weighted_square, weight_total) - mean_sum * mean_sum
        mean_average = mean_sum / sample_count
        variance_average = variance_sum / (sample_count * sample_count)
        shrink_gap = (
            Fraction(0)
            if sample_count == 1
            else previous_variance_average - variance_average
        )
        shrink_flag = int(sample_count == 1 or shrink_gap > 0)
        weight_mod0, weight_mod1 = mod_pair(weight_total)
        row = {
            "measure_id": measure_id,
            "sample_count": sample_count,
            "fiber_count": len(weights),
            "sum_value_min": 0,
            "sum_value_max": len(weights) - 1,
            "weight_total_digits": digits(weight_total),
            "weight_total_mod_1000000007": weight_mod0,
            "weight_total_mod_1000000009": weight_mod1,
            "conditional_normalization_flag": int(sum(weights) == weight_total),
            "variance_shrink_from_prev_flag": shrink_flag,
        }
        row.update(prefixed_fraction_fields("mean_sum", mean_sum))
        row.update(prefixed_fraction_fields("variance_sum", variance_sum))
        row.update(prefixed_fraction_fields("mean_average", mean_average))
        row.update(prefixed_fraction_fields("variance_average", variance_average))
        row.update(prefixed_fraction_fields("variance_shrink_gap", shrink_gap))
        rows.append(row)
        records[sample_count] = {
            "weight_total": weight_total,
            "mean_average": mean_average,
            "variance_average": variance_average,
        }
        previous_variance_average = variance_average
    return rows, records


def build_decomp_row(
    measure_id: int,
    moment_records: dict[int, dict[str, Any]],
    coeffs: dict[int, list[int]],
    mixed_total: int,
) -> dict[str, int]:
    weighted_mean = Fraction(0)
    weighted_second = Fraction(0)
    path_count = 0
    for sample_count, weights in coeffs.items():
        if sample_count == 0:
            continue
        path_count += len(weights)
        for sum_value, weight in enumerate(weights):
            average = Fraction(sum_value, sample_count)
            weighted_mean += average * weight
            weighted_second += average * average * weight
    global_mean = weighted_mean / mixed_total
    global_variance = weighted_second / mixed_total - global_mean * global_mean
    within = sum(
        Fraction(record["weight_total"], mixed_total) * record["variance_average"]
        for record in moment_records.values()
    )
    between = sum(
        Fraction(record["weight_total"], mixed_total)
        * (record["mean_average"] - global_mean)
        * (record["mean_average"] - global_mean)
        for record in moment_records.values()
    )
    decomp_gap = global_variance - within - between
    mixed_mod0, mixed_mod1 = mod_pair(mixed_total)
    row = {
        "measure_id": measure_id,
        "path_count": path_count,
        "weight_total_digits": digits(mixed_total),
        "weight_total_mod_1000000007": mixed_mod0,
        "weight_total_mod_1000000009": mixed_mod1,
        "variance_decomp_flag": int(decomp_gap == 0),
    }
    row.update(prefixed_fraction_fields("global_mean_average", global_mean))
    row.update(prefixed_fraction_fields("global_variance_average", global_variance))
    row.update(prefixed_fraction_fields("within_variance_average", within))
    row.update(prefixed_fraction_fields("between_variance_average", between))
    row.update(prefixed_fraction_fields("variance_decomp_gap", decomp_gap))
    return row


def build_rows() -> dict[str, Any]:
    loaded = load_inputs()
    component_rows = loaded["component_rows"]
    fiber_rows = loaded["fiber_rows"]
    horizon_rows = loaded["horizon_rows"]
    max_horizon = max(row["sample_count"] for row in horizon_rows)
    totals = raw_totals(loaded["raw_report"])

    measure_rows: list[dict[str, int]] = []
    dist_rows: list[dict[str, int]] = []
    moment_rows: list[dict[str, int]] = []
    decomp_rows: list[dict[str, int]] = []
    measure_summaries: dict[str, dict[str, int]] = {}

    for measure in MEASURES:
        measure_id = int(measure["measure_id"])
        weights = [row[str(measure["component_key"])] for row in component_rows]
        active_total = sum(weights)
        full_total = totals[str(measure["full_key"])]
        inactive_total = totals[str(measure["inactive_key"])]
        coeffs = weighted_coefficients(weights, max_horizon)
        mixed_total = sum(active_total**sample_count for sample_count in range(1, max_horizon + 1))
        mixed_mod0, mixed_mod1 = mod_pair(mixed_total)
        dist_for_measure = build_distribution_rows(
            measure_id, active_total, mixed_total, coeffs, fiber_rows
        )
        moment_for_measure, moment_records = build_moment_rows(
            measure_id, active_total, coeffs, max_horizon
        )
        decomp_for_measure = build_decomp_row(
            measure_id, moment_records, coeffs, mixed_total
        )
        dist_rows.extend(dist_for_measure)
        moment_rows.extend(moment_for_measure)
        decomp_rows.append(decomp_for_measure)
        measure_rows.append(
            {
                "measure_id": measure_id,
                "measure_code": int(measure["measure_code"]),
                "component_row_count": len(component_rows),
                "active_weight_total": active_total,
                "full_raw_weight_total": full_total,
                "inactive_weight_total": inactive_total,
                "inactive_gap_flag": int(inactive_total > 0),
                "mixed_weight_total_digits": digits(mixed_total),
                "mixed_weight_total_mod_1000000007": mixed_mod0,
                "mixed_weight_total_mod_1000000009": mixed_mod1,
                "distribution_row_count": len(dist_for_measure),
                "moment_row_count": len(moment_for_measure),
                "decomp_row_count": 1,
                "normalized_active_scope_flag": int(
                    all(row["conditional_normalization_flag"] == 1 for row in moment_for_measure)
                ),
                "full_raw_measure_certified_flag": 0,
                "full_raw_scope_gap_flag": int(inactive_total > 0),
                "next_target_code": 6,
            }
        )
        measure_summaries[str(measure["name"])] = {
            "active_total": active_total,
            "full_total": full_total,
            "inactive_total": inactive_total,
            "mixed_total_digits": digits(mixed_total),
            "mixed_total_mod_1000000007": mixed_mod0,
        }

    paths_summary = loaded["paths_report"].get("witness", {}).get("summary", {})
    obs = {
        "measure_row_count": len(measure_rows),
        "distribution_row_count": len(dist_rows),
        "moment_row_count": len(moment_rows),
        "decomp_row_count": len(decomp_rows),
        "fiber_row_count": len(fiber_rows),
        "horizon_row_count": len(horizon_rows),
        "component_row_count": len(component_rows),
        "support_component_weight_sum": measure_summaries[
            "active_raw_support_count"
        ]["active_total"],
        "coeff_component_weight_sum": measure_summaries["active_raw_coeff_mass"][
            "active_total"
        ],
        "raw_tensor_support_count": totals["raw_tensor_support_count"],
        "raw_tensor_coeff_sum": totals["raw_tensor_coeff_sum"],
        "inactive_raw_support_count": totals["inactive_raw_support_count"],
        "inactive_raw_coeff_sum": totals["inactive_raw_coeff_sum"],
        "conditional_normalization_flag_count": sum(
            row["conditional_normalization_flag"] for row in moment_rows
        ),
        "variance_shrink_flag_count": sum(
            row["variance_shrink_from_prev_flag"] for row in moment_rows
        ),
        "variance_decomp_flag_count": sum(
            row["variance_decomp_flag"] for row in decomp_rows
        ),
        "support_mixed_weight_total_digits": measure_summaries[
            "active_raw_support_count"
        ]["mixed_total_digits"],
        "coeff_mixed_weight_total_digits": measure_summaries[
            "active_raw_coeff_mass"
        ]["mixed_total_digits"],
        "support_mixed_weight_total_mod_1000000007": measure_summaries[
            "active_raw_support_count"
        ]["mixed_total_mod_1000000007"],
        "coeff_mixed_weight_total_mod_1000000007": measure_summaries[
            "active_raw_coeff_mass"
        ]["mixed_total_mod_1000000007"],
        "scoped_probability_law_flag": 1,
        "full_raw_measure_certified_flag": 0,
        "full_raw_scope_gap_flag": int(
            totals["inactive_raw_support_count"] > 0
            and totals["inactive_raw_coeff_sum"] > 0
        ),
        "materialized_raw_path_family_flag": int(
            paths_summary.get("materialized_raw_path_family_flag", -1)
        ),
        "exact_composable_raw_path_family_flag": int(
            paths_summary.get("exact_composable_raw_path_family_flag", -1)
        ),
        "next_target_code": 6,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    measure_hash = hashlib.sha256(
        digest_text(MEASURE_COLUMNS, measure_rows).encode("ascii")
    ).hexdigest()
    dist_hash = hashlib.sha256(
        digest_text(DIST_COLUMNS, dist_rows).encode("ascii")
    ).hexdigest()
    moment_hash = hashlib.sha256(
        digest_text(MOMENT_COLUMNS, moment_rows).encode("ascii")
    ).hexdigest()
    decomp_hash = hashlib.sha256(
        digest_text(DECOMP_COLUMNS, decomp_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": {
            "long_paths": loaded["paths_report"],
            "long_raw": loaded["raw_report"],
            "long_prob": loaded["prob_report"],
        },
        "measure_rows": measure_rows,
        "dist_rows": dist_rows,
        "moment_rows": moment_rows,
        "decomp_rows": decomp_rows,
        "obs_rows": obs_rows,
        "measure_table": table_from_rows(MEASURE_COLUMNS, measure_rows),
        "dist_table": table_from_rows(DIST_COLUMNS, dist_rows),
        "moment_table": table_from_rows(MOMENT_COLUMNS, moment_rows),
        "decomp_table": table_from_rows(DECOMP_COLUMNS, decomp_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "measure_hash": measure_hash,
        "dist_hash": dist_hash,
        "moment_hash": moment_hash,
        "decomp_hash": decomp_hash,
        "obs": obs,
        "measure_summaries": measure_summaries,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    reports = rows["input_reports"]
    checks = {
        "inputs_certified": (
            certified(reports["long_paths"], "LONG_PATHS_CERTIFIED"),
            certified(reports["long_raw"], "LONG_RAW_CERTIFIED"),
            certified(reports["long_prob"], "LONG_PROB_CERTIFIED"),
        )
        == (1, 1, 1),
        "active_weights_exact": (
            obs["component_row_count"],
            obs["support_component_weight_sum"],
            obs["coeff_component_weight_sum"],
        )
        == (3, 1_096_591, 1_985_840),
        "full_raw_gap_exact": (
            obs["raw_tensor_support_count"],
            obs["raw_tensor_coeff_sum"],
            obs["inactive_raw_support_count"],
            obs["inactive_raw_coeff_sum"],
            obs["full_raw_scope_gap_flag"],
        )
        == (1_414_965, 2_537_360, 318_374, 551_520, 1),
        "probability_tables_exact": (
            obs["measure_row_count"],
            obs["distribution_row_count"],
            obs["moment_row_count"],
            obs["decomp_row_count"],
            obs["fiber_row_count"],
            obs["horizon_row_count"],
        )
        == (2, 576, 32, 2, 288, 16),
        "normalization_exact": (
            obs["conditional_normalization_flag_count"],
            obs["variance_shrink_flag_count"],
            obs["variance_decomp_flag_count"],
            obs["scoped_probability_law_flag"],
        )
        == (32, 32, 2, 1),
        "scope_not_overclaimed": (
            obs["full_raw_measure_certified_flag"],
            obs["materialized_raw_path_family_flag"],
            obs["exact_composable_raw_path_family_flag"],
            obs["next_target_code"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 0, 6, 0),
        "fingerprints_exact": (
            rows["measure_hash"],
            rows["dist_hash"],
            rows["moment_hash"],
            rows["decomp_hash"],
        )
        == (
            MEASURE_TEXT_HASH,
            DIST_TEXT_HASH,
            MOMENT_TEXT_HASH,
            DECOMP_TEXT_HASH,
        ),
        "table_shapes_match": (
            tuple(rows["measure_table"].shape),
            tuple(rows["dist_table"].shape),
            tuple(rows["moment_table"].shape),
            tuple(rows["decomp_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (2, len(MEASURE_COLUMNS)),
            (576, len(DIST_COLUMNS)),
            (32, len(MOMENT_COLUMNS)),
            (2, len(DECOMP_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "scoped_active_raw_product_probability_boundary",
        "summary": {
            "measure_row_count": obs["measure_row_count"],
            "distribution_row_count": obs["distribution_row_count"],
            "moment_row_count": obs["moment_row_count"],
            "decomp_row_count": obs["decomp_row_count"],
            "conditional_normalization_flag_count": obs[
                "conditional_normalization_flag_count"
            ],
            "variance_shrink_flag_count": obs["variance_shrink_flag_count"],
            "variance_decomp_flag_count": obs["variance_decomp_flag_count"],
            "scoped_probability_law_flag": obs["scoped_probability_law_flag"],
            "full_raw_measure_certified_flag": obs[
                "full_raw_measure_certified_flag"
            ],
            "full_raw_scope_gap_flag": obs["full_raw_scope_gap_flag"],
            "next_target": "long_h16",
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "active_scope": {
            "support_component_weight_sum": obs["support_component_weight_sum"],
            "coeff_component_weight_sum": obs["coeff_component_weight_sum"],
            "support_mixed_weight_total_digits": obs[
                "support_mixed_weight_total_digits"
            ],
            "coeff_mixed_weight_total_digits": obs[
                "coeff_mixed_weight_total_digits"
            ],
            "support_mixed_weight_total_mod_1000000007": obs[
                "support_mixed_weight_total_mod_1000000007"
            ],
            "coeff_mixed_weight_total_mod_1000000007": obs[
                "coeff_mixed_weight_total_mod_1000000007"
            ],
        },
        "full_raw_gap": {
            "raw_tensor_support_count": obs["raw_tensor_support_count"],
            "raw_tensor_coeff_sum": obs["raw_tensor_coeff_sum"],
            "inactive_raw_support_count": obs["inactive_raw_support_count"],
            "inactive_raw_coeff_sum": obs["inactive_raw_coeff_sum"],
            "full_raw_scope_gap_flag": obs["full_raw_scope_gap_flag"],
        },
        "hashes": {
            "measure_text_sha256": rows["measure_hash"],
            "distribution_text_sha256": rows["dist_hash"],
            "moment_text_sha256": rows["moment_hash"],
            "decomp_text_sha256": rows["decomp_hash"],
            "measure_table_sha256": sha_array(rows["measure_table"]),
            "distribution_table_sha256": sha_array(rows["dist_table"]),
            "moment_table_sha256": sha_array(rows["moment_table"]),
            "decomp_table_sha256": sha_array(rows["decomp_table"]),
            "observable_table_sha256": sha_array(rows["observable_table"]),
        },
    }
    measure_payload = {
        "schema": "long.measure@1",
        "object": "scoped_active_raw_product_probability_boundary",
        "status": STATUS if all(checks.values()) else "LONG_MEASURE_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.measure.report@1",
        "status": measure_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_measure normalizes the compressed active raw product-family "
            "counts from long_paths into two scoped finite probability laws: "
            "one weighted by active raw-support counts and one weighted by "
            "active raw-coefficient mass. Each law has exact conditional "
            "normalization for horizons 1..16, exact mixed-horizon "
            "normalization, a strict sample-average variance shrink curve, and "
            "an exact law-of-total-variance decomposition. The certificate also "
            "records the inactive full-raw-support gap, so it demotes full "
            "raw-support measure claims under the current active-product "
            "ontology rather than silently upgrading the scoped law."
        ),
        "stage_protocol": {
            "draft": "read long_paths compressed product counts, long_raw full-support totals, and long_prob selected-witness probability boundary",
            "witness": "emit scoped support/count and coefficient-mass measure rows, distributions, moments, variance decompositions, and inactive full-raw gap rows",
            "coherence": "check source statuses, active weights, full raw gap, normalization, variance shrinkage, decomposition, hashes, and table shapes",
            "closure": "certify scoped active-product probability laws while preserving the full raw-support boundary",
            "emit": "write long_measure artifacts and verifier hook",
        },
        "inputs": {
            "long_paths_report": input_entry(
                LONG_PATHS_REPORT,
                {
                    "status": reports["long_paths"].get("status"),
                    "certificate_sha256": reports["long_paths"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_paths_component": input_entry(LONG_PATHS_COMPONENT),
            "long_paths_fiber": input_entry(LONG_PATHS_FIBER),
            "long_paths_horizon": input_entry(LONG_PATHS_HORIZON),
            "long_paths_tables": input_entry(LONG_PATHS_TABLES),
            "long_raw_report": input_entry(
                LONG_RAW_REPORT,
                {
                    "status": reports["long_raw"].get("status"),
                    "certificate_sha256": reports["long_raw"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_raw_tables": input_entry(LONG_RAW_TABLES),
            "long_prob_report": input_entry(
                LONG_PROB_REPORT,
                {
                    "status": reports["long_prob"].get("status"),
                    "certificate_sha256": reports["long_prob"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_prob_tables": input_entry(LONG_PROB_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "measure": relpath(OUT_DIR / "measure.json"),
            "measure_csv": relpath(OUT_DIR / "measure.csv"),
            "dist_csv": relpath(OUT_DIR / "dist.csv"),
            "moment_csv": relpath(OUT_DIR / "moment.csv"),
            "decomp_csv": relpath(OUT_DIR / "decomp.csv"),
            "obs_csv": relpath(OUT_DIR / "obs.csv"),
            "tables": relpath(OUT_DIR / "tables.npz"),
            "certificate": relpath(OUT_DIR / "cert.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "support-count and coefficient-mass probability laws on the current compressed active raw product family",
                "exact conditional normalization for both scoped laws over horizons 1..16",
                "exact mixed-horizon normalization for both scoped laws",
                "sample-average variance shrinkage and law-of-total-variance decomposition for both scoped laws",
                "the full raw-support gap that prevents treating the scoped laws as full raw-support measures in the current ontology",
            ],
            "does_not_certify_because_out_of_scope": [
                "a probability measure on the full raw tensor support independent of the current active-product boundary",
                "materialized rows for every raw address path",
                "exact C985 source/target composability of all raw paths",
                "a genuine horizon-16 long_prof profunctor",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Return to long_h16: use the scoped measure boundary to test whether "
            "a genuine horizon-16 owner/raw profunctor can be materialized or "
            "must remain an explicit current-model obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.measure.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.measure.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "measure": measure_payload,
        "measure_csv": csv_text(MEASURE_COLUMNS, rows["measure_rows"]),
        "dist_csv": csv_text(DIST_COLUMNS, rows["dist_rows"]),
        "moment_csv": csv_text(MOMENT_COLUMNS, rows["moment_rows"]),
        "decomp_csv": csv_text(DECOMP_COLUMNS, rows["decomp_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "measure_table": rows["measure_table"],
        "dist_table": rows["dist_table"],
        "moment_table": rows["moment_table"],
        "decomp_table": rows["decomp_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
        "manifest": manifest,
        "report": report,
        "computed_hashes": {
            "measure_text_sha256": rows["measure_hash"],
            "dist_text_sha256": rows["dist_hash"],
            "moment_text_sha256": rows["moment_hash"],
            "decomp_text_sha256": rows["decomp_hash"],
        },
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
    obligations.sort(key=lambda row: str(row["id"]))
    index = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": obligations,
    }
    index["registry_sha256"] = self_hash(index, "registry_sha256")
    write_json(INDEX_PATH, index)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "measure.json", payloads["measure"])
    (OUT_DIR / "measure.csv").write_text(payloads["measure_csv"], encoding="utf-8")
    (OUT_DIR / "dist.csv").write_text(payloads["dist_csv"], encoding="utf-8")
    (OUT_DIR / "moment.csv").write_text(payloads["moment_csv"], encoding="utf-8")
    (OUT_DIR / "decomp.csv").write_text(payloads["decomp_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        measure_table=payloads["measure_table"],
        dist_table=payloads["dist_table"],
        moment_table=payloads["moment_table"],
        decomp_table=payloads["decomp_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "certificate_sha256": report["certificate_sha256"],
                "computed_hashes": payloads["computed_hashes"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
