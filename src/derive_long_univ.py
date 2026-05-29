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
    from .derive_long_cls import OUT_DIR as LONG_CLS_DIR, STATUS as LONG_CLS_STATUS
    from .derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
    from .derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from .derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
    )
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
    from derive_long_cls import OUT_DIR as LONG_CLS_DIR, STATUS as LONG_CLS_STATUS
    from derive_long_conv import OUT_DIR as LONG_CONV_DIR, STATUS as LONG_CONV_STATUS
    from derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
    )
    from derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_univ"
STATUS = "LONG_UNIV_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_LLN_REPORT = LONG_LLN_DIR / "report.json"
LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_OBJECT = LONG_PROF_DIR / "object.csv"
LONG_PROF_PROFUNCTOR = LONG_PROF_DIR / "profunctor.csv"
LONG_PROF_COMPOSE = LONG_PROF_DIR / "compose.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
LONG_CONV_REPORT = LONG_CONV_DIR / "report.json"
LONG_CONV_MARGINAL = LONG_CONV_DIR / "marginal.csv"
LONG_CONV_TABLES = LONG_CONV_DIR / "tables.npz"
LONG_CLS_REPORT = LONG_CLS_DIR / "report.json"
LONG_CLS_MEAN = LONG_CLS_DIR / "mean.csv"
LONG_CLS_MOMENT = LONG_CLS_DIR / "moment.csv"
LONG_CLS_TAIL = LONG_CLS_DIR / "tail.csv"
LONG_CLS_SHRINK = LONG_CLS_DIR / "shrink.csv"
LONG_CLS_TABLES = LONG_CLS_DIR / "tables.npz"
LONG_MARKOV_REPORT = LONG_MARKOV_DIR / "report.json"
LONG_MARKOV_STATIONARY = LONG_MARKOV_DIR / "stationary.csv"
LONG_MARKOV_TABLES = LONG_MARKOV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_univ.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_univ.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
HORIZON = 16
PROF_HORIZON = 8
CENTERED_MOMENT_ORDERS = (2, 3, 4)
EPSILONS = ((0, Fraction(1, 2)), (1, Fraction(1, 3)), (2, Fraction(1, 4)))

NODE_TEXT_HASH = (
    "08cc7a3d90eb6b81eec7667cc2432a797e248f0e96369834254dac431b31f683"
)
ARROW_TEXT_HASH = (
    "9eb78e387f94d558b4cbf69c8f8e2bd5aaa05aee35daaf972039fbd55a46cdc8"
)
LAW_TEXT_HASH = (
    "51b8b41fc1b9d9c15d574b9bb67d3a98c404a726c8d86f2325a4c796019ff25a"
)
SQUARE_TEXT_HASH = (
    "e8f77fa26e1b0a0090952dde1e1dc0bbfc11275a3b394b73d138597db7296fc0"
)

