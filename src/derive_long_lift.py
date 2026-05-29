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
    from .derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from .derive_long_rec import OUT_DIR as LONG_REC_DIR, STATUS as LONG_REC_STATUS
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
    from derive_long_lln import OUT_DIR as LONG_LLN_DIR, STATUS as LONG_LLN_STATUS
    from derive_long_rec import OUT_DIR as LONG_REC_DIR, STATUS as LONG_REC_STATUS
    from derive_long_tens import OUT_DIR as LONG_TENS_DIR, STATUS as LONG_TENS_STATUS
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_lift"
STATUS = "LONG_LIFT_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

LONG_TENS_REPORT = LONG_TENS_DIR / "report.json"
LONG_TENS_FIBER = LONG_TENS_DIR / "fiber.csv"
LONG_TENS_HORIZON = LONG_TENS_DIR / "horizon.csv"
LONG_TENS_TABLES = LONG_TENS_DIR / "tables.npz"
LONG_LAP_REPORT = LONG_LAP_DIR / "report.json"
LONG_LAP_COMPONENT = LONG_LAP_DIR / "component.csv"
LONG_LAP_TABLES = LONG_LAP_DIR / "tables.npz"
LONG_LLN_REPORT = LONG_LLN_DIR / "report.json"
LONG_LLN_TABLES = LONG_LLN_DIR / "tables.npz"
LONG_REC_REPORT = LONG_REC_DIR / "report.json"
LONG_REC_OWNER = LONG_REC_DIR / "owner.csv"
LONG_REC_TABLES = LONG_REC_DIR / "tables.npz"
DERIVE_SCRIPT = ROOT / "src" / "derive_long_lift.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_lift.py"

COMPONENT_TEXT_HASH = (
    "cf8baf8867e64b2307f8b843f22caf723b5b2bae91e41a6aaa664f0afa9b8ba5"
)
HORIZON_TEXT_HASH = (
    "be58ca49d72f32f5f6193193d86c943d8c4223f9ac07fc2854ee8195197b0f58"
)
FIBER_TEXT_HASH = (
    "67eb8c48e1fe7db41e4f0e40205b7c3b0408150f8a63bbdd6485b633539c46ff"
)

MOD_PRIMES = (1_000_000_007, 1_000_000_009)
HORIZON_MAX = 16

