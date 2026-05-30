from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3k import (
        CANDIDATE_COLUMNS,
        COVER_COLUMNS,
        FIELD_CODES,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LIBRARY_CODES,
        LONG_C59P3G_TRANSITION_SCHEMA,
        LONG_C59P3H,
        LONG_C59P3J,
        LONG_CONTACT_CONTACT,
        LONG_CONTACT_LIFT,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_ENDPOINT,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        TARGET_SELECTOR_CODES,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3k import (
        CANDIDATE_COLUMNS,
        COVER_COLUMNS,
        FIELD_CODES,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LIBRARY_CODES,
        LONG_C59P3G_TRANSITION_SCHEMA,
        LONG_C59P3H,
        LONG_C59P3J,
        LONG_CONTACT_CONTACT,
        LONG_CONTACT_LIFT,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_ENDPOINT,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        TARGET_SELECTOR_CODES,
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


def validate_long_c59p3k() -> dict[str, Any]:
    expected = build_payloads()
    c59p3k = load_json(OUT_DIR / "c59p3k.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3k != expected["c59p3k"]:
        raise AssertionError("long_c59p3k JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3k cert mismatch")
    for filename, key in {
        "candidate.csv": "candidate_csv",
        "cover.csv": "cover_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3k {filename} mismatch")

    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "cover_table": expected["cover_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3k table mismatch: {key}")

    if report.get("schema") != "long.c59p3k.report@1":
        raise AssertionError("long_c59p3k report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3k report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3k all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3k checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3k report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3k report hash mismatch")

    csv_shapes = [
        ("candidate.csv", CANDIDATE_COLUMNS, 172),
        ("cover.csv", COVER_COLUMNS, 29),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3k {filename} shape mismatch")

    table_shapes = {
        "candidate_table": (172, len(CANDIDATE_COLUMNS)),
        "cover_table": (29, len(COVER_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3k {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 4,
        "input_certified_count": 4,
        "active_transition_count": 29,
        "direct_candidate_count": 108,
        "contact_candidate_count": 64,
        "mixed_candidate_count": 172,
        "full_candidate_count": 0,
        "best_candidate_id": 8,
        "best_candidate_library_code": LIBRARY_CODES["direct_endpoint_field"],
        "best_candidate_covered_transition_count": 15,
        "best_direct_candidate_id": 8,
        "best_direct_covered_transition_count": 15,
        "best_contact_candidate_id": 110,
        "best_contact_covered_transition_count": 11,
        "direct_union_covered_transition_count": 25,
        "contact_union_covered_transition_count": 18,
        "mixed_union_covered_transition_count": 26,
        "mixed_union_uncovered_transition_count": 3,
        "missing_transition_id_count": 3,
        "operation_promoted_row_count": 0,
        "semantic_operation_flag": 0,
        "transition_composition_law_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": GAP_CODES["transition_composition_law"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3k observable {key} mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if [row["candidate_id"] for row in candidate_rows] != list(range(172)):
        raise AssertionError("long_c59p3k candidate ids mismatch")
    if (
        sum(
            int(row["library_code"] == LIBRARY_CODES["direct_endpoint_field"])
            for row in candidate_rows
        )
        != 108
    ):
        raise AssertionError("long_c59p3k direct candidate count mismatch")
    if (
        sum(
            int(row["library_code"] == LIBRARY_CODES["contact_sample_slot"])
            for row in candidate_rows
        )
        != 64
    ):
        raise AssertionError("long_c59p3k contact candidate count mismatch")
    if sum(row["full_candidate_flag"] for row in candidate_rows) != 0:
        raise AssertionError("long_c59p3k full candidate flag mismatch")
    by_id = {row["candidate_id"]: row for row in candidate_rows}
    if by_id[8]["covered_transition_count"] != 15:
        raise AssertionError("long_c59p3k best direct candidate mismatch")
    if by_id[110]["covered_transition_count"] != 11:
        raise AssertionError("long_c59p3k best contact candidate mismatch")
    if by_id[110]["target_selector_code"] != TARGET_SELECTOR_CODES["sample_owner_a"]:
        raise AssertionError("long_c59p3k contact target selector mismatch")
    if by_id[110]["target_field_code"] != FIELD_CODES["target_addr"]:
        raise AssertionError("long_c59p3k contact target field mismatch")

    cover_rows = rows_from_table(np.asarray(tables["cover_table"]), COVER_COLUMNS)
    if [row["active_transition_id"] for row in cover_rows] != list(range(29)):
        raise AssertionError("long_c59p3k cover ids mismatch")
    if sum(row["direct_covered_flag"] for row in cover_rows) != 25:
        raise AssertionError("long_c59p3k direct union cover mismatch")
    if sum(row["contact_covered_flag"] for row in cover_rows) != 18:
        raise AssertionError("long_c59p3k contact union cover mismatch")
    if sum(row["mixed_covered_flag"] for row in cover_rows) != 26:
        raise AssertionError("long_c59p3k mixed union cover mismatch")
    missing_transition_ids = [
        row["transition_id"] for row in cover_rows if row["mixed_covered_flag"] == 0
    ]
    if missing_transition_ids != [24, 38, 40]:
        raise AssertionError("long_c59p3k missing transition ids mismatch")
    contact_only_transition_ids = [
        row["transition_id"]
        for row in cover_rows
        if row["direct_covered_flag"] == 0 and row["contact_covered_flag"] == 1
    ]
    if contact_only_transition_ids != [15]:
        raise AssertionError("long_c59p3k contact-only transition mismatch")
    if sum(row["mixed_obstruction_flag"] for row in cover_rows) != 3:
        raise AssertionError("long_c59p3k obstruction row count mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3k gap certified vector mismatch")
    if [row["obstruction_flag"] for row in gap_rows] != [0, 0, 0, 1, 1, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3k gap obstruction vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3k gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3k manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3k manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3k manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3h": LONG_C59P3H,
        "long_c59p3j": LONG_C59P3J,
        "long_contact_lift": LONG_CONTACT_LIFT,
        "long_contact_contact": LONG_CONTACT_CONTACT,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_c59p3g_transition_schema": LONG_C59P3G_TRANSITION_SCHEMA,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_transition_endpoint": LONG_TRANSITION_ENDPOINT,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3k index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3k index report hash mismatch")

    return {
        "schema": "long.c59p3k.verification@1",
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
    print(json.dumps(validate_long_c59p3k(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
