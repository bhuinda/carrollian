from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_dlim import (
        CONE_COLUMNS,
        CONE_TEXT_HASH,
        DEFECT_COLUMNS,
        DEFECT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LEVEL_COLUMNS,
        LEVEL_TEXT_HASH,
        LONG_MART_LEVEL,
        LONG_MART_REPORT,
        LONG_MART_STATE,
        LONG_MART_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        LONG_STOP_REPORT,
        LONG_STOP_STOP,
        LONG_STOP_TABLES,
        LONG_STOP_TAIL,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATE_COLUMNS,
        STATE_TEXT_HASH,
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
    from derive_long_dlim import (
        CONE_COLUMNS,
        CONE_TEXT_HASH,
        DEFECT_COLUMNS,
        DEFECT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LEVEL_COLUMNS,
        LEVEL_TEXT_HASH,
        LONG_MART_LEVEL,
        LONG_MART_REPORT,
        LONG_MART_STATE,
        LONG_MART_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        LONG_STOP_REPORT,
        LONG_STOP_STOP,
        LONG_STOP_TABLES,
        LONG_STOP_TAIL,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATE_COLUMNS,
        STATE_TEXT_HASH,
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


def validate_long_dlim() -> dict[str, Any]:
    expected = build_payloads()
    dlim_payload = load_json(OUT_DIR / "dlim.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if dlim_payload != expected["dlim"]:
        raise AssertionError("long_dlim dlim JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_dlim cert mismatch")
    for filename, key in {
        "state.csv": "state_csv",
        "level.csv": "level_csv",
        "cone.csv": "cone_csv",
        "defect.csv": "defect_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_dlim {filename} mismatch")

    for key, expected_array in {
        "state_table": expected["state_table"],
        "level_table": expected["level_table"],
        "cone_table": expected["cone_table"],
        "defect_table": expected["defect_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_dlim table mismatch: {key}")

    if report.get("schema") != "long.dlim.report@1":
        raise AssertionError("long_dlim report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_dlim report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_dlim all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_dlim checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dlim report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_dlim report hash mismatch")

    csv_shapes = [
        ("state.csv", STATE_COLUMNS, 255),
        ("level.csv", LEVEL_COLUMNS, 15),
        ("cone.csv", CONE_COLUMNS, 2),
        ("defect.csv", DEFECT_COLUMNS, 1),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_dlim {filename} shape mismatch")

    table_shapes = {
        "state_table": (255, len(STATE_COLUMNS)),
        "level_table": (15, len(LEVEL_COLUMNS)),
        "cone_table": (2, len(CONE_COLUMNS)),
        "defect_table": (1, len(DEFECT_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_dlim {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "state_row_count": 255,
        "level_row_count": 15,
        "cone_row_count": 2,
        "defect_row_count": 1,
        "drift_positive_count": 240,
        "drift_negative_count": 1,
        "drift_zero_count": 14,
        "boundary_state_count": 3,
        "boundary_negative_count": 1,
        "eventual_level_count": 14,
        "eventual_state_count": 252,
        "eventual_negative_count": 0,
        "eventual_zero_count": 14,
        "variance_shrink_level_count": 15,
        "tail_gap_nonnegative_count": 48,
        "stopped_tail_gap_nonnegative_count": 48,
        "defect_sample_count": 1,
        "defect_sum_value": 2,
        "defect_drift_num_mod_1000000007": 1_000_000_004,
        "defect_drift_den_mod_1000000007": 214,
        "defect_source_probability_num": 8,
        "defect_source_probability_den": 13,
        "max_outgoing_edge_count": 3,
        "state_abs_drift_num_mod_sum_1000000007": 236_694_364,
        "level_mean_drift_num_mod_sum_1000000007": 94_532_799,
        "cone_negative_mass_num_mod_sum_1000000007": 8,
        "input_long_prob_certified": 1,
        "input_long_path_certified": 1,
        "input_long_mart_certified": 1,
        "input_long_stop_certified": 1,
        "current_single_boundary_defect_flag": 1,
        "current_eventual_cone_flag": 1,
        "current_stopped_tail_bridge_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_dlim observable {key} mismatch")

    if hashlib.sha256(
        digest_text(STATE_COLUMNS, csv_rows["state.csv"]).encode("ascii")
    ).hexdigest() != STATE_TEXT_HASH:
        raise AssertionError("long_dlim state hash mismatch")
    if hashlib.sha256(
        digest_text(LEVEL_COLUMNS, csv_rows["level.csv"]).encode("ascii")
    ).hexdigest() != LEVEL_TEXT_HASH:
        raise AssertionError("long_dlim level hash mismatch")
    if hashlib.sha256(
        digest_text(CONE_COLUMNS, csv_rows["cone.csv"]).encode("ascii")
    ).hexdigest() != CONE_TEXT_HASH:
        raise AssertionError("long_dlim cone hash mismatch")
    if hashlib.sha256(
        digest_text(DEFECT_COLUMNS, csv_rows["defect.csv"]).encode("ascii")
    ).hexdigest() != DEFECT_TEXT_HASH:
        raise AssertionError("long_dlim defect hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_prob_report": LONG_PROB_REPORT,
        "long_prob_tables": LONG_PROB_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_tables": LONG_PATH_TABLES,
        "long_mart_report": LONG_MART_REPORT,
        "long_mart_state": LONG_MART_STATE,
        "long_mart_level": LONG_MART_LEVEL,
        "long_mart_tables": LONG_MART_TABLES,
        "long_stop_report": LONG_STOP_REPORT,
        "long_stop_tail": LONG_STOP_TAIL,
        "long_stop_stop": LONG_STOP_STOP,
        "long_stop_tables": LONG_STOP_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.dlim.manifest@1":
        raise AssertionError("long_dlim manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dlim manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_dlim manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_dlim missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_dlim proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_dlim proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.dlim.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "drift_partition": witness.get("drift_partition"),
            "boundary_defect": witness.get("boundary_defect"),
            "eventual_cone": witness.get("eventual_cone"),
            "stopped_tail_bridge": witness.get("stopped_tail_bridge"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_dlim(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
