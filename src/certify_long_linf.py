from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_linf import (
        CONE_COLUMNS,
        CONE_TEXT_HASH,
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        FIBER_TEXT_HASH,
        INDEX_PATH,
        LEVEL_COLUMNS,
        LEVEL_TEXT_HASH,
        LONG_DLIM_DEFECT,
        LONG_DLIM_REPORT,
        LONG_DLIM_TABLES,
        LONG_DUAL_COMPONENT,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
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
    from derive_long_linf import (
        CONE_COLUMNS,
        CONE_TEXT_HASH,
        DERIVE_SCRIPT,
        FIBER_COLUMNS,
        FIBER_TEXT_HASH,
        INDEX_PATH,
        LEVEL_COLUMNS,
        LEVEL_TEXT_HASH,
        LONG_DLIM_DEFECT,
        LONG_DLIM_REPORT,
        LONG_DLIM_TABLES,
        LONG_DUAL_COMPONENT,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
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


def validate_long_linf() -> dict[str, Any]:
    expected = build_payloads()
    linf_payload = load_json(OUT_DIR / "linf.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if linf_payload != expected["linf"]:
        raise AssertionError("long_linf linf JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_linf cert mismatch")
    for filename, key in {
        "fiber.csv": "fiber_csv",
        "state.csv": "state_csv",
        "level.csv": "level_csv",
        "cone.csv": "cone_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_linf {filename} mismatch")

    for key, expected_array in {
        "fiber_table": expected["fiber_table"],
        "state_table": expected["state_table"],
        "level_table": expected["level_table"],
        "cone_table": expected["cone_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_linf table mismatch: {key}")

    if report.get("schema") != "long.linf.report@1":
        raise AssertionError("long_linf report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_linf report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_linf all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_linf checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_linf report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_linf report hash mismatch")

    csv_shapes = [
        ("fiber.csv", FIBER_COLUMNS, 16_640),
        ("state.csv", STATE_COLUMNS, 16_383),
        ("level.csv", LEVEL_COLUMNS, 127),
        ("cone.csv", CONE_COLUMNS, 4),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_linf {filename} shape mismatch")

    table_shapes = {
        "fiber_table": (16_640, len(FIBER_COLUMNS)),
        "state_table": (16_383, len(STATE_COLUMNS)),
        "level_table": (127, len(LEVEL_COLUMNS)),
        "cone_table": (4, len(CONE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_linf {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "base_horizon": 16,
        "lift_horizon": 128,
        "fiber_row_count": 16_640,
        "state_row_count": 16_383,
        "level_row_count": 127,
        "cone_row_count": 4,
        "base_fiber_match_count": 288,
        "base_fiber_count": 288,
        "lift_extension_fiber_count": 16_352,
        "drift_positive_count": 16_256,
        "drift_negative_count": 1,
        "drift_zero_count": 126,
        "boundary_negative_count": 1,
        "extension_level_count": 112,
        "extension_state_count": 16_128,
        "extension_negative_count": 0,
        "extension_zero_count": 112,
        "eventual_level_count": 126,
        "eventual_negative_count": 0,
        "eventual_zero_count": 126,
        "variance_shrink_level_count": 127,
        "max_outgoing_edge_count": 3,
        "state_abs_drift_num_mod_sum_1000000007": 811_687_137,
        "level_mean_drift_num_mod_sum_1000000007": 757_022_242,
        "last_variance_num_mod_1000000007": 40_610_332,
        "last_variance_den_mod_1000000007": 984_634_787,
        "input_long_dual_certified": 1,
        "input_long_path_certified": 1,
        "input_long_prob_certified": 1,
        "input_long_dlim_certified": 1,
        "current_measure_match_flag": 1,
        "current_no_second_defect_flag": 1,
        "current_lift_cone_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_linf observable {key} mismatch")

    if hashlib.sha256(
        digest_text(FIBER_COLUMNS, csv_rows["fiber.csv"]).encode("ascii")
    ).hexdigest() != FIBER_TEXT_HASH:
        raise AssertionError("long_linf fiber hash mismatch")
    if hashlib.sha256(
        digest_text(STATE_COLUMNS, csv_rows["state.csv"]).encode("ascii")
    ).hexdigest() != STATE_TEXT_HASH:
        raise AssertionError("long_linf state hash mismatch")
    if hashlib.sha256(
        digest_text(LEVEL_COLUMNS, csv_rows["level.csv"]).encode("ascii")
    ).hexdigest() != LEVEL_TEXT_HASH:
        raise AssertionError("long_linf level hash mismatch")
    if hashlib.sha256(
        digest_text(CONE_COLUMNS, csv_rows["cone.csv"]).encode("ascii")
    ).hexdigest() != CONE_TEXT_HASH:
        raise AssertionError("long_linf cone hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_dual_report": LONG_DUAL_REPORT,
        "long_dual_component": LONG_DUAL_COMPONENT,
        "long_dual_path": LONG_DUAL_PATH,
        "long_dual_tables": LONG_DUAL_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_tables": LONG_PATH_TABLES,
        "long_prob_report": LONG_PROB_REPORT,
        "long_prob_tables": LONG_PROB_TABLES,
        "long_dlim_report": LONG_DLIM_REPORT,
        "long_dlim_defect": LONG_DLIM_DEFECT,
        "long_dlim_tables": LONG_DLIM_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.linf.manifest@1":
        raise AssertionError("long_linf manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_linf manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_linf manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_linf missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_linf proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_linf proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.linf.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "lift": witness.get("lift"),
            "transport": witness.get("transport"),
            "extension_cone": witness.get("extension_cone"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_linf(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
