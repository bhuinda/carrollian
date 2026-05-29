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
    from .derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
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
    from derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
    from derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_cls"
STATUS = "LONG_CLS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_CONV_REPORT = LONG_CONV_DIR / "report.json"
LONG_CONV_MARGINAL = LONG_CONV_DIR / "marginal.csv"
LONG_CONV_TABLES = LONG_CONV_DIR / "tables.npz"
LONG_MARKOV_REPORT = LONG_MARKOV_DIR / "report.json"
LONG_MARKOV_MEAN_VARIANCE = LONG_MARKOV_DIR / "mean_variance.csv"
LONG_MARKOV_TABLES = LONG_MARKOV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_cls.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_cls.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
HORIZON = 16
CENTERED_MOMENT_ORDERS = (2, 3, 4)
EPSILONS = ((0, Fraction(1, 2)), (1, Fraction(1, 3)), (2, Fraction(1, 4)))

MEAN_TEXT_HASH = (
    "c0038ff677c351cc8ac0e0f0a34a7ec72a455d68dd39d4a7132fb3a16069b742"
)
MOMENT_TEXT_HASH = (
    "d9c0dc95dad50787fefc365ac68378525abc327cf7db3dfd6459ff250f31e1d8"
)
TAIL_TEXT_HASH = (
    "1cd4550f8fd24267fd3d09a65306575927700b7f1049755f3c20b788c81381b0"
)
SHRINK_TEXT_HASH = (
    "152c2a5404ea7e7b8d0981103a07742b18d1e556356419fdaf8c64afd8c382c8"
)

