from __future__ import annotations

import csv
import hashlib
import json
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
    from .derive_long_lap import OUT_DIR as LONG_LAP_DIR, STATUS as LONG_LAP_STATUS
    from .derive_long_lift import OUT_DIR as LONG_LIFT_DIR, STATUS as LONG_LIFT_STATUS
    from .derive_long_lln import (
        OUT_DIR as LONG_LLN_DIR,
        RAW_TENSOR,
        STATUS as LONG_LLN_STATUS,
    )
    from .derive_long_rec import (
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as LONG_REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
    )
    from .derive_long_tens import OUT_DIR as LONG_TENS_DIR, STATUS as LONG_TENS_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_lap import OUT_DIR as LONG_LAP_DIR, STATUS as LONG_LAP_STATUS
    from derive_long_lift import OUT_DIR as LONG_LIFT_DIR, STATUS as LONG_LIFT_STATUS
    from derive_long_lln import (
        OUT_DIR as LONG_LLN_DIR,
        RAW_TENSOR,
        STATUS as LONG_LLN_STATUS,
    )
    from derive_long_rec import (
        OUT_DIR as LONG_REC_DIR,
        OWNER_COLUMNS as LONG_REC_OWNER_COLUMNS,
        STATUS as LONG_REC_STATUS,
    )
    from derive_long_tens import OUT_DIR as LONG_TENS_DIR, STATUS as LONG_TENS_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_raw"
STATUS = "LONG_RAW_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_LLN_REPORT = LONG_LLN_DIR / "report.json"
LONG_LLN_TABLES = LONG_LLN_DIR / "tables.npz"
LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_OWNER = LONG_REC_DIR / "owner.csv"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
LONG_LAP_REPORT = LONG_LAP_DIR / "report.json"
LONG_LAP_NODE = LONG_LAP_DIR / "node.csv"
LONG_LAP_COMPONENT = LONG_LAP_DIR / "component.csv"
LONG_LAP_TABLES = LONG_LAP_DIR / "tables.npz"
LONG_TENS_REPORT = LONG_TENS_DIR / "report.json"
LONG_TENS_FIBER = LONG_TENS_DIR / "fiber.csv"
LONG_TENS_HORIZON = LONG_TENS_DIR / "horizon.csv"
LONG_TENS_TABLES = LONG_TENS_DIR / "tables.npz"
LONG_LIFT_REPORT = LONG_LIFT_DIR / "report.json"
LONG_LIFT_TABLES = LONG_LIFT_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_raw.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_raw.py"

OWNER_TEXT_HASH = (
    "c26e35ee58f7af9968590a3fd5ba4cac8152fa6aff28a6d8e335b86814996921"
)
COMPONENT_TEXT_HASH = (
    "e26bb6a1d7cb82f15544c2e6d007ddd3bb190e793e60d43e318a13507d88fcd7"
)
HORIZON_TEXT_HASH = (
    "3e00187e79376b901aa4ff3df5509bbee00dc83be9b392796fb78f9741a69a64"
)
FIBER_TEXT_HASH = (
    "1bf75da6070493b9f5aa96e4137b8ac3d925d67ded016178f2582f488c230bde"
)

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
HORIZON_MAX = 16

