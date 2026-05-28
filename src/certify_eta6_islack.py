from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_islack import (
        AEXT_REPORT,
        AEXT_TABLES,
        DERIVE_SCRIPT,
        EXT_TABLES,
        HOLONOMY_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_LIMIT,
        SROWS_REPORT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        ext,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_islack import (
        AEXT_REPORT,
        AEXT_TABLES,
        DERIVE_SCRIPT,
        EXT_TABLES,
        HOLONOMY_REPORT,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SAMPLE_COLUMNS,
        SAMPLE_LIMIT,
        SROWS_REPORT,
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


def validate_eta6_islack() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    islack = load_json(OUT_DIR / "islack.json")
    cert = load_json(OUT_DIR / "cert.json")
    sample_csv = (OUT_DIR / "samp.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(ext.nonholonomic.preservation.INDEX_PATH)

    if islack != expected["islack"]:
        raise AssertionError("eta6_islack JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_islack cert mismatch")
    if sample_csv != expected["samples_csv"]:
        raise AssertionError("eta6_islack sample CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_islack obs CSV mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["observable_table"],
    ):
        raise AssertionError("eta6_islack observable table mismatch")

    if report.get("schema") != "eta6.islack.report@1":
        raise AssertionError("eta6_islack report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_islack report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_islack all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_islack checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_islack report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_islack report hash mismatch")

    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_islack obs table shape mismatch")
    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "vertex_count": 60,
        "support_face_count": 32,
        "nonface_slack_per_vertex": 29,
        "unique_intrinsic_height_count": 1,
        "intrinsic_height_value": 48_849_960_057_179,
        "signed_row_count": 4_903_515,
        "zero_pairing_count": 4_894_923,
        "positive_pairing_count": 8_592,
        "zero_c4_pairing_count": 2_043,
        "zero_c5_pairing_count": 4_892_880,
        "positive_c4_pairing_count": 8_592,
        "positive_c5_pairing_count": 0,
        "min_positive_pairing": 97_699_920_114_358,
        "max_positive_pairing_bit_length": 128,
        "strict_intrinsic_orientation_flag": 0,
        "symmetric_slack_degenerate_flag": 1,
        "eta6_holonomy_pairing": 1,
        "eta6_support_preserved_flag": 1,
        "surgery_certificate_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_islack observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("height_vector_sha256") != (
        "a57d06fdcc1e3946c4ccf770586f8d3a38004305a18bc43d28fe6267e664254e"
    ):
        raise AssertionError("eta6_islack height hash mismatch")
    if witness.get("row_stream_sha256") != (
        "d2bb71ef191a6360aad4754c53a911975a43cdd831d6a8042adf5db7742cd00e"
    ):
        raise AssertionError("eta6_islack row stream hash mismatch")
    if witness.get("pairing_counts", {}).get("max_positive_pairing") != (
        204_605_441_516_922_090_395_524_299_233_846_302_500
    ):
        raise AssertionError("eta6_islack max positive pairing mismatch")
    sample_lines = sample_csv.splitlines()
    if sample_lines[0].split(",") != SAMPLE_COLUMNS:
        raise AssertionError("eta6_islack sample header mismatch")
    if len(sample_lines) != SAMPLE_LIMIT + 1:
        raise AssertionError("eta6_islack sample count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("aext_report", {}), AEXT_REPORT, "aext report")
    assert_file_hash(inputs.get("aext_tables", {}), AEXT_TABLES, "aext tables")
    assert_file_hash(inputs.get("ext_tables", {}), EXT_TABLES, "ext tables")
    assert_file_hash(inputs.get("srows_report", {}), SROWS_REPORT, "srows report")
    assert_file_hash(
        inputs.get("holonomy_report", {}),
        HOLONOMY_REPORT,
        "holonomy report",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.islack.manifest@1":
        raise AssertionError("eta6_islack manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_islack manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_islack manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_islack missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_islack index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_islack index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.islack.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_islack(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
