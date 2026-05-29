from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_h16 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REPORTS,
        STATUS,
        SURFACE_COLUMNS,
        SURFACE_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_h16 import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REPORTS,
        STATUS,
        SURFACE_COLUMNS,
        SURFACE_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_h16() -> dict[str, Any]:
    expected = build_payloads()
    h16_payload = load_json(OUT_DIR / "h16.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if h16_payload != expected["h16"]:
        raise AssertionError("long_h16 h16 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_h16 cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_h16 {filename} mismatch")

    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_h16 table mismatch: {key}")

    if report.get("schema") != "long.h16.report@1":
        raise AssertionError("long_h16 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_h16 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_h16 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_h16 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_h16 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_h16 report hash mismatch")

    csv_shapes = [
        ("surface.csv", SURFACE_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_h16 {filename} shape mismatch")

    table_shapes = {
        "surface_table": (9, len(SURFACE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_h16 {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 14,
        "input_certified_count": 14,
        "surface_row_count": 9,
        "resolved_surface_count": 9,
        "open_boundary_count": 7,
        "h16_sum_state_count": 288,
        "h16_gap_sum_state_count": 208,
        "component_path_total": 64_570_080,
        "active_owner_count": 51,
        "owner_cell_count": 749_239,
        "raw_tensor_support_count": 1_414_965,
        "raw_tensor_coeff_sum": 2_537_360,
        "raw_support_lift_positive_count": 288,
        "raw_coeff_lift_positive_count": 288,
        "sample_path_count": 288,
        "sample_gap_path_count": 208,
        "exact_composable_path_count": 0,
        "zeta_composable_path_count": 288,
        "scoped_measure_law_flag": 1,
        "full_raw_measure_certified_flag": 0,
        "full_raw_scope_gap_flag": 1,
        "full_raw_oriented_sheaf_flag": 1,
        "full_raw_positive_zeta_sheaf_flag": 0,
        "reverse_section_count": 937_376,
        "global_gap_check_count": 131_586,
        "global_gap_nonnegative_count": 131_586,
        "materialized_h16_profunctor_flag": 0,
        "current_model_obstruction_flag": 1,
        "active_h16_frontier_flag": 0,
        "boundary_decision_code": 3,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_h16 observable {key} mismatch")

    if hashlib.sha256(
        digest_text(SURFACE_COLUMNS, csv_rows["surface.csv"]).encode("ascii")
    ).hexdigest() != SURFACE_TEXT_HASH:
        raise AssertionError("long_h16 surface hash mismatch")
    if hashlib.sha256(
        digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
    ).hexdigest() != OBS_TEXT_HASH:
        raise AssertionError("long_h16 observable hash mismatch")

    inputs = report.get("inputs", {})
    for name, path in REPORTS.items():
        assert_file_hash(inputs.get(name, {}), path, f"{name} input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.h16.manifest@1":
        raise AssertionError("long_h16 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_h16 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_h16 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_h16 missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_h16 proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_h16 proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.h16.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "horizon16": witness.get("horizon16"),
            "surface_code_map": witness.get("surface_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_h16(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
