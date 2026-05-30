from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3c import (
        COUNTERTERM_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3W,
        LONG_C59P3W_BALANCE,
        LONG_C59P3W_EDGE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3c import (
        COUNTERTERM_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3W,
        LONG_C59P3W_BALANCE,
        LONG_C59P3W_EDGE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
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


def validate_long_c59p3c() -> dict[str, Any]:
    expected = build_payloads()
    c59p3c = load_json(OUT_DIR / "c59p3c.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3c != expected["c59p3c"]:
        raise AssertionError("long_c59p3c JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3c cert mismatch")
    for filename, key in {
        "counterterm.csv": "counterterm_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3c {filename} mismatch")

    for key, expected_array in {
        "counterterm_table": expected["counterterm_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3c table mismatch: {key}")

    if report.get("schema") != "long.c59p3c.report@1":
        raise AssertionError("long_c59p3c report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3c report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3c all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3c checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3c report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3c report hash mismatch")

    csv_shapes = [
        ("counterterm.csv", COUNTERTERM_COLUMNS, 20),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3c {filename} shape mismatch")

    table_shapes = {
        "counterterm_table": (20, len(COUNTERTERM_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3c {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 1,
        "input_certified_count": 1,
        "atom_count": 20,
        "edge_row_count": 14,
        "pre_unbalanced_atom_count": 17,
        "counterterm_support_count": 17,
        "counterterm_sum_scaled": 0,
        "counterterm_abs_total_scaled": 657962662788,
        "counterterm_max_abs_scaled": 180000000000,
        "post_unbalanced_atom_count": 0,
        "post_global_divergence_sum_scaled": 0,
        "minimal_support_flag": 1,
        "formal_counterterm_flag": 1,
        "operation_backed_counterterm_flag": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 3,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3c observable {key} mismatch")

    counterterm_rows = rows_from_table(
        np.asarray(tables["counterterm_table"]), COUNTERTERM_COLUMNS
    )
    if [row["atom_id"] for row in counterterm_rows] != list(range(20)):
        raise AssertionError("long_c59p3c atom ids mismatch")
    if sum(row["counterterm_support_flag"] for row in counterterm_rows) != 17:
        raise AssertionError("long_c59p3c support count mismatch")
    if sum(row["counterterm_scaled"] for row in counterterm_rows) != 0:
        raise AssertionError("long_c59p3c counterterm sum mismatch")
    if sum(abs(row["counterterm_scaled"]) for row in counterterm_rows) != 657962662788:
        raise AssertionError("long_c59p3c counterterm abs total mismatch")
    if any(row["post_net_divergence_scaled"] != 0 for row in counterterm_rows):
        raise AssertionError("long_c59p3c corrected divergence mismatch")
    if any(row["post_local_balance_flag"] != 1 for row in counterterm_rows):
        raise AssertionError("long_c59p3c corrected local balance mismatch")
    zero_support_atoms = [
        row["atom_id"]
        for row in counterterm_rows
        if row["counterterm_support_flag"] == 0
    ]
    if zero_support_atoms != [2, 4, 15]:
        raise AssertionError("long_c59p3c zero-support atoms mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3c gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3c gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3c manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3c manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3c manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3w": LONG_C59P3W,
        "long_c59p3w_balance": LONG_C59P3W_BALANCE,
        "long_c59p3w_edge": LONG_C59P3W_EDGE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3c index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3c index report hash mismatch")

    return {
        "schema": "long.c59p3c.verification@1",
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
    print(json.dumps(validate_long_c59p3c(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
