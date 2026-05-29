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
    from .derive_long_prob import COMPONENT_WEIGHTS
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .derive_long_recind import (
        OUT_DIR as LONG_RECIND_DIR,
        STATUS as LONG_RECIND_STATUS,
        build_transition_rows,
        load_support_rows,
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
    from derive_long_prob import COMPONENT_WEIGHTS
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from derive_long_recind import (
        OUT_DIR as LONG_RECIND_DIR,
        STATUS as LONG_RECIND_STATUS,
        build_transition_rows,
        load_support_rows,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_formind"
STATUS = "LONG_FORMIND_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_RECIND_REPORT = LONG_RECIND_DIR / "report.json"
LONG_RECIND_TRANSITION = LONG_RECIND_DIR / "transition.csv"
LONG_RECIND_TYPE_SUMMARY = LONG_RECIND_DIR / "type_summary.csv"
LONG_RECIND_TABLES = LONG_RECIND_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_formind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_formind.py"

PROBE_START = 128
PROBE_END = 256
RECURRENCE_FACTOR = 12

CLASS_TEXT_HASH = "ca7820b210468d197ae2a79ba4c1e76b39671a23a627ee5d254665a68ecdb73c"
TERM_TEXT_HASH = "74e709d5feddf9b5143b9e6ecea16607f5de68879ac2dc1d35a19f331e562c75"
CHECK_TEXT_HASH = "e313884f013133defd4c5f39e94cf7c8ec989179804d81b7c5c288525264c59f"
BRIDGE_TEXT_HASH = "19f479e174ce7778699532ce76136c9928a3c93ce03004f0b8c6f299a9ef7659"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
BASE_A, BASE_B, BASE_C = COMPONENT_WEIGHTS

RULE_OFFSETS = {
    0: (0, 2),
    1: (1, 3),
    2: (2, 3),
    3: (2, 4),
    4: (3, 4),
    5: (3, 3),
    6: (2, 3),
    7: (2, 2),
}

CLASS_COLUMNS = [
    "class_id",
    "transition_type_code",
    "successor_side_mask",
    "predecessor_side_mask",
    "domain_code",
    "x_min_kind",
    "x_min_const",
    "x_max_kind",
    "x_max_const",
    "certified_transition_count",
    "probe_state_count",
]
TERM_COLUMNS = [
    "term_id",
    "class_id",
    "gap_kind",
    "coeff_num",
    "coeff_den",
    "exp12_n",
    "exp12_x",
    "exp12_const",
    "exp18_n",
    "exp18_x",
    "exp18_const",
    "exp48_n",
    "exp48_x",
    "exp48_const",
]
CHECK_COLUMNS = [
    "formula_id",
    "class_id",
    "gap_kind",
    "term_count",
    "certified_transition_count",
    "certified_match_count",
    "certified_integral_count",
    "certified_nonnegative_count",
    "probe_state_count",
    "probe_integral_count",
    "probe_nonnegative_count",
    "probe_zero_count",
    "probe_min_sign",
    "probe_min_digits",
    "probe_min_mod_1000000007",
    "probe_min_mod_1000000009",
    "formula_certificate_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "recurrence_factor",
    "probe_start_sample_count",
    "probe_end_sample_count",
    "transition_type_count",
    "formula_class_count",
    "formula_count",
    "term_count",
    "certified_transition_count",
    "certified_formula_match_count",
    "probe_state_count",
    "probe_formula_nonnegative_count",
    "long_recind_certified_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "probe_start_sample_count",
    "probe_end_sample_count",
    "transition_type_count",
    "formula_class_count",
    "formula_count",
    "term_count",
    "certified_transition_count",
    "certified_formula_eval_count",
    "certified_formula_match_count",
    "certified_formula_integral_count",
    "certified_formula_nonnegative_count",
    "probe_state_count",
    "probe_formula_eval_count",
    "probe_formula_integral_count",
    "probe_formula_nonnegative_count",
    "probe_formula_zero_count",
    "formula_class_split_count",
    "long_recind_certified_flag",
    "current_formula_match_flag",
    "current_probe_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

Affine = tuple[int, int, int]
Key = tuple[Affine, Affine, Affine]
Expr = dict[Key, Fraction]


def add_aff(left: Affine, right: Affine) -> Affine:
    return (left[0] + right[0], left[1] + right[1], left[2] + right[2])


def sub_aff(left: Affine, right: Affine) -> Affine:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def const(value: int) -> Affine:
    return (0, 0, value)


N: Affine = (1, 0, 0)
X: Affine = (0, 1, 0)


def term(
    coeff: Fraction,
    exp12: Affine = (0, 0, 0),
    exp18: Affine = (0, 0, 0),
    exp48: Affine = (0, 0, 0),
) -> Expr:
    return {(exp12, exp18, exp48): coeff}


def add_expr(left: Expr, right: Expr, scale: Fraction = Fraction(1)) -> Expr:
    out: dict[Key, Fraction] = defaultdict(Fraction)
    out.update(left)
    for key, value in right.items():
        out[key] += scale * value
    return {key: value for key, value in out.items() if value}


def mul_expr(left: Expr, right: Expr) -> Expr:
    out: dict[Key, Fraction] = defaultdict(Fraction)
    for left_key, left_coeff in left.items():
        for right_key, right_coeff in right.items():
            key = tuple(
                add_aff(left_key[index], right_key[index]) for index in range(3)
            )
            out[key] += left_coeff * right_coeff
    return {key: value for key, value in out.items() if value}


def scale_expr(expr: Expr, factor: int) -> Expr:
    return {key: value * factor for key, value in expr.items() if value * factor}


def prefix_left(sample_count: Affine, prefix_sum: Affine) -> Expr:
    return add_expr(
        term(
            Fraction(1, 6),
            exp12=sub_aff(sample_count, prefix_sum),
            exp18=add_aff(prefix_sum, const(1)),
        ),
        term(Fraction(-1, 6), exp12=add_aff(sample_count, const(1))),
    )


def prefix_right(sample_count: Affine, prefix_sum: Affine) -> Expr:
    offset = sub_aff(prefix_sum, sample_count)
    left_total = add_expr(
        term(Fraction(1, 6), exp18=add_aff(sample_count, const(1))),
        term(Fraction(-1, 6), exp12=add_aff(sample_count, const(1))),
    )
    tail = add_expr(
        term(
            Fraction(1, 30),
            exp18=sub_aff(sample_count, offset),
            exp48=add_aff(offset, const(1)),
        ),
        term(Fraction(-48, 30), exp18=sample_count),
    )
    return add_expr(left_total, tail)


def prefix_forced(sample_count: Affine, prefix_sum: Affine, side: int) -> Expr:
    if side == 0:
        return prefix_left(sample_count, prefix_sum)
    if side == 1:
        return prefix_right(sample_count, prefix_sum)
    raise AssertionError("invalid prefix side")


def total_weight(sample_count: Affine) -> Expr:
    return add_expr(
        add_expr(
            term(Fraction(1, 30), exp48=add_aff(sample_count, const(1))),
            term(Fraction(42, 30), exp18=sample_count),
        ),
        term(Fraction(-5, 30), exp12=add_aff(sample_count, const(1))),
    )


def gap_formula(
    sample_count: Affine,
    sum_value: Affine,
    rule_id: int,
    gap_kind: int,
    sides: tuple[int, int],
) -> Expr:
    dmin, dmax = RULE_OFFSETS[rule_id]
    target_sample = add_aff(sample_count, const(1))
    if gap_kind == 0:
        source_prefix = prefix_forced(
            sample_count,
            add_aff(sum_value, const(-1)),
            sides[0],
        )
        target_prefix = prefix_forced(
            target_sample,
            add_aff(sum_value, const(dmin - 1)),
            sides[1],
        )
        return add_expr(
            mul_expr(source_prefix, total_weight(target_sample)),
            mul_expr(target_prefix, total_weight(sample_count)),
            scale=Fraction(-1),
        )
    if gap_kind == 1:
        target_prefix = prefix_forced(
            target_sample,
            add_aff(sum_value, const(dmax)),
            sides[0],
        )
        source_prefix = prefix_forced(sample_count, sum_value, sides[1])
        return add_expr(
            mul_expr(target_prefix, total_weight(sample_count)),
            mul_expr(source_prefix, total_weight(target_sample)),
            scale=Fraction(-1),
        )
    raise AssertionError("invalid gap kind")


def state_affine(type_code: int, predecessor: bool) -> tuple[Affine, Affine, int]:
    if type_code == 0:
        return (add_aff(N, const(-1)) if predecessor else N, const(0), 0)
    if type_code == 9:
        return (add_aff(N, const(-1)) if predecessor else N, const(1), 1)
    if type_code == 18:
        return (add_aff(N, const(-1)) if predecessor else N, const(2), 2)
    if type_code == 27:
        return (add_aff(N, const(-1)) if predecessor else N, const(3), 3)
    if type_code == 36:
        return (add_aff(N, const(-1)) if predecessor else N, X, 4)
    if type_code == 44:
        if predecessor:
            return add_aff(N, const(-1)), add_aff(N, const(-2)), 5
        return N, add_aff(N, const(-2)), 4
    if type_code == 53:
        if predecessor:
            return add_aff(N, const(-1)), add_aff(N, const(-1)), 6
        return N, add_aff(N, const(-1)), 5
    if type_code == 54:
        if predecessor:
            return add_aff(N, const(-1)), add_aff(add_aff(N, const(-1)), X), 6
        return N, add_aff(N, X), 6
    if type_code == 62:
        if predecessor:
            return add_aff(N, const(-1)), add_aff((2, 0, 0), const(-2)), 7
        return N, add_aff((2, 0, 0), const(-1)), 6
    if type_code == 63:
        if predecessor:
            return add_aff(N, const(-1)), add_aff((2, 0, 0), const(-2)), 7
        return N, (2, 0, 0), 7
    raise AssertionError("unknown transition type")


def recurrence_formula(
    type_code: int,
    gap_kind: int,
    successor_sides: tuple[int, int, int, int],
    predecessor_sides: tuple[int, int, int, int],
) -> Expr:
    succ_n, succ_s, succ_rule = state_affine(type_code, predecessor=False)
    pred_n, pred_s, pred_rule = state_affine(type_code, predecessor=True)
    succ_gap_sides = successor_sides[:2] if gap_kind == 0 else successor_sides[2:]
    pred_gap_sides = predecessor_sides[:2] if gap_kind == 0 else predecessor_sides[2:]
    return add_expr(
        gap_formula(succ_n, succ_s, succ_rule, gap_kind, succ_gap_sides),
        scale_expr(gap_formula(pred_n, pred_s, pred_rule, gap_kind, pred_gap_sides), RECURRENCE_FACTOR),
        scale=Fraction(-1),
    )


def prefix_side(sample_count: int, prefix_sum: int) -> int:
    return int(prefix_sum > sample_count)


def side_signature(sample_count: int, sum_value: int, rule_id: int) -> tuple[int, int, int, int]:
    dmin, dmax = RULE_OFFSETS[rule_id]
    return (
        prefix_side(sample_count, sum_value - 1),
        prefix_side(sample_count + 1, sum_value + dmin - 1),
        prefix_side(sample_count + 1, sum_value + dmax),
        prefix_side(sample_count, sum_value),
    )


def side_mask(signature: tuple[int, int, int, int]) -> int:
    return sum(bit << index for index, bit in enumerate(signature))


def classify_transition_rows(
    support_rows: list[dict[str, int]],
    transition_rows: list[dict[str, int]],
) -> tuple[list[dict[str, int]], dict[int, list[dict[str, int]]], dict[int, tuple[int, tuple[int, int, int, int], tuple[int, int, int, int]]]]:
    support_by_key = {
        (row["sample_count"], row["sum_value"]): row for row in support_rows
    }
    grouped: dict[tuple[int, tuple[int, int, int, int], tuple[int, int, int, int]], list[dict[str, int]]] = defaultdict(list)
    for row in transition_rows:
        successor = support_by_key[(row["successor_sample_count"], row["successor_sum_value"])]
        predecessor = support_by_key[(row["predecessor_sample_count"], row["predecessor_sum_value"])]
        key = (
            row["transition_type_code"],
            side_signature(successor["sample_count"], successor["sum_value"], successor["rule_id"]),
            side_signature(predecessor["sample_count"], predecessor["sum_value"], predecessor["rule_id"]),
        )
        grouped[key].append(row)
    sorted_keys = sorted(grouped, key=lambda key: (key[0], key[1], key[2]))
    class_key_by_id = {class_id: key for class_id, key in enumerate(sorted_keys)}
    rows_by_class = {class_id: grouped[key] for class_id, key in class_key_by_id.items()}
    class_rows = []
    for class_id, key in class_key_by_id.items():
        type_code, successor_sides, predecessor_sides = key
        x_min_kind, x_min_const, x_max_kind, x_max_const = domain_bounds(type_code, successor_sides, predecessor_sides)
        probe_count = sum(
            max(0, (x_max_kind * n + x_max_const) - (x_min_kind * n + x_min_const) + 1)
            for n in range(PROBE_START, PROBE_END + 1)
        )
        class_rows.append(
            {
                "class_id": class_id,
                "transition_type_code": type_code,
                "successor_side_mask": side_mask(successor_sides),
                "predecessor_side_mask": side_mask(predecessor_sides),
                "domain_code": class_id,
                "x_min_kind": x_min_kind,
                "x_min_const": x_min_const,
                "x_max_kind": x_max_kind,
                "x_max_const": x_max_const,
                "certified_transition_count": len(rows_by_class[class_id]),
                "probe_state_count": probe_count,
            }
        )
    return class_rows, rows_by_class, class_key_by_id


def domain_bounds(
    type_code: int,
    successor_sides: tuple[int, int, int, int],
    predecessor_sides: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    if type_code == 36 and predecessor_sides == (0, 0, 0, 0):
        return 0, 4, 1, -4
    if type_code == 36:
        return 1, -3, 1, -3
    if type_code == 54 and successor_sides == (0, 0, 1, 0):
        return 0, 0, 0, 0
    if type_code == 54 and successor_sides == (0, 1, 1, 1):
        return 0, 1, 0, 1
    if type_code == 54:
        return 0, 2, 1, -2
    return 0, 0, 0, 0


def x_value(row: dict[str, int]) -> int:
    type_code = row["transition_type_code"]
    if type_code == 36:
        return row["successor_sum_value"]
    if type_code == 54:
        return row["successor_sum_value"] - row["successor_sample_count"]
    return 0


def evaluate_expr(expr: Expr, n_value: int, x_input: int) -> Fraction:
    total = Fraction(0)
    for key, coeff in expr.items():
        exponents = [
            affine[0] * n_value + affine[1] * x_input + affine[2]
            for affine in key
        ]
        if min(exponents) < 0:
            raise AssertionError("negative exponent in formula domain")
        total += (
            coeff
            * (BASE_A ** exponents[0])
            * (BASE_B ** exponents[1])
            * (BASE_C ** exponents[2])
        )
    return total


def sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def digits(value: int) -> int:
    return len(str(abs(value)))


def term_rows(
    class_key_by_id: dict[int, tuple[int, tuple[int, int, int, int], tuple[int, int, int, int]]]
) -> tuple[list[dict[str, int]], dict[tuple[int, int], Expr]]:
    rows: list[dict[str, int]] = []
    expressions: dict[tuple[int, int], Expr] = {}
    term_id = 0
    for class_id in sorted(class_key_by_id):
        type_code, successor_sides, predecessor_sides = class_key_by_id[class_id]
        for gap_kind in (0, 1):
            expr = recurrence_formula(
                type_code,
                gap_kind,
                successor_sides,
                predecessor_sides,
            )
            expressions[(class_id, gap_kind)] = expr
            for key, coeff in sorted(expr.items(), key=lambda item: str(item[0])):
                rows.append(
                    {
                        "term_id": term_id,
                        "class_id": class_id,
                        "gap_kind": gap_kind,
                        "coeff_num": coeff.numerator,
                        "coeff_den": coeff.denominator,
                        "exp12_n": key[0][0],
                        "exp12_x": key[0][1],
                        "exp12_const": key[0][2],
                        "exp18_n": key[1][0],
                        "exp18_x": key[1][1],
                        "exp18_const": key[1][2],
                        "exp48_n": key[2][0],
                        "exp48_x": key[2][1],
                        "exp48_const": key[2][2],
                    }
                )
                term_id += 1
    return rows, expressions


def check_rows(
    class_rows: list[dict[str, int]],
    rows_by_class: dict[int, list[dict[str, int]]],
    expressions: dict[tuple[int, int], Expr],
) -> list[dict[str, int]]:
    out = []
    formula_id = 0
    for class_row in class_rows:
        class_id = class_row["class_id"]
        rows = rows_by_class[class_id]
        for gap_kind in (0, 1):
            expr = expressions[(class_id, gap_kind)]
            match_count = 0
            integral_count = 0
            nonnegative_count = 0
            for row in rows:
                value = evaluate_expr(
                    expr,
                    row["successor_sample_count"],
                    x_value(row),
                )
                integral_count += int(value.denominator == 1)
                if value.denominator != 1:
                    continue
                actual = (
                    row["_lower_delta_value"]
                    if gap_kind == 0
                    else row["_upper_delta_value"]
                )
                match_count += int(value.numerator == actual)
                nonnegative_count += int(value.numerator >= 0)
            probe_values = []
            x_min_kind = class_row["x_min_kind"]
            x_max_kind = class_row["x_max_kind"]
            for sample_count in range(PROBE_START, PROBE_END + 1):
                x_min = x_min_kind * sample_count + class_row["x_min_const"]
                x_max = x_max_kind * sample_count + class_row["x_max_const"]
                for x_input in range(x_min, x_max + 1):
                    probe_values.append(evaluate_expr(expr, sample_count, x_input))
            probe_integral = sum(int(value.denominator == 1) for value in probe_values)
            probe_int_values = [
                value.numerator for value in probe_values if value.denominator == 1
            ]
            probe_nonnegative = sum(int(value >= 0) for value in probe_int_values)
            probe_zero = sum(int(value == 0) for value in probe_int_values)
            probe_min = min(probe_int_values) if probe_int_values else 0
            out.append(
                {
                    "formula_id": formula_id,
                    "class_id": class_id,
                    "gap_kind": gap_kind,
                    "term_count": len(expr),
                    "certified_transition_count": len(rows),
                    "certified_match_count": match_count,
                    "certified_integral_count": integral_count,
                    "certified_nonnegative_count": nonnegative_count,
                    "probe_state_count": len(probe_values),
                    "probe_integral_count": probe_integral,
                    "probe_nonnegative_count": probe_nonnegative,
                    "probe_zero_count": probe_zero,
                    "probe_min_sign": sign(probe_min),
                    "probe_min_digits": digits(probe_min),
                    "probe_min_mod_1000000007": probe_min % MOD_PRIMES[0],
                    "probe_min_mod_1000000009": probe_min % MOD_PRIMES[1],
                    "formula_certificate_flag": int(
                        match_count == len(rows)
                        and integral_count == len(rows)
                        and nonnegative_count == len(rows)
                        and probe_integral == len(probe_values)
                        and probe_nonnegative == len(probe_values)
                    ),
                }
            )
            formula_id += 1
    return out


def build_rows() -> dict[str, Any]:
    long_recind = load_json(LONG_RECIND_REPORT)
    support_rows = load_support_rows()
    transition_rows = build_transition_rows(support_rows)
    class_rows, rows_by_class, class_key_by_id = classify_transition_rows(
        support_rows,
        transition_rows,
    )
    terms, expressions = term_rows(class_key_by_id)
    checks = check_rows(class_rows, rows_by_class, expressions)
    bridge_rows = [
        {
            "bridge_id": 0,
            "recurrence_factor": RECURRENCE_FACTOR,
            "probe_start_sample_count": PROBE_START,
            "probe_end_sample_count": PROBE_END,
            "transition_type_count": len(
                {row["transition_type_code"] for row in transition_rows}
            ),
            "formula_class_count": len(class_rows),
            "formula_count": len(checks),
            "term_count": len(terms),
            "certified_transition_count": len(transition_rows),
            "certified_formula_match_count": sum(
                row["certified_match_count"] for row in checks
            ),
            "probe_state_count": sum(row["probe_state_count"] for row in checks) // 2,
            "probe_formula_nonnegative_count": sum(
                row["probe_nonnegative_count"] for row in checks
            ),
            "long_recind_certified_flag": int(
                long_recind.get("status") == LONG_RECIND_STATUS
            ),
        }
    ]
    obs = {
        "probe_start_sample_count": PROBE_START,
        "probe_end_sample_count": PROBE_END,
        "transition_type_count": bridge_rows[0]["transition_type_count"],
        "formula_class_count": len(class_rows),
        "formula_count": len(checks),
        "term_count": len(terms),
        "certified_transition_count": len(transition_rows),
        "certified_formula_eval_count": sum(
            row["certified_transition_count"] for row in checks
        ),
        "certified_formula_match_count": bridge_rows[0][
            "certified_formula_match_count"
        ],
        "certified_formula_integral_count": sum(
            row["certified_integral_count"] for row in checks
        ),
        "certified_formula_nonnegative_count": sum(
            row["certified_nonnegative_count"] for row in checks
        ),
        "probe_state_count": bridge_rows[0]["probe_state_count"],
        "probe_formula_eval_count": sum(row["probe_state_count"] for row in checks),
        "probe_formula_integral_count": sum(
            row["probe_integral_count"] for row in checks
        ),
        "probe_formula_nonnegative_count": bridge_rows[0][
            "probe_formula_nonnegative_count"
        ],
        "probe_formula_zero_count": sum(row["probe_zero_count"] for row in checks),
        "formula_class_split_count": len(class_rows)
        - bridge_rows[0]["transition_type_count"],
        "long_recind_certified_flag": bridge_rows[0]["long_recind_certified_flag"],
        "current_formula_match_flag": int(
            sum(row["formula_certificate_flag"] for row in checks) == len(checks)
        ),
        "current_probe_flag": int(
            sum(row["probe_nonnegative_count"] for row in checks)
            == sum(row["probe_state_count"] for row in checks)
        ),
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    class_hash = hashlib.sha256(
        digest_text(CLASS_COLUMNS, class_rows).encode("ascii")
    ).hexdigest()
    term_hash = hashlib.sha256(
        digest_text(TERM_COLUMNS, terms).encode("ascii")
    ).hexdigest()
    check_hash = hashlib.sha256(
        digest_text(CHECK_COLUMNS, checks).encode("ascii")
    ).hexdigest()
    bridge_hash = hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, bridge_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": {"long_recind": long_recind},
        "class_rows": class_rows,
        "term_rows": terms,
        "check_rows": checks,
        "bridge_rows": bridge_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "class_table": table_from_rows(CLASS_COLUMNS, class_rows),
        "term_table": table_from_rows(TERM_COLUMNS, terms),
        "check_table": table_from_rows(CHECK_COLUMNS, checks),
        "bridge_table": table_from_rows(BRIDGE_COLUMNS, bridge_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "class_hash": class_hash,
        "term_hash": term_hash,
        "check_hash": check_hash,
        "bridge_hash": bridge_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": obs["long_recind_certified_flag"] == 1,
        "formula_surface_exact": (
            obs["transition_type_count"],
            obs["formula_class_count"],
            obs["formula_count"],
            obs["term_count"],
            obs["formula_class_split_count"],
            rows["class_hash"],
            rows["term_hash"],
        )
        == (10, 13, 26, 581, 3, CLASS_TEXT_HASH, TERM_TEXT_HASH),
        "certified_match_exact": (
            obs["certified_transition_count"],
            obs["certified_formula_eval_count"],
            obs["certified_formula_match_count"],
            obs["certified_formula_integral_count"],
            obs["certified_formula_nonnegative_count"],
            rows["check_hash"],
        )
        == (16_095, 32_190, 32_190, 32_190, 32_190, CHECK_TEXT_HASH),
        "probe_exact": (
            obs["probe_start_sample_count"],
            obs["probe_end_sample_count"],
            obs["probe_state_count"],
            obs["probe_formula_eval_count"],
            obs["probe_formula_integral_count"],
            obs["probe_formula_nonnegative_count"],
            rows["bridge_hash"],
        )
        == (
            128,
            256,
            49_665,
            99_330,
            99_330,
            99_330,
            BRIDGE_TEXT_HASH,
        ),
        "current_representation_exact": (
            obs["current_formula_match_flag"],
            obs["current_probe_flag"],
        )
        == (1, 1),
        "table_shapes_match": (
            tuple(rows["class_table"].shape),
            tuple(rows["term_table"].shape),
            tuple(rows["check_table"].shape),
            tuple(rows["bridge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (13, len(CLASS_COLUMNS)),
            (581, len(TERM_COLUMNS)),
            (26, len(CHECK_COLUMNS)),
            (1, len(BRIDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "affine_exponent_recurrence_formula_certificate",
        "formula_surface": {
            "transition_type_count": obs["transition_type_count"],
            "formula_class_count": obs["formula_class_count"],
            "formula_count": obs["formula_count"],
            "term_count": obs["term_count"],
            "formula_class_split_count": obs["formula_class_split_count"],
            "class_text_sha256": rows["class_hash"],
            "term_text_sha256": rows["term_hash"],
            "class_table_sha256": sha_array(rows["class_table"]),
            "term_table_sha256": sha_array(rows["term_table"]),
        },
        "certified_match": {
            "transition_count": obs["certified_transition_count"],
            "formula_eval_count": obs["certified_formula_eval_count"],
            "formula_match_count": obs["certified_formula_match_count"],
            "formula_nonnegative_count": obs["certified_formula_nonnegative_count"],
            "check_text_sha256": rows["check_hash"],
            "check_table_sha256": sha_array(rows["check_table"]),
        },
        "probe": {
            "start_sample_count": PROBE_START,
            "end_sample_count": PROBE_END,
            "state_count": obs["probe_state_count"],
            "formula_eval_count": obs["probe_formula_eval_count"],
            "formula_nonnegative_count": obs["probe_formula_nonnegative_count"],
            "probe_zero_count": obs["probe_formula_zero_count"],
            "bridge_text_sha256": rows["bridge_hash"],
            "bridge_table_sha256": sha_array(rows["bridge_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    formind_payload = {
        "schema": "long.formind@1",
        "object": "affine_exponent_recurrence_formula_certificate",
        "status": STATUS if all(checks.values()) else "LONG_FORMIND_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.formind.report@1",
        "status": formind_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_formind extracts closed affine-exponent formulas for the "
            "long_recind recurrence deltas. The 10 recurrence transition types "
            "split into 13 formula classes because boundary states use different "
            "left/right cumulative-prefix branches. The formulas exactly match "
            "all certified recurrence deltas and remain nonnegative on the "
            "explicit probe range n=128..256."
        ),
        "stage_protocol": {
            "draft": "read long_recind recurrence transitions and support-gap formulas",
            "witness": "derive affine-exponent formula classes from cumulative-prefix branch signatures",
            "coherence": "check formula matches, integrality, probe signs, input status, hashes, and shapes",
            "closure": "emit formula-class certificate and keep the global dominance boundary explicit",
            "emit": "write long_formind artifacts and verifier hook",
        },
        "inputs": {
            "long_recind_report": input_entry(
                LONG_RECIND_REPORT,
                {"status": rows["input_reports"]["long_recind"].get("status")},
            ),
            "long_recind_transition": input_entry(LONG_RECIND_TRANSITION),
            "long_recind_type_summary": input_entry(LONG_RECIND_TYPE_SUMMARY),
            "long_recind_tables": input_entry(LONG_RECIND_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "formind": relpath(OUT_DIR / "formind.json"),
            "class_csv": relpath(OUT_DIR / "class.csv"),
            "term_csv": relpath(OUT_DIR / "term.csv"),
            "check_csv": relpath(OUT_DIR / "check.csv"),
            "bridge_csv": relpath(OUT_DIR / "bridge.csv"),
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
                "closed affine-exponent formulas for every long_recind recurrence delta class",
                "exact formula agreement with all 32,190 certified lower/upper recurrence deltas",
                "the 13-class branch split refining the 10 recurrence transition types",
                "nonnegative formula evaluations on the explicit extension probe n=128..256",
            ],
            "does_not_certify_because_out_of_scope": [
                "global symbolic dominance of mixed-sign formula terms for every n >= 257",
                "the full component-word measure",
                "semantic associator composition",
                "a complete infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_domind: prove dominance/positivity of the 13 mixed-sign "
            "formula classes for all remaining n, replacing the finite probe."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.formind.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.formind.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "formind": formind_payload,
        "class_csv": csv_text(CLASS_COLUMNS, rows["class_rows"]),
        "term_csv": csv_text(TERM_COLUMNS, rows["term_rows"]),
        "check_csv": csv_text(CHECK_COLUMNS, rows["check_rows"]),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "class_table": rows["class_table"],
        "term_table": rows["term_table"],
        "check_table": rows["check_table"],
        "bridge_table": rows["bridge_table"],
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
    write_json(OUT_DIR / "formind.json", payloads["formind"])
    (OUT_DIR / "class.csv").write_text(payloads["class_csv"], encoding="utf-8")
    (OUT_DIR / "term.csv").write_text(payloads["term_csv"], encoding="utf-8")
    (OUT_DIR / "check.csv").write_text(payloads["check_csv"], encoding="utf-8")
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        class_table=payloads["class_table"],
        term_table=payloads["term_table"],
        check_table=payloads["check_table"],
        bridge_table=payloads["bridge_table"],
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