MEAN_COLUMNS = [
    "sample_count",
    "mean_num",
    "mean_den",
    "mean_num_digits",
    "mean_den_digits",
    "mean_num_mod_1000000007",
    "mean_den_mod_1000000007",
    "mean_num_mod_1000000009",
    "mean_den_mod_1000000009",
    "mean_sha256",
    "stationary_mean_num",
    "stationary_mean_den",
    "mean_matches_stationary_flag",
]
MEAN_DIGEST_COLUMNS = [
    "sample_count",
    "mean_num_digits",
    "mean_den_digits",
    "mean_num_mod_1000000007",
    "mean_den_mod_1000000007",
    "mean_num_mod_1000000009",
    "mean_den_mod_1000000009",
    "stationary_mean_num",
    "stationary_mean_den",
    "mean_matches_stationary_flag",
]
MOMENT_COLUMNS = [
    "sample_count",
    "moment_order",
    "centered_num",
    "centered_den",
    "centered_num_digits",
    "centered_den_digits",
    "centered_num_mod_1000000007",
    "centered_den_mod_1000000007",
    "centered_num_mod_1000000009",
    "centered_den_mod_1000000009",
    "centered_sha256",
    "variance_matches_markov_flag",
    "nonnegative_even_flag",
]
MOMENT_DIGEST_COLUMNS = [
    "sample_count",
    "moment_order",
    "centered_num_digits",
    "centered_den_digits",
    "centered_num_mod_1000000007",
    "centered_den_mod_1000000007",
    "centered_num_mod_1000000009",
    "centered_den_mod_1000000009",
    "variance_matches_markov_flag",
    "nonnegative_even_flag",
]
TAIL_COLUMNS = [
    "sample_count",
    "epsilon_id",
    "eps_num",
    "eps_den",
    "tail_num",
    "tail_den",
    "bound_num",
    "bound_den",
    "gap_num",
    "gap_den",
    "tail_num_digits",
    "tail_den_digits",
    "tail_num_mod_1000000007",
    "tail_den_mod_1000000007",
    "tail_num_mod_1000000009",
    "tail_den_mod_1000000009",
    "tail_sha256",
    "bound_num_digits",
    "bound_den_digits",
    "bound_num_mod_1000000007",
    "bound_den_mod_1000000007",
    "bound_num_mod_1000000009",
    "bound_den_mod_1000000009",
    "bound_sha256",
    "gap_num_digits",
    "gap_den_digits",
    "gap_num_mod_1000000007",
    "gap_den_mod_1000000007",
    "gap_num_mod_1000000009",
    "gap_den_mod_1000000009",
    "gap_sha256",
    "gap_nonnegative_flag",
]
TAIL_DIGEST_COLUMNS = [
    "sample_count",
    "epsilon_id",
    "eps_num",
    "eps_den",
    "tail_num_digits",
    "tail_den_digits",
    "tail_num_mod_1000000007",
    "tail_den_mod_1000000007",
    "tail_num_mod_1000000009",
    "tail_den_mod_1000000009",
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
    "gap_nonnegative_flag",
]
SHRINK_COLUMNS = [
    "sample_count",
    "prev_variance_num",
    "prev_variance_den",
    "variance_num",
    "variance_den",
    "shrink_gap_num",
    "shrink_gap_den",
    "prev_variance_num_digits",
    "prev_variance_den_digits",
    "prev_variance_num_mod_1000000007",
    "prev_variance_den_mod_1000000007",
    "prev_variance_num_mod_1000000009",
    "prev_variance_den_mod_1000000009",
    "prev_variance_sha256",
    "variance_num_digits",
    "variance_den_digits",
    "variance_num_mod_1000000007",
    "variance_den_mod_1000000007",
    "variance_num_mod_1000000009",
    "variance_den_mod_1000000009",
    "variance_sha256",
    "shrink_gap_num_digits",
    "shrink_gap_den_digits",
    "shrink_gap_num_mod_1000000007",
    "shrink_gap_den_mod_1000000007",
    "shrink_gap_num_mod_1000000009",
    "shrink_gap_den_mod_1000000009",
    "shrink_gap_sha256",
    "shrink_nonnegative_flag",
]
SHRINK_DIGEST_COLUMNS = [
    "sample_count",
    "prev_variance_num_digits",
    "prev_variance_den_digits",
    "prev_variance_num_mod_1000000007",
    "prev_variance_den_mod_1000000007",
    "prev_variance_num_mod_1000000009",
    "prev_variance_den_mod_1000000009",
    "variance_num_digits",
    "variance_den_digits",
    "variance_num_mod_1000000007",
    "variance_den_mod_1000000007",
    "variance_num_mod_1000000009",
    "variance_den_mod_1000000009",
    "shrink_gap_num_digits",
    "shrink_gap_den_digits",
    "shrink_gap_num_mod_1000000007",
    "shrink_gap_den_mod_1000000007",
    "shrink_gap_num_mod_1000000009",
    "shrink_gap_den_mod_1000000009",
    "shrink_nonnegative_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "horizon",
    "epsilon_count",
    "mean_row_count",
    "mean_match_count",
    "mean_num_digit_max",
    "mean_den_digit_max",
    "centered_moment_row_count",
    "variance_markov_match_count",
    "order2_nonnegative_count",
    "order4_nonnegative_count",
    "moment_num_digit_max",
    "moment_den_digit_max",
    "tail_row_count",
    "tail_gap_nonnegative_count",
    "tail_num_digit_max",
    "tail_den_digit_max",
    "shrink_row_count",
    "shrink_nonnegative_count",
    "shrink_num_digit_max",
    "shrink_den_digit_max",
    "long_conv_input_certified",
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


def prefixed_fraction_fields(prefix: str, value: Fraction) -> dict[str, int | str]:
    record = fraction_record(value)
    return {
        f"{prefix}_num": record["num"],
        f"{prefix}_den": record["den"],
        f"{prefix}_num_digits": record["num_digits"],
        f"{prefix}_den_digits": record["den_digits"],
        f"{prefix}_num_mod_1000000007": record["num_mod_1000000007"],
        f"{prefix}_den_mod_1000000007": record["den_mod_1000000007"],
        f"{prefix}_num_mod_1000000009": record["num_mod_1000000009"],
        f"{prefix}_den_mod_1000000009": record["den_mod_1000000009"],
        f"{prefix}_sha256": record["sha256"],
    }


def read_marginals() -> dict[int, dict[int, Fraction]]:
    distributions: dict[int, dict[int, Fraction]] = {}
    with LONG_CONV_MARGINAL.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            sample_count = int(row["sample_count"])
            sum_value = int(row["sum_value"])
            distributions.setdefault(sample_count, {})[sum_value] = Fraction(
                int(row["prob_num"]),
                int(row["prob_den"]),
            )
    return distributions


def read_markov_variances() -> dict[int, Fraction]:
    variances: dict[int, Fraction] = {}
    with LONG_MARKOV_MEAN_VARIANCE.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            variances[int(row["sample_count"])] = Fraction(
                int(row["variance_num"]),
                int(row["variance_den"]),
            )
    return variances


def mean_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['mean_num']},{row['mean_den']},"
        f"{row['stationary_mean_num']},{row['stationary_mean_den']},"
        f"{row['mean_matches_stationary_flag']}\n"
        for row in rows
    )


