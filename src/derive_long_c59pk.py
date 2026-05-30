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


THEOREM_ID = "long_c59pk"
STATUS = "LONG_C59PK_INDUCED_PUBLIC_KERNEL_RESTRICTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"
PROOF_ROOT = D20_INVARIANTS / "proof_obligations"

LONG_C59Q = PROOF_ROOT / "long_c59q" / "report.json"
LONG_C59Q_BASIS = PROOF_ROOT / "long_c59q" / "basis.csv"
LONG_C59Q_QUOTIENT = PROOF_ROOT / "long_c59q" / "quotient_entry.csv"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_c59pk.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_c59pk.py"

RESTRICT_BASIS_COLUMNS = [
    "restricted_index",
    "quotient_index",
    "source_atom",
    "q_pub_value",
    "induced_kernel_flag",
]
RESTRICTED_ENTRY_COLUMNS = [
    "entry_id",
    "row_restricted_index",
    "col_restricted_index",
    "row_atom",
    "col_atom",
    "restricted_value",
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
    "induced_q_pub_kernel_materialized",
    "restricted_form_nondegenerate",
    "exact_inertia_10_8_0",
    "time_trace_removed",
    "three_spatial_rank_certified",
    "four_dimensional_metric_certified",
]
DECISION_CODES = {name: index for index, name in enumerate(DECISION_NAMES)}

GAP_NAMES = [
    "induced_q_pub_kernel_restriction",
    "nondegenerate_18_form",
    "three_spatial_rank_selection",
    "four_dimensional_metric_reduction",
    "physical_stress_energy_lift",
    "thermal_gravity_derivation",
]
GAP_CODES = {name: index for index, name in enumerate(GAP_NAMES)}

