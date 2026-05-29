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
    from .derive_long_formind import (
        BRIDGE_COLUMNS as LONG_FORMIND_BRIDGE_COLUMNS,
        CHECK_COLUMNS as LONG_FORMIND_CHECK_COLUMNS,
        CLASS_COLUMNS as LONG_FORMIND_CLASS_COLUMNS,
        OUT_DIR as LONG_FORMIND_DIR,
        STATUS as LONG_FORMIND_STATUS,
        TERM_COLUMNS as LONG_FORMIND_TERM_COLUMNS,
        build_transition_rows,
        classify_transition_rows,
        load_support_rows,
        term_rows,
    )
    from .derive_long_raw import csv_text, digest_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_formind import (
        BRIDGE_COLUMNS as LONG_FORMIND_BRIDGE_COLUMNS,
        CHECK_COLUMNS as LONG_FORMIND_CHECK_COLUMNS,
        CLASS_COLUMNS as LONG_FORMIND_CLASS_COLUMNS,
        OUT_DIR as LONG_FORMIND_DIR,
        STATUS as LONG_FORMIND_STATUS,
        TERM_COLUMNS as LONG_FORMIND_TERM_COLUMNS,
        build_transition_rows,
        classify_transition_rows,
        load_support_rows,
        term_rows,
    )
    from derive_long_raw import csv_text, digest_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_domind"
STATUS = "LONG_DOMIND_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_FORMIND_REPORT = LONG_FORMIND_DIR / "report.json"
LONG_FORMIND_CLASS = LONG_FORMIND_DIR / "class.csv"
LONG_FORMIND_TERM = LONG_FORMIND_DIR / "term.csv"
LONG_FORMIND_CHECK = LONG_FORMIND_DIR / "check.csv"
LONG_FORMIND_BRIDGE = LONG_FORMIND_DIR / "bridge.csv"
LONG_FORMIND_TABLES = LONG_FORMIND_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_domind.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_domind.py"

TAIL_START = 257
FORMIND_PROBE_END = 256
MOD_PRIMES = (1_000_000_007, 1_000_000_009)

FORMULA_TEXT_HASH = "9109f222e514b569df1dfd58ff40eca487c43f5a65e5e7a6d6dd16df6c5c51b4"
COVER_TEXT_HASH = "c2297ed50fcdb17a80d9c8f246440bb51248f5740b508bf13b4c6cb732c65da6"
BRIDGE_TEXT_HASH = "a63d23f58d45b84d193f947475b7d27085e1ba0695935c673c2d3ca983dc8dfe"

