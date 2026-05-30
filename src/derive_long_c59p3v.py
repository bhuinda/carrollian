from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path
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
    from .derive_long_raw import csv_text, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_c59p3v"
STATUS = "LONG_C59P3V_LOW_SUPPORT_VOLUME_SELECTOR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59P3S = PROOF_ROOT / "long_c59p3s" / "report.json"
LONG_C59PK = PROOF_ROOT / "long_c59pk" / "report.json"
LONG_C59PK_BASIS = PROOF_ROOT / "long_c59pk" / "restrict_basis.csv"
LONG_C59PK_RESTRICTED = PROOF_ROOT / "long_c59pk" / "restricted_entry.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59p3v.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59p3v.py"

CANDIDATE_COLUMNS = [
    "candidate_id",
    "candidate_type_code",
    "a_restricted_index",
    "b_restricted_index",
    "b_coefficient",
    "support_count",
]
MAX_COLUMNS = [
    "selector_id",
    "selector_code",
    "candidate_a",
    "candidate_b",
    "candidate_c",
    "inertia_positive",
    "inertia_negative",
    "coordinate_support_count",
    "det_sign",
    "det_abs_digit_count",
    "det_abs_mod_1000000007",
    "det_abs_mod_1000000009",
    "unique_within_sign_flag",
    "global_max_flag",
    "sign_dual_partner_id",
    "physical_selector_axiom_flag",
    "selected_physical_flag",
]
SUPPORT_COLUMNS = [
    "selector_id",
    "vector_id",
    "candidate_id",
    "restricted_index",
    "source_atom",
    "coefficient",
]
SUMMARY_COLUMNS = [
    "summary_id",
    "candidate_family_size",
    "triple_count",
    "positive_definite_count",
    "negative_definite_count",
    "definite_total_count",
    "positive_max_tie_count",
    "negative_max_tie_count",
    "global_max_tie_count",
    "sign_dual_pair_flag",
    "unique_physical_selector_flag",
]
DECISION_COLUMNS = [
    "decision_id",
    "decision_code",
    "value",
    "certified_flag",
    "obstruction_flag",
]
GAP_COLUMNS = [
    "gap_id",
    "gap_code",
    "certified_flag",
    "open_flag",
    "obstruction_flag",
    "next_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]

CANDIDATE_TYPE_NAMES = ["singleton", "pair_plus", "pair_minus"]
CANDIDATE_TYPE_CODES = {
    name: index for index, name in enumerate(CANDIDATE_TYPE_NAMES)
}
SELECTOR_NAMES = ["positive_volume_max", "negative_volume_max"]
SELECTOR_CODES = {name: index for index, name in enumerate(SELECTOR_NAMES)}
DECISION_NAMES = [
    "low_support_volume_search_exhaustive",
    "positive_volume_max_unique",
    "negative_volume_max_unique",
    "global_volume_selector_unique",
    "sign_dual_volume_pair_certified",
    "physical_selector_axiom_available",
    "physical_plane_selected",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}
GAP_NAMES = [
    "low_support_volume_pair",
    "sign_dual_orientation_rule",
    "physical_selector_axiom",
    "semantic_transition_operation",
    "stress_coupling_map",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "restricted_dimension",
    "candidate_family_size",
    "triple_count",
    "positive_definite_count",
    "negative_definite_count",
    "definite_total_count",
    "positive_max_candidate_a",
    "positive_max_candidate_b",
    "positive_max_candidate_c",
    "negative_max_candidate_a",
    "negative_max_candidate_b",
    "negative_max_candidate_c",
    "max_abs_det_digit_count",
    "max_abs_det_mod_1000000007",
    "max_abs_det_mod_1000000009",
    "positive_max_tie_count",
    "negative_max_tie_count",
    "global_max_tie_count",
    "sign_dual_pair_flag",
    "physical_selector_axiom_flag",
    "global_unique_selector_flag",
    "unique_physical_selector_flag",
    "selected_physical_flag",
    "next_gap_code",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv_int(path: Path) -> list[dict[str, int]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: int(value) for key, value in row.items()} for row in reader]


def certified(report: dict[str, Any]) -> bool:
    return report.get("all_checks_pass") is True and (
        "CERTIFIED" in str(report.get("status", ""))
        or "OBSTRUCTION_CERTIFIED" in str(report.get("status", ""))
    )


def det3_values(a: int, b: int, c: int, d: int, e: int, f: int) -> int:
    return a * (d * f - e * e) - b * (b * f - e * c) + c * (b * e - d * c)


def build_candidate_rows(dimension: int) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for index in range(dimension):
        rows.append(
            {
                "candidate_id": len(rows),
                "candidate_type_code": CANDIDATE_TYPE_CODES["singleton"],
                "a_restricted_index": index,
                "b_restricted_index": -1,
                "b_coefficient": 0,
                "support_count": 1,
            }
        )
    for left in range(dimension):
        for right in range(left + 1, dimension):
            for coefficient, type_name in [
                (1, "pair_plus"),
                (-1, "pair_minus"),
            ]:
                rows.append(
                    {
                        "candidate_id": len(rows),
                        "candidate_type_code": CANDIDATE_TYPE_CODES[type_name],
                        "a_restricted_index": left,
                        "b_restricted_index": right,
                        "b_coefficient": coefficient,
                        "support_count": 2,
                    }
                )
    return rows


def candidate_vector(candidate: dict[str, int], dimension: int) -> list[int]:
    vector = [0 for _ in range(dimension)]
    vector[candidate["a_restricted_index"]] = 1
    if candidate["b_restricted_index"] >= 0:
        vector[candidate["b_restricted_index"]] = candidate["b_coefficient"]
    return vector


def bilinear(matrix: list[list[int]], left: list[int], right: list[int]) -> int:
    total = 0
    for row_index, row_value in enumerate(left):
        if row_value == 0:
            continue
        row = matrix[row_index]
        for col_index, col_value in enumerate(right):
            if col_value:
                total += row_value * row[col_index] * col_value
    return total


def enumerate_volume_maxima(
    matrix: list[list[int]],
    candidates: list[dict[str, int]],
    dimension: int,
) -> dict[str, Any]:
    vectors = [candidate_vector(candidate, dimension) for candidate in candidates]
    candidate_count = len(candidates)
    gram_cache = [[0 for _ in range(candidate_count)] for _ in range(candidate_count)]
    for row in range(candidate_count):
        for col in range(row, candidate_count):
            value = bilinear(matrix, vectors[row], vectors[col])
            gram_cache[row][col] = value
            gram_cache[col][row] = value

    positive_count = 0
    negative_count = 0
    positive_max = 0
    negative_max = 0
    global_max = 0
    positive_rows: list[tuple[int, int, int, int]] = []
    negative_rows: list[tuple[int, int, int, int]] = []
    global_rows: list[tuple[int, int, int, int, str]] = []
    triple_count = 0
    for left in range(candidate_count - 2):
        left_left = gram_cache[left][left]
        for middle in range(left + 1, candidate_count - 1):
            left_middle = gram_cache[left][middle]
            middle_middle = gram_cache[middle][middle]
            leading_two = left_left * middle_middle - left_middle * left_middle
            for right in range(middle + 1, candidate_count):
                triple_count += 1
                determinant = det3_values(
                    left_left,
                    left_middle,
                    gram_cache[left][right],
                    middle_middle,
                    gram_cache[middle][right],
                    gram_cache[right][right],
                )
                if left_left > 0 and leading_two > 0 and determinant > 0:
                    positive_count += 1
                    abs_determinant = determinant
                    if abs_determinant > positive_max:
                        positive_max = abs_determinant
                        positive_rows = [(left, middle, right, determinant)]
                    elif abs_determinant == positive_max:
                        positive_rows.append((left, middle, right, determinant))
                    if abs_determinant > global_max:
                        global_max = abs_determinant
                        global_rows = [(left, middle, right, determinant, "positive")]
                    elif abs_determinant == global_max:
                        global_rows.append((left, middle, right, determinant, "positive"))
                if left_left < 0 and leading_two > 0 and determinant < 0:
                    negative_count += 1
                    abs_determinant = -determinant
                    if abs_determinant > negative_max:
                        negative_max = abs_determinant
                        negative_rows = [(left, middle, right, determinant)]
                    elif abs_determinant == negative_max:
                        negative_rows.append((left, middle, right, determinant))
                    if abs_determinant > global_max:
                        global_max = abs_determinant
                        global_rows = [(left, middle, right, determinant, "negative")]
                    elif abs_determinant == global_max:
                        global_rows.append((left, middle, right, determinant, "negative"))
    return {
        "vectors": vectors,
        "triple_count": triple_count,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "positive_max": positive_max,
        "negative_max": negative_max,
        "global_max": global_max,
        "positive_rows": positive_rows,
        "negative_rows": negative_rows,
        "global_rows": global_rows,
    }


def sign_dual_triple(
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
    candidates: list[dict[str, int]],
) -> bool:
    for left_id, right_id in zip(left[:3], right[:3]):
        left_candidate = candidates[left_id]
        right_candidate = candidates[right_id]
        if left_candidate["a_restricted_index"] != right_candidate["a_restricted_index"]:
            return False
        if left_candidate["b_restricted_index"] != right_candidate["b_restricted_index"]:
            return False
        if left_candidate["support_count"] != right_candidate["support_count"]:
            return False
        if left_candidate["support_count"] == 1:
            continue
        if left_candidate["b_coefficient"] != -right_candidate["b_coefficient"]:
            return False
    return True


def build_rows() -> dict[str, Any]:
    c59p3s = load_json(LONG_C59P3S)
    c59pk = load_json(LONG_C59PK)
    basis = read_csv_int(LONG_C59PK_BASIS)
    entries = read_csv_int(LONG_C59PK_RESTRICTED)
    dimension = len(basis)
    matrix = [[0 for _ in range(dimension)] for _ in range(dimension)]
    for row in entries:
        matrix[row["row_restricted_index"]][row["col_restricted_index"]] = row[
            "restricted_value"
        ]

    candidate_rows = build_candidate_rows(dimension)
    enumeration = enumerate_volume_maxima(matrix, candidate_rows, dimension)
    positive = enumeration["positive_rows"][0]
    negative = enumeration["negative_rows"][0]
    max_abs_det = enumeration["global_max"]
    physical_selector_flag = int(
        c59p3s["witness"]["summary"]["physical_selector_axiom_flag"]
    )
    sign_dual_pair_flag = int(
        len(enumeration["global_rows"]) == 2
        and sign_dual_triple(positive, negative, candidate_rows)
        and enumeration["positive_max"] == enumeration["negative_max"]
    )
    selector_specs = [
        (
            0,
            SELECTOR_CODES["positive_volume_max"],
            positive,
            3,
            0,
            1,
        ),
        (
            1,
            SELECTOR_CODES["negative_volume_max"],
            negative,
            0,
            3,
            0,
        ),
    ]
    max_rows = []
    support_rows = []
    for selector_id, selector_code, row, positive_inertia, negative_inertia, partner in selector_specs:
        determinant = row[3]
        candidate_ids = row[:3]
        coordinate_support = sorted(
            {
                index
                for candidate_id in candidate_ids
                for index, value in enumerate(enumeration["vectors"][candidate_id])
                if value != 0
            }
        )
        max_rows.append(
            {
                "selector_id": selector_id,
                "selector_code": selector_code,
                "candidate_a": candidate_ids[0],
                "candidate_b": candidate_ids[1],
                "candidate_c": candidate_ids[2],
                "inertia_positive": positive_inertia,
                "inertia_negative": negative_inertia,
                "coordinate_support_count": len(coordinate_support),
                "det_sign": int(determinant > 0) - int(determinant < 0),
                "det_abs_digit_count": len(str(abs(determinant))),
                "det_abs_mod_1000000007": abs(determinant) % 1_000_000_007,
                "det_abs_mod_1000000009": abs(determinant) % 1_000_000_009,
                "unique_within_sign_flag": 1,
                "global_max_flag": 1,
                "sign_dual_partner_id": partner,
                "physical_selector_axiom_flag": physical_selector_flag,
                "selected_physical_flag": 0,
            }
        )
        for vector_id, candidate_id in enumerate(candidate_ids):
            vector = enumeration["vectors"][candidate_id]
            for restricted_index, coefficient in enumerate(vector):
                if coefficient == 0:
                    continue
                support_rows.append(
                    {
                        "selector_id": selector_id,
                        "vector_id": vector_id,
                        "candidate_id": candidate_id,
                        "restricted_index": restricted_index,
                        "source_atom": basis[restricted_index]["source_atom"],
                        "coefficient": coefficient,
                    }
                )

    summary_rows = [
        {
            "summary_id": 0,
            "candidate_family_size": len(candidate_rows),
            "triple_count": enumeration["triple_count"],
            "positive_definite_count": enumeration["positive_count"],
            "negative_definite_count": enumeration["negative_count"],
            "definite_total_count": enumeration["positive_count"]
            + enumeration["negative_count"],
            "positive_max_tie_count": len(enumeration["positive_rows"]),
            "negative_max_tie_count": len(enumeration["negative_rows"]),
            "global_max_tie_count": len(enumeration["global_rows"]),
            "sign_dual_pair_flag": sign_dual_pair_flag,
            "unique_physical_selector_flag": 0,
        }
    ]
    obs = {
        "input_report_count": 2,
        "input_certified_count": int(certified(c59p3s)) + int(certified(c59pk)),
        "restricted_dimension": dimension,
        "candidate_family_size": len(candidate_rows),
        "triple_count": enumeration["triple_count"],
        "positive_definite_count": enumeration["positive_count"],
        "negative_definite_count": enumeration["negative_count"],
        "definite_total_count": enumeration["positive_count"]
        + enumeration["negative_count"],
        "positive_max_candidate_a": positive[0],
        "positive_max_candidate_b": positive[1],
        "positive_max_candidate_c": positive[2],
        "negative_max_candidate_a": negative[0],
        "negative_max_candidate_b": negative[1],
        "negative_max_candidate_c": negative[2],
        "max_abs_det_digit_count": len(str(max_abs_det)),
        "max_abs_det_mod_1000000007": max_abs_det % 1_000_000_007,
        "max_abs_det_mod_1000000009": max_abs_det % 1_000_000_009,
        "positive_max_tie_count": len(enumeration["positive_rows"]),
        "negative_max_tie_count": len(enumeration["negative_rows"]),
        "global_max_tie_count": len(enumeration["global_rows"]),
        "sign_dual_pair_flag": sign_dual_pair_flag,
        "physical_selector_axiom_flag": physical_selector_flag,
        "global_unique_selector_flag": int(len(enumeration["global_rows"]) == 1),
        "unique_physical_selector_flag": 0,
        "selected_physical_flag": 0,
        "next_gap_code": GAP_CODES["sign_dual_orientation_rule"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["low_support_volume_search_exhaustive"],
            "decision_code": DECISION_CODES["low_support_volume_search_exhaustive"],
            "value": obs["triple_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["positive_volume_max_unique"],
            "decision_code": DECISION_CODES["positive_volume_max_unique"],
            "value": obs["positive_max_tie_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["negative_volume_max_unique"],
            "decision_code": DECISION_CODES["negative_volume_max_unique"],
            "value": obs["negative_max_tie_count"],
            "certified_flag": 1,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["global_volume_selector_unique"],
            "decision_code": DECISION_CODES["global_volume_selector_unique"],
            "value": obs["global_unique_selector_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["sign_dual_volume_pair_certified"],
            "decision_code": DECISION_CODES["sign_dual_volume_pair_certified"],
            "value": sign_dual_pair_flag,
            "certified_flag": sign_dual_pair_flag,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["physical_selector_axiom_available"],
            "decision_code": DECISION_CODES["physical_selector_axiom_available"],
            "value": physical_selector_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["physical_plane_selected"],
            "decision_code": DECISION_CODES["physical_plane_selected"],
            "value": obs["selected_physical_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["low_support_volume_pair"],
            "gap_code": GAP_CODES["low_support_volume_pair"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["sign_dual_orientation_rule"],
            "gap_code": GAP_CODES["sign_dual_orientation_rule"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["semantic_transition_operation"],
            "gap_code": GAP_CODES["semantic_transition_operation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["stress_coupling_map"],
            "gap_code": GAP_CODES["stress_coupling_map"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["four_dimensional_metric_reduction"],
            "gap_code": GAP_CODES["four_dimensional_metric_reduction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["thermal_gravity_derivation"],
            "gap_code": GAP_CODES["thermal_gravity_derivation"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
    ]
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": obs[name],
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "c59p3s": c59p3s,
        "c59pk": c59pk,
        "candidate_rows": candidate_rows,
        "max_rows": max_rows,
        "support_rows": support_rows,
        "summary_rows": summary_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    max_table = table_from_rows(MAX_COLUMNS, rows["max_rows"])
    support_table = table_from_rows(SUPPORT_COLUMNS, rows["support_rows"])
    summary_table = table_from_rows(SUMMARY_COLUMNS, rows["summary_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "low_support_search_exhaustive": obs["restricted_dimension"] == 18
        and obs["candidate_family_size"] == 324
        and obs["triple_count"] == 5_616_324,
        "definite_counts_exact": obs["positive_definite_count"] == 2047
        and obs["negative_definite_count"] == 1459
        and obs["definite_total_count"] == 3506,
        "sign_volume_maxima_exact": [
            obs["positive_max_candidate_a"],
            obs["positive_max_candidate_b"],
            obs["positive_max_candidate_c"],
        ]
        == [48, 180, 235]
        and [
            obs["negative_max_candidate_a"],
            obs["negative_max_candidate_b"],
            obs["negative_max_candidate_c"],
        ]
        == [49, 181, 234],
        "global_max_is_sign_dual_pair": obs["positive_max_tie_count"] == 1
        and obs["negative_max_tie_count"] == 1
        and obs["global_max_tie_count"] == 2
        and obs["sign_dual_pair_flag"] == 1
        and obs["global_unique_selector_flag"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["unique_physical_selector_flag"] == 0
        and obs["selected_physical_flag"] == 0,
        "table_shapes_match": candidate_table.shape == (324, len(CANDIDATE_COLUMNS))
        and max_table.shape == (2, len(MAX_COLUMNS))
        and support_table.shape == (12, len(SUPPORT_COLUMNS))
        and summary_table.shape == (1, len(SUMMARY_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "low_support_volume_selector",
        "summary": {
            "candidate_family_size": obs["candidate_family_size"],
            "triple_count": obs["triple_count"],
            "positive_definite_count": obs["positive_definite_count"],
            "negative_definite_count": obs["negative_definite_count"],
            "definite_total_count": obs["definite_total_count"],
            "positive_max_candidate_triple": [
                obs["positive_max_candidate_a"],
                obs["positive_max_candidate_b"],
                obs["positive_max_candidate_c"],
            ],
            "negative_max_candidate_triple": [
                obs["negative_max_candidate_a"],
                obs["negative_max_candidate_b"],
                obs["negative_max_candidate_c"],
            ],
            "max_abs_det_digit_count": obs["max_abs_det_digit_count"],
            "max_abs_det_mod_1000000007": obs["max_abs_det_mod_1000000007"],
            "max_abs_det_mod_1000000009": obs["max_abs_det_mod_1000000009"],
            "positive_max_tie_count": obs["positive_max_tie_count"],
            "negative_max_tie_count": obs["negative_max_tie_count"],
            "global_max_tie_count": obs["global_max_tie_count"],
            "sign_dual_pair_flag": obs["sign_dual_pair_flag"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "global_unique_selector_flag": obs["global_unique_selector_flag"],
            "selected_physical_flag": obs["selected_physical_flag"],
        },
        "candidate_type_code_map": {
            str(value): key for key, value in CANDIDATE_TYPE_CODES.items()
        },
        "selector_code_map": {
            str(value): key for key, value in SELECTOR_CODES.items()
        },
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "candidate_table_sha256": sha_array(candidate_table),
        "max_table_sha256": sha_array(max_table),
        "support_table_sha256": sha_array(support_table),
        "summary_table_sha256": sha_array(summary_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "candidate_text_sha256": sha_text(
            csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"])
        ),
        "max_text_sha256": sha_text(csv_text(MAX_COLUMNS, rows["max_rows"])),
    }
    c59p3v = {
        "schema": "long.c59p3v@1",
        "object": "low_support_volume_selector",
        "status": STATUS if all(checks.values()) else "LONG_C59P3V_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59p3v.report@1",
        "status": c59p3v["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59p3v exhaustively scores the low-support 3-plane candidate "
            "family by exact Gram volume. It finds a unique positive maximum "
            "and a unique negative maximum, but the two are an exact sign-dual "
            "pair with equal absolute volume. The formal selector is therefore "
            "reduced to a two-element sign-dual pair, not a physical choice."
        ),
        "stage_protocol": {
            "draft": "read long_c59p3s and the 18D restricted form from long_c59pk",
            "witness": "emit the low-support candidate family, max-volume selector rows, support rows, summary, decisions, gaps, and observables",
            "coherence": "check exhaustive candidate-triple counts, definite counts, max triples, sign-dual equality, and physical exclusions",
            "closure": "certify the low-support volume selector pair and the sign-dual orientation gap",
            "emit": "write long_c59p3v artifacts and verifier hook",
        },
        "inputs": {
            "long_c59p3s": input_entry(
                LONG_C59P3S,
                {
                    "status": rows["c59p3s"].get("status"),
                    "certificate_sha256": rows["c59p3s"].get("certificate_sha256"),
                },
            ),
            "long_c59pk": input_entry(
                LONG_C59PK,
                {
                    "status": rows["c59pk"].get("status"),
                    "certificate_sha256": rows["c59pk"].get("certificate_sha256"),
                },
            ),
            "long_c59pk_basis": input_entry(LONG_C59PK_BASIS),
            "long_c59pk_restricted": input_entry(LONG_C59PK_RESTRICTED),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59p3v": relpath(OUT_DIR / "c59p3v.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "max_csv": relpath(OUT_DIR / "max.csv"),
            "support_csv": relpath(OUT_DIR / "support.csv"),
            "summary_csv": relpath(OUT_DIR / "summary.csv"),
            "decision_csv": relpath(OUT_DIR / "decision.csv"),
            "gap_csv": relpath(OUT_DIR / "gap.csv"),
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
                "all 5,616,324 triples in the low-support 18D candidate family are scored",
                "2,047 positive definite and 1,459 negative definite low-support triples exist",
                "the positive max-volume triple is uniquely [48,180,235]",
                "the negative max-volume triple is uniquely [49,181,234]",
                "the two sign maxima have equal absolute Gram volume and form a sign-dual pair",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a unique global physical 3-plane selector",
                "an orientation rule choosing between the sign-dual pair",
                "acceptance of a physical selector axiom",
                "semantic transition-operation realization",
                "a transition-to-stress coupling map",
                "a four-dimensional metric reduction or thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Resolve the sign-dual orientation gap: test whether time direction, "
            "transition semantics, or stress coupling distinguishes [48,180,235] "
            "from [49,181,234]; otherwise certify the symmetry as the current "
            "orientation obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59p3v.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59p3v.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59p3v": c59p3v,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "max_csv": csv_text(MAX_COLUMNS, rows["max_rows"]),
        "support_csv": csv_text(SUPPORT_COLUMNS, rows["support_rows"]),
        "summary_csv": csv_text(SUMMARY_COLUMNS, rows["summary_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": candidate_table,
        "max_table": max_table,
        "support_table": support_table,
        "summary_table": summary_table,
        "decision_table": decision_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "cert": cert,
        "manifest": manifest,
        "report": report,
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
    write_json(OUT_DIR / "c59p3v.json", payloads["c59p3v"])
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "max.csv").write_text(payloads["max_csv"], encoding="utf-8")
    (OUT_DIR / "support.csv").write_text(payloads["support_csv"], encoding="utf-8")
    (OUT_DIR / "summary.csv").write_text(payloads["summary_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        max_table=payloads["max_table"],
        support_table=payloads["support_table"],
        summary_table=payloads["summary_table"],
        decision_table=payloads["decision_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(OUT_DIR / "cert.json", payloads["cert"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    write_json(OUT_DIR / "report.json", payloads["report"])
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
                "summary": report["witness"]["summary"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
