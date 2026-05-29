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
    from .derive_long_dev import OUT_DIR as LONG_DEV_DIR, STATUS as LONG_DEV_STATUS
    from .derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_dev import OUT_DIR as LONG_DEV_DIR, STATUS as LONG_DEV_STATUS
    from derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_rate"
STATUS = "LONG_RATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_COMPOSE = LONG_PROF_DIR / "compose.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
LONG_DEV_REPORT = LONG_DEV_DIR / "report.json"
LONG_DEV_TILT = LONG_DEV_DIR / "tilt.csv"
LONG_DEV_TAIL = LONG_DEV_DIR / "tail.csv"
LONG_DEV_CHERNOFF = LONG_DEV_DIR / "chernoff.csv"
LONG_DEV_TABLES = LONG_DEV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_rate.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_rate.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
SAMPLE_HORIZON = 8
TILTS = [(0, Fraction(1, 2)), (1, Fraction(2, 1)), (2, Fraction(3, 1))]

CUMULANT_TEXT_HASH = (
    "cde28c51746fedb488e6e46f9ede898f6a87a82d78ac16b37cb94b873a8f6653"
)
BOUND_TEXT_HASH = (
    "39262abf492830a6182d9949747ea214a0b46a38f53d8bc7587c1a50ee074395"
)

CUMULANT_COLUMNS = [
    "sample_count",
    "tilt_id",
    "q_num",
    "q_den",
    "mgf_num",
    "mgf_den",
    "first_tilted_raw_num",
    "first_tilted_raw_den",
    "second_tilted_raw_num",
    "second_tilted_raw_den",
    "tilted_mean_num",
    "tilted_mean_den",
    "tilted_variance_num",
    "tilted_variance_den",
    "mgf_matches_dev_flag",
    "variance_nonnegative_flag",
]
FRACTION_NAMES = [
    "mgf",
    "first_tilted_raw",
    "second_tilted_raw",
    "tilted_mean",
    "tilted_variance",
]
CUMULANT_DIGEST_COLUMNS = [
    "sample_count",
    "tilt_id",
    "q_num",
    "q_den",
]
for _name in FRACTION_NAMES:
    CUMULANT_DIGEST_COLUMNS.extend(
        [
            f"{_name}_num_digits",
            f"{_name}_den_digits",
            f"{_name}_num_mod_1000000007",
            f"{_name}_den_mod_1000000007",
            f"{_name}_num_mod_1000000009",
            f"{_name}_den_mod_1000000009",
        ]
    )
CUMULANT_DIGEST_COLUMNS.extend(
    ["mgf_matches_dev_flag", "variance_nonnegative_flag"]
)

BOUND_COLUMNS = [
    "sample_count",
    "tail_id",
    "threshold",
    "tilt_id",
    "q_num",
    "q_den",
    "tail_num",
    "tail_den",
    "bound_num",
    "bound_den",
    "gap_num",
    "gap_den",
    "inverse_bound_num",
    "inverse_bound_den",
    "tightness_num",
    "tightness_den",
    "slack_num",
    "slack_den",
    "bound_matches_dev_flag",
    "gap_matches_dev_flag",
    "gap_nonnegative_flag",
]
BOUND_FRACTION_NAMES = [
    "tail",
    "bound",
    "gap",
    "inverse_bound",
    "tightness",
    "slack",
]
BOUND_DIGEST_COLUMNS = [
    "sample_count",
    "tail_id",
    "threshold",
    "tilt_id",
    "q_num",
    "q_den",
]
for _name in BOUND_FRACTION_NAMES:
    BOUND_DIGEST_COLUMNS.extend(
        [
            f"{_name}_num_digits",
            f"{_name}_den_digits",
            f"{_name}_num_mod_1000000007",
            f"{_name}_den_mod_1000000007",
            f"{_name}_num_mod_1000000009",
            f"{_name}_den_mod_1000000009",
        ]
    )
BOUND_DIGEST_COLUMNS.extend(
    ["bound_matches_dev_flag", "gap_matches_dev_flag", "gap_nonnegative_flag"]
)
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "sample_horizon",
    "tilt_count",
    "profunctor_distribution_row_count",
    "distribution_sum_one_count",
    "cumulant_row_count",
    "cumulant_mgf_match_count",
    "cumulant_variance_nonnegative_count",
    "cumulant_num_digit_max",
    "cumulant_den_digit_max",
    "bound_row_count",
    "bound_match_count",
    "gap_match_count",
    "gap_nonnegative_count",
    "bound_num_digit_max",
    "bound_den_digit_max",
    "prof_compose_law_count",
    "prof_compose_equal_count",
    "prof_compose_violation_count",
    "long_prof_input_certified",
    "long_dev_input_certified",
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


