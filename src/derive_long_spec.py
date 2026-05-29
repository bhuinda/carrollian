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
    from .derive_long_absorb import (
        OUT_DIR as LONG_ABSORB_DIR,
        STATUS as LONG_ABSORB_STATUS,
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
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_spec"
STATUS = "LONG_SPEC_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_ABSORB_REPORT = LONG_ABSORB_DIR / "report.json"
LONG_ABSORB_MATRIX = LONG_ABSORB_DIR / "matrix.csv"
LONG_ABSORB_TABLES = LONG_ABSORB_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_spec.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_spec.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
SPECTRAL_NAMES = [
    "trace",
    "tree_cofactor",
    "pseudodeterminant",
    "discriminant",
]

SCHUR_COLUMNS = [
    "row_component_id",
    "col_component_id",
    "entry_num",
    "entry_den",
    "entry_num_digits",
    "entry_den_digits",
    "entry_num_mod_1000000007",
    "entry_den_mod_1000000007",
    "entry_num_mod_1000000009",
    "entry_den_mod_1000000009",
    "entry_sha256",
    "diagonal_flag",
]
SCHUR_DIGEST_COLUMNS = [
    "row_component_id",
    "col_component_id",
    "entry_num_digits",
    "entry_den_digits",
    "entry_num_mod_1000000007",
    "entry_den_mod_1000000007",
    "entry_num_mod_1000000009",
    "entry_den_mod_1000000009",
    "diagonal_flag",
]
EDGE_COLUMNS = [
    "edge_id",
    "left_component_id",
    "right_component_id",
    "conductance_num",
    "conductance_den",
    "conductance_num_digits",
    "conductance_den_digits",
    "conductance_num_mod_1000000007",
    "conductance_den_mod_1000000007",
    "conductance_num_mod_1000000009",
    "conductance_den_mod_1000000009",
    "conductance_sha256",
]
EDGE_DIGEST_COLUMNS = [
    "edge_id",
    "left_component_id",
    "right_component_id",
    "conductance_num_digits",
    "conductance_den_digits",
    "conductance_num_mod_1000000007",
    "conductance_den_mod_1000000007",
    "conductance_num_mod_1000000009",
    "conductance_den_mod_1000000009",
]
RESISTANCE_COLUMNS = [
    "pair_id",
    "left_component_id",
    "right_component_id",
    "resistance_num",
    "resistance_den",
    "resistance_num_digits",
    "resistance_den_digits",
    "resistance_num_mod_1000000007",
    "resistance_den_mod_1000000007",
    "resistance_num_mod_1000000009",
    "resistance_den_mod_1000000009",
    "resistance_sha256",
]
RESISTANCE_DIGEST_COLUMNS = [
    "pair_id",
    "left_component_id",
    "right_component_id",
    "resistance_num_digits",
    "resistance_den_digits",
    "resistance_num_mod_1000000007",
    "resistance_den_mod_1000000007",
    "resistance_num_mod_1000000009",
    "resistance_den_mod_1000000009",
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
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "line_point_count",
    "active_component_count",
    "boundary0_count",
    "boundary1_count",
    "boundary2_count",
    "boundary_total_count",
    "schur_entry_count",
    "schur_edge_count",
    "schur_rank_mod_1000000007",
    "schur_rank_mod_1000000009",
    "schur_row_sum_zero_flag",
    "schur_symmetric_flag",
    "schur_cofactor_equal_flag",
    "schur_positive_edge_flag",
    "spectral_invariant_count",
    "trace_num_digits",
    "trace_den_digits",
    "trace_num_mod_1000000007",
    "trace_den_mod_1000000007",
    "tree_num_digits",
    "tree_den_digits",
    "tree_num_mod_1000000007",
    "tree_den_mod_1000000007",
    "pseudodet_num_digits",
    "pseudodet_den_digits",
    "pseudodet_num_mod_1000000007",
    "pseudodet_den_mod_1000000007",
    "discriminant_num_digits",
    "discriminant_den_digits",
    "discriminant_num_mod_1000000007",
    "discriminant_den_mod_1000000007",
    "discriminant_positive_flag",
    "discriminant_rational_square_flag",
    "resistance_pair_count",
    "resistance_num_digit_min",
    "resistance_num_digit_max",
    "resistance_den_digit_min",
    "resistance_den_digit_max",
    "long_absorb_input_certified",
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


def fraction_from_csv(row: dict[str, str]) -> Fraction:
    return Fraction(int(row["flow_num"]), int(row["flow_den"]))


def fraction_to_mod(value: Fraction, prime: int) -> int:
    return value.numerator * pow(value.denominator, prime - 2, prime) % prime


def rank_mod(matrix: list[list[Fraction]], prime: int) -> int:
    mod_matrix = [
        [fraction_to_mod(value, prime) for value in row]
        for row in matrix
    ]
    row_count = len(mod_matrix)
    col_count = len(mod_matrix[0])
    rank = 0
    for col in range(col_count):
        pivot = next(
            (row for row in range(rank, row_count) if mod_matrix[row][col] % prime),
            None,
        )
        if pivot is None:
            continue
        mod_matrix[rank], mod_matrix[pivot] = mod_matrix[pivot], mod_matrix[rank]
        inverse = pow(mod_matrix[rank][col], prime - 2, prime)
        for entry in range(col, col_count):
            mod_matrix[rank][entry] = mod_matrix[rank][entry] * inverse % prime
        for row in range(row_count):
            if row == rank or not mod_matrix[row][col] % prime:
                continue
            factor = mod_matrix[row][col]
            for entry in range(col, col_count):
                mod_matrix[row][entry] = (
                    mod_matrix[row][entry] - factor * mod_matrix[rank][entry]
                ) % prime
        rank += 1
    return rank


def schur_fraction_text(schur_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['row_component_id']},{row['col_component_id']},"
        f"{row['entry_num']},{row['entry_den']}\n"
        for row in schur_rows
    )


def edge_fraction_text(edge_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['left_component_id']},{row['right_component_id']},"
        f"{row['conductance_num']},{row['conductance_den']}\n"
        for row in edge_rows
    )


