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
    from .derive_long_absorb import (
        OUT_DIR as LONG_ABSORB_DIR,
        STATUS as LONG_ABSORB_STATUS,
        build_absorption_system,
    )
    from .derive_long_dev import (
        OUT_DIR as LONG_DEV_DIR,
        STATUS as LONG_DEV_STATUS,
        build_distributions,
        read_kernel,
        read_stationary,
    )
    from .derive_long_lap import (
        COMPONENT_COLUMNS as LAP_COMPONENT_COLUMNS,
        OUT_DIR as LONG_LAP_DIR,
        STATUS as LONG_LAP_STATUS,
    )
    from .derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
        read_transfer_matrix,
    )
    from .derive_long_rec import (
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
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
    from derive_long_absorb import (
        OUT_DIR as LONG_ABSORB_DIR,
        STATUS as LONG_ABSORB_STATUS,
        build_absorption_system,
    )
    from derive_long_dev import (
        OUT_DIR as LONG_DEV_DIR,
        STATUS as LONG_DEV_STATUS,
        build_distributions,
        read_kernel,
        read_stationary,
    )
    from derive_long_lap import (
        COMPONENT_COLUMNS as LAP_COMPONENT_COLUMNS,
        OUT_DIR as LONG_LAP_DIR,
        STATUS as LONG_LAP_STATUS,
    )
    from derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
        read_transfer_matrix,
    )
    from derive_long_rec import (
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_prof"
STATUS = "LONG_PROF_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
LONG_LAP_REPORT = LONG_LAP_DIR / "report.json"
LONG_LAP_TABLES = LONG_LAP_DIR / "tables.npz"
LONG_ABSORB_REPORT = LONG_ABSORB_DIR / "report.json"
LONG_ABSORB_TABLES = LONG_ABSORB_DIR / "tables.npz"
LONG_ABSORB_MATRIX = LONG_ABSORB_DIR / "matrix.csv"
LONG_MARKOV_REPORT = LONG_MARKOV_DIR / "report.json"
LONG_MARKOV_KERNEL = LONG_MARKOV_DIR / "kernel.csv"
LONG_MARKOV_STATIONARY = LONG_MARKOV_DIR / "stationary.csv"
LONG_DEV_REPORT = LONG_DEV_DIR / "report.json"
LONG_DEV_DISTRIBUTION = LONG_DEV_DIR / "distribution.csv"
LONG_DEV_TABLES = LONG_DEV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_prof.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_prof.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
SAMPLE_HORIZON = 8

OBJECT_CODES = {
    "unit": 0,
    "line_addr": 1,
    "line_pair": 2,
    "owner_basis": 3,
    "weak_class": 4,
    "active_owner": 5,
    "boundary_component": 6,
    "sample_horizon": 7,
    "deviation_state": 8,
}
PROFUNCTOR_CODES = {
    "pair_owner": 0,
    "owner_weak": 1,
    "active_owner_component": 2,
    "inactive_owner_component": 3,
    "owner_component_total": 4,
    "boundary_stationary": 5,
    "component_kernel": 6,
    "path_sum_distribution": 7,
}
LAW_CODES = {"stationary": 0, "kernel": 1, "deviation": 2}

OBJECT_COLUMNS = [
    "object_id",
    "object_code",
    "object_name",
    "address_count",
    "tensor_power",
    "source_object_code",
]
OBJECT_DIGEST_COLUMNS = [
    "object_id",
    "object_code",
    "address_count",
    "tensor_power",
    "source_object_code",
]
PROFUNCTOR_COLUMNS = [
    "profunctor_id",
    "profunctor_code",
    "profunctor_name",
    "source_object_code",
    "target_object_code",
    "source_count",
    "target_count",
    "support_entry_count",
    "positive_entry_count",
    "total_num",
    "total_den",
    "row_sum_one_flag",
    "deterministic_flag",
    "source_sha256",
]
PROFUNCTOR_DIGEST_COLUMNS = [
    "profunctor_id",
    "profunctor_code",
    "source_object_code",
    "target_object_code",
    "source_count",
    "target_count",
    "support_entry_count",
    "positive_entry_count",
    "total_num",
    "total_den",
    "row_sum_one_flag",
    "deterministic_flag",
]
OWNER_COMPONENT_COLUMNS = [
    "basis_id",
    "component_id",
    "prob_num",
    "prob_den",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "prob_sha256",
    "active_owner_flag",
    "dominant_component_flag",
    "positive_flag",
]
OWNER_COMPONENT_DIGEST_COLUMNS = [
    "basis_id",
    "component_id",
    "prob_num_digits",
    "prob_den_digits",
    "prob_num_mod_1000000007",
    "prob_den_mod_1000000007",
    "prob_num_mod_1000000009",
    "prob_den_mod_1000000009",
    "active_owner_flag",
    "dominant_component_flag",
    "positive_flag",
]
COMPOSE_COLUMNS = [
    "law_id",
    "law_code",
    "law_name",
    "source_id",
    "target_id",
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
COMPOSE_DIGEST_COLUMNS = [
    "law_id",
    "law_code",
    "source_id",
    "target_id",
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
    "object_count",
    "profunctor_count",
    "line_point_count",
    "line_pair_count",
    "owner_count",
    "weak_class_count",
    "active_owner_count",
    "inactive_owner_count",
    "boundary_component_count",
    "boundary_total_count",
    "deviation_distribution_row_count",
    "owner_component_row_count",
    "owner_component_positive_count",
    "owner_component_row_sum_violation_count",
    "owner_component_active_positive_count",
    "owner_component_inactive_positive_count",
    "owner_component_dominant0_count",
    "owner_component_dominant1_count",
    "owner_component_dominant2_count",
    "component0_active_owner_count",
    "component1_active_owner_count",
    "component2_active_owner_count",
    "owner_component_num_digit_max",
    "owner_component_den_digit_max",
    "compose_law_count",
    "compose_equal_count",
    "compose_violation_count",
    "composition_left_num_digit_max",
    "composition_left_den_digit_max",
    "long_rec_input_certified",
    "long_lap_input_certified",
    "long_absorb_input_certified",
    "long_markov_input_certified",
    "long_dev_input_certified",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

OBJECT_TEXT_HASH = (
    "71c02d9686d2cbe8630a48124c8b16d59ae9a3805126a4580c07142768ab2b3b"
)
PROFUNCTOR_TEXT_HASH = (
    "dbb2594318edc48bde39bdd13b323a50167c32a42450d046c95a608285db9c54"
)
OWNER_COMPONENT_TEXT_HASH = (
    "4b7bf49854c10856afab47df6569e49712192f942079140f11bdbec9435cb9a6"
)
COMPOSE_TEXT_HASH = (
    "c6a1d262c40ae9f0f2db3955a690948506b9cb7db4599558dff5f5f75cd40514"
)


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


def object_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in OBJECT_COLUMNS) + "\n"
        for row in rows
    )


def profunctor_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        ",".join(str(row[column]) for column in PROFUNCTOR_COLUMNS) + "\n"
        for row in rows
    )


