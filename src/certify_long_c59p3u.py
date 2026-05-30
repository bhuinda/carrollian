from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3u import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3F,
        LONG_C59P3F_ASSIGNMENT,
        LONG_OPROM,
        LONG_OPROM_PROMOTION,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OPCHECK_COLUMNS,
        OUT_DIR,
        SOURCE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3u import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3F,
        LONG_C59P3F_ASSIGNMENT,
        LONG_OPROM,
        LONG_OPROM_PROMOTION,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OPCHECK_COLUMNS,
        OUT_DIR,
        SOURCE_COLUMNS,
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


def validate_long_c59p3u() -> dict[str, Any]:
    expected = build_payloads()
    c59p3u = load_json(OUT_DIR / "c59p3u.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3u != expected["c59p3u"]:
        raise AssertionError("long_c59p3u JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3u cert mismatch")
    for filename, key in {
        "opcheck.csv": "opcheck_csv",
        "source.csv": "source_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3u {filename} mismatch")

    for key, expected_array in {
        "opcheck_table": expected["opcheck_table"],
        "source_table": expected["source_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3u table mismatch: {key}")

    if report.get("schema") != "long.c59p3u.report@1":
        raise AssertionError("long_c59p3u report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3u report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3u all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3u checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3u report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3u report hash mismatch")

    csv_shapes = [
        ("opcheck.csv", OPCHECK_COLUMNS, 59),
        ("source.csv", SOURCE_COLUMNS, 14),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3u {filename} shape mismatch")

    table_shapes = {
        "opcheck_table": (59, len(OPCHECK_COLUMNS)),
        "source_table": (14, len(SOURCE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3u {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "assignment_row_count": 59,
        "promotion_row_count": 59,
        "transition_row_count": 642,
        "joined_assignment_count": 59,
        "source_row_count": 14,
        "direct_assignment_count": 8,
        "reverse_assignment_count": 7,
        "fallback_assignment_count": 44,
        "formal_pushforward_count": 59,
        "operation_row_match_count": 0,
        "semantic_transition_match_count": 0,
        "operation_backed_source_count": 0,
        "source_assignment_total": 59,
        "source_signed_tension_total_scaled": -197809407552,
        "source_abs_tension_total_scaled": 354128490312,
        "source_max_assignment_multiplicity": 10,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 4,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3u observable {key} mismatch")

    opcheck_rows = rows_from_table(np.asarray(tables["opcheck_table"]), OPCHECK_COLUMNS)
    if [row["relation_id"] for row in opcheck_rows] != list(range(59)):
        raise AssertionError("long_c59p3u opcheck relation ids mismatch")
    if sum(row["formal_pushforward_flag"] for row in opcheck_rows) != 59:
        raise AssertionError("long_c59p3u formal pushforward count mismatch")
    if sum(row["promotion_transition_present_flag"] for row in opcheck_rows) != 59:
        raise AssertionError("long_c59p3u promotion join count mismatch")
    if sum(row["transition_row_present_flag"] for row in opcheck_rows) != 59:
        raise AssertionError("long_c59p3u transition join count mismatch")
    zero_columns = [
        "operation_row_present_flag",
        "semantic_transition_flag",
        "operation_backed_stress_source_flag",
    ]
    for column in zero_columns:
        if any(row[column] != 0 for row in opcheck_rows):
            raise AssertionError(f"long_c59p3u nonzero opcheck column: {column}")
    if sum(row["obstruction_code"] for row in opcheck_rows) != 59:
        raise AssertionError("long_c59p3u obstruction count mismatch")

    source_rows = rows_from_table(np.asarray(tables["source_table"]), SOURCE_COLUMNS)
    if [row["source_row_id"] for row in source_rows] != list(range(14)):
        raise AssertionError("long_c59p3u source row ids mismatch")
    if [row["stress_edge_id"] for row in source_rows] != [
        1,
        26,
        29,
        31,
        37,
        40,
        44,
        47,
        52,
        55,
        64,
        66,
        72,
        74,
    ]:
        raise AssertionError("long_c59p3u source stress-edge ids mismatch")
    if sum(row["assignment_count"] for row in source_rows) != 59:
        raise AssertionError("long_c59p3u source assignment total mismatch")
    if sum(row["direct_assignment_count"] for row in source_rows) != 8:
        raise AssertionError("long_c59p3u source direct total mismatch")
    if sum(row["reverse_assignment_count"] for row in source_rows) != 7:
        raise AssertionError("long_c59p3u source reverse total mismatch")
    if sum(row["fallback_assignment_count"] for row in source_rows) != 44:
        raise AssertionError("long_c59p3u source fallback total mismatch")
    if sum(row["signed_tension_sum_scaled"] for row in source_rows) != -197809407552:
        raise AssertionError("long_c59p3u source signed total mismatch")
    if sum(row["abs_tension_sum_scaled"] for row in source_rows) != 354128490312:
        raise AssertionError("long_c59p3u source abs total mismatch")
    if any(row["operation_backed_count"] != 0 for row in source_rows):
        raise AssertionError("long_c59p3u source operation-backed mismatch")
    if any(row["semantic_transition_count"] != 0 for row in source_rows):
        raise AssertionError("long_c59p3u source semantic count mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3u gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 1, 0]:
        raise AssertionError("long_c59p3u gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3u manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3u manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3u manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3f": LONG_C59P3F,
        "long_c59p3f_assignment": LONG_C59P3F_ASSIGNMENT,
        "long_oprom": LONG_OPROM,
        "long_oprom_promotion": LONG_OPROM_PROMOTION,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3u index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3u index report hash mismatch")

    return {
        "schema": "long.c59p3u.verification@1",
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
    print(json.dumps(validate_long_c59p3u(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
