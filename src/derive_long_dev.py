from __future__ import annotations

import csv
import hashlib
import json
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
    from .derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
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
    from derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_dev"
STATUS = "LONG_DEV_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_MARKOV_REPORT = LONG_MARKOV_DIR / "report.json"
LONG_MARKOV_KERNEL = LONG_MARKOV_DIR / "kernel.csv"
LONG_MARKOV_STATIONARY = LONG_MARKOV_DIR / "stationary.csv"
LONG_MARKOV_TABLES = LONG_MARKOV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_dev.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_dev.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
SAMPLE_HORIZON = 8
MOMENT_ORDER_MAX = 4
COMPONENT_VALUES = [0, 1, 2]
TILTS = [(0, Fraction(1, 2)), (1, Fraction(2, 1)), (2, Fraction(3, 1))]

DISTRIBUTION_COLUMNS = [
    "sample_count",
    "sum_value",
    "prob_num",
    "prob_den",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "prob_sha256",
]
DISTRIBUTION_DIGEST_COLUMNS = [
    "sample_count",
    "sum_value",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
]
MOMENT_COLUMNS = [
    "sample_count",
    "moment_order",
    "moment_num",
    "moment_den",
    "moment_num_digits",
    "moment_den_digits",
    "moment_num_mod_1000000007",
    "moment_den_mod_1000000007",
    "moment_num_mod_1000000009",
    "moment_den_mod_1000000009",
    "moment_sha256",
]
MOMENT_DIGEST_COLUMNS = [
    "sample_count",
    "moment_order",
    "moment_num_digits",
    "moment_den_digits",
    "moment_num_mod_1000000007",
    "moment_den_mod_1000000007",
    "moment_num_mod_1000000009",
    "moment_den_mod_1000000009",
]
TILT_COLUMNS = [
    "sample_count",
    "tilt_id",
    "q_num",
    "q_den",
    "value_num",
    "value_den",
    "value_num_digits",
    "value_den_digits",
    "value_num_mod_1000000007",
    "value_den_mod_1000000007",
    "value_num_mod_1000000009",
    "value_den_mod_1000000009",
    "value_sha256",
]
TILT_DIGEST_COLUMNS = [
    "sample_count",
    "tilt_id",
    "q_num",
    "q_den",
    "value_num_digits",
    "value_den_digits",
    "value_num_mod_1000000007",
    "value_den_mod_1000000007",
    "value_num_mod_1000000009",
    "value_den_mod_1000000009",
]
TAIL_COLUMNS = [
    "sample_count",
    "tail_id",
    "threshold",
    "prob_num",
    "prob_den",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "prob_sha256",
]
TAIL_DIGEST_COLUMNS = [
    "sample_count",
    "tail_id",
    "threshold",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
]
CHERNOFF_COLUMNS = [
    "sample_count",
    "tail_id",
    "threshold",
    "tilt_id",
    "q_num",
    "q_den",
    "bound_num",
    "bound_den",
    "bound_num_digits",
    "bound_den_digits",
    "bound_num_mod_1000000007",
    "bound_den_mod_1000000007",
    "bound_num_mod_1000000009",
    "bound_den_mod_1000000009",
    "bound_sha256",
    "gap_num",
    "gap_den",
    "gap_num_digits",
    "gap_den_digits",
    "gap_num_mod_1000000007",
    "gap_den_mod_1000000007",
    "gap_num_mod_1000000009",
    "gap_den_mod_1000000009",
    "gap_sha256",
]
CHERNOFF_DIGEST_COLUMNS = [
    "sample_count",
    "tail_id",
    "threshold",
    "tilt_id",
    "q_num",
    "q_den",
    "bound_num_digits",
    "bound_den_digits",
    "bound_num_mod_1000000007",
    "bound_den_mod_1000000007",
    "bound_num_mod_1000000009",
    "bound_den_mod_1000000009",
    "gap_num_digits",
    "gap_den_digits",
    "gap_num_mod_1000000007",
    "gap_den_mod_1000000007",
    "gap_num_mod_1000000009",
    "gap_den_mod_1000000009",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "component_count",
    "component_value_min",
    "component_value_max",
    "sample_horizon",
    "moment_order_max",
    "distribution_row_count",
    "distribution_sum_one_flag",
    "distribution_full_support_flag",
    "distribution_prob_num_digit_max",
    "distribution_prob_den_digit_max",
    "moment_row_count",
    "first_moment_linear_flag",
    "moment_num_digit_max",
    "moment_den_digit_max",
    "tilt_row_count",
    "tilt_count",
    "tilt_num_digit_max",
    "tilt_den_digit_max",
    "tail_row_count",
    "tail_num_digit_max",
    "tail_den_digit_max",
    "chernoff_row_count",
    "chernoff_gap_nonnegative_flag",
    "chernoff_bound_num_digit_max",
    "chernoff_bound_den_digit_max",
    "chernoff_gap_num_digit_max",
    "chernoff_gap_den_digit_max",
    "long_markov_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def table_from_rows(columns: list[str], rows: list[dict[str, int]]) -> np.ndarray:
    return np.asarray(
        [[int(row[column]) for column in columns] for row in rows],
        dtype=np.int64,
    )


def rows_from_table(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def fraction_record(value: Fraction) -> dict[str, int | str]:
    text = f"{value.numerator}/{value.denominator}"
    return {
        "num": value.numerator,
        "den": value.denominator,
        "num_digits": len(str(abs(value.numerator))),
        "den_digits": len(str(value.denominator)),
        "num_mod_1000000007": value.numerator % MOD_PRIMES[0],
        "den_mod_1000000007": value.denominator % MOD_PRIMES[0],
        "num_mod_1000000009": value.numerator % MOD_PRIMES[1],
        "den_mod_1000000009": value.denominator % MOD_PRIMES[1],
        "sha256": hashlib.sha256(text.encode("ascii")).hexdigest(),
    }


def read_kernel() -> list[list[Fraction]]:
    kernel = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    with LONG_MARKOV_KERNEL.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            kernel[int(row["row_component_id"])][int(row["col_component_id"])] = Fraction(
                int(row["prob_num"]),
                int(row["prob_den"]),
            )
    return kernel


def read_stationary() -> list[Fraction]:
    stationary = [Fraction(0) for _ in range(3)]
    with LONG_MARKOV_STATIONARY.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            stationary[int(row["component_id"])] = Fraction(
                int(row["weight_num"]),
                int(row["weight_den"]),
            )
    return stationary


def distribution_fraction_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['sum_value']},{row['prob_num']},{row['prob_den']}\n"
        for row in rows
    )


