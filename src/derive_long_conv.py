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
    from .derive_long_markov import OUT_DIR as LONG_MARKOV_DIR, STATUS as LONG_MARKOV_STATUS
    from .derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from .derive_long_rate import OUT_DIR as LONG_RATE_DIR, STATUS as LONG_RATE_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_markov import OUT_DIR as LONG_MARKOV_DIR, STATUS as LONG_MARKOV_STATUS
    from derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from derive_long_rate import OUT_DIR as LONG_RATE_DIR, STATUS as LONG_RATE_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_conv"
STATUS = "LONG_CONV_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_MARKOV_REPORT = LONG_MARKOV_DIR / "report.json"
LONG_MARKOV_KERNEL = LONG_MARKOV_DIR / "kernel.csv"
LONG_MARKOV_STATIONARY = LONG_MARKOV_DIR / "stationary.csv"
LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_COMPOSE = LONG_PROF_DIR / "compose.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
LONG_RATE_REPORT = LONG_RATE_DIR / "report.json"
LONG_RATE_TABLES = LONG_RATE_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_conv.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_conv.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
COMPONENT_VALUES = [0, 1, 2]
HORIZON = 16
SPLIT_HORIZON = 8

STATE_TEXT_HASH = (
    "0e521913032a890664c162d30a68096b53c4c2bb57e33065404db22014a1509b"
)
CONTINUATION_TEXT_HASH = (
    "789f54fbc438137b8b6adc477b541ce1965d2ce7a183c1fb8688114bd5722f03"
)
MARGINAL_TEXT_HASH = (
    "c033e1e0e01d0ccdb11bedfab70c0d72ca14bf32258e0193a2a24c5f8ea4cc1d"
)
CONV_TEXT_HASH = (
    "a88527e9c215532296615269ef11f4a46999b596d2c4f1171fd49597af574761"
)

STATE_COLUMNS = [
    "sample_count",
    "end_component_id",
    "sum_value",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "positive_flag",
]
CONTINUATION_COLUMNS = [
    "continuation_horizon",
    "start_component_id",
    "end_component_id",
    "add_sum_value",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "positive_flag",
]
MARGINAL_COLUMNS = [
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
    "positive_flag",
    "prof_match_flag",
]
MARGINAL_DIGEST_COLUMNS = [
    "sample_count",
    "sum_value",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "positive_flag",
    "prof_match_flag",
]
CONV_COLUMNS = [
    "split_id",
    "left_horizon",
    "right_horizon",
    "total_horizon",
    "end_component_id",
    "sum_value",
    "left_num_digits",
    "left_den_digits",
    "left_num_mod_1000000007",
    "left_den_mod_1000000007",
    "left_num_mod_1000000009",
    "left_den_mod_1000000009",
    "right_num_digits",
    "right_den_digits",
    "right_num_mod_1000000007",
    "right_den_mod_1000000007",
    "right_num_mod_1000000009",
    "right_den_mod_1000000009",
    "equal_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "state_horizon",
    "split_horizon",
    "state_row_count",
    "state_positive_count",
    "state_mass_one_count",
    "state_num_digit_max",
    "state_den_digit_max",
    "continuation_row_count",
    "continuation_positive_count",
    "continuation_row_sum_one_count",
    "continuation_num_digit_max",
    "continuation_den_digit_max",
    "marginal_row_count",
    "marginal_positive_count",
    "marginal_sum_one_count",
    "marginal_prof_match_count",
    "marginal_num_digit_max",
    "marginal_den_digit_max",
    "convolution_row_count",
    "convolution_equal_count",
    "convolution_violation_count",
    "convolution_num_digit_max",
    "convolution_den_digit_max",
    "long_markov_input_certified",
    "long_prof_input_certified",
    "long_rate_input_certified",
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


def digest_row(value: Fraction, prefix: str = "prob") -> dict[str, int]:
    record = fraction_record(value)
    return {
        f"{prefix}_num_digits": int(record["num_digits"]),
        f"{prefix}_den_digits": int(record["den_digits"]),
        f"{prefix}_num_mod_1000000007": int(record["num_mod_1000000007"]),
        f"{prefix}_den_mod_1000000007": int(record["den_mod_1000000007"]),
        f"{prefix}_num_mod_1000000009": int(record["num_mod_1000000009"]),
        f"{prefix}_den_mod_1000000009": int(record["den_mod_1000000009"]),
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


def read_prof_deviations() -> dict[int, dict[int, Fraction]]:
    distributions: dict[int, dict[int, Fraction]] = {}
    with LONG_PROF_COMPOSE.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["law_name"] != "deviation":
                continue
            sample_count = int(row["source_id"])
            sum_value = int(row["target_id"])
            distributions.setdefault(sample_count, {})[sum_value] = Fraction(
                int(row["right_num"]),
                int(row["right_den"]),
            )
    return distributions


def build_prefix_state_laws(
    kernel: list[list[Fraction]],
    stationary: list[Fraction],
) -> list[dict[tuple[int, int], Fraction]]:
    current = {
        (component_id, COMPONENT_VALUES[component_id]): stationary[component_id]
        for component_id in range(3)
    }
    laws: list[dict[tuple[int, int], Fraction]] = []
    for _sample_count in range(1, HORIZON + 1):
        laws.append(current)
        nxt: dict[tuple[int, int], Fraction] = {}
        for (state, total), probability in current.items():
            for target in range(3):
                key = (target, total + COMPONENT_VALUES[target])
                nxt[key] = nxt.get(key, Fraction(0)) + probability * kernel[state][target]
        current = nxt
    return laws


def build_continuation_laws(
    kernel: list[list[Fraction]],
) -> list[dict[tuple[int, int, int], Fraction]]:
    laws: list[dict[tuple[int, int, int], Fraction]] = [
        {(component_id, component_id, 0): Fraction(1) for component_id in range(3)}
    ]
    for _horizon in range(1, SPLIT_HORIZON + 1):
        previous = laws[-1]
        nxt: dict[tuple[int, int, int], Fraction] = {}
        for (start, state, total), probability in previous.items():
            for target in range(3):
                key = (start, target, total + COMPONENT_VALUES[target])
                nxt[key] = nxt.get(key, Fraction(0)) + probability * kernel[state][target]
        laws.append(nxt)
    return laws


def state_text(rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in STATE_COLUMNS) + "\n"
        for row in rows
    )


def continuation_text(rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in CONTINUATION_COLUMNS) + "\n"
        for row in rows
    )


