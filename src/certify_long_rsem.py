from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_rsem import (
        INDEX_PATH,
        LAW_CODES,
        LAW_COLUMNS,
        LONG_RTICK,
        LONG_RTICK_RELATION,
        LONG_RTICK_TICK,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
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
    from derive_long_rsem import (
        INDEX_PATH,
        LAW_CODES,
        LAW_COLUMNS,
        LONG_RTICK,
        LONG_RTICK_RELATION,
        LONG_RTICK_TICK,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
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


def validate_long_rsem() -> dict[str, Any]:
    expected = build_payloads()
    rsem = load_json(OUT_DIR / "rsem.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if rsem != expected["rsem"]:
        raise AssertionError("long_rsem JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rsem cert mismatch")
    for filename, key in {
        "law.csv": "law_csv",
        "tick.csv": "tick_csv",
        "relation.csv": "relation_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rsem {filename} mismatch")

    for key, expected_array in {
        "law_table": expected["law_table"],
        "tick_table": expected["tick_table"],
        "relation_table": expected["relation_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rsem table mismatch: {key}")

    if report.get("schema") != "long.rsem.report@1":
        raise AssertionError("long_rsem report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rsem report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rsem all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rsem checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rsem report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rsem report hash mismatch")

    csv_shapes = [
        ("law.csv", LAW_COLUMNS, len(LAW_CODES)),
        ("tick.csv", TICK_COLUMNS, 20),
        ("relation.csv", RELATION_COLUMNS, 59),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_rsem {filename} shape mismatch")

    table_shapes = {
        "law_table": (len(LAW_CODES), len(LAW_COLUMNS)),
        "tick_table": (20, len(TICK_COLUMNS)),
        "relation_table": (59, len(RELATION_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_rsem {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "affine_tick_count": 20,
        "relation_row_count": 59,
        "covered_tick_count": 20,
        "guarded_semantic_tick_count": 20,
        "single_valued_tick_count": 7,
        "multivalued_tick_count": 13,
        "guarded_semantic_relation_count": 59,
        "raw_backed_relation_count": 59,
        "unit_time_relation_count": 59,
        "contact_lift_relation_count": 59,
        "relation_semantic_law_flag": 1,
        "single_valued_functor_flag": 0,
        "semantic_a985_operation_flag": 0,
        "operation_row_materialized_count": 0,
        "physical_selector_axiom_flag": 0,
        "physical_transition_flag": 0,
        "gr_source_ready_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_rsem observable {key} mismatch")

    law_rows = rows_from_table(np.asarray(tables["law_table"]), LAW_COLUMNS)
    if [row["law_code"] for row in law_rows] != list(range(len(LAW_CODES))):
        raise AssertionError("long_rsem law code order mismatch")
    if [row["certified_flag"] for row in law_rows] != [1, 0, 0, 0]:
        raise AssertionError("long_rsem law certified flags mismatch")
    if law_rows[0]["guarded_relation_flag"] != 1:
        raise AssertionError("long_rsem relation law flag mismatch")

    tick_rows = rows_from_table(np.asarray(tables["tick_table"]), TICK_COLUMNS)
    if [row["visible_index"] for row in tick_rows] != list(range(20)):
        raise AssertionError("long_rsem tick order mismatch")
    if any(row["guarded_relation_semantic_flag"] != 1 for row in tick_rows):
        raise AssertionError("long_rsem guarded tick mismatch")
    if any(row["semantic_operation_flag"] != 0 for row in tick_rows):
        raise AssertionError("long_rsem operation tick mismatch")
    if sum(row["single_valued_flag"] for row in tick_rows) != 7:
        raise AssertionError("long_rsem singleton count mismatch")

    relation_rows = rows_from_table(
        np.asarray(tables["relation_table"]), RELATION_COLUMNS
    )
    if [row["relation_id"] for row in relation_rows] != list(range(59)):
        raise AssertionError("long_rsem relation ids mismatch")
    if any(row["guarded_relation_semantic_flag"] != 1 for row in relation_rows):
        raise AssertionError("long_rsem guarded relation mismatch")
    if any(row["semantic_operation_flag"] != 0 for row in relation_rows):
        raise AssertionError("long_rsem semantic operation relation mismatch")
    if any(row["physical_transition_flag"] != 0 for row in relation_rows):
        raise AssertionError("long_rsem physical relation mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_rsem manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_rsem manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rsem manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_rtick": LONG_RTICK,
        "long_rtick_tick": LONG_RTICK_TICK,
        "long_rtick_relation": LONG_RTICK_RELATION,
        "long_transition_sem": LONG_TRANSITION_SEM,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_rsem index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rsem index report hash mismatch")

    return {
        "schema": "long.rsem.verification@1",
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
    print(json.dumps(validate_long_rsem(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
