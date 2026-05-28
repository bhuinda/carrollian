from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_aext import (
        AEXT_COLUMNS,
        C4_COLUMNS,
        DERIVE_SCRIPT,
        EXT_REPORT,
        EXT_TABLES,
        GORDAN_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        ext,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_aext import (
        AEXT_COLUMNS,
        C4_COLUMNS,
        DERIVE_SCRIPT,
        EXT_REPORT,
        EXT_TABLES,
        GORDAN_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        ext,
        pair,
    )


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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_eta6_aext() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    aext = load_json(OUT_DIR / "aext.json")
    cert = load_json(OUT_DIR / "cert.json")
    aext_csv = (OUT_DIR / "aext.csv").read_text(encoding="utf-8")
    c4_csv = (OUT_DIR / "c4.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(ext.nonholonomic.preservation.INDEX_PATH)

    if aext != expected["aext"]:
        raise AssertionError("eta6_aext JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_aext cert mismatch")
    if aext_csv != expected["aext_csv"]:
        raise AssertionError("eta6_aext exterior CSV mismatch")
    if c4_csv != expected["c4_csv"]:
        raise AssertionError("eta6_aext c4 CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_aext obs CSV mismatch")
    for name in ["aext_table", "c4_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6_aext table {name} mismatch")

    if report.get("schema") != "eta6.aext.report@1":
        raise AssertionError("eta6_aext report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_aext report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_aext all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_aext checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_aext report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_aext report hash mismatch")

    aext_table = np.asarray(tables["aext_table"], dtype=np.int64)
    c4_table = np.asarray(tables["c4_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(aext_table.shape) != (1_740, len(AEXT_COLUMNS)):
        raise AssertionError("eta6_aext table shape mismatch")
    if tuple(c4_table.shape) != (10_635, len(C4_COLUMNS)):
        raise AssertionError("eta6_aext c4 table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_aext obs table shape mismatch")

    aext_rows = table_rows(aext_table, AEXT_COLUMNS)
    c4_rows = table_rows(c4_table, C4_COLUMNS)
    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    if any(row["positive_flag"] != 1 for row in aext_rows):
        raise AssertionError("eta6_aext nonpositive exterior row")
    if min(row["test_value_x1e12"] for row in aext_rows) != 350_487_408_079:
        raise AssertionError("eta6_aext min test value mismatch")
    if max(row["test_value_x1e12"] for row in aext_rows) != 3_103_251_249_022:
        raise AssertionError("eta6_aext max test value mismatch")
    if any(row["circuit_id"] != row_id for row_id, row in enumerate(c4_rows)):
        raise AssertionError("eta6_aext c4 ids are not consecutive")
    if any(
        [row["v0"], row["v1"], row["v2"], row["v3"]]
        != sorted([row["v0"], row["v1"], row["v2"], row["v3"]])
        for row in c4_rows
    ):
        raise AssertionError("eta6_aext c4 row is not sorted")

    required = {
        "aext_row_count": 1_740,
        "aext_positive_row_count": 1_740,
        "aext_zero_row_count": 0,
        "aext_test_vector_dimension": 1,
        "aext_test_h_x1e12": ext.SCALE,
        "aext_min_test_value_x1e12": 350_487_408_079,
        "aext_max_test_value_x1e12": 3_103_251_249_022,
        "aext_gordan_no_nonzero_y_flag": 1,
        "collinear_triple_count": 0,
        "minimal_c4_count": 10_635,
        "minimal_c5_count": 4_892_880,
        "minimal_affine_circuit_count": 4_903_515,
        "circuit_census_gap_flag": 1,
        "full_circuit_gordan_flag": 0,
        "surgery_certificate_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_aext observable {key} mismatch")
    if obs[OBS_CODES["max_c4_det_abs_x1e15"]] >= 100_000:
        raise AssertionError("eta6_aext c4 determinant residual too large")
    if obs[OBS_CODES["min_non_c4_det_abs_x1e12"]] <= 1_000_000_000:
        raise AssertionError("eta6_aext non-c4 determinant gap too small")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("ext_report", {}), EXT_REPORT, "ext report")
    assert_file_hash(inputs.get("ext_tables", {}), EXT_TABLES, "ext tables")
    assert_file_hash(
        inputs.get("gordan_report", {}),
        GORDAN_REPORT,
        "gordan report",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.aext.manifest@1":
        raise AssertionError("eta6_aext manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_aext manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_aext manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_aext missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_aext index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_aext index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.aext.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_aext(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
