from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_gap import (
        DERIVE_SCRIPT,
        HPOL_REPORT,
        MARG_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPL_REPORT,
        REPL_TABLES,
        SAMPLE_COLUMNS,
        EXPECTED_HPOL_MIN_COUNT,
        SAMPLE_LIMIT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        hpol,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_gap import (
        DERIVE_SCRIPT,
        HPOL_REPORT,
        MARG_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REPL_REPORT,
        REPL_TABLES,
        SAMPLE_COLUMNS,
        EXPECTED_HPOL_MIN_COUNT,
        SAMPLE_LIMIT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        hpol,
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


def validate_eta6_gap() -> dict[str, Any]:
    expected = build_payloads()
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    gap = load_json(OUT_DIR / "gap.json")
    cert = load_json(OUT_DIR / "cert.json")
    marg_csv = (OUT_DIR / "marg.csv").read_text(encoding="utf-8")
    sample_csv = (OUT_DIR / "samp.csv").read_text(encoding="utf-8")
    obs_csv = (OUT_DIR / "obs.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    index = load_json(hpol.ext.nonholonomic.preservation.INDEX_PATH)

    if gap != expected["gap"]:
        raise AssertionError("eta6_gap JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("eta6_gap cert mismatch")
    if marg_csv != expected["marg_csv"]:
        raise AssertionError("eta6_gap margin CSV mismatch")
    if sample_csv != expected["samp_csv"]:
        raise AssertionError("eta6_gap sample CSV mismatch")
    if obs_csv != expected["obs_csv"]:
        raise AssertionError("eta6_gap obs CSV mismatch")
    if not np.array_equal(np.asarray(tables["margin_table"]), expected["marg_table"]):
        raise AssertionError("eta6_gap margin table mismatch")
    if not np.array_equal(np.asarray(tables["sample_table"]), expected["sample_table"]):
        raise AssertionError("eta6_gap sample table mismatch")
    if not np.array_equal(
        np.asarray(tables["observable_table"]),
        expected["obs_table"],
    ):
        raise AssertionError("eta6_gap observable table mismatch")

    if report.get("schema") != "eta6.gap.report@1":
        raise AssertionError("eta6_gap report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6_gap report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6_gap all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6_gap checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6_gap report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6_gap report hash mismatch")

    margin_table = np.asarray(tables["margin_table"], dtype=np.int64)
    sample_table = np.asarray(tables["sample_table"], dtype=np.int64)
    obs_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(margin_table.shape) != (2, len(MARG_COLUMNS)):
        raise AssertionError("eta6_gap margin table shape mismatch")
    expected_sample_rows = min(SAMPLE_LIMIT, EXPECTED_HPOL_MIN_COUNT)
    if tuple(sample_table.shape) != (expected_sample_rows, len(SAMPLE_COLUMNS)):
        raise AssertionError("eta6_gap sample table shape mismatch")
    if tuple(obs_table.shape) != (len(OBS_CODES), len(OBS_COLUMNS)):
        raise AssertionError("eta6_gap obs table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(obs_table, OBS_COLUMNS)
    }
    required = {
        "hpol_row_count": 4_903_515,
        "hpol_zero_count": 0,
        "hpol_positive_count": 4_903_515,
        "hpol_min_margin": 1,
        "hpol_max_margin_bit_length": 136,
        "hpol_row_hash_match_flag": 1,
        "hpol_gap_positive_flag": 1,
        "no_positive_annihilator_flag": 1,
        "repl_row_count": 2_831_367,
        "repl_zero_count": 0,
        "repl_positive_count": 2_831_367,
        "repl_min_margin": 146,
        "repl_gap_positive_flag": 1,
        "repl_row_hash_match_flag": 1,
        "checked_carrier_count": 2,
        "universal_completion_claim_flag": 0,
        "current_replacement_stability_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"eta6_gap observable {key} mismatch")
    min_count = obs.get(OBS_CODES["hpol_min_count"])
    min_c4 = obs.get(OBS_CODES["hpol_min_c4_count"])
    min_c5 = obs.get(OBS_CODES["hpol_min_c5_count"])
    if (
        min_count is None
        or min_count != EXPECTED_HPOL_MIN_COUNT
        or min_count != min_c4 + min_c5
    ):
        raise AssertionError("eta6_gap hpol min count mismatch")

    witness = report.get("witness", {})
    hpol_witness = witness.get("hpol", {})
    repl_witness = witness.get("repl", {})
    if hpol_witness.get("min_margin") != 1:
        raise AssertionError("eta6_gap hpol min margin mismatch")
    if hpol_witness.get("min_margin_count") != min_count:
        raise AssertionError("eta6_gap hpol min margin count mismatch")
    if hpol_witness.get("row_stream_sha256") != (
        "70a6216673205d9ed0e3df7a67fa9a61f05ea9343246cf06355b9d764eca72f0"
    ):
        raise AssertionError("eta6_gap hpol row hash mismatch")
    if repl_witness.get("min_margin") != 146:
        raise AssertionError("eta6_gap repl min margin mismatch")
    if repl_witness.get("row_stream_sha256") != (
        "58a495540af510f0ef52e8d730ffbf58d42c07725971dff463364f67d79e118c"
    ):
        raise AssertionError("eta6_gap repl row hash mismatch")
    sample_lines = sample_csv.splitlines()
    if sample_lines[0].split(",") != SAMPLE_COLUMNS:
        raise AssertionError("eta6_gap sample header mismatch")
    if len(sample_lines) != expected_sample_rows + 1:
        raise AssertionError("eta6_gap sample count mismatch")
    if marg_csv.splitlines()[0].split(",") != MARG_COLUMNS:
        raise AssertionError("eta6_gap margin header mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("hpol_report", {}), HPOL_REPORT, "hpol report")
    assert_file_hash(inputs.get("repl_report", {}), REPL_REPORT, "repl report")
    assert_file_hash(inputs.get("repl_tables", {}), REPL_TABLES, "repl tables")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "eta6.gap.manifest@1":
        raise AssertionError("eta6_gap manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_gap manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6_gap manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6_gap missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6_gap index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6_gap index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.gap.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_eta6_gap(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