def digest_fields(prefix: str, value: Fraction) -> dict[str, int]:
    record = fraction_record(value)
    return {
        f"{prefix}_num_digits": int(record["num_digits"]),
        f"{prefix}_den_digits": int(record["den_digits"]),
        f"{prefix}_num_mod_1000000007": int(record["num_mod_1000000007"]),
        f"{prefix}_den_mod_1000000007": int(record["den_mod_1000000007"]),
        f"{prefix}_num_mod_1000000009": int(record["num_mod_1000000009"]),
        f"{prefix}_den_mod_1000000009": int(record["den_mod_1000000009"]),
    }


def read_prof_distributions() -> tuple[dict[int, dict[int, Fraction]], dict[str, int]]:
    distributions: dict[int, dict[int, Fraction]] = {}
    compose_law_count = 0
    compose_equal_count = 0
    with LONG_PROF_COMPOSE.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            compose_law_count += 1
            compose_equal_count += int(row["equal_flag"])
            if row["law_name"] != "deviation":
                continue
            sample_count = int(row["source_id"])
            sum_value = int(row["target_id"])
            distributions.setdefault(sample_count, {})[sum_value] = Fraction(
                int(row["right_num"]),
                int(row["right_den"]),
            )
    return distributions, {
        "compose_law_count": compose_law_count,
        "compose_equal_count": compose_equal_count,
        "compose_violation_count": compose_law_count - compose_equal_count,
    }


def read_tilts() -> dict[tuple[int, int], Fraction]:
    tilts: dict[tuple[int, int], Fraction] = {}
    with LONG_DEV_TILT.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            tilts[(int(row["sample_count"]), int(row["tilt_id"]))] = Fraction(
                int(row["value_num"]),
                int(row["value_den"]),
            )
    return tilts


def read_tails() -> dict[tuple[int, int], tuple[int, Fraction]]:
    tails: dict[tuple[int, int], tuple[int, Fraction]] = {}
    with LONG_DEV_TAIL.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            tails[(int(row["sample_count"]), int(row["tail_id"]))] = (
                int(row["threshold"]),
                Fraction(int(row["prob_num"]), int(row["prob_den"])),
            )
    return tails


def read_chernoff() -> dict[tuple[int, int], tuple[int, int, Fraction, Fraction, Fraction]]:
    chernoff: dict[tuple[int, int], tuple[int, int, Fraction, Fraction, Fraction]] = {}
    with LONG_DEV_CHERNOFF.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            chernoff[(int(row["sample_count"]), int(row["tail_id"]))] = (
                int(row["threshold"]),
                int(row["tilt_id"]),
                Fraction(int(row["q_num"]), int(row["q_den"])),
                Fraction(int(row["bound_num"]), int(row["bound_den"])),
                Fraction(int(row["gap_num"]), int(row["gap_den"])),
            )
    return chernoff


def cumulant_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['tilt_id']},{row['q_num']},{row['q_den']},"
        f"{row['mgf_num']},{row['mgf_den']},"
        f"{row['first_tilted_raw_num']},{row['first_tilted_raw_den']},"
        f"{row['second_tilted_raw_num']},{row['second_tilted_raw_den']},"
        f"{row['tilted_mean_num']},{row['tilted_mean_den']},"
        f"{row['tilted_variance_num']},{row['tilted_variance_den']},"
        f"{row['mgf_matches_dev_flag']},{row['variance_nonnegative_flag']}\n"
        for row in rows
    )


def bound_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['sample_count']},{row['tail_id']},{row['threshold']},"
        f"{row['tilt_id']},{row['q_num']},{row['q_den']},"
        f"{row['tail_num']},{row['tail_den']},"
        f"{row['bound_num']},{row['bound_den']},"
        f"{row['gap_num']},{row['gap_den']},"
        f"{row['inverse_bound_num']},{row['inverse_bound_den']},"
        f"{row['tightness_num']},{row['tightness_den']},"
        f"{row['slack_num']},{row['slack_den']},"
        f"{row['bound_matches_dev_flag']},{row['gap_matches_dev_flag']},"
        f"{row['gap_nonnegative_flag']}\n"
        for row in rows
    )