OBS_NAMES = [
    "input_report_count",
    "input_certified_count",
    "quotient_dimension",
    "induced_q_pub_rank",
    "restricted_dimension",
    "restricted_entry_count",
    "active_restricted_pair_count",
    "restricted_rank",
    "restricted_nullity",
    "inertia_positive_count",
    "inertia_negative_count",
    "inertia_zero_count",
    "time_trace_removed_flag",
    "three_spatial_rank_flag",
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
        for index in range(col, col_count):
            current[pivot_row][index] /= pivot
        for row in range(row_count):
            if row == pivot_row or current[row][col] == 0:
                continue
            factor = current[row][col]
            for index in range(col, col_count):
                current[row][index] -= factor * current[pivot_row][index]
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


def build_rows() -> dict[str, Any]:
    c59q = load_json(LONG_C59Q)
    basis_source = read_csv_int(LONG_C59Q_BASIS)
    quotient_entries = read_csv_int(LONG_C59Q_QUOTIENT)
    quotient_dimension = len(basis_source)
    quotient = [[0 for _ in range(quotient_dimension)] for _ in range(quotient_dimension)]
    for row in quotient_entries:
        quotient[row["row_quotient_index"]][row["col_quotient_index"]] = row[
            "quotient_value"
        ]

    keep_indices = [
        row["quotient_index"] for row in basis_source if row["q_pub_value"] == 0
    ]
    restricted = [[quotient[row][col] for col in keep_indices] for row in keep_indices]
    rank = exact_rank(restricted)
    positive, negative, inertia_zero, inertia_rows = exact_inertia(restricted)
    restricted_basis_rows = []
    for restricted_index, quotient_index in enumerate(keep_indices):
        row = basis_source[quotient_index]
        restricted_basis_rows.append(
            {
                "restricted_index": restricted_index,
                "quotient_index": quotient_index,
                "source_atom": row["source_atom"],
                "q_pub_value": row["q_pub_value"],
                "induced_kernel_flag": 1,
            }
        )

    restricted_entry_rows = []
    for row_index, row_basis in enumerate(restricted_basis_rows):
        for col_index, col_basis in enumerate(restricted_basis_rows):
            value = restricted[row_index][col_index]
            restricted_entry_rows.append(
                {
                    "entry_id": row_index * len(restricted_basis_rows) + col_index,
                    "row_restricted_index": row_index,
                    "col_restricted_index": col_index,
                    "row_atom": row_basis["source_atom"],
                    "col_atom": col_basis["source_atom"],
                    "restricted_value": value,
                    "diagonal_flag": int(row_index == col_index),
                    "nonzero_flag": int(value != 0),
                }
            )

    active_pairs = sum(
        restricted[row][col] != 0
        for row in range(len(restricted_basis_rows))
        for col in range(row + 1, len(restricted_basis_rows))
    )
    obs = {
        "input_report_count": 1,
        "input_certified_count": int(certified(c59q)),
        "quotient_dimension": quotient_dimension,
        "induced_q_pub_rank": int(
            any(row["q_pub_value"] != 0 for row in basis_source)
        ),
        "restricted_dimension": len(restricted_basis_rows),
        "restricted_entry_count": len(restricted_entry_rows),
        "active_restricted_pair_count": active_pairs,
        "restricted_rank": rank,
        "restricted_nullity": len(restricted_basis_rows) - rank,
        "inertia_positive_count": positive,
        "inertia_negative_count": negative,
        "inertia_zero_count": inertia_zero,
        "time_trace_removed_flag": int(
            all(row["q_pub_value"] == 0 for row in restricted_basis_rows)
        ),
        "three_spatial_rank_flag": int(len(restricted_basis_rows) == 3),
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": GAP_CODES["three_spatial_rank_selection"],
    }
    decision_rows = [
        {
            "decision_id": DECISION_CODES["induced_q_pub_kernel_materialized"],
            "decision_code": DECISION_CODES["induced_q_pub_kernel_materialized"],
            "value": obs["restricted_dimension"],
            "certified_flag": int(obs["restricted_dimension"] == 18),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["restricted_form_nondegenerate"],
            "decision_code": DECISION_CODES["restricted_form_nondegenerate"],
            "value": rank,
            "certified_flag": int(rank == 18 and obs["restricted_nullity"] == 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["exact_inertia_10_8_0"],
            "decision_code": DECISION_CODES["exact_inertia_10_8_0"],
            "value": positive * 100 + negative * 10 + inertia_zero,
            "certified_flag": int(positive == 10 and negative == 8 and inertia_zero == 0),
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["time_trace_removed"],
            "decision_code": DECISION_CODES["time_trace_removed"],
            "value": obs["time_trace_removed_flag"],
            "certified_flag": obs["time_trace_removed_flag"],
            "obstruction_flag": 0,
        },
        {
            "decision_id": DECISION_CODES["three_spatial_rank_certified"],
            "decision_code": DECISION_CODES["three_spatial_rank_certified"],
            "value": obs["three_spatial_rank_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
        {
            "decision_id": DECISION_CODES["four_dimensional_metric_certified"],
            "decision_code": DECISION_CODES["four_dimensional_metric_certified"],
            "value": obs["four_dimensional_metric_flag"],
            "certified_flag": 0,
            "obstruction_flag": 1,
        },
    ]
    gap_rows = [
        {
            "gap_id": GAP_CODES["induced_q_pub_kernel_restriction"],
            "gap_code": GAP_CODES["induced_q_pub_kernel_restriction"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["nondegenerate_18_form"],
            "gap_code": GAP_CODES["nondegenerate_18_form"],
            "certified_flag": 1,
            "open_flag": 0,
            "obstruction_flag": 0,
            "next_flag": 0,
        },
        {
            "gap_id": GAP_CODES["three_spatial_rank_selection"],
            "gap_code": GAP_CODES["three_spatial_rank_selection"],
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
        "c59q": c59q,
        "restrict_basis_rows": restricted_basis_rows,
        "restricted_entry_rows": restricted_entry_rows,
        "inertia_rows": inertia_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "restricted_matrix": restricted,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    restrict_basis_table = table_from_rows(
        RESTRICT_BASIS_COLUMNS, rows["restrict_basis_rows"]
    )
    restricted_entry_table = table_from_rows(
        RESTRICTED_ENTRY_COLUMNS, rows["restricted_entry_rows"]
    )
    inertia_table = table_from_rows(INERTIA_COLUMNS, rows["inertia_rows"])
    decision_table = table_from_rows(DECISION_COLUMNS, rows["decision_rows"])
    gap_table = table_from_rows(GAP_COLUMNS, rows["gap_rows"])
    observable_table = table_from_rows(OBS_COLUMNS, rows["obs_rows"])
    restricted_matrix = np.asarray(rows["restricted_matrix"], dtype=np.int64)
    obs = rows["obs"]
    checks = {
        "input_report_certified": obs["input_report_count"]
        == obs["input_certified_count"],
        "induced_kernel_restriction_exact": obs["quotient_dimension"] == 19
        and obs["induced_q_pub_rank"] == 1
        and obs["restricted_dimension"] == 18
        and obs["time_trace_removed_flag"] == 1,
        "restricted_form_nondegenerate": obs["restricted_rank"] == 18
        and obs["restricted_nullity"] == 0
        and obs["inertia_positive_count"] == 10
        and obs["inertia_negative_count"] == 8
        and obs["inertia_zero_count"] == 0,
        "three_spatial_rank_not_certified": obs["three_spatial_rank_flag"] == 0
        and obs["four_dimensional_metric_flag"] == 0,
        "physical_boundaries_preserved": obs["physical_stress_energy_flag"] == 0
        and obs["smooth_metric_flag"] == 0
        and obs["thermal_gravity_flag"] == 0,
        "table_shapes_match": restrict_basis_table.shape
        == (18, len(RESTRICT_BASIS_COLUMNS))
        and restricted_entry_table.shape == (324, len(RESTRICTED_ENTRY_COLUMNS))
        and inertia_table.shape[1] == len(INERTIA_COLUMNS)
        and decision_table.shape == (len(DECISION_CODES), len(DECISION_COLUMNS))
        and gap_table.shape == (len(GAP_CODES), len(GAP_COLUMNS))
        and observable_table.shape == (len(OBS_CODES), len(OBS_COLUMNS))
        and restricted_matrix.shape == (18, 18),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "c59x_induced_public_kernel_restriction",
        "summary": {
            "quotient_dimension": obs["quotient_dimension"],
            "induced_q_pub_rank": obs["induced_q_pub_rank"],
            "restricted_dimension": obs["restricted_dimension"],
            "restricted_rank": obs["restricted_rank"],
            "restricted_nullity": obs["restricted_nullity"],
            "inertia_positive_count": obs["inertia_positive_count"],
            "inertia_negative_count": obs["inertia_negative_count"],
            "inertia_zero_count": obs["inertia_zero_count"],
            "time_trace_removed_flag": obs["time_trace_removed_flag"],
            "three_spatial_rank_flag": obs["three_spatial_rank_flag"],
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
        "restrict_basis_table_sha256": sha_array(restrict_basis_table),
        "restrict_basis_text_sha256": sha_text(
            csv_text(RESTRICT_BASIS_COLUMNS, rows["restrict_basis_rows"])
        ),
        "restricted_entry_table_sha256": sha_array(restricted_entry_table),
        "restricted_entry_text_sha256": sha_text(
            csv_text(RESTRICTED_ENTRY_COLUMNS, rows["restricted_entry_rows"])
        ),
        "inertia_table_sha256": sha_array(inertia_table),
        "decision_table_sha256": sha_array(decision_table),
        "gap_table_sha256": sha_array(gap_table),
        "observable_table_sha256": sha_array(observable_table),
        "restricted_matrix_sha256": sha_array(restricted_matrix),
    }
    c59pk = {
        "schema": "long.c59pk@1",
        "object": "c59x_induced_public_kernel_restriction",
        "status": STATUS if all(checks.values()) else "LONG_C59PK_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.c59pk.report@1",
        "status": c59pk["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_c59pk restricts the 19-dimensional gauge-null quotient form "
            "to the induced q_pub kernel. The resulting 18-dimensional form is "
            "nondegenerate with exact inertia (10,8,0). This removes the public "
            "time trace but does not certify a three-spatial-rank or 3+1 metric "
            "selection."
        ),
        "stage_protocol": {
            "draft": "read long_c59q quotient basis and quotient form",
            "witness": "emit induced-kernel basis rows, restricted form entries, inertia pivots, decisions, gaps, and observables",
            "coherence": "check q_pub-kernel restriction, nondegeneracy, exact inertia, and metric boundaries",
            "closure": "certify the 18D induced public-kernel restriction while preserving the 3-rank gap",
            "emit": "write long_c59pk artifacts and verifier hook",
        },
        "inputs": {
            "long_c59q": input_entry(
                LONG_C59Q,
                {
                    "status": rows["c59q"].get("status"),
                    "certificate_sha256": rows["c59q"].get("certificate_sha256"),
                },
            ),
            "long_c59q_basis": input_entry(LONG_C59Q_BASIS),
            "long_c59q_quotient": input_entry(LONG_C59Q_QUOTIENT),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "c59pk": relpath(OUT_DIR / "c59pk.json"),
            "restrict_basis_csv": relpath(OUT_DIR / "restrict_basis.csv"),
            "restricted_entry_csv": relpath(OUT_DIR / "restricted_entry.csv"),
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
                "the induced q_pub-kernel restriction of the 19D quotient form",
                "a nondegenerate 18-dimensional finite form",
                "exact restricted inertia (10,8,0)",
                "removal of the public time trace from the quotient form",
            ],
            "does_not_certify_because_obstructed_or_open": [
                "a canonical three-spatial-rank selection inside the 18D form",
                "a four-dimensional metric reduction",
                "a smooth Lorentzian metric",
                "a physical stress-energy tensor",
                "a thermal-gravity derivation",
            ],
        },
        "next_highest_yield_item": (
            "Search for, or obstruct, a canonical three-dimensional spatial "
            "subform inside the 18-dimensional induced public-kernel form."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.c59pk.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.c59pk.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "c59pk": c59pk,
        "restrict_basis_csv": csv_text(
            RESTRICT_BASIS_COLUMNS, rows["restrict_basis_rows"]
        ),
        "restricted_entry_csv": csv_text(
            RESTRICTED_ENTRY_COLUMNS, rows["restricted_entry_rows"]
        ),
        "inertia_csv": csv_text(INERTIA_COLUMNS, rows["inertia_rows"]),
        "decision_csv": csv_text(DECISION_COLUMNS, rows["decision_rows"]),
        "gap_csv": csv_text(GAP_COLUMNS, rows["gap_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "restrict_basis_table": restrict_basis_table,
        "restricted_entry_table": restricted_entry_table,
        "inertia_table": inertia_table,
        "decision_table": decision_table,
        "gap_table": gap_table,
        "observable_table": observable_table,
        "restricted_matrix": restricted_matrix,
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
    write_json(OUT_DIR / "c59pk.json", payloads["c59pk"])
    (OUT_DIR / "restrict_basis.csv").write_text(
        payloads["restrict_basis_csv"], encoding="utf-8"
    )
    (OUT_DIR / "restricted_entry.csv").write_text(
        payloads["restricted_entry_csv"], encoding="utf-8"
    )
    (OUT_DIR / "inertia.csv").write_text(payloads["inertia_csv"], encoding="utf-8")
    (OUT_DIR / "decision.csv").write_text(payloads["decision_csv"], encoding="utf-8")
    (OUT_DIR / "gap.csv").write_text(payloads["gap_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        restrict_basis_table=payloads["restrict_basis_table"],
        restricted_entry_table=payloads["restricted_entry_table"],
        inertia_table=payloads["inertia_table"],
        decision_table=payloads["decision_table"],
        gap_table=payloads["gap_table"],
        observable_table=payloads["observable_table"],
        restricted_matrix=payloads["restricted_matrix"],
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
