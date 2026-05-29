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
    from .derive_long_dual import (
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_DUAL_DIR,
        STATUS as LONG_DUAL_STATUS,
    )
    from .derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from .derive_long_path import STATUS as LONG_PATH_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_dual import (
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        OUT_DIR as LONG_DUAL_DIR,
        STATUS as LONG_DUAL_STATUS,
    )
    from derive_long_raw import (
        csv_text,
        digest_text,
        int_rows,
        read_csv_rows,
        rows_from_table,
        table_from_rows,
    )
    from derive_long_path import STATUS as LONG_PATH_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_prob"
STATUS = "LONG_PROB_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
LONG_DUAL_REPORT = LONG_DUAL_DIR / "report.json"
LONG_DUAL_PATH = LONG_DUAL_DIR / "path.csv"
LONG_DUAL_TABLES = LONG_DUAL_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_prob.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_prob.py"

DIST_TEXT_HASH = "7fcd64d08f6cd9aaaf7ecc520d25bd5291f34b3b01857497e8f355e0eba74c27"
MOMENT_TEXT_HASH = "ffcb67a74049913d491a295fb53fe7b39312309feb6f2a2ebbd29f75740f8a31"
DECOMP_TEXT_HASH = "0dbafa8cf95b7c6a6c4b6d70ea318683b184db67a793dadd376974f84d1638db"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
COMPONENT_WEIGHTS = (12, 18, 48)

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


