from __future__ import annotations

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
    from .derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_typed_simple_object_registry import (
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from derive_long_raw import csv_text, digest_text, int_rows, read_csv_rows, table_from_rows
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "long_paths"
STATUS = "LONG_PATHS_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID
INDEX_PATH = D20_INVARIANTS / "proof_obligations" / "index.json"

PROOF_ROOT = D20_INVARIANTS / "proof_obligations"
LONG_PATH_REPORT = PROOF_ROOT / "long_path" / "report.json"
LONG_PATH_COMPONENT = PROOF_ROOT / "long_path" / "component.csv"
LONG_PATH_PATH = PROOF_ROOT / "long_path" / "path.csv"
LONG_PATH_TABLES = PROOF_ROOT / "long_path" / "tables.npz"
LONG_POBJ_REPORT = PROOF_ROOT / "long_pobj" / "report.json"
LONG_POBJ_TABLES = PROOF_ROOT / "long_pobj" / "tables.npz"
LONG_TENS_REPORT = PROOF_ROOT / "long_tens" / "report.json"
LONG_TENS_FIBER = PROOF_ROOT / "long_tens" / "fiber.csv"
LONG_TENS_HORIZON = PROOF_ROOT / "long_tens" / "horizon.csv"
LONG_TENS_TABLES = PROOF_ROOT / "long_tens" / "tables.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_long_paths.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_long_paths.py"

MOD_PRIMES = (1_000_000_007, 1_000_000_009)

COMPONENT_COLUMNS = [
    "component_id",
    "raw_support_count",
    "raw_coeff_sum",
    "representative_raw_row_id",
    "representative_owner_active_flag",
]
FIBER_COLUMNS = [
    "fiber_row_id",
    "sample_count",
    "sum_value",
    "component_path_count",
    "raw_support_path_count_digits",
    "raw_support_path_count_mod_1000000007",
    "raw_support_path_count_mod_1000000009",
    "raw_coeff_path_mass_digits",
    "raw_coeff_path_mass_mod_1000000007",
    "raw_coeff_path_mass_mod_1000000009",
    "selected_witness_count",
    "missing_component_path_count",
    "long_tens_gap_flag",
    "compressed_raw_product_family_flag",
    "materialized_raw_path_family_flag",
    "exact_composable_raw_path_family_flag",
]
HORIZON_COLUMNS = [
    "horizon_id",
    "sample_count",
    "sum_state_count",
    "component_path_count",
    "raw_support_path_count_digits",
    "raw_support_path_count_mod_1000000007",
    "raw_support_path_count_mod_1000000009",
    "raw_coeff_path_mass_digits",
    "raw_coeff_path_mass_mod_1000000007",
    "raw_coeff_path_mass_mod_1000000009",
    "selected_witness_count",
    "missing_component_path_count",
    "gap_sum_state_count",
    "gap_component_path_count",
    "compressed_raw_product_family_flag",
    "materialized_raw_path_family_flag",
    "exact_composable_raw_path_family_flag",
]
OBS_COLUMNS = ["observable_id", "observable_code", "value"]
OBS_NAMES = [
    "component_row_count",
    "fiber_row_count",
    "horizon_row_count",
    "existing_fiber_count",
    "gap_fiber_count",
    "component_path_total",
    "component_path_gap_total",
    "selected_witness_count",
    "missing_component_path_count",
    "active_raw_support_count",
    "active_raw_coeff_sum",
    "raw_support_positive_fiber_count",
    "raw_coeff_positive_fiber_count",
    "max_sample_count",
    "max_raw_support_fiber_digits",
    "max_raw_coeff_fiber_digits",
    "horizon16_raw_support_total_digits",
    "horizon16_raw_coeff_total_digits",
    "compressed_raw_product_family_flag",
    "materialized_raw_path_family_flag",
    "exact_composable_raw_path_family_flag",
    "next_target_code",
    "complete_goal_claim_flag",
]
OBS_CODES = {name: index for index, name in enumerate(OBS_NAMES)}


def certified(report: dict[str, Any], status: str) -> int:
    return int(report.get("status") == status and report.get("all_checks_pass") is True)


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


def digits(value: int) -> int:
    return len(str(value))


def mod_pair(value: int) -> tuple[int, int]:
    return value % MOD_PRIMES[0], value % MOD_PRIMES[1]


def load_component_rows() -> list[dict[str, int]]:
    rows = int_rows(read_csv_rows(LONG_PATH_COMPONENT))
    return [
        {
            "component_id": row["component_id"],
            "raw_support_count": row["raw_support_count"],
            "raw_coeff_sum": row["raw_coeff_sum"],
            "representative_raw_row_id": row["representative_raw_row_id"],
            "representative_owner_active_flag": row["representative_owner_active_flag"],
        }
        for row in rows
    ]


def build_rows() -> dict[str, Any]:
    path_report = load_json(LONG_PATH_REPORT)
    pobj_report = load_json(LONG_POBJ_REPORT)
    tens_report = load_json(LONG_TENS_REPORT)
    component_rows = load_component_rows()
    path_rows = int_rows(read_csv_rows(LONG_PATH_PATH))
    tens_fiber_rows = int_rows(read_csv_rows(LONG_TENS_FIBER))
    tens_horizon_rows = int_rows(read_csv_rows(LONG_TENS_HORIZON))

    support_weights = [row["raw_support_count"] for row in component_rows]
    coeff_weights = [row["raw_coeff_sum"] for row in component_rows]
    max_horizon = max(row["sample_count"] for row in tens_horizon_rows)
    support_coeffs = weighted_coefficients(support_weights, max_horizon)
    coeff_mass = weighted_coefficients(coeff_weights, max_horizon)

    selected_by_fiber = {row["fiber_row_id"]: 1 for row in path_rows}
    fiber_rows: list[dict[str, int]] = []
    for fiber in tens_fiber_rows:
        sample_count = fiber["sample_count"]
        sum_value = fiber["sum_value"]
        support_value = support_coeffs[sample_count][sum_value]
        coeff_value = coeff_mass[sample_count][sum_value]
        support_mod0, support_mod1 = mod_pair(support_value)
        coeff_mod0, coeff_mod1 = mod_pair(coeff_value)
        selected_count = selected_by_fiber.get(fiber["fiber_row_id"], 0)
        component_path_count = fiber["fiber_path_count"]
        fiber_rows.append(
            {
                "fiber_row_id": fiber["fiber_row_id"],
                "sample_count": sample_count,
                "sum_value": sum_value,
                "component_path_count": component_path_count,
                "raw_support_path_count_digits": digits(support_value),
                "raw_support_path_count_mod_1000000007": support_mod0,
                "raw_support_path_count_mod_1000000009": support_mod1,
                "raw_coeff_path_mass_digits": digits(coeff_value),
                "raw_coeff_path_mass_mod_1000000007": coeff_mod0,
                "raw_coeff_path_mass_mod_1000000009": coeff_mod1,
                "selected_witness_count": selected_count,
                "missing_component_path_count": component_path_count - selected_count,
                "long_tens_gap_flag": fiber["long_obj_object_gap_flag"],
                "compressed_raw_product_family_flag": int(support_value > 0),
                "materialized_raw_path_family_flag": 0,
                "exact_composable_raw_path_family_flag": 0,
            }
        )

    horizon_rows: list[dict[str, int]] = []
    for horizon in tens_horizon_rows:
        sample_count = horizon["sample_count"]
        support_value = sum(support_weights) ** sample_count
        coeff_value = sum(coeff_weights) ** sample_count
        support_mod0, support_mod1 = mod_pair(support_value)
        coeff_mod0, coeff_mod1 = mod_pair(coeff_value)
        selected_count = horizon["sum_state_count"]
        component_path_count = horizon["component_path_count"]
        gap_flag = horizon["object_gap_flag"]
        horizon_rows.append(
            {
                "horizon_id": horizon["horizon_id"],
                "sample_count": sample_count,
                "sum_state_count": horizon["sum_state_count"],
                "component_path_count": component_path_count,
                "raw_support_path_count_digits": digits(support_value),
                "raw_support_path_count_mod_1000000007": support_mod0,
                "raw_support_path_count_mod_1000000009": support_mod1,
                "raw_coeff_path_mass_digits": digits(coeff_value),
                "raw_coeff_path_mass_mod_1000000007": coeff_mod0,
                "raw_coeff_path_mass_mod_1000000009": coeff_mod1,
                "selected_witness_count": selected_count,
                "missing_component_path_count": component_path_count - selected_count,
                "gap_sum_state_count": horizon["sum_state_count"] * gap_flag,
                "gap_component_path_count": component_path_count * gap_flag,
                "compressed_raw_product_family_flag": 1,
                "materialized_raw_path_family_flag": 0,
                "exact_composable_raw_path_family_flag": 0,
            }
        )

    obs = {
        "component_row_count": len(component_rows),
        "fiber_row_count": len(fiber_rows),
        "horizon_row_count": len(horizon_rows),
        "existing_fiber_count": sum(1 - row["long_tens_gap_flag"] for row in fiber_rows),
        "gap_fiber_count": sum(row["long_tens_gap_flag"] for row in fiber_rows),
        "component_path_total": sum(row["component_path_count"] for row in horizon_rows),
        "component_path_gap_total": sum(
            row["gap_component_path_count"] for row in horizon_rows
        ),
        "selected_witness_count": sum(row["selected_witness_count"] for row in fiber_rows),
        "missing_component_path_count": sum(
            row["missing_component_path_count"] for row in fiber_rows
        ),
        "active_raw_support_count": sum(support_weights),
        "active_raw_coeff_sum": sum(coeff_weights),
        "raw_support_positive_fiber_count": sum(
            row["compressed_raw_product_family_flag"] for row in fiber_rows
        ),
        "raw_coeff_positive_fiber_count": sum(
            int(row["raw_coeff_path_mass_digits"] > 0) for row in fiber_rows
        ),
        "max_sample_count": max(row["sample_count"] for row in horizon_rows),
        "max_raw_support_fiber_digits": max(
            row["raw_support_path_count_digits"] for row in fiber_rows
        ),
        "max_raw_coeff_fiber_digits": max(
            row["raw_coeff_path_mass_digits"] for row in fiber_rows
        ),
        "horizon16_raw_support_total_digits": horizon_rows[-1][
            "raw_support_path_count_digits"
        ],
        "horizon16_raw_coeff_total_digits": horizon_rows[-1][
            "raw_coeff_path_mass_digits"
        ],
        "compressed_raw_product_family_flag": 1,
        "materialized_raw_path_family_flag": 0,
        "exact_composable_raw_path_family_flag": 0,
        "next_target_code": 5,
        "complete_goal_claim_flag": 0,
    }
    obs_rows = [
        {
            "observable_id": index,
            "observable_code": OBS_CODES[name],
            "value": int(obs[name]),
        }
        for index, name in enumerate(OBS_NAMES)
    ]
    return {
        "path_report": path_report,
        "pobj_report": pobj_report,
        "tens_report": tens_report,
        "component_rows": component_rows,
        "fiber_rows": fiber_rows,
        "horizon_rows": horizon_rows,
        "obs": obs,
        "obs_rows": obs_rows,
        "component_table": table_from_rows(COMPONENT_COLUMNS, component_rows),
        "fiber_table": table_from_rows(FIBER_COLUMNS, fiber_rows),
        "horizon_table": table_from_rows(HORIZON_COLUMNS, horizon_rows),
        "observable_table": table_from_rows(OBS_COLUMNS, obs_rows),
        "component_hash": hashlib.sha256(
            digest_text(COMPONENT_COLUMNS, component_rows).encode("ascii")
        ).hexdigest(),
        "fiber_hash": hashlib.sha256(
            digest_text(FIBER_COLUMNS, fiber_rows).encode("ascii")
        ).hexdigest(),
        "horizon_hash": hashlib.sha256(
            digest_text(HORIZON_COLUMNS, horizon_rows).encode("ascii")
        ).hexdigest(),
    }


def build_payloads() -> dict[str, Any]:
    rows = build_rows()
    obs = rows["obs"]
    checks = {
        "inputs_certified": (
            certified(rows["path_report"], "LONG_PATH_CERTIFIED"),
            certified(rows["pobj_report"], "LONG_POBJ_CERTIFIED"),
            certified(rows["tens_report"], "LONG_TENS_CERTIFIED"),
        )
        == (1, 1, 1),
        "component_weights_exact": (
            obs["component_row_count"],
            obs["active_raw_support_count"],
            obs["active_raw_coeff_sum"],
        )
        == (3, 1_096_591, 1_985_840),
        "fiber_inventory_exact": (
            obs["fiber_row_count"],
            obs["existing_fiber_count"],
            obs["gap_fiber_count"],
            obs["selected_witness_count"],
        )
        == (288, 80, 208, 288),
        "component_path_inventory_exact": (
            obs["component_path_total"],
            obs["component_path_gap_total"],
            obs["missing_component_path_count"],
        )
        == (64_570_080, 64_560_240, 64_569_792),
        "compressed_raw_products_positive": (
            obs["raw_support_positive_fiber_count"],
            obs["raw_coeff_positive_fiber_count"],
            obs["compressed_raw_product_family_flag"],
        )
        == (288, 288, 1),
        "large_count_boundary_exact": (
            obs["max_sample_count"],
            obs["max_raw_support_fiber_digits"],
            obs["max_raw_coeff_fiber_digits"],
            obs["horizon16_raw_support_total_digits"],
            obs["horizon16_raw_coeff_total_digits"],
        )
        == (16, 96, 101, 97, 101),
        "path_family_not_overclaimed": (
            obs["materialized_raw_path_family_flag"],
            obs["exact_composable_raw_path_family_flag"],
            obs["next_target_code"],
            obs["complete_goal_claim_flag"],
        )
        == (0, 0, 5, 0),
        "table_shapes_match": (
            tuple(rows["component_table"].shape),
            tuple(rows["fiber_table"].shape),
            tuple(rows["horizon_table"].shape),
            tuple(rows["observable_table"].shape),
        )
        == (
            (3, len(COMPONENT_COLUMNS)),
            (288, len(FIBER_COLUMNS)),
            (16, len(HORIZON_COLUMNS)),
            (len(OBS_CODES), len(OBS_COLUMNS)),
        ),
    }
    witness = {
        "name": THEOREM_ID,
        "classification": "compressed_active_raw_product_path_family",
        "summary": {
            "fiber_row_count": obs["fiber_row_count"],
            "horizon_row_count": obs["horizon_row_count"],
            "component_path_total": obs["component_path_total"],
            "component_path_gap_total": obs["component_path_gap_total"],
            "selected_witness_count": obs["selected_witness_count"],
            "missing_component_path_count": obs["missing_component_path_count"],
            "active_raw_support_count": obs["active_raw_support_count"],
            "active_raw_coeff_sum": obs["active_raw_coeff_sum"],
            "compressed_raw_product_family_flag": obs[
                "compressed_raw_product_family_flag"
            ],
            "materialized_raw_path_family_flag": obs[
                "materialized_raw_path_family_flag"
            ],
            "exact_composable_raw_path_family_flag": obs[
                "exact_composable_raw_path_family_flag"
            ],
            "next_target": "long_measure",
            "complete_goal_claim_flag": obs["complete_goal_claim_flag"],
        },
        "component_table_sha256": sha_array(rows["component_table"]),
        "fiber_table_sha256": sha_array(rows["fiber_table"]),
        "horizon_table_sha256": sha_array(rows["horizon_table"]),
        "observable_table_sha256": sha_array(rows["observable_table"]),
        "component_text_sha256": rows["component_hash"],
        "fiber_text_sha256": rows["fiber_hash"],
        "horizon_text_sha256": rows["horizon_hash"],
    }
    paths_payload = {
        "schema": "long.paths@1",
        "object": "compressed_active_raw_product_path_family",
        "status": STATUS if all(checks.values()) else "LONG_PATHS_PROVISIONAL",
        "witness": witness,
    }
    report = {
        "schema": "long.paths.report@1",
        "status": paths_payload["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "long_paths certifies an exact compressed enumeration of the current "
            "active-component raw product path family. For each of the 288 "
            "horizon-16 sum fibers it records the full component-path count, "
            "active raw-support product count, and active raw-coefficient mass "
            "by digits and modular witnesses. This closes the product-family "
            "accounting behind the 64,570,080 component paths, including the "
            "64,560,240 gap paths, without materializing every raw address path "
            "or claiming exact C985/profunctor composability."
        ),
        "stage_protocol": {
            "draft": "read long_path, long_pobj, and long_tens witnesses",
            "witness": "emit active-component weights, per-fiber compressed raw product counts, and per-horizon totals",
            "coherence": "check source statuses, component weights, fiber inventory, component-path totals, positivity, large-count boundaries, table shapes, and hashes",
            "closure": "certify compressed product-family accounting without claiming materialized or exact-composable raw paths",
            "emit": "write long_paths artifacts and verifier hook",
        },
        "inputs": {
            "long_path_report": input_entry(
                LONG_PATH_REPORT,
                {
                    "status": rows["path_report"].get("status"),
                    "certificate_sha256": rows["path_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_path_component": input_entry(LONG_PATH_COMPONENT),
            "long_path_path": input_entry(LONG_PATH_PATH),
            "long_path_tables": input_entry(LONG_PATH_TABLES),
            "long_pobj_report": input_entry(
                LONG_POBJ_REPORT,
                {
                    "status": rows["pobj_report"].get("status"),
                    "certificate_sha256": rows["pobj_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_pobj_tables": input_entry(LONG_POBJ_TABLES),
            "long_tens_report": input_entry(
                LONG_TENS_REPORT,
                {
                    "status": rows["tens_report"].get("status"),
                    "certificate_sha256": rows["tens_report"].get(
                        "certificate_sha256"
                    ),
                },
            ),
            "long_tens_fiber": input_entry(LONG_TENS_FIBER),
            "long_tens_horizon": input_entry(LONG_TENS_HORIZON),
            "long_tens_tables": input_entry(LONG_TENS_TABLES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "paths": relpath(OUT_DIR / "paths.json"),
            "component_csv": relpath(OUT_DIR / "component.csv"),
            "fiber_csv": relpath(OUT_DIR / "fiber.csv"),
            "horizon_csv": relpath(OUT_DIR / "horizon.csv"),
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
                "all 288 current active-component sum fibers have exact compressed raw product-family counts",
                "the 208 gap fibers are included in the compressed path-family accounting",
                "the full 64,570,080 component-path family is accounted for by fiber and horizon",
                "active raw-support path counts and active raw-coefficient masses are reproducible by digits and modular witnesses",
            ],
            "does_not_certify_because_out_of_scope": [
                "materialized rows for every raw address path",
                "exact C985 source/target composability of all raw paths",
                "a probability measure on the full raw tensor support",
                "a genuine horizon-16 long_prof profunctor",
                "completion of the active theorem-discovery goal",
            ],
        },
        "next_highest_yield_item": (
            "Build long_measure: turn the compressed active raw product-family "
            "counts into a scoped probability law while keeping full raw-support "
            "measure claims separate."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")
    cert = {
        "schema": "long.paths.cert@1",
        "status": report["status"],
        "checks": checks,
        "witness": witness,
    }
    manifest = {
        "schema": "long.paths.manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")
    return {
        "paths": paths_payload,
        "component_csv": csv_text(COMPONENT_COLUMNS, rows["component_rows"]),
        "fiber_csv": csv_text(FIBER_COLUMNS, rows["fiber_rows"]),
        "horizon_csv": csv_text(HORIZON_COLUMNS, rows["horizon_rows"]),
        "obs_csv": csv_text(OBS_COLUMNS, rows["obs_rows"]),
        "component_table": rows["component_table"],
        "fiber_table": rows["fiber_table"],
        "horizon_table": rows["horizon_table"],
        "observable_table": rows["observable_table"],
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
    write_json(OUT_DIR / "paths.json", payloads["paths"])
    (OUT_DIR / "component.csv").write_text(payloads["component_csv"], encoding="utf-8")
    (OUT_DIR / "fiber.csv").write_text(payloads["fiber_csv"], encoding="utf-8")
    (OUT_DIR / "horizon.csv").write_text(payloads["horizon_csv"], encoding="utf-8")
    (OUT_DIR / "obs.csv").write_text(payloads["obs_csv"], encoding="utf-8")
    np.savez_compressed(
        OUT_DIR / "tables.npz",
        component_table=payloads["component_table"],
        fiber_table=payloads["fiber_table"],
        horizon_table=payloads["horizon_table"],
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
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