FORMULA_COLUMNS = [
    "formula_id",
    "class_id",
    "gap_kind",
    "positive_term_count",
    "negative_term_count",
    "assignment_count",
    "covered_negative_count",
    "saturated_positive_count",
    "capacity_over_count",
    "ray_violation_count",
    "unassigned_negative_count",
    "max_capacity_num_digits",
    "max_capacity_den_digits",
    "max_capacity_num_mod_1000000007",
    "max_capacity_den_mod_1000000007",
    "max_capacity_num_mod_1000000009",
    "max_capacity_den_mod_1000000009",
    "tail_nonnegative_flag",
]
COVER_COLUMNS = [
    "assignment_id",
    "formula_id",
    "class_id",
    "gap_kind",
    "negative_local_index",
    "positive_local_index",
    "negative_term_id",
    "positive_term_id",
    "share_num_digits",
    "share_num_mod_1000000007",
    "share_num_mod_1000000009",
    "share_den_digits",
    "share_den_mod_1000000007",
    "share_den_mod_1000000009",
    "cost_num_digits",
    "cost_num_mod_1000000007",
    "cost_num_mod_1000000009",
    "cost_den_digits",
    "cost_den_mod_1000000007",
    "cost_den_mod_1000000009",
    "consumption_num_digits",
    "consumption_num_mod_1000000007",
    "consumption_num_mod_1000000009",
    "consumption_den_digits",
    "consumption_den_mod_1000000007",
    "consumption_den_mod_1000000009",
    "lower_ray_le_one_flag",
    "upper_ray_le_one_flag",
    "endpoint_code",
    "assignment_certificate_flag",
]
BRIDGE_COLUMNS = [
    "bridge_id",
    "tail_start_sample_count",
    "formind_probe_end_sample_count",
    "formula_count",
    "positive_term_count",
    "negative_term_count",
    "cover_assignment_count",
    "covered_negative_term_count",
    "formula_tail_nonnegative_count",
    "lower_ray_certificate_count",
    "upper_ray_certificate_count",
    "long_formind_certified_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "tail_start_sample_count",
    "formind_probe_end_sample_count",
    "formula_count",
    "positive_term_count",
    "negative_term_count",
    "cover_assignment_count",
    "covered_negative_term_count",
    "formula_tail_nonnegative_count",
    "lower_ray_certificate_count",
    "upper_ray_certificate_count",
    "long_formind_certified_flag",
    "current_dominance_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}

Affine = tuple[int, int, int]
Key = tuple[Affine, Affine, Affine]
FormulaKey = tuple[int, int]


def digits(value: int) -> int:
    return len(str(abs(value)))


def int_mod(value: int, prime: int) -> int:
    return int(value % prime)


def fraction_stats(prefix: str, value: Fraction) -> dict[str, int]:
    return {
        f"{prefix}_num_digits": digits(value.numerator),
        f"{prefix}_num_mod_1000000007": int_mod(value.numerator, MOD_PRIMES[0]),
        f"{prefix}_num_mod_1000000009": int_mod(value.numerator, MOD_PRIMES[1]),
        f"{prefix}_den_digits": digits(value.denominator),
        f"{prefix}_den_mod_1000000007": int_mod(value.denominator, MOD_PRIMES[0]),
        f"{prefix}_den_mod_1000000009": int_mod(value.denominator, MOD_PRIMES[1]),
    }


def basis_affine(key: Key) -> tuple[Affine, Affine]:
    exp12, exp18, exp48 = key
    exp2 = (
        2 * exp12[0] + exp18[0] + 4 * exp48[0],
        2 * exp12[1] + exp18[1] + 4 * exp48[1],
        2 * exp12[2] + exp18[2] + 4 * exp48[2],
    )
    exp3 = (
        exp12[0] + 2 * exp18[0] + exp48[0],
        exp12[1] + 2 * exp18[1] + exp48[1],
        exp12[2] + 2 * exp18[2] + exp48[2],
    )
    return exp2, exp3


def eval_affine(affine: Affine, sample_count: int, x_value: int) -> int:
    return affine[0] * sample_count + affine[1] * x_value + affine[2]


def pow23_le_one(exp2: int, exp3: int) -> bool:
    if exp2 >= 0 and exp3 >= 0:
        return exp2 == 0 and exp3 == 0
    if exp2 <= 0 and exp3 <= 0:
        return True
    if exp2 > 0:
        return 2**exp2 <= 3 ** (-exp3)
    return 3**exp3 <= 2 ** (-exp2)


def pow23_fraction(exp2: int, exp3: int) -> Fraction:
    numerator = 1
    denominator = 1
    if exp2 >= 0:
        numerator *= 2**exp2
    else:
        denominator *= 2 ** (-exp2)
    if exp3 >= 0:
        numerator *= 3**exp3
    else:
        denominator *= 3 ** (-exp3)
    return Fraction(numerator, denominator)


def ratio_certificate(
    negative_key: Key,
    positive_key: Key,
    class_row: dict[str, int],
) -> tuple[Fraction, int, int, int] | None:
    negative2, negative3 = basis_affine(negative_key)
    positive2, positive3 = basis_affine(positive_key)
    delta2 = tuple(negative2[index] - positive2[index] for index in range(3))
    delta3 = tuple(negative3[index] - positive3[index] for index in range(3))

    lower_slope = class_row["x_min_kind"]
    upper_slope = class_row["x_max_kind"]
    lower_flag = int(
        pow23_le_one(
            delta2[0] + lower_slope * delta2[1],
            delta3[0] + lower_slope * delta3[1],
        )
    )
    upper_flag = int(
        pow23_le_one(
            delta2[0] + upper_slope * delta2[1],
            delta3[0] + upper_slope * delta3[1],
        )
    )
    if not lower_flag or not upper_flag:
        return None

    lower_x = lower_slope * TAIL_START + class_row["x_min_const"]
    upper_x = upper_slope * TAIL_START + class_row["x_max_const"]
    lower_bound = pow23_fraction(
        eval_affine(delta2, TAIL_START, lower_x),
        eval_affine(delta3, TAIL_START, lower_x),
    )
    upper_bound = pow23_fraction(
        eval_affine(delta2, TAIL_START, upper_x),
        eval_affine(delta3, TAIL_START, upper_x),
    )
    if lower_bound > upper_bound:
        return lower_bound, lower_flag, upper_flag, 0
    if upper_bound > lower_bound:
        return upper_bound, lower_flag, upper_flag, 1
    return lower_bound, lower_flag, upper_flag, 2


def formula_items(
    expressions: dict[FormulaKey, dict[Key, Fraction]],
    term_rows_payload: list[dict[str, int]],
) -> dict[FormulaKey, list[tuple[int, Key, Fraction]]]:
    by_formula: dict[FormulaKey, list[tuple[int, Key, Fraction]]] = defaultdict(list)
    term_id = 0
    for class_id in sorted({class_id for class_id, _ in expressions}):
        for gap_kind in (0, 1):
            for key, coeff in sorted(
                expressions[(class_id, gap_kind)].items(),
                key=lambda item: str(item[0]),
            ):
                recorded = term_rows_payload[term_id]
                if (
                    recorded["class_id"],
                    recorded["gap_kind"],
                    recorded["term_id"],
                ) != (class_id, gap_kind, term_id):
                    raise AssertionError("long_formind term order mismatch")
                by_formula[(class_id, gap_kind)].append((term_id, key, coeff))
                term_id += 1
    if term_id != len(term_rows_payload):
        raise AssertionError("long_formind term count mismatch")
    return by_formula


def greedy_cover(
    formula_id: int,
    class_row: dict[str, int],
    class_id: int,
    gap_kind: int,
    items: list[tuple[int, Key, Fraction]],
    assignment_start: int,
) -> tuple[dict[str, int], list[dict[str, int]]]:
    positives = [
        (index, term_id, key, coeff)
        for index, (term_id, key, coeff) in enumerate(items)
        if coeff > 0
    ]
    negatives = [
        (index, term_id, key, coeff)
        for index, (term_id, key, coeff) in enumerate(items)
        if coeff < 0
    ]
    capacities = {index: Fraction(1) for index, _, _, _ in positives}
    edges: dict[int, list[tuple[Fraction, int, int, int, int]]] = {}
    for neg_index, _, neg_key, neg_coeff in negatives:
        costs = []
        for pos_index, _, pos_key, pos_coeff in positives:
            certificate = ratio_certificate(neg_key, pos_key, class_row)
            if certificate is None:
                continue
            ratio_bound, lower_flag, upper_flag, endpoint_code = certificate
            cost = abs(neg_coeff) * ratio_bound / pos_coeff
            costs.append((cost, pos_index, lower_flag, upper_flag, endpoint_code))
        edges[neg_index] = sorted(costs, key=lambda row: (row[0], row[1]))

    order = sorted(
        negatives,
        key=lambda row: (
            len(edges[row[0]]),
            edges[row[0]][0][0] if edges[row[0]] else Fraction(10**9),
            row[0],
        ),
    )
    assignments = []
    share_by_negative: dict[int, Fraction] = defaultdict(Fraction)
    consumption_by_positive: dict[int, Fraction] = defaultdict(Fraction)
    assignment_id = assignment_start
    for neg_index, neg_term_id, _, _ in order:
        remaining = Fraction(1)
        for cost, pos_index, lower_flag, upper_flag, endpoint_code in edges[neg_index]:
            if remaining <= 0:
                break
            if cost <= 0:
                take = remaining
            else:
                take = min(remaining, capacities[pos_index] / cost)
            if take <= 0:
                continue
            consumption = take * cost
            capacities[pos_index] -= consumption
            share_by_negative[neg_index] += take
            consumption_by_positive[pos_index] += consumption
            remaining -= take
            pos_term_id = next(
                term_id
                for local_index, term_id, _, _ in positives
                if local_index == pos_index
            )
            row = {
                "assignment_id": assignment_id,
                "formula_id": formula_id,
                "class_id": class_id,
                "gap_kind": gap_kind,
                "negative_local_index": neg_index,
                "positive_local_index": pos_index,
                "negative_term_id": neg_term_id,
                "positive_term_id": pos_term_id,
                **fraction_stats("share", take),
                **fraction_stats("cost", cost),
                **fraction_stats("consumption", consumption),
                "lower_ray_le_one_flag": lower_flag,
                "upper_ray_le_one_flag": upper_flag,
                "endpoint_code": endpoint_code,
                "assignment_certificate_flag": int(
                    lower_flag
                    and upper_flag
                    and take > 0
                    and cost > 0
                    and consumption <= 1
                ),
            }
            assignments.append(row)
            assignment_id += 1
    covered_negative_count = sum(
        int(share_by_negative[index] == 1) for index, _, _, _ in negatives
    )
    unassigned_negative_count = len(negatives) - covered_negative_count
    capacity_over_count = sum(
        int(consumption_by_positive[index] > 1) for index, _, _, _ in positives
    )
    saturated_positive_count = sum(
        int(consumption_by_positive[index] == 1) for index, _, _, _ in positives
    )
    max_capacity = (
        max(consumption_by_positive.values())
        if consumption_by_positive
        else Fraction(0)
    )
    ray_violation_count = sum(
        int(
            row["lower_ray_le_one_flag"] != 1
            or row["upper_ray_le_one_flag"] != 1
            or row["assignment_certificate_flag"] != 1
        )
        for row in assignments
    )
    formula_row = {
        "formula_id": formula_id,
        "class_id": class_id,
        "gap_kind": gap_kind,
        "positive_term_count": len(positives),
        "negative_term_count": len(negatives),
        "assignment_count": len(assignments),
        "covered_negative_count": covered_negative_count,
        "saturated_positive_count": saturated_positive_count,
        "capacity_over_count": capacity_over_count,
        "ray_violation_count": ray_violation_count,
        "unassigned_negative_count": unassigned_negative_count,
        **fraction_stats("max_capacity", max_capacity),
        "tail_nonnegative_flag": int(
            covered_negative_count == len(negatives)
            and capacity_over_count == 0
            and ray_violation_count == 0
        ),
    }
    return formula_row, assignments


def build_rows() -> dict[str, Any]:
    long_formind = load_json(LONG_FORMIND_REPORT)
    support_rows = load_support_rows()
    transition_rows = build_transition_rows(support_rows)
    class_rows, _, class_key_by_id = classify_transition_rows(
        support_rows,
        transition_rows,
    )
    term_row_payload, expressions = term_rows(class_key_by_id)
    items_by_formula = formula_items(expressions, term_row_payload)

    formula_rows = []
    cover_rows = []
    assignment_start = 0
    formula_id = 0
    for class_row in class_rows:
        class_id = class_row["class_id"]
        for gap_kind in (0, 1):
            formula_row, assignments = greedy_cover(
                formula_id,
                class_row,
                class_id,
                gap_kind,
                items_by_formula[(class_id, gap_kind)],
                assignment_start,
            )
            formula_rows.append(formula_row)
            cover_rows.extend(assignments)
            assignment_start += len(assignments)
            formula_id += 1

    bridge_rows = [
        {
            "bridge_id": 0,
            "tail_start_sample_count": TAIL_START,
            "formind_probe_end_sample_count": FORMIND_PROBE_END,
            "formula_count": len(formula_rows),
            "positive_term_count": sum(row["positive_term_count"] for row in formula_rows),
            "negative_term_count": sum(row["negative_term_count"] for row in formula_rows),
            "cover_assignment_count": len(cover_rows),
            "covered_negative_term_count": sum(
                row["covered_negative_count"] for row in formula_rows
            ),
            "formula_tail_nonnegative_count": sum(
                row["tail_nonnegative_flag"] for row in formula_rows
            ),
            "lower_ray_certificate_count": sum(
                row["lower_ray_le_one_flag"] for row in cover_rows
            ),
            "upper_ray_certificate_count": sum(
                row["upper_ray_le_one_flag"] for row in cover_rows
            ),
            "long_formind_certified_flag": int(
                long_formind.get("status") == LONG_FORMIND_STATUS
            ),
        }
    ]
    obs = {
        "tail_start_sample_count": TAIL_START,
        "formind_probe_end_sample_count": FORMIND_PROBE_END,
        "formula_count": len(formula_rows),
        "positive_term_count": bridge_rows[0]["positive_term_count"],
        "negative_term_count": bridge_rows[0]["negative_term_count"],
        "cover_assignment_count": len(cover_rows),
        "covered_negative_term_count": bridge_rows[0]["covered_negative_term_count"],
        "formula_tail_nonnegative_count": bridge_rows[0][
            "formula_tail_nonnegative_count"
        ],
        "lower_ray_certificate_count": bridge_rows[0]["lower_ray_certificate_count"],
        "upper_ray_certificate_count": bridge_rows[0]["upper_ray_certificate_count"],
        "long_formind_certified_flag": bridge_rows[0][
            "long_formind_certified_flag"
        ],
        "current_dominance_flag": int(
            bridge_rows[0]["formula_tail_nonnegative_count"] == len(formula_rows)
            and bridge_rows[0]["covered_negative_term_count"]
            == bridge_rows[0]["negative_term_count"]
            and bridge_rows[0]["lower_ray_certificate_count"] == len(cover_rows)
            and bridge_rows[0]["upper_ray_certificate_count"] == len(cover_rows)
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
    formula_hash = hashlib.sha256(
        digest_text(FORMULA_COLUMNS, formula_rows).encode("ascii")
    ).hexdigest()
    cover_hash = hashlib.sha256(
        digest_text(COVER_COLUMNS, cover_rows).encode("ascii")
    ).hexdigest()
    bridge_hash = hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, bridge_rows).encode("ascii")
    ).hexdigest()
    return {
        "formula_rows": formula_rows,
        "cover_rows": cover_rows,
        "bridge_rows": bridge_rows,
        "obs_rows": obs_rows,
        "formula_table": table_from_rows(FORMULA_COLUMNS, formula_rows),
        "cover_table": table_from_rows(COVER_COLUMNS, cover_rows),
        "bridge_table": table_from_rows(BRIDGE_COLUMNS, bridge_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "formula_hash": formula_hash,
        "cover_hash": cover_hash,
        "bridge_hash": bridge_hash,
        "obs": obs,
        "input_reports": {"long_formind": long_formind},
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "input_certified": obs["long_formind_certified_flag"] == 1,
        "dominance_surface_exact": (
            obs["formula_count"],
            obs["positive_term_count"],
            obs["negative_term_count"],
            obs["cover_assignment_count"],
            rows["formula_hash"],
            rows["cover_hash"],
        )
        == (26, 290, 291, 306, FORMULA_TEXT_HASH, COVER_TEXT_HASH),
        "tail_bridge_exact": (
            obs["tail_start_sample_count"],
            obs["formind_probe_end_sample_count"],
            obs["covered_negative_term_count"],
            obs["formula_tail_nonnegative_count"],
            obs["lower_ray_certificate_count"],
            obs["upper_ray_certificate_count"],
            rows["bridge_hash"],
        )
        == (257, 256, 291, 26, 306, 306, BRIDGE_TEXT_HASH),
        "current_dominance_exact": obs["current_dominance_flag"] == 1,
        "table_shapes_match": (
            tuple(rows["formula_table"].shape),
            tuple(rows["cover_table"].shape),
            tuple(rows["bridge_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (26, len(FORMULA_COLUMNS)),
            (306, len(COVER_COLUMNS)),
            (1, len(BRIDGE_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "tail_monomial_dominance_cover_certificate",
        "tail_start_sample_count": TAIL_START,
        "dominance_surface": {
            "formula_count": obs["formula_count"],
            "positive_term_count": obs["positive_term_count"],
            "negative_term_count": obs["negative_term_count"],
            "cover_assignment_count": obs["cover_assignment_count"],
            "covered_negative_term_count": obs["covered_negative_term_count"],
            "formula_tail_nonnegative_count": obs[
                "formula_tail_nonnegative_count"
            ],
            "formula_text_sha256": rows["formula_hash"],
            "cover_text_sha256": rows["cover_hash"],
            "formula_table_sha256": sha_array(rows["formula_table"]),
            "cover_table_sha256": sha_array(rows["cover_table"]),
        },
        "ray_certificates": {
            "lower_ray_certificate_count": obs["lower_ray_certificate_count"],
            "upper_ray_certificate_count": obs["upper_ray_certificate_count"],
            "bridge_text_sha256": rows["bridge_hash"],
            "bridge_table_sha256": sha_array(rows["bridge_table"]),
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    domind_payload = {
        "schema": "long.domind@1",
        "object": "tail_monomial_dominance_cover_certificate",
        "status": STATUS if all(checks.values()) else "LONG_DOMIND_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.domind.report@1",
        "status": domind_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_domind proves the long_formind recurrence formulas "
            "nonnegative for every state in the tail n>=257. Each negative "
            "monomial is fractionally covered by positive monomials whose "
            "2/3-basis ratios are nonincreasing on both domain rays; the "
            "worst ratio is therefore attained at the n=257 endpoints."
        ),
        "stage_protocol": {
            "draft": "read the long_formind formula classes and affine-exponent terms",
            "witness": "construct exact fractional positive-term covers for all negative monomials",
            "coherence": "check ray monotonicity, endpoint bounds, cover capacities, statuses, hashes, and shapes",
            "closure": "emit the tail dominance certificate with the finite-probe seam explicit",
            "emit": "write long_domind artifacts and verifier hook",
        },
        "inputs": {
            "long_formind_report": input_entry(
                LONG_FORMIND_REPORT,
                {"status": rows["input_reports"]["long_formind"].get("status")},
            ),
            "long_formind_class": input_entry(
                LONG_FORMIND_CLASS,
                {"columns": LONG_FORMIND_CLASS_COLUMNS},
            ),
            "long_formind_term": input_entry(
                LONG_FORMIND_TERM,
                {"columns": LONG_FORMIND_TERM_COLUMNS},
            ),
            "long_formind_check": input_entry(
                LONG_FORMIND_CHECK,
                {"columns": LONG_FORMIND_CHECK_COLUMNS},
            ),
            "long_formind_bridge": input_entry(
                LONG_FORMIND_BRIDGE,
                {"columns": LONG_FORMIND_BRIDGE_COLUMNS},
            ),
            "long_formind_tables": input_entry(LONG_FORMIND_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "domind": relpath(OUT_DIR / "domind.json"),
            "formula_csv": relpath(OUT_DIR / "formula.csv"),
            "cover_csv": relpath(OUT_DIR / "cover.csv"),
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
                "tail nonnegativity of all 26 long_formind affine-exponent formulas for n >= 257",
                "fractional positive-term cover of all 291 negative monomial terms",
                "nonincreasing 2/3-basis ratio certificates on both domain rays",
                "the exact seam from the long_formind finite probe ending at n=256",
            ],
            "does_not_certify_because_out_of_scope": [
                "semantic associator composition",
                "the full component-word measure",
                "a raw tensor table materialized in the infinite tail",
                "the final tensor-lookup LLN theorem without the remaining global assembly layer",
            ],
        },
        "next_highest_yield_item": (
            "Build long_gapind: assemble recind, formind, and domind into one "
            "global support-gap induction certificate across the seed, probe, "
            "and infinite-tail regimes."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.domind.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.domind.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "domind": domind_payload,
        "formula_csv": csv_text(FORMULA_COLUMNS, rows["formula_rows"]),
        "cover_csv": csv_text(COVER_COLUMNS, rows["cover_rows"]),
        "bridge_csv": csv_text(BRIDGE_COLUMNS, rows["bridge_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "formula_table": rows["formula_table"],
        "cover_table": rows["cover_table"],
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
    write_json(OUT_DIR / "domind.json", payloads["domind"])
    (OUT_DIR / "formula.csv").write_text(payloads["formula_csv"], encoding="utf-8")
    (OUT_DIR / "cover.csv").write_text(payloads["cover_csv"], encoding="utf-8")
    (OUT_DIR / "bridge.csv").write_text(payloads["bridge_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        formula_table=payloads["formula_table"],
        cover_table=payloads["cover_table"],
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
