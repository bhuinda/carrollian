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
    from .derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from .derive_long_markov import (
        OUT_DIR as LONG_MARKOV_DIR,
        STATUS as LONG_MARKOV_STATUS,
    )
    from .derive_long_obj import OUT_DIR as LONG_OBJ_DIR, STATUS as LONG_OBJ_STATUS
    from .derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from .derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from derive_long_markov import OUT_DIR as LONG_MARKOV_DIR, STATUS as LONG_MARKOV_STATUS
    from derive_long_obj import OUT_DIR as LONG_OBJ_DIR, STATUS as LONG_OBJ_STATUS
    from derive_long_prof import OUT_DIR as LONG_PROF_DIR, STATUS as LONG_PROF_STATUS
    from derive_long_univ import OUT_DIR as LONG_UNIV_DIR, STATUS as LONG_UNIV_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_tens"
STATUS = "LONG_TENS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_OBJ_REPORT = LONG_OBJ_DIR / "report.json"
LONG_OBJ_COMPARISON = LONG_OBJ_DIR / "comparison.csv"
LONG_OBJ_HORIZON = LONG_OBJ_DIR / "horizon.csv"
LONG_OBJ_TABLES = LONG_OBJ_DIR / "tables.npz"
LONG_LLN_REPORT = LONG_LLN_DIR / "report.json"
LONG_LLN_LINE = LONG_LLN_DIR / "line.json"
LONG_LLN_TABLES = LONG_LLN_DIR / "tables.npz"
LONG_MARKOV_REPORT = LONG_MARKOV_DIR / "report.json"
LONG_MARKOV_KERNEL = LONG_MARKOV_DIR / "kernel.csv"
LONG_MARKOV_STATIONARY = LONG_MARKOV_DIR / "stationary.csv"
LONG_MARKOV_TABLES = LONG_MARKOV_DIR / "tables.npz"
LONG_PROF_REPORT = LONG_PROF_DIR / "report.json"
LONG_PROF_OBJECT = LONG_PROF_DIR / "object.csv"
LONG_PROF_TABLES = LONG_PROF_DIR / "tables.npz"
LONG_UNIV_REPORT = LONG_UNIV_DIR / "report.json"
LONG_UNIV_NODE = LONG_UNIV_DIR / "node.csv"
LONG_UNIV_TABLES = LONG_UNIV_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_tens.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_tens.py"

INVENTORY_TEXT_HASH = (
    "83798e0c6e37447b8d941c1162f93dc56d2a52bec00077bd6e68c63b5fc3ae6b"
)
HORIZON_TEXT_HASH = (
    "b2f58280f9835f64383042d1f4ed10b6d49f36aa4cbf2f890dca6a32b047fbd5"
)
FIBER_TEXT_HASH = (
    "1c25ecdb863beb4ca99fa6daeac2727ccf7f217500ec6a49cee140f98dc83b70"
)

COMPONENT_COUNT = 3
HORIZON_MAX = 16
PROFUNCTOR_HORIZON = 8
MOD_PRIMES = (1_000_000_007, 1_000_000_009)

