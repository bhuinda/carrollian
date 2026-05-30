from __future__ import annotations

import csv
import hashlib
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


THEOREM_ID = "long_c59q"
STATUS = "LONG_C59Q_GAUGE_NULL_QUOTIENT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59ST = PROOF_ROOT / "long_c59st" / "report.json"
LONG_C59ST_TENSOR = PROOF_ROOT / "long_c59st" / "tensor_entry.csv"
LONG_C59ST_KERNEL = PROOF_ROOT / "long_c59st" / "kernel.csv"
LONG_C59KT = PROOF_ROOT / "long_c59kt" / "report.json"
LONG_TIME_MAP_MATRIX = PROOF_ROOT / "long_time_map" / "matrix.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59q.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59q.py"

BASIS_COLUMNS = [
    "quotient_index",
    "source_atom",
    "pivot_atom",
    "source_kernel_value",
    "q_pub_value",
    "time_support_flag",
    "basis_flag",
]
QUOTIENT_ENTRY_COLUMNS = [
    "entry_id",
    "row_quotient_index",
    "col_quotient_index",
    "row_atom",
    "col_atom",
    "quotient_value",
    "diagonal_flag",
    "nonzero_flag",
]
INERTIA_COLUMNS = [
    "pivot_id",
    "pivot_type",
    "positive_increment",
    "negative_increment",
    "zero_increment",
    "pivot_sign",
    "remaining_dimension_before",
    "remaining_dimension_after",
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

DECISION_NAMES = [
    "gauge_null_mode_available",
    "quotient_basis_materialized",
    "quotient_form_nondegenerate",
    "exact_inertia_11_8_0",
    "quotient_dimension_matches_public_kernel_count",
    "induced_time_trace_survives",
    "public_kernel_boundary_identified",
    "one_plus_eighteen_quotient_split",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "gauge_null_quotient",
    "nondegenerate_19_form",
    "public_kernel_count_match",
    "public_kernel_boundary_identification",
    "induced_time_kernel_restriction",
    "four_dimensional_metric_reduction",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "ambient_dimension",
    "pivot_atom",
    "pivot_kernel_value",
    "gauge_kernel_support_count",
    "quotient_dimension",
    "quotient_entry_count",
    "active_quotient_pair_count",
    "quotient_rank",
    "quotient_nullity",
    "inertia_positive_count",
    "inertia_negative_count",
    "inertia_zero_count",
    "public_kernel_dimension",
    "time_rank",
    "quotient_dimension_matches_public_kernel_flag",
    "induced_q_pub_rank",
    "induced_q_pub_kernel_dimension",
    "induced_time_survives_flag",
    "public_kernel_boundary_identification_flag",
    "one_plus_eighteen_split_flag",
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
    return report.get("all_checks_pass") is True and "CERTIFIED" in str(
        report.get("status", "")
    )


def exact_rank(matrix: list[list[int]]) -> int:
    current = [[Fraction(value) for value in row] for row in matrix]
    row_count = len(current)
    col_count = len(current[0]) if current else 0
    pivot_row = 0
    for col in range(col_count):
        selected = None
        for row in range(pivot_row, row_count):
            if current[row][col] != 0:
                selected = row
                break
        if selected is None:
            continue
        current[pivot_row], current[selected] = current[selected], current[pivot_row]
        pivot = current[pivot_row][col]
        for j in range(col, col_count):
            current[pivot_row][j] /= pivot
        for row in range(row_count):
            if row == pivot_row or current[row][col] == 0:
                continue
            factor = current[row][col]
            for j in range(col, col_count):
                current[row][j] -= factor * current[pivot_row][j]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def exact_inertia(matrix: list[list[int]]) -> tuple[int, int, int, list[dict[str, int]]]:
    current = [[Fraction(value) for value in row] for row in matrix]
    positive = 0
    negative = 0
    zero = 0
    rows: list[dict[str, int]] = []
    pivot_id = 0
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
            sign = 1 if pivot > 0 else -1
            positive += int(sign > 0)
            negative += int(sign < 0)
            rows.append(
                {
                    "pivot_id": pivot_id,
                    "pivot_type": 1,
                    "positive_increment": int(sign > 0),
                    "negative_increment": int(sign < 0),
                    "zero_increment": 0,
                    "pivot_sign": sign,
                    "remaining_dimension_before": dimension,
                    "remaining_dimension_after": dimension - 1,
                }
            )
            pivot_id += 1
            if dimension == 1:
                current = []
                continue
            column = [current[row][0] for row in range(1, dimension)]
            current = [
                [
                    current[row][col]
                    - column[row - 1] * column[col - 1] / pivot
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
            rows.append(
                {
                    "pivot_id": pivot_id,
                    "pivot_type": 0,
                    "positive_increment": 0,
                    "negative_increment": 0,
                    "zero_increment": dimension,
                    "pivot_sign": 0,
                    "remaining_dimension_before": dimension,
                    "remaining_dimension_after": 0,
                }
            )
            break

        order = [pair[0], pair[1]] + [
            index for index in range(dimension) if index not in pair
        ]
        current = [[current[row][col] for col in order] for row in order]
        off_diagonal = current[0][1]
        sign = 1 if off_diagonal > 0 else -1
        positive += 1
        negative += 1
        rows.append(
            {
                "pivot_id": pivot_id,
                "pivot_type": 2,
                "positive_increment": 1,
                "negative_increment": 1,
                "zero_increment": 0,
                "pivot_sign": sign,
                "remaining_dimension_before": dimension,
                "remaining_dimension_after": dimension - 2,
            }
        )
        pivot_id += 1
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
    return positive, negative, zero, rows


def q_pub_vector(matrix_rows: list[dict[str, int]]) -> list[int]:
    q_pub = [0] * 20
    for row in matrix_rows:
        if row["matrix_code"] == 1:
            q_pub[row["column_index"]] = row["value"]
    return q_pub


def build_rows() -> dict[str, Any]:
    c59st = load_json(LONG_C59ST)
    c59kt = load_json(LONG_C59KT)
    tensor_rows = read_csv_int(LONG_C59ST_TENSOR)
    kernel_rows = read_csv_int(LONG_C59ST_KERNEL)
    matrix_rows = read_csv_int(LONG_TIME_MAP_MATRIX)
    q_pub = q_pub_vector(matrix_rows)

    ambient_dimension = 20
    tensor = [[0 for _ in range(ambient_dimension)] for _ in range(ambient_dimension)]
    for row in tensor_rows:
        tensor[row["row_atom"]][row["col_atom"]] = row["symmetric_flux_scaled"]
    kernel = [
        row["kernel_value"]
        for row in sorted(kernel_rows, key=lambda row: row["atom_id"])
    ]
    support = [atom for atom, value in enumerate(kernel) if value != 0]
    pivot_atom = max(support, key=lambda atom: (abs(kernel[atom]), atom))
    quotient_atoms = [atom for atom in range(ambient_dimension) if atom != pivot_atom]
    quotient = [[tensor[row][col] for col in quotient_atoms] for row in quotient_atoms]
    quotient_rank = exact_rank(quotient)
    positive, negative, inertia_zero, inertia_rows = exact_inertia(quotient)
    induced_q = [q_pub[atom] for atom in quotient_atoms]
    induced_q_rank = int(any(value != 0 for value in induced_q))
    induced_q_kernel_dim = len(quotient_atoms) - induced_q_rank

    basis_rows = [
        {
            "quotient_index": index,
            "source_atom": atom,
            "pivot_atom": pivot_atom,
            "source_kernel_value": kernel[atom],
            "q_pub_value": q_pub[atom],
            "time_support_flag": int(q_pub[atom] != 0),
            "basis_flag": 1,
        }
        for index, atom in enumerate(quotient_atoms)
    ]
    quotient_entry_rows = []
    for row_index, row_atom in enumerate(quotient_atoms):
        for col_index, col_atom in enumerate(quotient_atoms):
            value = quotient[row_index][col_index]
            quotient_entry_rows.append(
                {
                    "entry_id": row_index * len(quotient_atoms) + col_index,
                    "row_quotient_index": row_index,
                    "col_quotient_index": col_index,
                    "row_atom": row_atom,
                    "col_atom": col_atom,
                    "quotient_value": value,
                    "diagonal_flag": int(row_index == col_index),
                    "nonzero_flag": int(value != 0),
                }
            )

    public_kernel_dimension = int(c59st["witness"]["summary"]["public_kernel_dimension"])
    time_rank = int(c59st["witness"]["summary"]["time_rank"])
    quotient_nullity = len(quotient_atoms) - quotient_rank
    quotient_dim_match = int(len(quotient_atoms) == public_kernel_dimension)
    induced_time_survives = int(induced_q_rank == 1)
    public_kernel_identification = int(
        quotient_dim_match == 1 and induced_q_rank == 0
    )
    one_plus_eighteen = int(
        len(quotient_atoms) == 19
        and induced_q_rank == 1
        and induced_q_kernel_dim == 18
    )
    active_pairs = sum(
        quotient[row][col] != 0
        for row in range(len(quotient_atoms))
        for col in range(row + 1, len(quotient_atoms))
    )
    obs = {
        "input_report_count": 2,
        "input_certified_count": int(certified(c59st)) + int(certified(c59kt)),
        "ambient_dimension": ambient_dimension,
        "pivot_atom": pivot_atom,
        "pivot_kernel_value": kernel[pivot_atom],
        "gauge_kernel_support_count": len(support),
        "quotient_dimension": len(quotient_atoms),
        "quotient_entry_count": len(quotient_entry_rows),
        "active_quotient_pair_count": active_pairs,
        "quotient_rank": quotient_rank,
        "quotient_nullity": quotient_nullity,
        "inertia_positive_count": positive,
        "inertia_negative_count": negative,
        "inertia_zero_count": inertia_zero,
        "public_kernel_dimension": public_kernel_dimension,
        "time_rank": time_rank,
        "quotient_dimension_matches_public_kernel_flag": quotient_dim_match,
        "induced_q_pub_rank": induced_q_rank,
        "induced_q_pub_kernel_dimension": induced_q_kernel_dim,
        "induced_time_survives_flag": induced_time_survives,
        "public_kernel_boundary_identification_flag": public_kernel_identification,
        "one_plus_eighteen_split_flag": one_plus_eighteen,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["induced_time_kernel_restriction"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["gauge_null_mode_available"],
            "decision_code": DECISION_CODES["gauge_null_mode_available"],
            "value": len(support),
            "certified_flag": int(len(support) == 2),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["quotient_basis_materialized"],
            "decision_code": DECISION_CODES["quotient_basis_materialized"],
            "value": len(quotient_atoms),
            "certified_flag": int(len(quotient_atoms) == 19),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["quotient_form_nondegenerate"],
            "decision_code": DECISION_CODES["quotient_form_nondegenerate"],
            "value": quotient_rank,
            "certified_flag": int(quotient_rank == 19 and quotient_nullity == 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["exact_inertia_11_8_0"],
            "decision_code": DECISION_CODES["exact_inertia_11_8_0"],
            "value": positive * 100 + negative * 10 + inertia_zero,
            "certified_flag": int(positive == 11 and negative == 8 and inertia_zero == 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES[
                "quotient_dimension_matches_public_kernel_count"
            ],
            "decision_code": DECISION_CODES[
                "quotient_dimension_matches_public_kernel_count"
            ],
            "value": quotient_dim_match,
            "certified_flag": quotient_dim_match,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["induced_time_trace_survives"],
            "decision_code": DECISION_CODES["induced_time_trace_survives"],
            "value": induced_time_survives,
            "certified_flag": induced_time_survives,
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["public_kernel_boundary_identified"],
            "decision_code": DECISION_CODES["public_kernel_boundary_identified"],
            "value": public_kernel_identification,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["one_plus_eighteen_quotient_split"],
            "decision_code": DECISION_CODES["one_plus_eighteen_quotient_split"],
            "value": one_plus_eighteen,
            "certified_flag": one_plus_eighteen,
            "obstruction_flag": 0,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["gauge_null_quotient"],
            "gap_code": GAP_CODES["gauge_null_quotient"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["nondegenerate_19_form"],
            "gap_code": GAP_CODES["nondegenerate_19_form"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["public_kernel_count_match"],
            "gap_code": GAP_CODES["public_kernel_count_match"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["public_kernel_boundary_identification"],
            "gap_code": GAP_CODES["public_kernel_boundary_identification"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["induced_time_kernel_restriction"],
            "gap_code": GAP_CODES["induced_time_kernel_restriction"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 0,
            "next_flag": 1,
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
        "c59st": c59st,
        "c59kt": c59kt,
        "basis_rows": basis_rows,
        "quotient_entry_rows": quotient_entry_rows,
        "inertia_rows": inertia_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "quotient_matrix": quotient,
        "induced_q": induced_q,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    basis_table = table_from_rows(BASIS_COLUMNS, rows["basis_rows"])
    quotient_entry_table = table_from_rows(
        QUOTIENT_ENTRY_COLUMNS, rows["quotient_entry_rows"]
    )
    inertia_table = table_from_rows(INERTIA_COLUMNS, rows["inertia_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    quotient_matrix = np.asarray(rows["quotient_matrix"], dtype=np.int64)
    induced_q_table = np.asarray([rows["induced_q"]], dtype=np.int64)
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "quotient_basis_exact": obs["ambient_dimension"] == 20
        and obs["gauge_kernel_support_count"] == 2
        and obs["quotient_dimension"] == 19
        and obs["pivot_kernel_value"] != 0,
        "quotient_form_nondegenerate": obs["quotient_rank"] == 19
        and obs["quotient_nullity"] == 0
        and obs["inertia_positive_count"] == 11
        and obs["inertia_negative_count"] == 8
        and obs["inertia_zero_count"] == 0,
        "public_kernel_boundary_retest": obs[
            "quotient_dimension_matches_public_kernel_flag"
        ]
        == 1
        and obs["induced_q_pub_rank"] == 1
        and obs["induced_q_pub_kernel_dimension"] == 18
        and obs["induced_time_survives_flag"] == 1
        and obs["public_kernel_boundary_identification_flag"] == 0,
        "metric_physical_boundaries_preserved": obs["one_plus_eighteen_split_flag"]
        == 1
        and obs["four_dimensional_metric_flag"] == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": basis_table.shape == (19, len(BASIS_COLUMNS))
        and quotient_entry_table.shape == (361, len(QUOTIENT_ENTRY_COLUMNS))
        and inertia_table.shape[1] == len(INERTIA_COLUMNS)
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS))
        and quotient_matrix.shape == (19, 19)
        and induced_q_table.shape == (1, 19),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c59x_gauge_null_quotient",
        "summary": {
            "pivot_atom": obs["pivot_atom"],
            "pivot_kernel_value": obs["pivot_kernel_value"],
            "quotient_dimension": obs["quotient_dimension"],
            "quotient_rank": obs["quotient_rank"],
            "quotient_nullity": obs["quotient_nullity"],
            "inertia_positive_count": obs["inertia_positive_count"],
            "inertia_negative_count": obs["inertia_negative_count"],
            "inertia_zero_count": obs["inertia_zero_count"],
            "public_kernel_dimension": obs["public_kernel_dimension"],
            "time_rank": obs["time_rank"],
            "quotient_dimension_matches_public_kernel_flag": obs[
                "quotient_dimension_matches_public_kernel_flag"
            ],
            "induced_q_pub_rank": obs["induced_q_pub_rank"],
            "induced_q_pub_kernel_dimension": obs[
                "induced_q_pub_kernel_dimension"
            ],
            "induced_time_survives_flag": obs["induced_time_survives_flag"],
            "public_kernel_boundary_identification_flag": obs[
                "public_kernel_boundary_identification_flag"
            ],
            "one_plus_eighteen_split_flag": obs["one_plus_eighteen_split_flag"],
            "four_dimensional_metric_flag": obs["four_dimensional_metric_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "decision_code_map": {
            str(value): key for key, value in DECISION_CODES.items()
        },
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "basis_table_sha256": sha_array(basis_table),
        "basis_text_sha256": sha_text(csv_text(BASIS_COLUMNS, rows["basis_rows"])),
        "quotient_entry_table_sha256": sha_array(quotient_entry_table),
        "quotient_entry_text_sha256": sha_text(
            csv_text(QUOTIENT_ENTRY_COLUMNS, rows["quotient_entry_rows"])
        ),
        "inertia_table_sha256": sha_array(inertia_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "quotient_matrix_sha256": sha_array(quotient_matrix),
        "induced_q_table_sha256": sha_array(induced_q_table),
    }
    c59q = {
        "schema": "long.c59q@1",
        "object": "c59x_gauge_null_quotient",
        "status": STATUS if all(checks.values()) else "LONG_C59Q_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59q.report@1",
        "status": c59q["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59q quotients the finite symmetric stress candidate by the "
            "certified gauge-null mode. The induced 19-dimensional form is "
            "nondegenerate with exact inertia (11,8,0). Its dimension matches "
            "the public-kernel count, but q_pub still has rank 1 on the "
            "quotient, so the quotient is a 1+18 split rather than the public "
            "kernel boundary itself."
        ),
        "stage_protocol": {
            "draft": "read long_c59st tensor/kernel and long_c59kt gauge-null decision",
            "witness": "emit quotient basis, 19x19 form entries, exact inertia pivots, decisions, gaps, and observables",
            "coherence": "check nondegeneracy, inertia, induced q_pub rank, and public-kernel boundary obstruction",
            "closure": "certify the gauge-null quotient and preserve the induced public-time seam",
            "emit": "write long_c59q artifacts and verifier hook",
        },
        "inputs": {
            "long_c59st": input_entry(
                LONG_C59ST,
                {
                    "status": rows["c59st"].get("status"),
                    "certificate_sha256": rows["c59st"].get("certificate_sha256"),
                },
            ),
            "long_c59st_tensor": input_entry(LONG_C59ST_TENSOR),
            "long_c59st_kernel": input_entry(LONG_C59ST_KERNEL),
            "long_c59kt": input_entry(
                LONG_C59KT,
                {
                    "status": rows["c59kt"].get("status"),
                    "certificate_sha256": rows["c59kt"].get("certificate_sha256"),
                },
            ),
            "long_time_map_matrix": input_entry(LONG_TIME_MAP_MATRIX),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59q": relpath(OUT_DIR / "c59q.json"),
            "basis_csv": relpath(OUT_DIR / "basis.csv"),
            "quotient_entry_csv": relpath(OUT_DIR / "quotient_entry.csv"),
            "inertia_csv": relpath(OUT_DIR / "inertia.csv"),
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
                "a concrete quotient by the certified gauge-null stress mode",
                "a nondegenerate 19-dimensional finite quotient form",
                "exact quotient inertia (11,8,0)",
                "the quotient dimension matches the public-kernel count 19",
                "q_pub descends to the quotient with rank 1, leaving a 1+18 split",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "identification of the quotient form with the public-kernel boundary itself",
                "restriction of the quotient form to the induced q_pub kernel",
                "a four-dimensional metric reduction",
                "a smooth Lorentzian metric",
                "a physical stress-energy tensor",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Restrict the nondegenerate quotient form to the induced q_pub "
            "kernel and test the resulting 18-dimensional public-kernel form."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59q.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59q.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59q": c59q,
        "basis_csv": csv_text(BASIS_COLUMNS, rows["basis_rows"]),
        "quotient_entry_csv": csv_text(
            QUOTIENT_ENTRY_COLUMNS, rows["quotient_entry_rows"]
        ),
        "inertia_csv": csv_text(INERTIA_COLUMNS, rows["inertia_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "basis_table": basis_table,
        "quotient_entry_table": quotient_entry_table,
        "inertia_table": inertia_table,
        "decision_table": decision_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "quotient_matrix": quotient_matrix,
        "induced_q_table": induced_q_table,
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
    write_json(OUT_DIR / "c59q.json", payloads["c59q"])
    (OUT_DIR / "basis.csv").write_text(payloads["basis_csv"], encoding="utf-8")
    (OUT_DIR / "quotient_entry.csv").write_text(
        payloads["quotient_entry_csv"], encoding="utf-8"
    )
    (OUT_DIR / "inertia.csv").write_text(payloads["inertia_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(payloads["decision_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        basis_table=payloads["basis_table"],
        quotient_entry_table=payloads["quotient_entry_table"],
        inertia_table=payloads["inertia_table"],
        decision_table=payloads["decision_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
        quotient_matrix=payloads["quotient_matrix"],
        induced_q_table=payloads["induced_q_table"],
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
