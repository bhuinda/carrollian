from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_srows import (
        AEXT_REPORT,
        AEXT_TABLES,
        DERIVE_SCRIPT,
        EXT_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_LIMIT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        aext,
        build_payloads,
        ext,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_srows import (
        AEXT_REPORT,
        AEXT_TABLES,
        DERIVE_SCRIPT,
        EXT_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_LIMIT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        aext,
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


def validate_eta6_srows() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    srows = load_json(OUT_DIR / "srows.json")
    cert = load_json(OUT_DIR / "cert.json")
    sample_csv = (OUT_DIR / "samp.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(ext.nonholonomic.preservation.INDEX_PATH)

    if srows != expected["srows"]:
        raise AssertionError("eta6_srows JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_srows cert mismatch")
    if sample_csv != expected["samples_csv"]:
        raise AssertionError("eta6_srows sample CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_srows obs CSV mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["observable_table"],
    ):
        raise AssertionError("eta6_srows observable table mismatch")

    if report.get("schema") != "eta6.srows.report@1":
        raise AssertionError("eta6_srows report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_srows report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_srows all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_srows checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_srows report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_srows report hash mismatch")

    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_srows obs table shape mismatch")
    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "signed_row_count": 4_903_515,
        "signed_c4_row_count": 10_635,
        "signed_c5_row_count": 4_892_880,
        "positive_height_row_count": 4_903_515,
        "zero_height_row_count": 0,
        "min_height_value_bit_length": 8,
        "max_height_value_bit_length": 141,
        "max_abs_coefficient_bit_length": 123,
        "positive_coefficient_count": 12_280_656,
        "negative_coefficient_count": 12_226_284,
        "height_vector_dimension": 60,
        "height_min_value": 56,
        "height_max_value": 279_067,
        "full_signed_circuit_gordan_flag": 1,
        "intrinsic_surgery_orientation_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_srows observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("row_stream_sha256") != (
        "2d4f17d00b4e1408d408e275eabd2c7095641b0544ece528729d86b83c238e84"
    ):
        raise AssertionError("eta6_srows row stream hash mismatch")
    if witness.get("support_stream_sha256") != (
        "16a3ba24aef7c4b02f306601dd45438ccda18f0257a125a3cc98acd4e523639e"
    ):
        raise AssertionError("eta6_srows support stream hash mismatch")
    if witness.get("height_vector_sha256") != (
        "3287f972a5b170b1b98212122fc9c71076b80af61ebe55a9ada1027e68190399"
    ):
        raise AssertionError("eta6_srows height vector hash mismatch")
    signed = witness.get("signed_rows", {})
    if signed.get("min_height_value") != 146:
        raise AssertionError("eta6_srows minimum height value mismatch")
    if signed.get("max_height_value") != (
        1_785_469_952_977_992_005_725_003_102_734_298_922_128_131
    ):
        raise AssertionError("eta6_srows maximum height value mismatch")
    if signed.get("max_abs_coefficient") != (
        6_765_881_002_874_089_994_707_122_257_159_202_037
    ):
        raise AssertionError("eta6_srows max coefficient mismatch")
    sample_lines = sample_csv.splitlines()
    if sample_lines[0].split(",") != SAMPLE_COLUMNS:
        raise AssertionError("eta6_srows sample header mismatch")
    if len(sample_lines) != SAMPLE_LIMIT + 1:
        raise AssertionError("eta6_srows sample row count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("aext_report", {}), AEXT_REPORT, "aext report")
    assert_file_hash(inputs.get("aext_tables", {}), AEXT_TABLES, "aext tables")
    assert_file_hash(inputs.get("ext_tables", {}), EXT_TABLES, "ext tables")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.srows.manifest@1":
        raise AssertionError("eta6_srows manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_srows manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_srows manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_srows missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_srows index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_srows index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.srows.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_srows(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
