from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3i import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3R,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_RSEM_TICK,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RELATION_STRESS_COLUMNS,
        STATUS,
        THEOREM_ID,
        TICK_STRESS_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3i import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3R,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_RSEM_TICK,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RELATION_STRESS_COLUMNS,
        STATUS,
        THEOREM_ID,
        TICK_STRESS_COLUMNS,
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


def validate_long_c59p3i() -> dict[str, Any]:
    expected = build_payloads()
    c59p3i = load_json(OUT_DIR / "c59p3i.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3i != expected["c59p3i"]:
        raise AssertionError("long_c59p3i JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3i cert mismatch")
    for filename, key in {
        "tick_stress.csv": "tick_stress_csv",
        "relation_stress.csv": "relation_stress_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3i {filename} mismatch")

    for key, expected_array in {
        "tick_stress_table": expected["tick_stress_table"],
        "relation_stress_table": expected["relation_stress_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3i table mismatch: {key}")

    if report.get("schema") != "long.c59p3i.report@1":
        raise AssertionError("long_c59p3i report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3i report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3i all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3i checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3i report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3i report hash mismatch")

    csv_shapes = [
        ("tick_stress.csv", TICK_STRESS_COLUMNS, 20),
        ("relation_stress.csv", RELATION_STRESS_COLUMNS, 59),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3i {filename} shape mismatch")

    table_shapes = {
        "tick_stress_table": (20, len(TICK_STRESS_COLUMNS)),
        "relation_stress_table": (59, len(RELATION_STRESS_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3i {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "tick_row_count": 20,
        "relation_row_count": 59,
        "stress_edge_row_count": 100,
        "direct_tick_stress_count": 3,
        "reverse_tick_stress_count": 5,
        "undirected_tick_stress_count": 6,
        "missing_tick_stress_count": 14,
        "direct_relation_stress_count": 8,
        "undirected_relation_stress_count": 15,
        "missing_relation_stress_count": 44,
        "total_visible_tick_stress_map_flag": 0,
        "total_relation_stress_incidence_flag": 0,
        "relation_stress_extension_flag": 0,
        "operation_row_match_count": 0,
        "semantic_transition_match_count": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 5,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3i observable {key} mismatch")

    tick_rows = rows_from_table(
        np.asarray(tables["tick_stress_table"]), TICK_STRESS_COLUMNS
    )
    if [row["visible_index"] for row in tick_rows] != list(range(20)):
        raise AssertionError("long_c59p3i tick order mismatch")
    if sum(row["direct_stress_flag"] for row in tick_rows) != 3:
        raise AssertionError("long_c59p3i direct tick count mismatch")
    if sum(row["reverse_stress_flag"] for row in tick_rows) != 5:
        raise AssertionError("long_c59p3i reverse tick count mismatch")
    if sum(row["undirected_stress_flag"] for row in tick_rows) != 6:
        raise AssertionError("long_c59p3i undirected tick count mismatch")
    if sum(row["missing_stress_flag"] for row in tick_rows) != 14:
        raise AssertionError("long_c59p3i missing tick count mismatch")

    relation_rows = rows_from_table(
        np.asarray(tables["relation_stress_table"]), RELATION_STRESS_COLUMNS
    )
    if [row["relation_id"] for row in relation_rows] != list(range(59)):
        raise AssertionError("long_c59p3i relation ids mismatch")
    if sum(row["direct_stress_flag"] for row in relation_rows) != 8:
        raise AssertionError("long_c59p3i direct relation count mismatch")
    if sum(row["undirected_stress_flag"] for row in relation_rows) != 15:
        raise AssertionError("long_c59p3i undirected relation count mismatch")
    if sum(row["stress_incidence_flag"] for row in relation_rows) != 15:
        raise AssertionError("long_c59p3i stress incidence count mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3i gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 0, 1, 0]:
        raise AssertionError("long_c59p3i gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3i manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3i manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3i manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
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
        raise AssertionError("long_c59p3i index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3i index report hash mismatch")

    return {
        "schema": "long.c59p3i.verification@1",
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
    print(json.dumps(validate_long_c59p3i(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