def owner_component_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['basis_id']},{row['component_id']},"
        f"{row['prob_num']},{row['prob_den']},"
        f"{row['active_owner_flag']},{row['dominant_component_flag']},"
        f"{row['positive_flag']}\n"
        for row in rows
    )


def compose_text(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['law_name']},{row['source_id']},{row['target_id']},"
        f"{row['left_num']},{row['left_den']},"
        f"{row['right_num']},{row['right_den']}\n"
        for row in rows
    )


def read_distribution_rows() -> list[dict[str, str]]:
    with LONG_DEV_DISTRIBUTION.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_owner_component_rows(system: dict[str, Any]) -> dict[str, Any]:
    lap_tables = np.load(LONG_LAP_TABLES, allow_pickle=False)
    active_owners = [int(value) for value in np.asarray(lap_tables["active_owner_ids"])]
    component_ids = [int(value) for value in np.asarray(lap_tables["component_ids"])]
    active_set = set(active_owners)
    component_by_active = dict(zip(active_owners, component_ids))
    component_count = max(component_ids) + 1
    owner_by_basis = {
        int(row["basis_id"]): row for row in system["rec_owner_rows"]
    }
    inactive_rank = {
        owner: rank for rank, owner in enumerate(system["inactive_owners"])
    }

    rows: list[dict[str, Any]] = []
    digest_rows: list[dict[str, int]] = []
    row_sum_violations = 0
    dominant_counts = [0 for _ in range(component_count)]
    active_component_counts = [0 for _ in range(component_count)]
    active_positive = 0
    inactive_positive = 0
    positive_count = 0
    for owner in sorted(owner_by_basis):
        if owner in active_set:
            active_flag = 1
            active_component = int(component_by_active[owner])
            values = [
                Fraction(int(component_id == active_component))
                for component_id in range(component_count)
            ]
            active_component_counts[active_component] += 1
        else:
            active_flag = 0
            values = system["probabilities"][inactive_rank[owner]]
        if sum(values) != 1:
            row_sum_violations += 1
        dominant = max(range(component_count), key=lambda index: (values[index], -index))
        dominant_counts[dominant] += 1
        for component_id, value in enumerate(values):
            record = fraction_record(value)
            positive_flag = int(value > 0)
            positive_count += positive_flag
            if positive_flag and active_flag:
                active_positive += 1
            if positive_flag and not active_flag:
                inactive_positive += 1
            row = {
                "basis_id": owner,
                "component_id": component_id,
                "prob_num": record["num"],
                "prob_den": record["den"],
                "prob_num_digits": record["num_digits"],
                "prob_den_digits": record["den_digits"],
                "prob_num_mod_1000000007": record["num_mod_1000000007"],
                "prob_den_mod_1000000007": record["den_mod_1000000007"],
                "prob_num_mod_1000000009": record["num_mod_1000000009"],
                "prob_den_mod_1000000009": record["den_mod_1000000009"],
                "prob_sha256": record["sha256"],
                "active_owner_flag": active_flag,
                "dominant_component_flag": int(component_id == dominant),
                "positive_flag": positive_flag,
            }
            rows.append(row)
            digest_rows.append(
                {
                    column: int(row[column])
                    for column in OWNER_COMPONENT_DIGEST_COLUMNS
                }
            )
    return {
        "rows": rows,
        "digest_rows": digest_rows,
        "row_sum_violations": row_sum_violations,
        "dominant_counts": dominant_counts,
        "active_component_counts": active_component_counts,
        "active_positive": active_positive,
        "inactive_positive": inactive_positive,
        "positive_count": positive_count,
    }