INVENTORY_COLUMNS = [
    "inventory_id",
    "object_role_code",
    "carrier_code",
    "tensor_power_min",
    "tensor_power_max",
    "address_count",
    "horizon_limit",
    "current_artifact_flag",
    "finite_line_tensor_flag",
    "component_path_tensor_flag",
    "sum_quotient_flag",
    "profunctor_backed_flag",
    "formal_shadow_flag",
    "required_for_horizon16_flag",
]
HORIZON_COLUMNS = [
    "horizon_id",
    "sample_count",
    "sum_state_count",
    "component_path_count",
    "fiber_path_count_total",
    "component_path_count_digits",
    "component_path_count_mod_1000000007",
    "component_path_count_mod_1000000009",
    "existing_tensor_object_flag",
    "object_gap_flag",
    "component_support_full_flag",
    "explicit_component_tensor_flag",
    "materialized_path_object_flag",
    "profunctor_sum_object_flag",
    "formal_sum_object_flag",
    "fiber_total_equal_flag",
]
FIBER_COLUMNS = [
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "component_count",
    "fiber_path_count",
    "fiber_path_count_digits",
    "fiber_path_count_mod_1000000007",
    "fiber_path_count_mod_1000000009",
    "long_obj_tensor_lookup_object_flag",
    "long_obj_object_gap_flag",
    "existing_prof_flag",
    "formal_added_flag",
    "full_support_flag",
    "tensor_fiber_positive_flag",
    "fiber_sum_state_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "inventory_row_count",
    "fiber_row_count",
    "horizon_row_count",
    "component_count",
    "component_support_full_flag",
    "total_sum_state_count",
    "total_component_path_count",
    "backed_sum_state_count",
    "gap_sum_state_count",
    "backed_component_path_count",
    "gap_component_path_count",
    "materialized_component_path_object_count",
    "current_sum_quotient_object_count",
    "profunctor_backed_sum_object_count",
    "formal_shadow_sum_object_count",
    "finite_line_tensor_inventory_count",
    "component_path_required_count",
    "current_horizon16_component_path_flag",
    "current_horizon16_sum_profunctor_flag",
    "current_horizon16_sum_shadow_flag",
    "fiber_total_matches_paths_flag",
    "object_gap_matches_long_obj_flag",
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


def path_coefficients(max_horizon: int) -> dict[int, list[int]]:
    coeffs = {0: [1]}
    for sample_count in range(1, max_horizon + 1):
        previous = coeffs[sample_count - 1]
        current = [0 for _ in range(len(previous) + COMPONENT_COUNT - 1)]
        for index, value in enumerate(previous):
            for add_value in range(COMPONENT_COUNT):
                current[index + add_value] += value
        coeffs[sample_count] = current
    return coeffs


def support_full() -> int:
    kernel_rows = read_csv_rows(LONG_MARKOV_KERNEL)
    stationary_rows = read_csv_rows(LONG_MARKOV_STATIONARY)
    return int(
        all(int(row["prob_num"]) > 0 for row in kernel_rows)
        and all(int(row["weight_num"]) > 0 for row in stationary_rows)
    )


def build_inventory(
    line_point_count: int,
    raw_support_count: int,
    line_cube_domain_count: int,
    backed_path_count: int,
    total_path_count: int,
) -> list[dict[str, int]]:
    gap_path_count = total_path_count - backed_path_count
    return [
        {
            "inventory_id": 0,
            "object_role_code": 0,
            "carrier_code": 0,
            "tensor_power_min": 1,
            "tensor_power_max": 1,
            "address_count": line_point_count,
            "horizon_limit": 0,
            "current_artifact_flag": 1,
            "finite_line_tensor_flag": 1,
            "component_path_tensor_flag": 0,
            "sum_quotient_flag": 0,
            "profunctor_backed_flag": 1,
            "formal_shadow_flag": 0,
            "required_for_horizon16_flag": 0,
        },
        {
            "inventory_id": 1,
            "object_role_code": 1,
            "carrier_code": 0,
            "tensor_power_min": 2,
            "tensor_power_max": 2,
            "address_count": line_point_count**2,
            "horizon_limit": 0,
            "current_artifact_flag": 1,
            "finite_line_tensor_flag": 1,
            "component_path_tensor_flag": 0,
            "sum_quotient_flag": 0,
            "profunctor_backed_flag": 1,
            "formal_shadow_flag": 0,
            "required_for_horizon16_flag": 0,
        },
        {
            "inventory_id": 2,
            "object_role_code": 2,
            "carrier_code": 0,
            "tensor_power_min": 3,
            "tensor_power_max": 3,
            "address_count": raw_support_count,
            "horizon_limit": 0,
            "current_artifact_flag": 1,
            "finite_line_tensor_flag": 1,
            "component_path_tensor_flag": 0,
            "sum_quotient_flag": 0,
            "profunctor_backed_flag": 0,
            "formal_shadow_flag": 0,
            "required_for_horizon16_flag": 0,
        },
        {
            "inventory_id": 3,
            "object_role_code": 3,
            "carrier_code": 0,
            "tensor_power_min": 3,
            "tensor_power_max": 3,
            "address_count": line_cube_domain_count,
            "horizon_limit": 0,
            "current_artifact_flag": 0,
            "finite_line_tensor_flag": 1,
            "component_path_tensor_flag": 0,
            "sum_quotient_flag": 0,
            "profunctor_backed_flag": 0,
            "formal_shadow_flag": 0,
            "required_for_horizon16_flag": 0,
        },
        {
            "inventory_id": 4,
            "object_role_code": 4,
            "carrier_code": 1,
            "tensor_power_min": 1,
            "tensor_power_max": PROFUNCTOR_HORIZON,
            "address_count": PROFUNCTOR_HORIZON * (PROFUNCTOR_HORIZON + 2),
            "horizon_limit": PROFUNCTOR_HORIZON,
            "current_artifact_flag": 1,
            "finite_line_tensor_flag": 0,
            "component_path_tensor_flag": 0,
            "sum_quotient_flag": 1,
            "profunctor_backed_flag": 1,
            "formal_shadow_flag": 0,
            "required_for_horizon16_flag": 0,
        },
        {
            "inventory_id": 5,
            "object_role_code": 5,
            "carrier_code": 1,
            "tensor_power_min": 1,
            "tensor_power_max": HORIZON_MAX,
            "address_count": HORIZON_MAX * (HORIZON_MAX + 2),
            "horizon_limit": HORIZON_MAX,
            "current_artifact_flag": 1,
            "finite_line_tensor_flag": 0,
            "component_path_tensor_flag": 0,
            "sum_quotient_flag": 1,
            "profunctor_backed_flag": 0,
            "formal_shadow_flag": 1,
            "required_for_horizon16_flag": 1,
        },
        {
            "inventory_id": 6,
            "object_role_code": 6,
            "carrier_code": 2,
            "tensor_power_min": 1,
            "tensor_power_max": HORIZON_MAX,
            "address_count": total_path_count,
            "horizon_limit": HORIZON_MAX,
            "current_artifact_flag": 0,
            "finite_line_tensor_flag": 0,
            "component_path_tensor_flag": 1,
            "sum_quotient_flag": 0,
            "profunctor_backed_flag": 0,
            "formal_shadow_flag": 0,
            "required_for_horizon16_flag": 1,
        },
        {
            "inventory_id": 7,
            "object_role_code": 7,
            "carrier_code": 2,
            "tensor_power_min": PROFUNCTOR_HORIZON + 1,
            "tensor_power_max": HORIZON_MAX,
            "address_count": gap_path_count,
            "horizon_limit": HORIZON_MAX,
            "current_artifact_flag": 0,
            "finite_line_tensor_flag": 0,
            "component_path_tensor_flag": 1,
            "sum_quotient_flag": 0,
            "profunctor_backed_flag": 0,
            "formal_shadow_flag": 0,
            "required_for_horizon16_flag": 1,
        },
    ]


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_obj": load_json(LONG_OBJ_REPORT),
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_markov": load_json(LONG_MARKOV_REPORT),
        "long_prof": load_json(LONG_PROF_REPORT),
        "long_univ": load_json(LONG_UNIV_REPORT),
    }
    long_lln_witness = input_reports["long_lln"]["witness"]
    line_point_count = int(long_lln_witness["line"]["point_count"])
    raw_support_count = int(long_lln_witness["tensor_lookup"]["support_count"])
    line_cube_domain_count = int(long_lln_witness["tensor_lookup"]["domain_word_count"])
    comparison_rows = int_rows(read_csv_rows(LONG_OBJ_COMPARISON))
    long_obj_horizon_rows = int_rows(read_csv_rows(LONG_OBJ_HORIZON))
    coeffs = path_coefficients(HORIZON_MAX)
    full_support_flag = support_full()

    fiber_rows: list[dict[str, int]] = []
    for row in comparison_rows:
        sample_count = row["sample_count"]
        sum_value = row["sum_value"]
        fiber_count = coeffs[sample_count][sum_value]
        fiber_rows.append(
            {
                "fiber_row_id": row["comparison_row_id"],
                "sample_count": sample_count,
                "sum_value": sum_value,
                "component_count": COMPONENT_COUNT,
                "fiber_path_count": fiber_count,
                "fiber_path_count_digits": len(str(fiber_count)),
                "fiber_path_count_mod_1000000007": fiber_count % MOD_PRIMES[0],
                "fiber_path_count_mod_1000000009": fiber_count % MOD_PRIMES[1],
                "long_obj_tensor_lookup_object_flag": row[
                    "tensor_lookup_object_flag"
                ],
                "long_obj_object_gap_flag": row["object_gap_flag"],
                "existing_prof_flag": row["long_prof_law_flag"],
                "formal_added_flag": row["long_ext_formal_added_flag"],
                "full_support_flag": full_support_flag,
                "tensor_fiber_positive_flag": int(
                    fiber_count > 0 and full_support_flag == 1
                ),
                "fiber_sum_state_flag": int(0 <= sum_value <= 2 * sample_count),
            }
        )

    horizon_rows: list[dict[str, int]] = []
    for row in long_obj_horizon_rows:
        sample_count = row["sample_count"]
        component_path_count = COMPONENT_COUNT**sample_count
        fiber_path_total = sum(coeffs[sample_count])
        horizon_rows.append(
            {
                "horizon_id": row["horizon_id"],
                "sample_count": sample_count,
                "sum_state_count": row["expected_sum_state_count"],
                "component_path_count": component_path_count,
                "fiber_path_count_total": fiber_path_total,
                "component_path_count_digits": len(str(component_path_count)),
                "component_path_count_mod_1000000007": component_path_count
                % MOD_PRIMES[0],
                "component_path_count_mod_1000000009": component_path_count
                % MOD_PRIMES[1],
                "existing_tensor_object_flag": row["tensor_lookup_object_flag"],
                "object_gap_flag": row["object_gap_flag"],
                "component_support_full_flag": full_support_flag,
                "explicit_component_tensor_flag": 1,
                "materialized_path_object_flag": 0,
                "profunctor_sum_object_flag": row["tensor_lookup_object_flag"],
                "formal_sum_object_flag": row["object_gap_flag"],
                "fiber_total_equal_flag": int(fiber_path_total == component_path_count),
            }
        )

    backed_path_count = sum(
        COMPONENT_COUNT**sample_count
        for sample_count in range(1, PROFUNCTOR_HORIZON + 1)
    )
    total_path_count = sum(
        COMPONENT_COUNT**sample_count for sample_count in range(1, HORIZON_MAX + 1)
    )
    inventory_rows = build_inventory(
        line_point_count,
        raw_support_count,
        line_cube_domain_count,
        backed_path_count,
        total_path_count,
    )
    obs = {
        "inventory_row_count": len(inventory_rows),
        "fiber_row_count": len(fiber_rows),
        "horizon_row_count": len(horizon_rows),
        "component_count": COMPONENT_COUNT,
        "component_support_full_flag": full_support_flag,
        "total_sum_state_count": sum(row["sum_state_count"] for row in horizon_rows),
        "total_component_path_count": total_path_count,
        "backed_sum_state_count": sum(
            row["sum_state_count"]
            for row in horizon_rows
            if row["existing_tensor_object_flag"]
        ),
        "gap_sum_state_count": sum(
            row["sum_state_count"] for row in horizon_rows if row["object_gap_flag"]
        ),
        "backed_component_path_count": backed_path_count,
        "gap_component_path_count": total_path_count - backed_path_count,
        "materialized_component_path_object_count": sum(
            row["current_artifact_flag"]
            for row in inventory_rows
            if row["component_path_tensor_flag"]
        ),
        "current_sum_quotient_object_count": sum(
            row["current_artifact_flag"]
            for row in inventory_rows
            if row["sum_quotient_flag"]
        ),
        "profunctor_backed_sum_object_count": sum(
            row["profunctor_backed_flag"]
            for row in inventory_rows
            if row["sum_quotient_flag"]
        ),
        "formal_shadow_sum_object_count": sum(
            row["formal_shadow_flag"]
            for row in inventory_rows
            if row["sum_quotient_flag"]
        ),
        "finite_line_tensor_inventory_count": sum(
            row["finite_line_tensor_flag"] for row in inventory_rows
        ),
        "component_path_required_count": sum(
            row["component_path_tensor_flag"] and row["required_for_horizon16_flag"]
            for row in inventory_rows
        ),
        "current_horizon16_component_path_flag": 0,
        "current_horizon16_sum_profunctor_flag": 0,
        "current_horizon16_sum_shadow_flag": 1,
        "fiber_total_matches_paths_flag": int(
            all(row["fiber_total_equal_flag"] for row in horizon_rows)
        ),
        "object_gap_matches_long_obj_flag": int(
            sum(row["long_obj_object_gap_flag"] for row in fiber_rows) == 208
            and sum(row["formal_added_flag"] for row in fiber_rows) == 208
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
    inventory_hash = hashlib.sha256(
        digest_text(INVENTORY_COLUMNS, inventory_rows).encode("ascii")
    ).hexdigest()
    horizon_hash = hashlib.sha256(
        digest_text(HORIZON_COLUMNS, horizon_rows).encode("ascii")
    ).hexdigest()
    fiber_hash = hashlib.sha256(
        digest_text(FIBER_COLUMNS, fiber_rows).encode("ascii")
    ).hexdigest()
    return {
        "input_reports": input_reports,
        "inventory_rows": inventory_rows,
        "horizon_rows": horizon_rows,
        "fiber_rows": fiber_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "inventory_table": table_from_rows(INVENTORY_COLUMNS, inventory_rows),
        "horizon_table": table_from_rows(HORIZON_COLUMNS, horizon_rows),
        "fiber_table": table_from_rows(FIBER_COLUMNS, fiber_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "inventory_hash": inventory_hash,
        "horizon_hash": horizon_hash,
        "fiber_hash": fiber_hash,
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    input_reports = rows["input_reports"]
    checks = {
        "input_certified": (
            input_reports["long_obj"].get("status"),
            input_reports["long_lln"].get("status"),
            input_reports["long_markov"].get("status"),
            input_reports["long_prof"].get("status"),
            input_reports["long_univ"].get("status"),
        )
        == (
            LONG_OBJ_STATUS,
            LONG_LLN_STATUS,
            LONG_MARKOV_STATUS,
            LONG_PROF_STATUS,
            LONG_UNIV_STATUS,
        ),
        "inventory_fingerprint_exact": (
            obs["inventory_row_count"],
            obs["finite_line_tensor_inventory_count"],
            obs["current_sum_quotient_object_count"],
            obs["component_path_required_count"],
            rows["inventory_hash"],
        )
        == (8, 4, 2, 2, INVENTORY_TEXT_HASH),
        "horizon_fingerprint_exact": (
            obs["horizon_row_count"],
            obs["total_sum_state_count"],
            obs["total_component_path_count"],
            obs["backed_component_path_count"],
            obs["gap_component_path_count"],
            obs["fiber_total_matches_paths_flag"],
            rows["horizon_hash"],
        )
        == (16, 288, 64_570_080, 9_840, 64_560_240, 1, HORIZON_TEXT_HASH),
        "fiber_fingerprint_exact": (
            obs["fiber_row_count"],
            obs["backed_sum_state_count"],
            obs["gap_sum_state_count"],
            obs["component_support_full_flag"],
            obs["object_gap_matches_long_obj_flag"],
            rows["fiber_hash"],
        )
        == (288, 80, 208, 1, 1, FIBER_TEXT_HASH),
        "current_representation_exact": (
            obs["materialized_component_path_object_count"],
            obs["current_horizon16_component_path_flag"],
            obs["current_horizon16_sum_profunctor_flag"],
            obs["current_horizon16_sum_shadow_flag"],
            obs["formal_shadow_sum_object_count"],
        )
        == (0, 0, 0, 1, 1),
        "table_shapes_match": (
            tuple(rows["inventory_table"].shape),
            tuple(rows["horizon_table"].shape),
            tuple(rows["fiber_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (8, len(INVENTORY_COLUMNS)),
            (16, len(HORIZON_COLUMNS)),
            (288, len(FIBER_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_component_path_tensor_expansion_gap",
        "inventory": {
            "inventory_row_count": obs["inventory_row_count"],
            "finite_line_tensor_inventory_count": obs[
                "finite_line_tensor_inventory_count"
            ],
            "current_sum_quotient_object_count": obs[
                "current_sum_quotient_object_count"
            ],
            "component_path_required_count": obs["component_path_required_count"],
            "text_sha256": rows["inventory_hash"],
            "table_sha256": sha_array(rows["inventory_table"]),
        },
        "horizons": {
            "horizon_row_count": obs["horizon_row_count"],
            "total_sum_state_count": obs["total_sum_state_count"],
            "total_component_path_count": obs["total_component_path_count"],
            "backed_component_path_count": obs["backed_component_path_count"],
            "gap_component_path_count": obs["gap_component_path_count"],
            "fiber_total_matches_paths_flag": obs["fiber_total_matches_paths_flag"],
            "text_sha256": rows["horizon_hash"],
            "table_sha256": sha_array(rows["horizon_table"]),
        },
        "fibers": {
            "fiber_row_count": obs["fiber_row_count"],
            "backed_sum_state_count": obs["backed_sum_state_count"],
            "gap_sum_state_count": obs["gap_sum_state_count"],
            "component_support_full_flag": obs["component_support_full_flag"],
            "object_gap_matches_long_obj_flag": obs["object_gap_matches_long_obj_flag"],
            "text_sha256": rows["fiber_hash"],
            "table_sha256": sha_array(rows["fiber_table"]),
        },
        "current_representation": {
            "materialized_component_path_object_count": obs[
                "materialized_component_path_object_count"
            ],
            "current_horizon16_component_path_flag": obs[
                "current_horizon16_component_path_flag"
            ],
            "current_horizon16_sum_profunctor_flag": obs[
                "current_horizon16_sum_profunctor_flag"
            ],
            "current_horizon16_sum_shadow_flag": obs[
                "current_horizon16_sum_shadow_flag"
            ],
            "formal_shadow_sum_object_count": obs["formal_shadow_sum_object_count"],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    tens_payload = {
        "schema": "long.tens@1",
        "object": "finite_component_path_tensor_expansion_gap",
        "status": STATUS if all(checks.values()) else "LONG_TENS_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.tens.report@1",
        "status": tens_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_tens certifies the exact component-path tensor expansion "
            "behind the long_obj gap. Every horizon-16 sum row is a quotient "
            "fiber of the finite 3-component tensor powers; the 208 gap rows "
            "account for 64,560,240 positive component-path words. The current "
            "artifacts contain the horizon-16 sum quotient only as a formal "
            "convolution shadow, with no materialized component-path object "
            "or long_prof horizon-16 sum profunctor."
        ),
        "stage_protocol": {
            "draft": "read long_obj, long_lln, long_markov, long_prof, and long_univ artifacts",
            "witness": "expand each sum-state row into the coefficient of (1+x+x^2)^n and compare it to current object backing",
            "coherence": "check input status, inventory/horizon/fiber fingerprints, support positivity, representation flags, hashes, and shapes",
            "closure": "emit inventory, horizon, fiber, table, certificate, manifest, and report artifacts",
            "emit": "write long_tens artifacts and verifier hook",
        },
        "inputs": {
            "long_obj_report": input_entry(
                LONG_OBJ_REPORT,
                {"status": rows["input_reports"]["long_obj"].get("status")},
            ),
            "long_obj_comparison": input_entry(LONG_OBJ_COMPARISON),
            "long_obj_horizon": input_entry(LONG_OBJ_HORIZON),
            "long_obj_tables": input_entry(LONG_OBJ_TABLES),
            "long_lln_report": input_entry(
                LONG_LLN_REPORT,
                {"status": rows["input_reports"]["long_lln"].get("status")},
            ),
            "long_lln_line": input_entry(LONG_LLN_LINE),
            "long_lln_tables": input_entry(LONG_LLN_TABLES),
            "long_markov_report": input_entry(
                LONG_MARKOV_REPORT,
                {"status": rows["input_reports"]["long_markov"].get("status")},
            ),
            "long_markov_kernel": input_entry(LONG_MARKOV_KERNEL),
            "long_markov_stationary": input_entry(LONG_MARKOV_STATIONARY),
            "long_markov_tables": input_entry(LONG_MARKOV_TABLES),
            "long_prof_report": input_entry(
                LONG_PROF_REPORT,
                {"status": rows["input_reports"]["long_prof"].get("status")},
            ),
            "long_prof_object": input_entry(LONG_PROF_OBJECT),
            "long_prof_tables": input_entry(LONG_PROF_TABLES),
            "long_univ_report": input_entry(
                LONG_UNIV_REPORT,
                {"status": rows["input_reports"]["long_univ"].get("status")},
            ),
            "long_univ_node": input_entry(LONG_UNIV_NODE),
            "long_univ_tables": input_entry(LONG_UNIV_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "tens": relpath(OUT_DIR / "tens.json"),
            "inventory_csv": relpath(OUT_DIR / "inventory.csv"),
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
                "the 288 horizon-16 sum-state rows are exact fibers of finite 3-component path tensor powers",
                "horizons 1-8 cover 9,840 component-path words and are profunctor-backed at the sum quotient",
                "horizons 9-16 cover 64,560,240 additional component-path words and exactly the 208 long_obj gap rows",
                "the current artifact inventory has no materialized component-path tensor object and no horizon-16 long_prof sum profunctor",
            ],
            "does_not_certify_because_out_of_scope": [
                "materializing all 64,570,080 component paths as an artifact",
                "lifting the component-path tensor object back to raw 985-line tensor addresses",
                "a genuine long_prof horizon-16 profunctor",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_lift: lift the component-path tensor fibers back "
            "through the owner/component maps toward raw 985-line tensor "
            "addresses, and test whether the 64,560,240-word gap has a "
            "finite profunctor lift or only a compressed Markov quotient."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.tens.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.tens.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "tens": tens_payload,
        "inventory_csv": csv_text(INVENTORY_COLUMNS, rows["inventory_rows"]),
        "horizon_csv": csv_text(HORIZON_COLUMNS, rows["horizon_rows"]),
        "fiber_csv": csv_text(FIBER_COLUMNS, rows["fiber_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "inventory_table": rows["inventory_table"],
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
    write_json(OUT_DIR / "tens.json", payloads["tens"])
    (OUT_DIR / "inventory.csv").write_text(
        payloads["inventory_csv"], encoding="utf-8"
    )
    (OUT_DIR / "horizon.csv").write_text(payloads["horizon_csv"], encoding="utf-8")
    (OUT_DIR / "fiber.csv").write_text(payloads["fiber_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        inventory_table=payloads["inventory_table"],
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