def marginal_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['sum_value']},{row['prob_num']},{row['prob_den']},"
        f"{row['positive_flag']},{row['prof_match_flag']}\n"
        for row in rows
    )


def conv_text(rows: list[dict[str, int]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in CONV_COLUMNS) + "\n"
        for row in rows
    )


def build_rows() -> dict[str, Any]:
    long_markov = load_json(LONG_MARKOV_REPORT)
    long_prof = load_json(LONG_PROF_REPORT)
    long_rate = load_json(LONG_RATE_REPORT)
    kernel = read_kernel()
    stationary = read_stationary()
    prof_deviations = read_prof_deviations()
    prefix_laws = build_prefix_state_laws(kernel, stationary)
    continuation_laws = build_continuation_laws(kernel)

    state_rows: list[dict[str, int]] = []
    for sample_count, law in enumerate(prefix_laws, start=1):
        for end_component_id in range(3):
            for sum_value in range(0, 2 * sample_count + 1):
                value = law.get((end_component_id, sum_value), Fraction(0))
                state_rows.append(
                    {
                        "sample_count": sample_count,
                        "end_component_id": end_component_id,
                        "sum_value": sum_value,
                        **digest_row(value),
                        "positive_flag": int(value > 0),
                    }
                )

    continuation_rows: list[dict[str, int]] = []
    for continuation_horizon, law in enumerate(continuation_laws):
        for start_component_id in range(3):
            for end_component_id in range(3):
                for add_sum_value in range(0, 2 * continuation_horizon + 1):
                    value = law.get(
                        (start_component_id, end_component_id, add_sum_value),
                        Fraction(0),
                    )
                    continuation_rows.append(
                        {
                            "continuation_horizon": continuation_horizon,
                            "start_component_id": start_component_id,
                            "end_component_id": end_component_id,
                            "add_sum_value": add_sum_value,
                            **digest_row(value),
                            "positive_flag": int(value > 0),
                        }
                    )

    marginal_rows: list[dict[str, Any]] = []
    marginal_digest_rows: list[dict[str, int]] = []
    for sample_count, law in enumerate(prefix_laws, start=1):
        for sum_value in range(0, 2 * sample_count + 1):
            value = sum(
                law.get((end_component_id, sum_value), Fraction(0))
                for end_component_id in range(3)
            )
            record = fraction_record(value)
            prof_match = (
                int(value == prof_deviations[sample_count][sum_value])
                if sample_count <= SPLIT_HORIZON
                else -1
            )
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
                "positive_flag": int(value > 0),
                "prof_match_flag": prof_match,
            }
            marginal_rows.append(row)
            marginal_digest_rows.append(
                {column: int(row[column]) for column in MARGINAL_DIGEST_COLUMNS}
            )

    conv_rows: list[dict[str, int]] = []
    split_id = 0
    for left_horizon in range(1, SPLIT_HORIZON + 1):
        for right_horizon in range(1, SPLIT_HORIZON + 1):
            total_horizon = left_horizon + right_horizon
            target_law = prefix_laws[total_horizon - 1]
            for end_component_id in range(3):
                for sum_value in range(0, 2 * total_horizon + 1):
                    left_value = Fraction(0)
                    for mid_component_id in range(3):
                        for prefix_sum in range(0, 2 * left_horizon + 1):
                            prefix_value = prefix_laws[left_horizon - 1].get(
                                (mid_component_id, prefix_sum),
                                Fraction(0),
                            )
                            if prefix_value == 0:
                                continue
                            add_sum = sum_value - prefix_sum
                            if 0 <= add_sum <= 2 * right_horizon:
                                left_value += prefix_value * continuation_laws[
                                    right_horizon
                                ].get(
                                    (mid_component_id, end_component_id, add_sum),
                                    Fraction(0),
                                )
                    right_value = target_law.get((end_component_id, sum_value), Fraction(0))
                    conv_rows.append(
                        {
                            "split_id": split_id,
                            "left_horizon": left_horizon,
                            "right_horizon": right_horizon,
                            "total_horizon": total_horizon,
                            "end_component_id": end_component_id,
                            "sum_value": sum_value,
                            **digest_row(left_value, "left"),
                            **digest_row(right_value, "right"),
                            "equal_flag": int(left_value == right_value),
                        }
                    )
            split_id += 1

    state_masses = [
        sum(law.values())
        for law in prefix_laws
    ]
    continuation_row_sums = [
        sum(
            law.get((start_component_id, end_component_id, add_sum_value), Fraction(0))
            for end_component_id in range(3)
            for add_sum_value in range(0, 2 * continuation_horizon + 1)
        )
        for continuation_horizon, law in enumerate(continuation_laws)
        for start_component_id in range(3)
    ]
    marginal_masses = [
        sum(
            Fraction(row["prob_num"], row["prob_den"])
            for row in marginal_rows
            if int(row["sample_count"]) == sample_count
        )
        for sample_count in range(1, HORIZON + 1)
    ]
    obs = {
        "state_horizon": HORIZON,
        "split_horizon": SPLIT_HORIZON,
        "state_row_count": len(state_rows),
        "state_positive_count": sum(row["positive_flag"] for row in state_rows),
        "state_mass_one_count": sum(int(value == 1) for value in state_masses),
        "state_num_digit_max": max(row["prob_num_digits"] for row in state_rows),
        "state_den_digit_max": max(row["prob_den_digits"] for row in state_rows),
        "continuation_row_count": len(continuation_rows),
        "continuation_positive_count": sum(
            row["positive_flag"] for row in continuation_rows
        ),
        "continuation_row_sum_one_count": sum(
            int(value == 1) for value in continuation_row_sums
        ),
        "continuation_num_digit_max": max(
            row["prob_num_digits"] for row in continuation_rows
        ),
        "continuation_den_digit_max": max(
            row["prob_den_digits"] for row in continuation_rows
        ),
        "marginal_row_count": len(marginal_rows),
        "marginal_positive_count": sum(row["positive_flag"] for row in marginal_rows),
        "marginal_sum_one_count": sum(int(value == 1) for value in marginal_masses),
        "marginal_prof_match_count": sum(
            int(row["prof_match_flag"] == 1) for row in marginal_rows
        ),
        "marginal_num_digit_max": max(row["prob_num_digits"] for row in marginal_rows),
        "marginal_den_digit_max": max(row["prob_den_digits"] for row in marginal_rows),
        "convolution_row_count": len(conv_rows),
        "convolution_equal_count": sum(row["equal_flag"] for row in conv_rows),
        "convolution_violation_count": sum(
            int(row["equal_flag"] == 0) for row in conv_rows
        ),
        "convolution_num_digit_max": max(
            max(row["left_num_digits"], row["right_num_digits"]) for row in conv_rows
        ),
        "convolution_den_digit_max": max(
            max(row["left_den_digits"], row["right_den_digits"]) for row in conv_rows
        ),
        "long_markov_input_certified": int(
            long_markov.get("status") == LONG_MARKOV_STATUS
        ),
        "long_prof_input_certified": int(long_prof.get("status") == LONG_PROF_STATUS),
        "long_rate_input_certified": int(long_rate.get("status") == LONG_RATE_STATUS),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "input_reports": {
            "long_markov": long_markov,
            "long_prof": long_prof,
            "long_rate": long_rate,
        },
        "state_rows": state_rows,
        "continuation_rows": continuation_rows,
        "marginal_rows": marginal_rows,
        "marginal_digest_rows": marginal_digest_rows,
        "conv_rows": conv_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    state_table = table_from_rows(STATE_COLUMNS, rows["state_rows"])
    continuation_table = table_from_rows(
        CONTINUATION_COLUMNS,
        rows["continuation_rows"],
    )
    marginal_table = table_from_rows(
        MARGINAL_DIGEST_COLUMNS,
        rows["marginal_digest_rows"],
    )
    conv_table = table_from_rows(CONV_COLUMNS, rows["conv_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    state_hash = hashlib.sha256(state_text(rows["state_rows"]).encode("ascii")).hexdigest()
    continuation_hash = hashlib.sha256(
        continuation_text(rows["continuation_rows"]).encode("ascii")
    ).hexdigest()
    marginal_hash = hashlib.sha256(
        marginal_text(rows["marginal_rows"]).encode("ascii")
    ).hexdigest()
    conv_hash = hashlib.sha256(conv_text(rows["conv_rows"]).encode("ascii")).hexdigest()
    checks = {
        "inputs_certified": (
            obs["long_markov_input_certified"] == 1
            and obs["long_prof_input_certified"] == 1
            and obs["long_rate_input_certified"] == 1
        ),
        "state_fingerprint_exact": (
            obs["state_row_count"],
            obs["state_positive_count"],
            obs["state_mass_one_count"],
            obs["state_num_digit_max"],
            obs["state_den_digit_max"],
            state_hash,
        )
        == (864, 768, 16, 3_890, 3_892, STATE_TEXT_HASH),
        "continuation_fingerprint_exact": (
            obs["continuation_row_count"],
            obs["continuation_positive_count"],
            obs["continuation_row_sum_one_count"],
            obs["continuation_num_digit_max"],
            obs["continuation_den_digit_max"],
            continuation_hash,
        )
        == (729, 579, 27, 2_070, 2_071, CONTINUATION_TEXT_HASH),
        "marginal_fingerprint_exact": (
            obs["marginal_row_count"],
            obs["marginal_positive_count"],
            obs["marginal_sum_one_count"],
            obs["marginal_prof_match_count"],
            obs["marginal_num_digit_max"],
            obs["marginal_den_digit_max"],
            marginal_hash,
        )
        == (288, 288, 16, 80, 3_893, 3_895, MARGINAL_TEXT_HASH),
        "convolution_fingerprint_exact": (
            obs["convolution_row_count"],
            obs["convolution_equal_count"],
            obs["convolution_violation_count"],
            obs["convolution_num_digit_max"],
            obs["convolution_den_digit_max"],
            conv_hash,
        )
        == (3_648, 3_648, 0, 3_890, 3_892, CONV_TEXT_HASH),
        "table_shapes_match": (
            tuple(state_table.shape),
            tuple(continuation_table.shape),
            tuple(marginal_table.shape),
            tuple(conv_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (864, len(STATE_COLUMNS)),
            (729, len(CONTINUATION_COLUMNS)),
            (288, len(MARGINAL_DIGEST_COLUMNS)),
            (3_648, len(CONV_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_stateful_path_sum_convolution_tensor_lookup",
        "horizon": {
            "state_horizon": HORIZON,
            "split_horizon": SPLIT_HORIZON,
            "extended_public_horizon": HORIZON,
        },
        "state_laws": {
            "row_count": obs["state_row_count"],
            "positive_count": obs["state_positive_count"],
            "mass_one_count": obs["state_mass_one_count"],
            "digest_text_sha256": state_hash,
            "table_sha256": sha_array(state_table),
        },
        "continuation_laws": {
            "row_count": obs["continuation_row_count"],
            "positive_count": obs["continuation_positive_count"],
            "row_sum_one_count": obs["continuation_row_sum_one_count"],
            "digest_text_sha256": continuation_hash,
            "table_sha256": sha_array(continuation_table),
        },
        "marginals": {
            "row_count": obs["marginal_row_count"],
            "positive_count": obs["marginal_positive_count"],
            "mass_one_count": obs["marginal_sum_one_count"],
            "prof_match_count": obs["marginal_prof_match_count"],
            "fraction_text_sha256": marginal_hash,
            "table_sha256": sha_array(marginal_table),
        },
        "convolution": {
            "row_count": obs["convolution_row_count"],
            "equal_count": obs["convolution_equal_count"],
            "violation_count": obs["convolution_violation_count"],
            "digest_text_sha256": conv_hash,
            "table_sha256": sha_array(conv_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    conv = {
        "schema": "long.conv@1",
        "object": "finite_stateful_path_sum_convolution_tensor_lookup",
        "status": STATUS if all(checks.values()) else "LONG_CONV_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.conv.report@1",
        "status": conv["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_conv certifies the exact stateful convolution law behind the "
            "long_prof path-sum tensor lookup: state-sum prefix laws through "
            "horizon 16, continuation kernels through horizon 8, and all "
            "a+b split compositions for a,b<=8."
        ),
        "stage_protocol": {
            "draft": "read long_markov's kernel/stationary law and long_prof's public deviation composition",
            "witness": "compute state-sum prefix, continuation, marginal, and split-convolution tables",
            "coherence": "check mass conservation, long_prof agreement through horizon eight, exact split equalities, hashes, and shapes",
            "closure": "emit state, continuation, marginal, convolution, table, certificate, manifest, and report artifacts",
            "emit": "write long_conv artifacts and verifier hook",
        },
        "inputs": {
            "long_markov_report": input_entry(
                LONG_MARKOV_REPORT,
                {"status": rows["input_reports"]["long_markov"].get("status")},
            ),
            "long_markov_kernel": input_entry(LONG_MARKOV_KERNEL),
            "long_markov_stationary": input_entry(LONG_MARKOV_STATIONARY),
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["long_prof"].get("status")},
            ),
            "long_prof_compose": input_entry(LONG_PROF_COMPOSE),
            "long_prof_tables": input_entry(LONG_PROF_TABLES),
            "long_rate_report": input_entry(
                LONG_RATE_REPORT,
                {"status": rows["input_reports"]["long_rate"].get("status")},
            ),
            "long_rate_tables": input_entry(LONG_RATE_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "conv": relpath(OUT_DIR / "conv.json"),
            "state_csv": relpath(OUT_DIR / "state.csv"),
            "continuation_csv": relpath(OUT_DIR / "continuation.csv"),
            "marginal_csv": relpath(OUT_DIR / "marginal.csv"),
            "convolution_csv": relpath(OUT_DIR / "convolution.csv"),
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
                "state-sum path laws through horizon 16",
                "continuation kernels through horizon 8",
                "public path-sum marginals through horizon 16, matching long_prof through horizon 8",
                "all exact split-convolution identities for a,b<=8",
            ],
            "does_not_certify_because_out_of_scope": [
                "an infinite-horizon Markov theorem",
                "analytic rates or logarithmic limit transforms",
                "support-changing recouplings outside the certified long_rec owner graph",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_cls: certify finite concentration/LLN shrinkage from "
            "the horizon-16 convolution laws using exact centered moments and "
            "tail windows."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.conv.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.conv.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "conv": conv,
        "state_csv": csv_text(STATE_COLUMNS, rows["state_rows"]),
        "continuation_csv": csv_text(CONTINUATION_COLUMNS, rows["continuation_rows"]),
        "marginal_csv": csv_text(MARGINAL_COLUMNS, rows["marginal_rows"]),
        "convolution_csv": csv_text(CONV_COLUMNS, rows["conv_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "state_table": state_table,
        "continuation_table": continuation_table,
        "marginal_table": marginal_table,
        "convolution_table": conv_table,
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
    write_json(OUT_DIR / "conv.json", payloads["conv"])
    (OUT_DIR / "state.csv").write_text(payloads["state_csv"], encoding="utf-8")
    (OUT_DIR / "continuation.csv").write_text(
        payloads["continuation_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "marginal.csv").write_text(payloads["marginal_csv"], encoding="utf-8")
    (OUT_DIR / "convolution.csv").write_text(
        payloads["convolution_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        state_table=payloads["state_table"],
        continuation_table=payloads["continuation_table"],
        marginal_table=payloads["marginal_table"],
        convolution_table=payloads["convolution_table"],
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