def build_compose_rows() -> dict[str, Any]:
    kernel = read_kernel()
    stationary = read_stationary()
    distributions = build_distributions(kernel, stationary)
    transfer = read_transfer_matrix()
    boundary = [sum(row) for row in transfer]
    total_boundary = sum(boundary)
    dev_distribution_rows = read_distribution_rows()

    rows: list[dict[str, Any]] = []
    digest_rows: list[dict[str, int]] = []

    def append_row(
        law_name: str,
        source_id: int,
        target_id: int,
        left: Fraction,
        right: Fraction,
    ) -> None:
        law_id = len(rows)
        left_record = fraction_record(left)
        right_record = fraction_record(right)
        diff = left - right
        diff_record = fraction_record(diff)
        row = {
            "law_id": law_id,
            "law_code": LAW_CODES[law_name],
            "law_name": law_name,
            "source_id": source_id,
            "target_id": target_id,
            "left_num": left_record["num"],
            "left_den": left_record["den"],
            "right_num": right_record["num"],
            "right_den": right_record["den"],
            "diff_num": diff_record["num"],
            "diff_den": diff_record["den"],
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
        rows.append(row)
        digest_rows.append(
            {column: int(row[column]) for column in COMPOSE_DIGEST_COLUMNS}
        )

    for component_id, value in enumerate(stationary):
        append_row(
            "stationary",
            component_id,
            0,
            boundary[component_id] / total_boundary,
            value,
        )
    for row in range(3):
        for col in range(3):
            append_row("kernel", row, col, transfer[row][col] / boundary[row], kernel[row][col])
    for dev_row in dev_distribution_rows:
        sample_count = int(dev_row["sample_count"])
        sum_value = int(dev_row["sum_value"])
        append_row(
            "deviation",
            sample_count,
            sum_value,
            distributions[sample_count - 1].get(sum_value, Fraction(0)),
            Fraction(int(dev_row["prob_num"]), int(dev_row["prob_den"])),
        )
    return {"rows": rows, "digest_rows": digest_rows}


def build_rows() -> dict[str, Any]:
    long_rec = load_json(LONG_REC_REPORT)
    long_lap = load_json(LONG_LAP_REPORT)
    long_absorb = load_json(LONG_ABSORB_REPORT)
    long_markov = load_json(LONG_MARKOV_REPORT)
    long_dev = load_json(LONG_DEV_REPORT)
    rec_tables = np.load(LONG_REC_TABLES, allow_pickle=False)
    lap_tables = np.load(LONG_LAP_TABLES, allow_pickle=False)

    rec_owner_table = np.asarray(rec_tables["owner_table"])
    owner_grid = np.asarray(rec_tables["owner_grid"])
    weak_owner_table = np.asarray(rec_tables["weak_owner_table"])
    component_table = np.asarray(lap_tables["component_table"])
    component_ids = np.asarray(lap_tables["component_ids"])
    system = build_absorption_system()
    owner_component = build_owner_component_rows(system)
    compose = build_compose_rows()
    boundary_total = int(
        component_table[:, LAP_COMPONENT_COLUMNS.index("external_boundary")].sum()
    )
    line_point_count = int(owner_grid.shape[0])
    line_pair_count = int(owner_grid.size)
    owner_count = int(rec_owner_table.shape[0])
    weak_class_count = int(weak_owner_table.shape[0])
    active_owner_count = int(component_ids.shape[0])
    inactive_owner_count = owner_count - active_owner_count

    object_rows = [
        {
            "object_id": 0,
            "object_code": OBJECT_CODES["unit"],
            "object_name": "unit",
            "address_count": 1,
            "tensor_power": 0,
            "source_object_code": -1,
        },
        {
            "object_id": 1,
            "object_code": OBJECT_CODES["line_addr"],
            "object_name": "line_addr",
            "address_count": line_point_count,
            "tensor_power": 1,
            "source_object_code": -1,
        },
        {
            "object_id": 2,
            "object_code": OBJECT_CODES["line_pair"],
            "object_name": "line_pair",
            "address_count": line_pair_count,
            "tensor_power": 2,
            "source_object_code": OBJECT_CODES["line_addr"],
        },
        {
            "object_id": 3,
            "object_code": OBJECT_CODES["owner_basis"],
            "object_name": "owner_basis",
            "address_count": owner_count,
            "tensor_power": 0,
            "source_object_code": OBJECT_CODES["line_pair"],
        },
        {
            "object_id": 4,
            "object_code": OBJECT_CODES["weak_class"],
            "object_name": "weak_class",
            "address_count": weak_class_count,
            "tensor_power": 0,
            "source_object_code": OBJECT_CODES["owner_basis"],
        },
        {
            "object_id": 5,
            "object_code": OBJECT_CODES["active_owner"],
            "object_name": "active_owner",
            "address_count": active_owner_count,
            "tensor_power": 0,
            "source_object_code": OBJECT_CODES["owner_basis"],
        },
        {
            "object_id": 6,
            "object_code": OBJECT_CODES["boundary_component"],
            "object_name": "boundary_component",
            "address_count": 3,
            "tensor_power": 0,
            "source_object_code": OBJECT_CODES["active_owner"],
        },
        {
            "object_id": 7,
            "object_code": OBJECT_CODES["sample_horizon"],
            "object_name": "sample_horizon",
            "address_count": SAMPLE_HORIZON,
            "tensor_power": 0,
            "source_object_code": OBJECT_CODES["boundary_component"],
        },
        {
            "object_id": 8,
            "object_code": OBJECT_CODES["deviation_state"],
            "object_name": "deviation_state",
            "address_count": 80,
            "tensor_power": 0,
            "source_object_code": OBJECT_CODES["sample_horizon"],
        },
    ]
    object_digest_rows = [
        {column: int(row[column]) for column in OBJECT_DIGEST_COLUMNS}
        for row in object_rows
    ]
    object_table = table_from_rows(OBJECT_DIGEST_COLUMNS, object_digest_rows)

    profunctor_rows = [
        {
            "profunctor_id": 0,
            "profunctor_code": PROFUNCTOR_CODES["pair_owner"],
            "profunctor_name": "pair_owner",
            "source_object_code": OBJECT_CODES["line_pair"],
            "target_object_code": OBJECT_CODES["owner_basis"],
            "source_count": line_pair_count,
            "target_count": owner_count,
            "support_entry_count": line_pair_count,
            "positive_entry_count": line_pair_count,
            "total_num": line_pair_count,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 1,
            "source_sha256": sha_array(owner_grid),
        },
        {
            "profunctor_id": 1,
            "profunctor_code": PROFUNCTOR_CODES["owner_weak"],
            "profunctor_name": "owner_weak",
            "source_object_code": OBJECT_CODES["owner_basis"],
            "target_object_code": OBJECT_CODES["weak_class"],
            "source_count": owner_count,
            "target_count": weak_class_count,
            "support_entry_count": owner_count,
            "positive_entry_count": owner_count,
            "total_num": owner_count,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 1,
            "source_sha256": sha_array(weak_owner_table),
        },
        {
            "profunctor_id": 2,
            "profunctor_code": PROFUNCTOR_CODES["active_owner_component"],
            "profunctor_name": "active_owner_component",
            "source_object_code": OBJECT_CODES["active_owner"],
            "target_object_code": OBJECT_CODES["boundary_component"],
            "source_count": active_owner_count,
            "target_count": 3,
            "support_entry_count": active_owner_count,
            "positive_entry_count": active_owner_count,
            "total_num": active_owner_count,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 1,
            "source_sha256": sha_array(component_ids),
        },
        {
            "profunctor_id": 3,
            "profunctor_code": PROFUNCTOR_CODES["inactive_owner_component"],
            "profunctor_name": "inactive_owner_component",
            "source_object_code": OBJECT_CODES["owner_basis"],
            "target_object_code": OBJECT_CODES["boundary_component"],
            "source_count": inactive_owner_count,
            "target_count": 3,
            "support_entry_count": inactive_owner_count * 3,
            "positive_entry_count": owner_component["inactive_positive"],
            "total_num": inactive_owner_count,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 0,
            "source_sha256": hashlib.sha256(
                owner_component_text(
                    [
                        row
                        for row in owner_component["rows"]
                        if int(row["active_owner_flag"]) == 0
                    ]
                ).encode("ascii")
            ).hexdigest(),
        },
        {
            "profunctor_id": 4,
            "profunctor_code": PROFUNCTOR_CODES["owner_component_total"],
            "profunctor_name": "owner_component_total",
            "source_object_code": OBJECT_CODES["owner_basis"],
            "target_object_code": OBJECT_CODES["boundary_component"],
            "source_count": owner_count,
            "target_count": 3,
            "support_entry_count": owner_count * 3,
            "positive_entry_count": owner_component["positive_count"],
            "total_num": owner_count,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 0,
            "source_sha256": hashlib.sha256(
                owner_component_text(owner_component["rows"]).encode("ascii")
            ).hexdigest(),
        },
        {
            "profunctor_id": 5,
            "profunctor_code": PROFUNCTOR_CODES["boundary_stationary"],
            "profunctor_name": "boundary_stationary",
            "source_object_code": OBJECT_CODES["unit"],
            "target_object_code": OBJECT_CODES["boundary_component"],
            "source_count": 1,
            "target_count": 3,
            "support_entry_count": 3,
            "positive_entry_count": 3,
            "total_num": 1,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 0,
            "source_sha256": hashlib.sha256(
                LONG_MARKOV_STATIONARY.read_bytes()
            ).hexdigest(),
        },
        {
            "profunctor_id": 6,
            "profunctor_code": PROFUNCTOR_CODES["component_kernel"],
            "profunctor_name": "component_kernel",
            "source_object_code": OBJECT_CODES["boundary_component"],
            "target_object_code": OBJECT_CODES["boundary_component"],
            "source_count": 3,
            "target_count": 3,
            "support_entry_count": 9,
            "positive_entry_count": 9,
            "total_num": 3,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 0,
            "source_sha256": hashlib.sha256(LONG_MARKOV_KERNEL.read_bytes()).hexdigest(),
        },
        {
            "profunctor_id": 7,
            "profunctor_code": PROFUNCTOR_CODES["path_sum_distribution"],
            "profunctor_name": "path_sum_distribution",
            "source_object_code": OBJECT_CODES["sample_horizon"],
            "target_object_code": OBJECT_CODES["deviation_state"],
            "source_count": SAMPLE_HORIZON,
            "target_count": 80,
            "support_entry_count": 80,
            "positive_entry_count": 80,
            "total_num": SAMPLE_HORIZON,
            "total_den": 1,
            "row_sum_one_flag": 1,
            "deterministic_flag": 0,
            "source_sha256": hashlib.sha256(
                LONG_DEV_DISTRIBUTION.read_bytes()
            ).hexdigest(),
        },
    ]
    profunctor_digest_rows = [
        {column: int(row[column]) for column in PROFUNCTOR_DIGEST_COLUMNS}
        for row in profunctor_rows
    ]
    profunctor_table = table_from_rows(
        PROFUNCTOR_DIGEST_COLUMNS,
        profunctor_digest_rows,
    )
    owner_component_table = table_from_rows(
        OWNER_COMPONENT_DIGEST_COLUMNS,
        owner_component["digest_rows"],
    )
    compose_table = table_from_rows(COMPOSE_DIGEST_COLUMNS, compose["digest_rows"])

    object_hash = hashlib.sha256(object_text(object_rows).encode("ascii")).hexdigest()
    profunctor_hash = hashlib.sha256(
        profunctor_text(profunctor_rows).encode("ascii")
    ).hexdigest()
    owner_component_hash = hashlib.sha256(
        owner_component_text(owner_component["rows"]).encode("ascii")
    ).hexdigest()
    compose_hash = hashlib.sha256(compose_text(compose["rows"]).encode("ascii")).hexdigest()
    compose_equal_count = sum(int(row["equal_flag"]) for row in compose["rows"])

    obs = {
        "object_count": len(object_rows),
        "profunctor_count": len(profunctor_rows),
        "line_point_count": line_point_count,
        "line_pair_count": line_pair_count,
        "owner_count": owner_count,
        "weak_class_count": weak_class_count,
        "active_owner_count": active_owner_count,
        "inactive_owner_count": inactive_owner_count,
        "boundary_component_count": 3,
        "boundary_total_count": boundary_total,
        "deviation_distribution_row_count": 80,
        "owner_component_row_count": len(owner_component["rows"]),
        "owner_component_positive_count": owner_component["positive_count"],
        "owner_component_row_sum_violation_count": owner_component[
            "row_sum_violations"
        ],
        "owner_component_active_positive_count": owner_component["active_positive"],
        "owner_component_inactive_positive_count": owner_component[
            "inactive_positive"
        ],
        "owner_component_dominant0_count": owner_component["dominant_counts"][0],
        "owner_component_dominant1_count": owner_component["dominant_counts"][1],
        "owner_component_dominant2_count": owner_component["dominant_counts"][2],
        "component0_active_owner_count": owner_component["active_component_counts"][0],
        "component1_active_owner_count": owner_component["active_component_counts"][1],
        "component2_active_owner_count": owner_component["active_component_counts"][2],
        "owner_component_num_digit_max": max(
            int(row["prob_num_digits"]) for row in owner_component["rows"]
        ),
        "owner_component_den_digit_max": max(
            int(row["prob_den_digits"]) for row in owner_component["rows"]
        ),
        "compose_law_count": len(compose["rows"]),
        "compose_equal_count": compose_equal_count,
        "compose_violation_count": len(compose["rows"]) - compose_equal_count,
        "composition_left_num_digit_max": max(
            int(row["left_num_digits"]) for row in compose["rows"]
        ),
        "composition_left_den_digit_max": max(
            int(row["left_den_digits"]) for row in compose["rows"]
        ),
        "long_rec_input_certified": int(long_rec.get("status") == LONG_REC_STATUS),
        "long_lap_input_certified": int(long_lap.get("status") == LONG_LAP_STATUS),
        "long_absorb_input_certified": int(
            long_absorb.get("status") == LONG_ABSORB_STATUS
        ),
        "long_markov_input_certified": int(
            long_markov.get("status") == LONG_MARKOV_STATUS
        ),
        "long_dev_input_certified": int(long_dev.get("status") == LONG_DEV_STATUS),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    obs_table = table_from_rows(OBS_COLUMNS, obs_rows)

    return {
        "obs": obs,
        "object_rows": object_rows,
        "object_digest_rows": object_digest_rows,
        "profunctor_rows": profunctor_rows,
        "profunctor_digest_rows": profunctor_digest_rows,
        "owner_component_rows": owner_component["rows"],
        "owner_component_digest_rows": owner_component["digest_rows"],
        "compose_rows": compose["rows"],
        "compose_digest_rows": compose["digest_rows"],
        "obs_rows": obs_rows,
        "object_table": object_table,
        "profunctor_table": profunctor_table,
        "owner_component_table": owner_component_table,
        "compose_table": compose_table,
        "observable_table": obs_table,
        "object_hash": object_hash,
        "profunctor_hash": profunctor_hash,
        "owner_component_hash": owner_component_hash,
        "compose_hash": compose_hash,
        "input_reports": {
            "long_rec": long_rec,
            "long_lap": long_lap,
            "long_absorb": long_absorb,
            "long_markov": long_markov,
            "long_dev": long_dev,
        },
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": all(
            obs[name] == 1
            for name in [
                "long_rec_input_certified",
                "long_lap_input_certified",
                "long_absorb_input_certified",
                "long_markov_input_certified",
                "long_dev_input_certified",
            ]
        ),
        "object_fingerprint_exact": (
            obs["object_count"],
            rows["object_hash"],
        )
        == (9, OBJECT_TEXT_HASH),
        "profunctor_fingerprint_exact": (
            obs["profunctor_count"],
            rows["profunctor_hash"],
        )
        == (8, PROFUNCTOR_TEXT_HASH),
        "owner_component_fingerprint_exact": (
            obs["owner_component_row_count"],
            obs["owner_component_positive_count"],
            obs["owner_component_row_sum_violation_count"],
            obs["owner_component_num_digit_max"],
            obs["owner_component_den_digit_max"],
            rows["owner_component_hash"],
        )
        == (
            777,
            675,
            0,
            255,
            256,
            OWNER_COMPONENT_TEXT_HASH,
        ),
        "compose_fingerprint_exact": (
            obs["compose_law_count"],
            obs["compose_equal_count"],
            obs["compose_violation_count"],
            obs["composition_left_num_digit_max"],
            obs["composition_left_den_digit_max"],
            rows["compose_hash"],
        )
        == (
            92,
            92,
            0,
            1_819,
            1_820,
            COMPOSE_TEXT_HASH,
        ),
        "table_shapes_match": (
            tuple(rows["object_table"].shape),
            tuple(rows["profunctor_table"].shape),
            tuple(rows["owner_component_table"].shape),
            tuple(rows["compose_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (9, len(OBJECT_DIGEST_COLUMNS)),
            (8, len(PROFUNCTOR_DIGEST_COLUMNS)),
            (777, len(OWNER_COMPONENT_DIGEST_COLUMNS)),
            (92, len(COMPOSE_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_alexandrov_line_profunctor_tensor_lookup_chain",
        "objects": {
            "count": obs["object_count"],
            "object_text_sha256": rows["object_hash"],
            "object_table_sha256": sha_array(rows["object_table"]),
        },
        "profunctors": {
            "count": obs["profunctor_count"],
            "profunctor_text_sha256": rows["profunctor_hash"],
            "profunctor_table_sha256": sha_array(rows["profunctor_table"]),
            "chain": [
                "line_pair -> owner_basis",
                "owner_basis -> weak_class",
                "owner_basis -> boundary_component",
                "unit -> boundary_component",
                "boundary_component -> boundary_component",
                "sample_horizon -> deviation_state",
            ],
        },
        "owner_component": {
            "row_count": obs["owner_component_row_count"],
            "positive_count": obs["owner_component_positive_count"],
            "row_sum_violations": obs["owner_component_row_sum_violation_count"],
            "dominant_counts": [
                obs["owner_component_dominant0_count"],
                obs["owner_component_dominant1_count"],
                obs["owner_component_dominant2_count"],
            ],
            "active_component_counts": [
                obs["component0_active_owner_count"],
                obs["component1_active_owner_count"],
                obs["component2_active_owner_count"],
            ],
            "fraction_text_sha256": rows["owner_component_hash"],
            "digest_table_sha256": sha_array(rows["owner_component_table"]),
        },
        "composition": {
            "law_count": obs["compose_law_count"],
            "equal_count": obs["compose_equal_count"],
            "violation_count": obs["compose_violation_count"],
            "fraction_text_sha256": rows["compose_hash"],
            "digest_table_sha256": sha_array(rows["compose_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    prof = {
        "schema": "long.prof@1",
        "object": "finite_alexandrov_line_profunctor_tensor_lookup_chain",
        "status": STATUS if all(checks.values()) else "LONG_PROF_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.prof.report@1",
        "status": prof["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_prof packages the certified finite Alexandrov-line chain as "
            "explicit profunctor data: line-pair ownership, weak-class "
            "projection, owner-to-boundary hitting, stationary boundary kernel, "
            "and finite path-sum deviation readout. The downstream LLN "
            "distribution is certified as tensor lookup composition."
        ),
        "stage_protocol": {
            "draft": "take the certified long_rec, long_lap, long_absorb, long_markov, and long_dev artifacts",
            "witness": "emit finite object/profunctor tables plus exact owner-component and composition laws",
            "coherence": "check input statuses, row sums, exact equality laws, fixed hashes, and table shapes",
            "closure": "emit profunctor, CSV, NPZ, certificate, manifest, and report artifacts",
            "emit": "write long_prof artifacts and verifier hook",
        },
        "inputs": {
            "long_rec_report": input_entry(
                LONG_REC_REPORT,
                {"status": rows["input_reports"]["long_rec"].get("status")},
            ),
            "long_rec_tables": input_entry(LONG_REC_TABLES),
            "long_lap_report": input_entry(
                LONG_LAP_REPORT,
                {"status": rows["input_reports"]["long_lap"].get("status")},
            ),
            "long_lap_tables": input_entry(LONG_LAP_TABLES),
            "long_absorb_report": input_entry(
                LONG_ABSORB_REPORT,
                {"status": rows["input_reports"]["long_absorb"].get("status")},
            ),
            "long_absorb_tables": input_entry(LONG_ABSORB_TABLES),
            "long_absorb_matrix": input_entry(LONG_ABSORB_MATRIX),
            "long_markov_report": input_entry(
                LONG_MARKOV_REPORT,
                {"status": rows["input_reports"]["long_markov"].get("status")},
            ),
            "long_markov_kernel": input_entry(LONG_MARKOV_KERNEL),
            "long_markov_stationary": input_entry(LONG_MARKOV_STATIONARY),
            "long_dev_report": input_entry(
                LONG_DEV_REPORT,
                {"status": rows["input_reports"]["long_dev"].get("status")},
            ),
            "long_dev_distribution": input_entry(LONG_DEV_DISTRIBUTION),
            "long_dev_tables": input_entry(LONG_DEV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "prof": relpath(OUT_DIR / "prof.json"),
            "object_csv": relpath(OUT_DIR / "object.csv"),
            "profunctor_csv": relpath(OUT_DIR / "profunctor.csv"),
            "owner_component_csv": relpath(OUT_DIR / "owner_component.csv"),
            "compose_csv": relpath(OUT_DIR / "compose.csv"),
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
                "a finite object/profunctor spine from line pairs through owner and boundary addresses",
                "the exact 259x3 owner-to-boundary hitting profunctor",
                "stationary and kernel laws from the absorption transfer matrix",
                "the exact finite path-sum distribution laws through horizon eight as tensor lookup composition",
            ],
            "does_not_certify_because_out_of_scope": [
                "all possible profunctor presentations of the Alexandrov line",
                "asymptotic LLN or large-deviation theorems beyond the finite checked horizon",
                "support-changing recouplings outside the certified long_rec owner graph",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_rate: extract finite cumulant/rate-function fingerprints "
            "from the profunctor-composed path-sum laws and compare them against "
            "the certified long_dev Chernoff gaps."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.prof.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.prof.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "prof": prof,
        "object_csv": csv_text(OBJECT_COLUMNS, rows["object_rows"]),
        "profunctor_csv": csv_text(PROFUNCTOR_COLUMNS, rows["profunctor_rows"]),
        "owner_component_csv": csv_text(
            OWNER_COMPONENT_COLUMNS,
            rows["owner_component_rows"],
        ),
        "compose_csv": csv_text(COMPOSE_COLUMNS, rows["compose_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "object_table": rows["object_table"],
        "profunctor_table": rows["profunctor_table"],
        "owner_component_table": rows["owner_component_table"],
        "compose_table": rows["compose_table"],
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
    write_json(OUT_DIR / "prof.json", payloads["prof"])
    (OUT_DIR / "object.csv").write_text(payloads["object_csv"], encoding="utf-8")
    (OUT_DIR / "profunctor.csv").write_text(
        payloads["profunctor_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "owner_component.csv").write_text(
        payloads["owner_component_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "compose.csv").write_text(payloads["compose_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        object_table=payloads["object_table"],
        profunctor_table=payloads["profunctor_table"],
        owner_component_table=payloads["owner_component_table"],
        compose_table=payloads["compose_table"],
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
