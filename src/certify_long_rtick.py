from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_rtick import (
        INDEX_PATH,
        LONG_ABMAP,
        LONG_ABMAP_EDGE,
        LONG_ABMAP_MATCH,
        LONG_GCLK,
        LONG_GCLK_CLOCK,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POLICY_CODES,
        POLICY_COLUMNS,
        RELATION_COLUMNS,
        STATUS,
        THEOREM_ID,
        TICK_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_rtick import (
        INDEX_PATH,
        LONG_ABMAP,
        LONG_ABMAP_EDGE,
        LONG_ABMAP_MATCH,
        LONG_GCLK,
        LONG_GCLK_CLOCK,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POLICY_CODES,
        POLICY_COLUMNS,
        RELATION_COLUMNS,
        STATUS,
        THEOREM_ID,
        TICK_COLUMNS,
        build_payloads,
        self_hash,
    )


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


def validate_long_rtick() -> dict[str, Any]:
    expected = build_payloads()
    rtick = load_json(OUT_DIR / "rtick.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if rtick != expected["rtick"]:
        raise AssertionError("long_rtick JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rtick cert mismatch")
    for filename, key in {
        "tick.csv": "tick_csv",
        "relation.csv": "relation_csv",
        "policy.csv": "policy_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rtick {filename} mismatch")

    for key, expected_array in {
        "tick_table": expected["tick_table"],
        "relation_table": expected["relation_table"],
        "policy_table": expected["policy_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rtick table mismatch: {key}")

    if report.get("schema") != "long.rtick.report@1":
        raise AssertionError("long_rtick report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rtick report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rtick all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rtick checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rtick report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rtick report hash mismatch")

    csv_shapes = [
        ("tick.csv", TICK_COLUMNS, 20),
        ("relation.csv", RELATION_COLUMNS, 59),
        ("policy.csv", POLICY_COLUMNS, len(POLICY_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_rtick {filename} shape mismatch")

    table_shapes = {
        "tick_table": (20, len(TICK_COLUMNS)),
        "relation_table": (59, len(RELATION_COLUMNS)),
        "policy_table": (len(POLICY_CODES), len(POLICY_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_rtick {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "affine_tick_count": 20,
        "relation_row_count": 59,
        "covered_tick_count": 20,
        "singleton_tick_count": 7,
        "multivalued_tick_count": 13,
        "max_relation_multiplicity": 6,
        "raw_backed_relation_count": 59,
        "unit_time_relation_count": 59,
        "contact_lift_relation_count": 59,
        "semantic_relation_count": 0,
        "operation_row_materialized_count": 0,
        "relation_cover_certified_flag": 1,
        "single_valued_functor_flag": 0,
        "relation_valued_semantic_law_flag": 0,
        "semantic_transition_operation_flag": 0,
        "physical_selector_axiom_flag": 0,
        "gr_source_ready_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_rtick observable {key} mismatch")

    tick_rows = rows_from_table(np.asarray(tables["tick_table"]), TICK_COLUMNS)
    if [row["visible_index"] for row in tick_rows] != list(range(20)):
        raise AssertionError("long_rtick tick order mismatch")
    if any(row["covered_flag"] != 1 for row in tick_rows):
        raise AssertionError("long_rtick uncovered tick")
    if sum(row["relation_match_count"] for row in tick_rows) != 59:
        raise AssertionError("long_rtick tick relation sum mismatch")
    if any(
        row["semantic_match_count"] != 0 or row["operation_row_match_count"] != 0
        for row in tick_rows
    ):
        raise AssertionError("long_rtick semantic tick mismatch")

    relation_rows = rows_from_table(
        np.asarray(tables["relation_table"]), RELATION_COLUMNS
    )
    if [row["relation_id"] for row in relation_rows] != list(range(59)):
        raise AssertionError("long_rtick relation ids mismatch")
    if any(row["left_raw_row_id"] < 0 or row["right_raw_row_id"] < 0 for row in relation_rows):
        raise AssertionError("long_rtick raw row id mismatch")
    if any(row["normal_form_delta_t"] != 1 for row in relation_rows):
        raise AssertionError("long_rtick delta_t mismatch")
    if any(row["contact_lift_flag"] != 1 for row in relation_rows):
        raise AssertionError("long_rtick contact lift mismatch")
    if any(row["endpoint_pair_raw_row_flag"] != 1 for row in relation_rows):
        raise AssertionError("long_rtick endpoint raw flag mismatch")
    if any(row["operation_row_id"] != -1 or row["semantic_transition_flag"] != 0 for row in relation_rows):
        raise AssertionError("long_rtick semantic relation mismatch")

    policy_rows = rows_from_table(np.asarray(tables["policy_table"]), POLICY_COLUMNS)
    if [row["policy_code"] for row in policy_rows] != list(range(len(POLICY_CODES))):
        raise AssertionError("long_rtick policy code order mismatch")
    if [row["certified_flag"] for row in policy_rows] != [1, 0, 0, 0, 0]:
        raise AssertionError("long_rtick policy certification mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_rtick manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_rtick manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rtick manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_gclk": LONG_GCLK,
        "long_gclk_clock": LONG_GCLK_CLOCK,
        "long_abmap": LONG_ABMAP,
        "long_abmap_edge": LONG_ABMAP_EDGE,
        "long_abmap_match": LONG_ABMAP_MATCH,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_rtick index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rtick index report hash mismatch")

    return {
        "schema": "long.rtick.verification@1",
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
    print(json.dumps(validate_long_rtick(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
