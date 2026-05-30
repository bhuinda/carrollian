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


THEOREM_ID = "long_c59s3"
STATUS = "LONG_C59S3_PRINCIPAL_THREE_SUBFORM_SEARCH_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59PK = PROOF_ROOT / "long_c59pk" / "report.json"
LONG_C59PK_BASIS = PROOF_ROOT / "long_c59pk" / "restrict_basis.csv"
LONG_C59PK_RESTRICTED = PROOF_ROOT / "long_c59pk" / "restricted_entry.csv"
LONG_SEL = PROOF_ROOT / "long_sel" / "report.json"
LONG_DIM4_GATE = PROOF_ROOT / "long_dim4_gate" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59s3.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59s3.py"

SUBFORM_COLUMNS = [
    "subform_id",
    "a_restricted_index",
    "b_restricted_index",
    "c_restricted_index",
    "a_source_atom",
    "b_source_atom",
    "c_source_atom",
    "rank",
    "inertia_positive",
    "inertia_negative",
    "inertia_zero",
    "det_sign",
    "det_abs_digit_count",
    "det_abs_mod_1000000007",
    "det_abs_mod_1000000009",
    "nondegenerate_flag",
    "definite_spatial_flag",
    "max_abs_det_flag",
]
DETERMINANT_COLUMNS = ["subform_id", "determinant_exact"]
CANDIDATE_COLUMNS = [
    "candidate_id",
    "subform_id",
    "a_restricted_index",
    "b_restricted_index",
    "c_restricted_index",
    "a_source_atom",
    "b_source_atom",
    "c_source_atom",
    "inertia_positive",
    "inertia_negative",
    "det_sign",
    "det_abs_digit_count",
    "det_abs_mod_1000000007",
    "det_abs_mod_1000000009",
    "max_abs_det_flag",
    "definite_spatial_flag",
]
SUMMARY_COLUMNS = [
    "summary_id",
    "summary_code",
    "subform_count",
    "rank3_count",
    "rank2_count",
    "rank1_count",
    "rank0_count",
    "positive_definite_count",
    "negative_definite_count",
    "inertia_210_count",
    "inertia_120_count",
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

SUMMARY_NAMES = ["principal_three_subform_inventory"]
SUMMARY_CODES = {name: index for index, name in enumerate(SUMMARY_NAMES)}

DECISION_NAMES = [
    "principal_three_search_exhaustive",
    "nondegenerate_principal_three_exists",
    "unique_max_volume_principal_three_exists",
    "definite_spatial_principal_three_exists",
    "physical_selector_axiom_available",
    "canonical_three_spatial_selection_certified",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "principal_three_subform_inventory",
    "definite_spatial_three_subform",
    "physical_selector_axiom",
    "canonical_three_spatial_selection",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "restricted_dimension",
    "principal_three_subform_count",
    "rank3_subform_count",
    "rank2_subform_count",
    "rank1_subform_count",
    "rank0_subform_count",
    "positive_definite_count",
    "negative_definite_count",
    "definite_spatial_count",
    "inertia_210_count",
    "inertia_120_count",
    "unique_max_abs_det_flag",
    "max_abs_det_subform_id",
    "max_abs_det_inertia_positive",
    "max_abs_det_inertia_negative",
    "max_abs_det_digit_count",
    "max_abs_det_mod_1000000007",
    "physical_selector_axiom_flag",
    "dim4_reduction_certified_flag",
    "canonical_three_spatial_selection_flag",
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


def det3(matrix: list[list[int]]) -> int:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def rank3(matrix: list[list[int]]) -> int:
    determinant = det3(matrix)
    if determinant != 0:
        return 3
    for i in range(3):
        for j in range(i + 1, 3):
            if matrix[i][i] * matrix[j][j] - matrix[i][j] * matrix[j][i] != 0:
                return 2
    if any(value != 0 for row in matrix for value in row):
        return 1
    return 0


def inertia(matrix: list[list[int]]) -> tuple[int, int, int]:
    current = [[Fraction(value) for value in row] for row in matrix]
    positive = 0
    negative = 0
    zero = 0
    while current:
        dimension = len(current)
        diagonal = None
        for index in range(dimension):
            if current[index][index] != 0:
                diagonal = index
                break
        if diagonal is not None:
            if diagonal != 0:
                current[0], current[diagonal] = current[diagonal], current[0]
                for row in current:
                    row[0], row[diagonal] = row[diagonal], row[0]
            pivot = current[0][0]
            positive += int(pivot > 0)
            negative += int(pivot < 0)
            if dimension == 1:
                current = []
                continue
            column = [current[row][0] for row in range(1, dimension)]
            current = [
                [
                    current[row][col] - column[row - 1] * column[col - 1] / pivot
                    for col in range(1, dimension)
                ]
                for row in range(1, dimension)
            ]
            continue

        pair = None
        for row in range(dimension):
            for col in range(row + 1, dimension):
                if current[row][col] != 0:
                    pair = (row, col)
                    break
            if pair is not None:
                break
        if pair is None:
            zero += dimension
            break
        order = [pair[0], pair[1]] + [
            index for index in range(dimension) if index not in pair
        ]
        current = [[current[row][col] for col in order] for row in order]
        off_diagonal = current[0][1]
        positive += 1
        negative += 1
        if dimension == 2:
            current = []
            continue
        side = [[current[row][col] for col in range(2)] for row in range(2, dimension)]
        corner = [
            [current[row][col] for col in range(2, dimension)]
            for row in range(2, dimension)
        ]
        current = [
            [
                corner[row][col]
                - (
                    side[row][0] * side[col][1]
                    + side[row][1] * side[col][0]
                )
                / off_diagonal
                for col in range(dimension - 2)
            ]
            for row in range(dimension - 2)
        ]
    return positive, negative, zero


def build_rows() -> dict[str, Any]:
    c59pk = load_json(LONG_C59PK)
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

    subform_rows = []
    determinant_rows = []
    for subform_id, combo in enumerate(itertools.combinations(range(dimension), 3)):
        submatrix = [[matrix[row][col] for col in combo] for row in combo]
        determinant = det3(submatrix)
        abs_determinant = abs(determinant)
        positive, negative, zero = inertia(submatrix)
        row_rank = rank3(submatrix)
        subform_rows.append(
            {
                "subform_id": subform_id,
                "a_restricted_index": combo[0],
                "b_restricted_index": combo[1],
                "c_restricted_index": combo[2],
                "a_source_atom": basis[combo[0]]["source_atom"],
                "b_source_atom": basis[combo[1]]["source_atom"],
                "c_source_atom": basis[combo[2]]["source_atom"],
                "rank": row_rank,
                "inertia_positive": positive,
                "inertia_negative": negative,
                "inertia_zero": zero,
                "det_sign": int(determinant > 0) - int(determinant < 0),
                "det_abs_digit_count": len(str(abs_determinant)),
                "det_abs_mod_1000000007": abs_determinant % 1_000_000_007,
                "det_abs_mod_1000000009": abs_determinant % 1_000_000_009,
                "nondegenerate_flag": int(row_rank == 3),
                "definite_spatial_flag": int((positive, negative, zero) in [(3, 0, 0), (0, 3, 0)]),
                "max_abs_det_flag": 0,
            }
        )
        determinant_rows.append(
            {
                "subform_id": subform_id,
                "determinant_exact": str(determinant),
            }
        )

    max_abs_det = max(abs(int(row["determinant_exact"])) for row in determinant_rows)
    max_subform_ids = [
        row["subform_id"]
        for row in determinant_rows
        if abs(int(row["determinant_exact"])) == max_abs_det
    ]
    for row in subform_rows:
        row["max_abs_det_flag"] = int(row["subform_id"] in max_subform_ids)

    rank_counts = {
        rank: sum(row["rank"] == rank for row in subform_rows) for rank in range(4)
    }
    positive_definite_count = sum(
        (row["inertia_positive"], row["inertia_negative"], row["inertia_zero"])
        == (3, 0, 0)
        for row in subform_rows
    )
    negative_definite_count = sum(
        (row["inertia_positive"], row["inertia_negative"], row["inertia_zero"])
        == (0, 3, 0)
        for row in subform_rows
    )
    inertia_210_count = sum(
        (row["inertia_positive"], row["inertia_negative"], row["inertia_zero"])
        == (2, 1, 0)
        for row in subform_rows
    )
    inertia_120_count = sum(
        (row["inertia_positive"], row["inertia_negative"], row["inertia_zero"])
        == (1, 2, 0)
        for row in subform_rows
    )
    nondegenerate_rows = [
        row for row in subform_rows if row["nondegenerate_flag"] == 1
    ]
    candidate_rows = [
        {
            "candidate_id": candidate_id,
            "subform_id": row["subform_id"],
            "a_restricted_index": row["a_restricted_index"],
            "b_restricted_index": row["b_restricted_index"],
            "c_restricted_index": row["c_restricted_index"],
            "a_source_atom": row["a_source_atom"],
            "b_source_atom": row["b_source_atom"],
            "c_source_atom": row["c_source_atom"],
            "inertia_positive": row["inertia_positive"],
            "inertia_negative": row["inertia_negative"],
            "det_sign": row["det_sign"],
            "det_abs_digit_count": row["det_abs_digit_count"],
            "det_abs_mod_1000000007": row["det_abs_mod_1000000007"],
            "det_abs_mod_1000000009": row["det_abs_mod_1000000009"],
            "max_abs_det_flag": row["max_abs_det_flag"],
            "definite_spatial_flag": row["definite_spatial_flag"],
        }
        for candidate_id, row in enumerate(nondegenerate_rows)
    ]

    selector_flag = int(long_sel["witness"]["summary"]["physical_selector_axiom_flag"])
    dim4_flag = int(dim4_gate["witness"]["summary"]["dim4_reduction_certified_flag"])
    canonical_flag = int(
        positive_definite_count + negative_definite_count > 0
        and selector_flag == 1
        and dim4_flag == 1
    )
    max_row = [row for row in subform_rows if row["max_abs_det_flag"] == 1][0]
    summary_rows = [
        {
            "summary_id": SUMMARY_CODES["principal_three_subform_inventory"],
            "summary_code": SUMMARY_CODES["principal_three_subform_inventory"],
            "subform_count": len(subform_rows),
            "rank3_count": rank_counts[3],
            "rank2_count": rank_counts[2],
            "rank1_count": rank_counts[1],
            "rank0_count": rank_counts[0],
            "positive_definite_count": positive_definite_count,
            "negative_definite_count": negative_definite_count,
            "inertia_210_count": inertia_210_count,
            "inertia_120_count": inertia_120_count,
        }
    ]
    obs = {
        "input_report_count": 3,
        "input_certified_count": int(certified(c59pk))
        + int(certified(long_sel))
        + int(certified(dim4_gate)),
        "restricted_dimension": dimension,
        "principal_three_subform_count": len(subform_rows),
        "rank3_subform_count": rank_counts[3],
        "rank2_subform_count": rank_counts[2],
        "rank1_subform_count": rank_counts[1],
        "rank0_subform_count": rank_counts[0],
        "positive_definite_count": positive_definite_count,
        "negative_definite_count": negative_definite_count,
        "definite_spatial_count": positive_definite_count + negative_definite_count,
        "inertia_210_count": inertia_210_count,
        "inertia_120_count": inertia_120_count,
        "unique_max_abs_det_flag": int(len(max_subform_ids) == 1),
        "max_abs_det_subform_id": max_subform_ids[0],
        "max_abs_det_inertia_positive": max_row["inertia_positive"],
        "max_abs_det_inertia_negative": max_row["inertia_negative"],
        "max_abs_det_digit_count": len(str(max_abs_det)),
        "max_abs_det_mod_1000000007": max_abs_det % 1_000_000_007,
        "physical_selector_axiom_flag": selector_flag,
        "dim4_reduction_certified_flag": dim4_flag,
        "canonical_three_spatial_selection_flag": canonical_flag,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["definite_spatial_three_subform"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["principal_three_search_exhaustive"],
            "decision_code": DECISION_CODES["principal_three_search_exhaustive"],
            "value": obs["principal_three_subform_count"],
            "certified_flag": int(obs["principal_three_subform_count"] == 816),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["nondegenerate_principal_three_exists"],
            "decision_code": DECISION_CODES["nondegenerate_principal_three_exists"],
            "value": obs["rank3_subform_count"],
            "certified_flag": int(obs["rank3_subform_count"] > 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["unique_max_volume_principal_three_exists"],
            "decision_code": DECISION_CODES[
                "unique_max_volume_principal_three_exists"
            ],
            "value": obs["unique_max_abs_det_flag"],
            "certified_flag": obs["unique_max_abs_det_flag"],
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["definite_spatial_principal_three_exists"],
            "decision_code": DECISION_CODES[
                "definite_spatial_principal_three_exists"
            ],
            "value": obs["definite_spatial_count"],
            "certified_flag": 0,
            "obstruction_flag": 1,
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
                "canonical_three_spatial_selection_certified"
            ],
            "decision_code": DECISION_CODES[
                "canonical_three_spatial_selection_certified"
            ],
            "value": canonical_flag,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["principal_three_subform_inventory"],
            "gap_code": GAP_CODES["principal_three_subform_inventory"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["definite_spatial_three_subform"],
            "gap_code": GAP_CODES["definite_spatial_three_subform"],
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
            "gap_id": GAP_CODES["canonical_three_spatial_selection"],
            "gap_code": GAP_CODES["canonical_three_spatial_selection"],
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
        "c59pk": c59pk,
        "long_sel": long_sel,
        "dim4_gate": dim4_gate,
        "subform_rows": subform_rows,
        "determinant_rows": determinant_rows,
        "candidate_rows": candidate_rows,
        "summary_rows": summary_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
    }


def determinant_csv(rows: list[dict[str, Any]]) -> str:
    lines = [",".join(DETERMINANT_COLUMNS)]
    lines.extend(f"{row['subform_id']},{row['determinant_exact']}" for row in rows)
    return "\n".join(lines) + "\n"


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    subform_table = table_from_rows(SUBFORM_COLUMNS, rows["subform_rows"])
    candidate_table = table_from_rows(CANDIDATE_COLUMNS, rows["candidate_rows"])
    summary_table = table_from_rows(SUMMARY_COLUMNS, rows["summary_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    determinant_text = determinant_csv(rows["determinant_rows"])
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "principal_search_exhaustive": obs["restricted_dimension"] == 18
        and obs["principal_three_subform_count"] == 816,
        "principal_inventory_exact": obs["rank3_subform_count"] == 11
        and obs["rank2_subform_count"] == 426
        and obs["rank0_subform_count"] == 379
        and obs["rank1_subform_count"] == 0,
        "nondegenerate_candidates_materialized": obs["inertia_210_count"] == 8
        and obs["inertia_120_count"] == 3
        and candidate_table.shape[0] == 11,
        "definite_spatial_principal_obstructed": obs["positive_definite_count"] == 0
        and obs["negative_definite_count"] == 0
        and obs["definite_spatial_count"] == 0,
        "canonical_selection_obstructed": obs["unique_max_abs_det_flag"] == 1
        and obs["physical_selector_axiom_flag"] == 0
        and obs["dim4_reduction_certified_flag"] == 0
        and obs["canonical_three_spatial_selection_flag"] == 0,
        "metric_physical_boundaries_preserved": obs["four_dimensional_metric_flag"]
        == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": subform_table.shape == (816, len(SUBFORM_COLUMNS))
        and candidate_table.shape == (11, len(CANDIDATE_COLUMNS))
        and summary_table.shape == (1, len(SUMMARY_COLUMNS))
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "principal_three_subform_search",
        "summary": {
            "restricted_dimension": obs["restricted_dimension"],
            "principal_three_subform_count": obs["principal_three_subform_count"],
            "rank3_subform_count": obs["rank3_subform_count"],
            "rank2_subform_count": obs["rank2_subform_count"],
            "rank0_subform_count": obs["rank0_subform_count"],
            "positive_definite_count": obs["positive_definite_count"],
            "negative_definite_count": obs["negative_definite_count"],
            "inertia_210_count": obs["inertia_210_count"],
            "inertia_120_count": obs["inertia_120_count"],
            "unique_max_abs_det_flag": obs["unique_max_abs_det_flag"],
            "max_abs_det_subform_id": obs["max_abs_det_subform_id"],
            "max_abs_det_inertia_positive": obs["max_abs_det_inertia_positive"],
            "max_abs_det_inertia_negative": obs["max_abs_det_inertia_negative"],
            "physical_selector_axiom_flag": obs["physical_selector_axiom_flag"],
            "canonical_three_spatial_selection_flag": obs[
                "canonical_three_spatial_selection_flag"
            ],
            "four_dimensional_metric_flag": obs["four_dimensional_metric_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "summary_code_map": {str(value): key for key, value in SUMMARY_CODES.items()},
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "subform_table_sha256": sha_array(subform_table),
        "subform_text_sha256": sha_text(csv_text(SUBFORM_COLUMNS, rows["subform_rows"])),
        "determinant_text_sha256": sha_text(determinant_text),
        "candidate_table_sha256": sha_array(candidate_table),
        "summary_table_sha256": sha_array(summary_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
    }
    c59s3 = {
        "schema": "long.c59s3@1",
        "object": "principal_three_subform_search",
        "status": STATUS if all(checks.values()) else "LONG_C59S3_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59s3.report@1",
        "status": c59s3["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59s3 exhaustively enumerates principal three-coordinate "
            "subforms of the 18D induced public-kernel form. It finds 11 "
            "nondegenerate principal triples and a unique maximum-volume "
            "triple, but no definite spatial principal triple and no certified "
            "physical selector axiom. Therefore the current boundary still "
            "does not certify a canonical three-spatial-rank selection."
        ),
        "stage_protocol": {
            "draft": "read long_c59pk, long_sel, and long_dim4_gate",
            "witness": "emit all 816 principal three-subform rows, exact determinant rows, nondegenerate candidates, summary, decisions, gaps, and observables",
            "coherence": "check rank/inertia counts, determinant max uniqueness, definite-spatial absence, selector absence, and metric exclusions",
            "closure": "certify principal three-subform inventory and the current-boundary spatial-selection obstruction",
            "emit": "write long_c59s3 artifacts and verifier hook",
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
            "c59s3": relpath(OUT_DIR / "c59s3.json"),
            "subform_csv": relpath(OUT_DIR / "subform.csv"),
            "determinant_csv": relpath(OUT_DIR / "determinant.csv"),
            "candidate_csv": relpath(OUT_DIR / "candidate.csv"),
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
                "all 816 principal three-coordinate subforms of the 18D restricted form are enumerated",
                "11 principal triples are nondegenerate",
                "the unique maximum-volume principal triple has inertia (2,1,0)",
                "no positive-definite or negative-definite principal three-subform exists",
                "the current certified selector boundary still lacks a physical selector axiom",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a definite three-spatial principal subform",
                "a canonical physical selector for a three-spatial-rank boundary",
                "an exhaustive search over all non-principal 3D linear subspaces",
                "a four-dimensional metric reduction",
                "a smooth Lorentzian metric",
                "a physical stress-energy tensor",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Decide the non-principal 3D question: either construct a selector "
            "for a definite 3-plane inside the 18D form, or certify that the "
            "current oracle only supplies principal-coordinate candidates."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59s3.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59s3.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59s3": c59s3,
        "subform_csv": csv_text(SUBFORM_COLUMNS, rows["subform_rows"]),
        "determinant_csv": determinant_text,
        "candidate_csv": csv_text(CANDIDATE_COLUMNS, rows["candidate_rows"]),
        "summary_csv": csv_text(SUMMARY_COLUMNS, rows["summary_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "subform_table": subform_table,
        "candidate_table": candidate_table,
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
    write_json(OUT_DIR / "c59s3.json", payloads["c59s3"])
    (OUT_DIR / "subform.csv").write_text(payloads["subform_csv"], encoding="utf-8")
    (OUT_DIR / "determinant.csv").write_text(
        payloads["determinant_csv"], encoding="utf-8"
    )
    (OUT_DIR / "candidate.csv").write_text(
        payloads["candidate_csv"], encoding="utf-8"
    )
    (OUT_DIR / "summary.csv").write_text(payloads["summary_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(payloads["decision_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        subform_table=payloads["subform_table"],
        candidate_table=payloads["candidate_table"],
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
