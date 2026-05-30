from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23wdep import (
        DECISION_COLUMNS,
        DECISION_TEXT_HASH,
        DERIVE_SCRIPT,
        EQUATION_COLUMNS,
        EQUATION_TEXT_HASH,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23wdep import (
        DECISION_COLUMNS,
        DECISION_TEXT_HASH,
        DERIVE_SCRIPT,
        EQUATION_COLUMNS,
        EQUATION_TEXT_HASH,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_DECISION = (0, 0, 1, 1, 0, 5376, 1568, 0, 1)
EXPECTED_FIRST_EQUATION = (0, 0, 224, 224, 1, 0, 0)
EXPECTED_LAST_EQUATION = (3, 3, 3808, 3808, 1, 0, 1)
EXPECTED_FIRST_LIMIT = (0, 0, 1, 1, 0)
EXPECTED_LAST_LIMIT = (3, 3, 1, 1, 0)


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


def assert_locked_hash(label: str, actual: str, expected: str) -> None:
    if not expected:
        raise AssertionError(f"{label} witness hash is not locked")
    if actual != expected:
        raise AssertionError(f"{label} witness hash mismatch")


def int_tuple(row: dict[str, str], columns: list[str]) -> tuple[int, ...]:
    return tuple(int(row[column]) for column in columns)


def validate_long_k23wdep() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23wdep_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23wdep seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23wdep cert mismatch")
    for filename, key in {
        "decision_rows.csv": "decision_csv",
        "equation_rows.csv": "equation_csv",
        "limit_rows.csv": "limit_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23wdep {filename} mismatch")
    for key, expected_array in {
        "decision_table": expected["decision_table"],
        "equation_table": expected["equation_table"],
        "limit_table": expected["limit_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23wdep table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23wdep matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23wdep.report@1":
        raise AssertionError("long_k23wdep report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23wdep report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23wdep all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23wdep checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23wdep report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23wdep report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("decision_rows.csv", DECISION_COLUMNS, 1),
        ("equation_rows.csv", EQUATION_COLUMNS, 4),
        ("limit_rows.csv", LIMIT_COLUMNS, 4),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23wdep {filename} shape mismatch")

    assert_locked_hash(
        "decision rows",
        hashlib.sha256(digest_text(DECISION_COLUMNS, csv_rows["decision_rows.csv"]).encode("ascii")).hexdigest(),
        DECISION_TEXT_HASH,
    )
    assert_locked_hash(
        "equation rows",
        hashlib.sha256(digest_text(EQUATION_COLUMNS, csv_rows["equation_rows.csv"]).encode("ascii")).hexdigest(),
        EQUATION_TEXT_HASH,
    )
    assert_locked_hash(
        "limit rows",
        hashlib.sha256(digest_text(LIMIT_COLUMNS, csv_rows["limit_rows.csv"]).encode("ascii")).hexdigest(),
        LIMIT_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["decision_table", "equation_table", "limit_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    if int_tuple(csv_rows["decision_rows.csv"][0], DECISION_COLUMNS) != EXPECTED_DECISION:
        raise AssertionError("long_k23wdep decision row mismatch")
    equation_rows = csv_rows["equation_rows.csv"]
    if int_tuple(equation_rows[0], EQUATION_COLUMNS) != EXPECTED_FIRST_EQUATION:
        raise AssertionError("long_k23wdep first equation mismatch")
    if int_tuple(equation_rows[-1], EQUATION_COLUMNS) != EXPECTED_LAST_EQUATION:
        raise AssertionError("long_k23wdep last equation mismatch")
    if sum(int(row["demotion_support_flag"]) for row in equation_rows) != 3:
        raise AssertionError("long_k23wdep demotion support mismatch")
    limit_rows = csv_rows["limit_rows.csv"]
    if int_tuple(limit_rows[0], LIMIT_COLUMNS) != EXPECTED_FIRST_LIMIT:
        raise AssertionError("long_k23wdep first limit row mismatch")
    if int_tuple(limit_rows[-1], LIMIT_COLUMNS) != EXPECTED_LAST_LIMIT:
        raise AssertionError("long_k23wdep last limit row mismatch")
    if any(int(row["open_flag"]) != 1 for row in limit_rows):
        raise AssertionError("long_k23wdep limit openness mismatch")
    if any(int(row["overclaim_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23wdep limit overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 1,
        "certified_input_count": 1,
        "decision_row_count": 1,
        "compact_wire_flag": 1,
        "wire_total_bytes": 224,
        "wire_row_count": 56,
        "table_index_dependency_count": 56,
        "shared_dependency_all_rows_flag": 1,
        "self_contained_public_transcript_flag": 0,
        "current_model_self_contained_bytes": 5376,
        "baseline_public_exchange_bytes": 1568,
        "current_model_delta_vs_baseline_bytes": 3808,
        "current_model_greater_than_baseline_flag": 1,
        "external_efficiency_claim_count": 0,
        "external_efficiency_path_demoted_count": 1,
        "equation_row_count": 4,
        "equation_pass_count": 4,
        "demotion_support_count": 3,
        "limit_row_count": 4,
        "open_limit_count": 4,
        "overclaim_count": 0,
        "decision_surface_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23wdep observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23wdep index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23wdep.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23wdep(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
