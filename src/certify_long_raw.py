from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import (
        COMPONENT_COLUMNS,
        COMPONENT_TEXT_HASH,
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        FIBER_TEXT_HASH,
        HORIZON_COLUMNS,
        HORIZON_TEXT_HASH,
        INDEX_PATH,
        LONG_LAP_COMPONENT,
        LONG_LAP_NODE,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_LIFT_REPORT,
        LONG_LIFT_TABLES,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_REC_OWNER,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_HORIZON,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        OWNER_TEXT_HASH,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import (
        COMPONENT_COLUMNS,
        COMPONENT_TEXT_HASH,
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        FIBER_TEXT_HASH,
        HORIZON_COLUMNS,
        HORIZON_TEXT_HASH,
        INDEX_PATH,
        LONG_LAP_COMPONENT,
        LONG_LAP_NODE,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_LIFT_REPORT,
        LONG_LIFT_TABLES,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_REC_OWNER,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_HORIZON,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        OWNER_TEXT_HASH,
        RAW_TENSOR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )


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


def validate_long_raw() -> dict[str, Any]:
    expected = build_payloads()
    raw_payload = load_json(OUT_DIR / "raw.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if raw_payload != expected["raw"]:
        raise AssertionError("long_raw raw JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_raw cert mismatch")
    for filename, key in {
        "owner.csv": "owner_csv",
        "component.csv": "component_csv",
        "horizon.csv": "horizon_csv",
        "fiber.csv": "fiber_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_raw {filename} mismatch")

    for key, expected_array in {
        "owner_table": expected["owner_table"],
        "component_table": expected["component_table"],
        "horizon_table": expected["horizon_table"],
        "fiber_table": expected["fiber_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_raw table mismatch: {key}")

    if report.get("schema") != "long.raw.report@1":
        raise AssertionError("long_raw report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_raw report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_raw all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_raw checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_raw report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_raw report hash mismatch")

    csv_shapes = [
        ("owner.csv", OWNER_COLUMNS, 259),
        ("component.csv", COMPONENT_COLUMNS, 3),
        ("horizon.csv", HORIZON_COLUMNS, 16),
        ("fiber.csv", FIBER_COLUMNS, 288),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_raw {filename} shape mismatch")

    table_shapes = {
        "owner_table": (259, len(OWNER_COLUMNS)),
        "component_table": (3, len(COMPONENT_COLUMNS)),
        "horizon_table": (16, len(HORIZON_COLUMNS)),
        "fiber_table": (288, len(FIBER_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_raw {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "owner_row_count": 259,
        "component_row_count": 3,
        "horizon_row_count": 16,
        "fiber_row_count": 288,
        "raw_tensor_support_count": 1_414_965,
        "raw_tensor_coeff_sum": 2_537_360,
        "raw_owner_assignment_count": 1_414_965,
        "raw_owner_assignment_complete_flag": 1,
        "owner_raw_support_positive_count": 259,
        "owner_raw_source_cell_positive_count": 259,
        "raw_source_cell_count": 198_029,
        "owner_cell_total": 970_225,
        "active_owner_count": 51,
        "active_owner_cell_count": 749_239,
        "active_raw_source_cell_count": 136_589,
        "active_raw_support_count": 1_096_591,
        "active_raw_coeff_sum": 1_985_840,
        "inactive_raw_support_count": 318_374,
        "inactive_raw_coeff_sum": 551_520,
        "component_raw_source_cell_positive_count": 3,
        "component_raw_support_positive_count": 3,
        "component_raw_coeff_positive_count": 3,
        "target_ge_owner_target_count": 1_414_965,
        "target_eq_owner_target_count": 22_044,
        "target_diff_min": 0,
        "target_diff_max": 283,
        "raw_support_horizon_total_equal_count": 16,
        "raw_coeff_horizon_total_equal_count": 16,
        "raw_support_lift_positive_count": 288,
        "raw_coeff_lift_positive_count": 288,
        "gap_fiber_row_count": 208,
        "existing_fiber_row_count": 80,
        "compressed_raw_quotient_row_count": 208,
        "current_raw_owner_support_flag": 1,
        "current_compressed_raw_lift_flag": 1,
        "current_materialized_raw_path_flag": 0,
        "current_markov_only_quotient_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_raw observable {key} mismatch")

    if hashlib.sha256(
        digest_text(OWNER_COLUMNS, csv_rows["owner.csv"]).encode("ascii")
    ).hexdigest() != OWNER_TEXT_HASH:
        raise AssertionError("long_raw owner hash mismatch")
    if hashlib.sha256(
        digest_text(COMPONENT_COLUMNS, csv_rows["component.csv"]).encode("ascii")
    ).hexdigest() != COMPONENT_TEXT_HASH:
        raise AssertionError("long_raw component hash mismatch")
    if hashlib.sha256(
        digest_text(HORIZON_COLUMNS, csv_rows["horizon.csv"]).encode("ascii")
    ).hexdigest() != HORIZON_TEXT_HASH:
        raise AssertionError("long_raw horizon hash mismatch")
    if hashlib.sha256(
        digest_text(FIBER_COLUMNS, csv_rows["fiber.csv"]).encode("ascii")
    ).hexdigest() != FIBER_TEXT_HASH:
        raise AssertionError("long_raw fiber hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "raw_tensor": RAW_TENSOR,
        "long_lln_report": LONG_LLN_REPORT,
        "long_lln_tables": LONG_LLN_TABLES,
        "long_rec_report": LONG_REC_REPORT,
        "long_rec_owner": LONG_REC_OWNER,
        "long_rec_tables": LONG_REC_TABLES,
        "long_lap_report": LONG_LAP_REPORT,
        "long_lap_node": LONG_LAP_NODE,
        "long_lap_component": LONG_LAP_COMPONENT,
        "long_lap_tables": LONG_LAP_TABLES,
        "long_tens_report": LONG_TENS_REPORT,
        "long_tens_fiber": LONG_TENS_FIBER,
        "long_tens_horizon": LONG_TENS_HORIZON,
        "long_tens_tables": LONG_TENS_TABLES,
        "long_lift_report": LONG_LIFT_REPORT,
        "long_lift_tables": LONG_LIFT_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.raw.manifest@1":
        raise AssertionError("long_raw manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_raw manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_raw manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_raw missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_raw proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_raw proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.raw.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "raw_owner_assignment": witness.get("raw_owner_assignment"),
            "active_components": witness.get("active_components"),
            "horizons": witness.get("horizons"),
            "fibers": witness.get("fibers"),
            "current_representation": witness.get("current_representation"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_raw(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