def moment_fraction_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['moment_order']},{row['moment_num']},{row['moment_den']}\n"
        for row in rows
    )


def tilt_fraction_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['tilt_id']},{row['q_num']},{row['q_den']},"
        f"{row['value_num']},{row['value_den']}\n"
        for row in rows
    )


def tail_fraction_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['tail_id']},{row['threshold']},"
        f"{row['prob_num']},{row['prob_den']}\n"
        for row in rows
    )


def chernoff_fraction_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['tail_id']},{row['threshold']},"
        f"{row['tilt_id']},{row['q_num']},{row['q_den']},"
        f"{row['bound_num']},{row['bound_den']},"
        f"{row['gap_num']},{row['gap_den']}\n"
        for row in rows
    )


def build_distributions(
    kernel: list[list[Fraction]],
    stationary: list[Fraction],
) -> list[dict[int, Fraction]]:
    state_distribution = {
        (component_id, COMPONENT_VALUES[component_id]): stationary[component_id]
        for component_id in range(3)
    }
    distributions: list[dict[int, Fraction]] = []
    for _sample_count in range(1, SAMPLE_HORIZON + 1):
        summed: dict[int, Fraction] = {}
        for (_state, total), probability in state_distribution.items():
            summed[total] = summed.get(total, Fraction(0)) + probability
        distributions.append(summed)

        next_distribution: dict[tuple[int, int], Fraction] = {}
        for (state, total), probability in state_distribution.items():
            for nxt in range(3):
                key = (nxt, total + COMPONENT_VALUES[nxt])
                next_distribution[key] = (
                    next_distribution.get(key, Fraction(0))
                    + probability * kernel[state][nxt]
                )
        state_distribution = next_distribution
    return distributions


