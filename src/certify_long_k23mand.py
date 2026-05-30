from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23mand import (
        DERIVE_SCRIPT,
        MANDATE_COLUMNS,
        MANDATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROFILE_COLUMNS,
        PROFILE_TEXT_HASH,
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
    from derive_long_k23mand import (
        DERIVE_SCRIPT,
        MANDATE_COLUMNS,
        MANDATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROFILE_COLUMNS,
        PROFILE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_PROFILE_ROWS = (
    (0, 0, 0, 45, 1, 2),
    (1, 1, 1, 10, 2, 2),
    (2, 5, 5, 1, 10, 10),
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


def int_tuple(row: dict[str, str], columns: list[str]) -> tuple[int, ...]:
    return tuple(int(row[column]) for column in columns)


def validate_long_k23mand() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23mand_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23mand seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23mand cert mismatch")
    for filename, key in {
        "mandate_rows.csv": "mandate_csv",
        "profile_rows.csv": "profile_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23mand {filename} mismatch")
    for key, expected_array in {
        "mandate_table": expected["mandate_table"],
        "profile_table": expected["profile_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23mand table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23mand matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23mand.report@1":
        raise AssertionError("long_k23mand report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23mand report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23mand all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23mand checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23mand report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23mand report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("mandate_rows.csv", MANDATE_COLUMNS, 56),
        ("profile_rows.csv", PROFILE_COLUMNS, 3),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23mand {filename} shape mismatch")

    assert_locked_hash(
        "mandate rows",
        hashlib.sha256(digest_text(MANDATE_COLUMNS, csv_rows["mandate_rows.csv"]).encode("ascii")).hexdigest(),
        MANDATE_TEXT_HASH,
    )
    assert_locked_hash(
        "profile rows",
        hashlib.sha256(digest_text(PROFILE_COLUMNS, csv_rows["profile_rows.csv"]).encode("ascii")).hexdigest(),
        PROFILE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["mandate_table", "profile_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    mandate_rows = csv_rows["mandate_rows.csv"]
    if any(int(row["selector_match_flag"]) != 1 for row in mandate_rows):
        raise AssertionError("long_k23mand selector mismatch")
    if any(int(row["opening_match_flag"]) != 1 for row in mandate_rows):
        raise AssertionError("long_k23mand opening mismatch")
    if any(int(row["digest_bound_flag"]) != 1 for row in mandate_rows):
        raise AssertionError("long_k23mand digest binding mismatch")
    if any(int(row["external_randomness_used_flag"]) != 0 for row in mandate_rows):
        raise AssertionError("long_k23mand external randomness used")

    profile_rows = tuple(int_tuple(row, PROFILE_COLUMNS) for row in csv_rows["profile_rows.csv"])
    if profile_rows != EXPECTED_PROFILE_ROWS:
        raise AssertionError("long_k23mand selector profile mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 2,
        "certified_input_count": 2,
        "public_transcript_count": 56,
        "opening_row_count": 91,
        "challenge_count": 56,
        "mandate_row_count": 56,
        "selector_match_count": 56,
        "opening_match_count": 56,
        "digest_bound_count": 56,
        "selector_zero_count": 45,
        "selector_nonzero_count": 11,
        "selector_profile_count": 3,
        "selected_opening_unique_count": 56,
        "selected_word_unique_count": 56,
        "external_randomness_used_count": 0,
        "external_randomness_claim_flag": 0,
        "challenge_randomness_source_certified_flag": 0,
        "deterministic_mandate_certified_flag": 1,
        "proof_of_mandate_flag": 1,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23mand observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23mand index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23mand.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23mand(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
