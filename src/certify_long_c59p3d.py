from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3d import (
        ATOM_COLUMNS,
        CARRIER_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_ABMAP,
        LONG_ABMAP_DOMAIN,
        LONG_C59P3C,
        LONG_C59P3C_COUNTERTERM,
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
    from derive_long_c59p3d import (
        ATOM_COLUMNS,
        CARRIER_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_ABMAP,
        LONG_ABMAP_DOMAIN,
        LONG_C59P3C,
        LONG_C59P3C_COUNTERTERM,
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


def validate_long_c59p3d() -> dict[str, Any]:
    expected = build_payloads()
    c59p3d = load_json(OUT_DIR / "c59p3d.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3d != expected["c59p3d"]:
        raise AssertionError("long_c59p3d JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3d cert mismatch")
    for filename, key in {
        "atom.csv": "atom_csv",
        "carrier.csv": "carrier_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3d {filename} mismatch")

    for key, expected_array in {
        "atom_table": expected["atom_table"],
        "carrier_table": expected["carrier_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3d table mismatch: {key}")

    if report.get("schema") != "long.c59p3d.report@1":
        raise AssertionError("long_c59p3d report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3d report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3d all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3d checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3d report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3d report hash mismatch")

    csv_shapes = [
        ("atom.csv", ATOM_COLUMNS, 20),
        ("carrier.csv", CARRIER_COLUMNS, 77),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3d {filename} shape mismatch")

    table_shapes = {
        "atom_table": (20, len(ATOM_COLUMNS)),
        "carrier_table": (77, len(CARRIER_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3d {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "atom_count": 20,
        "domain_row_count": 90,
        "counterterm_support_count": 17,
        "selector_supported_counterterm_atom_count": 17,
        "selector_carrier_row_count": 77,
        "min_selector_domain_count_on_support": 3,
        "max_selector_domain_count_on_support": 6,
        "zero_counterterm_atom_count": 3,
        "zero_counterterm_domain_row_count": 13,
        "selector_carrier_flag": 1,
        "exact_selector_weight_distribution_flag": 0,
        "operation_backed_counterterm_flag": 0,
        "physical_selector_axiom_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 2,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3d observable {key} mismatch")

    atom_rows = rows_from_table(np.asarray(tables["atom_table"]), ATOM_COLUMNS)
    if [row["atom_id"] for row in atom_rows] != list(range(20)):
        raise AssertionError("long_c59p3d atom ids mismatch")
    if sum(row["counterterm_support_flag"] for row in atom_rows) != 17:
        raise AssertionError("long_c59p3d active atom count mismatch")
    if min(
        row["selector_domain_count"]
        for row in atom_rows
        if row["counterterm_support_flag"] == 1
    ) != 3:
        raise AssertionError("long_c59p3d min domain count mismatch")
    if max(
        row["selector_domain_count"]
        for row in atom_rows
        if row["counterterm_support_flag"] == 1
    ) != 6:
        raise AssertionError("long_c59p3d max domain count mismatch")
    if any(row["operation_backed_flag"] != 0 for row in atom_rows):
        raise AssertionError("long_c59p3d atom operation-backed mismatch")

    carrier_rows = rows_from_table(np.asarray(tables["carrier_table"]), CARRIER_COLUMNS)
    if [row["carrier_id"] for row in carrier_rows] != list(range(77)):
        raise AssertionError("long_c59p3d carrier ids mismatch")
    if sum(row["selector_carrier_flag"] for row in carrier_rows) != 77:
        raise AssertionError("long_c59p3d selector carrier count mismatch")
    if any(row["operation_backed_flag"] != 0 for row in carrier_rows):
        raise AssertionError("long_c59p3d carrier operation-backed mismatch")
    carrier_atoms = sorted({row["atom_id"] for row in carrier_rows})
    if carrier_atoms != [0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19]:
        raise AssertionError("long_c59p3d carrier atom set mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3d gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3d gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3d manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3d manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3d manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3c": LONG_C59P3C,
        "long_c59p3c_counterterm": LONG_C59P3C_COUNTERTERM,
        "long_abmap": LONG_ABMAP,
        "long_abmap_domain": LONG_ABMAP_DOMAIN,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3d index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3d index report hash mismatch")

    return {
        "schema": "long.c59p3d.verification@1",
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
    print(json.dumps(validate_long_c59p3d(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
