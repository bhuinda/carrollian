from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3m import (
        CARRIER_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        JOIN_COLUMNS,
        LONG_C59P3E_WEIGHT,
        LONG_C59P3N,
        LONG_C59P3N_WEIGHT_CLEAR,
        LONG_GCLK,
        LONG_GCLK_CYCLE,
        LONG_OPROM,
        LONG_OPROM_PROMOTION,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VISIBLE_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3m import (
        CARRIER_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        JOIN_COLUMNS,
        LONG_C59P3E_WEIGHT,
        LONG_C59P3N,
        LONG_C59P3N_WEIGHT_CLEAR,
        LONG_GCLK,
        LONG_GCLK_CYCLE,
        LONG_OPROM,
        LONG_OPROM_PROMOTION,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VISIBLE_COLUMNS,
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


def validate_long_c59p3m() -> dict[str, Any]:
    expected = build_payloads()
    c59p3m = load_json(OUT_DIR / "c59p3m.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3m != expected["c59p3m"]:
        raise AssertionError("long_c59p3m JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3m cert mismatch")
    for filename, key in {
        "join.csv": "join_csv",
        "carrier.csv": "carrier_csv",
        "visible.csv": "visible_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3m {filename} mismatch")

    for key, expected_array in {
        "join_table": expected["join_table"],
        "carrier_table": expected["carrier_table"],
        "visible_table": expected["visible_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3m table mismatch: {key}")

    if report.get("schema") != "long.c59p3m.report@1":
        raise AssertionError("long_c59p3m report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3m report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3m all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3m checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3m report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3m report hash mismatch")

    csv_shapes = [
        ("join.csv", JOIN_COLUMNS, 229),
        ("carrier.csv", CARRIER_COLUMNS, 77),
        ("visible.csv", VISIBLE_COLUMNS, 17),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3m {filename} shape mismatch")

    table_shapes = {
        "join_table": (229, len(JOIN_COLUMNS)),
        "carrier_table": (77, len(CARRIER_COLUMNS)),
        "visible_table": (17, len(VISIBLE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3m {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "carrier_row_count": 77,
        "active_atom_count": 17,
        "active_visible_index_count": 17,
        "active_unique_promotion_row_count": 49,
        "inactive_promotion_row_count": 10,
        "joined_row_count": 229,
        "zero_promotion_carrier_count": 0,
        "visible20_cleared_carrier_count": 77,
        "operation_row_join_count": 0,
        "semantic_transition_join_count": 0,
        "operation_backed_join_count": 0,
        "operation_backed_carrier_count": 0,
        "operation_promotion_flag": 0,
        "semantic_transition_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "first_failure_gap_code": 2,
        "next_gap_code": 4,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3m observable {key} mismatch")

    join_rows = rows_from_table(np.asarray(tables["join_table"]), JOIN_COLUMNS)
    if [row["join_id"] for row in join_rows] != list(range(229)):
        raise AssertionError("long_c59p3m join ids mismatch")
    if sum(row["operation_row_present_flag"] for row in join_rows) != 0:
        raise AssertionError("long_c59p3m operation row count mismatch")
    if sum(row["semantic_transition_flag"] for row in join_rows) != 0:
        raise AssertionError("long_c59p3m semantic transition count mismatch")
    if sum(row["operation_backed_normalized_flag"] for row in join_rows) != 0:
        raise AssertionError("long_c59p3m operation-backed join count mismatch")
    if {row["obstruction_code"] for row in join_rows} != {0}:
        raise AssertionError("long_c59p3m obstruction code mismatch")

    carrier_rows = rows_from_table(np.asarray(tables["carrier_table"]), CARRIER_COLUMNS)
    if [row["carrier_id"] for row in carrier_rows] != list(range(77)):
        raise AssertionError("long_c59p3m carrier ids mismatch")
    if sum(row["visible20_cleared_flag"] for row in carrier_rows) != 77:
        raise AssertionError("long_c59p3m carrier clearance mismatch")
    if sum(int(row["promotion_row_count"] == 0) for row in carrier_rows) != 0:
        raise AssertionError("long_c59p3m zero-promotion carrier mismatch")
    if max(row["promotion_row_count"] for row in carrier_rows) != 6:
        raise AssertionError("long_c59p3m max promotion multiplicity mismatch")

    visible_rows = rows_from_table(np.asarray(tables["visible_table"]), VISIBLE_COLUMNS)
    if [row["visible_index"] for row in visible_rows] != [
        0,
        1,
        3,
        4,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        16,
        17,
        18,
        19,
    ]:
        raise AssertionError("long_c59p3m active visible indices mismatch")
    if sum(row["join_count"] for row in visible_rows) != 229:
        raise AssertionError("long_c59p3m visible join total mismatch")
    if sum(row["operation_row_count"] for row in visible_rows) != 0:
        raise AssertionError("long_c59p3m visible operation total mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3m gap certified vector mismatch")
    if [row["obstruction_flag"] for row in gap_rows] != [0, 0, 1, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3m gap obstruction vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3m gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3m manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3m manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3m manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3n": LONG_C59P3N,
        "long_c59p3n_weight_clear": LONG_C59P3N_WEIGHT_CLEAR,
        "long_c59p3e_weight": LONG_C59P3E_WEIGHT,
        "long_gclk": LONG_GCLK,
        "long_gclk_cycle": LONG_GCLK_CYCLE,
        "long_oprom": LONG_OPROM,
        "long_oprom_promotion": LONG_OPROM_PROMOTION,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3m index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3m index report hash mismatch")

    return {
        "schema": "long.c59p3m.verification@1",
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
    print(json.dumps(validate_long_c59p3m(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
