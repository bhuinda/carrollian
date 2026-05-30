from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3w import (
        BALANCE_COLUMNS,
        EDGE_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3F,
        LONG_C59P3F_ASSIGNMENT,
        LONG_C59P3U,
        LONG_C59P3U_SOURCE,
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
    from derive_long_c59p3w import (
        BALANCE_COLUMNS,
        EDGE_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3F,
        LONG_C59P3F_ASSIGNMENT,
        LONG_C59P3U,
        LONG_C59P3U_SOURCE,
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


def validate_long_c59p3w() -> dict[str, Any]:
    expected = build_payloads()
    c59p3w = load_json(OUT_DIR / "c59p3w.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3w != expected["c59p3w"]:
        raise AssertionError("long_c59p3w JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3w cert mismatch")
    for filename, key in {
        "edge.csv": "edge_csv",
        "balance.csv": "balance_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3w {filename} mismatch")

    for key, expected_array in {
        "edge_table": expected["edge_table"],
        "balance_table": expected["balance_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3w table mismatch: {key}")

    if report.get("schema") != "long.c59p3w.report@1":
        raise AssertionError("long_c59p3w report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3w report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3w all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3w checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3w report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3w report hash mismatch")

    csv_shapes = [
        ("edge.csv", EDGE_COLUMNS, 14),
        ("balance.csv", BALANCE_COLUMNS, 20),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3w {filename} shape mismatch")

    table_shapes = {
        "edge_table": (14, len(EDGE_COLUMNS)),
        "balance_table": (20, len(BALANCE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3w {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "source_row_count": 14,
        "assignment_row_count": 59,
        "stress_edge_count": 14,
        "atom_count": 20,
        "source_assignment_total": 59,
        "source_signed_tension_total_scaled": -197809407552,
        "source_abs_tension_total_scaled": 354128490312,
        "global_divergence_sum_scaled": 0,
        "local_balanced_atom_count": 3,
        "local_unbalanced_atom_count": 17,
        "max_abs_divergence_scaled": 180000000000,
        "incident_abs_tension_total_scaled": 708256980624,
        "global_balance_flag": 1,
        "local_balance_flag": 0,
        "operation_backed_source_count": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 3,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3w observable {key} mismatch")

    edge_rows = rows_from_table(np.asarray(tables["edge_table"]), EDGE_COLUMNS)
    if [row["stress_edge_id"] for row in edge_rows] != [
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
        raise AssertionError("long_c59p3w edge ids mismatch")
    if sum(row["assignment_count"] for row in edge_rows) != 59:
        raise AssertionError("long_c59p3w edge assignment total mismatch")
    if sum(row["signed_tension_sum_scaled"] for row in edge_rows) != -197809407552:
        raise AssertionError("long_c59p3w edge signed total mismatch")
    if sum(row["abs_tension_sum_scaled"] for row in edge_rows) != 354128490312:
        raise AssertionError("long_c59p3w edge abs total mismatch")

    balance_rows = rows_from_table(
        np.asarray(tables["balance_table"]), BALANCE_COLUMNS
    )
    if [row["atom_id"] for row in balance_rows] != list(range(20)):
        raise AssertionError("long_c59p3w atom ids mismatch")
    if sum(row["net_divergence_scaled"] for row in balance_rows) != 0:
        raise AssertionError("long_c59p3w global divergence mismatch")
    if sum(row["local_balance_flag"] for row in balance_rows) != 3:
        raise AssertionError("long_c59p3w local balance count mismatch")
    if max(abs(row["net_divergence_scaled"]) for row in balance_rows) != 180000000000:
        raise AssertionError("long_c59p3w max divergence mismatch")
    zero_atoms = [
        row["atom_id"] for row in balance_rows if row["local_balance_flag"] == 1
    ]
    if zero_atoms != [2, 4, 15]:
        raise AssertionError("long_c59p3w balanced atom set mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3w gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3w gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3w manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3w manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3w manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3u": LONG_C59P3U,
        "long_c59p3u_source": LONG_C59P3U_SOURCE,
        "long_c59p3f": LONG_C59P3F,
        "long_c59p3f_assignment": LONG_C59P3F_ASSIGNMENT,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3w index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3w index report hash mismatch")

    return {
        "schema": "long.c59p3w.verification@1",
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
    print(json.dumps(validate_long_c59p3w(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