def moment_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['moment_order']},"
        f"{row['centered_num']},{row['centered_den']},"
        f"{row['variance_matches_markov_flag']},"
        f"{row['nonnegative_even_flag']}\n"
        for row in rows
    )


def tail_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['epsilon_id']},"
        f"{row['eps_num']},{row['eps_den']},"
        f"{row['tail_num']},{row['tail_den']},"
        f"{row['bound_num']},{row['bound_den']},"
        f"{row['gap_num']},{row['gap_den']},"
        f"{row['gap_nonnegative_flag']}\n"
        for row in rows
    )


def shrink_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['shrink_gap_num']},"
        f"{row['shrink_gap_den']},{row['shrink_nonnegative_flag']}\n"
        for row in rows
    )


def build_rows() -> dict[str, Any]:
    long_conv = load_json(LONG_CONV_REPORT)
    long_markov = load_json(LONG_MARKOV_REPORT)
    mean_block = long_markov["witness"]["finite_lln"]["mean"]
    stationary_mean = Fraction(int(mean_block["num"]), int(mean_block["den"]))
    distributions = read_marginals()
    markov_variances = read_markov_variances()

    mean_rows: list[dict[str, Any]] = []
    mean_digest_rows: list[dict[str, int]] = []
    moment_rows: list[dict[str, Any]] = []
    moment_digest_rows: list[dict[str, int]] = []
    variance_by_sample: dict[int, Fraction] = {}
    for sample_count in range(1, HORIZON + 1):
        distribution = distributions[sample_count]
        sample_mean = sum(
            Fraction(sum_value, sample_count) * probability
            for sum_value, probability in distribution.items()
        )
        mean_row = {
            "sample_count": sample_count,
            **prefixed_fraction_fields("mean", sample_mean),
            "stationary_mean_num": stationary_mean.numerator,
            "stationary_mean_den": stationary_mean.denominator,
            "mean_matches_stationary_flag": int(sample_mean == stationary_mean),
        }
        mean_rows.append(mean_row)
        mean_digest_rows.append(
            {column: int(mean_row[column]) for column in MEAN_DIGEST_COLUMNS}
        )

        for moment_order in CENTERED_MOMENT_ORDERS:
            centered = sum(
                (Fraction(sum_value, sample_count) - stationary_mean) ** moment_order
                * probability
                for sum_value, probability in distribution.items()
            )
            if moment_order == 2:
                variance_by_sample[sample_count] = centered
                variance_match = (
                    int(centered == markov_variances[sample_count])
                    if sample_count in markov_variances
                    else -1
                )
            else:
                variance_match = 0
            nonnegative_even = (
                int(centered >= 0) if moment_order % 2 == 0 else -1
            )
            moment_row = {
                "sample_count": sample_count,
                "moment_order": moment_order,
                **prefixed_fraction_fields("centered", centered),
                "variance_matches_markov_flag": variance_match,
                "nonnegative_even_flag": nonnegative_even,
            }
            moment_rows.append(moment_row)
            moment_digest_rows.append(
                {column: int(moment_row[column]) for column in MOMENT_DIGEST_COLUMNS}
            )

    tail_rows: list[dict[str, Any]] = []
    tail_digest_rows: list[dict[str, int]] = []
    for sample_count in range(1, HORIZON + 1):
        distribution = distributions[sample_count]
        variance = variance_by_sample[sample_count]
        for epsilon_id, epsilon in EPSILONS:
            tail = sum(
                probability
                for sum_value, probability in distribution.items()
                if abs(Fraction(sum_value, sample_count) - stationary_mean) >= epsilon
            )
            bound = variance / (epsilon * epsilon)
            gap = bound - tail
            tail_row = {
                "sample_count": sample_count,
                "epsilon_id": epsilon_id,
                "eps_num": epsilon.numerator,
                "eps_den": epsilon.denominator,
                **prefixed_fraction_fields("tail", tail),
                **prefixed_fraction_fields("bound", bound),
                **prefixed_fraction_fields("gap", gap),
                "gap_nonnegative_flag": int(gap >= 0),
            }
            tail_rows.append(tail_row)
            tail_digest_rows.append(
                {column: int(tail_row[column]) for column in TAIL_DIGEST_COLUMNS}
            )

    shrink_rows: list[dict[str, Any]] = []
    shrink_digest_rows: list[dict[str, int]] = []
    for sample_count in range(2, HORIZON + 1):
        previous = variance_by_sample[sample_count - 1]
        current = variance_by_sample[sample_count]
        gap = previous - current
        shrink_row = {
            "sample_count": sample_count,
            **prefixed_fraction_fields("prev_variance", previous),
            **prefixed_fraction_fields("variance", current),
            **prefixed_fraction_fields("shrink_gap", gap),
            "shrink_nonnegative_flag": int(gap >= 0),
        }
        shrink_rows.append(shrink_row)
        shrink_digest_rows.append(
            {column: int(shrink_row[column]) for column in SHRINK_DIGEST_COLUMNS}
        )

    moment_values = [
        Fraction(row["centered_num"], row["centered_den"]) for row in moment_rows
    ]
    tail_values = [
        Fraction(row[f"{name}_num"], row[f"{name}_den"])
        for row in tail_rows
        for name in ("tail", "bound", "gap")
    ]
    shrink_values = [
        Fraction(row[f"{name}_num"], row[f"{name}_den"])
        for row in shrink_rows
        for name in ("prev_variance", "variance", "shrink_gap")
    ]
    obs = {
        "horizon": HORIZON,
        "epsilon_count": len(EPSILONS),
        "mean_row_count": len(mean_rows),
        "mean_match_count": sum(
            int(row["mean_matches_stationary_flag"]) for row in mean_rows
        ),
        "mean_num_digit_max": max(row["mean_num_digits"] for row in mean_rows),
        "mean_den_digit_max": max(row["mean_den_digits"] for row in mean_rows),
        "centered_moment_row_count": len(moment_rows),
        "variance_markov_match_count": sum(
            int(row["variance_matches_markov_flag"] == 1) for row in moment_rows
        ),
        "order2_nonnegative_count": sum(
            int(
                row["moment_order"] == 2 and row["nonnegative_even_flag"] == 1
            )
            for row in moment_rows
        ),
        "order4_nonnegative_count": sum(
            int(
                row["moment_order"] == 4 and row["nonnegative_even_flag"] == 1
            )
            for row in moment_rows
        ),
        "moment_num_digit_max": max(
            len(str(abs(value.numerator))) for value in moment_values
        ),
        "moment_den_digit_max": max(len(str(value.denominator)) for value in moment_values),
        "tail_row_count": len(tail_rows),
        "tail_gap_nonnegative_count": sum(
            int(row["gap_nonnegative_flag"]) for row in tail_rows
        ),
        "tail_num_digit_max": max(
            len(str(abs(value.numerator))) for value in tail_values
        ),
        "tail_den_digit_max": max(len(str(value.denominator)) for value in tail_values),
        "shrink_row_count": len(shrink_rows),
        "shrink_nonnegative_count": sum(
            int(row["shrink_nonnegative_flag"]) for row in shrink_rows
        ),
        "shrink_num_digit_max": max(
            len(str(abs(value.numerator))) for value in shrink_values
        ),
        "shrink_den_digit_max": max(
            len(str(value.denominator)) for value in shrink_values
        ),
        "long_conv_input_certified": int(long_conv.get("status") == LONG_CONV_STATUS),
        "long_markov_input_certified": int(
            long_markov.get("status") == LONG_MARKOV_STATUS
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "input_reports": {"long_conv": long_conv, "long_markov": long_markov},
        "mean_rows": mean_rows,
        "mean_digest_rows": mean_digest_rows,
        "moment_rows": moment_rows,
        "moment_digest_rows": moment_digest_rows,
        "tail_rows": tail_rows,
        "tail_digest_rows": tail_digest_rows,
        "shrink_rows": shrink_rows,
        "shrink_digest_rows": shrink_digest_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    mean_table = table_from_rows(MEAN_DIGEST_COLUMNS, rows["mean_digest_rows"])
    moment_table = table_from_rows(MOMENT_DIGEST_COLUMNS, rows["moment_digest_rows"])
    tail_table = table_from_rows(TAIL_DIGEST_COLUMNS, rows["tail_digest_rows"])
    shrink_table = table_from_rows(SHRINK_DIGEST_COLUMNS, rows["shrink_digest_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    mean_hash = hashlib.sha256(mean_text(rows["mean_rows"]).encode("ascii")).hexdigest()
    moment_hash = hashlib.sha256(
        moment_text(rows["moment_rows"]).encode("ascii")
    ).hexdigest()
    tail_hash = hashlib.sha256(tail_text(rows["tail_rows"]).encode("ascii")).hexdigest()
    shrink_hash = hashlib.sha256(
        shrink_text(rows["shrink_rows"]).encode("ascii")
    ).hexdigest()
    checks = {
        "inputs_certified": (
            obs["long_conv_input_certified"] == 1
            and obs["long_markov_input_certified"] == 1
        ),
        "mean_fingerprint_exact": (
            obs["mean_row_count"],
            obs["mean_match_count"],
            obs["mean_num_digit_max"],
            obs["mean_den_digit_max"],
            mean_hash,
        )
        == (16, 16, 4, 4, MEAN_TEXT_HASH),
        "centered_moment_fingerprint_exact": (
            obs["centered_moment_row_count"],
            obs["variance_markov_match_count"],
            obs["order2_nonnegative_count"],
            obs["order4_nonnegative_count"],
            obs["moment_num_digit_max"],
            obs["moment_den_digit_max"],
            moment_hash,
        )
        == (48, 8, 16, 16, 3_940, 3_941, MOMENT_TEXT_HASH),
        "chebyshev_tail_fingerprint_exact": (
            obs["tail_row_count"],
            obs["tail_gap_nonnegative_count"],
            obs["tail_num_digit_max"],
            obs["tail_den_digit_max"],
            tail_hash,
        )
        == (48, 48, 3_934, 3_934, TAIL_TEXT_HASH),
        "variance_shrink_fingerprint_exact": (
            obs["shrink_row_count"],
            obs["shrink_nonnegative_count"],
            obs["shrink_num_digit_max"],
            obs["shrink_den_digit_max"],
            shrink_hash,
        )
        == (15, 15, 3_933, 3_933, SHRINK_TEXT_HASH),
        "table_shapes_match": (
            tuple(mean_table.shape),
            tuple(moment_table.shape),
            tuple(tail_table.shape),
            tuple(shrink_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (16, len(MEAN_DIGEST_COLUMNS)),
            (48, len(MOMENT_DIGEST_COLUMNS)),
            (48, len(TAIL_DIGEST_COLUMNS)),
            (15, len(SHRINK_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_concentration_lln_shrinkage_tensor_lookup",
        "horizon": HORIZON,
        "source": {
            "distribution": "long_conv marginal.csv public path-sum laws",
            "comparison": "long_markov mean_variance.csv through horizon eight",
        },
        "means": {
            "row_count": obs["mean_row_count"],
            "match_count": obs["mean_match_count"],
            "fraction_text_sha256": mean_hash,
            "table_sha256": sha_array(mean_table),
        },
        "centered_moments": {
            "row_count": obs["centered_moment_row_count"],
            "orders": list(CENTERED_MOMENT_ORDERS),
            "variance_markov_match_count": obs["variance_markov_match_count"],
            "order2_nonnegative_count": obs["order2_nonnegative_count"],
            "order4_nonnegative_count": obs["order4_nonnegative_count"],
            "fraction_text_sha256": moment_hash,
            "table_sha256": sha_array(moment_table),
        },
        "chebyshev_tails": {
            "row_count": obs["tail_row_count"],
            "epsilons": [
                {"epsilon_id": epsilon_id, "num": eps.numerator, "den": eps.denominator}
                for epsilon_id, eps in EPSILONS
            ],
            "gap_nonnegative_count": obs["tail_gap_nonnegative_count"],
            "fraction_text_sha256": tail_hash,
            "table_sha256": sha_array(tail_table),
        },
        "variance_shrink": {
            "row_count": obs["shrink_row_count"],
            "nonnegative_count": obs["shrink_nonnegative_count"],
            "fraction_text_sha256": shrink_hash,
            "table_sha256": sha_array(shrink_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    cls = {
        "schema": "long.cls@1",
        "object": "finite_concentration_lln_shrinkage_tensor_lookup",
        "status": STATUS if all(checks.values()) else "LONG_CLS_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.cls.report@1",
        "status": cls["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_cls certifies finite concentration/shrinkage from the "
            "long_conv horizon-16 path-sum laws: every sample mean equals the "
            "long_markov stationary mean, centered second/fourth moments are "
            "nonnegative, the first eight variances match long_markov exactly, "
            "Chebyshev tail-window gaps are nonnegative, and sample-mean "
            "variance decreases through horizon 16."
        ),
        "stage_protocol": {
            "draft": "read long_conv public marginals and long_markov stationary finite-LLN rows",
            "witness": "compute exact sample means, centered moments, Chebyshev tail gaps, and variance shrink gaps",
            "coherence": "check mean equality, Markov variance agreement, nonnegative even moments/tail gaps/shrink gaps, hashes, and shapes",
            "closure": "emit mean, moment, tail, shrink, table, certificate, manifest, and report artifacts",
            "emit": "write long_cls artifacts and verifier hook",
        },
        "inputs": {
            "long_conv_report": input_entry(
                LONG_CONV_REPORT,
                {"status": rows["input_reports"]["long_conv"].get("status")},
            ),
            "long_conv_marginal": input_entry(LONG_CONV_MARGINAL),
            "long_conv_tables": input_entry(LONG_CONV_TABLES),
            "long_markov_report": input_entry(
                LONG_MARKOV_REPORT,
                {"status": rows["input_reports"]["long_markov"].get("status")},
            ),
            "long_markov_mean_variance": input_entry(LONG_MARKOV_MEAN_VARIANCE),
            "long_markov_tables": input_entry(LONG_MARKOV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "cls": relpath(OUT_DIR / "cls.json"),
            "mean_csv": relpath(OUT_DIR / "mean.csv"),
            "moment_csv": relpath(OUT_DIR / "moment.csv"),
            "tail_csv": relpath(OUT_DIR / "tail.csv"),
            "shrink_csv": relpath(OUT_DIR / "shrink.csv"),
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
                "exact sample-mean equality to the long_markov stationary mean through horizon 16",
                "centered moments of orders 2, 3, and 4 from long_conv marginals",
                "exact agreement with long_markov sample-mean variances through horizon eight",
                "nonnegative Chebyshev tail gaps for epsilon 1/2, 1/3, and 1/4 through horizon 16",
                "monotone sample-mean variance decrease through horizon 16",
            ],
            "does_not_certify_because_out_of_scope": [
                "an infinite-horizon convergence theorem",
                "optimal exponential concentration bounds",
                "continuous probability limits beyond finite tensor lookup",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_univ: certify the commuting profunctor diagram from "
            "line-address ownership through Markov convolution to finite LLN "
            "concentration windows."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.cls.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.cls.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "cls": cls,
        "mean_csv": csv_text(MEAN_COLUMNS, rows["mean_rows"]),
        "moment_csv": csv_text(MOMENT_COLUMNS, rows["moment_rows"]),
        "tail_csv": csv_text(TAIL_COLUMNS, rows["tail_rows"]),
        "shrink_csv": csv_text(SHRINK_COLUMNS, rows["shrink_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "mean_table": mean_table,
        "moment_table": moment_table,
        "tail_table": tail_table,
        "shrink_table": shrink_table,
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
    write_json(OUT_DIR / "cls.json", payloads["cls"])
    (OUT_DIR / "mean.csv").write_text(payloads["mean_csv"], encoding="utf-8")
    (OUT_DIR / "moment.csv").write_text(payloads["moment_csv"], encoding="utf-8")
    (OUT_DIR / "tail.csv").write_text(payloads["tail_csv"], encoding="utf-8")
    (OUT_DIR / "shrink.csv").write_text(payloads["shrink_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        mean_table=payloads["mean_table"],
        moment_table=payloads["moment_table"],
        tail_table=payloads["tail_table"],
        shrink_table=payloads["shrink_table"],
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
