from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3h import (
        BEST_MATCH_COLUMNS,
        CANDIDATE_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3G,
        LONG_C59P3G_TRANSITION_SCHEMA,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_ENDPOINT,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_INDEX,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3h import (
        BEST_MATCH_COLUMNS,
        CANDIDATE_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3G,
        LONG_C59P3G_TRANSITION_SCHEMA,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_ENDPOINT,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_INDEX,
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


def validate_long_c59p3h() -> dict[str, Any]:
    expected = build_payloads()
    c59p3h = load_json(OUT_DIR / "c59p3h.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3h != expected["c59p3h"]:
        raise AssertionError("long_c59p3h JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3h cert mismatch")
    for filename, key in {
        "candidate.csv": "candidate_csv",
        "best_match.csv": "best_match_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3h {filename} mismatch")

    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "best_match_table": expected["best_match_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3h table mismatch: {key}")

    if report.get("schema") != "long.c59p3h.report@1":
        raise AssertionError("long_c59p3h report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3h report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3h all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3h checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3h report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3h report hash mismatch")

    csv_shapes = [
        ("candidate.csv", CANDIDATE_COLUMNS, 108),
        ("best_match.csv", BEST_MATCH_COLUMNS, 29),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3h {filename} shape mismatch")

    table_shapes = {
        "candidate_table": (108, len(CANDIDATE_COLUMNS)),
        "best_match_table": (29, len(BEST_MATCH_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3h {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "active_transition_count": 29,
        "candidate_count": 108,
        "full_address_map_candidate_count": 0,
        "best_candidate_id": 8,
        "best_candidate_covered_transition_count": 15,
        "best_candidate_uncovered_transition_count": 14,
        "best_candidate_total_raw_match_count": 15,
        "best_candidate_max_raw_match_count": 1,
        "best_match_row_count": 29,
        "best_raw_matched_row_count": 15,
        "best_raw_unmatched_row_count": 14,
        "operation_promoted_match_count": 0,
        "semantic_operation_flag": 0,
        "address_screen_obstruction_flag": 1,
        "transition_composition_law_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": 5,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3h observable {key} mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if [row["candidate_id"] for row in candidate_rows] != list(range(108)):
        raise AssertionError("long_c59p3h candidate ids mismatch")
    if sum(row["full_address_map_flag"] for row in candidate_rows) != 0:
        raise AssertionError("long_c59p3h full address map count mismatch")
    best = max(
        candidate_rows,
        key=lambda row: (
            row["covered_transition_count"],
            row["total_raw_match_count"],
            -row["candidate_id"],
        ),
    )
    if (
        best["candidate_id"],
        best["covered_transition_count"],
        best["total_raw_match_count"],
        best["max_raw_match_count"],
    ) != (8, 15, 15, 1):
        raise AssertionError("long_c59p3h best candidate mismatch")

    best_rows = rows_from_table(
        np.asarray(tables["best_match_table"]), BEST_MATCH_COLUMNS
    )
    if [row["active_transition_id"] for row in best_rows] != list(range(29)):
        raise AssertionError("long_c59p3h best active transition ids mismatch")
    if sum(row["raw_match_flag"] for row in best_rows) != 15:
        raise AssertionError("long_c59p3h best match count mismatch")
    if sum(row["operation_promoted_flag"] for row in best_rows) != 0:
        raise AssertionError("long_c59p3h promoted match count mismatch")
    if {row["candidate_id"] for row in best_rows} != {8}:
        raise AssertionError("long_c59p3h best candidate id mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3h gap certified vector mismatch")
    if [row["obstruction_flag"] for row in gap_rows] != [0, 0, 1, 0, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3h gap obstruction vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3h gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3h manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3h manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3h manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3g": LONG_C59P3G,
        "long_c59p3g_transition_schema": LONG_C59P3G_TRANSITION_SCHEMA,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_transition_endpoint": LONG_TRANSITION_ENDPOINT,
        "raw_index": RAW_INDEX,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3h index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3h index report hash mismatch")

    return {
        "schema": "long.c59p3h.verification@1",
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
    print(json.dumps(validate_long_c59p3h(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