COMPONENT_COLUMNS = [
    "component_id",
    "active_owner_count",
    "owner_cell_count",
    "support_occurrence_count",
    "mult_occurrence_count",
    "component_value",
    "active_owner_weight_mod_1000000007",
    "owner_cell_weight_mod_1000000007",
    "support_weight_mod_1000000007",
    "mult_weight_mod_1000000007",
    "active_owner_weight_mod_1000000009",
    "owner_cell_weight_mod_1000000009",
    "support_weight_mod_1000000009",
    "mult_weight_mod_1000000009",
]
HORIZON_COLUMNS = [
    "horizon_id",
    "sample_count",
    "sum_state_count",
    "component_path_count",
    "active_owner_path_lift_digits",
    "active_owner_path_lift_mod_1000000007",
    "active_owner_path_lift_mod_1000000009",
    "owner_cell_path_lift_digits",
    "owner_cell_path_lift_mod_1000000007",
    "owner_cell_path_lift_mod_1000000009",
    "gap_horizon_flag",
    "existing_sum_profunctor_flag",
    "compressed_sum_quotient_flag",
    "active_owner_total_equal_flag",
    "owner_cell_total_equal_flag",
]
FIBER_COLUMNS = [
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "component_fiber_path_count",
    "active_owner_fiber_lift_digits",
    "active_owner_fiber_lift_mod_1000000007",
    "active_owner_fiber_lift_mod_1000000009",
    "owner_cell_fiber_lift_digits",
    "owner_cell_fiber_lift_mod_1000000007",
    "owner_cell_fiber_lift_mod_1000000009",
    "long_tens_gap_flag",
    "existing_prof_flag",
    "active_owner_lift_positive_flag",
    "owner_cell_lift_positive_flag",
    "compressed_quotient_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "component_row_count",
    "horizon_row_count",
    "fiber_row_count",
    "active_owner_total",
    "owner_cell_total",
    "support_occurrence_total",
    "mult_occurrence_total",
    "component_path_total",
    "sum_state_total",
    "gap_sum_state_count",
    "existing_sum_state_count",
    "gap_fiber_row_count",
    "existing_fiber_row_count",
    "compressed_quotient_row_count",
    "active_owner_total_equal_count",
    "owner_cell_total_equal_count",
    "active_owner_lift_positive_count",
    "owner_cell_lift_positive_count",
    "current_materialized_owner_path_flag",
    "current_materialized_owner_cell_path_flag",
    "current_raw_line_address_lift_flag",
    "current_compressed_markov_quotient_flag",
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


def build_rows() -> dict[str, Any]:
    input_reports = {
        "long_tens": load_json(LONG_TENS_REPORT),
        "long_lap": load_json(LONG_LAP_REPORT),
        "long_lln": load_json(LONG_LLN_REPORT),
        "long_rec": load_json(LONG_REC_REPORT),
    }
    tens_fiber_rows = int_rows(read_csv_rows(LONG_TENS_FIBER))
    tens_horizon_rows = int_rows(read_csv_rows(LONG_TENS_HORIZON))
    lap_component_rows = read_csv_rows(LONG_LAP_COMPONENT)

    component_rows: list[dict[str, int]] = []
    for row in lap_component_rows:
        active_owner_count = int(row["node_count"])
        owner_cell_count = int(row["owner_cell_count"])
        support_count = int(row["support_occurrence_count"])
        mult_count = int(row["mult_occurrence_count"])
        component_rows.append(
            {
                "component_id": int(row["component_id"]),
                "active_owner_count": active_owner_count,
                "owner_cell_count": owner_cell_count,
                "support_occurrence_count": support_count,
                "mult_occurrence_count": mult_count,
                "component_value": row["component_id"],
                "active_owner_weight_mod_1000000007": active_owner_count
                % MOD_PRIMES[0],
                "owner_cell_weight_mod_1000000007": owner_cell_count
                % MOD_PRIMES[0],
                "support_weight_mod_1000000007": support_count % MOD_PRIMES[0],
                "mult_weight_mod_1000000007": mult_count % MOD_PRIMES[0],
                "active_owner_weight_mod_1000000009": active_owner_count
                % MOD_PRIMES[1],
                "owner_cell_weight_mod_1000000009": owner_cell_count
                % MOD_PRIMES[1],
                "support_weight_mod_1000000009": support_count % MOD_PRIMES[1],
                "mult_weight_mod_1000000009": mult_count % MOD_PRIMES[1],
            }
        )

    active_weights = [row["active_owner_count"] for row in component_rows]
    owner_cell_weights = [row["owner_cell_count"] for row in component_rows]
    active_coeffs = weighted_coefficients(active_weights, HORIZON_MAX)
    owner_cell_coeffs = weighted_coefficients(owner_cell_weights, HORIZON_MAX)
    active_weight_total = sum(active_weights)
    owner_cell_weight_total = sum(owner_cell_weights)

    horizon_rows: list[dict[str, int]] = []
    for row in tens_horizon_rows:
        sample_count = row["sample_count"]
        active_total = sum(active_coeffs[sample_count])
        owner_cell_total = sum(owner_cell_coeffs[sample_count])
        horizon_rows.append(
            {
                "horizon_id": row["horizon_id"],
                "sample_count": sample_count,
                "sum_state_count": row["sum_state_count"],
                "component_path_count": row["component_path_count"],
                "active_owner_path_lift_digits": len(str(active_total)),
                "active_owner_path_lift_mod_1000000007": active_total % MOD_PRIMES[0],
                "active_owner_path_lift_mod_1000000009": active_total % MOD_PRIMES[1],
                "owner_cell_path_lift_digits": len(str(owner_cell_total)),
                "owner_cell_path_lift_mod_1000000007": owner_cell_total
                % MOD_PRIMES[0],
                "owner_cell_path_lift_mod_1000000009": owner_cell_total
                % MOD_PRIMES[1],
                "gap_horizon_flag": row["object_gap_flag"],
                "existing_sum_profunctor_flag": row["profunctor_sum_object_flag"],
                "compressed_sum_quotient_flag": row["formal_sum_object_flag"],
                "active_owner_total_equal_flag": int(
                    active_total == active_weight_total**sample_count
                ),
                "owner_cell_total_equal_flag": int(
                    owner_cell_total == owner_cell_weight_total**sample_count
                ),
            }
        )

    fiber_rows: list[dict[str, int]] = []
    for row in tens_fiber_rows:
        sample_count = row["sample_count"]
        sum_value = row["sum_value"]
        active_count = active_coeffs[sample_count][sum_value]
        owner_cell_count = owner_cell_coeffs[sample_count][sum_value]
        fiber_rows.append(
            {
                "fiber_row_id": row["fiber_row_id"],
                "sample_count": sample_count,
                "sum_value": sum_value,
                "component_fiber_path_count": row["fiber_path_count"],
                "active_owner_fiber_lift_digits": len(str(active_count)),
                "active_owner_fiber_lift_mod_1000000007": active_count
                % MOD_PRIMES[0],
                "active_owner_fiber_lift_mod_1000000009": active_count
                % MOD_PRIMES[1],
                "owner_cell_fiber_lift_digits": len(str(owner_cell_count)),
                "owner_cell_fiber_lift_mod_1000000007": owner_cell_count
                % MOD_PRIMES[0],
                "owner_cell_fiber_lift_mod_1000000009": owner_cell_count
                % MOD_PRIMES[1],
                "long_tens_gap_flag": row["long_obj_object_gap_flag"],
                "existing_prof_flag": row["existing_prof_flag"],
                "active_owner_lift_positive_flag": int(active_count > 0),
                "owner_cell_lift_positive_flag": int(owner_cell_count > 0),
                "compressed_quotient_flag": row["formal_added_flag"],
            }
        )

    obs = {
        "component_row_count": len(component_rows),
        "horizon_row_count": len(horizon_rows),
        "fiber_row_count": len(fiber_rows),
        "active_owner_total": active_weight_total,
        "owner_cell_total": owner_cell_weight_total,
        "support_occurrence_total": sum(
            row["support_occurrence_count"] for row in component_rows
        ),
        "mult_occurrence_total": sum(
            row["mult_occurrence_count"] for row in component_rows
        ),
        "component_path_total": sum(row["component_path_count"] for row in horizon_rows),
        "sum_state_total": sum(row["sum_state_count"] for row in horizon_rows),
        "gap_sum_state_count": sum(
            row["sum_state_count"] for row in horizon_rows if row["gap_horizon_flag"]
        ),
        "existing_sum_state_count": sum(
            row["sum_state_count"]
            for row in horizon_rows
            if row["existing_sum_profunctor_flag"]
        ),
        "gap_fiber_row_count": sum(row["long_tens_gap_flag"] for row in fiber_rows),
        "existing_fiber_row_count": sum(row["existing_prof_flag"] for row in fiber_rows),
        "compressed_quotient_row_count": sum(
            row["compressed_quotient_flag"] for row in fiber_rows
        ),
        "active_owner_total_equal_count": sum(
            row["active_owner_total_equal_flag"] for row in horizon_rows
        ),
        "owner_cell_total_equal_count": sum(
            row["owner_cell_total_equal_flag"] for row in horizon_rows
        ),
        "active_owner_lift_positive_count": sum(
            row["active_owner_lift_positive_flag"] for row in fiber_rows
        ),
        "owner_cell_lift_positive_count": sum(
            row["owner_cell_lift_positive_flag"] for row in fiber_rows
        ),
        "current_materialized_owner_path_flag": 0,
        "current_materialized_owner_cell_path_flag": 0,
        "current_raw_line_address_lift_flag": 0,
        "current_compressed_markov_quotient_flag": 1,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
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
        "component_rows": component_rows,
        "horizon_rows": horizon_rows,
        "fiber_rows": fiber_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "component_table": table_from_rows(COMPONENT_COLUMNS, component_rows),
        "horizon_table": table_from_rows(HORIZON_COLUMNS, horizon_rows),
        "fiber_table": table_from_rows(FIBER_COLUMNS, fiber_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
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
            input_reports["long_tens"].get("status"),
            input_reports["long_lap"].get("status"),
            input_reports["long_lln"].get("status"),
            input_reports["long_rec"].get("status"),
        )
        == (LONG_TENS_STATUS, LONG_LAP_STATUS, LONG_LLN_STATUS, LONG_REC_STATUS),
        "component_fingerprint_exact": (
            obs["component_row_count"],
            obs["active_owner_total"],
            obs["owner_cell_total"],
            obs["support_occurrence_total"],
            obs["mult_occurrence_total"],
            rows["component_hash"],
        )
        == (
            3,
            51,
            749_239,
            16_261_179_264,
            88_155_095_040,
            COMPONENT_TEXT_HASH,
        ),
        "horizon_lift_fingerprint_exact": (
            obs["horizon_row_count"],
            obs["component_path_total"],
            obs["sum_state_total"],
            obs["active_owner_total_equal_count"],
            obs["owner_cell_total_equal_count"],
            rows["horizon_hash"],
        )
        == (16, 64_570_080, 288, 16, 16, HORIZON_TEXT_HASH),
        "fiber_lift_fingerprint_exact": (
            obs["fiber_row_count"],
            obs["gap_fiber_row_count"],
            obs["existing_fiber_row_count"],
            obs["compressed_quotient_row_count"],
            obs["active_owner_lift_positive_count"],
            obs["owner_cell_lift_positive_count"],
            rows["fiber_hash"],
        )
        == (288, 208, 80, 208, 288, 288, FIBER_TEXT_HASH),
        "current_representation_exact": (
            obs["current_materialized_owner_path_flag"],
            obs["current_materialized_owner_cell_path_flag"],
            obs["current_raw_line_address_lift_flag"],
            obs["current_compressed_markov_quotient_flag"],
        )
        == (0, 0, 0, 1),
        "table_shapes_match": (
            tuple(rows["component_table"].shape),
            tuple(rows["horizon_table"].shape),
            tuple(rows["fiber_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (3, len(COMPONENT_COLUMNS)),
            (16, len(HORIZON_COLUMNS)),
            (288, len(FIBER_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "finite_owner_component_lift_quotient",
        "components": {
            "component_row_count": obs["component_row_count"],
            "active_owner_total": obs["active_owner_total"],
            "owner_cell_total": obs["owner_cell_total"],
            "support_occurrence_total": obs["support_occurrence_total"],
            "mult_occurrence_total": obs["mult_occurrence_total"],
            "text_sha256": rows["component_hash"],
            "table_sha256": sha_array(rows["component_table"]),
        },
        "horizons": {
            "horizon_row_count": obs["horizon_row_count"],
            "component_path_total": obs["component_path_total"],
            "sum_state_total": obs["sum_state_total"],
            "gap_sum_state_count": obs["gap_sum_state_count"],
            "existing_sum_state_count": obs["existing_sum_state_count"],
            "active_owner_total_equal_count": obs["active_owner_total_equal_count"],
            "owner_cell_total_equal_count": obs["owner_cell_total_equal_count"],
            "text_sha256": rows["horizon_hash"],
            "table_sha256": sha_array(rows["horizon_table"]),
        },
        "fibers": {
            "fiber_row_count": obs["fiber_row_count"],
            "gap_fiber_row_count": obs["gap_fiber_row_count"],
            "existing_fiber_row_count": obs["existing_fiber_row_count"],
            "compressed_quotient_row_count": obs["compressed_quotient_row_count"],
            "active_owner_lift_positive_count": obs[
                "active_owner_lift_positive_count"
            ],
            "owner_cell_lift_positive_count": obs["owner_cell_lift_positive_count"],
            "text_sha256": rows["fiber_hash"],
            "table_sha256": sha_array(rows["fiber_table"]),
        },
        "current_representation": {
            "current_materialized_owner_path_flag": obs[
                "current_materialized_owner_path_flag"
            ],
            "current_materialized_owner_cell_path_flag": obs[
                "current_materialized_owner_cell_path_flag"
            ],
            "current_raw_line_address_lift_flag": obs[
                "current_raw_line_address_lift_flag"
            ],
            "current_compressed_markov_quotient_flag": obs[
                "current_compressed_markov_quotient_flag"
            ],
        },
        "observable_table_sha256": sha_array(rows["observable_table"]),
    }
    lift_payload = {
        "schema": "long.lift@1",
        "object": "finite_owner_component_lift_quotient",
        "status": STATUS if all(checks.values()) else "LONG_LIFT_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.lift.report@1",
        "status": lift_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_lift certifies the owner/component lift of the long_tens "
            "component-path fibers. Each of the 288 sum-state fibers has a "
            "positive active-owner lift and a positive owner-cell lift through "
            "the long_lap component masses, but the current artifacts still "
            "represent the horizon-16 extension only as a compressed Markov "
            "quotient: no owner-path, owner-cell-path, or raw 985-line address "
            "lift has been materialized or certified."
        ),
        "stage_protocol": {
            "draft": "read long_tens fibers and long_lap component owner/cell masses",
            "witness": "lift component-value fibers by coefficients of weighted polynomials over active owners and owner cells",
            "coherence": "check input status, component/horizon/fiber fingerprints, positivity, representation flags, hashes, and shapes",
            "closure": "emit component, horizon, fiber, table, certificate, manifest, and report artifacts",
            "emit": "write long_lift artifacts and verifier hook",
        },
        "inputs": {
            "long_tens_report": input_entry(
                LONG_TENS_REPORT,
                {"status": rows["input_reports"]["long_tens"].get("status")},
            ),
            "long_tens_fiber": input_entry(LONG_TENS_FIBER),
            "long_tens_horizon": input_entry(LONG_TENS_HORIZON),
            "long_tens_tables": input_entry(LONG_TENS_TABLES),
            "long_lap_report": input_entry(
                LONG_LAP_REPORT,
                {"status": rows["input_reports"]["long_lap"].get("status")},
            ),
            "long_lap_component": input_entry(LONG_LAP_COMPONENT),
            "long_lap_tables": input_entry(LONG_LAP_TABLES),
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "lift": relpath(OUT_DIR / "lift.json"),
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
                "the three component values lift to 51 active owners and 749,239 owner cells",
                "every long_tens sum-state fiber has positive active-owner and owner-cell lift counts",
                "the 208 gap rows remain exactly the compressed quotient rows after owner/component lifting",
                "the current certified artifacts contain no materialized owner-path, owner-cell-path, or raw-line-address lift",
            ],
            "does_not_certify_because_out_of_scope": [
                "a materialized owner-path tensor object",
                "a materialized owner-cell-path tensor object",
                "a raw 985-line tensor-address lift for horizons 9-16",
                "a genuine long_prof horizon-16 profunctor",
                "an infinite-horizon LLN theorem",
            ],
        },
        "next_highest_yield_item": (
            "Build long_raw: test a compressed raw-line-address lift using "
            "owner_cell_count fibers against the 985-line tensor support, to "
            "separate a realizable finite lift from a Markov-only quotient."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.lift.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.lift.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "lift": lift_payload,
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "horizon_csv": csv_text(HORIZON_COLUMNS, rows["horizon_rows"]),
        "fiber_csv": csv_text(FIBER_COLUMNS, rows["fiber_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
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
    write_json(OUT_DIR / "lift.json", payloads["lift"])
    (OUT_DIR / "component.csv").write_text(
        payloads["component_csv"], encoding="utf-8"
    )
    (OUT_DIR / "horizon.csv").write_text(payloads["horizon_csv"], encoding="utf-8")
    (OUT_DIR / "fiber.csv").write_text(payloads["fiber_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
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