def build_rows() -> dict[str, Any]:
    long_markov = load_json(LONG_MARKOV_REPORT)
    kernel = read_kernel()
    stationary = read_stationary()
    distributions = build_distributions(kernel, stationary)
    stationary_mean = Fraction(1405, 1146)

    distribution_rows: list[dict[str, Any]] = []
    distribution_digest_rows: list[dict[str, int]] = []
    for sample_count, distribution in enumerate(distributions, start=1):
        for sum_value in range(0, 2 * sample_count + 1):
            probability = distribution.get(sum_value, Fraction(0))
            record = fraction_record(probability)
            row = {
                "sample_count": sample_count,
                "sum_value": sum_value,
                "prob_num": record["num"],
                "prob_den": record["den"],
                "prob_num_digits": record["num_digits"],
                "prob_den_digits": record["den_digits"],
                "prob_num_mod_1000000007": record["num_mod_1000000007"],
                "prob_den_mod_1000000007": record["den_mod_1000000007"],
                "prob_num_mod_1000000009": record["num_mod_1000000009"],
                "prob_den_mod_1000000009": record["den_mod_1000000009"],
                "prob_sha256": record["sha256"],
            }
            distribution_rows.append(row)
            distribution_digest_rows.append(
                {column: int(row[column]) for column in DISTRIBUTION_DIGEST_COLUMNS}
            )

    moment_rows: list[dict[str, Any]] = []
    moment_digest_rows: list[dict[str, int]] = []
    first_moment_linear = True
    for sample_count, distribution in enumerate(distributions, start=1):
        for moment_order in range(1, MOMENT_ORDER_MAX + 1):
            moment = sum(
                Fraction(sum_value) ** moment_order * probability
                for sum_value, probability in distribution.items()
            )
            if moment_order == 1 and moment != sample_count * stationary_mean:
                first_moment_linear = False
            record = fraction_record(moment)
            row = {
                "sample_count": sample_count,
                "moment_order": moment_order,
                "moment_num": record["num"],
                "moment_den": record["den"],
                "moment_num_digits": record["num_digits"],
                "moment_den_digits": record["den_digits"],
                "moment_num_mod_1000000007": record["num_mod_1000000007"],
                "moment_den_mod_1000000007": record["den_mod_1000000007"],
                "moment_num_mod_1000000009": record["num_mod_1000000009"],
                "moment_den_mod_1000000009": record["den_mod_1000000009"],
                "moment_sha256": record["sha256"],
            }
            moment_rows.append(row)
            moment_digest_rows.append(
                {column: int(row[column]) for column in MOMENT_DIGEST_COLUMNS}
            )

    tilt_rows: list[dict[str, Any]] = []
    tilt_digest_rows: list[dict[str, int]] = []
    for sample_count, distribution in enumerate(distributions, start=1):
        for tilt_id, q_value in TILTS:
            value = sum(
                q_value**sum_value * probability
                for sum_value, probability in distribution.items()
            )
            record = fraction_record(value)
            row = {
                "sample_count": sample_count,
                "tilt_id": tilt_id,
                "q_num": q_value.numerator,
                "q_den": q_value.denominator,
                "value_num": record["num"],
                "value_den": record["den"],
                "value_num_digits": record["num_digits"],
                "value_den_digits": record["den_digits"],
                "value_num_mod_1000000007": record["num_mod_1000000007"],
                "value_den_mod_1000000007": record["den_mod_1000000007"],
                "value_num_mod_1000000009": record["num_mod_1000000009"],
                "value_den_mod_1000000009": record["den_mod_1000000009"],
                "value_sha256": record["sha256"],
            }
            tilt_rows.append(row)
            tilt_digest_rows.append(
                {column: int(row[column]) for column in TILT_DIGEST_COLUMNS}
            )

    tail_rows: list[dict[str, Any]] = []
    tail_digest_rows: list[dict[str, int]] = []
    chernoff_rows: list[dict[str, Any]] = []
    chernoff_digest_rows: list[dict[str, int]] = []
    for sample_count, distribution in enumerate(distributions, start=1):
        tail_specs = [
            (0, sample_count // 2, 0, Fraction(1, 2)),
            (1, (3 * sample_count + 1) // 2, 1, Fraction(2, 1)),
        ]
        for tail_id, threshold, tilt_id, q_value in tail_specs:
            probability = sum(
                value
                for sum_value, value in distribution.items()
                if (sum_value <= threshold if tail_id == 0 else sum_value >= threshold)
            )
            prob_record = fraction_record(probability)
            tail_row = {
                "sample_count": sample_count,
                "tail_id": tail_id,
                "threshold": threshold,
                "prob_num": prob_record["num"],
                "prob_den": prob_record["den"],
                "prob_num_digits": prob_record["num_digits"],
                "prob_den_digits": prob_record["den_digits"],
                "prob_num_mod_1000000007": prob_record["num_mod_1000000007"],
                "prob_den_mod_1000000007": prob_record["den_mod_1000000007"],
                "prob_num_mod_1000000009": prob_record["num_mod_1000000009"],
                "prob_den_mod_1000000009": prob_record["den_mod_1000000009"],
                "prob_sha256": prob_record["sha256"],
            }
            tail_rows.append(tail_row)
            tail_digest_rows.append(
                {column: int(tail_row[column]) for column in TAIL_DIGEST_COLUMNS}
            )

            tilted_moment = sum(
                q_value**sum_value * value
                for sum_value, value in distribution.items()
            )
            bound = tilted_moment / (q_value**threshold)
            gap = bound - probability
            bound_record = fraction_record(bound)
            gap_record = fraction_record(gap)
            chernoff_row = {
                "sample_count": sample_count,
                "tail_id": tail_id,
                "threshold": threshold,
                "tilt_id": tilt_id,
                "q_num": q_value.numerator,
                "q_den": q_value.denominator,
                "bound_num": bound_record["num"],
                "bound_den": bound_record["den"],
                "bound_num_digits": bound_record["num_digits"],
                "bound_den_digits": bound_record["den_digits"],
                "bound_num_mod_1000000007": bound_record["num_mod_1000000007"],
                "bound_den_mod_1000000007": bound_record["den_mod_1000000007"],
                "bound_num_mod_1000000009": bound_record["num_mod_1000000009"],
                "bound_den_mod_1000000009": bound_record["den_mod_1000000009"],
                "bound_sha256": bound_record["sha256"],
                "gap_num": gap_record["num"],
                "gap_den": gap_record["den"],
                "gap_num_digits": gap_record["num_digits"],
                "gap_den_digits": gap_record["den_digits"],
                "gap_num_mod_1000000007": gap_record["num_mod_1000000007"],
                "gap_den_mod_1000000007": gap_record["den_mod_1000000007"],
                "gap_num_mod_1000000009": gap_record["num_mod_1000000009"],
                "gap_den_mod_1000000009": gap_record["den_mod_1000000009"],
                "gap_sha256": gap_record["sha256"],
            }
            chernoff_rows.append(chernoff_row)
            chernoff_digest_rows.append(
                {column: int(chernoff_row[column]) for column in CHERNOFF_DIGEST_COLUMNS}
            )

    obs = {
        "line_point_count": 985,
        "component_count": 3,
        "component_value_min": min(COMPONENT_VALUES),
        "component_value_max": max(COMPONENT_VALUES),
        "sample_horizon": SAMPLE_HORIZON,
        "moment_order_max": MOMENT_ORDER_MAX,
        "distribution_row_count": len(distribution_rows),
        "distribution_sum_one_flag": int(
            all(sum(distribution.values()) == 1 for distribution in distributions)
        ),
        "distribution_full_support_flag": int(
            all(
                all(distribution.get(sum_value, Fraction(0)) > 0 for sum_value in range(2 * sample_count + 1))
                for sample_count, distribution in enumerate(distributions, start=1)
            )
        ),
        "distribution_prob_num_digit_max": max(
            int(row["prob_num_digits"]) for row in distribution_rows
        ),
        "distribution_prob_den_digit_max": max(
            int(row["prob_den_digits"]) for row in distribution_rows
        ),
        "moment_row_count": len(moment_rows),
        "first_moment_linear_flag": int(first_moment_linear),
        "moment_num_digit_max": max(int(row["moment_num_digits"]) for row in moment_rows),
        "moment_den_digit_max": max(int(row["moment_den_digits"]) for row in moment_rows),
        "tilt_row_count": len(tilt_rows),
        "tilt_count": len(TILTS),
        "tilt_num_digit_max": max(int(row["value_num_digits"]) for row in tilt_rows),
        "tilt_den_digit_max": max(int(row["value_den_digits"]) for row in tilt_rows),
        "tail_row_count": len(tail_rows),
        "tail_num_digit_max": max(int(row["prob_num_digits"]) for row in tail_rows),
        "tail_den_digit_max": max(int(row["prob_den_digits"]) for row in tail_rows),
        "chernoff_row_count": len(chernoff_rows),
        "chernoff_gap_nonnegative_flag": int(
            all(Fraction(row["gap_num"], row["gap_den"]) >= 0 for row in chernoff_rows)
        ),
        "chernoff_bound_num_digit_max": max(
            int(row["bound_num_digits"]) for row in chernoff_rows
        ),
        "chernoff_bound_den_digit_max": max(
            int(row["bound_den_digits"]) for row in chernoff_rows
        ),
        "chernoff_gap_num_digit_max": max(
            int(row["gap_num_digits"]) for row in chernoff_rows
        ),
        "chernoff_gap_den_digit_max": max(
            int(row["gap_den_digits"]) for row in chernoff_rows
        ),
        "long_markov_input_certified": int(
            long_markov.get("status") == LONG_MARKOV_STATUS
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "long_markov": long_markov,
        "kernel": kernel,
        "stationary": stationary,
        "distributions": distributions,
        "distribution_rows": distribution_rows,
        "distribution_digest_rows": distribution_digest_rows,
        "moment_rows": moment_rows,
        "moment_digest_rows": moment_digest_rows,
        "tilt_rows": tilt_rows,
        "tilt_digest_rows": tilt_digest_rows,
        "tail_rows": tail_rows,
        "tail_digest_rows": tail_digest_rows,
        "chernoff_rows": chernoff_rows,
        "chernoff_digest_rows": chernoff_digest_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    distribution_digest_table = table_from_rows(
        DISTRIBUTION_DIGEST_COLUMNS,
        rows["distribution_digest_rows"],
    )
    moment_digest_table = table_from_rows(
        MOMENT_DIGEST_COLUMNS,
        rows["moment_digest_rows"],
    )
    tilt_digest_table = table_from_rows(
        TILT_DIGEST_COLUMNS,
        rows["tilt_digest_rows"],
    )
    tail_digest_table = table_from_rows(
        TAIL_DIGEST_COLUMNS,
        rows["tail_digest_rows"],
    )
    chernoff_digest_table = table_from_rows(
        CHERNOFF_DIGEST_COLUMNS,
        rows["chernoff_digest_rows"],
    )
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])

    distribution_hash = hashlib.sha256(
        distribution_fraction_text(rows["distribution_rows"]).encode("ascii")
    ).hexdigest()
    moment_hash = hashlib.sha256(
        moment_fraction_text(rows["moment_rows"]).encode("ascii")
    ).hexdigest()
    tilt_hash = hashlib.sha256(
        tilt_fraction_text(rows["tilt_rows"]).encode("ascii")
    ).hexdigest()
    tail_hash = hashlib.sha256(
        tail_fraction_text(rows["tail_rows"]).encode("ascii")
    ).hexdigest()
    chernoff_hash = hashlib.sha256(
        chernoff_fraction_text(rows["chernoff_rows"]).encode("ascii")
    ).hexdigest()
    checks = {
        "input_certified": obs["long_markov_input_certified"] == 1,
        "distribution_fingerprint_exact": (
            obs["distribution_row_count"],
            obs["distribution_sum_one_flag"],
            obs["distribution_full_support_flag"],
            obs["distribution_prob_num_digit_max"],
            obs["distribution_prob_den_digit_max"],
            distribution_hash,
        )
        == (
            80,
            1,
            1,
            1_819,
            1_820,
            "9298c8d0100769d65e0432c21d09c37e48ddb718475d5f532bfc65e81ff5b66e",
        ),
        "moment_fingerprint_exact": (
            obs["moment_row_count"],
            obs["moment_order_max"],
            obs["first_moment_linear_flag"],
            obs["moment_num_digit_max"],
            obs["moment_den_digit_max"],
            moment_hash,
        )
        == (
            32,
            4,
            1,
            1_835,
            1_831,
            "3a6e0b3831d10559fe27508ca1196a53b72d10d9e2f2e38999eff837a77c0838",
        ),
        "tilt_fingerprint_exact": (
            obs["tilt_row_count"],
            obs["tilt_count"],
            obs["tilt_num_digit_max"],
            obs["tilt_den_digit_max"],
            tilt_hash,
        )
        == (
            24,
            3,
            1_835,
            1_833,
            "7513e77f2b3601a7d26b3cb3d0dea1131f4836975e811225354b02b8b86639ce",
        ),
        "tail_fingerprint_exact": (
            obs["tail_row_count"],
            obs["tail_num_digit_max"],
            obs["tail_den_digit_max"],
            tail_hash,
        )
        == (
            16,
            1_814,
            1_814,
            "4002870068ef1f0f5989e4765524800e536cdd1b76b55fc6626e4e4bc4487bfb",
        ),
        "chernoff_fingerprint_exact": (
            obs["chernoff_row_count"],
            obs["chernoff_gap_nonnegative_flag"],
            obs["chernoff_bound_num_digit_max"],
            obs["chernoff_bound_den_digit_max"],
            obs["chernoff_gap_num_digit_max"],
            obs["chernoff_gap_den_digit_max"],
            chernoff_hash,
        )
        == (
            16,
            1,
            1_835,
            1_834,
            1_835,
            1_834,
            "d74e1e0c3c973175017decb4e79577445b85fec2f745aa4667994ac2328c3550",
        ),
        "table_shapes_match": (
            tuple(distribution_digest_table.shape),
            tuple(moment_digest_table.shape),
            tuple(tilt_digest_table.shape),
            tuple(tail_digest_table.shape),
            tuple(chernoff_digest_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (80, len(DISTRIBUTION_DIGEST_COLUMNS)),
            (32, len(MOMENT_DIGEST_COLUMNS)),
            (24, len(TILT_DIGEST_COLUMNS)),
            (16, len(TAIL_DIGEST_COLUMNS)),
            (16, len(CHERNOFF_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "long_markov_finite_path_sum_deviation_kernel",
        "scope": {
            "source": "long_markov reversible boundary kernel",
            "observable": "component_value in {0,1,2}",
            "sample_horizon": SAMPLE_HORIZON,
            "tail_rules": {
                "lower_tail": "S_n <= floor(n/2), bounded with q=1/2",
                "upper_tail": "S_n >= ceil(3n/2), bounded with q=2",
            },
        },
        "distribution": {
            "row_count": obs["distribution_row_count"],
            "sum_one": bool(obs["distribution_sum_one_flag"]),
            "full_support": bool(obs["distribution_full_support_flag"]),
            "fraction_text_sha256": distribution_hash,
            "digest_table_sha256": sha_array(distribution_digest_table),
        },
        "moments": {
            "row_count": obs["moment_row_count"],
            "moment_order_max": MOMENT_ORDER_MAX,
            "first_moment_linear": bool(obs["first_moment_linear_flag"]),
            "fraction_text_sha256": moment_hash,
            "digest_table_sha256": sha_array(moment_digest_table),
        },
        "tilts": {
            "tilt_values": [
                {"tilt_id": tilt_id, "q_num": q.numerator, "q_den": q.denominator}
                for tilt_id, q in TILTS
            ],
            "fraction_text_sha256": tilt_hash,
            "digest_table_sha256": sha_array(tilt_digest_table),
        },
        "tails": {
            "row_count": obs["tail_row_count"],
            "fraction_text_sha256": tail_hash,
            "digest_table_sha256": sha_array(tail_digest_table),
        },
        "chernoff": {
            "row_count": obs["chernoff_row_count"],
            "gap_nonnegative": bool(obs["chernoff_gap_nonnegative_flag"]),
            "fraction_text_sha256": chernoff_hash,
            "digest_table_sha256": sha_array(chernoff_digest_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    dev = {
        "schema": "long.dev@1",
        "object": "long_markov_finite_path_sum_deviation_kernel",
        "status": STATUS if all(checks.values()) else "LONG_DEV_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.dev.report@1",
        "status": dev["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_dev certifies the exact finite path-sum laws of the "
            "long_markov boundary observable through horizon 8, raw moment "
            "fingerprints through order 4, tilted moment generating "
            "fingerprints for q=1/2,2,3, and explicit finite Chernoff-style "
            "tail bounds with nonnegative exact gaps."
        ),
        "stage_protocol": {
            "draft": "take long_markov's exact kernel and stationary law",
            "witness": "dynamic-program exact distributions for S_n through n=8",
            "coherence": "check distribution sums, support, moments, tilts, tails, Chernoff gaps, and hashes",
            "closure": "emit distribution, moment, tilt, tail, Chernoff, table, certificate, manifest, and report artifacts",
            "emit": "write long_dev artifacts and verifier hook",
        },
        "inputs": {
            "long_markov_report": input_entry(
                LONG_MARKOV_REPORT,
                {"status": rows["long_markov"].get("status")},
            ),
            "long_markov_kernel": input_entry(LONG_MARKOV_KERNEL),
            "long_markov_stationary": input_entry(LONG_MARKOV_STATIONARY),
            "long_markov_tables": input_entry(LONG_MARKOV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "dev": relpath(OUT_DIR / "dev.json"),
            "distribution_csv": relpath(OUT_DIR / "distribution.csv"),
            "moment_csv": relpath(OUT_DIR / "moment.csv"),
            "tilt_csv": relpath(OUT_DIR / "tilt.csv"),
            "tail_csv": relpath(OUT_DIR / "tail.csv"),
            "chernoff_csv": relpath(OUT_DIR / "chernoff.csv"),
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
                "the exact finite distribution of S_n through n=8",
                "raw moments through order four for each finite horizon",
                "tilted moment generating fingerprints at q=1/2, q=2, and q=3",
                "finite Chernoff-style lower and upper tail bounds with exact nonnegative gaps",
            ],
            "does_not_certify_because_out_of_scope": [
                "optimized continuous Chernoff rates over all q",
                "asymptotic large-deviation principles",
                "support-changing recouplings outside the long_rec owner graph",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_prof: package the long-chain kernels as explicit finite "
            "profunctors between line, owner, boundary, Markov, and deviation "
            "addresses so the LLN derivation can be read as tensor lookup composition."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.dev.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.dev.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "dev": dev,
        "distribution_csv": csv_text(DISTRIBUTION_COLUMNS, rows["distribution_rows"]),
        "moment_csv": csv_text(MOMENT_COLUMNS, rows["moment_rows"]),
        "tilt_csv": csv_text(TILT_COLUMNS, rows["tilt_rows"]),
        "tail_csv": csv_text(TAIL_COLUMNS, rows["tail_rows"]),
        "chernoff_csv": csv_text(CHERNOFF_COLUMNS, rows["chernoff_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "distribution_digest_table": distribution_digest_table,
        "moment_digest_table": moment_digest_table,
        "tilt_digest_table": tilt_digest_table,
        "tail_digest_table": tail_digest_table,
        "chernoff_digest_table": chernoff_digest_table,
        "observable_table": obs_table,
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
    write_json(OUT_DIR / "dev.json", payloads["dev"])
    (OUT_DIR / "distribution.csv").write_text(
        payloads["distribution_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "moment.csv").write_text(payloads["moment_csv"], encoding="utf-8")
    (OUT_DIR / "tilt.csv").write_text(payloads["tilt_csv"], encoding="utf-8")
    (OUT_DIR / "tail.csv").write_text(payloads["tail_csv"], encoding="utf-8")
    (OUT_DIR / "chernoff.csv").write_text(
        payloads["chernoff_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        distribution_digest_table=payloads["distribution_digest_table"],
        moment_digest_table=payloads["moment_digest_table"],
        tilt_digest_table=payloads["tilt_digest_table"],
        tail_digest_table=payloads["tail_digest_table"],
        chernoff_digest_table=payloads["chernoff_digest_table"],
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
