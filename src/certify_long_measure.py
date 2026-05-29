from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_measure import (
        DECOMP_COLUMNS,
        DERIVE_SCRIPT,
        DIST_COLUMNS,
        INDEX_PATH,
        LONG_PATHS_COMPONENT,
        LONG_PATHS_FIBER,
        LONG_PATHS_HORIZON,
        LONG_PATHS_REPORT,
        LONG_PATHS_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        LONG_RAW_REPORT,
        LONG_RAW_TABLES,
        MEASURE_COLUMNS,
        MOMENT_COLUMNS,
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
    from derive_long_measure import (
        DECOMP_COLUMNS,
        DERIVE_SCRIPT,
        DIST_COLUMNS,
        INDEX_PATH,
        LONG_PATHS_COMPONENT,
        LONG_PATHS_FIBER,
        LONG_PATHS_HORIZON,
        LONG_PATHS_REPORT,
        LONG_PATHS_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        LONG_RAW_REPORT,
        LONG_RAW_TABLES,
        MEASURE_COLUMNS,
        MOMENT_COLUMNS,
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


def validate_long_measure() -> dict[str, Any]:
    expected = build_payloads()
    measure_payload = load_json(OUT_DIR / "measure.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if measure_payload != expected["measure"]:
        raise AssertionError("long_measure measure JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_measure cert mismatch")
    for filename, key in {
        "measure.csv": "measure_csv",
        "dist.csv": "dist_csv",
        "moment.csv": "moment_csv",
        "decomp.csv": "decomp_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_measure {filename} mismatch")

    for key, expected_array in {
        "measure_table": expected["measure_table"],
        "dist_table": expected["dist_table"],
        "moment_table": expected["moment_table"],
        "decomp_table": expected["decomp_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_measure table mismatch: {key}")

    if report.get("schema") != "long.measure.report@1":
        raise AssertionError("long_measure report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_measure report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_measure all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_measure checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_measure report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_measure report hash mismatch")

    csv_shapes = [
        ("measure.csv", MEASURE_COLUMNS, 2),
        ("dist.csv", DIST_COLUMNS, 576),
        ("moment.csv", MOMENT_COLUMNS, 32),
        ("decomp.csv", DECOMP_COLUMNS, 2),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_measure {filename} shape mismatch")

    table_shapes = {
        "measure_table": (2, len(MEASURE_COLUMNS)),
        "dist_table": (576, len(DIST_COLUMNS)),
        "moment_table": (32, len(MOMENT_COLUMNS)),
        "decomp_table": (2, len(DECOMP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_measure {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "measure_row_count": 2,
        "distribution_row_count": 576,
        "moment_row_count": 32,
        "decomp_row_count": 2,
        "fiber_row_count": 288,
        "horizon_row_count": 16,
        "component_row_count": 3,
        "support_component_weight_sum": 1_096_591,
        "coeff_component_weight_sum": 1_985_840,
        "raw_tensor_support_count": 1_414_965,
        "raw_tensor_coeff_sum": 2_537_360,
        "inactive_raw_support_count": 318_374,
        "inactive_raw_coeff_sum": 551_520,
        "conditional_normalization_flag_count": 32,
        "variance_shrink_flag_count": 32,
        "variance_decomp_flag_count": 2,
        "scoped_probability_law_flag": 1,
        "full_raw_measure_certified_flag": 0,
        "full_raw_scope_gap_flag": 1,
        "materialized_raw_path_family_flag": 0,
        "exact_composable_raw_path_family_flag": 0,
        "next_target_code": 6,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_measure observable {key} mismatch")

    measure_rows = rows_from_table(np.asarray(tables["measure_table"]), MEASURE_COLUMNS)
    if sum(row["normalized_active_scope_flag"] for row in measure_rows) != 2:
        raise AssertionError("long_measure active normalization flag mismatch")
    if sum(row["full_raw_measure_certified_flag"] for row in measure_rows) != 0:
        raise AssertionError("long_measure full raw overclaim mismatch")
    if sum(row["full_raw_scope_gap_flag"] for row in measure_rows) != 2:
        raise AssertionError("long_measure full raw scope gap mismatch")
    moment_rows = rows_from_table(np.asarray(tables["moment_table"]), MOMENT_COLUMNS)
    if sum(row["conditional_normalization_flag"] for row in moment_rows) != 32:
        raise AssertionError("long_measure conditional normalization mismatch")
    if sum(row["variance_shrink_from_prev_flag"] for row in moment_rows) != 32:
        raise AssertionError("long_measure variance shrink mismatch")
    decomp_rows = rows_from_table(np.asarray(tables["decomp_table"]), DECOMP_COLUMNS)
    if sum(row["variance_decomp_flag"] for row in decomp_rows) != 2:
        raise AssertionError("long_measure variance decomposition mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_paths_report": LONG_PATHS_REPORT,
        "long_paths_component": LONG_PATHS_COMPONENT,
        "long_paths_fiber": LONG_PATHS_FIBER,
        "long_paths_horizon": LONG_PATHS_HORIZON,
        "long_paths_tables": LONG_PATHS_TABLES,
        "long_raw_report": LONG_RAW_REPORT,
        "long_raw_tables": LONG_RAW_TABLES,
        "long_prob_report": LONG_PROB_REPORT,
        "long_prob_tables": LONG_PROB_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.measure.manifest@1":
        raise AssertionError("long_measure manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_measure manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_measure manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_measure missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_measure proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_measure proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.measure.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "full_raw_gap": witness.get("full_raw_gap"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_measure(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
