from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3n import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_C59P3E,
        LONG_C59P3E_WEIGHT,
        LONG_GCLK,
        NORMALIZATION_CODES,
        NORMALIZATION_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PROFILE_COLUMNS,
        STATUS,
        THEOREM_ID,
        WEIGHT_CLEAR_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3n import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_BINC,
        LONG_C59P3E,
        LONG_C59P3E_WEIGHT,
        LONG_GCLK,
        NORMALIZATION_CODES,
        NORMALIZATION_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PROFILE_COLUMNS,
        STATUS,
        THEOREM_ID,
        WEIGHT_CLEAR_COLUMNS,
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


def validate_long_c59p3n() -> dict[str, Any]:
    expected = build_payloads()
    c59p3n = load_json(OUT_DIR / "c59p3n.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3n != expected["c59p3n"]:
        raise AssertionError("long_c59p3n JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3n cert mismatch")
    for filename, key in {
        "normalization.csv": "normalization_csv",
        "weight_clear.csv": "weight_clear_csv",
        "profile.csv": "profile_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3n {filename} mismatch")

    for key, expected_array in {
        "normalization_table": expected["normalization_table"],
        "weight_clear_table": expected["weight_clear_table"],
        "profile_table": expected["profile_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3n table mismatch: {key}")

    if report.get("schema") != "long.c59p3n.report@1":
        raise AssertionError("long_c59p3n report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3n report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3n all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3n checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3n report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3n report hash mismatch")

    csv_shapes = [
        ("normalization.csv", NORMALIZATION_COLUMNS, len(NORMALIZATION_CODES)),
        ("weight_clear.csv", WEIGHT_CLEAR_COLUMNS, 77),
        ("profile.csv", PROFILE_COLUMNS, 4),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3n {filename} shape mismatch")

    table_shapes = {
        "normalization_table": (
            len(NORMALIZATION_CODES),
            len(NORMALIZATION_COLUMNS),
        ),
        "weight_clear_table": (77, len(WEIGHT_CLEAR_COLUMNS)),
        "profile_table": (4, len(PROFILE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3n {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "carrier_row_count": 77,
        "common_denominator": 20,
        "visible_cycle_scale": 20,
        "hidden_clock_scale": 10,
        "packet_scale": 32,
        "joint_lcm_scale": 160,
        "visible_cleared_row_count": 77,
        "hidden_cleared_row_count": 65,
        "hidden_uncleared_row_count": 12,
        "packet_cleared_row_count": 52,
        "packet_uncleared_row_count": 25,
        "lcm_cleared_row_count": 77,
        "denominator1_row_count": 30,
        "denominator2_row_count": 10,
        "denominator4_row_count": 12,
        "denominator5_row_count": 25,
        "denominator5_atom_count": 5,
        "hidden_den4_uncleared_row_count": 12,
        "visible_denominator_clearance_flag": 1,
        "hidden_clock_clearance_flag": 0,
        "packet_index_clearance_flag": 0,
        "joint_lcm_clearance_flag": 1,
        "operation_backed_flag": 0,
        "physical_selector_axiom_flag": 0,
        "metric_derivation_flag": 0,
        "next_gap_code": 5,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3n observable {key} mismatch")

    normalization_rows = rows_from_table(
        np.asarray(tables["normalization_table"]), NORMALIZATION_COLUMNS
    )
    expected_scales = [20, 10, 20, 32, 160]
    if [row["scale_value"] for row in normalization_rows] != expected_scales:
        raise AssertionError("long_c59p3n normalization scale mismatch")
    if [row["clears_common_denominator_flag"] for row in normalization_rows] != [
        1,
        0,
        1,
        0,
        1,
    ]:
        raise AssertionError("long_c59p3n common denominator clearance mismatch")
    if [row["residual_denominator"] for row in normalization_rows] != [1, 2, 1, 5, 1]:
        raise AssertionError("long_c59p3n residual denominator mismatch")
    if [row["cleared_row_count"] for row in normalization_rows] != [77, 65, 77, 52, 77]:
        raise AssertionError("long_c59p3n normalization row counts mismatch")

    profile_rows = rows_from_table(np.asarray(tables["profile_table"]), PROFILE_COLUMNS)
    expected_profile = [
        (1, 30, 7, 1, 1, 1, 1),
        (2, 10, 2, 1, 1, 1, 1),
        (4, 12, 3, 1, 0, 1, 1),
        (5, 25, 5, 1, 1, 0, 1),
    ]
    actual_profile = [
        (
            row["weight_den"],
            row["row_count"],
            row["atom_count"],
            row["visible20_cleared_flag"],
            row["hidden10_cleared_flag"],
            row["packet32_cleared_flag"],
            row["lcm160_cleared_flag"],
        )
        for row in profile_rows
    ]
    if actual_profile != expected_profile:
        raise AssertionError("long_c59p3n denominator profile mismatch")

    weight_rows = rows_from_table(
        np.asarray(tables["weight_clear_table"]), WEIGHT_CLEAR_COLUMNS
    )
    if [row["carrier_id"] for row in weight_rows] != list(range(77)):
        raise AssertionError("long_c59p3n carrier ids mismatch")
    if sum(row["visible20_cleared_flag"] for row in weight_rows) != 77:
        raise AssertionError("long_c59p3n visible clearance count mismatch")
    if sum(row["hidden10_cleared_flag"] for row in weight_rows) != 65:
        raise AssertionError("long_c59p3n hidden clearance count mismatch")
    if sum(row["packet32_cleared_flag"] for row in weight_rows) != 52:
        raise AssertionError("long_c59p3n packet clearance count mismatch")
    if sum(row["lcm160_cleared_flag"] for row in weight_rows) != 77:
        raise AssertionError("long_c59p3n lcm clearance count mismatch")
    if sum(int(row["packet_residual_denominator"] == 5) for row in weight_rows) != 25:
        raise AssertionError("long_c59p3n packet residual count mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3n gap certified vector mismatch")
    if [row["obstruction_flag"] for row in gap_rows] != [0, 0, 1, 1, 0, 1, 1, 1]:
        raise AssertionError("long_c59p3n gap obstruction vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59p3n gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3n manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3n manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3n manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3e": LONG_C59P3E,
        "long_c59p3e_weight": LONG_C59P3E_WEIGHT,
        "long_gclk": LONG_GCLK,
        "long_binc": LONG_BINC,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3n index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3n index report hash mismatch")

    return {
        "schema": "long.c59p3n.verification@1",
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
    print(json.dumps(validate_long_c59p3n(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
