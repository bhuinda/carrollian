from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_paths import (
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        HORIZON_COLUMNS,
        INDEX_PATH,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_POBJ_REPORT,
        LONG_POBJ_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_HORIZON,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_paths import (
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        HORIZON_COLUMNS,
        INDEX_PATH,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_POBJ_REPORT,
        LONG_POBJ_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_HORIZON,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_paths() -> dict[str, Any]:
    expected = build_payloads()
    paths_payload = load_json(OUT_DIR / "paths.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if paths_payload != expected["paths"]:
        raise AssertionError("long_paths paths JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_paths cert mismatch")
    for filename, key in {
        "component.csv": "component_csv",
        "fiber.csv": "fiber_csv",
        "horizon.csv": "horizon_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_paths {filename} mismatch")

    for key, expected_array in {
        "component_table": expected["component_table"],
        "fiber_table": expected["fiber_table"],
        "horizon_table": expected["horizon_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_paths table mismatch: {key}")

    if report.get("schema") != "long.paths.report@1":
        raise AssertionError("long_paths report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_paths report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_paths all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_paths checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_paths report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_paths report hash mismatch")

    csv_shapes = [
        ("component.csv", COMPONENT_COLUMNS, 3),
        ("fiber.csv", FIBER_COLUMNS, 288),
        ("horizon.csv", HORIZON_COLUMNS, 16),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_paths {filename} shape mismatch")

    table_shapes = {
        "component_table": (3, len(COMPONENT_COLUMNS)),
        "fiber_table": (288, len(FIBER_COLUMNS)),
        "horizon_table": (16, len(HORIZON_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_paths {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "component_row_count": 3,
        "fiber_row_count": 288,
        "horizon_row_count": 16,
        "existing_fiber_count": 80,
        "gap_fiber_count": 208,
        "component_path_total": 64_570_080,
        "component_path_gap_total": 64_560_240,
        "selected_witness_count": 288,
        "missing_component_path_count": 64_569_792,
        "active_raw_support_count": 1_096_591,
        "active_raw_coeff_sum": 1_985_840,
        "raw_support_positive_fiber_count": 288,
        "raw_coeff_positive_fiber_count": 288,
        "max_sample_count": 16,
        "max_raw_support_fiber_digits": 96,
        "max_raw_coeff_fiber_digits": 101,
        "horizon16_raw_support_total_digits": 97,
        "horizon16_raw_coeff_total_digits": 101,
        "compressed_raw_product_family_flag": 1,
        "materialized_raw_path_family_flag": 0,
        "exact_composable_raw_path_family_flag": 0,
        "next_target_code": 5,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_paths observable {key} mismatch")

    fiber_rows = rows_from_table(np.asarray(tables["fiber_table"]), FIBER_COLUMNS)
    if sum(row["compressed_raw_product_family_flag"] for row in fiber_rows) != 288:
        raise AssertionError("long_paths compressed fiber count mismatch")
    if sum(row["materialized_raw_path_family_flag"] for row in fiber_rows) != 0:
        raise AssertionError("long_paths materialized flag mismatch")
    horizon_rows = rows_from_table(
        np.asarray(tables["horizon_table"]), HORIZON_COLUMNS
    )
    if sum(row["component_path_count"] for row in horizon_rows) != 64_570_080:
        raise AssertionError("long_paths horizon component total mismatch")
    if sum(row["gap_component_path_count"] for row in horizon_rows) != 64_560_240:
        raise AssertionError("long_paths horizon gap total mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_path_report": LONG_PATH_REPORT,
        "long_path_component": LONG_PATH_COMPONENT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_tables": LONG_PATH_TABLES,
        "long_pobj_report": LONG_POBJ_REPORT,
        "long_pobj_tables": LONG_POBJ_TABLES,
        "long_tens_report": LONG_TENS_REPORT,
        "long_tens_fiber": LONG_TENS_FIBER,
        "long_tens_horizon": LONG_TENS_HORIZON,
        "long_tens_tables": LONG_TENS_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.paths.manifest@1":
        raise AssertionError("long_paths manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_paths manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_paths manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_paths missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_paths proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_paths proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.paths.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_paths(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
