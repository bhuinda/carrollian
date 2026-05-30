from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23cop import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OPENING_COLUMNS,
        OPENING_NUMERIC_COLUMNS,
        OPENING_TEXT_HASH,
        OUT_DIR,
        PUBLIC_COLUMNS,
        PUBLIC_NUMERIC_COLUMNS,
        PUBLIC_TEXT_HASH,
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
    from derive_long_k23cop import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OPENING_COLUMNS,
        OPENING_NUMERIC_COLUMNS,
        OPENING_TEXT_HASH,
        OUT_DIR,
        PUBLIC_COLUMNS,
        PUBLIC_NUMERIC_COLUMNS,
        PUBLIC_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_PUBLIC = (
    "0",
    "0",
    "9dec6b9f118e950898d48bc91853af17bf8fcba13dbfd58c5e15042746ed8f25",
    "13424a6b56a52f480d41f30a71c22800fdbceb8dfb61fc81f6f5a478b892978c",
    "27",
    "1",
    "10",
    "106b681d171d054d41d0fb3e3f9608b8a43301e8b5d9592fea25166ae8488b34",
)
EXPECTED_LAST_PUBLIC = (
    "55",
    "55",
    "78713227542fabe640703d34bde9ce7babb50fb2481a9c729e72f1d0e6af7ed9",
    "165d79ccddf8c4a9f42fc38a7acd34c64e86f398686ad9281776d49cad026667",
    "39",
    "0",
    "1",
    "440f64f2926670ba4ceb556abad804e0b67892561c756f5e361a86cc1714ca1c",
)
EXPECTED_FIRST_OPENING = (
    "0",
    "0",
    "0",
    "0",
    "0",
    "-1",
    "-1",
    "9dec6b9f118e950898d48bc91853af17bf8fcba13dbfd58c5e15042746ed8f25",
    "13424a6b56a52f480d41f30a71c22800fdbceb8dfb61fc81f6f5a478b892978c",
    "75c4124e7b4e22b53b59f9208d359b0cc16157ae1e4beba52159c5a6b801dd2b",
    "0",
    "1",
    "e3e75ac792ebf0cd4e11376d75235acce0b2d784347bcb1da89b77b462d86d5f",
)
EXPECTED_LAST_OPENING = (
    "90",
    "55",
    "55",
    "85",
    "2",
    "8",
    "3",
    "78713227542fabe640703d34bde9ce7babb50fb2481a9c729e72f1d0e6af7ed9",
    "165d79ccddf8c4a9f42fc38a7acd34c64e86f398686ad9281776d49cad026667",
    "a9d9e69095513a2340da3f87682473e85fd3c79bc70f4520aaf8c13bec392953",
    "141210",
    "0",
    "f482cea927da248e383c22a83d03f12453aa57f0909f4b606b65bb9d3b3658bc",
)


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


def row_tuple(row: dict[str, str], columns: list[str]) -> tuple[str, ...]:
    return tuple(str(row[column]) for column in columns)


def validate_long_k23cop() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23cop_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23cop seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23cop cert mismatch")
    for filename, key in {
        "public_transcript.csv": "public_csv",
        "opening_rows.csv": "opening_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23cop {filename} mismatch")
    for key, expected_array in {
        "public_numeric_table": expected["public_numeric_table"],
        "opening_numeric_table": expected["opening_numeric_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23cop table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23cop matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23cop.report@1":
        raise AssertionError("long_k23cop report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23cop report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23cop all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23cop checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23cop report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23cop report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("public_transcript.csv", PUBLIC_COLUMNS, 56),
        ("opening_rows.csv", OPENING_COLUMNS, 91),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23cop {filename} shape mismatch")

    assert_locked_hash(
        "public transcript rows",
        hashlib.sha256(digest_text(PUBLIC_COLUMNS, csv_rows["public_transcript.csv"]).encode("ascii")).hexdigest(),
        PUBLIC_TEXT_HASH,
    )
    assert_locked_hash(
        "opening rows",
        hashlib.sha256(digest_text(OPENING_COLUMNS, csv_rows["opening_rows.csv"]).encode("ascii")).hexdigest(),
        OPENING_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["public_numeric_table", "opening_numeric_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23rew_certified_flag": 1,
        "public_transcript_count": 56,
        "opening_row_count": 91,
        "public_digest_unique_count": 56,
        "opening_digest_unique_count": 91,
        "source_fingerprint_unique_count": 56,
        "target_fingerprint_unique_count": 56,
        "residual_class_count": 56,
        "clean_public_transcript_count": 1,
        "defective_public_transcript_count": 55,
        "clean_opening_count": 10,
        "defective_opening_count": 81,
        "transcript_opening_mismatch_count": 0,
        "matrix_hash_mismatch_count": 0,
        "product_residual_mismatch_count": 0,
        "public_matrix_entry_column_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23cop observable {name} mismatch")

    public_rows = csv_rows["public_transcript.csv"]
    opening_rows = csv_rows["opening_rows.csv"]
    if row_tuple(public_rows[0], PUBLIC_COLUMNS) != EXPECTED_FIRST_PUBLIC:
        raise AssertionError("long_k23cop first public transcript mismatch")
    if row_tuple(public_rows[-1], PUBLIC_COLUMNS) != EXPECTED_LAST_PUBLIC:
        raise AssertionError("long_k23cop last public transcript mismatch")
    if row_tuple(opening_rows[0], OPENING_COLUMNS) != EXPECTED_FIRST_OPENING:
        raise AssertionError("long_k23cop first opening mismatch")
    if row_tuple(opening_rows[-1], OPENING_COLUMNS) != EXPECTED_LAST_OPENING:
        raise AssertionError("long_k23cop last opening mismatch")

    public_by_class = {row["class_id"]: row for row in public_rows}
    for row in opening_rows:
        transcript = public_by_class[row["class_id"]]
        if row["transcript_id"] != transcript["transcript_id"]:
            raise AssertionError("long_k23cop transcript id mismatch")
        if row["source_matrix_sha256"] != transcript["source_fingerprint"]:
            raise AssertionError("long_k23cop source hash mismatch")
        if row["target_matrix_sha256"] != transcript["target_fingerprint"]:
            raise AssertionError("long_k23cop target hash mismatch")

    public_numeric_rows = rows_from_table(np.asarray(tables["public_numeric_table"]), PUBLIC_NUMERIC_COLUMNS)
    opening_numeric_rows = rows_from_table(np.asarray(tables["opening_numeric_table"]), OPENING_NUMERIC_COLUMNS)
    if len(public_numeric_rows) != len(public_rows):
        raise AssertionError("long_k23cop public numeric row count mismatch")
    if len(opening_numeric_rows) != len(opening_rows):
        raise AssertionError("long_k23cop opening numeric row count mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23cop index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23cop.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23cop(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
