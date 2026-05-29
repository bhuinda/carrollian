from __future__ import annotations

import csv
import hashlib
import json
import math
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
    from .derive_long_absorb import OUT_DIR as LONG_ABSORB_DIR
    from .derive_long_spec import (
        OUT_DIR as LONG_SPEC_DIR,
        STATUS as LONG_SPEC_STATUS,
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
    from derive_long_absorb import OUT_DIR as LONG_ABSORB_DIR
    from derive_long_spec import (
        OUT_DIR as LONG_SPEC_DIR,
        STATUS as LONG_SPEC_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_markov"
STATUS = "LONG_MARKOV_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_ABSORB_MATRIX = LONG_ABSORB_DIR / "matrix.csv"
LONG_SPEC_REPORT = LONG_SPEC_DIR / "report.json"
LONG_SPEC_TABLES = LONG_SPEC_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_markov.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_markov.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
POWER_HORIZON = 8
COMPONENT_VALUES = [Fraction(0), Fraction(1), Fraction(2)]
SPECTRAL_NAMES = [
    "trace",
    "principal_minor_sum",
    "determinant",
    "nontrivial_sum",
    "nontrivial_product",
    "nontrivial_discriminant",
]

KERNEL_COLUMNS = [
    "row_component_id",
    "col_component_id",
    "prob_num",
    "prob_den",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "prob_sha256",
    "diagonal_flag",
]
KERNEL_DIGEST_COLUMNS = [
    "row_component_id",
    "col_component_id",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "diagonal_flag",
]
STATIONARY_COLUMNS = [
    "component_id",
    "component_value",
    "weight_num",
    "weight_den",
    "weight_num_digits",
    "weight_den_digits",
    "weight_num_mod_1000000007",
    "weight_den_mod_1000000007",
    "weight_num_mod_1000000009",
    "weight_den_mod_1000000009",
    "weight_sha256",
]
SPECTRAL_COLUMNS = [
    "invariant_id",
    "invariant_name",
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
SPECTRAL_DIGEST_COLUMNS = [
    "invariant_id",
    "value_num_digits",
    "value_den_digits",
    "value_num_mod_1000000007",
    "value_den_mod_1000000007",
    "value_num_mod_1000000009",
    "value_den_mod_1000000009",
]
POWER_DIGEST_COLUMNS = [
    "power",
    "row_component_id",
    "col_component_id",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
]
COVARIANCE_COLUMNS = [
    "lag",
    "cov_num",
    "cov_den",
    "cov_num_digits",
    "cov_den_digits",
    "cov_num_mod_1000000007",
    "cov_den_mod_1000000007",
    "cov_num_mod_1000000009",
    "cov_den_mod_1000000009",
    "cov_sha256",
]
COVARIANCE_DIGEST_COLUMNS = [
    "lag",
    "cov_num_digits",
    "cov_den_digits",
    "cov_num_mod_1000000007",
    "cov_den_mod_1000000007",
    "cov_num_mod_1000000009",
    "cov_den_mod_1000000009",
]
MEAN_VARIANCE_COLUMNS = [
    "sample_count",
    "variance_num",
    "variance_den",
    "variance_num_digits",
    "variance_den_digits",
    "variance_num_mod_1000000007",
    "variance_den_mod_1000000007",
    "variance_num_mod_1000000009",
    "variance_den_mod_1000000009",
    "variance_sha256",
]
MEAN_VARIANCE_DIGEST_COLUMNS = [
    "sample_count",
    "variance_num_digits",
    "variance_den_digits",
    "variance_num_mod_1000000007",
    "variance_den_mod_1000000007",
    "variance_num_mod_1000000009",
    "variance_den_mod_1000000009",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "component_count",
    "boundary0_count",
    "boundary1_count",
    "boundary2_count",
    "boundary_total_count",
    "kernel_entry_count",
    "kernel_positive_entry_count",
    "kernel_row_sum_one_flag",
    "stationary_entry_count",
    "stationary_sum_one_flag",
    "stationary_fixed_flag",
    "detailed_balance_flag",
    "power_horizon",
    "power_digest_entry_count",
    "power_row_sum_violation_count",
    "power_stationary_fixed_violation_count",
    "spectral_invariant_count",
    "nontrivial_discriminant_num_digits",
    "nontrivial_discriminant_den_digits",
    "nontrivial_discriminant_num_mod_1000000007",
    "nontrivial_discriminant_den_mod_1000000007",
    "nontrivial_discriminant_positive_flag",
    "nontrivial_discriminant_rational_square_flag",
    "stationary_mean_num_digits",
    "stationary_mean_den_digits",
    "stationary_mean_num_mod_1000000007",
    "stationary_mean_den_mod_1000000007",
    "stationary_variance_num_digits",
    "stationary_variance_den_digits",
    "stationary_variance_num_mod_1000000007",
    "stationary_variance_den_mod_1000000007",
    "autocovariance_count",
    "mean_variance_count",
    "mean_variance_monotone_decrease_flag",
    "mean_variance_first_matches_stationary_flag",
    "long_spec_input_certified",
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


def digest_values(value: Fraction) -> list[int]:
    record = fraction_record(value)
    return [
        int(record["num_digits"]),
        int(record["den_digits"]),
        int(record["num_mod_1000000007"]),
        int(record["den_mod_1000000007"]),
        int(record["num_mod_1000000009"]),
        int(record["den_mod_1000000009"]),
    ]


def read_transfer_matrix() -> list[list[Fraction]]:
    matrix = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    with LONG_ABSORB_MATRIX.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source = int(row["source_component_id"])
            target = int(row["absorbing_component_id"])
            matrix[source][target] = Fraction(int(row["flow_num"]), int(row["flow_den"]))
    return matrix


def matmul(
    left: list[list[Fraction]],
    right: list[list[Fraction]],
) -> list[list[Fraction]]:
    return [
        [
            sum(left[row][mid] * right[mid][col] for mid in range(3))
            for col in range(3)
        ]
        for row in range(3)
    ]


def det3(matrix: list[list[Fraction]]) -> Fraction:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def principal_minor_sum(matrix: list[list[Fraction]]) -> Fraction:
    return (
        matrix[0][0] * matrix[1][1]
        - matrix[0][1] * matrix[1][0]
        + matrix[0][0] * matrix[2][2]
        - matrix[0][2] * matrix[2][0]
        + matrix[1][1] * matrix[2][2]
        - matrix[1][2] * matrix[2][1]
    )


def kernel_fraction_text(kernel_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['row_component_id']},{row['col_component_id']},"
        f"{row['prob_num']},{row['prob_den']}\n"
        for row in kernel_rows
    )


def stationary_fraction_text(stationary_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['component_id']},{row['weight_num']},{row['weight_den']}\n"
        for row in stationary_rows
    )


def detailed_balance_text(
    stationary: list[Fraction],
    kernel: list[list[Fraction]],
) -> str:
    return "".join(
        f"{row},{col},{(stationary[row] * kernel[row][col]).numerator},"
        f"{(stationary[row] * kernel[row][col]).denominator}\n"
        for row in range(3)
        for col in range(3)
    )


def spectral_fraction_text(spectral_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['invariant_id']},{row['invariant_name']},"
        f"{row['value_num']},{row['value_den']}\n"
        for row in spectral_rows
    )


def power_digest_text(power_rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in POWER_DIGEST_COLUMNS) + "\n"
        for row in power_rows
    )


