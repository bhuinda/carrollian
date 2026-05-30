from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction
from math import gcd
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


THEOREM_ID = "long_c59st"
STATUS = "LONG_C59ST_SYMMETRIC_STRESS_CANDIDATE_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59CF = PROOF_ROOT / "long_c59cf" / "report.json"
LONG_C59CF_CORRECTED_EDGE = PROOF_ROOT / "long_c59cf" / "corrected_edge.csv"
LONG_C59CF_CORRECTED_NODE = PROOF_ROOT / "long_c59cf" / "corrected_node.csv"
LONG_METRIC_RANK_GATE = PROOF_ROOT / "long_metric_rank_gate" / "report.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59st.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59st.py"

TENSOR_ENTRY_COLUMNS = [
    "entry_id",
    "row_atom",
    "col_atom",
    "directed_flux_scaled",
    "transpose_flux_scaled",
    "symmetric_flux_scaled",
    "diagonal_flag",
    "nonzero_flag",
]
PAIR_COLUMNS = [
    "pair_id",
    "atom_i",
    "atom_j",
    "forward_flux_scaled",
    "reverse_flux_scaled",
    "symmetric_flux_scaled",
    "abs_symmetric_flux_scaled",
    "directed_support_count",
    "symmetric_nonzero_flag",
]
KERNEL_COLUMNS = [
    "atom_id",
    "kernel_value",
    "kernel_nonzero_flag",
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
METRIC_COLUMNS = [
    "metric_row_id",
    "metric_code",
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

METRIC_NAMES = [
    "symmetric_stress_candidate_materialized",
    "exact_rank_19_nullity_1",
    "exact_inertia_11_8_1",
    "conserved_current_input",
    "rank_matches_public_kernel_count",
    "nullity_matches_time_count",
    "kernel_time_trace_identification",
    "lorentzian_signature_certified",
    "four_dimensional_metric_certified",
    "physical_stress_energy_certified",
    "thermal_gravity_derivation_certified",
]
METRIC_CODES = {name: index for index, name in enumerate(METRIC_NAMES)}

GAP_NAMES = [
    "finite_symmetric_stress_candidate",
    "exact_rank_inertia",
    "one_plus_nineteen_count_match",
    "canonical_kernel_time_identification",
    "four_dimensional_metric_reduction",
    "physical_stress_energy_lift",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "stress_node_count",
    "directed_edge_count",
    "tensor_entry_count",
    "pair_row_count",
    "active_pair_count",
    "symmetric_tensor_flag",
    "diagonal_zero_count",
    "conserved_node_count",
    "tensor_rank",
    "tensor_nullity",
    "inertia_positive_count",
    "inertia_negative_count",
    "inertia_zero_count",
    "public_kernel_dimension",
    "time_rank",
    "rank_matches_public_kernel_flag",
    "nullity_matches_time_rank_flag",
    "kernel_support_count",
    "kernel_time_identification_flag",
    "lorentzian_signature_flag",
    "four_dimensional_metric_flag",
    "finite_stress_candidate_flag",
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


def exact_rank_and_kernel(matrix: list[list[int]]) -> tuple[int, list[int]]:
    rows = [[Fraction(value) for value in row] for row in matrix]
    row_count = len(rows)
    col_count = len(rows[0]) if rows else 0
    pivot_columns: list[int] = []
    pivot_row = 0
    for col in range(col_count):
        selected = None
        for row in range(pivot_row, row_count):
            if rows[row][col] != 0:
                selected = row
                break
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        pivot = rows[pivot_row][col]
        for j in range(col, col_count):
            rows[pivot_row][j] /= pivot
        for row in range(row_count):
            if row == pivot_row or rows[row][col] == 0:
                continue
            factor = rows[row][col]
            for j in range(col, col_count):
                rows[row][j] -= factor * rows[pivot_row][j]
        pivot_columns.append(col)
        pivot_row += 1
        if pivot_row == row_count:
            break

    free_columns = [col for col in range(col_count) if col not in pivot_columns]
    if not free_columns:
        return len(pivot_columns), [0] * col_count
    free_col = free_columns[0]
    kernel = [Fraction(0) for _ in range(col_count)]
    kernel[free_col] = Fraction(1)
    for row, col in enumerate(pivot_columns):
        kernel[col] = -rows[row][free_col]

    scale = 1
    for value in kernel:
        scale = scale * value.denominator // gcd(scale, value.denominator)
    integers = [int(value * scale) for value in kernel]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    if divisor:
        integers = [value // divisor for value in integers]
    for value in integers:
        if value != 0:
            if value < 0:
                integers = [-item for item in integers]
            break
    return len(pivot_columns), integers


def exact_inertia(matrix: list[list[int]]) -> tuple[int, int, int, list[dict[str, int]]]:
    current = [[Fraction(value) for value in row] for row in matrix]
    positive = 0
    negative = 0
    zero = 0
    pivot_rows: list[dict[str, int]] = []
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
            pivot_rows.append(
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
            reduced = []
            for row in range(1, dimension):
                reduced_row = []
                for col in range(1, dimension):
                    reduced_row.append(
                        current[row][col] - column[row - 1] * column[col - 1] / pivot
                    )
                reduced.append(reduced_row)
            current = reduced
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
            pivot_rows.append(
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
        pivot_rows.append(
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
        reduced = []
        for row in range(dimension - 2):
            reduced_row = []
            for col in range(dimension - 2):
                reduced_row.append(
                    corner[row][col]
                    - (
                        side[row][0] * side[col][1]
                        + side[row][1] * side[col][0]
                    )
                    / off_diagonal
                )
            reduced.append(reduced_row)
        current = reduced
    return positive, negative, zero, pivot_rows


def build_rows() -> dict[str, Any]:
    c59cf = load_json(LONG_C59CF)
    metric_gate = load_json(LONG_METRIC_RANK_GATE)
    corrected_edges = read_csv_int(LONG_C59CF_CORRECTED_EDGE)
    corrected_nodes = read_csv_int(LONG_C59CF_CORRECTED_NODE)

    node_count = 20
    directed = [[0 for _ in range(node_count)] for _ in range(node_count)]
    for row in corrected_edges:
        directed[row["source_atom"]][row["target_atom"]] += row[
            "corrected_flux_scaled"
        ]
    symmetric = [
        [directed[row][col] + directed[col][row] for col in range(node_count)]
        for row in range(node_count)
    ]
    tensor_entry_rows = []
    for row in range(node_count):
        for col in range(node_count):
            value = symmetric[row][col]
            tensor_entry_rows.append(
                {
                    "entry_id": row * node_count + col,
                    "row_atom": row,
                    "col_atom": col,
                    "directed_flux_scaled": directed[row][col],
                    "transpose_flux_scaled": directed[col][row],
                    "symmetric_flux_scaled": value,
                    "diagonal_flag": int(row == col),
                    "nonzero_flag": int(value != 0),
                }
            )

    pair_rows = []
    pair_id = 0
    for atom_i in range(node_count):
        for atom_j in range(atom_i + 1, node_count):
            forward = directed[atom_i][atom_j]
            reverse = directed[atom_j][atom_i]
            value = forward + reverse
            pair_rows.append(
                {
                    "pair_id": pair_id,
                    "atom_i": atom_i,
                    "atom_j": atom_j,
                    "forward_flux_scaled": forward,
                    "reverse_flux_scaled": reverse,
                    "symmetric_flux_scaled": value,
                    "abs_symmetric_flux_scaled": abs(value),
                    "directed_support_count": int(forward != 0) + int(reverse != 0),
                    "symmetric_nonzero_flag": int(value != 0),
                }
            )
            pair_id += 1

    rank, kernel = exact_rank_and_kernel(symmetric)
    positive, negative, inertia_zero, inertia_rows = exact_inertia(symmetric)
    kernel_rows = [
        {
            "atom_id": atom,
            "kernel_value": value,
            "kernel_nonzero_flag": int(value != 0),
        }
        for atom, value in enumerate(kernel)
    ]

    metric_summary = metric_gate["witness"]["summary"]
    public_kernel = int(metric_summary["public_kernel_dimension"])
    time_rank = int(metric_summary["time_rank"])
    tensor_nullity = node_count - rank
    conserved_node_count = sum(
        row["corrected_local_conserved_flag"] for row in corrected_nodes
    )
    obs = {
        "input_report_count": 2,
        "input_certified_count": int(certified(c59cf)) + int(certified(metric_gate)),
        "stress_node_count": node_count,
        "directed_edge_count": len(corrected_edges),
        "tensor_entry_count": len(tensor_entry_rows),
        "pair_row_count": len(pair_rows),
        "active_pair_count": sum(row["symmetric_nonzero_flag"] for row in pair_rows),
        "symmetric_tensor_flag": int(
            all(symmetric[row][col] == symmetric[col][row] for row in range(node_count) for col in range(node_count))
        ),
        "diagonal_zero_count": sum(int(symmetric[index][index] == 0) for index in range(node_count)),
        "conserved_node_count": conserved_node_count,
        "tensor_rank": rank,
        "tensor_nullity": tensor_nullity,
        "inertia_positive_count": positive,
        "inertia_negative_count": negative,
        "inertia_zero_count": inertia_zero,
        "public_kernel_dimension": public_kernel,
        "time_rank": time_rank,
        "rank_matches_public_kernel_flag": int(rank == public_kernel),
        "nullity_matches_time_rank_flag": int(tensor_nullity == time_rank),
        "kernel_support_count": sum(row["kernel_nonzero_flag"] for row in kernel_rows),
        "kernel_time_identification_flag": 0,
        "lorentzian_signature_flag": 0,
        "four_dimensional_metric_flag": 0,
        "finite_stress_candidate_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["canonical_kernel_time_identification"],
    }

    metric_rows = [
        {
            "metric_row_id": METRIC_CODES["symmetric_stress_candidate_materialized"],
            "metric_code": METRIC_CODES["symmetric_stress_candidate_materialized"],
            "value": obs["finite_stress_candidate_flag"],
            "certified_flag": obs["finite_stress_candidate_flag"],
            "obstruction_flag": 0,
        },
        {
            "metric_row_id": METRIC_CODES["exact_rank_19_nullity_1"],
            "metric_code": METRIC_CODES["exact_rank_19_nullity_1"],
            "value": obs["tensor_rank"],
            "certified_flag": int(rank == 19 and tensor_nullity == 1),
            "obstruction_flag": 0,
        },
        {
            "metric_row_id": METRIC_CODES["exact_inertia_11_8_1"],
            "metric_code": METRIC_CODES["exact_inertia_11_8_1"],
            "value": positive * 100 + negative * 10 + inertia_zero,
            "certified_flag": int(positive == 11 and negative == 8 and inertia_zero == 1),
            "obstruction_flag": 0,
        },
        {
            "metric_row_id": METRIC_CODES["conserved_current_input"],
            "metric_code": METRIC_CODES["conserved_current_input"],
            "value": conserved_node_count,
            "certified_flag": int(conserved_node_count == node_count),
            "obstruction_flag": 0,
        },
        {
            "metric_row_id": METRIC_CODES["rank_matches_public_kernel_count"],
            "metric_code": METRIC_CODES["rank_matches_public_kernel_count"],
            "value": obs["rank_matches_public_kernel_flag"],
            "certified_flag": obs["rank_matches_public_kernel_flag"],
            "obstruction_flag": 0,
        },
        {
            "metric_row_id": METRIC_CODES["nullity_matches_time_count"],
            "metric_code": METRIC_CODES["nullity_matches_time_count"],
            "value": obs["nullity_matches_time_rank_flag"],
            "certified_flag": obs["nullity_matches_time_rank_flag"],
            "obstruction_flag": 0,
        },
        {
            "metric_row_id": METRIC_CODES["kernel_time_trace_identification"],
            "metric_code": METRIC_CODES["kernel_time_trace_identification"],
            "value": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "metric_row_id": METRIC_CODES["lorentzian_signature_certified"],
            "metric_code": METRIC_CODES["lorentzian_signature_certified"],
            "value": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "metric_row_id": METRIC_CODES["four_dimensional_metric_certified"],
            "metric_code": METRIC_CODES["four_dimensional_metric_certified"],
            "value": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "metric_row_id": METRIC_CODES["physical_stress_energy_certified"],
            "metric_code": METRIC_CODES["physical_stress_energy_certified"],
            "value": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "metric_row_id": METRIC_CODES["thermal_gravity_derivation_certified"],
            "metric_code": METRIC_CODES["thermal_gravity_derivation_certified"],
            "value": 0,
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["finite_symmetric_stress_candidate"],
            "gap_code": GAP_CODES["finite_symmetric_stress_candidate"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["exact_rank_inertia"],
            "gap_code": GAP_CODES["exact_rank_inertia"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["one_plus_nineteen_count_match"],
            "gap_code": GAP_CODES["one_plus_nineteen_count_match"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["canonical_kernel_time_identification"],
            "gap_code": GAP_CODES["canonical_kernel_time_identification"],
            "certified_flag": 0,
            "open_flag": 1,
            "obstruction_flag": 1,
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
            "gap_id": GAP_CODES["physical_stress_energy_lift"],
            "gap_code": GAP_CODES["physical_stress_energy_lift"],
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
        "c59cf": c59cf,
        "metric_gate": metric_gate,
        "tensor_entry_rows": tensor_entry_rows,
        "pair_rows": pair_rows,
        "kernel_rows": kernel_rows,
        "inertia_rows": inertia_rows,
        "metric_rows": metric_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "symmetric_matrix": symmetric,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    tensor_entry_table = table_from_rows(
        TENSOR_ENTRY_COLUMNS, rows["tensor_entry_rows"]
    )
    pair_table = table_from_rows(PAIR_COLUMNS, rows["pair_rows"])
    kernel_table = table_from_rows(KERNEL_COLUMNS, rows["kernel_rows"])
    inertia_table = table_from_rows(INERTIA_COLUMNS, rows["inertia_rows"])
    metric_table = table_from_rows(METRIC_COLUMNS, rows["metric_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    symmetric_matrix = np.asarray(rows["symmetric_matrix"], dtype=np.int64)
    obs = rows["obs"]
    checks = {
        "input_reports_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "symmetric_tensor_materialized": obs["tensor_entry_count"] == 400
        and obs["pair_row_count"] == 190
        and obs["active_pair_count"] == 40
        and obs["symmetric_tensor_flag"] == 1
        and obs["diagonal_zero_count"] == 20,
        "conserved_current_input_exact": obs["conserved_node_count"] == 20,
        "exact_rank_inertia": obs["tensor_rank"] == 19
        and obs["tensor_nullity"] == 1
        and obs["inertia_positive_count"] == 11
        and obs["inertia_negative_count"] == 8
        and obs["inertia_zero_count"] == 1,
        "one_plus_nineteen_count_match": obs["public_kernel_dimension"] == 19
        and obs["time_rank"] == 1
        and obs["rank_matches_public_kernel_flag"] == 1
        and obs["nullity_matches_time_rank_flag"] == 1,
        "kernel_boundary_explicit": obs["kernel_support_count"] == 2
        and obs["kernel_time_identification_flag"] == 0,
        "metric_physical_boundaries_preserved": obs["lorentzian_signature_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0
        and obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": tensor_entry_table.shape
        == (400, len(TENSOR_ENTRY_COLUMNS))
        and pair_table.shape == (190, len(PAIR_COLUMNS))
        and kernel_table.shape == (20, len(KERNEL_COLUMNS))
        and inertia_table.shape[1] == len(INERTIA_COLUMNS)
        and metric_table.shape == (len(METRIC_CODES), len(METRIC_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS))
        and symmetric_matrix.shape == (20, 20),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c59x_symmetric_stress_candidate",
        "summary": {
            "stress_node_count": obs["stress_node_count"],
            "directed_edge_count": obs["directed_edge_count"],
            "tensor_entry_count": obs["tensor_entry_count"],
            "active_pair_count": obs["active_pair_count"],
            "conserved_node_count": obs["conserved_node_count"],
            "tensor_rank": obs["tensor_rank"],
            "tensor_nullity": obs["tensor_nullity"],
            "inertia_positive_count": obs["inertia_positive_count"],
            "inertia_negative_count": obs["inertia_negative_count"],
            "inertia_zero_count": obs["inertia_zero_count"],
            "public_kernel_dimension": obs["public_kernel_dimension"],
            "time_rank": obs["time_rank"],
            "rank_matches_public_kernel_flag": obs[
                "rank_matches_public_kernel_flag"
            ],
            "nullity_matches_time_rank_flag": obs[
                "nullity_matches_time_rank_flag"
            ],
            "kernel_support_count": obs["kernel_support_count"],
            "kernel_time_identification_flag": obs[
                "kernel_time_identification_flag"
            ],
            "lorentzian_signature_flag": obs["lorentzian_signature_flag"],
            "four_dimensional_metric_flag": obs["four_dimensional_metric_flag"],
            "physical_stress_energy_flag": obs["physical_stress_energy_flag"],
            "smooth_metric_flag": obs["smooth_metric_flag"],
            "thermal_gravity_flag": obs["thermal_gravity_flag"],
        },
        "metric_code_map": {str(value): key for key, value in METRIC_CODES.items()},
        "gap_code_map": {str(value): key for key, value in GAP_CODES.items()},
        "observable_code_map": {str(value): key for key, value in OBS_CODES.items()},
        "tensor_entry_table_sha256": sha_array(tensor_entry_table),
        "tensor_entry_text_sha256": sha_text(
            csv_text(TENSOR_ENTRY_COLUMNS, rows["tensor_entry_rows"])
        ),
        "pair_table_sha256": sha_array(pair_table),
        "kernel_table_sha256": sha_array(kernel_table),
        "inertia_table_sha256": sha_array(inertia_table),
        "metric_table_sha256": sha_array(metric_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "symmetric_matrix_sha256": sha_array(symmetric_matrix),
    }
    c59st = {
        "schema": "long.c59st@1",
        "object": "c59x_symmetric_stress_candidate",
        "status": STATUS if all(checks.values()) else "LONG_C59ST_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59st.report@1",
        "status": c59st["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59st symmetrizes the conserved directed edge current from "
            "long_c59cf into a finite 20x20 stress candidate. The candidate "
            "has exact rank 19, nullity 1, and exact inertia (11,8,1), matching "
            "the certified 1+19 count boundary but not identifying its null "
            "direction with the public time trace."
        ),
        "stage_protocol": {
            "draft": "read long_c59cf corrected current and the metric rank gate",
            "witness": "emit tensor entries, node-pair rows, exact kernel vector, inertia pivots, metric decisions, gaps, and observables",
            "coherence": "check symmetry, conservation, exact rank/inertia, 1+19 count match, and open metric boundaries",
            "closure": "certify a finite symmetric stress candidate while preserving the kernel/time identification gap",
            "emit": "write long_c59st artifacts and verifier hook",
        },
        "inputs": {
            "long_c59cf": input_entry(
                LONG_C59CF,
                {
                    "status": rows["c59cf"].get("status"),
                    "certificate_sha256": rows["c59cf"].get("certificate_sha256"),
                },
            ),
            "long_c59cf_corrected_edge": input_entry(LONG_C59CF_CORRECTED_EDGE),
            "long_c59cf_corrected_node": input_entry(LONG_C59CF_CORRECTED_NODE),
            "long_metric_rank_gate": input_entry(
                LONG_METRIC_RANK_GATE,
                {
                    "status": rows["metric_gate"].get("status"),
                    "certificate_sha256": rows["metric_gate"].get(
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
            "c59st": relpath(OUT_DIR / "c59st.json"),
            "tensor_entry_csv": relpath(OUT_DIR / "tensor_entry.csv"),
            "pair_csv": relpath(OUT_DIR / "pair.csv"),
            "kernel_csv": relpath(OUT_DIR / "kernel.csv"),
            "inertia_csv": relpath(OUT_DIR / "inertia.csv"),
            "metric_csv": relpath(OUT_DIR / "metric.csv"),
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
                "a symmetric finite 20x20 stress candidate from the conserved directed current",
                "exact rank 19, nullity 1, and inertia (11,8,1)",
                "rank/nullity count match with the certified 1+19 public boundary",
                "an explicit one-dimensional kernel vector for the finite tensor candidate",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "canonical identification of the tensor kernel with the public time trace",
                "a four-dimensional metric reduction",
                "a smooth Lorentzian metric",
                "a physical stress-energy tensor",
                "curvature, Einstein tensor, or field equations",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Test whether the one-dimensional tensor kernel is functorially "
            "identified with the certified public time trace; if not, certify "
            "it as a finite gauge-null stress mode before any metric lift."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59st.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59st.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59st": c59st,
        "tensor_entry_csv": csv_text(
            TENSOR_ENTRY_COLUMNS, rows["tensor_entry_rows"]
        ),
        "pair_csv": csv_text(PAIR_COLUMNS, rows["pair_rows"]),
        "kernel_csv": csv_text(KERNEL_COLUMNS, rows["kernel_rows"]),
        "inertia_csv": csv_text(INERTIA_COLUMNS, rows["inertia_rows"]),
        "metric_csv": csv_text(METRIC_COLUMNS, rows["metric_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "tensor_entry_table": tensor_entry_table,
        "pair_table": pair_table,
        "kernel_table": kernel_table,
        "inertia_table": inertia_table,
        "metric_table": metric_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "symmetric_matrix": symmetric_matrix,
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
    write_json(OUT_DIR / "c59st.json", payloads["c59st"])
    (OUT_DIR / "tensor_entry.csv").write_text(
        payloads["tensor_entry_csv"], encoding="utf-8"
    )
    (OUT_DIR / "pair.csv").write_text(payloads["pair_csv"], encoding="utf-8")
    (OUT_DIR / "kernel.csv").write_text(payloads["kernel_csv"], encoding="utf-8")
    (OUT_DIR / "inertia.csv").write_text(payloads["inertia_csv"], encoding="utf-8")
    (OUT_DIR / "metric.csv").write_text(payloads["metric_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        tensor_entry_table=payloads["tensor_entry_table"],
        pair_table=payloads["pair_table"],
        kernel_table=payloads["kernel_table"],
        inertia_table=payloads["inertia_table"],
        metric_table=payloads["metric_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
        symmetric_matrix=payloads["symmetric_matrix"],
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
