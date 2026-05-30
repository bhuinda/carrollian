from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3f import (
        ASSIGNMENT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3I,
        LONG_C59P3R,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_RSEM_TICK,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RULE_CODES,
        RULE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3f import (
        ASSIGNMENT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3I,
        LONG_C59P3R,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_RSEM_TICK,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RULE_CODES,
        RULE_COLUMNS,
        STATUS,
        THEOREM_ID,
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


def validate_long_c59p3f() -> dict[str, Any]:
    expected = build_payloads()
    c59p3f = load_json(OUT_DIR / "c59p3f.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3f != expected["c59p3f"]:
        raise AssertionError("long_c59p3f JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3f cert mismatch")
    for filename, key in {
        "assignment.csv": "assignment_csv",
        "rule.csv": "rule_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3f {filename} mismatch")

    for key, expected_array in {
        "assignment_table": expected["assignment_table"],
        "rule_table": expected["rule_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3f table mismatch: {key}")

    if report.get("schema") != "long.c59p3f.report@1":
        raise AssertionError("long_c59p3f report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3f report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3f all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3f checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3f report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3f report hash mismatch")

    csv_shapes = [
        ("assignment.csv", ASSIGNMENT_COLUMNS, 59),
        ("rule.csv", RULE_COLUMNS, len(RULE_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3f {filename} shape mismatch")

    table_shapes = {
        "assignment_table": (59, len(ASSIGNMENT_COLUMNS)),
        "rule_table": (len(RULE_CODES), len(RULE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3f {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 4,
        "input_certified_count": 4,
        "relation_row_count": 59,
        "stress_edge_row_count": 100,
        "assigned_relation_count": 59,
        "direct_assignment_count": 8,
        "reverse_assignment_count": 7,
        "fallback_assignment_count": 44,
        "unique_stress_edge_count": 14,
        "max_assignment_multiplicity": 10,
        "formal_pushforward_flag": 1,
        "operation_row_match_count": 0,
        "semantic_transition_match_count": 0,
        "physical_selector_axiom_flag": 0,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3f observable {key} mismatch")

    assignment_rows = rows_from_table(
        np.asarray(tables["assignment_table"]), ASSIGNMENT_COLUMNS
    )
    if [row["relation_id"] for row in assignment_rows] != list(range(59)):
        raise AssertionError("long_c59p3f assignment ids mismatch")
    if sum(row["formal_pushforward_flag"] for row in assignment_rows) != 59:
        raise AssertionError("long_c59p3f formal assignment count mismatch")
    if sum(int(row["rule_code"] == 0) for row in assignment_rows) != 8:
        raise AssertionError("long_c59p3f direct assignment count mismatch")
    if sum(int(row["rule_code"] == 1) for row in assignment_rows) != 7:
        raise AssertionError("long_c59p3f reverse assignment count mismatch")
    if sum(int(row["rule_code"] == 2) for row in assignment_rows) != 44:
        raise AssertionError("long_c59p3f fallback assignment count mismatch")
    if any(row["operation_row_present_flag"] != 0 for row in assignment_rows):
        raise AssertionError("long_c59p3f operation row flag mismatch")
    if any(row["physical_selector_axiom_flag"] != 0 for row in assignment_rows):
        raise AssertionError("long_c59p3f physical selector flag mismatch")

    rule_rows = rows_from_table(np.asarray(tables["rule_table"]), RULE_COLUMNS)
    if [row["rule_code"] for row in rule_rows] != [0, 1, 2]:
        raise AssertionError("long_c59p3f rule order mismatch")
    if [row["assignment_count"] for row in rule_rows] != [8, 7, 44]:
        raise AssertionError("long_c59p3f rule assignment vector mismatch")
    if [row["formal_rule_flag"] for row in rule_rows] != [1, 1, 1]:
        raise AssertionError("long_c59p3f formal rule vector mismatch")
    if [row["physical_selector_axiom_flag"] for row in rule_rows] != [0, 0, 0]:
        raise AssertionError("long_c59p3f physical rule vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3f gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3f gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3f manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3f manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3f manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3i": LONG_C59P3I,
        "long_c59p3r": LONG_C59P3R,
        "long_rsem": LONG_RSEM,
        "long_rsem_tick": LONG_RSEM_TICK,
        "long_rsem_relation": LONG_RSEM_RELATION,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3f index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3f index report hash mismatch")

    return {
        "schema": "long.c59p3f.verification@1",
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
    print(json.dumps(validate_long_c59p3f(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