NODE_COLUMNS = [
    "node_id",
    "node_code",
    "node_name",
    "address_count",
    "tensor_power",
    "source_node_code",
    "public_flag",
]
NODE_DIGEST_COLUMNS = [
    "node_id",
    "node_code",
    "address_count",
    "tensor_power",
    "source_node_code",
    "public_flag",
]
ARROW_COLUMNS = [
    "arrow_id",
    "arrow_code",
    "arrow_name",
    "source_node_code",
    "target_node_code",
    "arrow_kind_code",
    "source_count",
    "target_count",
    "support_entry_count",
    "positive_entry_count",
    "total_num",
    "total_den",
    "row_sum_one_count",
    "deterministic_flag",
]
ARROW_DIGEST_COLUMNS = [
    "arrow_id",
    "arrow_code",
    "source_node_code",
    "target_node_code",
    "arrow_kind_code",
    "source_count",
    "target_count",
    "support_entry_count",
    "positive_entry_count",
    "total_num",
    "total_den",
    "row_sum_one_count",
    "deterministic_flag",
]
SQUARE_COLUMNS = [
    "square_id",
    "square_code",
    "square_name",
    "law_start",
    "law_count",
    "equal_count",
    "violation_count",
    "max_num_digits",
    "max_den_digits",
]
SQUARE_DIGEST_COLUMNS = [
    "square_id",
    "square_code",
    "law_start",
    "law_count",
    "equal_count",
    "violation_count",
    "max_num_digits",
    "max_den_digits",
]
LAW_COLUMNS = [
    "law_id",
    "square_code",
    "law_code",
    "source_id",
    "target_id",
    "subtarget_id",
    "left_num",
    "left_den",
    "right_num",
    "right_den",
    "diff_num",
    "diff_den",
    "equal_flag",
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
]
LAW_DIGEST_COLUMNS = [
    "law_id",
    "square_code",
    "law_code",
    "source_id",
    "target_id",
    "subtarget_id",
    "equal_flag",
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
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "node_count",
    "arrow_count",
    "square_count",
    "law_count",
    "law_equal_count",
    "law_violation_count",
    "node_address_total",
    "arrow_positive_entry_total",
    "prof_conv_law_count",
    "prof_conv_equal_count",
    "stationary_law_count",
    "stationary_equal_count",
    "mean_law_count",
    "mean_equal_count",
    "moment_law_count",
    "moment_equal_count",
    "tail_law_count",
    "tail_equal_count",
    "shrink_law_count",
    "shrink_equal_count",
    "law_num_digit_max",
    "law_den_digit_max",
    "long_lln_input_certified",
    "long_prof_input_certified",
    "long_conv_input_certified",
    "long_cls_input_certified",
    "long_markov_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def digest_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    return "".join(",".join(str(row[column]) for column in columns) + "\n" for row in rows)


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


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fraction_record(value: Fraction) -> dict[str, int]:
    return {
        "num_digits": len(str(abs(value.numerator))),
        "den_digits": len(str(value.denominator)),
        "num_mod_1000000007": value.numerator % MOD_PRIMES[0],
        "den_mod_1000000007": value.denominator % MOD_PRIMES[0],
        "num_mod_1000000009": value.numerator % MOD_PRIMES[1],
        "den_mod_1000000009": value.denominator % MOD_PRIMES[1],
    }


def read_fraction(row: dict[str, str], prefix: str) -> Fraction:
    return Fraction(int(row[f"{prefix}_num"]), int(row[f"{prefix}_den"]))


def build_node_rows(prof_object_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "node_id": int(row["object_id"]),
            "node_code": int(row["object_code"]),
            "node_name": row["object_name"],
            "address_count": int(row["address_count"]),
            "tensor_power": int(row["tensor_power"]),
            "source_node_code": int(row["source_object_code"]),
            "public_flag": 1,
        }
        for row in prof_object_rows
    ]
    extras = [
        (9, 9, "sample_horizon16", 16, 0, 6, 1),
        (10, 10, "sum_state16", 288, 0, 9, 1),
        (11, 11, "mean_readout", 16, 0, 10, 1),
        (12, 12, "moment_readout", 48, 0, 10, 1),
        (13, 13, "tail_window", 48, 0, 10, 1),
        (14, 14, "shrink_window", 15, 0, 12, 1),
    ]
    rows.extend(dict(zip(NODE_COLUMNS, values)) for values in extras)
    return rows