def build_rows() -> dict[str, Any]:
    long_prof = load_json(LONG_PROF_REPORT)
    long_dev = load_json(LONG_DEV_REPORT)
    distributions, compose_counts = read_prof_distributions()
    dev_tilts = read_tilts()
    dev_tails = read_tails()
    dev_chernoff = read_chernoff()

    cumulant_rows: list[dict[str, Any]] = []
    cumulant_digest_rows: list[dict[str, int]] = []
    for sample_count in range(1, SAMPLE_HORIZON + 1):
        distribution = distributions[sample_count]
        for tilt_id, q_value in TILTS:
            mgf = sum(
                q_value**sum_value * probability
                for sum_value, probability in distribution.items()
            )
            first_raw = sum(
                sum_value * q_value**sum_value * probability
                for sum_value, probability in distribution.items()
            )
            second_raw = sum(
                sum_value * sum_value * q_value**sum_value * probability
                for sum_value, probability in distribution.items()
            )
            tilted_mean = first_raw / mgf
            tilted_variance = second_raw / mgf - tilted_mean * tilted_mean
            row = {
                "sample_count": sample_count,
                "tilt_id": tilt_id,
                "q_num": q_value.numerator,
                "q_den": q_value.denominator,
                "mgf_num": mgf.numerator,
                "mgf_den": mgf.denominator,
                "first_tilted_raw_num": first_raw.numerator,
                "first_tilted_raw_den": first_raw.denominator,
                "second_tilted_raw_num": second_raw.numerator,
                "second_tilted_raw_den": second_raw.denominator,
                "tilted_mean_num": tilted_mean.numerator,
                "tilted_mean_den": tilted_mean.denominator,
                "tilted_variance_num": tilted_variance.numerator,
                "tilted_variance_den": tilted_variance.denominator,
                "mgf_matches_dev_flag": int(mgf == dev_tilts[(sample_count, tilt_id)]),
                "variance_nonnegative_flag": int(tilted_variance >= 0),
            }
            cumulant_rows.append(row)
            digest_row = {
                "sample_count": sample_count,
                "tilt_id": tilt_id,
                "q_num": q_value.numerator,
                "q_den": q_value.denominator,
                **digest_fields("mgf", mgf),
                **digest_fields("first_tilted_raw", first_raw),
                **digest_fields("second_tilted_raw", second_raw),
                **digest_fields("tilted_mean", tilted_mean),
                **digest_fields("tilted_variance", tilted_variance),
                "mgf_matches_dev_flag": int(row["mgf_matches_dev_flag"]),
                "variance_nonnegative_flag": int(row["variance_nonnegative_flag"]),
            }
            cumulant_digest_rows.append(digest_row)

    bound_rows: list[dict[str, Any]] = []
    bound_digest_rows: list[dict[str, int]] = []
    for sample_count in range(1, SAMPLE_HORIZON + 1):
        distribution = distributions[sample_count]
        for tail_id in (0, 1):
            threshold, tail = dev_tails[(sample_count, tail_id)]
            (
                chernoff_threshold,
                tilt_id,
                q_value,
                dev_bound,
                dev_gap,
            ) = dev_chernoff[(sample_count, tail_id)]
            if threshold != chernoff_threshold:
                raise ValueError("tail/chernoff threshold mismatch")
            mgf = sum(
                q_value**sum_value * probability
                for sum_value, probability in distribution.items()
            )
            bound = mgf / (q_value**threshold)
            gap = bound - tail
            inverse_bound = Fraction(1) / bound
            tightness = tail / bound
            slack = gap / bound
            row = {
                "sample_count": sample_count,
                "tail_id": tail_id,
                "threshold": threshold,
                "tilt_id": tilt_id,
                "q_num": q_value.numerator,
                "q_den": q_value.denominator,
                "tail_num": tail.numerator,
                "tail_den": tail.denominator,
                "bound_num": bound.numerator,
                "bound_den": bound.denominator,
                "gap_num": gap.numerator,
                "gap_den": gap.denominator,
                "inverse_bound_num": inverse_bound.numerator,
                "inverse_bound_den": inverse_bound.denominator,
                "tightness_num": tightness.numerator,
                "tightness_den": tightness.denominator,
                "slack_num": slack.numerator,
                "slack_den": slack.denominator,
                "bound_matches_dev_flag": int(bound == dev_bound),
                "gap_matches_dev_flag": int(gap == dev_gap),
                "gap_nonnegative_flag": int(gap >= 0),
            }
            bound_rows.append(row)
            digest_row = {
                "sample_count": sample_count,
                "tail_id": tail_id,
                "threshold": threshold,
                "tilt_id": tilt_id,
                "q_num": q_value.numerator,
                "q_den": q_value.denominator,
                **digest_fields("tail", tail),
                **digest_fields("bound", bound),
                **digest_fields("gap", gap),
                **digest_fields("inverse_bound", inverse_bound),
                **digest_fields("tightness", tightness),
                **digest_fields("slack", slack),
                "bound_matches_dev_flag": int(row["bound_matches_dev_flag"]),
                "gap_matches_dev_flag": int(row["gap_matches_dev_flag"]),
                "gap_nonnegative_flag": int(row["gap_nonnegative_flag"]),
            }
            bound_digest_rows.append(digest_row)

    distribution_sum_one_count = sum(
        int(sum(distribution.values()) == 1)
        for distribution in distributions.values()
    )
    cumulant_fraction_values = [
        Fraction(row[f"{name}_num"], row[f"{name}_den"])
        for row in cumulant_rows
        for name in [
            "mgf",
            "first_tilted_raw",
            "second_tilted_raw",
            "tilted_mean",
            "tilted_variance",
        ]
    ]
    bound_fraction_values = [
        Fraction(row[f"{name}_num"], row[f"{name}_den"])
        for row in bound_rows
        for name in [
            "tail",
            "bound",
            "gap",
            "inverse_bound",
            "tightness",
            "slack",
        ]
    ]
    obs = {
        "sample_horizon": SAMPLE_HORIZON,
        "tilt_count": len(TILTS),
        "profunctor_distribution_row_count": sum(
            len(distribution) for distribution in distributions.values()
        ),
        "distribution_sum_one_count": distribution_sum_one_count,
        "cumulant_row_count": len(cumulant_rows),
        "cumulant_mgf_match_count": sum(
            int(row["mgf_matches_dev_flag"]) for row in cumulant_rows
        ),
        "cumulant_variance_nonnegative_count": sum(
            int(row["variance_nonnegative_flag"]) for row in cumulant_rows
        ),
        "cumulant_num_digit_max": max(
            len(str(abs(value.numerator))) for value in cumulant_fraction_values
        ),
        "cumulant_den_digit_max": max(
            len(str(value.denominator)) for value in cumulant_fraction_values
        ),
        "bound_row_count": len(bound_rows),
        "bound_match_count": sum(
            int(row["bound_matches_dev_flag"]) for row in bound_rows
        ),
        "gap_match_count": sum(int(row["gap_matches_dev_flag"]) for row in bound_rows),
        "gap_nonnegative_count": sum(
            int(row["gap_nonnegative_flag"]) for row in bound_rows
        ),
        "bound_num_digit_max": max(
            len(str(abs(value.numerator))) for value in bound_fraction_values
        ),
        "bound_den_digit_max": max(
            len(str(value.denominator)) for value in bound_fraction_values
        ),
        "prof_compose_law_count": compose_counts["compose_law_count"],
        "prof_compose_equal_count": compose_counts["compose_equal_count"],
        "prof_compose_violation_count": compose_counts["compose_violation_count"],
        "long_prof_input_certified": int(long_prof.get("status") == LONG_PROF_STATUS),
        "long_dev_input_certified": int(long_dev.get("status") == LONG_DEV_STATUS),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "input_reports": {"long_prof": long_prof, "long_dev": long_dev},
        "cumulant_rows": cumulant_rows,
        "cumulant_digest_rows": cumulant_digest_rows,
        "bound_rows": bound_rows,
        "bound_digest_rows": bound_digest_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    cumulant_table = table_from_rows(
        CUMULANT_DIGEST_COLUMNS,
        rows["cumulant_digest_rows"],
    )
    bound_table = table_from_rows(BOUND_DIGEST_COLUMNS, rows["bound_digest_rows"])
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    cumulant_hash = hashlib.sha256(
        cumulant_text(rows["cumulant_rows"]).encode("ascii")
    ).hexdigest()
    bound_hash = hashlib.sha256(bound_text(rows["bound_rows"]).encode("ascii")).hexdigest()
    checks = {
        "inputs_certified": (
            obs["long_prof_input_certified"] == 1
            and obs["long_dev_input_certified"] == 1
        ),
        "profunctor_distribution_coherent": (
            obs["profunctor_distribution_row_count"],
            obs["distribution_sum_one_count"],
            obs["prof_compose_law_count"],
            obs["prof_compose_equal_count"],
            obs["prof_compose_violation_count"],
        )
        == (80, 8, 92, 92, 0),
        "cumulant_fingerprint_exact": (
            obs["cumulant_row_count"],
            obs["cumulant_mgf_match_count"],
            obs["cumulant_variance_nonnegative_count"],
            obs["cumulant_num_digit_max"],
            obs["cumulant_den_digit_max"],
            cumulant_hash,
        )
        == (24, 24, 24, 3_669, 3_669, CUMULANT_TEXT_HASH),
        "chernoff_rate_fingerprint_exact": (
            obs["bound_row_count"],
            obs["bound_match_count"],
            obs["gap_match_count"],
            obs["gap_nonnegative_count"],
            obs["bound_num_digit_max"],
            obs["bound_den_digit_max"],
            bound_hash,
        )
        == (16, 16, 16, 16, 1_835, 1_835, BOUND_TEXT_HASH),
        "table_shapes_match": (
            tuple(cumulant_table.shape),
            tuple(bound_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (24, len(CUMULANT_DIGEST_COLUMNS)),
            (16, len(BOUND_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_log_free_rate_cumulant_tensor_lookup",
        "source": {
            "distribution": "long_prof compose.csv deviation laws",
            "comparison": "long_dev tilt/tail/chernoff CSVs",
        },
        "cumulants": {
            "row_count": obs["cumulant_row_count"],
            "mgf_match_count": obs["cumulant_mgf_match_count"],
            "variance_nonnegative_count": obs[
                "cumulant_variance_nonnegative_count"
            ],
            "fraction_text_sha256": cumulant_hash,
            "digest_table_sha256": sha_array(cumulant_table),
        },
        "chernoff_rates": {
            "row_count": obs["bound_row_count"],
            "bound_match_count": obs["bound_match_count"],
            "gap_match_count": obs["gap_match_count"],
            "gap_nonnegative_count": obs["gap_nonnegative_count"],
            "fraction_text_sha256": bound_hash,
            "digest_table_sha256": sha_array(bound_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    rate = {
        "schema": "long.rate@1",
        "object": "finite_log_free_rate_cumulant_tensor_lookup",
        "status": STATUS if all(checks.values()) else "LONG_RATE_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.rate.report@1",
        "status": rate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_rate extracts exact rational cumulant and log-free Chernoff "
            "rate fingerprints from the long_prof path-sum tensor lookup, and "
            "checks them against the certified long_dev tilt and Chernoff gaps."
        ),
        "stage_protocol": {
            "draft": "read long_prof deviation composition laws and long_dev tilt/tail/chernoff witnesses",
            "witness": "compute tilted raw moments, tilted mean/variance, inverse-bound, tightness, and slack fractions",
            "coherence": "check MGF equality, Chernoff bound/gap equality, nonnegative variance/gap, hashes, and shapes",
            "closure": "emit cumulant, bound, table, certificate, manifest, and report artifacts",
            "emit": "write long_rate artifacts and verifier hook",
        },
        "inputs": {
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["long_prof"].get("status")},
            ),
            "long_prof_compose": input_entry(LONG_PROF_COMPOSE),
            "long_prof_tables": input_entry(LONG_PROF_TABLES),
            "long_dev_report": input_entry(
                LONG_DEV_REPORT,
                {"status": rows["input_reports"]["long_dev"].get("status")},
            ),
            "long_dev_tilt": input_entry(LONG_DEV_TILT),
            "long_dev_tail": input_entry(LONG_DEV_TAIL),
            "long_dev_chernoff": input_entry(LONG_DEV_CHERNOFF),
            "long_dev_tables": input_entry(LONG_DEV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "rate": relpath(OUT_DIR / "rate.json"),
            "cumulant_csv": relpath(OUT_DIR / "cumulant.csv"),
            "bound_csv": relpath(OUT_DIR / "bound.csv"),
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
                "tilted MGF, first tilted raw moment, second tilted raw moment, tilted mean, and tilted variance for q=1/2,2,3 through horizon eight",
                "exact agreement between profunctor-composed MGFs and long_dev tilt rows",
                "exact agreement between profunctor-composed Chernoff bounds/gaps and long_dev chernoff rows",
                "nonnegative exact tilted variance and Chernoff gap witnesses",
            ],
            "does_not_certify_because_out_of_scope": [
                "analytic logarithms of the cumulant generating function",
                "continuous optimization over all q",
                "asymptotic large-deviation principles",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_conv: certify convolution/composition laws for extending "
            "the profunctor path-sum distribution horizon beyond eight without "
            "leaving exact tensor lookup arithmetic."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.rate.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.rate.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "rate": rate,
        "cumulant_csv": csv_text(CUMULANT_COLUMNS, rows["cumulant_rows"]),
        "bound_csv": csv_text(BOUND_COLUMNS, rows["bound_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "cumulant_table": cumulant_table,
        "bound_table": bound_table,
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
    write_json(OUT_DIR / "rate.json", payloads["rate"])
    (OUT_DIR / "cumulant.csv").write_text(
        payloads["cumulant_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "bound.csv").write_text(payloads["bound_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        cumulant_table=payloads["cumulant_table"],
        bound_table=payloads["bound_table"],
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