OWNER_COLUMNS = [
    "basis_id",
    "component_id",
    "active_owner_flag",
    "owner_cell_count",
    "raw_source_cell_count",
    "raw_support_count",
    "raw_coeff_sum",
    "owner_target_addr",
    "raw_target_min",
    "raw_target_max",
    "raw_target_min_minus_owner_target",
    "raw_target_max_minus_owner_target",
    "raw_support_mod_1000000007",
    "raw_support_mod_1000000009",
    "raw_coeff_mod_1000000007",
    "raw_coeff_mod_1000000009",
]
COMPONENT_COLUMNS = [
    "component_id",
    "active_owner_count",
    "owner_cell_count",
    "raw_source_cell_count",
    "raw_support_count",
    "raw_coeff_sum",
    "raw_source_cell_owner_positive_count",
    "raw_support_owner_positive_count",
    "raw_coeff_owner_positive_count",
    "raw_support_mod_1000000007",
    "raw_support_mod_1000000009",
    "raw_coeff_mod_1000000007",
    "raw_coeff_mod_1000000009",
]
HORIZON_COLUMNS = [
    "horizon_id",
    "sample_count",
    "sum_state_count",
    "component_path_count",
    "raw_support_path_lift_digits",
    "raw_support_path_lift_mod_1000000007",
    "raw_support_path_lift_mod_1000000009",
    "raw_coeff_path_lift_digits",
    "raw_coeff_path_lift_mod_1000000007",
    "raw_coeff_path_lift_mod_1000000009",
    "long_tens_gap_horizon_flag",
    "existing_sum_profunctor_flag",
    "compressed_raw_owner_quotient_flag",
    "raw_support_total_equal_flag",
    "raw_coeff_total_equal_flag",
]
FIBER_COLUMNS = [
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "component_fiber_path_count",
    "raw_support_fiber_lift_digits",
    "raw_support_fiber_lift_mod_1000000007",
    "raw_support_fiber_lift_mod_1000000009",
    "raw_coeff_fiber_lift_digits",
    "raw_coeff_fiber_lift_mod_1000000007",
    "raw_coeff_fiber_lift_mod_1000000009",
    "long_tens_gap_flag",
    "existing_prof_flag",
    "raw_support_lift_positive_flag",
    "raw_coeff_lift_positive_flag",
    "compressed_raw_quotient_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "owner_row_count",
    "component_row_count",
    "horizon_row_count",
    "fiber_row_count",
    "raw_tensor_support_count",
    "raw_tensor_coeff_sum",
    "raw_owner_assignment_count",
    "raw_owner_assignment_complete_flag",
    "owner_raw_support_positive_count",
    "owner_raw_source_cell_positive_count",
    "raw_source_cell_count",
    "owner_cell_total",
    "active_owner_count",
    "active_owner_cell_count",
    "active_raw_source_cell_count",
    "active_raw_support_count",
    "active_raw_coeff_sum",
    "inactive_raw_support_count",
    "inactive_raw_coeff_sum",
    "component_raw_source_cell_positive_count",
    "component_raw_support_positive_count",
    "component_raw_coeff_positive_count",
    "target_ge_owner_target_count",
    "target_eq_owner_target_count",
    "target_diff_min",
    "target_diff_max",
    "raw_support_horizon_total_equal_count",
    "raw_coeff_horizon_total_equal_count",
    "raw_support_lift_positive_count",
    "raw_coeff_lift_positive_count",
    "gap_fiber_row_count",
    "existing_fiber_row_count",
    "compressed_raw_quotient_row_count",
    "current_raw_owner_support_flag",
    "current_compressed_raw_lift_flag",
    "current_materialized_raw_path_flag",
    "current_markov_only_quotient_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def csv_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    lines = [",".join(columns)]
    lines.extend(",".join(str(row[column]) for column in columns) for row in rows)
    return "\n".join(lines) + "\n"


def digest_text(columns: list[str], rows: list[dict[str, Any]]) -> str:
    return "".join(",".join(str(row[column]) for column in columns) + "\n" for row in rows)


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


def read_csv_rows(path: Any) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def int_rows(rows: list[dict[str, str]]) -> list[dict[str, int]]:
    return [{key: int(value) for key, value in row.items()} for row in rows]


def weighted_coefficients(weights: list[int], max_horizon: int) -> dict[int, list[int]]:
    coeffs = {0: [1]}
    for sample_count in range(1, max_horizon + 1):
        previous = coeffs[sample_count - 1]
        current = [0 for _ in range(len(previous) + len(weights) - 1)]
        for index, value in enumerate(previous):
            for add_value, weight in enumerate(weights):
                current[index + add_value] += value * weight
        coeffs[sample_count] = current
    return coeffs


def load_raw_triples() -> np.ndarray:
    with np.load(RAW_TENSOR, allow_pickle=False) as payload:
        triples = np.asarray(payload["triples"], dtype=np.int64)
    if triples.ndim != 2 or triples.shape[1] != 4:
        raise ValueError("raw tensor triples must have shape (*, 4)")
    return triples


def load_rec_tables() -> tuple[np.ndarray, np.ndarray]:
    with np.load(LONG_REC_TABLES, allow_pickle=False) as payload:
        owner_grid = np.asarray(payload["owner_grid"], dtype=np.int64)
        owner_table = np.asarray(payload["owner_table"], dtype=np.int64)
    return owner_grid, owner_table


def raw_owner_profiles(
    triples: np.ndarray,
    owner_grid: np.ndarray,
    owner_table: np.ndarray,
) -> dict[str, Any]:
    n = int(owner_grid.shape[0])
    basis_count = int(owner_table.shape[0])
    source0 = triples[:, 0]
    source1 = triples[:, 1]
    target = triples[:, 2]
    coeff = triples[:, 3]
    owners = owner_grid[source0, source1].astype(np.int64, copy=False)
    owner_support = np.bincount(owners, minlength=basis_count).astype(np.int64)
    owner_coeff = np.bincount(owners, weights=coeff, minlength=basis_count).astype(
        np.int64
    )
    encoded_cells = source0.astype(np.int64) * n + source1.astype(np.int64)
    unique_cells = np.unique(encoded_cells)
    cell_owners = owner_grid.ravel()[unique_cells].astype(np.int64, copy=False)
    owner_source_cells = np.bincount(cell_owners, minlength=basis_count).astype(
        np.int64
    )
    owner_target = owner_table[:, LONG_REC_OWNER_COLUMNS.index("target_addr")].astype(
        np.int64,
        copy=False,
    )
    owner_target_for_rows = owner_target[owners]
    target_diff = target.astype(np.int64, copy=False) - owner_target_for_rows
    target_min = np.full(basis_count, n, dtype=np.int64)
    target_max = np.full(basis_count, -1, dtype=np.int64)
    np.minimum.at(target_min, owners, target)
    np.maximum.at(target_max, owners, target)
    return {
        "n": n,
        "basis_count": basis_count,
        "owners": owners,
        "owner_support": owner_support,
        "owner_coeff": owner_coeff,
        "owner_source_cells": owner_source_cells,
        "owner_target": owner_target,
        "target_min": target_min,
        "target_max": target_max,
        "target_diff": target_diff,
        "unique_source_cell_count": int(unique_cells.size),
    }


def active_component_maps(
    owner_table: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[int, list[int]], list[int], list[dict[str, str]]]:
    basis_count = int(owner_table.shape[0])
    active_component = np.full(basis_count, -1, dtype=np.int64)
    active_owner_cell = np.zeros(basis_count, dtype=np.int64)
    component_to_basis: dict[int, list[int]] = {}
    node_rows = read_csv_rows(LONG_LAP_NODE)
    for row in node_rows:
        basis_id = int(row["basis_id"])
        component_id = int(row["component_id"])
        active_component[basis_id] = component_id
        active_owner_cell[basis_id] = int(row["owner_cell_count"])
        component_to_basis.setdefault(component_id, []).append(basis_id)
    component_ids = sorted(component_to_basis)
    return active_component, active_owner_cell, component_to_basis, component_ids, node_rows


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_rec": load_json(LONG_REC_REPORT),
        "long_lap": load_json(LONG_LAP_REPORT),
        "long_tens": load_json(LONG_TENS_REPORT),
        "long_lift": load_json(LONG_LIFT_REPORT),
    }
    triples = load_raw_triples()
    owner_grid, owner_table = load_rec_tables()
    raw = raw_owner_profiles(triples, owner_grid, owner_table)
    tens_fiber_rows = int_rows(read_csv_rows(LONG_TENS_FIBER))
    tens_horizon_rows = int_rows(read_csv_rows(LONG_TENS_HORIZON))
    lap_component_rows = read_csv_rows(LONG_LAP_COMPONENT)
    active_component, active_owner_cell, component_to_basis, component_ids, node_rows = (
        active_component_maps(owner_table)
    )
    owner_cell_count = owner_table[
        :, LONG_REC_OWNER_COLUMNS.index("owner_cell_count")
    ].astype(np.int64, copy=False)

    owner_rows: list[dict[str, int]] = []
    for basis_id in range(raw["basis_count"]):
        component_id = int(active_component[basis_id])
        target_min = int(raw["target_min"][basis_id])
        target_max = int(raw["target_max"][basis_id])
        owner_target = int(raw["owner_target"][basis_id])
        owner_rows.append(
            {
                "basis_id": basis_id,
                "component_id": component_id,
                "active_owner_flag": int(component_id >= 0),
                "owner_cell_count": int(owner_cell_count[basis_id]),
                "raw_source_cell_count": int(raw["owner_source_cells"][basis_id]),
                "raw_support_count": int(raw["owner_support"][basis_id]),
                "raw_coeff_sum": int(raw["owner_coeff"][basis_id]),
                "owner_target_addr": owner_target,
                "raw_target_min": target_min,
                "raw_target_max": target_max,
                "raw_target_min_minus_owner_target": target_min - owner_target,
                "raw_target_max_minus_owner_target": target_max - owner_target,
                "raw_support_mod_1000000007": int(
                    raw["owner_support"][basis_id] % MOD_PRIMES[0]
                ),
                "raw_support_mod_1000000009": int(
                    raw["owner_support"][basis_id] % MOD_PRIMES[1]
                ),
                "raw_coeff_mod_1000000007": int(
                    raw["owner_coeff"][basis_id] % MOD_PRIMES[0]
                ),
                "raw_coeff_mod_1000000009": int(
                    raw["owner_coeff"][basis_id] % MOD_PRIMES[1]
                ),
            }
        )

    lap_component_by_id = {
        int(row["component_id"]): row for row in lap_component_rows
    }
    component_rows: list[dict[str, int]] = []
    for component_id in component_ids:
        basis_ids = component_to_basis[component_id]
        raw_source_cells = int(raw["owner_source_cells"][basis_ids].sum())
        raw_support = int(raw["owner_support"][basis_ids].sum())
        raw_coeff = int(raw["owner_coeff"][basis_ids].sum())
        lap_row = lap_component_by_id[component_id]
        component_rows.append(
            {
                "component_id": component_id,
                "active_owner_count": len(basis_ids),
                "owner_cell_count": int(lap_row["owner_cell_count"]),
                "raw_source_cell_count": raw_source_cells,
                "raw_support_count": raw_support,
                "raw_coeff_sum": raw_coeff,
                "raw_source_cell_owner_positive_count": int(
                    np.count_nonzero(raw["owner_source_cells"][basis_ids])
                ),
                "raw_support_owner_positive_count": int(
                    np.count_nonzero(raw["owner_support"][basis_ids])
                ),
                "raw_coeff_owner_positive_count": int(
                    np.count_nonzero(raw["owner_coeff"][basis_ids])
                ),
                "raw_support_mod_1000000007": raw_support % MOD_PRIMES[0],
                "raw_support_mod_1000000009": raw_support % MOD_PRIMES[1],
                "raw_coeff_mod_1000000007": raw_coeff % MOD_PRIMES[0],
                "raw_coeff_mod_1000000009": raw_coeff % MOD_PRIMES[1],
            }
        )

    raw_support_weights = [row["raw_support_count"] for row in component_rows]
    raw_coeff_weights = [row["raw_coeff_sum"] for row in component_rows]
    support_coeffs = weighted_coefficients(raw_support_weights, HORIZON_MAX)
    coeff_coeffs = weighted_coefficients(raw_coeff_weights, HORIZON_MAX)
    raw_support_total = sum(raw_support_weights)
    raw_coeff_total = sum(raw_coeff_weights)

    horizon_rows: list[dict[str, int]] = []
    for row in tens_horizon_rows:
        sample_count = row["sample_count"]
        support_total = sum(support_coeffs[sample_count])
        coeff_total = sum(coeff_coeffs[sample_count])
        horizon_rows.append(
            {
                "horizon_id": row["horizon_id"],
                "sample_count": sample_count,
                "sum_state_count": row["sum_state_count"],
                "component_path_count": row["component_path_count"],
                "raw_support_path_lift_digits": len(str(support_total)),
                "raw_support_path_lift_mod_1000000007": support_total
                % MOD_PRIMES[0],
                "raw_support_path_lift_mod_1000000009": support_total
                % MOD_PRIMES[1],
                "raw_coeff_path_lift_digits": len(str(coeff_total)),
                "raw_coeff_path_lift_mod_1000000007": coeff_total % MOD_PRIMES[0],
                "raw_coeff_path_lift_mod_1000000009": coeff_total % MOD_PRIMES[1],
                "long_tens_gap_horizon_flag": row["object_gap_flag"],
                "existing_sum_profunctor_flag": row["profunctor_sum_object_flag"],
                "compressed_raw_owner_quotient_flag": row["formal_sum_object_flag"],
                "raw_support_total_equal_flag": int(
                    support_total == raw_support_total**sample_count
                ),
                "raw_coeff_total_equal_flag": int(
                    coeff_total == raw_coeff_total**sample_count
                ),
            }
        )

    fiber_rows: list[dict[str, int]] = []
    for row in tens_fiber_rows:
        sample_count = row["sample_count"]
        sum_value = row["sum_value"]
        support_count = support_coeffs[sample_count][sum_value]
        coeff_count = coeff_coeffs[sample_count][sum_value]
        fiber_rows.append(
            {
                "fiber_row_id": row["fiber_row_id"],
                "sample_count": sample_count,
                "sum_value": sum_value,
                "component_fiber_path_count": row["fiber_path_count"],
                "raw_support_fiber_lift_digits": len(str(support_count)),
                "raw_support_fiber_lift_mod_1000000007": support_count
                % MOD_PRIMES[0],
                "raw_support_fiber_lift_mod_1000000009": support_count
                % MOD_PRIMES[1],
                "raw_coeff_fiber_lift_digits": len(str(coeff_count)),
                "raw_coeff_fiber_lift_mod_1000000007": coeff_count % MOD_PRIMES[0],
                "raw_coeff_fiber_lift_mod_1000000009": coeff_count % MOD_PRIMES[1],
                "long_tens_gap_flag": row["long_obj_object_gap_flag"],
                "existing_prof_flag": row["existing_prof_flag"],
                "raw_support_lift_positive_flag": int(support_count > 0),
                "raw_coeff_lift_positive_flag": int(coeff_count > 0),
                "compressed_raw_quotient_flag": row["formal_added_flag"],
            }
        )

    active_mask = active_component >= 0
    active_basis_ids = np.flatnonzero(active_mask)
    obs = {
        "owner_row_count": len(owner_rows),
        "component_row_count": len(component_rows),
        "horizon_row_count": len(horizon_rows),
        "fiber_row_count": len(fiber_rows),
        "raw_tensor_support_count": int(triples.shape[0]),
        "raw_tensor_coeff_sum": int(triples[:, 3].sum()),
        "raw_owner_assignment_count": int(raw["owners"].shape[0]),
        "raw_owner_assignment_complete_flag": int(bool(np.all(raw["owners"] >= 0))),
        "owner_raw_support_positive_count": int(np.count_nonzero(raw["owner_support"])),
        "owner_raw_source_cell_positive_count": int(
            np.count_nonzero(raw["owner_source_cells"])
        ),
        "raw_source_cell_count": raw["unique_source_cell_count"],
        "owner_cell_total": int(owner_cell_count.sum()),
        "active_owner_count": int(active_mask.sum()),
        "active_owner_cell_count": int(owner_cell_count[active_basis_ids].sum()),
        "active_raw_source_cell_count": int(
            raw["owner_source_cells"][active_basis_ids].sum()
        ),
        "active_raw_support_count": int(raw["owner_support"][active_basis_ids].sum()),
        "active_raw_coeff_sum": int(raw["owner_coeff"][active_basis_ids].sum()),
        "inactive_raw_support_count": int(raw["owner_support"][~active_mask].sum()),
        "inactive_raw_coeff_sum": int(raw["owner_coeff"][~active_mask].sum()),
        "component_raw_source_cell_positive_count": sum(
            int(row["raw_source_cell_count"] > 0) for row in component_rows
        ),
        "component_raw_support_positive_count": sum(
            int(row["raw_support_count"] > 0) for row in component_rows
        ),
        "component_raw_coeff_positive_count": sum(
            int(row["raw_coeff_sum"] > 0) for row in component_rows
        ),
        "target_ge_owner_target_count": int(np.count_nonzero(raw["target_diff"] >= 0)),
        "target_eq_owner_target_count": int(np.count_nonzero(raw["target_diff"] == 0)),
        "target_diff_min": int(raw["target_diff"].min()),
        "target_diff_max": int(raw["target_diff"].max()),
        "raw_support_horizon_total_equal_count": sum(
            row["raw_support_total_equal_flag"] for row in horizon_rows
        ),
        "raw_coeff_horizon_total_equal_count": sum(
            row["raw_coeff_total_equal_flag"] for row in horizon_rows
        ),
        "raw_support_lift_positive_count": sum(
            row["raw_support_lift_positive_flag"] for row in fiber_rows
        ),
        "raw_coeff_lift_positive_count": sum(
            row["raw_coeff_lift_positive_flag"] for row in fiber_rows
        ),
        "gap_fiber_row_count": sum(row["long_tens_gap_flag"] for row in fiber_rows),
        "existing_fiber_row_count": sum(row["existing_prof_flag"] for row in fiber_rows),
        "compressed_raw_quotient_row_count": sum(
            row["compressed_raw_quotient_flag"] for row in fiber_rows
        ),
        "current_raw_owner_support_flag": 1,
        "current_compressed_raw_lift_flag": 1,
        "current_materialized_raw_path_flag": 0,
        "current_markov_only_quotient_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    owner_hash = hashlib.sha256(
        digest_text(OWNER_COLUMNS, owner_rows).encode("ascii")
    ).hexdigest()
    component_hash = hashlib.sha256(
        digest_text(COMPONENT_COLUMNS, component_rows).encode("ascii")
    ).hexdigest()
    horizon_hash = hashlib.sha256(
        digest_text(HORIZON_COLUMNS, horizon_rows).encode("ascii")
    ).hexdigest()
    fiber_hash = hashlib.sha256(
        digest_text(FIBER_COLUMNS, fiber_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": input_reports,
        "node_rows": node_rows,
        "owner_rows": owner_rows,
        "component_rows": component_rows,
        "horizon_rows": horizon_rows,
        "fiber_rows": fiber_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "owner_table": table_from_rows(OWNER_COLUMNS, owner_rows),
        "component_table": table_from_rows(COMPONENT_COLUMNS, component_rows),
        "horizon_table": table_from_rows(HORIZON_COLUMNS, horizon_rows),
        "fiber_table": table_from_rows(FIBER_COLUMNS, fiber_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "owner_hash": owner_hash,
        "component_hash": component_hash,
        "horizon_hash": horizon_hash,
        "fiber_hash": fiber_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_lln"].get("status"),
            input_reports["long_rec"].get("status"),
            input_reports["long_lap"].get("status"),
            input_reports["long_tens"].get("status"),
            input_reports["long_lift"].get("status"),
        )
        == (
            LONG_LLN_STATUS,
            LONG_REC_STATUS,
            LONG_LAP_STATUS,
            LONG_TENS_STATUS,
            LONG_LIFT_STATUS,
        ),
        "raw_tensor_owner_assignment_exact": (
            obs["raw_tensor_support_count"],
            obs["raw_tensor_coeff_sum"],
            obs["raw_owner_assignment_count"],
            obs["raw_owner_assignment_complete_flag"],
            obs["owner_raw_support_positive_count"],
            obs["owner_raw_source_cell_positive_count"],
            obs["raw_source_cell_count"],
        )
        == (1_414_965, 2_537_360, 1_414_965, 1, 259, 259, 198_029),
        "active_raw_component_fingerprint_exact": (
            obs["component_row_count"],
            obs["active_owner_count"],
            obs["active_owner_cell_count"],
            obs["active_raw_source_cell_count"],
            obs["active_raw_support_count"],
            obs["active_raw_coeff_sum"],
            obs["inactive_raw_support_count"],
            obs["inactive_raw_coeff_sum"],
            rows["component_hash"],
        )
        == (
            3,
            51,
            749_239,
            136_589,
            1_096_591,
            1_985_840,
            318_374,
            551_520,
            COMPONENT_TEXT_HASH,
        ),
        "owner_raw_fingerprint_exact": (
            obs["owner_row_count"],
            obs["owner_cell_total"],
            rows["owner_hash"],
        )
        == (259, 970_225, OWNER_TEXT_HASH),
        "raw_target_frontier_exact": (
            obs["target_ge_owner_target_count"],
            obs["target_eq_owner_target_count"],
            obs["target_diff_min"],
            obs["target_diff_max"],
        )
        == (1_414_965, 22_044, 0, 283),
        "horizon_raw_lift_fingerprint_exact": (
            obs["horizon_row_count"],
            obs["raw_support_horizon_total_equal_count"],
            obs["raw_coeff_horizon_total_equal_count"],
            rows["horizon_hash"],
        )
        == (16, 16, 16, HORIZON_TEXT_HASH),
        "fiber_raw_lift_fingerprint_exact": (
            obs["fiber_row_count"],
            obs["gap_fiber_row_count"],
            obs["existing_fiber_row_count"],
            obs["compressed_raw_quotient_row_count"],
            obs["raw_support_lift_positive_count"],
            obs["raw_coeff_lift_positive_count"],
            rows["fiber_hash"],
        )
        == (288, 208, 80, 208, 288, 288, FIBER_TEXT_HASH),
        "current_representation_exact": (
            obs["current_raw_owner_support_flag"],
            obs["current_compressed_raw_lift_flag"],
            obs["current_materialized_raw_path_flag"],
            obs["current_markov_only_quotient_flag"],
        )
        == (1, 1, 0, 0),
        "table_shapes_match": (
            tuple(rows["owner_table"].shape),
            tuple(rows["component_table"].shape),
            tuple(rows["horizon_table"].shape),
            tuple(rows["fiber_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (259, len(OWNER_COLUMNS)),
            (3, len(COMPONENT_COLUMNS)),
            (16, len(HORIZON_COLUMNS)),
            (288, len(FIBER_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "compressed_raw_owner_lift",
        "raw_owner_assignment": {
            "raw_tensor_support_count": obs["raw_tensor_support_count"],
            "raw_tensor_coeff_sum": obs["raw_tensor_coeff_sum"],
            "raw_owner_assignment_complete": bool(
                obs["raw_owner_assignment_complete_flag"]
            ),
            "owner_raw_support_positive_count": obs[
                "owner_raw_support_positive_count"
            ],
            "raw_source_cell_count": obs["raw_source_cell_count"],
            "target_ge_owner_target_count": obs["target_ge_owner_target_count"],
            "target_eq_owner_target_count": obs["target_eq_owner_target_count"],
            "target_diff_range": [obs["target_diff_min"], obs["target_diff_max"]],
            "owner_table_sha256": sha_array(rows["owner_table"]),
            "owner_text_sha256": rows["owner_hash"],
        },
        "active_components": {
            "component_row_count": obs["component_row_count"],
            "active_owner_count": obs["active_owner_count"],
            "active_owner_cell_count": obs["active_owner_cell_count"],
            "active_raw_source_cell_count": obs["active_raw_source_cell_count"],
            "active_raw_support_count": obs["active_raw_support_count"],
            "active_raw_coeff_sum": obs["active_raw_coeff_sum"],
            "inactive_raw_support_count": obs["inactive_raw_support_count"],
            "inactive_raw_coeff_sum": obs["inactive_raw_coeff_sum"],
            "component_table_sha256": sha_array(rows["component_table"]),
            "component_text_sha256": rows["component_hash"],
        },
        "horizons": {
            "horizon_row_count": obs["horizon_row_count"],
            "raw_support_horizon_total_equal_count": obs[
                "raw_support_horizon_total_equal_count"
            ],
            "raw_coeff_horizon_total_equal_count": obs[
                "raw_coeff_horizon_total_equal_count"
            ],
            "horizon_table_sha256": sha_array(rows["horizon_table"]),
            "horizon_text_sha256": rows["horizon_hash"],
        },
        "fibers": {
            "fiber_row_count": obs["fiber_row_count"],
            "gap_fiber_row_count": obs["gap_fiber_row_count"],
            "existing_fiber_row_count": obs["existing_fiber_row_count"],
            "compressed_raw_quotient_row_count": obs[
                "compressed_raw_quotient_row_count"
            ],
            "raw_support_lift_positive_count": obs[
                "raw_support_lift_positive_count"
            ],
            "raw_coeff_lift_positive_count": obs["raw_coeff_lift_positive_count"],
            "fiber_table_sha256": sha_array(rows["fiber_table"]),
            "fiber_text_sha256": rows["fiber_hash"],
        },
        "current_representation": {
            "current_raw_owner_support_flag": obs["current_raw_owner_support_flag"],
            "current_compressed_raw_lift_flag": obs[
                "current_compressed_raw_lift_flag"
            ],
            "current_materialized_raw_path_flag": obs[
                "current_materialized_raw_path_flag"
            ],
            "current_markov_only_quotient_flag": obs[
                "current_markov_only_quotient_flag"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    raw_payload = {
        "schema": "long.raw@1",
        "object": "compressed_raw_owner_lift",
        "status": STATUS if all(checks.values()) else "LONG_RAW_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.raw.report@1",
        "status": raw_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_raw certifies that the long_lift component quotient is backed "
            "by actual raw 985-line tensor support at the owner level: every raw "
            "tensor support row maps to a long_rec owner, each active component "
            "has positive raw support and coefficient mass, and every long_tens "
            "sum-state fiber has a positive compressed raw-support and "
            "raw-coefficient lift. It still does not materialize raw address "
            "paths for the horizon-16 extension."
        ),
        "stage_protocol": {
            "draft": "read long_lln raw tensor rows, long_rec owner grid, long_lap active components, long_tens fibers, and long_lift quotient status",
            "witness": "assign raw tensor rows to owner cells and lift active component fibers by raw support and raw coefficient weights",
            "coherence": "check owner assignment, active component masses, target-frontier monotonicity, horizon/fiber fingerprints, flags, hashes, and shapes",
            "closure": "separate compressed raw-owner lift from absent materialized raw path object",
            "emit": "write long_raw artifacts and verifier hook",
        },
        "inputs": {
            "raw_tensor": input_entry(RAW_TENSOR),
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_lln_tables": input_entry(LONG_LLN_TABLES),
            "long_rec_report": input_entry(
                LONG_REC_REPORT,
                {"status": rows["input_reports"]["long_rec"].get("status")},
            ),
            "long_rec_owner": input_entry(LONG_REC_OWNER),
            "long_rec_tables": input_entry(LONG_REC_TABLES),
            "long_lap_report": input_entry(
                LONG_LAP_REPORT,
                {"status": rows["input_reports"]["long_lap"].get("status")},
            ),
            "long_lap_node": input_entry(LONG_LAP_NODE),
            "long_lap_component": input_entry(LONG_LAP_COMPONENT),
            "long_lap_tables": input_entry(LONG_LAP_TABLES),
            "long_tens_report": input_entry(
                LONG_TENS_REPORT,
                {"status": rows["input_reports"]["long_tens"].get("status")},
            ),
            "long_tens_fiber": input_entry(LONG_TENS_FIBER),
            "long_tens_horizon": input_entry(LONG_TENS_HORIZON),
            "long_tens_tables": input_entry(LONG_TENS_TABLES),
            "long_lift_report": input_entry(
                LONG_LIFT_REPORT,
                {"status": rows["input_reports"]["long_lift"].get("status")},
            ),
            "long_lift_tables": input_entry(LONG_LIFT_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "raw": relpath(OUT_DIR / "raw.json"),
            "owner_csv": relpath(OUT_DIR / "owner.csv"),
            "component_csv": relpath(OUT_DIR / "component.csv"),
            "horizon_csv": relpath(OUT_DIR / "horizon.csv"),
            "fiber_csv": relpath(OUT_DIR / "fiber.csv"),
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
                "every raw tensor support row is assigned to a long_rec owner",
                "every long_rec owner has at least one raw tensor support row and one raw source cell",
                "the eta6-active long_lap components carry positive raw support and positive raw coefficient mass",
                "every long_tens sum-state fiber has a positive compressed raw-support and raw-coefficient lift",
                "the long_lift quotient is not merely Markov-only: it is grounded in raw one-step tensor support",
            ],
            "does_not_certify_because_out_of_scope": [
                "a materialized owner-path tensor object",
                "a materialized raw source-cell path object",
                "a raw 985-line tensor-address path object for horizons 9-16",
                "a genuine long_prof horizon-16 profunctor",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_path: sample or construct explicit raw owner-path "
            "witnesses for selected horizon-9..16 gap fibers, starting with the "
            "smallest gap-fiber coefficients."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.raw.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.raw.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "raw": raw_payload,
        "owner_csv": csv_text(OWNER_COLUMNS, rows["owner_rows"]),
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "horizon_csv": csv_text(HORIZON_COLUMNS, rows["horizon_rows"]),
        "fiber_csv": csv_text(FIBER_COLUMNS, rows["fiber_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "owner_table": rows["owner_table"],
        "component_table": rows["component_table"],
        "horizon_table": rows["horizon_table"],
        "fiber_table": rows["fiber_table"],
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
    write_json(OUT_DIR / "raw.json", payloads["raw"])
    (OUT_DIR / "owner.csv").write_text(payloads["owner_csv"], encoding="utf-8")
    (OUT_DIR / "component.csv").write_text(
        payloads["component_csv"], encoding="utf-8"
    )
    (OUT_DIR / "horizon.csv").write_text(payloads["horizon_csv"], encoding="utf-8")
    (OUT_DIR / "fiber.csv").write_text(payloads["fiber_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        owner_table=payloads["owner_table"],
        component_table=payloads["component_table"],
        horizon_table=payloads["horizon_table"],
        fiber_table=payloads["fiber_table"],
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
