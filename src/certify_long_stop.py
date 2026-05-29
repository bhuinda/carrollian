from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_stop import (
        COMPARE_COLUMNS,
        COMPARE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_CLS_REPORT,
        LONG_CLS_TABLES,
        LONG_CLS_TAIL,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_MART_EDGE,
        LONG_MART_LEVEL,
        LONG_MART_REPORT,
        LONG_MART_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        STOP_COLUMNS,
        STOP_TEXT_HASH,
        TAIL_COLUMNS,
        TAIL_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_stop import (
        COMPARE_COLUMNS,
        COMPARE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_CLS_REPORT,
        LONG_CLS_TABLES,
        LONG_CLS_TAIL,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_MART_EDGE,
        LONG_MART_LEVEL,
        LONG_MART_REPORT,
        LONG_MART_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        LONG_PROB_DIST,
        LONG_PROB_MOMENT,
        LONG_PROB_REPORT,
        LONG_PROB_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        STOP_COLUMNS,
        STOP_TEXT_HASH,
        TAIL_COLUMNS,
        TAIL_TEXT_HASH,
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


def validate_long_stop() -> dict[str, Any]:
    expected = build_payloads()
    stop_payload = load_json(OUT_DIR / "stop.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if stop_payload != expected["stop"]:
        raise AssertionError("long_stop stop JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_stop cert mismatch")
    for filename, key in {
        "tail.csv": "tail_csv",
        "stop.csv": "stop_csv",
        "compare.csv": "compare_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_stop {filename} mismatch")

    for key, expected_array in {
        "tail_table": expected["tail_table"],
        "stop_table": expected["stop_table"],
        "compare_table": expected["compare_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_stop table mismatch: {key}")

    if report.get("schema") != "long.stop.report@1":
        raise AssertionError("long_stop report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_stop report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_stop all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_stop checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stop report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_stop report hash mismatch")

    csv_shapes = [
        ("tail.csv", TAIL_COLUMNS, 48),
        ("stop.csv", STOP_COLUMNS, 48),
        ("compare.csv", COMPARE_COLUMNS, 1),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_stop {filename} shape mismatch")

    table_shapes = {
        "tail_table": (48, len(TAIL_COLUMNS)),
        "stop_table": (48, len(STOP_COLUMNS)),
        "compare_table": (1, len(COMPARE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_stop {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "horizon": 16,
        "epsilon_count": 3,
        "tail_row_count": 48,
        "tail_gap_nonnegative_count": 48,
        "stop_row_count": 48,
        "stop_gap_nonnegative_count": 48,
        "compare_row_count": 1,
        "long_cls_tail_gap_count": 48,
        "tail_prob_num_mod_sum_1000000007": 228_485_013,
        "tail_gap_num_mod_sum_1000000007": 455_837_620,
        "stopped_prob_num_mod_sum_1000000007": 16_587,
        "union_bound_num_mod_sum_1000000007": 93_091_961,
        "stop_gap_num_mod_sum_1000000007": 543_186_879,
        "max_tail_prob_num_digits": 13,
        "max_tail_prob_den_digits": 15,
        "max_stopped_prob_num_digits": 4,
        "max_stopped_prob_den_digits": 4,
        "grammar_match_flag": 1,
        "input_long_prob_certified": 1,
        "input_long_dual_certified": 1,
        "input_long_path_certified": 1,
        "input_long_mart_certified": 1,
        "input_long_cls_certified": 1,
        "current_dual_tail_flag": 1,
        "current_stopped_tail_flag": 1,
        "current_optional_union_bound_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_stop observable {key} mismatch")

    if hashlib.sha256(
        digest_text(TAIL_COLUMNS, csv_rows["tail.csv"]).encode("ascii")
    ).hexdigest() != TAIL_TEXT_HASH:
        raise AssertionError("long_stop tail hash mismatch")
    if hashlib.sha256(
        digest_text(STOP_COLUMNS, csv_rows["stop.csv"]).encode("ascii")
    ).hexdigest() != STOP_TEXT_HASH:
        raise AssertionError("long_stop stop hash mismatch")
    if hashlib.sha256(
        digest_text(COMPARE_COLUMNS, csv_rows["compare.csv"]).encode("ascii")
    ).hexdigest() != COMPARE_TEXT_HASH:
        raise AssertionError("long_stop compare hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_prob_report": LONG_PROB_REPORT,
        "long_prob_dist": LONG_PROB_DIST,
        "long_prob_moment": LONG_PROB_MOMENT,
        "long_prob_tables": LONG_PROB_TABLES,
        "long_dual_report": LONG_DUAL_REPORT,
        "long_dual_path": LONG_DUAL_PATH,
        "long_dual_tables": LONG_DUAL_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_tables": LONG_PATH_TABLES,
        "long_mart_report": LONG_MART_REPORT,
        "long_mart_edge": LONG_MART_EDGE,
        "long_mart_level": LONG_MART_LEVEL,
        "long_mart_tables": LONG_MART_TABLES,
        "long_cls_report": LONG_CLS_REPORT,
        "long_cls_tail": LONG_CLS_TAIL,
        "long_cls_tables": LONG_CLS_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.stop.manifest@1":
        raise AssertionError("long_stop manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stop manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_stop manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_stop missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stop proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_stop proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.stop.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "tail": witness.get("tail"),
            "stopped_tail": witness.get("stopped_tail"),
            "comparison": witness.get("comparison"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_stop(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
