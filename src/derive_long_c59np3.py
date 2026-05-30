from __future__ import annotations

import csv
import hashlib
import itertools
import json
from fractions import Fraction
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


THEOREM_ID = "long_c59np3"
STATUS = "LONG_C59NP3_NONPRINCIPAL_THREE_PLANE_WITNESS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59PK = PROOF_ROOT / "long_c59pk" / "report.json"
LONG_C59PK_BASIS = PROOF_ROOT / "long_c59pk" / "restrict_basis.csv"
LONG_C59PK_RESTRICTED = PROOF_ROOT / "long_c59pk" / "restricted_entry.csv"
LONG_C59S3 = PROOF_ROOT / "long_c59s3" / "report.json"
LONG_SEL = PROOF_ROOT / "long_sel" / "report.json"
LONG_DIM4_GATE = PROOF_ROOT / "long_dim4_gate" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59np3.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59np3.py"

CANDIDATE_COLUMNS = [
    "candidate_id",
    "candidate_type_code",
    "a_restricted_index",
    "b_restricted_index",
    "b_coefficient",
    "support_count",
]
SEARCH_COLUMNS = [
    "plane_id",
    "plane_code",
    "candidate_a",
    "candidate_b",
    "candidate_c",
    "lex_first_flag",
    "checked_triple_count",
]
PLANE_COLUMNS = [
    "plane_id",
    "plane_code",
    "candidate_family_code",
    "vector_count",
    "coordinate_support_count",
    "coordinate_rank",
    "nonprincipal_flag",
    "inertia_positive",
    "inertia_negative",
    "inertia_zero",
    "definite_spatial_flag",
    "gram_det_sign",
    "gram_det_abs_digit_count",
    "gram_det_abs_mod_1000000007",
    "gram_det_abs_mod_1000000009",
    "physical_selector_axiom_flag",
    "canonical_physical_selection_flag",
]
VECTOR_COLUMNS = [
    "plane_id",
    "vector_id",
    "candidate_id",
    "restricted_index",
    "source_atom",
    "coefficient",
]
GRAM_COLUMNS = ["plane_id", "row_vector_id", "col_vector_id", "gram_value"]
MINOR_COLUMNS = [
    "plane_id",
    "minor_order",
    "minor_sign",
    "minor_abs_digit_count",
    "minor_abs_mod_1000000007",
    "minor_abs_mod_1000000009",
    "positive_condition_flag",
    "negative_condition_flag",
]
MINOR_EXACT_COLUMNS = ["plane_id", "minor_order", "minor_exact"]
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
PLANE_NAMES = ["positive_definite_plane", "negative_definite_plane"]
PLANE_CODES = {name: index for index, name in enumerate(PLANE_NAMES)}
CANDIDATE_FAMILY_NAMES = ["low_support_pair_vectors"]
CANDIDATE_FAMILY_CODES = {
    name: index for index, name in enumerate(CANDIDATE_FAMILY_NAMES)
}
DECISION_NAMES = [
    "low_support_nonprincipal_positive_plane_exists",
    "low_support_nonprincipal_negative_plane_exists",
    "principal_only_candidate_boundary_retired",
    "physical_selector_axiom_available",
    "canonical_physical_three_selection_certified",
    "four_dimensional_metric_reduction_certified",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}
GAP_NAMES = [
    "nonprincipal_algebraic_three_plane",
    "physical_selector_axiom",
    "canonical_physical_three_selection",
    "four_dimensional_metric_reduction",
    "smooth_lorentzian_metric",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}
OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "restricted_dimension",
    "candidate_family_size",
    "positive_plane_found_flag",
    "negative_plane_found_flag",
    "nonprincipal_definite_plane_count",
    "positive_plane_candidate_a",
    "positive_plane_candidate_b",
    "positive_plane_candidate_c",
    "negative_plane_candidate_a",
    "negative_plane_candidate_b",
    "negative_plane_candidate_c",
    "positive_checked_triple_count",
    "negative_checked_triple_count",
    "principal_positive_definite_count",
    "principal_negative_definite_count",
    "principal_only_candidate_boundary_retired_flag",
    "physical_selector_axiom_flag",
    "dim4_reduction_certified_flag",
    "formal_nonprincipal_selector_flag",
    "canonical_physical_selection_flag",
    "four_dimensional_metric_flag",
    "physical_stress_energy_flag",
    "smooth_metric_flag",
    "thermal_gravity_flag",
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


