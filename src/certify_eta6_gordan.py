from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_gordan import (
        DUAL_COLUMNS,
        DERIVE_SCRIPT,
        EXT_REPORT,
        EXT_TABLES,
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
    from derive_eta6_gordan import (
        DUAL_COLUMNS,
        DERIVE_SCRIPT,
        EXT_REPORT,
        EXT_TABLES,
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


def validate_eta6_gordan() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    gordan = load_json(OUT_DIR / "gordan.json")
    cert = load_json(OUT_DIR / "cert.json")
    dual_csv = (OUT_DIR / "dual.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(ext.nonholonomic.preservation.INDEX_PATH)

    if gordan != expected["gordan"]:
        raise AssertionError("eta6_gordan JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_gordan cert mismatch")
    if dual_csv != expected["dual_csv"]:
        raise AssertionError("eta6_gordan dual CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_gordan obs CSV mismatch")
    for name in ["dual_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6_gordan table {name} mismatch")

    if report.get("schema") != "eta6.gordan.report@1":
        raise AssertionError("eta6_gordan report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_gordan report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_gordan all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_gordan checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_gordan report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_gordan report hash mismatch")

    dual_table = np.asarray(tables["dual_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(dual_table.shape) != (32, len(DUAL_COLUMNS)):
        raise AssertionError("eta6_gordan dual table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_gordan obs table shape mismatch")

    dual_rows = table_rows(dual_table, DUAL_COLUMNS)
    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    if min(row["test_value_x1e12"] for row in dual_rows) != 1_511_522_628_152:
        raise AssertionError("eta6_gordan min test value mismatch")
    if max(row["test_value_x1e12"] for row in dual_rows) != 1_551_625_624_511:
        raise AssertionError("eta6_gordan max test value mismatch")
    if any(row["positive_flag"] != 1 for row in dual_rows):
        raise AssertionError("eta6_gordan nonpositive dual row")

    required = {
        "support_face_row_count": 32,
        "expanded_support_row_count": 1_740,
        "gordan_test_vector_dimension": 4,
        "test_vector_a0_x1e12": ext.SCALE,
        "test_vector_a1_x1e12": 0,
        "test_vector_a2_x1e12": 0,
        "test_vector_a3_x1e12": 0,
        "min_dual_test_value_x1e12": 1_511_522_628_152,
        "max_dual_test_value_x1e12": 1_551_625_624_511,
        "positive_dual_row_count": 32,
        "zero_dual_row_count": 0,
        "gordan_no_nonzero_y_flag": 1,
        "support_plane_gordan_certificate_flag": 1,
        "full_affine_circuit_gordan_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_gordan observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("ext_report", {}), EXT_REPORT, "ext report")
    assert_file_hash(inputs.get("ext_tables", {}), EXT_TABLES, "ext tables")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.gordan.manifest@1":
        raise AssertionError("eta6_gordan manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_gordan manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_gordan manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_gordan missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_gordan index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_gordan index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.gordan.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_gordan(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