DIST_COLUMNS = [
    "path_id",
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "average_num",
    "average_den",
    "weight_digits",
    "weight_mod_1000000007",
    "weight_mod_1000000009",
    *prefixed_fraction_columns("conditional_prob"),
    *prefixed_fraction_columns("global_prob"),
]
MOMENT_COLUMNS = [
    "sample_count",
    "path_count",
    "sum_value_min",
    "sum_value_max",
    "weight_total_digits",
    "weight_total_mod_1000000007",
    "weight_total_mod_1000000009",
    *prefixed_fraction_columns("mean_sum"),
    *prefixed_fraction_columns("variance_sum"),
    *prefixed_fraction_columns("mean_average"),
    *prefixed_fraction_columns("variance_average"),
    *prefixed_fraction_columns("variance_shrink_gap"),
    "variance_shrink_from_prev_flag",
]
DECOMP_COLUMNS = [
    "decomp_id",
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
    "distribution_row_count",
    "moment_row_count",
    "decomp_row_count",
    "path_count",
    "sample_count_min",
    "sample_count_max",
    "weight_total_digits",
    "weight_total_mod_1000000007",
    "weight_total_mod_1000000009",
    "weighted_sum_value_mod_1000000007",
    "weighted_square_sum_value_mod_1000000007",
    "global_mean_num_digits",
    "global_mean_den_digits",
    "global_mean_num_mod_1000000007",
    "global_mean_den_mod_1000000007",
    "global_variance_num_digits",
    "global_variance_den_digits",
    "global_variance_num_mod_1000000007",
    "global_variance_den_mod_1000000007",
    "within_variance_num_mod_1000000007",
    "between_variance_num_mod_1000000007",
    "variance_decomp_flag",
    "variance_shrink_flag_count",
    "variance_shrink_gap_num_mod_sum_1000000007",
    "first_variance_num_mod_1000000007",
    "first_variance_den_mod_1000000007",
    "last_variance_num_mod_1000000007",
    "last_variance_den_mod_1000000007",
    "current_dual_probability_flag",
    "current_conditional_lln_shrink_flag",
    "current_variance_decomp_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def fraction_record(value: Fraction) -> dict[str, int]:
    return {
        "num_digits": len(str(abs(value.numerator))),
        "den_digits": len(str(value.denominator)),
        "num_mod_1000000007": value.numerator % MOD_PRIMES[0],
        "den_mod_1000000007": value.denominator % MOD_PRIMES[0],
        "num_mod_1000000009": value.numerator % MOD_PRIMES[1],
        "den_mod_1000000009": value.denominator % MOD_PRIMES[1],
    }


def prefixed_fraction_fields(prefix: str, value: Fraction) -> dict[str, int]:
    record = fraction_record(value)
    return {f"{prefix}_{key}": int(record[key]) for key in FRACTION_FIELDS}


def path_weight(row: dict[str, int]) -> int:
    return (
        COMPONENT_WEIGHTS[0] ** row["count_component0"]
        * COMPONENT_WEIGHTS[1] ** row["count_component1"]
        * COMPONENT_WEIGHTS[2] ** row["count_component2"]
    )


def load_inputs() -> dict[str, Any]:
    dual_rows = int_rows(read_csv_rows(LONG_DUAL_PATH))
    path_rows = int_rows(read_csv_rows(LONG_PATH_PATH))
    input_reports = {
        "long_dual": load_json(LONG_DUAL_REPORT),
        "long_path": load_json(LONG_PATH_REPORT),
    }
    return {
        "dual_rows": dual_rows,
        "path_rows": path_rows,
        "input_reports": input_reports,
    }


def build_measure_rows(
    dual_rows: list[dict[str, int]],
    path_rows: list[dict[str, int]],
) -> tuple[list[dict[str, int]], dict[int, list[dict[str, Any]]], int]:
    path_by_id = {row["path_id"]: row for row in path_rows}
    weights: dict[int, int] = {}
    for row in dual_rows:
        weight = path_weight(row)
        weights[row["path_id"]] = weight
        if weight % MOD_PRIMES[0] != row["dual_coeff_product_mod_1000000007"]:
            raise AssertionError("dual weight mod 1000000007 mismatch")
        if weight % MOD_PRIMES[1] != row["dual_coeff_product_mod_1000000009"]:
            raise AssertionError("dual weight mod 1000000009 mismatch")
    total_weight = sum(weights.values())
    sample_groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for path_id, weight in weights.items():
        path = path_by_id[path_id]
        sample_groups[path["sample_count"]].append(
            {
                "path_id": path_id,
                "fiber_row_id": path["fiber_row_id"],
                "sample_count": path["sample_count"],
                "sum_value": path["sum_value"],
                "weight": weight,
            }
        )
    rows: list[dict[str, int]] = []
    for sample_count in sorted(sample_groups):
        group = sorted(sample_groups[sample_count], key=lambda row: row["sum_value"])
        sample_weight = sum(row["weight"] for row in group)
        for row in group:
            conditional = Fraction(row["weight"], sample_weight)
            global_prob = Fraction(row["weight"], total_weight)
            out = {
                "path_id": row["path_id"],
                "fiber_row_id": row["fiber_row_id"],
                "sample_count": row["sample_count"],
                "sum_value": row["sum_value"],
                "average_num": row["sum_value"],
                "average_den": row["sample_count"],
                "weight_digits": len(str(row["weight"])),
                "weight_mod_1000000007": row["weight"] % MOD_PRIMES[0],
                "weight_mod_1000000009": row["weight"] % MOD_PRIMES[1],
            }
            out.update(prefixed_fraction_fields("conditional_prob", conditional))
            out.update(prefixed_fraction_fields("global_prob", global_prob))
            rows.append(out)
    return rows, sample_groups, total_weight


def build_moment_rows(
    sample_groups: dict[int, list[dict[str, Any]]]
) -> tuple[list[dict[str, int]], dict[int, dict[str, Any]]]:
    rows: list[dict[str, int]] = []
    records: dict[int, dict[str, Any]] = {}
    previous_variance_average = Fraction(0)
    for sample_count in sorted(sample_groups):
        group = sample_groups[sample_count]
        weight_total = sum(row["weight"] for row in group)
        weighted_sum = sum(row["sum_value"] * row["weight"] for row in group)
        weighted_square = sum(
            row["sum_value"] * row["sum_value"] * row["weight"] for row in group
        )
        mean_sum = Fraction(weighted_sum, weight_total)
        variance_sum = Fraction(weighted_square, weight_total) - mean_sum * mean_sum
        mean_average = mean_sum / sample_count
        variance_average = variance_sum / (sample_count * sample_count)
        shrink_gap = (
            Fraction(0)
            if sample_count == min(sample_groups)
            else previous_variance_average - variance_average
        )
        shrink_flag = int(sample_count == min(sample_groups) or shrink_gap > 0)
        row = {
            "sample_count": sample_count,
            "path_count": len(group),
            "sum_value_min": min(row["sum_value"] for row in group),
            "sum_value_max": max(row["sum_value"] for row in group),
            "weight_total_digits": len(str(weight_total)),
            "weight_total_mod_1000000007": weight_total % MOD_PRIMES[0],
            "weight_total_mod_1000000009": weight_total % MOD_PRIMES[1],
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
            "shrink_gap": shrink_gap,
        }
        previous_variance_average = variance_average
    return rows, records


def build_decomp_rows(
    sample_groups: dict[int, list[dict[str, Any]]],
    moment_records: dict[int, dict[str, Any]],
    total_weight: int,
) -> tuple[list[dict[str, int]], dict[str, Fraction]]:
    weighted_mean = sum(
        Fraction(row["sum_value"], row["sample_count"]) * row["weight"]
        for group in sample_groups.values()
        for row in group
    )
    weighted_second = sum(
        Fraction(row["sum_value"] * row["sum_value"], row["sample_count"] * row["sample_count"])
        * row["weight"]
        for group in sample_groups.values()
        for row in group
    )
    global_mean = weighted_mean / total_weight
    global_variance = weighted_second / total_weight - global_mean * global_mean
    within = sum(
        Fraction(record["weight_total"], total_weight) * record["variance_average"]
        for record in moment_records.values()
    )
    between = sum(
        Fraction(record["weight_total"], total_weight)
        * (record["mean_average"] - global_mean)
        * (record["mean_average"] - global_mean)
        for record in moment_records.values()
    )
    decomp_gap = global_variance - within - between
    row = {
        "decomp_id": 0,
        "path_count": sum(len(group) for group in sample_groups.values()),
        "weight_total_digits": len(str(total_weight)),
        "weight_total_mod_1000000007": total_weight % MOD_PRIMES[0],
        "weight_total_mod_1000000009": total_weight % MOD_PRIMES[1],
        "variance_decomp_flag": int(decomp_gap == 0),
    }
    row.update(prefixed_fraction_fields("global_mean_average", global_mean))
    row.update(prefixed_fraction_fields("global_variance_average", global_variance))
    row.update(prefixed_fraction_fields("within_variance_average", within))
    row.update(prefixed_fraction_fields("between_variance_average", between))
    row.update(prefixed_fraction_fields("variance_decomp_gap", decomp_gap))
    return [row], {
        "global_mean": global_mean,
        "global_variance": global_variance,
        "within_variance": within,
        "between_variance": between,
        "decomp_gap": decomp_gap,
    }


def build_rows() -> dict[str, Any]:
    loaded = load_inputs()
    dist_rows, sample_groups, total_weight = build_measure_rows(
        loaded["dual_rows"], loaded["path_rows"]
    )
    moment_rows, moment_records = build_moment_rows(sample_groups)
    decomp_rows, decomp = build_decomp_rows(sample_groups, moment_records, total_weight)
    weighted_sum_value = sum(
        row["sum_value"] * row["weight"]
        for group in sample_groups.values()
        for row in group
    )
    weighted_square_sum_value = sum(
        row["sum_value"] * row["sum_value"] * row["weight"]
        for group in sample_groups.values()
        for row in group
    )
    first_variance = moment_records[min(moment_records)]["variance_average"]
    last_variance = moment_records[max(moment_records)]["variance_average"]
    obs = {
        "distribution_row_count": len(dist_rows),
        "moment_row_count": len(moment_rows),
        "decomp_row_count": len(decomp_rows),
        "path_count": len(dist_rows),
        "sample_count_min": min(sample_groups),
        "sample_count_max": max(sample_groups),
        "weight_total_digits": len(str(total_weight)),
        "weight_total_mod_1000000007": total_weight % MOD_PRIMES[0],
        "weight_total_mod_1000000009": total_weight % MOD_PRIMES[1],
        "weighted_sum_value_mod_1000000007": weighted_sum_value % MOD_PRIMES[0],
        "weighted_square_sum_value_mod_1000000007": weighted_square_sum_value
        % MOD_PRIMES[0],
        "global_mean_num_digits": len(str(abs(decomp["global_mean"].numerator))),
        "global_mean_den_digits": len(str(decomp["global_mean"].denominator)),
        "global_mean_num_mod_1000000007": decomp["global_mean"].numerator
        % MOD_PRIMES[0],
        "global_mean_den_mod_1000000007": decomp["global_mean"].denominator
        % MOD_PRIMES[0],
        "global_variance_num_digits": len(
            str(abs(decomp["global_variance"].numerator))
        ),
        "global_variance_den_digits": len(str(decomp["global_variance"].denominator)),
        "global_variance_num_mod_1000000007": decomp[
            "global_variance"
        ].numerator
        % MOD_PRIMES[0],
        "global_variance_den_mod_1000000007": decomp[
            "global_variance"
        ].denominator
        % MOD_PRIMES[0],
        "within_variance_num_mod_1000000007": decomp["within_variance"].numerator
        % MOD_PRIMES[0],
        "between_variance_num_mod_1000000007": decomp[
            "between_variance"
        ].numerator
        % MOD_PRIMES[0],
        "variance_decomp_flag": int(decomp["decomp_gap"] == 0),
        "variance_shrink_flag_count": sum(
            row["variance_shrink_from_prev_flag"] for row in moment_rows
        ),
        "variance_shrink_gap_num_mod_sum_1000000007": sum(
            row["variance_shrink_gap_num_mod_1000000007"] for row in moment_rows
        )
        % MOD_PRIMES[0],
        "first_variance_num_mod_1000000007": first_variance.numerator
        % MOD_PRIMES[0],
        "first_variance_den_mod_1000000007": first_variance.denominator
        % MOD_PRIMES[0],
        "last_variance_num_mod_1000000007": last_variance.numerator
        % MOD_PRIMES[0],
        "last_variance_den_mod_1000000007": last_variance.denominator
        % MOD_PRIMES[0],
        "current_dual_probability_flag": 1,
        "current_conditional_lln_shrink_flag": int(
            sum(row["variance_shrink_from_prev_flag"] for row in moment_rows)
            == len(moment_rows)
        ),
        "current_variance_decomp_flag": int(decomp["decomp_gap"] == 0),
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
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
        "input_reports": loaded["input_reports"],
        "dist_rows": dist_rows,
        "moment_rows": moment_rows,
        "decomp_rows": decomp_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "exact": {
            "total_weight": str(total_weight),
            "global_mean": f"{decomp['global_mean'].numerator}/{decomp['global_mean'].denominator}",
            "global_variance": f"{decomp['global_variance'].numerator}/{decomp['global_variance'].denominator}",
            "within_variance": f"{decomp['within_variance'].numerator}/{decomp['within_variance'].denominator}",
            "between_variance": f"{decomp['between_variance'].numerator}/{decomp['between_variance'].denominator}",
            "variance_decomp_gap": f"{decomp['decomp_gap'].numerator}/{decomp['decomp_gap'].denominator}",
            "first_variance": f"{first_variance.numerator}/{first_variance.denominator}",
            "last_variance": f"{last_variance.numerator}/{last_variance.denominator}",
        },
        "dist_table": table_from_rows(DIST_COLUMNS, dist_rows),
        "moment_table": table_from_rows(MOMENT_COLUMNS, moment_rows),
        "decomp_table": table_from_rows(DECOMP_COLUMNS, decomp_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "dist_hash": dist_hash,
        "moment_hash": moment_hash,
        "decomp_hash": decomp_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_dual"].get("status"),
            input_reports["long_path"].get("status"),
        )
        == (LONG_DUAL_STATUS, LONG_PATH_STATUS),
        "distribution_exact": (
            obs["distribution_row_count"],
            obs["path_count"],
            obs["sample_count_min"],
            obs["sample_count_max"],
            obs["weight_total_digits"],
            obs["weight_total_mod_1000000007"],
            obs["weight_total_mod_1000000009"],
            obs["weighted_sum_value_mod_1000000007"],
            obs["weighted_square_sum_value_mod_1000000007"],
            rows["dist_hash"],
        )
        == (
            288,
            288,
            1,
            16,
            28,
            497_101_086,
            118_327_119,
            558_093_655,
            610_560_676,
            DIST_TEXT_HASH,
        ),
        "moment_curve_exact": (
            obs["moment_row_count"],
            obs["variance_shrink_flag_count"],
            obs["variance_shrink_gap_num_mod_sum_1000000007"],
            obs["first_variance_num_mod_1000000007"],
            obs["first_variance_den_mod_1000000007"],
            obs["last_variance_num_mod_1000000007"],
            obs["last_variance_den_mod_1000000007"],
            obs["current_conditional_lln_shrink_flag"],
            rows["moment_hash"],
        )
        == (
            16,
            16,
            956_356_567,
            94,
            169,
            923_295_380,
            269_357_187,
            1,
            MOMENT_TEXT_HASH,
        ),
        "variance_decomposition_exact": (
            obs["decomp_row_count"],
            obs["global_mean_num_digits"],
            obs["global_mean_den_digits"],
            obs["global_mean_num_mod_1000000007"],
            obs["global_mean_den_mod_1000000007"],
            obs["global_variance_num_digits"],
            obs["global_variance_den_digits"],
            obs["global_variance_num_mod_1000000007"],
            obs["global_variance_den_mod_1000000007"],
            obs["within_variance_num_mod_1000000007"],
            obs["between_variance_num_mod_1000000007"],
            obs["variance_decomp_flag"],
            obs["current_variance_decomp_flag"],
            rows["decomp_hash"],
        )
        == (
            1,
            31,
            31,
            102_643_987,
            665_153_007,
            58,
            61,
            328_754_671,
            624_142_416,
            18_093_641,
            732_540_241,
            1,
            1,
            DECOMP_TEXT_HASH,
        ),
        "current_representation_exact": (
            obs["current_dual_probability_flag"],
            obs["current_conditional_lln_shrink_flag"],
            obs["current_variance_decomp_flag"],
        )
        == (1, 1, 1),
        "table_shapes_match": (
            tuple(rows["dist_table"].shape),
            tuple(rows["moment_table"].shape),
            tuple(rows["decomp_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (288, len(DIST_COLUMNS)),
            (16, len(MOMENT_COLUMNS)),
            (1, len(DECOMP_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "dual_coefficient_probability_lln_curve",
        "measure": {
            "component_weights": list(COMPONENT_WEIGHTS),
            "path_count": obs["path_count"],
            "sample_count_min": obs["sample_count_min"],
            "sample_count_max": obs["sample_count_max"],
            "total_weight_decimal": rows["exact"]["total_weight"],
            "total_weight_mod_1000000007": obs["weight_total_mod_1000000007"],
            "total_weight_mod_1000000009": obs["weight_total_mod_1000000009"],
            "distribution_table_sha256": sha_array(rows["dist_table"]),
            "distribution_text_sha256": rows["dist_hash"],
        },
        "conditional_lln_curve": {
            "moment_row_count": obs["moment_row_count"],
            "variance_shrink_flag_count": obs["variance_shrink_flag_count"],
            "first_variance": rows["exact"]["first_variance"],
            "last_variance": rows["exact"]["last_variance"],
            "moment_table_sha256": sha_array(rows["moment_table"]),
            "moment_text_sha256": rows["moment_hash"],
        },
        "variance_decomposition": {
            "global_mean": rows["exact"]["global_mean"],
            "global_variance": rows["exact"]["global_variance"],
            "within_variance": rows["exact"]["within_variance"],
            "between_variance": rows["exact"]["between_variance"],
            "variance_decomp_gap": rows["exact"]["variance_decomp_gap"],
            "variance_decomp_flag": bool(obs["variance_decomp_flag"]),
            "decomp_table_sha256": sha_array(rows["decomp_table"]),
            "decomp_text_sha256": rows["decomp_hash"],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    prob_payload = {
        "schema": "long.prob@1",
        "object": "dual_coefficient_probability_lln_curve",
        "status": STATUS if all(checks.values()) else "LONG_PROB_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.prob.report@1",
        "status": prob_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_prob normalizes the long_dual coefficient kernel into a "
            "finite path probability measure. Conditional on sample count, "
            "the variance of sum_value/sample_count strictly shrinks across "
            "the 1..16 witness chain, and the global variance decomposes "
            "exactly into within-sample and between-sample components."
        ),
        "stage_protocol": {
            "draft": "read long_dual path weights and long_path value coordinates",
            "witness": "normalize positive coefficient-dual products into exact rational path probabilities",
            "coherence": "check conditional moment curve, strict variance shrinkage, global variance decomposition, statuses, hashes, and shapes",
            "closure": "emit finite probability LLN curve over witness paths",
            "emit": "write long_prob artifacts and verifier hook",
        },
        "inputs": {
            "long_dual_report": input_entry(
                LONG_DUAL_REPORT,
                {"status": rows["input_reports"]["long_dual"].get("status")},
            ),
            "long_dual_path": input_entry(LONG_DUAL_PATH),
            "long_dual_tables": input_entry(LONG_DUAL_TABLES),
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {"status": rows["input_reports"]["long_path"].get("status")},
            ),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "prob": relpath(OUT_DIR / "prob.json"),
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
                "positive coefficient-dual normalization on all 288 witness paths",
                "conditional finite LLN shrinkage for the sample-average coordinate over sample counts 1..16",
                "exact law-of-total-variance decomposition into within-sample and between-sample terms",
            ],
            "does_not_certify_because_out_of_scope": [
                "a probability measure on the full raw tensor support",
                "semantic C985 associator composition",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_mart: derive the finite conditional expectation "
            "operator behind the dual probability curve and test martingale "
            "or supermartingale structure for the sample-average variance."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.prob.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.prob.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "prob": prob_payload,
        "dist_csv": csv_text(DIST_COLUMNS, rows["dist_rows"]),
        "moment_csv": csv_text(MOMENT_COLUMNS, rows["moment_rows"]),
        "decomp_csv": csv_text(DECOMP_COLUMNS, rows["decomp_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "dist_table": rows["dist_table"],
        "moment_table": rows["moment_table"],
        "decomp_table": rows["decomp_table"],
        "observable_table": rows["observable_table"],
        "cert": cert,
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
    write_json(OUT_DIR / "prob.json", payloads["prob"])
    (OUT_DIR / "dist.csv").write_text(payloads["dist_csv"], encoding="utf-8")
    (OUT_DIR / "moment.csv").write_text(payloads["moment_csv"], encoding="utf-8")
    (OUT_DIR / "decomp.csv").write_text(payloads["decomp_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        dist_table=payloads["dist_table"],
        moment_table=payloads["moment_table"],
        decomp_table=payloads["decomp_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
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
                "certificate_sha256": report["certificate_sha256"],
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