def determinant2(matrix: list[list[int]]) -> int:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def determinant3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def leading_minors(matrix: list[list[int]]) -> list[int]:
    return [matrix[0][0], determinant2([row[:2] for row in matrix[:2]]), determinant3(matrix)]


def is_positive_definite(matrix: list[list[int]]) -> bool:
    return all(value > 0 for value in leading_minors(matrix))


def is_negative_definite(matrix: list[list[int]]) -> bool:
    minors = leading_minors(matrix)
    return minors[0] < 0 and minors[1] > 0 and minors[2] < 0


def matrix_rank(rows: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in rows]
    rank = 0
    column_count = len(work[0]) if work else 0
    for column in range(column_count):
        pivot = None
        for row in range(rank, len(work)):
            if work[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(len(work)):
            if row == rank:
                continue
            factor = work[row][column]
            if factor == 0:
                continue
            work[row] = [
                work[row][index] - factor * work[rank][index]
                for index in range(column_count)
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def sign(value: int) -> int:
    return int(value > 0) - int(value < 0)


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
        for col_index, col_value in enumerate(right):
            if col_value != 0:
                total += row_value * matrix[row_index][col_index] * col_value
    return total


def gram_matrix(matrix: list[list[int]], vectors: list[list[int]]) -> list[list[int]]:
    return [
        [bilinear(matrix, left, right) for right in vectors]
        for left in vectors
    ]


def find_first_definite_triples(
    matrix: list[list[int]],
    candidates: list[dict[str, int]],
    dimension: int,
) -> dict[str, dict[str, Any]]:
    vectors = [candidate_vector(candidate, dimension) for candidate in candidates]
    gram_cache = [
        [bilinear(matrix, vectors[row], vectors[col]) for col in range(len(vectors))]
        for row in range(len(vectors))
    ]
    found: dict[str, dict[str, Any]] = {}
    checked = 0
    for triple in itertools.combinations(range(len(candidates)), 3):
        checked += 1
        a, b, c = triple
        gram = [
            [gram_cache[a][a], gram_cache[a][b], gram_cache[a][c]],
            [gram_cache[b][a], gram_cache[b][b], gram_cache[b][c]],
            [gram_cache[c][a], gram_cache[c][b], gram_cache[c][c]],
        ]
        if "positive" not in found and is_positive_definite(gram):
            found["positive"] = {
                "triple": triple,
                "vectors": [vectors[index] for index in triple],
                "gram": gram,
                "checked_triple_count": checked,
            }
        if "negative" not in found and is_negative_definite(gram):
            found["negative"] = {
                "triple": triple,
                "vectors": [vectors[index] for index in triple],
                "gram": gram,
                "checked_triple_count": checked,
            }
        if len(found) == 2:
            break
    return found


def exact_csv(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def build_rows() -> dict[str, Any]:
    c59pk = load_json(LONG_C59PK)
    c59s3 = load_json(LONG_C59S3)
    long_sel = load_json(LONG_SEL)
    dim4_gate = load_json(LONG_DIM4_GATE)
    basis = read_csv_int(LONG_C59PK_BASIS)
    entries = read_csv_int(LONG_C59PK_RESTRICTED)
    dimension = len(basis)
    matrix = [[0 for _ in range(dimension)] for _ in range(dimension)]
    for row in entries:
        matrix[row["row_restricted_index"]][row["col_restricted_index"]] = row[
            "restricted_value"
        ]

    candidate_rows = build_candidate_rows(dimension)
    found = find_first_definite_triples(matrix, candidate_rows, dimension)
    selector_flag = int(long_sel["witness"]["summary"]["physical_selector_axiom_flag"])
    dim4_flag = int(dim4_gate["witness"]["summary"]["dim4_reduction_certified_flag"])
    principal_positive = int(c59s3["witness"]["summary"]["positive_definite_count"])
    principal_negative = int(c59s3["witness"]["summary"]["negative_definite_count"])

    plane_specs = [
        (
            PLANE_CODES["positive_definite_plane"],
            "positive",
            (3, 0, 0),
        ),
        (
            PLANE_CODES["negative_definite_plane"],
            "negative",
            (0, 3, 0),
        ),
    ]
    search_rows = []
    plane_rows = []
    vector_rows = []
    gram_rows = []
    minor_rows = []
    minor_exact_rows = []
    for plane_id, lookup_key, inertia in plane_specs:
        witness = found[lookup_key]
        triple = witness["triple"]
        vectors = witness["vectors"]
        gram = witness["gram"]
        minors = leading_minors(gram)
        determinant = minors[2]
        coordinate_support = sorted(
            {
                index
                for vector in vectors
                for index, value in enumerate(vector)
                if value != 0
            }
        )
        search_rows.append(
            {
                "plane_id": plane_id,
                "plane_code": plane_id,
                "candidate_a": triple[0],
                "candidate_b": triple[1],
                "candidate_c": triple[2],
                "lex_first_flag": 1,
                "checked_triple_count": witness["checked_triple_count"],
            }
        )
        plane_rows.append(
            {
                "plane_id": plane_id,
                "plane_code": plane_id,
                "candidate_family_code": CANDIDATE_FAMILY_CODES[
                    "low_support_pair_vectors"
                ],
                "vector_count": 3,
                "coordinate_support_count": len(coordinate_support),
                "coordinate_rank": matrix_rank(vectors),
                "nonprincipal_flag": int(len(coordinate_support) > 3),
                "inertia_positive": inertia[0],
                "inertia_negative": inertia[1],
                "inertia_zero": inertia[2],
                "definite_spatial_flag": 1,
                "gram_det_sign": sign(determinant),
                "gram_det_abs_digit_count": len(str(abs(determinant))),
                "gram_det_abs_mod_1000000007": abs(determinant) % 1_000_000_007,
                "gram_det_abs_mod_1000000009": abs(determinant) % 1_000_000_009,
                "physical_selector_axiom_flag": selector_flag,
                "canonical_physical_selection_flag": 0,
            }
        )
        for vector_id, (candidate_id, vector) in enumerate(zip(triple, vectors)):
            for restricted_index, coefficient in enumerate(vector):
                if coefficient == 0:
                    continue
                vector_rows.append(
                    {
                        "plane_id": plane_id,
                        "vector_id": vector_id,
                        "candidate_id": candidate_id,
                        "restricted_index": restricted_index,
                        "source_atom": basis[restricted_index]["source_atom"],
                        "coefficient": coefficient,
                    }
                )
        for row_index, gram_row in enumerate(gram):
            for col_index, value in enumerate(gram_row):
                gram_rows.append(
                    {
                        "plane_id": plane_id,
                        "row_vector_id": row_index,
                        "col_vector_id": col_index,
                        "gram_value": value,
                    }
                )
        for minor_order, minor_value in enumerate(minors, start=1):
            minor_rows.append(
                {
                    "plane_id": plane_id,
                    "minor_order": minor_order,
                    "minor_sign": sign(minor_value),
                    "minor_abs_digit_count": len(str(abs(minor_value))),
                    "minor_abs_mod_1000000007": abs(minor_value) % 1_000_000_007,
                    "minor_abs_mod_1000000009": abs(minor_value) % 1_000_000_009,
                    "positive_condition_flag": int(minor_value > 0),
                    "negative_condition_flag": int(
                        (minor_order in [1, 3] and minor_value < 0)
                        or (minor_order == 2 and minor_value > 0)
                    ),
                }
            )
            minor_exact_rows.append(
                {
                    "plane_id": plane_id,
                    "minor_order": minor_order,
                    "minor_exact": str(minor_value),
                }
            )

    positive_search = search_rows[PLANE_CODES["positive_definite_plane"]]
    negative_search = search_rows[PLANE_CODES["negative_definite_plane"]]
    formal_selector_flag = int(
        len(plane_rows) == 2
        and all(row["nonprincipal_flag"] == 1 for row in plane_rows)
        and all(row["definite_spatial_flag"] == 1 for row in plane_rows)
    )
    principal_only_retired = int(
        formal_selector_flag == 1
        and principal_positive == 0
        and principal_negative == 0
    )
    obs = {
        "input_report_count": 4,
        "input_certified_count": int(certified(c59pk))
        + int(certified(c59s3))
        + int(certified(long_sel))
        + int(certified(dim4_gate)),
        "restricted_dimension": dimension,
        "candidate_family_size": len(candidate_rows),
        "positive_plane_found_flag": int("positive" in found),
        "negative_plane_found_flag": int("negative" in found),
        "nonprincipal_definite_plane_count": len(plane_rows),
        "positive_plane_candidate_a": positive_search["candidate_a"],
        "positive_plane_candidate_b": positive_search["candidate_b"],
        "positive_plane_candidate_c": positive_search["candidate_c"],
        "negative_plane_candidate_a": negative_search["candidate_a"],
        "negative_plane_candidate_b": negative_search["candidate_b"],
        "negative_plane_candidate_c": negative_search["candidate_c"],
        "positive_checked_triple_count": positive_search["checked_triple_count"],
        "negative_checked_triple_count": negative_search["checked_triple_count"],
        "principal_positive_definite_count": principal_positive,
        "principal_negative_definite_count": principal_negative,
        "principal_only_candidate_boundary_retired_flag": principal_only_retired,
        "physical_selector_axiom_flag": selector_flag,
        "dim4_reduction_certified_flag": dim4_flag,
        "formal_nonprincipal_selector_flag": formal_selector_flag,
        "canonical_physical_selection_flag": 0,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["physical_selector_axiom"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES[
                "low_support_nonprincipal_positive_plane_exists"
            ],
            "decision_code": DECISION_CODES[
                "low_support_nonprincipal_positive_plane_exists"
            ],
            "value": obs["positive_plane_found_flag"],
            "certified_flag": obs["positive_plane_found_flag"],
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES[
                "low_support_nonprincipal_negative_plane_exists"
            ],
            "decision_code": DECISION_CODES[
                "low_support_nonprincipal_negative_plane_exists"
            ],
            "value": obs["negative_plane_found_flag"],
            "certified_flag": obs["negative_plane_found_flag"],
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["principal_only_candidate_boundary_retired"],
            "decision_code": DECISION_CODES["principal_only_candidate_boundary_retired"],
            "value": principal_only_retired,
            "certified_flag": principal_only_retired,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["physical_selector_axiom_available"],
            "decision_code": DECISION_CODES["physical_selector_axiom_available"],
            "value": selector_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES[
                "canonical_physical_three_selection_certified"
            ],
            "decision_code": DECISION_CODES[
                "canonical_physical_three_selection_certified"
            ],
            "value": obs["canonical_physical_selection_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES[
                "four_dimensional_metric_reduction_certified"
            ],
            "decision_code": DECISION_CODES[
                "four_dimensional_metric_reduction_certified"
            ],
            "value": dim4_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["nonprincipal_algebraic_three_plane"],
            "gap_code": GAP_CODES["nonprincipal_algebraic_three_plane"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["physical_selector_axiom"],
            "gap_code": GAP_CODES["physical_selector_axiom"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 1,
        },
        {
            "gap_id": GAP_CODES["canonical_physical_three_selection"],
            "gap_code": GAP_CODES["canonical_physical_three_selection"],
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
            "gap_id": GAP_CODES["smooth_lorentzian_metric"],
            "gap_code": GAP_CODES["smooth_lorentzian_metric"],
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
        "c59pk": c59pk,
        "c59s3": c59s3,
        "long_sel": long_sel,
        "dim4_gate": dim4_gate,
        "candidate_rows": candidate_rows,
        "search_rows": search_rows,
        "plane_rows": plane_rows,
        "vector_rows": vector_rows,
        "gram_rows": gram_rows,
        "minor_rows": minor_rows,
        "minor_exact_rows": minor_exact_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    search_table = table_from_rows(SEARCH_COLUMNS, rows["search_rows"])
    plane_table = table_from_rows(PLANE_COLUMNS, rows["plane_rows"])
    vector_table = table_from_rows(VECTOR_COLUMNS, rows["vector_rows"])
    gram_table = table_from_rows(GRAM_COLUMNS, rows["gram_rows"])
    minor_table = table_from_rows(MINOR_COLUMNS, rows["minor_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    minor_exact_text = exact_csv(MINOR_EXACT_COLUMNS, rows["minor_exact_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "candidate_family_exact": obs["restricted_dimension"] == 18
        and obs["candidate_family_size"] == 324,
        "positive_nonprincipal_witness_exact": obs["positive_plane_found_flag"] == 1
        and [
            obs["positive_plane_candidate_a"],
            obs["positive_plane_candidate_b"],
            obs["positive_plane_candidate_c"],
        ]
        == [20, 54, 153],
        "negative_nonprincipal_witness_exact": obs["negative_plane_found_flag"] == 1
        and [
            obs["negative_plane_candidate_a"],
            obs["negative_plane_candidate_b"],
            obs["negative_plane_candidate_c"],
        ]
        == [21, 55, 171],
        "definite_nonprincipal_planes_verified": all(
            row["definite_spatial_flag"] == 1
            and row["nonprincipal_flag"] == 1
            and row["coordinate_rank"] == 3
            for row in rows["plane_rows"]
        )
        and obs["nonprincipal_definite_plane_count"] == 2,
        "principal_only_boundary_retired": obs[
            "principal_only_candidate_boundary_retired_flag"
        ]
        == 1
        and obs["principal_positive_definite_count"] == 0
        and obs["principal_negative_definite_count"] == 0,
        "physical_boundaries_preserved": obs["physical_selector_axiom_flag"] == 0
        and obs["dim4_reduction_certified_flag"] == 0
        and obs["canonical_physical_selection_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": candidate_table.shape == (324, len(CANDIDATE_COLUMNS))
        and search_table.shape == (2, len(SEARCH_COLUMNS))
        and plane_table.shape == (2, len(PLANE_COLUMNS))
        and vector_table.shape == (12, len(VECTOR_COLUMNS))
        and gram_table.shape == (18, len(GRAM_COLUMNS))
        and minor_table.shape == (6, len(MINOR_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "nonprincipal_three_plane_witness",
        "summary": {
            "restricted_dimension": obs["restricted_dimension"],
            "candidate_family_size": obs["candidate_family_size"],
            "positive_plane_found_flag": obs["positive_plane_found_flag"],
            "negative_plane_found_flag": obs["negative_plane_found_flag"],
            "nonprincipal_definite_plane_count": obs[
                "nonprincipal_definite_plane_count"
            ],
            "positive_plane_candidate_triple": [
                obs["positive_plane_candidate_a"],
                obs["positive_plane_candidate_b"],
                obs["positive_plane_candidate_c"],
            ],
            "negative_plane_candidate_triple": [
                obs["negative_plane_candidate_a"],
                obs["negative_plane_candidate_b"],
                obs["negative_plane_candidate_c"],
            ],
            "principal_positive_definite_count": obs[
                "principal_positive_definite_count"
            ],
            "principal_negative_definite_count": obs[
                "principal_negative_definite_count"
            ],
            "principal_only_candidate_boundary_retired_flag": obs[
                "principal_only_candidate_boundary_retired_flag"
            ],
            "formal_nonprincipal_selector_flag": obs[
                "formal_nonprincipal_selector_flag"
            ],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "canonical_physical_selection_flag": obs[
                "canonical_physical_selection_flag"
            ],
            "four_dimensional_metric_flag": obs["four_dimensional_metric_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "candidate_type_code_map": {
            str(value): key for key, value in CANDIDATE_TYPE_CODES.items()
        },
        "plane_code_map": {str(value): key for key, value in PLANE_CODES.items()},
        "candidate_family_code_map": {
            str(value): key for key, value in CANDIDATE_FAMILY_CODES.items()
        },
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "candidate_table_sha256": sha_array(candidate_table),
        "search_table_sha256": sha_array(search_table),
        "plane_table_sha256": sha_array(plane_table),
        "vector_table_sha256": sha_array(vector_table),
        "gram_table_sha256": sha_array(gram_table),
        "minor_table_sha256": sha_array(minor_table),
        "minor_exact_text_sha256": sha_text(minor_exact_text),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59np3 = {
        "schema": "long.c59np3@1",
        "object": "nonprincipal_three_plane_witness",
        "status": STATUS if all(checks.values()) else "LONG_C59NP3_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59np3.report@1",
        "status": c59np3["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59np3 constructs exact low-support non-principal positive "
            "and negative definite 3-plane witnesses inside the 18D induced "
            "public-kernel form. This retires the principal-only candidate "
            "boundary from long_c59s3, while preserving the open physical "
            "selector and metric-reduction gaps."
        ),
        "stage_protocol": {
            "draft": "read long_c59pk, long_c59s3, long_sel, and long_dim4_gate",
            "witness": "emit the low-support candidate family, first definite plane searches, vector rows, Gram rows, minors, decisions, gaps, and observables",
            "coherence": "check exact definiteness, rank, non-principal support, candidate triples, and preserved selector/metric obstructions",
            "closure": "certify algebraic non-principal 3-plane witnesses without certifying a physical selector",
            "emit": "write long_c59np3 artifacts and verifier hook",
        },
        "inputs": {
            "long_c59pk": input_entry(
                LONG_C59PK,
                {
                    "status": rows["c59pk"].get("status"),
                    "certificate_sha256": rows["c59pk"].get("certificate_sha256"),
                },
            ),
            "long_c59pk_basis": input_entry(LONG_C59PK_BASIS),
            "long_c59pk_restricted": input_entry(LONG_C59PK_RESTRICTED),
            "long_c59s3": input_entry(
                LONG_C59S3,
                {
                    "status": rows["c59s3"].get("status"),
                    "certificate_sha256": rows["c59s3"].get("certificate_sha256"),
                },
            ),
            "long_sel": input_entry(
                LONG_SEL,
                {
                    "status": rows["long_sel"].get("status"),
                    "certificate_sha256": rows["long_sel"].get("certificate_sha256"),
                },
            ),
            "long_dim4_gate": input_entry(
                LONG_DIM4_GATE,
                {
                    "status": rows["dim4_gate"].get("status"),
                    "certificate_sha256": rows["dim4_gate"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59np3": relpath(OUT_DIR / "c59np3.json"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
            "search_csv": relpath(OUT_DIR / "search.csv"),
            "plane_csv": relpath(OUT_DIR / "plane.csv"),
            "vector_csv": relpath(OUT_DIR / "vector.csv"),
            "gram_csv": relpath(OUT_DIR / "gram.csv"),
            "minor_csv": relpath(OUT_DIR / "minor.csv"),
            "minor_exact_csv": relpath(OUT_DIR / "minor_exact.csv"),
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
                "an exact low-support non-principal positive definite 3-plane exists in the 18D restricted form",
                "an exact low-support non-principal negative definite 3-plane exists in the 18D restricted form",
                "the long_c59s3 principal-only candidate boundary is retired by explicit non-principal witnesses",
                "the witnessed 3-planes are algebraic finite-form subspaces, not physical selector axioms",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "exhaustive classification of all non-principal 3D linear subspaces",
                "a canonical physical selector for one of the witnessed 3-planes",
                "a four-dimensional metric reduction",
                "a smooth Lorentzian metric",
                "a physical stress-energy tensor",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Promote or obstruct the physical selector axiom over the witnessed "
            "non-principal 3-planes: decide whether the finite oracle can "
            "choose one plane coherently with time, transition semantics, and "
            "stress coupling."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59np3.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59np3.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59np3": c59np3,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "search_csv": csv_text(SEARCH_COLUMNS, rows["search_rows"]),
        "plane_csv": csv_text(PLANE_COLUMNS, rows["plane_rows"]),
        "vector_csv": csv_text(VECTOR_COLUMNS, rows["vector_rows"]),
        "gram_csv": csv_text(GRAM_COLUMNS, rows["gram_rows"]),
        "minor_csv": csv_text(MINOR_COLUMNS, rows["minor_rows"]),
        "minor_exact_csv": minor_exact_text,
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "candidate_table": candidate_table,
        "search_table": search_table,
        "plane_table": plane_table,
        "vector_table": vector_table,
        "gram_table": gram_table,
        "minor_table": minor_table,
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
    write_json(OUT_DIR / "c59np3.json", payloads["c59np3"])
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "search.csv").write_text(payloads["search_csv"], encoding="utf-8")
    (OUT_DIR / "plane.csv").write_text(payloads["plane_csv"], encoding="utf-8")
    (OUT_DIR / "vector.csv").write_text(payloads["vector_csv"], encoding="utf-8")
    (OUT_DIR / "gram.csv").write_text(payloads["gram_csv"], encoding="utf-8")
    (OUT_DIR / "minor.csv").write_text(payloads["minor_csv"], encoding="utf-8")
    (OUT_DIR / "minor_exact.csv").write_text(
        payloads["minor_exact_csv"], encoding="utf-8"
    )
    (OUT_DIR / "decision.csv").write_text(
        payloads["decision_csv"], encoding="utf-8"
    )
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        candidate_table=payloads["candidate_table"],
        search_table=payloads["search_table"],
        plane_table=payloads["plane_table"],
        vector_table=payloads["vector_table"],
        gram_table=payloads["gram_table"],
        minor_table=payloads["minor_table"],
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