def covariance_fraction_text(covariance_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['lag']},{row['cov_num']},{row['cov_den']}\n"
        for row in covariance_rows
    )


def mean_variance_fraction_text(mean_variance_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['variance_num']},{row['variance_den']}\n"
        for row in mean_variance_rows
    )


def build_rows() -> dict[str, Any]:
    long_spec = load_json(LONG_SPEC_REPORT)
    transfer = read_transfer_matrix()
    boundary = [sum(transfer[row][col] for col in range(3)) for row in range(3)]
    total_boundary = sum(boundary)
    kernel = [
        [transfer[row][col] / boundary[row] for col in range(3)]
        for row in range(3)
    ]
    stationary = [weight / total_boundary for weight in boundary]

    kernel_rows: list[dict[str, Any]] = []
    kernel_digest_rows: list[dict[str, int]] = []
    for row in range(3):
        for col in range(3):
            record = fraction_record(kernel[row][col])
            out_row = {
                "row_component_id": row,
                "col_component_id": col,
                "prob_num": record["num"],
                "prob_den": record["den"],
                "prob_num_digits": record["num_digits"],
                "prob_den_digits": record["den_digits"],
                "prob_num_mod_1000000007": record["num_mod_1000000007"],
                "prob_den_mod_1000000007": record["den_mod_1000000007"],
                "prob_num_mod_1000000009": record["num_mod_1000000009"],
                "prob_den_mod_1000000009": record["den_mod_1000000009"],
                "prob_sha256": record["sha256"],
                "diagonal_flag": int(row == col),
            }
            kernel_rows.append(out_row)
            kernel_digest_rows.append(
                {column: int(out_row[column]) for column in KERNEL_DIGEST_COLUMNS}
            )

    stationary_rows: list[dict[str, Any]] = []
    stationary_digest_rows: list[dict[str, int]] = []
    for component_id, weight in enumerate(stationary):
        record = fraction_record(weight)
        row = {
            "component_id": component_id,
            "component_value": int(COMPONENT_VALUES[component_id]),
            "weight_num": record["num"],
            "weight_den": record["den"],
            "weight_num_digits": record["num_digits"],
            "weight_den_digits": record["den_digits"],
            "weight_num_mod_1000000007": record["num_mod_1000000007"],
            "weight_den_mod_1000000007": record["den_mod_1000000007"],
            "weight_num_mod_1000000009": record["num_mod_1000000009"],
            "weight_den_mod_1000000009": record["den_mod_1000000009"],
            "weight_sha256": record["sha256"],
        }
        stationary_rows.append(row)
        stationary_digest_rows.append(
            {
                column: int(row[column])
                for column in STATIONARY_COLUMNS
                if column != "weight_sha256"
            }
        )

    trace = sum(kernel[index][index] for index in range(3))
    minor_sum = principal_minor_sum(kernel)
    determinant = det3(kernel)
    nontrivial_sum = trace - 1
    nontrivial_product = determinant
    nontrivial_discriminant = nontrivial_sum * nontrivial_sum - 4 * nontrivial_product
    spectral_values = [
        trace,
        minor_sum,
        determinant,
        nontrivial_sum,
        nontrivial_product,
        nontrivial_discriminant,
    ]
    spectral_rows: list[dict[str, Any]] = []
    spectral_digest_rows: list[dict[str, int]] = []
    for invariant_id, (name, value) in enumerate(zip(SPECTRAL_NAMES, spectral_values)):
        record = fraction_record(value)
        row = {
            "invariant_id": invariant_id,
            "invariant_name": name,
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
        spectral_rows.append(row)
        spectral_digest_rows.append(
            {column: int(row[column]) for column in SPECTRAL_DIGEST_COLUMNS}
        )

    identity = [[Fraction(int(row == col)) for col in range(3)] for row in range(3)]
    powers = [identity]
    for _power in range(1, POWER_HORIZON + 1):
        powers.append(matmul(powers[-1], kernel))
    power_rows: list[dict[str, int]] = []
    for power, matrix in enumerate(powers):
        for row in range(3):
            for col in range(3):
                values = digest_values(matrix[row][col])
                power_rows.append(
                    {
                        "power": power,
                        "row_component_id": row,
                        "col_component_id": col,
                        "prob_num_digits": values[0],
                        "prob_den_digits": values[1],
                        "prob_num_mod_1000000007": values[2],
                        "prob_den_mod_1000000007": values[3],
                        "prob_num_mod_1000000009": values[4],
                        "prob_den_mod_1000000009": values[5],
                    }
                )

    mean = sum(
        stationary[index] * COMPONENT_VALUES[index]
        for index in range(3)
    )
    second_moment = sum(
        stationary[index] * COMPONENT_VALUES[index] * COMPONENT_VALUES[index]
        for index in range(3)
    )
    variance = second_moment - mean * mean
    centered = [value - mean for value in COMPONENT_VALUES]
    covariance_values: list[Fraction] = []
    for power_matrix in powers:
        covariance_values.append(
            sum(
                stationary[row]
                * centered[row]
                * sum(power_matrix[row][col] * centered[col] for col in range(3))
                for row in range(3)
            )
        )
    covariance_rows: list[dict[str, Any]] = []
    covariance_digest_rows: list[dict[str, int]] = []
    for lag, value in enumerate(covariance_values):
        record = fraction_record(value)
        row = {
            "lag": lag,
            "cov_num": record["num"],
            "cov_den": record["den"],
            "cov_num_digits": record["num_digits"],
            "cov_den_digits": record["den_digits"],
            "cov_num_mod_1000000007": record["num_mod_1000000007"],
            "cov_den_mod_1000000007": record["den_mod_1000000007"],
            "cov_num_mod_1000000009": record["num_mod_1000000009"],
            "cov_den_mod_1000000009": record["den_mod_1000000009"],
            "cov_sha256": record["sha256"],
        }
        covariance_rows.append(row)
        covariance_digest_rows.append(
            {
                column: int(row[column])
                for column in COVARIANCE_DIGEST_COLUMNS
            }
        )

    mean_variance_values: list[Fraction] = []
    for sample_count in range(1, POWER_HORIZON + 1):
        mean_variance_values.append(
            (
                sample_count * covariance_values[0]
                + 2
                * sum(
                    (sample_count - lag) * covariance_values[lag]
                    for lag in range(1, sample_count)
                )
            )
            / (sample_count * sample_count)
        )
    mean_variance_rows: list[dict[str, Any]] = []
    mean_variance_digest_rows: list[dict[str, int]] = []
    for sample_count, value in enumerate(mean_variance_values, start=1):
        record = fraction_record(value)
        row = {
            "sample_count": sample_count,
            "variance_num": record["num"],
            "variance_den": record["den"],
            "variance_num_digits": record["num_digits"],
            "variance_den_digits": record["den_digits"],
            "variance_num_mod_1000000007": record["num_mod_1000000007"],
            "variance_den_mod_1000000007": record["den_mod_1000000007"],
            "variance_num_mod_1000000009": record["num_mod_1000000009"],
            "variance_den_mod_1000000009": record["den_mod_1000000009"],
            "variance_sha256": record["sha256"],
        }
        mean_variance_rows.append(row)
        mean_variance_digest_rows.append(
            {
                column: int(row[column])
                for column in MEAN_VARIANCE_DIGEST_COLUMNS
            }
        )

    stationary_fixed_violations = 0
    power_row_sum_violations = 0
    for matrix in powers:
        for row in range(3):
            if sum(matrix[row]) != 1:
                power_row_sum_violations += 1
        for col in range(3):
            if sum(stationary[row] * matrix[row][col] for row in range(3)) != stationary[col]:
                stationary_fixed_violations += 1

    mean_record = fraction_record(mean)
    variance_record = fraction_record(variance)
    nontrivial_discriminant_record = fraction_record(nontrivial_discriminant)
    obs = {
        "line_point_count": 985,
        "component_count": 3,
        "boundary0_count": int(boundary[0]),
        "boundary1_count": int(boundary[1]),
        "boundary2_count": int(boundary[2]),
        "boundary_total_count": int(total_boundary),
        "kernel_entry_count": len(kernel_rows),
        "kernel_positive_entry_count": sum(
            1 for row in kernel for value in row if value > 0
        ),
        "kernel_row_sum_one_flag": int(all(sum(row) == 1 for row in kernel)),
        "stationary_entry_count": len(stationary_rows),
        "stationary_sum_one_flag": int(sum(stationary) == 1),
        "stationary_fixed_flag": int(
            all(
                sum(stationary[row] * kernel[row][col] for row in range(3))
                == stationary[col]
                for col in range(3)
            )
        ),
        "detailed_balance_flag": int(
            all(
                stationary[row] * kernel[row][col]
                == stationary[col] * kernel[col][row]
                for row in range(3)
                for col in range(3)
            )
        ),
        "power_horizon": POWER_HORIZON,
        "power_digest_entry_count": len(power_rows),
        "power_row_sum_violation_count": power_row_sum_violations,
        "power_stationary_fixed_violation_count": stationary_fixed_violations,
        "spectral_invariant_count": len(spectral_rows),
        "nontrivial_discriminant_num_digits": int(
            nontrivial_discriminant_record["num_digits"]
        ),
        "nontrivial_discriminant_den_digits": int(
            nontrivial_discriminant_record["den_digits"]
        ),
        "nontrivial_discriminant_num_mod_1000000007": int(
            nontrivial_discriminant_record["num_mod_1000000007"]
        ),
        "nontrivial_discriminant_den_mod_1000000007": int(
            nontrivial_discriminant_record["den_mod_1000000007"]
        ),
        "nontrivial_discriminant_positive_flag": int(
            nontrivial_discriminant > 0
        ),
        "nontrivial_discriminant_rational_square_flag": int(
            math.isqrt(nontrivial_discriminant.numerator) ** 2
            == nontrivial_discriminant.numerator
            and math.isqrt(nontrivial_discriminant.denominator) ** 2
            == nontrivial_discriminant.denominator
        ),
        "stationary_mean_num_digits": int(mean_record["num_digits"]),
        "stationary_mean_den_digits": int(mean_record["den_digits"]),
        "stationary_mean_num_mod_1000000007": int(
            mean_record["num_mod_1000000007"]
        ),
        "stationary_mean_den_mod_1000000007": int(
            mean_record["den_mod_1000000007"]
        ),
        "stationary_variance_num_digits": int(variance_record["num_digits"]),
        "stationary_variance_den_digits": int(variance_record["den_digits"]),
        "stationary_variance_num_mod_1000000007": int(
            variance_record["num_mod_1000000007"]
        ),
        "stationary_variance_den_mod_1000000007": int(
            variance_record["den_mod_1000000007"]
        ),
        "autocovariance_count": len(covariance_rows),
        "mean_variance_count": len(mean_variance_rows),
        "mean_variance_monotone_decrease_flag": int(
            all(
                mean_variance_values[index] > mean_variance_values[index + 1]
                for index in range(len(mean_variance_values) - 1)
            )
        ),
        "mean_variance_first_matches_stationary_flag": int(
            mean_variance_values[0] == variance
        ),
        "long_spec_input_certified": int(
            long_spec.get("status") == LONG_SPEC_STATUS
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "long_spec": long_spec,
        "transfer": transfer,
        "boundary": boundary,
        "kernel": kernel,
        "stationary": stationary,
        "powers": powers,
        "spectral_values": spectral_values,
        "mean": mean,
        "second_moment": second_moment,
        "variance": variance,
        "covariance_values": covariance_values,
        "mean_variance_values": mean_variance_values,
        "kernel_rows": kernel_rows,
        "kernel_digest_rows": kernel_digest_rows,
        "stationary_rows": stationary_rows,
        "stationary_digest_rows": stationary_digest_rows,
        "spectral_rows": spectral_rows,
        "spectral_digest_rows": spectral_digest_rows,
        "power_rows": power_rows,
        "covariance_rows": covariance_rows,
        "covariance_digest_rows": covariance_digest_rows,
        "mean_variance_rows": mean_variance_rows,
        "mean_variance_digest_rows": mean_variance_digest_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    kernel_digest_table = table_from_rows(
        KERNEL_DIGEST_COLUMNS,
        rows["kernel_digest_rows"],
    )
    stationary_digest_table = table_from_rows(
        [
            column
            for column in STATIONARY_COLUMNS
            if column != "weight_sha256"
        ],
        rows["stationary_digest_rows"],
    )
    spectral_digest_table = table_from_rows(
        SPECTRAL_DIGEST_COLUMNS,
        rows["spectral_digest_rows"],
    )
    power_digest_table = table_from_rows(
        POWER_DIGEST_COLUMNS,
        rows["power_rows"],
    )
    covariance_digest_table = table_from_rows(
        COVARIANCE_DIGEST_COLUMNS,
        rows["covariance_digest_rows"],
    )
    mean_variance_digest_table = table_from_rows(
        MEAN_VARIANCE_DIGEST_COLUMNS,
        rows["mean_variance_digest_rows"],
    )
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])

    kernel_hash = hashlib.sha256(
        kernel_fraction_text(rows["kernel_rows"]).encode("ascii")
    ).hexdigest()
    stationary_hash = hashlib.sha256(
        stationary_fraction_text(rows["stationary_rows"]).encode("ascii")
    ).hexdigest()
    detailed_balance_hash = hashlib.sha256(
        detailed_balance_text(rows["stationary"], rows["kernel"]).encode("ascii")
    ).hexdigest()
    spectral_hash = hashlib.sha256(
        spectral_fraction_text(rows["spectral_rows"]).encode("ascii")
    ).hexdigest()
    power_hash = hashlib.sha256(
        power_digest_text(rows["power_rows"]).encode("ascii")
    ).hexdigest()
    covariance_hash = hashlib.sha256(
        covariance_fraction_text(rows["covariance_rows"]).encode("ascii")
    ).hexdigest()
    mean_variance_hash = hashlib.sha256(
        mean_variance_fraction_text(rows["mean_variance_rows"]).encode("ascii")
    ).hexdigest()
    kernel_signature = [
        tuple(row[column] for column in KERNEL_DIGEST_COLUMNS)
        for row in rows["kernel_digest_rows"]
    ]
    stationary_signature = [
        (
            row["component_id"],
            row["weight_num_digits"],
            row["weight_den_digits"],
            row["weight_num_mod_1000000007"],
            row["weight_den_mod_1000000007"],
            row["weight_num_mod_1000000009"],
            row["weight_den_mod_1000000009"],
        )
        for row in rows["stationary_digest_rows"]
    ]
    spectral_signature = [
        tuple(row[column] for column in SPECTRAL_DIGEST_COLUMNS)
        for row in rows["spectral_digest_rows"]
    ]
    checks = {
        "input_certified": obs["long_spec_input_certified"] == 1,
        "kernel_stationary_exact": (
            obs["boundary0_count"],
            obs["boundary1_count"],
            obs["boundary2_count"],
            obs["boundary_total_count"],
            obs["kernel_entry_count"],
            obs["kernel_positive_entry_count"],
            obs["kernel_row_sum_one_flag"],
            obs["stationary_entry_count"],
            obs["stationary_sum_one_flag"],
            obs["stationary_fixed_flag"],
            obs["detailed_balance_flag"],
        )
        == (1_342, 864, 2_378, 4_584, 9, 9, 1, 3, 1, 1, 1),
        "kernel_signature_exact": kernel_signature
        == [
            (0, 0, 258, 258, 618_582_603, 683_696_920, 518_772_888, 502_409_092, 1),
            (0, 1, 255, 257, 844_593_645, 847_577_025, 240_707_565, 927_133_531, 0),
            (0, 2, 258, 258, 524_619_644, 683_696_920, 429_673_192, 502_409_092, 0),
            (1, 0, 255, 256, 922_296_826, 675_225_990, 620_353_787, 326_767_277, 0),
            (1, 1, 257, 257, 500_341_420, 700_903_946, 752_850_196, 307_069_099, 1),
            (1, 2, 256, 257, 511_375_250, 700_903_946, 72_803_782, 307_069_099, 0),
            (2, 0, 258, 259, 524_619_644, 409_710_334, 429_673_192, 894_730_865, 0),
            (2, 1, 256, 257, 511_375_250, 933_737_937, 72_803_782, 328_947_122, 0),
            (2, 2, 259, 259, 612_084_781, 409_710_334, 717_766_923, 894_730_865, 1),
        ],
        "stationary_signature_exact": stationary_signature
        == [
            (0, 3, 4, 671, 2_292, 671, 2_292),
            (1, 2, 3, 36, 191, 36, 191),
            (2, 4, 4, 1_189, 2_292, 1_189, 2_292),
        ],
        "spectral_signature_exact": spectral_signature
        == [
            (0, 263, 263, 553_278_613, 481_379_416, 151_183_804, 559_290_216),
            (1, 264, 263, 144_483_733, 925_517_657, 810_273_291, 237_160_846),
            (2, 263, 263, 285_628_984, 975_172_557, 147_566_307, 745_720_288),
            (3, 263, 263, 71_899_197, 481_379_416, 591_893_597, 559_290_216),
            (4, 263, 263, 285_628_984, 975_172_557, 147_566_307, 745_720_288),
            (5, 524, 525, 848_692_485, 526_418_076, 95_873_787, 898_076_778),
        ],
        "power_fingerprint_exact": (
            obs["power_horizon"],
            obs["power_digest_entry_count"],
            obs["power_row_sum_violation_count"],
            obs["power_stationary_fixed_violation_count"],
            power_hash,
        )
        == (
            8,
            81,
            0,
            0,
            "c3e77932668eb5f83979c6b805f9d456450d02cdceb7a1bd335684633f1aeee6",
        ),
        "lln_fingerprint_exact": (
            obs["stationary_mean_num_digits"],
            obs["stationary_mean_den_digits"],
            obs["stationary_mean_num_mod_1000000007"],
            obs["stationary_mean_den_mod_1000000007"],
            obs["stationary_variance_num_digits"],
            obs["stationary_variance_den_digits"],
            obs["stationary_variance_num_mod_1000000007"],
            obs["stationary_variance_den_mod_1000000007"],
            obs["autocovariance_count"],
            obs["mean_variance_count"],
            obs["mean_variance_monotone_decrease_flag"],
            obs["mean_variance_first_matches_stationary_flag"],
            covariance_hash,
            mean_variance_hash,
        )
        == (
            4,
            4,
            1_405,
            1_146,
            6,
            7,
            998_699,
            1_313_316,
            9,
            8,
            1,
            1,
            "d9e86f019666d3161c71d69f7c277320bd6782a0771a58bde1922dd5b3ae723a",
            "46d3daf5ecb3caf90f29834f98afe7c7a2e90997e68a56ca936bbc47a0e3be47",
        ),
        "discriminant_fingerprint_exact": (
            obs["nontrivial_discriminant_num_digits"],
            obs["nontrivial_discriminant_den_digits"],
            obs["nontrivial_discriminant_num_mod_1000000007"],
            obs["nontrivial_discriminant_den_mod_1000000007"],
            obs["nontrivial_discriminant_positive_flag"],
            obs["nontrivial_discriminant_rational_square_flag"],
        )
        == (524, 525, 848_692_485, 526_418_076, 1, 0),
        "digest_hashes_exact": (
            kernel_hash,
            stationary_hash,
            detailed_balance_hash,
            spectral_hash,
        )
        == (
            "1de86eb4c03287b20e03ad6d38170e08a3398b721ba281a6f8fa61982e83b552",
            "67c0cd6ff0bca3e0575d0136033240098abb705bdeb93812783853f7a20695d2",
            "f2cb23a2c33352d0dc40163ff7a1fd241d6ab10668971a0b20cdd6e4d5974899",
            "0d0f56de3fa6c48d111c5af6d85589ad17077cc97130028390cdb9fd9848a0f7",
        ),
        "table_shapes_match": (
            tuple(kernel_digest_table.shape),
            tuple(stationary_digest_table.shape),
            tuple(spectral_digest_table.shape),
            tuple(power_digest_table.shape),
            tuple(covariance_digest_table.shape),
            tuple(mean_variance_digest_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (9, len(KERNEL_DIGEST_COLUMNS)),
            (3, len(STATIONARY_COLUMNS) - 1),
            (6, len(SPECTRAL_DIGEST_COLUMNS)),
            (81, len(POWER_DIGEST_COLUMNS)),
            (9, len(COVARIANCE_DIGEST_COLUMNS)),
            (8, len(MEAN_VARIANCE_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    mean_record = fraction_record(rows["mean"])
    second_record = fraction_record(rows["second_moment"])
    variance_record = fraction_record(rows["variance"])
    witness = {
        "name": THEOREM_ID,
        "classification": "long_spec_reversible_boundary_markov_lln",
        "scope": {
            "source": "long_absorb three-terminal transfer matrix",
            "kernel": "D^{-1}T with D equal to boundary totals",
            "observable": "component_value in {0,1,2}",
        },
        "kernel": {
            "row_stochastic": bool(obs["kernel_row_sum_one_flag"]),
            "positive_entry_count": obs["kernel_positive_entry_count"],
            "kernel_fraction_text_sha256": kernel_hash,
            "kernel_digest_table_sha256": sha_array(kernel_digest_table),
        },
        "stationary": {
            "weights": [
                {"component_id": row["component_id"], "num": row["weight_num"], "den": row["weight_den"]}
                for row in rows["stationary_rows"]
            ],
            "fixed": bool(obs["stationary_fixed_flag"]),
            "detailed_balance": bool(obs["detailed_balance_flag"]),
            "stationary_fraction_text_sha256": stationary_hash,
            "detailed_balance_text_sha256": detailed_balance_hash,
            "stationary_digest_table_sha256": sha_array(stationary_digest_table),
        },
        "spectrum": {
            "charpoly": "lambda^3 - trace*lambda^2 + principal_minor_sum*lambda - determinant",
            "nontrivial_factor": "lambda^2 - nontrivial_sum*lambda + nontrivial_product",
            "nontrivial_discriminant_positive": bool(
                obs["nontrivial_discriminant_positive_flag"]
            ),
            "nontrivial_discriminant_rational_square": bool(
                obs["nontrivial_discriminant_rational_square_flag"]
            ),
            "spectral_fraction_text_sha256": spectral_hash,
            "spectral_digest_table_sha256": sha_array(spectral_digest_table),
        },
        "powers": {
            "horizon": POWER_HORIZON,
            "row_sum_violation_count": obs["power_row_sum_violation_count"],
            "stationary_fixed_violation_count": obs[
                "power_stationary_fixed_violation_count"
            ],
            "power_digest_text_sha256": power_hash,
            "power_digest_table_sha256": sha_array(power_digest_table),
        },
        "finite_lln": {
            "mean": mean_record,
            "second_moment": second_record,
            "variance": variance_record,
            "autocovariance_horizon": POWER_HORIZON,
            "sample_mean_variance_horizon": POWER_HORIZON,
            "mean_variance_monotone_decrease": bool(
                obs["mean_variance_monotone_decrease_flag"]
            ),
            "autocovariance_fraction_text_sha256": covariance_hash,
            "mean_variance_fraction_text_sha256": mean_variance_hash,
            "covariance_digest_table_sha256": sha_array(covariance_digest_table),
            "mean_variance_digest_table_sha256": sha_array(
                mean_variance_digest_table
            ),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    markov = {
        "schema": "long.markov@1",
        "object": "long_spec_reversible_boundary_markov_lln",
        "status": STATUS if all(checks.values()) else "LONG_MARKOV_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.markov.report@1",
        "status": markov["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_markov certifies the reversible three-state boundary Markov "
            "kernel D^{-1}T induced by long_absorb/long_spec, its stationary "
            "law, detailed balance, exact finite powers through horizon 8, "
            "and stationary finite-LLN autocovariance and sample-mean variance "
            "fingerprints for the component-value observable."
        ),
        "stage_protocol": {
            "draft": "normalize the symmetric long_absorb transfer matrix by boundary totals",
            "witness": "derive the stationary law, detailed balance, powers, spectral fingerprints, and LLN autocovariances",
            "coherence": "check stochasticity, reversibility, power invariance, signatures, and text hashes",
            "closure": "emit kernel, stationary, spectral, power, covariance, variance, table, certificate, manifest, and report artifacts",
            "emit": "write long_markov artifacts and verifier hook",
        },
        "inputs": {
            "long_spec_report": input_entry(
                LONG_SPEC_REPORT,
                {"status": rows["long_spec"].get("status")},
            ),
            "long_spec_tables": input_entry(LONG_SPEC_TABLES),
            "long_absorb_matrix": input_entry(LONG_ABSORB_MATRIX),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "markov": relpath(OUT_DIR / "markov.json"),
            "kernel_csv": relpath(OUT_DIR / "kernel.csv"),
            "stationary_csv": relpath(OUT_DIR / "stationary.csv"),
            "spectral_csv": relpath(OUT_DIR / "spectral.csv"),
            "power_csv": relpath(OUT_DIR / "power.csv"),
            "covariance_csv": relpath(OUT_DIR / "covariance.csv"),
            "mean_variance_csv": relpath(OUT_DIR / "mean_variance.csv"),
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
                "the exact reversible boundary Markov kernel from long_spec",
                "stationary distribution and detailed balance",
                "finite kernel powers through horizon eight",
                "finite Markov LLN autocovariance and sample-mean variance fingerprints through horizon eight",
            ],
            "does_not_certify_because_out_of_scope": [
                "an asymptotic central limit theorem",
                "continuous-time diffusion beyond the finite kernel",
                "support-changing recouplings outside the long_rec owner graph",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_dev: certify finite large-deviation/Chernoff-style "
            "moment fingerprints for the boundary Markov observable, still "
            "without leaving exact tensor lookup arithmetic."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.markov.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.markov.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "markov": markov,
        "kernel_csv": csv_text(KERNEL_COLUMNS, rows["kernel_rows"]),
        "stationary_csv": csv_text(STATIONARY_COLUMNS, rows["stationary_rows"]),
        "spectral_csv": csv_text(SPECTRAL_COLUMNS, rows["spectral_rows"]),
        "power_csv": csv_text(POWER_DIGEST_COLUMNS, rows["power_rows"]),
        "covariance_csv": csv_text(COVARIANCE_COLUMNS, rows["covariance_rows"]),
        "mean_variance_csv": csv_text(
            MEAN_VARIANCE_COLUMNS,
            rows["mean_variance_rows"],
        ),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "kernel_digest_table": kernel_digest_table,
        "stationary_digest_table": stationary_digest_table,
        "spectral_digest_table": spectral_digest_table,
        "power_digest_table": power_digest_table,
        "covariance_digest_table": covariance_digest_table,
        "mean_variance_digest_table": mean_variance_digest_table,
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
    write_json(OUT_DIR / "markov.json", payloads["markov"])
    (OUT_DIR / "kernel.csv").write_text(payloads["kernel_csv"], encoding="utf-8")
    (OUT_DIR / "stationary.csv").write_text(
        payloads["stationary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "spectral.csv").write_text(
        payloads["spectral_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "power.csv").write_text(payloads["power_csv"], encoding="utf-8")
    (OUT_DIR / "covariance.csv").write_text(
        payloads["covariance_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "mean_variance.csv").write_text(
        payloads["mean_variance_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        kernel_digest_table=payloads["kernel_digest_table"],
        stationary_digest_table=payloads["stationary_digest_table"],
        spectral_digest_table=payloads["spectral_digest_table"],
        power_digest_table=payloads["power_digest_table"],
        covariance_digest_table=payloads["covariance_digest_table"],
        mean_variance_digest_table=payloads["mean_variance_digest_table"],
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
