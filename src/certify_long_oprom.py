from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_oprom import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PROMOTION_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_oprom import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PROMOTION_COLUMNS,
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


def validate_long_oprom() -> dict[str, Any]:
    expected = build_payloads()
    oprom = load_json(OUT_DIR / "oprom.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if oprom != expected["oprom"]:
        raise AssertionError("long_oprom JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_oprom cert mismatch")
    for filename, key in {
        "promotion.csv": "promotion_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_oprom {filename} mismatch")

    for key, expected_array in {
        "promotion_table": expected["promotion_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_oprom table mismatch: {key}")

    if report.get("schema") != "long.oprom.report@1":
        raise AssertionError("long_oprom report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_oprom report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_oprom all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_oprom checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_oprom report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_oprom report hash mismatch")

    csv_shapes = [
        ("promotion.csv", PROMOTION_COLUMNS, 59),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_oprom {filename} shape mismatch")

    table_shapes = {
        "promotion_table": (59, len(PROMOTION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_oprom {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "golden_relation_row_count": 59,
        "transition_row_count": 642,
        "matched_transition_row_count": 59,
        "guarded_relation_row_count": 59,
        "operation_row_match_count": 0,
        "semantic_transition_match_count": 0,
        "promotion_success_count": 0,
        "promotion_blocked_count": 59,
        "operation_promotion_flag": 0,
        "semantic_a985_operation_flag": 0,
        "transition_composition_law_flag": 0,
        "physical_selector_axiom_flag": 0,
        "gr_source_ready_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_oprom observable {key} mismatch")

    promotion_rows = rows_from_table(
        np.asarray(tables["promotion_table"]), PROMOTION_COLUMNS
    )
    if [row["relation_id"] for row in promotion_rows] != list(range(59)):
        raise AssertionError("long_oprom relation id order mismatch")
    if any(row["transition_row_present_flag"] != 1 for row in promotion_rows):
        raise AssertionError("long_oprom transition row match mismatch")
    if any(row["operation_row_id"] != -1 for row in promotion_rows):
        raise AssertionError("long_oprom operation row id mismatch")
    if any(row["operation_promotion_flag"] != 0 for row in promotion_rows):
        raise AssertionError("long_oprom promotion flag mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["gap_code"] for row in gap_rows] != list(range(len(GAP_CODES))):
        raise AssertionError("long_oprom gap code order mismatch")
    if [row["obstruction_flag"] for row in gap_rows] != [0, 0, 1, 1]:
        raise AssertionError("long_oprom gap obstruction vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_oprom manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_oprom manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_oprom manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_rsem": LONG_RSEM,
        "long_rsem_relation": LONG_RSEM_RELATION,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_oprom index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_oprom index report hash mismatch")

    return {
        "schema": "long.oprom.verification@1",
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
    print(json.dumps(validate_long_oprom(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
