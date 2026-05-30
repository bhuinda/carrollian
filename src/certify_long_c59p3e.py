from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3e import (
        ATOM_SUM_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3D,
        LONG_C59P3D_ATOM,
        LONG_C59P3D_CARRIER,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        WEIGHT_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3e import (
        ATOM_SUM_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3D,
        LONG_C59P3D_ATOM,
        LONG_C59P3D_CARRIER,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        WEIGHT_COLUMNS,
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


def validate_long_c59p3e() -> dict[str, Any]:
    expected = build_payloads()
    c59p3e = load_json(OUT_DIR / "c59p3e.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3e != expected["c59p3e"]:
        raise AssertionError("long_c59p3e JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3e cert mismatch")
    for filename, key in {
        "weight.csv": "weight_csv",
        "atom_sum.csv": "atom_sum_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3e {filename} mismatch")

    for key, expected_array in {
        "weight_table": expected["weight_table"],
        "atom_sum_table": expected["atom_sum_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3e table mismatch: {key}")

    if report.get("schema") != "long.c59p3e.report@1":
        raise AssertionError("long_c59p3e report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3e report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3e all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3e checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3e report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3e report hash mismatch")

    csv_shapes = [
        ("weight.csv", WEIGHT_COLUMNS, 77),
        ("atom_sum.csv", ATOM_SUM_COLUMNS, 17),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3e {filename} shape mismatch")

    table_shapes = {
        "weight_table": (77, len(WEIGHT_COLUMNS)),
        "atom_sum_table": (17, len(ATOM_SUM_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3e {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 1,
        "input_certified_count": 1,
        "active_atom_count": 17,
        "carrier_row_count": 77,
        "exact_weight_row_count": 77,
        "atom_sum_pass_count": 17,
        "common_denominator": 20,
        "integral_weight_row_count": 30,
        "nonintegral_weight_row_count": 47,
        "integral_atom_count": 7,
        "nonintegral_atom_count": 10,
        "integral_distribution_flag": 0,
        "exact_rational_distribution_flag": 1,
        "common_den_weight_num_abs_total": 13159253255760,
        "operation_backed_counterterm_flag": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 3,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3e observable {key} mismatch")

    weight_rows = rows_from_table(np.asarray(tables["weight_table"]), WEIGHT_COLUMNS)
    if [row["carrier_id"] for row in weight_rows] != list(range(77)):
        raise AssertionError("long_c59p3e carrier ids mismatch")
    if sum(row["exact_weight_flag"] for row in weight_rows) != 77:
        raise AssertionError("long_c59p3e exact weight count mismatch")
    if sum(row["row_integral_flag"] for row in weight_rows) != 30:
        raise AssertionError("long_c59p3e integral row count mismatch")
    if any(row["operation_backed_flag"] != 0 for row in weight_rows):
        raise AssertionError("long_c59p3e operation-backed row mismatch")
    if max(row["weight_den"] for row in weight_rows) != 5:
        raise AssertionError("long_c59p3e max reduced denominator mismatch")
    common_den_abs = sum(abs(row["common_den_weight_num"]) for row in weight_rows)
    if common_den_abs != 13159253255760:
        raise AssertionError("long_c59p3e common-denominator abs total mismatch")

    atom_sum_rows = rows_from_table(
        np.asarray(tables["atom_sum_table"]), ATOM_SUM_COLUMNS
    )
    if [row["atom_id"] for row in atom_sum_rows] != [
        0,
        1,
        3,
        5,
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
        raise AssertionError("long_c59p3e atom sum ids mismatch")
    if sum(row["sum_equals_counterterm_flag"] for row in atom_sum_rows) != 17:
        raise AssertionError("long_c59p3e atom sum exactness mismatch")
    if sum(row["all_rows_integral_flag"] for row in atom_sum_rows) != 7:
        raise AssertionError("long_c59p3e integral atom count mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3e gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3e gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3e manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3e manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3e manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3d": LONG_C59P3D,
        "long_c59p3d_atom": LONG_C59P3D_ATOM,
        "long_c59p3d_carrier": LONG_C59P3D_CARRIER,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3e index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3e index report hash mismatch")

    return {
        "schema": "long.c59p3e.verification@1",
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
    print(json.dumps(validate_long_c59p3e(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