def build_arrow_rows(
    profunctor_rows: list[dict[str, str]],
    conv_rows: list[dict[str, str]],
    mean_rows: list[dict[str, str]],
    moment_rows: list[dict[str, str]],
    tail_rows: list[dict[str, str]],
    shrink_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    by_name = {row["profunctor_name"]: row for row in profunctor_rows}
    rows: list[dict[str, Any]] = []
    for arrow_id, name, kind in [
        (0, "pair_owner", 0),
        (1, "owner_component_total", 1),
        (2, "boundary_stationary", 1),
        (3, "component_kernel", 1),
        (4, "path_sum_distribution", 1),
    ]:
        row = by_name[name]
        rows.append(
            {
                "arrow_id": arrow_id,
                "arrow_code": arrow_id,
                "arrow_name": name,
                "source_node_code": int(row["source_object_code"]),
                "target_node_code": int(row["target_object_code"]),
                "arrow_kind_code": kind,
                "source_count": int(row["source_count"]),
                "target_count": int(row["target_count"]),
                "support_entry_count": int(row["support_entry_count"]),
                "positive_entry_count": int(row["positive_entry_count"]),
                "total_num": int(row["total_num"]),
                "total_den": int(row["total_den"]),
                "row_sum_one_count": int(row["source_count"])
                if int(row["row_sum_one_flag"])
                else 0,
                "deterministic_flag": int(row["deterministic_flag"]),
            }
        )
    rows.extend(
        [
            {
                "arrow_id": 5,
                "arrow_code": 5,
                "arrow_name": "conv_path_sum16",
                "source_node_code": 9,
                "target_node_code": 10,
                "arrow_kind_code": 1,
                "source_count": HORIZON,
                "target_count": len(conv_rows),
                "support_entry_count": len(conv_rows),
                "positive_entry_count": sum(int(row["positive_flag"]) for row in conv_rows),
                "total_num": HORIZON,
                "total_den": 1,
                "row_sum_one_count": HORIZON,
                "deterministic_flag": 0,
            },
            {
                "arrow_id": 6,
                "arrow_code": 6,
                "arrow_name": "mean_probe",
                "source_node_code": 10,
                "target_node_code": 11,
                "arrow_kind_code": 2,
                "source_count": HORIZON,
                "target_count": len(mean_rows),
                "support_entry_count": len(mean_rows),
                "positive_entry_count": len(mean_rows),
                "total_num": len(mean_rows),
                "total_den": 1,
                "row_sum_one_count": 0,
                "deterministic_flag": 0,
            },
            {
                "arrow_id": 7,
                "arrow_code": 7,
                "arrow_name": "moment_probe",
                "source_node_code": 10,
                "target_node_code": 12,
                "arrow_kind_code": 2,
                "source_count": HORIZON,
                "target_count": len(moment_rows),
                "support_entry_count": len(moment_rows),
                "positive_entry_count": len(moment_rows),
                "total_num": len(moment_rows),
                "total_den": 1,
                "row_sum_one_count": 0,
                "deterministic_flag": 0,
            },
            {
                "arrow_id": 8,
                "arrow_code": 8,
                "arrow_name": "tail_probe",
                "source_node_code": 10,
                "target_node_code": 13,
                "arrow_kind_code": 3,
                "source_count": HORIZON,
                "target_count": len(tail_rows),
                "support_entry_count": len(tail_rows),
                "positive_entry_count": len(tail_rows),
                "total_num": len(tail_rows),
                "total_den": 1,
                "row_sum_one_count": 0,
                "deterministic_flag": 0,
            },
            {
                "arrow_id": 9,
                "arrow_code": 9,
                "arrow_name": "shrink_probe",
                "source_node_code": 12,
                "target_node_code": 14,
                "arrow_kind_code": 4,
                "source_count": HORIZON - 1,
                "target_count": len(shrink_rows),
                "support_entry_count": len(shrink_rows),
                "positive_entry_count": len(shrink_rows),
                "total_num": len(shrink_rows),
                "total_den": 1,
                "row_sum_one_count": 0,
                "deterministic_flag": 0,
            },
        ]
    )
    return rows


def add_law(
    rows: list[dict[str, int]],
    *,
    square_code: int,
    law_code: int,
    source_id: int,
    target_id: int,
    subtarget_id: int,
    left: Fraction,
    right: Fraction,
) -> None:
    diff = left - right
    left_record = fraction_record(left)
    right_record = fraction_record(right)
    rows.append(
        {
            "law_id": len(rows),
            "square_code": square_code,
            "law_code": law_code,
            "source_id": source_id,
            "target_id": target_id,
            "subtarget_id": subtarget_id,
            "left_num": left.numerator,
            "left_den": left.denominator,
            "right_num": right.numerator,
            "right_den": right.denominator,
            "diff_num": diff.numerator,
            "diff_den": diff.denominator,
            "equal_flag": int(diff == 0),
            "left_num_digits": left_record["num_digits"],
            "left_den_digits": left_record["den_digits"],
            "left_num_mod_1000000007": left_record["num_mod_1000000007"],
            "left_den_mod_1000000007": left_record["den_mod_1000000007"],
            "left_num_mod_1000000009": left_record["num_mod_1000000009"],
            "left_den_mod_1000000009": left_record["den_mod_1000000009"],
            "right_num_digits": right_record["num_digits"],
            "right_den_digits": right_record["den_digits"],
            "right_num_mod_1000000007": right_record["num_mod_1000000007"],
            "right_den_mod_1000000007": right_record["den_mod_1000000007"],
            "right_num_mod_1000000009": right_record["num_mod_1000000009"],
            "right_den_mod_1000000009": right_record["den_mod_1000000009"],
        }
    )


def build_law_rows(
    prof_compose_rows: list[dict[str, str]],
    conv_rows: list[dict[str, str]],
    cls_mean_rows: list[dict[str, str]],
    cls_moment_rows: list[dict[str, str]],
    cls_tail_rows: list[dict[str, str]],
    cls_shrink_rows: list[dict[str, str]],
    stationary_rows: list[dict[str, str]],
    stationary_mean: Fraction,
) -> list[dict[str, int]]:
    conv = {
        (int(row["sample_count"]), int(row["sum_value"])): Fraction(
            int(row["prob_num"]),
            int(row["prob_den"]),
        )
        for row in conv_rows
    }
    prof_dev = {
        (int(row["source_id"]), int(row["target_id"])): Fraction(
            int(row["left_num"]),
            int(row["left_den"]),
        )
        for row in prof_compose_rows
        if row["law_name"] == "deviation"
    }
    laws: list[dict[str, int]] = []
    for sample_count in range(1, PROF_HORIZON + 1):
        for sum_value in range(0, 2 * sample_count + 1):
            add_law(
                laws,
                square_code=0,
                law_code=0,
                source_id=sample_count,
                target_id=sum_value,
                subtarget_id=-1,
                left=prof_dev[(sample_count, sum_value)],
                right=conv[(sample_count, sum_value)],
            )

    stationary = {
        int(row["component_id"]): Fraction(
            int(row["weight_num"]),
            int(row["weight_den"]),
        )
        for row in stationary_rows
    }
    for component_id in range(3):
        add_law(
            laws,
            square_code=1,
            law_code=1,
            source_id=1,
            target_id=component_id,
            subtarget_id=-1,
            left=stationary[component_id],
            right=conv[(1, component_id)],
        )

    mean_by_sample = {int(row["sample_count"]): row for row in cls_mean_rows}
    for sample_count in range(1, HORIZON + 1):
        left = sum(
            Fraction(sum_value, sample_count) * probability
            for (horizon, sum_value), probability in conv.items()
            if horizon == sample_count
        )
        row = mean_by_sample[sample_count]
        add_law(
            laws,
            square_code=2,
            law_code=2,
            source_id=sample_count,
            target_id=0,
            subtarget_id=-1,
            left=left,
            right=read_fraction(row, "mean"),
        )

    variance_by_sample: dict[int, Fraction] = {}
    moment_by_key = {
        (int(row["sample_count"]), int(row["moment_order"])): row
        for row in cls_moment_rows
    }
    for sample_count in range(1, HORIZON + 1):
        for moment_order in CENTERED_MOMENT_ORDERS:
            left = sum(
                (Fraction(sum_value, sample_count) - stationary_mean) ** moment_order
                * probability
                for (horizon, sum_value), probability in conv.items()
                if horizon == sample_count
            )
            if moment_order == 2:
                variance_by_sample[sample_count] = left
            row = moment_by_key[(sample_count, moment_order)]
            add_law(
                laws,
                square_code=3,
                law_code=3,
                source_id=sample_count,
                target_id=moment_order,
                subtarget_id=-1,
                left=left,
                right=read_fraction(row, "centered"),
            )

    tail_by_key = {
        (int(row["sample_count"]), int(row["epsilon_id"])): row
        for row in cls_tail_rows
    }
    for sample_count in range(1, HORIZON + 1):
        for epsilon_id, epsilon in EPSILONS:
            tail = sum(
                probability
                for (horizon, sum_value), probability in conv.items()
                if horizon == sample_count
                and abs(Fraction(sum_value, sample_count) - stationary_mean) >= epsilon
            )
            bound = variance_by_sample[sample_count] / (epsilon * epsilon)
            gap = bound - tail
            row = tail_by_key[(sample_count, epsilon_id)]
            add_law(
                laws,
                square_code=4,
                law_code=4,
                source_id=sample_count,
                target_id=epsilon_id,
                subtarget_id=0,
                left=tail,
                right=read_fraction(row, "tail"),
            )
            add_law(
                laws,
                square_code=4,
                law_code=5,
                source_id=sample_count,
                target_id=epsilon_id,
                subtarget_id=1,
                left=bound,
                right=read_fraction(row, "bound"),
            )
            add_law(
                laws,
                square_code=4,
                law_code=6,
                source_id=sample_count,
                target_id=epsilon_id,
                subtarget_id=2,
                left=gap,
                right=read_fraction(row, "gap"),
            )

    shrink_by_sample = {int(row["sample_count"]): row for row in cls_shrink_rows}
    for sample_count in range(2, HORIZON + 1):
        gap = variance_by_sample[sample_count - 1] - variance_by_sample[sample_count]
        row = shrink_by_sample[sample_count]
        add_law(
            laws,
            square_code=5,
            law_code=7,
            source_id=sample_count,
            target_id=0,
            subtarget_id=-1,
            left=gap,
            right=read_fraction(row, "shrink_gap"),
        )
    return laws


def build_square_rows(law_rows: list[dict[str, int]]) -> list[dict[str, Any]]:
    names = [
        "prof_conv_overlap",
        "stationary_seed",
        "mean_readout",
        "moment_readout",
        "tail_windows",
        "variance_shrink",
    ]
    rows: list[dict[str, Any]] = []
    for square_code, square_name in enumerate(names):
        laws = [row for row in law_rows if row["square_code"] == square_code]
        rows.append(
            {
                "square_id": square_code,
                "square_code": square_code,
                "square_name": square_name,
                "law_start": min(row["law_id"] for row in laws),
                "law_count": len(laws),
                "equal_count": sum(int(row["equal_flag"]) for row in laws),
                "violation_count": sum(int(row["equal_flag"] == 0) for row in laws),
                "max_num_digits": max(
                    max(row["left_num_digits"], row["right_num_digits"])
                    for row in laws
                ),
                "max_den_digits": max(
                    max(row["left_den_digits"], row["right_den_digits"])
                    for row in laws
                ),
            }
        )
    return rows


def build_rows() -> dict[str, Any]:
    long_lln = load_json(LONG_LLN_REPORT)
    long_prof = load_json(LONG_PROF_REPORT)
    long_conv = load_json(LONG_CONV_REPORT)
    long_cls = load_json(LONG_CLS_REPORT)
    long_markov = load_json(LONG_MARKOV_REPORT)
    mean_block = long_markov["witness"]["finite_lln"]["mean"]
    stationary_mean = Fraction(int(mean_block["num"]), int(mean_block["den"]))

    prof_object_rows = read_csv_rows(LONG_PROF_OBJECT)
    profunctor_rows = read_csv_rows(LONG_PROF_PROFUNCTOR)
    prof_compose_rows = read_csv_rows(LONG_PROF_COMPOSE)
    conv_rows = read_csv_rows(LONG_CONV_MARGINAL)
    cls_mean_rows = read_csv_rows(LONG_CLS_MEAN)
    cls_moment_rows = read_csv_rows(LONG_CLS_MOMENT)
    cls_tail_rows = read_csv_rows(LONG_CLS_TAIL)
    cls_shrink_rows = read_csv_rows(LONG_CLS_SHRINK)
    stationary_rows = read_csv_rows(LONG_MARKOV_STATIONARY)

    node_rows = build_node_rows(prof_object_rows)
    arrow_rows = build_arrow_rows(
        profunctor_rows,
        conv_rows,
        cls_mean_rows,
        cls_moment_rows,
        cls_tail_rows,
        cls_shrink_rows,
    )
    law_rows = build_law_rows(
        prof_compose_rows,
        conv_rows,
        cls_mean_rows,
        cls_moment_rows,
        cls_tail_rows,
        cls_shrink_rows,
        stationary_rows,
        stationary_mean,
    )
    square_rows = build_square_rows(law_rows)

    node_digest_rows = [
        {column: int(row[column]) for column in NODE_DIGEST_COLUMNS}
        for row in node_rows
    ]
    arrow_digest_rows = [
        {column: int(row[column]) for column in ARROW_DIGEST_COLUMNS}
        for row in arrow_rows
    ]
    square_digest_rows = [
        {column: int(row[column]) for column in SQUARE_DIGEST_COLUMNS}
        for row in square_rows
    ]
    node_table = table_from_rows(NODE_DIGEST_COLUMNS, node_digest_rows)
    arrow_table = table_from_rows(ARROW_DIGEST_COLUMNS, arrow_digest_rows)
    square_table = table_from_rows(SQUARE_DIGEST_COLUMNS, square_digest_rows)
    law_table = table_from_rows(LAW_DIGEST_COLUMNS, law_rows)

    node_hash = hashlib.sha256(digest_text(NODE_COLUMNS, node_rows).encode("ascii")).hexdigest()
    arrow_hash = hashlib.sha256(
        digest_text(ARROW_COLUMNS, arrow_rows).encode("ascii")
    ).hexdigest()
    law_hash = hashlib.sha256(digest_text(LAW_COLUMNS, law_rows).encode("ascii")).hexdigest()
    square_hash = hashlib.sha256(
        digest_text(SQUARE_COLUMNS, square_rows).encode("ascii")
    ).hexdigest()
    equal_count = sum(int(row["equal_flag"]) for row in law_rows)

    by_square = {int(row["square_code"]): row for row in square_rows}
    obs = {
        "node_count": len(node_rows),
        "arrow_count": len(arrow_rows),
        "square_count": len(square_rows),
        "law_count": len(law_rows),
        "law_equal_count": equal_count,
        "law_violation_count": len(law_rows) - equal_count,
        "node_address_total": sum(int(row["address_count"]) for row in node_rows),
        "arrow_positive_entry_total": sum(
            int(row["positive_entry_count"]) for row in arrow_rows
        ),
        "prof_conv_law_count": int(by_square[0]["law_count"]),
        "prof_conv_equal_count": int(by_square[0]["equal_count"]),
        "stationary_law_count": int(by_square[1]["law_count"]),
        "stationary_equal_count": int(by_square[1]["equal_count"]),
        "mean_law_count": int(by_square[2]["law_count"]),
        "mean_equal_count": int(by_square[2]["equal_count"]),
        "moment_law_count": int(by_square[3]["law_count"]),
        "moment_equal_count": int(by_square[3]["equal_count"]),
        "tail_law_count": int(by_square[4]["law_count"]),
        "tail_equal_count": int(by_square[4]["equal_count"]),
        "shrink_law_count": int(by_square[5]["law_count"]),
        "shrink_equal_count": int(by_square[5]["equal_count"]),
        "law_num_digit_max": max(
            max(row["left_num_digits"], row["right_num_digits"])
            for row in law_rows
        ),
        "law_den_digit_max": max(
            max(row["left_den_digits"], row["right_den_digits"])
            for row in law_rows
        ),
        "long_lln_input_certified": int(long_lln.get("status") == LONG_LLN_STATUS),
        "long_prof_input_certified": int(long_prof.get("status") == LONG_PROF_STATUS),
        "long_conv_input_certified": int(long_conv.get("status") == LONG_CONV_STATUS),
        "long_cls_input_certified": int(long_cls.get("status") == LONG_CLS_STATUS),
        "long_markov_input_certified": int(
            long_markov.get("status") == LONG_MARKOV_STATUS
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)
    return {
        "input_reports": {
            "long_lln": long_lln,
            "long_prof": long_prof,
            "long_conv": long_conv,
            "long_cls": long_cls,
            "long_markov": long_markov,
        },
        "node_rows": node_rows,
        "arrow_rows": arrow_rows,
        "square_rows": square_rows,
        "law_rows": law_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "node_table": node_table,
        "arrow_table": arrow_table,
        "square_table": square_table,
        "law_table": law_table,
        "observable_table": obs_table,
        "node_hash": node_hash,
        "arrow_hash": arrow_hash,
        "law_hash": law_hash,
        "square_hash": square_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": all(
            obs[name] == 1
            for name in [
                "long_lln_input_certified",
                "long_prof_input_certified",
                "long_conv_input_certified",
                "long_cls_input_certified",
                "long_markov_input_certified",
            ]
        ),
        "node_fingerprint_exact": (obs["node_count"], rows["node_hash"])
        == (15, NODE_TEXT_HASH),
        "arrow_fingerprint_exact": (
            obs["arrow_count"],
            obs["arrow_positive_entry_total"],
            rows["arrow_hash"],
        )
        == (10, 971_407, ARROW_TEXT_HASH),
        "law_fingerprint_exact": (
            obs["law_count"],
            obs["law_equal_count"],
            obs["law_violation_count"],
            obs["law_num_digit_max"],
            obs["law_den_digit_max"],
            rows["law_hash"],
        )
        == (306, 306, 0, 3_940, 3_941, LAW_TEXT_HASH),
        "square_fingerprint_exact": (
            obs["square_count"],
            sum(int(row["equal_count"]) for row in rows["square_rows"]),
            sum(int(row["violation_count"]) for row in rows["square_rows"]),
            rows["square_hash"],
        )
        == (6, 306, 0, SQUARE_TEXT_HASH),
        "diagram_counts_match": (
            obs["prof_conv_law_count"],
            obs["prof_conv_equal_count"],
            obs["stationary_law_count"],
            obs["stationary_equal_count"],
            obs["mean_law_count"],
            obs["mean_equal_count"],
            obs["moment_law_count"],
            obs["moment_equal_count"],
            obs["tail_law_count"],
            obs["tail_equal_count"],
            obs["shrink_law_count"],
            obs["shrink_equal_count"],
        )
        == (80, 80, 3, 3, 16, 16, 48, 48, 144, 144, 15, 15),
        "table_shapes_match": (
            tuple(rows["node_table"].shape),
            tuple(rows["arrow_table"].shape),
            tuple(rows["square_table"].shape),
            tuple(rows["law_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (15, len(NODE_DIGEST_COLUMNS)),
            (10, len(ARROW_DIGEST_COLUMNS)),
            (6, len(SQUARE_DIGEST_COLUMNS)),
            (306, len(LAW_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_universal_lln_profunctor_diagram",
        "scope": {
            "line_points": 985,
            "owner_basis": 259,
            "public_horizon": HORIZON,
            "profunctor_horizon": PROF_HORIZON,
        },
        "nodes": {
            "count": obs["node_count"],
            "address_total": obs["node_address_total"],
            "text_sha256": rows["node_hash"],
            "table_sha256": sha_array(rows["node_table"]),
        },
        "arrows": {
            "count": obs["arrow_count"],
            "positive_entry_total": obs["arrow_positive_entry_total"],
            "text_sha256": rows["arrow_hash"],
            "table_sha256": sha_array(rows["arrow_table"]),
        },
        "commuting_squares": {
            "count": obs["square_count"],
            "law_count": obs["law_count"],
            "equal_count": obs["law_equal_count"],
            "violation_count": obs["law_violation_count"],
            "square_text_sha256": rows["square_hash"],
            "law_text_sha256": rows["law_hash"],
            "square_table_sha256": sha_array(rows["square_table"]),
            "law_table_sha256": sha_array(rows["law_table"]),
            "counts": {
                "prof_conv": [
                    obs["prof_conv_law_count"],
                    obs["prof_conv_equal_count"],
                ],
                "stationary": [
                    obs["stationary_law_count"],
                    obs["stationary_equal_count"],
                ],
                "mean": [obs["mean_law_count"], obs["mean_equal_count"]],
                "moment": [obs["moment_law_count"], obs["moment_equal_count"]],
                "tail": [obs["tail_law_count"], obs["tail_equal_count"]],
                "shrink": [obs["shrink_law_count"], obs["shrink_equal_count"]],
            },
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    univ = {
        "schema": "long.univ@1",
        "object": "finite_universal_lln_profunctor_diagram",
        "status": STATUS if all(checks.values()) else "LONG_UNIV_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.univ.report@1",
        "status": univ["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_univ certifies the finite commuting diagram from the "
            "Alexandrov-line tensor address spine to LLN concentration windows: "
            "line-pair ownership and boundary profunctors feed the Markov "
            "path-sum law, the horizon-16 convolution extends that law, and "
            "mean, moment, tail, and shrink readouts commute exactly with the "
            "convolution marginals."
        ),
        "stage_protocol": {
            "draft": "read long_lln, long_prof, long_conv, long_cls, and long_markov certified artifacts",
            "witness": "emit finite nodes, arrows, commuting squares, and row-level rational equality laws",
            "coherence": "check input statuses, profunctor/convolution overlap, stationary seed, concentration readouts, hashes, and shapes",
            "closure": "emit diagram, CSV, NPZ, certificate, manifest, and report artifacts",
            "emit": "write long_univ artifacts and verifier hook",
        },
        "inputs": {
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["long_prof"].get("status")},
            ),
            "long_prof_object": input_entry(LONG_PROF_OBJECT),
            "long_prof_profunctor": input_entry(LONG_PROF_PROFUNCTOR),
            "long_prof_compose": input_entry(LONG_PROF_COMPOSE),
            "long_prof_tables": input_entry(LONG_PROF_TABLES),
            "long_conv_report": input_entry(
                LONG_CONV_REPORT,
                {"status": rows["input_reports"]["long_conv"].get("status")},
            ),
            "long_conv_marginal": input_entry(LONG_CONV_MARGINAL),
            "long_conv_tables": input_entry(LONG_CONV_TABLES),
            "long_cls_report": input_entry(
                LONG_CLS_REPORT,
                {"status": rows["input_reports"]["long_cls"].get("status")},
            ),
            "long_cls_mean": input_entry(LONG_CLS_MEAN),
            "long_cls_moment": input_entry(LONG_CLS_MOMENT),
            "long_cls_tail": input_entry(LONG_CLS_TAIL),
            "long_cls_shrink": input_entry(LONG_CLS_SHRINK),
            "long_cls_tables": input_entry(LONG_CLS_TABLES),
            "long_markov_report": input_entry(
                LONG_MARKOV_REPORT,
                {"status": rows["input_reports"]["long_markov"].get("status")},
            ),
            "long_markov_stationary": input_entry(LONG_MARKOV_STATIONARY),
            "long_markov_tables": input_entry(LONG_MARKOV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "univ": relpath(OUT_DIR / "univ.json"),
            "node_csv": relpath(OUT_DIR / "node.csv"),
            "arrow_csv": relpath(OUT_DIR / "arrow.csv"),
            "square_csv": relpath(OUT_DIR / "square.csv"),
            "law_csv": relpath(OUT_DIR / "law.csv"),
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
                "the finite node/arrow diagram from line address pairs to LLN concentration readouts",
                "exact agreement between long_prof path-sum laws and long_conv marginals through horizon eight",
                "exact agreement between the stationary boundary seed and the one-step convolution marginal",
                "exact commutation of mean, centered-moment, Chebyshev-tail, and variance-shrink readouts with horizon-16 convolution marginals",
            ],
            "does_not_certify_because_out_of_scope": [
                "all possible profunctor factorizations of the Alexandrov line",
                "an infinite-horizon probability theorem",
                "optimality or uniqueness of the selected concentration windows",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_min: identify a minimal generating subset of the "
            "long_univ commuting laws and certify which readouts are forced by "
            "the finite tensor-lookup diagram."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.univ.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.univ.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "univ": univ,
        "node_csv": csv_text(NODE_COLUMNS, rows["node_rows"]),
        "arrow_csv": csv_text(ARROW_COLUMNS, rows["arrow_rows"]),
        "square_csv": csv_text(SQUARE_COLUMNS, rows["square_rows"]),
        "law_csv": csv_text(LAW_COLUMNS, rows["law_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "node_table": rows["node_table"],
        "arrow_table": rows["arrow_table"],
        "square_table": rows["square_table"],
        "law_table": rows["law_table"],
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
    write_json(OUT_DIR / "univ.json", payloads["univ"])
    (OUT_DIR / "node.csv").write_text(payloads["node_csv"], encoding="utf-8")
    (OUT_DIR / "arrow.csv").write_text(payloads["arrow_csv"], encoding="utf-8")
    (OUT_DIR / "square.csv").write_text(payloads["square_csv"], encoding="utf-8")
    (OUT_DIR / "law.csv").write_text(payloads["law_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        node_table=payloads["node_table"],
        arrow_table=payloads["arrow_table"],
        square_table=payloads["square_table"],
        law_table=payloads["law_table"],
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
