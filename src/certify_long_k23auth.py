from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23auth import (
        AUTHORITY_COLUMNS,
        AUTHORITY_TEXT_HASH,
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SCOPE_COLUMNS,
        SCOPE_TEXT_HASH,
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
    from derive_long_k23auth import (
        AUTHORITY_COLUMNS,
        AUTHORITY_TEXT_HASH,
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SCOPE_COLUMNS,
        SCOPE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_AUTHORITY = (0, 0, 0, 5, 1, 1, 1, 1, 1, 0)
EXPECTED_LAST_AUTHORITY = (55, 55, 55, 90, 1, 1, 1, 1, 1, 0)
EXPECTED_SCOPE_ROWS = (
    (0, 0, 1, 1, 1, 0),
    (1, 1, 1, 1, 1, 0),
    (2, 2, 1, 1, 1, 0),
    (3, 3, 0, 0, 0, 1),
    (4, 4, 0, 0, 0, 1),
    (5, 5, 0, 0, 0, 1),
    (6, 6, 0, 0, 0, 1),
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


def validate_long_k23auth() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23auth_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23auth seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23auth cert mismatch")
    for filename, key in {
        "authority_rows.csv": "authority_csv",
        "scope_rows.csv": "scope_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23auth {filename} mismatch")
    for key, expected_array in {
        "authority_table": expected["authority_table"],
        "scope_table": expected["scope_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23auth table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23auth matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23auth.report@1":
        raise AssertionError("long_k23auth report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23auth report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23auth all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23auth checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23auth report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23auth report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("authority_rows.csv", AUTHORITY_COLUMNS, 56),
        ("scope_rows.csv", SCOPE_COLUMNS, 7),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23auth {filename} shape mismatch")

    assert_locked_hash(
        "authority rows",
        hashlib.sha256(digest_text(AUTHORITY_COLUMNS, csv_rows["authority_rows.csv"]).encode("ascii")).hexdigest(),
        AUTHORITY_TEXT_HASH,
    )
    assert_locked_hash(
        "scope rows",
        hashlib.sha256(digest_text(SCOPE_COLUMNS, csv_rows["scope_rows.csv"]).encode("ascii")).hexdigest(),
        SCOPE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["authority_table", "scope_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    authority_rows = csv_rows["authority_rows.csv"]
    if int_tuple(authority_rows[0], AUTHORITY_COLUMNS) != EXPECTED_FIRST_AUTHORITY:
        raise AssertionError("long_k23auth first authority row mismatch")
    if int_tuple(authority_rows[-1], AUTHORITY_COLUMNS) != EXPECTED_LAST_AUTHORITY:
        raise AssertionError("long_k23auth last authority row mismatch")
    if any(int(row["accepted_authority_flag"]) != 1 for row in authority_rows):
        raise AssertionError("long_k23auth authority accept mismatch")
    if any(int(row["external_randomness_required_flag"]) != 0 for row in authority_rows):
        raise AssertionError("long_k23auth external randomness requirement mismatch")
    scope_rows = tuple(int_tuple(row, SCOPE_COLUMNS) for row in csv_rows["scope_rows.csv"])
    if scope_rows != EXPECTED_SCOPE_ROWS:
        raise AssertionError("long_k23auth scope rows mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 2,
        "certified_input_count": 2,
        "authority_row_count": 56,
        "accepted_authority_count": 56,
        "selector_binding_count": 56,
        "opening_binding_count": 56,
        "digest_binding_count": 56,
        "soundness_guard_count": 56,
        "external_randomness_required_count": 0,
        "scope_row_count": 7,
        "certified_scope_count": 3,
        "open_scope_count": 4,
        "all_depth_false_accept_strategy_words": 0,
        "all_depth_tamper_reject_strategy_words": 112_869_680,
        "bounded_soundness_error_numerator": 0,
        "proof_of_mandate_flag": 1,
        "finite_authority_closure_flag": 1,
        "randomness_claim_flag": 0,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "unbounded_adversary_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23auth observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23auth index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23auth.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23auth(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
