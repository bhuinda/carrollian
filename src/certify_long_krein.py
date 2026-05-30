from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_krein import (
        CHAR_REPORT,
        CHAR_TABLE,
        CLEARANCE_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        HANDOFF,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SOURCE_COLUMNS,
        STATUS,
        TARGET_COLUMNS,
        THEOREM_ID,
        TRACE_SUMMARY,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_krein import (
        CHAR_REPORT,
        CHAR_TABLE,
        CLEARANCE_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        HANDOFF,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SOURCE_COLUMNS,
        STATUS,
        TARGET_COLUMNS,
        THEOREM_ID,
        TRACE_SUMMARY,
        build_payloads,
        self_hash,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_long_krein() -> dict[str, Any]:
    expected = build_payloads()
    krein = load_json(OUT_DIR / "krein.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if krein != expected["krein"]:
        raise AssertionError("long_krein JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_krein cert mismatch")
    for filename, key in {
        "source.csv": "source_csv",
        "target.csv": "target_csv",
        "clearance.csv": "clearance_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
        "krein_denominator_obstruction_report.md": "markdown_report",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_krein {filename} mismatch")

    for key, expected_array in {
        "source_table": expected["source_table"],
        "target_table": expected["target_table"],
        "clearance_table": expected["clearance_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_krein table mismatch: {key}")

    if report.get("schema") != "long.krein.report@1":
        raise AssertionError("long_krein report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_krein report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_krein all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_krein checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_krein report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_krein report hash mismatch")

    csv_shapes = [
        ("source.csv", SOURCE_COLUMNS, 4),
        ("target.csv", TARGET_COLUMNS, 4),
        ("clearance.csv", CLEARANCE_COLUMNS, 5),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_krein {filename} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "source_row_count": 4,
        "present_source_count": 2,
        "certified_source_count": 1,
        "required_source_count": 4,
        "blocking_source_count": 2,
        "character_sector_count": 39,
        "character_relation_count": 985,
        "character_table_row_count": 38_415,
        "target_exception_row_count": 4,
        "computed_exception_row_count": 0,
        "verified_exception_row_count": 0,
        "half_integral_exception_row_count": 4,
        "clearance_candidate_count": 5,
        "clearance_tested_count": 0,
        "provisional_flag": 1,
        "next_gap_code": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_krein observable {key} mismatch")

    source_rows = rows_from_table(np.asarray(tables["source_table"]), SOURCE_COLUMNS)
    if [row["present_flag"] for row in source_rows] != [1, 1, 0, 0]:
        raise AssertionError("long_krein source present vector mismatch")
    if [row["blocks_full_krein_flag"] for row in source_rows] != [0, 0, 1, 1]:
        raise AssertionError("long_krein source block vector mismatch")

    target_rows = rows_from_table(np.asarray(tables["target_table"]), TARGET_COLUMNS)
    expected_targets = [(5, 5, 2), (5, 6, 2), (6, 5, 2), (6, 6, 2)]
    if [(row["i"], row["j"], row["k"]) for row in target_rows] != expected_targets:
        raise AssertionError("long_krein target triples mismatch")
    if [row["expected_numerator"] for row in target_rows] != [135, 135, 135, 135]:
        raise AssertionError("long_krein target numerator mismatch")
    if [row["expected_denominator"] for row in target_rows] != [2, 2, 2, 2]:
        raise AssertionError("long_krein target denominator mismatch")
    if sum(row["verified_flag"] for row in target_rows) != 0:
        raise AssertionError("long_krein target verification mismatch")

    clearance_rows = rows_from_table(
        np.asarray(tables["clearance_table"]), CLEARANCE_COLUMNS
    )
    if sum(row["tested_flag"] for row in clearance_rows) != 0:
        raise AssertionError("long_krein clearance tested count mismatch")
    if sum(row["open_flag"] for row in clearance_rows) != 5:
        raise AssertionError("long_krein clearance open count mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0]:
        raise AssertionError("long_krein gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0]:
        raise AssertionError("long_krein gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_krein manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_krein manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_krein manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "handoff": HANDOFF,
        "character_report": CHAR_REPORT,
        "character_table": CHAR_TABLE,
        "trace_summary": TRACE_SUMMARY,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_krein index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_krein index report hash mismatch")

    return {
        "schema": "long.krein.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_krein(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
