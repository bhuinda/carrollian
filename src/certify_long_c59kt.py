from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59kt import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        KERNEL_TIME_COLUMNS,
        LONG_C59ST,
        LONG_C59ST_KERNEL,
        LONG_TIME_MAP,
        LONG_TIME_MAP_MATRIX,
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
    from derive_long_c59kt import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        KERNEL_TIME_COLUMNS,
        LONG_C59ST,
        LONG_C59ST_KERNEL,
        LONG_TIME_MAP,
        LONG_TIME_MAP_MATRIX,
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


def validate_long_c59kt() -> dict[str, Any]:
    expected = build_payloads()
    c59kt = load_json(OUT_DIR / "c59kt.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59kt != expected["c59kt"]:
        raise AssertionError("long_c59kt JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59kt cert mismatch")
    for filename, key in {
        "kernel_time.csv": "kernel_time_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59kt {filename} mismatch")

    for key, expected_array in {
        "kernel_time_table": expected["kernel_time_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
        "q_pub_table": expected["q_pub_table"],
        "kernel_table": expected["kernel_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59kt table mismatch: {key}")

    if report.get("schema") != "long.c59kt.report@1":
        raise AssertionError("long_c59kt report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59kt report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59kt all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59kt checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59kt report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59kt report hash mismatch")

    csv_shapes = [
        ("kernel_time.csv", KERNEL_TIME_COLUMNS, 20),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59kt {filename} shape mismatch")

    table_shapes = {
        "kernel_time_table": (20, len(KERNEL_TIME_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
        "q_pub_table": (1, 20),
        "kernel_table": (1, 20),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59kt {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "public_rank": 20,
        "time_rank": 1,
        "kernel_support_count": 2,
        "q_pub_support_count": 1,
        "support_intersection_count": 0,
        "q_pub_dot_kernel": 0,
        "public_kernel_membership_flag": 1,
        "time_trace_nonzero_flag": 0,
        "kernel_time_identification_flag": 0,
        "finite_gauge_null_stress_mode_flag": 1,
        "stress_quotient_needed_flag": 1,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59kt observable {key} mismatch")

    kernel_time_rows = rows_from_table(
        np.asarray(tables["kernel_time_table"]), KERNEL_TIME_COLUMNS
    )
    if [row["atom_id"] for row in kernel_time_rows] != list(range(20)):
        raise AssertionError("long_c59kt kernel/time order mismatch")
    if sum(row["time_product"] for row in kernel_time_rows) != 0:
        raise AssertionError("long_c59kt time product mismatch")
    if sum(row["kernel_support_flag"] for row in kernel_time_rows) != 2:
        raise AssertionError("long_c59kt kernel support mismatch")
    if sum(row["q_pub_support_flag"] for row in kernel_time_rows) != 1:
        raise AssertionError("long_c59kt q_pub support mismatch")
    if sum(row["support_intersection_flag"] for row in kernel_time_rows) != 0:
        raise AssertionError("long_c59kt support intersection mismatch")
    for row in kernel_time_rows:
        if row["time_product"] != row["kernel_value"] * row["q_pub_value"]:
            raise AssertionError("long_c59kt product row mismatch")

    q_pub = np.asarray(tables["q_pub_table"], dtype=np.int64)[0]
    kernel = np.asarray(tables["kernel_table"], dtype=np.int64)[0]
    if int(q_pub.dot(kernel)) != 0:
        raise AssertionError("long_c59kt q_pub dot kernel mismatch")
    if int(np.count_nonzero(q_pub)) != 1:
        raise AssertionError("long_c59kt q_pub support count mismatch")
    if int(np.count_nonzero(kernel)) != 2:
        raise AssertionError("long_c59kt kernel support count mismatch")
    if int(np.count_nonzero(q_pub * kernel)) != 0:
        raise AssertionError("long_c59kt q/kernel support mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59kt decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 1, 0, 1]:
        raise AssertionError("long_c59kt decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 0, 1, 0]:
        raise AssertionError("long_c59kt decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59kt gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 1, 0, 0, 0]:
        raise AssertionError("long_c59kt gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59kt manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59kt manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59kt manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59st": LONG_C59ST,
        "long_c59st_kernel": LONG_C59ST_KERNEL,
        "long_time_map": LONG_TIME_MAP,
        "long_time_map_matrix": LONG_TIME_MAP_MATRIX,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59kt index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59kt index report hash mismatch")

    return {
        "schema": "long.c59kt.verification@1",
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
    print(json.dumps(validate_long_c59kt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