def resistance_fraction_text(resistance_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['left_component_id']},{row['right_component_id']},"
        f"{row['resistance_num']},{row['resistance_den']}\n"
        for row in resistance_rows
    )


def spectral_fraction_text(spectral_rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"{row['invariant_id']},{row['invariant_name']},"
        f"{row['value_num']},{row['value_den']}\n"
        for row in spectral_rows
    )


def read_transfer_matrix() -> list[list[Fraction]]:
    matrix = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    with LONG_ABSORB_MATRIX.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source = int(row["source_component_id"])
            target = int(row["absorbing_component_id"])
            matrix[source][target] = fraction_from_csv(row)
    return matrix


def build_rows() -> dict[str, Any]:
    long_absorb = load_json(LONG_ABSORB_REPORT)
    transfer = read_transfer_matrix()
    boundary = [sum(transfer[row][col] for col in range(3)) for row in range(3)]
    schur = [
        [
            (boundary[row] if row == col else Fraction(0)) - transfer[row][col]
            for col in range(3)
        ]
        for row in range(3)
    ]
    conductances = [
        (0, 1, transfer[0][1]),
        (0, 2, transfer[0][2]),
        (1, 2, transfer[1][2]),
    ]
    trace = sum(schur[index][index] for index in range(3))
    tree = (
        conductances[0][2] * conductances[1][2]
        + conductances[0][2] * conductances[2][2]
        + conductances[1][2] * conductances[2][2]
    )
    pseudodeterminant = 3 * tree
    discriminant = trace * trace - 4 * pseudodeterminant
    spectral_values = [trace, tree, pseudodeterminant, discriminant]
    resistances = [
        (0, 1, (conductances[1][2] + conductances[2][2]) / tree),
        (0, 2, (conductances[0][2] + conductances[2][2]) / tree),
        (1, 2, (conductances[0][2] + conductances[1][2]) / tree),
    ]

    schur_rows: list[dict[str, Any]] = []
    schur_digest_rows: list[dict[str, int]] = []
    for row in range(3):
        for col in range(3):
            value = schur[row][col]
            record = fraction_record(value)
            out_row = {
                "row_component_id": row,
                "col_component_id": col,
                "entry_num": record["num"],
                "entry_den": record["den"],
                "entry_num_digits": record["num_digits"],
                "entry_den_digits": record["den_digits"],
                "entry_num_mod_1000000007": record["num_mod_1000000007"],
                "entry_den_mod_1000000007": record["den_mod_1000000007"],
                "entry_num_mod_1000000009": record["num_mod_1000000009"],
                "entry_den_mod_1000000009": record["den_mod_1000000009"],
                "entry_sha256": record["sha256"],
                "diagonal_flag": int(row == col),
            }
            schur_rows.append(out_row)
            schur_digest_rows.append(
                {column: int(out_row[column]) for column in SCHUR_DIGEST_COLUMNS}
            )

    edge_rows: list[dict[str, Any]] = []
    edge_digest_rows: list[dict[str, int]] = []
    for edge_id, (left, right, value) in enumerate(conductances):
        record = fraction_record(value)
        out_row = {
            "edge_id": edge_id,
            "left_component_id": left,
            "right_component_id": right,
            "conductance_num": record["num"],
            "conductance_den": record["den"],
            "conductance_num_digits": record["num_digits"],
            "conductance_den_digits": record["den_digits"],
            "conductance_num_mod_1000000007": record["num_mod_1000000007"],
            "conductance_den_mod_1000000007": record["den_mod_1000000007"],
            "conductance_num_mod_1000000009": record["num_mod_1000000009"],
            "conductance_den_mod_1000000009": record["den_mod_1000000009"],
            "conductance_sha256": record["sha256"],
        }
        edge_rows.append(out_row)
        edge_digest_rows.append(
            {column: int(out_row[column]) for column in EDGE_DIGEST_COLUMNS}
        )

    resistance_rows: list[dict[str, Any]] = []
    resistance_digest_rows: list[dict[str, int]] = []
    for pair_id, (left, right, value) in enumerate(resistances):
        record = fraction_record(value)
        out_row = {
            "pair_id": pair_id,
            "left_component_id": left,
            "right_component_id": right,
            "resistance_num": record["num"],
            "resistance_den": record["den"],
            "resistance_num_digits": record["num_digits"],
            "resistance_den_digits": record["den_digits"],
            "resistance_num_mod_1000000007": record["num_mod_1000000007"],
            "resistance_den_mod_1000000007": record["den_mod_1000000007"],
            "resistance_num_mod_1000000009": record["num_mod_1000000009"],
            "resistance_den_mod_1000000009": record["den_mod_1000000009"],
            "resistance_sha256": record["sha256"],
        }
        resistance_rows.append(out_row)
        resistance_digest_rows.append(
            {
                column: int(out_row[column])
                for column in RESISTANCE_DIGEST_COLUMNS
            }
        )

    spectral_rows: list[dict[str, Any]] = []
    spectral_digest_rows: list[dict[str, int]] = []
    for invariant_id, (name, value) in enumerate(
        zip(SPECTRAL_NAMES, spectral_values)
    ):
        record = fraction_record(value)
        out_row = {
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
        spectral_rows.append(out_row)
        spectral_digest_rows.append(
            {
                column: int(out_row[column])
                for column in SPECTRAL_DIGEST_COLUMNS
            }
        )

    cofactor_values = []
    for drop in range(3):
        keep = [index for index in range(3) if index != drop]
        cofactor_values.append(
            schur[keep[0]][keep[0]] * schur[keep[1]][keep[1]]
            - schur[keep[0]][keep[1]] * schur[keep[1]][keep[0]]
        )
    resistance_num_digits = [
        int(row["resistance_num_digits"]) for row in resistance_rows
    ]
    resistance_den_digits = [
        int(row["resistance_den_digits"]) for row in resistance_rows
    ]
    trace_record = fraction_record(trace)
    tree_record = fraction_record(tree)
    pseudodet_record = fraction_record(pseudodeterminant)
    discriminant_record = fraction_record(discriminant)
    obs = {
        "line_point_count": 985,
        "active_component_count": 3,
        "boundary0_count": int(boundary[0]),
        "boundary1_count": int(boundary[1]),
        "boundary2_count": int(boundary[2]),
        "boundary_total_count": int(sum(boundary)),
        "schur_entry_count": 9,
        "schur_edge_count": 3,
        "schur_rank_mod_1000000007": rank_mod(schur, MOD_PRIMES[0]),
        "schur_rank_mod_1000000009": rank_mod(schur, MOD_PRIMES[1]),
        "schur_row_sum_zero_flag": int(
            all(sum(row) == 0 for row in schur)
        ),
        "schur_symmetric_flag": int(
            all(schur[row][col] == schur[col][row] for row in range(3) for col in range(3))
        ),
        "schur_cofactor_equal_flag": int(
            all(value == tree for value in cofactor_values)
        ),
        "schur_positive_edge_flag": int(
            all(value > 0 for _left, _right, value in conductances)
        ),
        "spectral_invariant_count": len(spectral_rows),
        "trace_num_digits": int(trace_record["num_digits"]),
        "trace_den_digits": int(trace_record["den_digits"]),
        "trace_num_mod_1000000007": int(trace_record["num_mod_1000000007"]),
        "trace_den_mod_1000000007": int(trace_record["den_mod_1000000007"]),
        "tree_num_digits": int(tree_record["num_digits"]),
        "tree_den_digits": int(tree_record["den_digits"]),
        "tree_num_mod_1000000007": int(tree_record["num_mod_1000000007"]),
        "tree_den_mod_1000000007": int(tree_record["den_mod_1000000007"]),
        "pseudodet_num_digits": int(pseudodet_record["num_digits"]),
        "pseudodet_den_digits": int(pseudodet_record["den_digits"]),
        "pseudodet_num_mod_1000000007": int(
            pseudodet_record["num_mod_1000000007"]
        ),
        "pseudodet_den_mod_1000000007": int(
            pseudodet_record["den_mod_1000000007"]
        ),
        "discriminant_num_digits": int(discriminant_record["num_digits"]),
        "discriminant_den_digits": int(discriminant_record["den_digits"]),
        "discriminant_num_mod_1000000007": int(
            discriminant_record["num_mod_1000000007"]
        ),
        "discriminant_den_mod_1000000007": int(
            discriminant_record["den_mod_1000000007"]
        ),
        "discriminant_positive_flag": int(discriminant > 0),
        "discriminant_rational_square_flag": int(
            math.isqrt(discriminant.numerator) ** 2 == discriminant.numerator
            and math.isqrt(discriminant.denominator) ** 2
            == discriminant.denominator
        ),
        "resistance_pair_count": len(resistance_rows),
        "resistance_num_digit_min": min(resistance_num_digits),
        "resistance_num_digit_max": max(resistance_num_digits),
        "resistance_den_digit_min": min(resistance_den_digits),
        "resistance_den_digit_max": max(resistance_den_digits),
        "long_absorb_input_certified": int(
            long_absorb.get("status") == LONG_ABSORB_STATUS
        ),
    }
    obs_rows = [
        {"observable_id": code, "observable_code": code, "value": int(obs[name])}
        for name, code in sorted(OBS_CODES.items(), key=lambda item: item[1])
    ]
    return {
        "long_absorb": long_absorb,
        "transfer": transfer,
        "boundary": boundary,
        "schur": schur,
        "conductances": conductances,
        "resistances": resistances,
        "spectral_values": spectral_values,
        "cofactor_values": cofactor_values,
        "schur_rows": schur_rows,
        "schur_digest_rows": schur_digest_rows,
        "edge_rows": edge_rows,
        "edge_digest_rows": edge_digest_rows,
        "resistance_rows": resistance_rows,
        "resistance_digest_rows": resistance_digest_rows,
        "spectral_rows": spectral_rows,
        "spectral_digest_rows": spectral_digest_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    schur_digest_table = table_from_rows(
        SCHUR_DIGEST_COLUMNS,
        rows["schur_digest_rows"],
    )
    edge_digest_table = table_from_rows(
        EDGE_DIGEST_COLUMNS,
        rows["edge_digest_rows"],
    )
    resistance_digest_table = table_from_rows(
        RESISTANCE_DIGEST_COLUMNS,
        rows["resistance_digest_rows"],
    )
    spectral_digest_table = table_from_rows(
        SPECTRAL_DIGEST_COLUMNS,
        rows["spectral_digest_rows"],
    )
    obs_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    schur_hash = hashlib.sha256(
        schur_fraction_text(rows["schur_rows"]).encode("ascii")
    ).hexdigest()
    edge_hash = hashlib.sha256(
        edge_fraction_text(rows["edge_rows"]).encode("ascii")
    ).hexdigest()
    resistance_hash = hashlib.sha256(
        resistance_fraction_text(rows["resistance_rows"]).encode("ascii")
    ).hexdigest()
    spectral_hash = hashlib.sha256(
        spectral_fraction_text(rows["spectral_rows"]).encode("ascii")
    ).hexdigest()
    schur_signature = [
        tuple(row[column] for column in SCHUR_DIGEST_COLUMNS)
        for row in rows["schur_digest_rows"]
    ]
    edge_signature = [
        tuple(row[column] for column in EDGE_DIGEST_COLUMNS)
        for row in rows["edge_digest_rows"]
    ]
    resistance_signature = [
        tuple(row[column] for column in RESISTANCE_DIGEST_COLUMNS)
        for row in rows["resistance_digest_rows"]
    ]
    spectral_signature = [
        tuple(row[column] for column in SPECTRAL_DIGEST_COLUMNS)
        for row in rows["spectral_digest_rows"]
    ]
    checks = {
        "input_certified": obs["long_absorb_input_certified"] == 1,
        "schur_operator_exact": (
            obs["boundary0_count"],
            obs["boundary1_count"],
            obs["boundary2_count"],
            obs["boundary_total_count"],
            obs["schur_rank_mod_1000000007"],
            obs["schur_rank_mod_1000000009"],
            obs["schur_row_sum_zero_flag"],
            obs["schur_symmetric_flag"],
            obs["schur_cofactor_equal_flag"],
            obs["schur_positive_edge_flag"],
        )
        == (1_342, 864, 2_378, 4_584, 2, 2, 1, 1, 1, 1),
        "schur_signature_exact": schur_signature
        == [
            (0, 0, 258, 255, 65_114_317, 75_025_110, 983_636_213, 814_085_260, 1),
            (0, 1, 256, 254, 310_812_724, 253_126_048, 518_584_879, 867_253_560, 0),
            (0, 2, 258, 255, 475_380_363, 75_025_110, 570_326_817, 814_085_260, 0),
            (1, 0, 256, 254, 310_812_724, 253_126_048, 518_584_879, 867_253_560, 0),
            (1, 1, 256, 254, 200_562_526, 253_126_048, 554_218_912, 867_253_560, 1),
            (1, 2, 256, 254, 488_624_757, 253_126_048, 927_196_227, 867_253_560, 0),
            (2, 0, 258, 255, 475_380_363, 75_025_110, 570_326_817, 814_085_260, 0),
            (2, 1, 256, 254, 488_624_757, 253_126_048, 927_196_227, 867_253_560, 0),
            (2, 2, 258, 255, 797_625_560, 75_025_110, 176_963_942, 814_085_260, 1),
        ],
        "edge_signature_exact": edge_signature
        == [
            (0, 0, 1, 256, 254, 689_187_283, 253_126_048, 481_415_130, 867_253_560),
            (1, 0, 2, 258, 255, 524_619_644, 75_025_110, 429_673_192, 814_085_260),
            (2, 1, 2, 256, 254, 511_375_250, 253_126_048, 72_803_782, 867_253_560),
        ],
        "resistance_signature_exact": resistance_signature
        == [
            (0, 0, 1, 258, 260, 797_625_560, 489_501_615, 176_963_942, 776_504_119),
            (1, 0, 2, 258, 260, 813_500_596, 489_501_615, 301_253_771, 776_504_119),
            (2, 1, 2, 258, 260, 65_114_317, 489_501_615, 983_636_213, 776_504_119),
        ],
        "spectral_signature_exact": spectral_signature
        == [
            (0, 258, 255, 338_120_233, 37_512_555, 730_926_963, 407_042_630),
            (1, 260, 255, 489_501_615, 75_025_110, 776_504_119, 814_085_260),
            (2, 260, 255, 489_501_615, 25_008_370, 776_504_119, 938_028_426),
            (3, 515, 510, 403_262_461, 772_777_688, 678_352_473, 146_163_591),
        ],
        "spectral_observables_exact": (
            obs["trace_num_digits"],
            obs["trace_den_digits"],
            obs["tree_num_digits"],
            obs["tree_den_digits"],
            obs["pseudodet_num_digits"],
            obs["pseudodet_den_digits"],
            obs["discriminant_num_digits"],
            obs["discriminant_den_digits"],
            obs["discriminant_positive_flag"],
            obs["discriminant_rational_square_flag"],
            obs["resistance_num_digit_min"],
            obs["resistance_num_digit_max"],
            obs["resistance_den_digit_min"],
            obs["resistance_den_digit_max"],
        )
        == (258, 255, 260, 255, 260, 255, 515, 510, 1, 0, 258, 258, 260, 260),
        "digest_hashes_exact": (
            schur_hash,
            edge_hash,
            resistance_hash,
            spectral_hash,
        )
        == (
            "0f9d997c3b976dce091a82ce44527c4c2b7df14629fe056c98427d570e27d07d",
            "323b2bcdda4e7771c1c910a2827c5d390adbec86c9e197f7ea937874ec6675cc",
            "c91a0b33dc5a2cd6d0ed32d870a2a642972f6dbad2f4c3b2609516563e103de4",
            "9033e3c8a751478502449e29710f132425cbf1aedf99ab3e065a8c7201197633",
        ),
        "table_shapes_match": (
            tuple(schur_digest_table.shape),
            tuple(edge_digest_table.shape),
            tuple(resistance_digest_table.shape),
            tuple(spectral_digest_table.shape),
            tuple(obs_table.shape),
        )
        == (
            (9, len(SCHUR_DIGEST_COLUMNS)),
            (3, len(EDGE_DIGEST_COLUMNS)),
            (3, len(RESISTANCE_DIGEST_COLUMNS)),
            (4, len(SPECTRAL_DIGEST_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "long_absorb_three_terminal_schur_spectrum",
        "scope": {
            "source": "long_absorb symmetric transfer matrix",
            "operator": "three-terminal Schur complement diag(boundary)-transfer",
            "boundary_totals": [
                obs["boundary0_count"],
                obs["boundary1_count"],
                obs["boundary2_count"],
            ],
        },
        "schur": {
            "rank_mod_1000000007": obs["schur_rank_mod_1000000007"],
            "rank_mod_1000000009": obs["schur_rank_mod_1000000009"],
            "row_sum_zero": bool(obs["schur_row_sum_zero_flag"]),
            "symmetric": bool(obs["schur_symmetric_flag"]),
            "cofactors_equal": bool(obs["schur_cofactor_equal_flag"]),
            "positive_edges": bool(obs["schur_positive_edge_flag"]),
            "schur_fraction_text_sha256": schur_hash,
            "edge_fraction_text_sha256": edge_hash,
            "schur_digest_table_sha256": sha_array(schur_digest_table),
            "edge_digest_table_sha256": sha_array(edge_digest_table),
        },
        "spectrum": {
            "charpoly": "lambda * (lambda^2 - trace*lambda + pseudodeterminant)",
            "trace": fraction_record(rows["spectral_values"][0]),
            "tree_cofactor": fraction_record(rows["spectral_values"][1]),
            "pseudodeterminant": fraction_record(rows["spectral_values"][2]),
            "discriminant": fraction_record(rows["spectral_values"][3]),
            "discriminant_rational_square": bool(
                obs["discriminant_rational_square_flag"]
            ),
            "spectral_fraction_text_sha256": spectral_hash,
            "spectral_digest_table_sha256": sha_array(spectral_digest_table),
        },
        "resistance": {
            "pair_count": obs["resistance_pair_count"],
            "resistance_fraction_text_sha256": resistance_hash,
            "resistance_digest_table_sha256": sha_array(resistance_digest_table),
        },
        "observable_table_sha256": sha_array(obs_table),
    }
    spec = {
        "schema": "long.spec@1",
        "object": "long_absorb_three_terminal_schur_spectrum",
        "status": STATUS if all(checks.values()) else "LONG_SPEC_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.spec.report@1",
        "status": spec["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_spec certifies the exact three-terminal Schur boundary "
            "operator induced by long_absorb: a symmetric rank-two Laplacian "
            "with zero row sums, equal tree cofactors, positive edge "
            "conductances, exact resistance fingerprints, and a quadratic "
            "nonzero spectral factor with nonsquare discriminant."
        ),
        "stage_protocol": {
            "draft": "read the long_absorb exact 3x3 transfer matrix",
            "witness": "form diag(boundary)-transfer and compute conductance, resistance, cofactor, and spectral fingerprints",
            "coherence": "check rank, row sums, symmetry, cofactors, signatures, and text hashes",
            "closure": "emit Schur, edge, resistance, spectral, table, certificate, manifest, and report artifacts",
            "emit": "write long_spec artifacts and verifier hook",
        },
        "inputs": {
            "long_absorb_report": input_entry(
                LONG_ABSORB_REPORT,
                {"status": rows["long_absorb"].get("status")},
            ),
            "long_absorb_matrix": input_entry(LONG_ABSORB_MATRIX),
            "long_absorb_tables": input_entry(LONG_ABSORB_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "spec": relpath(OUT_DIR / "spec.json"),
            "schur_csv": relpath(OUT_DIR / "schur.csv"),
            "edge_csv": relpath(OUT_DIR / "edge.csv"),
            "resistance_csv": relpath(OUT_DIR / "resistance.csv"),
            "spectral_csv": relpath(OUT_DIR / "spectral.csv"),
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
                "the exact reduced three-terminal Schur Laplacian from long_absorb",
                "rank-two zero-row-sum symmetric boundary conductance",
                "tree cofactor and pseudodeterminant fingerprints",
                "three exact boundary effective-resistance fingerprints",
            ],
            "does_not_certify_because_out_of_scope": [
                "a continuous spectral theorem beyond the finite three-terminal operator",
                "support-changing recouplings outside the long_rec owner graph",
                "all higher-order tensor repairs",
                "a universal eta6 horizon theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_markov: certify the reversible boundary Markov kernel "
            "D^{-1}T and its finite LLN mixing fingerprints from the same "
            "three-terminal transfer matrix."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.spec.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.spec.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "spec": spec,
        "schur_csv": csv_text(SCHUR_COLUMNS, rows["schur_rows"]),
        "edge_csv": csv_text(EDGE_COLUMNS, rows["edge_rows"]),
        "resistance_csv": csv_text(RESISTANCE_COLUMNS, rows["resistance_rows"]),
        "spectral_csv": csv_text(SPECTRAL_COLUMNS, rows["spectral_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "schur_digest_table": schur_digest_table,
        "edge_digest_table": edge_digest_table,
        "resistance_digest_table": resistance_digest_table,
        "spectral_digest_table": spectral_digest_table,
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
    write_json(OUT_DIR / "spec.json", payloads["spec"])
    (OUT_DIR / "schur.csv").write_text(payloads["schur_csv"], encoding="utf-8")
    (OUT_DIR / "edge.csv").write_text(payloads["edge_csv"], encoding="utf-8")
    (OUT_DIR / "resistance.csv").write_text(
        payloads["resistance_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "spectral.csv").write_text(
        payloads["spectral_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        schur_digest_table=payloads["schur_digest_table"],
        edge_digest_table=payloads["edge_digest_table"],
        resistance_digest_table=payloads["resistance_digest_table"],
        spectral_digest_table=payloads["spectral_digest_table"],
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
