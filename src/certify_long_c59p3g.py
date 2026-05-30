from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3g import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        JOIN_SCHEMA_COLUMNS,
        LONG_C59P3M,
        LONG_C59P3M_JOIN,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SCHEMA_GAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SCHEMA_GAP_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_SCHEMA_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3g import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        JOIN_SCHEMA_COLUMNS,
        LONG_C59P3M,
        LONG_C59P3M_JOIN,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SCHEMA_GAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SCHEMA_GAP_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_SCHEMA_COLUMNS,
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


def validate_long_c59p3g() -> dict[str, Any]:
    expected = build_payloads()
    c59p3g = load_json(OUT_DIR / "c59p3g.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3g != expected["c59p3g"]:
        raise AssertionError("long_c59p3g JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3g cert mismatch")
    for filename, key in {
        "join_schema.csv": "join_schema_csv",
        "transition_schema.csv": "transition_schema_csv",
        "schema_gap.csv": "schema_gap_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3g {filename} mismatch")

    for key, expected_array in {
        "join_schema_table": expected["join_schema_table"],
        "transition_schema_table": expected["transition_schema_table"],
        "schema_gap_table": expected["schema_gap_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3g table mismatch: {key}")

    if report.get("schema") != "long.c59p3g.report@1":
        raise AssertionError("long_c59p3g report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3g report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3g all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3g checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3g report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3g report hash mismatch")

    csv_shapes = [
        ("join_schema.csv", JOIN_SCHEMA_COLUMNS, 229),
        ("transition_schema.csv", TRANSITION_SCHEMA_COLUMNS, 29),
        ("schema_gap.csv", SCHEMA_GAP_COLUMNS, 5),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3g {filename} shape mismatch")

    table_shapes = {
        "join_schema_table": (229, len(JOIN_SCHEMA_COLUMNS)),
        "transition_schema_table": (29, len(TRANSITION_SCHEMA_COLUMNS)),
        "schema_gap_table": (5, len(SCHEMA_GAP_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3g {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "join_row_count": 229,
        "active_relation_count": 49,
        "active_transition_count": 29,
        "contact_lift_join_count": 229,
        "endpoint_pair_raw_row_join_count": 229,
        "unit_time_join_count": 229,
        "operation_row_sentinel_join_count": 229,
        "operation_addr_sentinel_join_count": 229,
        "operation_coeff_zero_join_count": 229,
        "operation_time_component_zero_join_count": 229,
        "semantic_transition_zero_join_count": 229,
        "transition_ready_join_count": 229,
        "operation_backed_join_count": 0,
        "schema_gap_operation_rows_absent_flag": 1,
        "schema_gap_composition_law_absent_flag": 1,
        "operation_schema_gap_flag": 1,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": 5,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3g observable {key} mismatch")

    join_rows = rows_from_table(
        np.asarray(tables["join_schema_table"]), JOIN_SCHEMA_COLUMNS
    )
    if [row["join_id"] for row in join_rows] != list(range(229)):
        raise AssertionError("long_c59p3g join ids mismatch")
    if sum(row["transition_ready_flag"] for row in join_rows) != 229:
        raise AssertionError("long_c59p3g transition readiness mismatch")
    if sum(row["operation_sentinel_flag"] for row in join_rows) != 229:
        raise AssertionError("long_c59p3g operation sentinel mismatch")
    if sum(row["operation_backed_flag"] for row in join_rows) != 0:
        raise AssertionError("long_c59p3g operation-backed join mismatch")
    if {row["blocking_schema_gap_code"] for row in join_rows} != {3}:
        raise AssertionError("long_c59p3g blocking schema code mismatch")

    transition_rows = rows_from_table(
        np.asarray(tables["transition_schema_table"]), TRANSITION_SCHEMA_COLUMNS
    )
    if [row["active_transition_id"] for row in transition_rows] != list(range(29)):
        raise AssertionError("long_c59p3g active transition ids mismatch")
    if [row["transition_id"] for row in transition_rows] != [
        0,
        1,
        2,
        3,
        4,
        7,
        9,
        10,
        12,
        13,
        15,
        16,
        17,
        19,
        21,
        24,
        26,
        35,
        37,
        38,
        39,
        40,
        42,
        43,
        44,
        49,
        53,
        63,
        65,
    ]:
        raise AssertionError("long_c59p3g active transition list mismatch")
    if sum(row["operation_sentinel_flag"] for row in transition_rows) != 29:
        raise AssertionError("long_c59p3g active transition sentinel mismatch")
    if sum(row["operation_backed_flag"] for row in transition_rows) != 0:
        raise AssertionError("long_c59p3g active transition backing mismatch")

    schema_gap_rows = rows_from_table(
        np.asarray(tables["schema_gap_table"]), SCHEMA_GAP_COLUMNS
    )
    if [row["source_obstruction_flag"] for row in schema_gap_rows] != [0, 0, 0, 1, 1]:
        raise AssertionError("long_c59p3g source schema obstruction mismatch")
    if [row["blocks_operation_backing_flag"] for row in schema_gap_rows] != [
        0,
        0,
        0,
        1,
        1,
    ]:
        raise AssertionError("long_c59p3g schema block vector mismatch")
    if [row["active_join_impacted_count"] for row in schema_gap_rows] != [
        0,
        0,
        0,
        229,
        229,
    ]:
        raise AssertionError("long_c59p3g schema active join impact mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3g gap certified vector mismatch")
    if [row["obstruction_flag"] for row in gap_rows] != [0, 0, 1, 1, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3g gap obstruction vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3g gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3g manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3g manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3g manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3m": LONG_C59P3M,
        "long_c59p3m_join": LONG_C59P3M_JOIN,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_transition_schema_gap": LONG_TRANSITION_SCHEMA_GAP,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3g index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3g index report hash mismatch")

    return {
        "schema": "long.c59p3g.verification@1",
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
    print(json.dumps(validate_long_c59p3g(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
