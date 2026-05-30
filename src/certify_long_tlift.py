from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_tlift import (
        CANDIDATE_COLUMNS,
        FIELD_CODES,
        INDEX_PATH,
        LONG_CONTACT_CSV,
        LONG_CONTACT_LIFT,
        LONG_GCLK,
        LONG_GCLK_CLOCK,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_ENDPOINT,
        LONG_TRANSITION_SEM,
        MATCH_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        ORIENTATION_CODES,
        OUT_DIR,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALUE_CODES,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_tlift import (
        CANDIDATE_COLUMNS,
        FIELD_CODES,
        INDEX_PATH,
        LONG_CONTACT_CSV,
        LONG_CONTACT_LIFT,
        LONG_GCLK,
        LONG_GCLK_CLOCK,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_ENDPOINT,
        LONG_TRANSITION_SEM,
        MATCH_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        ORIENTATION_CODES,
        OUT_DIR,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALUE_CODES,
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


def candidate_by_codes(rows: list[dict[str, int]]) -> dict[tuple[str, str, str], dict[str, int]]:
    value_names = {value: key for key, value in VALUE_CODES.items()}
    field_names = {value: key for key, value in FIELD_CODES.items()}
    orientation_names = {value: key for key, value in ORIENTATION_CODES.items()}
    return {
        (
            value_names[row["value_code"]],
            field_names[row["field_code"]],
            orientation_names[row["orientation_code"]],
        ): row
        for row in rows
    }


def validate_long_tlift() -> dict[str, Any]:
    expected = build_payloads()
    tlift = load_json(OUT_DIR / "tlift.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if tlift != expected["tlift"]:
        raise AssertionError("long_tlift JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_tlift cert mismatch")
    for filename, key in {
        "candidate.csv": "candidate_csv",
        "match.csv": "match_csv",
        "schema.csv": "schema_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_tlift {filename} mismatch")

    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "match_table": expected["match_table"],
        "schema_table": expected["schema_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_tlift table mismatch: {key}")

    if report.get("schema") != "long.tlift.report@1":
        raise AssertionError("long_tlift report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_tlift report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_tlift all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_tlift checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tlift report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_tlift report hash mismatch")

    csv_shapes = [
        ("candidate.csv", CANDIDATE_COLUMNS, 24),
        ("match.csv", MATCH_COLUMNS, 20),
        ("schema.csv", SCHEMA_COLUMNS, len(SCHEMA_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_tlift {filename} shape mismatch")

    table_shapes = {
        "candidate_table": (24, len(CANDIDATE_COLUMNS)),
        "match_table": (20, len(MATCH_COLUMNS)),
        "schema_table": (len(SCHEMA_CODES), len(SCHEMA_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_tlift {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "affine_tick_count": 20,
        "transition_endpoint_count": 259,
        "transition_row_count": 642,
        "contact_row_count": 642,
        "candidate_encoding_count": 24,
        "full_lift_candidate_count": 0,
        "best_candidate_covered_ticks": 7,
        "best_candidate_total_matches": 7,
        "best_candidate_max_multiplicity": 1,
        "atom_basis_directed_covered_ticks": 3,
        "atom_basis_undirected_covered_ticks": 7,
        "coordinate_basis_directed_covered_ticks": 0,
        "coordinate_basis_undirected_covered_ticks": 0,
        "endpoint_address_full_lift_candidate_count": 0,
        "semantic_transition_operation_flag": 0,
        "semantic_transition_realized_count": 0,
        "operation_row_materialized_count": 0,
        "physical_transition_flag": 0,
        "affine_tick_lift_obstruction_flag": 1,
        "gr_source_ready_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_tlift observable {key} mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if sorted(row["candidate_id"] for row in candidate_rows) != list(range(24)):
        raise AssertionError("long_tlift candidate ids mismatch")
    if any(row["full_lift_flag"] != 0 for row in candidate_rows):
        raise AssertionError("long_tlift unexpected full lift")
    if max(row["tick_covered_count"] for row in candidate_rows) != 7:
        raise AssertionError("long_tlift best candidate count mismatch")
    by_code = candidate_by_codes(candidate_rows)
    if by_code[("atom_id", "basis_id", "directed")]["tick_covered_count"] != 3:
        raise AssertionError("long_tlift atom/basis directed mismatch")
    if by_code[("atom_id", "basis_id", "undirected")]["tick_covered_count"] != 7:
        raise AssertionError("long_tlift atom/basis undirected mismatch")
    if by_code[("coordinate_mask", "basis_id", "undirected")]["tick_covered_count"] != 0:
        raise AssertionError("long_tlift coordinate/basis mismatch")

    match_rows = rows_from_table(np.asarray(tables["match_table"]), MATCH_COLUMNS)
    if [row["visible_index"] for row in match_rows] != list(range(20)):
        raise AssertionError("long_tlift match row order mismatch")
    if sum(row["matched_flag"] for row in match_rows) != 7:
        raise AssertionError("long_tlift match count mismatch")
    if any(row["semantic_transition_flag"] != 0 for row in match_rows):
        raise AssertionError("long_tlift semantic match mismatch")
    if any(
        row["matched_flag"] == 1
        and (row["matched_left_raw_row_id"] < 0 or row["matched_right_raw_row_id"] < 0)
        for row in match_rows
    ):
        raise AssertionError("long_tlift matched raw row id mismatch")

    schema_rows = rows_from_table(np.asarray(tables["schema_table"]), SCHEMA_COLUMNS)
    if [row["schema_code"] for row in schema_rows] != list(range(len(SCHEMA_CODES))):
        raise AssertionError("long_tlift schema code order mismatch")
    if any(row["shared_key_flag"] != 0 for row in schema_rows):
        raise AssertionError("long_tlift shared key flag mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_tlift manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_tlift manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tlift manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_gclk": LONG_GCLK,
        "long_gclk_clock": LONG_GCLK_CLOCK,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_endpoint": LONG_TRANSITION_ENDPOINT,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_contact_lift": LONG_CONTACT_LIFT,
        "long_contact_csv": LONG_CONTACT_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_tlift index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_tlift index report hash mismatch")

    return {
        "schema": "long.tlift.verification@1",
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
    print(json.dumps(validate_long_tlift(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
