from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23game import (
        DERIVE_SCRIPT,
        GAME_COLUMNS,
        GAME_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PAYOFF_COLUMNS,
        PAYOFF_NUMERIC_COLUMNS,
        PAYOFF_TEXT_HASH,
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
    from derive_long_k23game import (
        DERIVE_SCRIPT,
        GAME_COLUMNS,
        GAME_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PAYOFF_COLUMNS,
        PAYOFF_NUMERIC_COLUMNS,
        PAYOFF_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_GAME = (0, 0, 0, 0, 5, 50, 0, 0, 1, 1, 1, 1, 0, 1, 0)
EXPECTED_LAST_GAME = (335, 55, 55, 55, 90, 85, 5, 0, 0, 0, 0, 1, 1, 0, 1)
EXPECTED_PAYOFF_ROWS = (
    ("0", "honest_accept", "56", "1", "1", "1", "0"),
    ("1", "tamper_reject", "280", "0", "1", "0", "1"),
    ("2", "bad_accept", "0", "0", "0", "1", "1"),
    ("3", "bad_reject", "0", "0", "0", "0", "0"),
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


def row_tuple(row: dict[str, str], columns: list[str]) -> tuple[str, ...]:
    return tuple(str(row[column]) for column in columns)


def validate_long_k23game() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23game_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23game seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23game cert mismatch")
    for filename, key in {
        "game_rows.csv": "game_csv",
        "payoff_rows.csv": "payoff_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23game {filename} mismatch")
    for key, expected_array in {
        "game_table": expected["game_table"],
        "payoff_numeric_table": expected["payoff_numeric_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23game table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23game matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23game.report@1":
        raise AssertionError("long_k23game report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23game report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23game all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23game checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23game report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23game report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("game_rows.csv", GAME_COLUMNS, 336),
        ("payoff_rows.csv", PAYOFF_COLUMNS, 4),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23game {filename} shape mismatch")

    assert_locked_hash(
        "game rows",
        hashlib.sha256(digest_text(GAME_COLUMNS, csv_rows["game_rows.csv"]).encode("ascii")).hexdigest(),
        GAME_TEXT_HASH,
    )
    assert_locked_hash(
        "payoff rows",
        hashlib.sha256(digest_text(PAYOFF_COLUMNS, csv_rows["payoff_rows.csv"]).encode("ascii")).hexdigest(),
        PAYOFF_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["game_table", "payoff_numeric_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23chal_certified_flag": 1,
        "challenge_count": 56,
        "control_count": 336,
        "game_row_count": 336,
        "honest_move_count": 56,
        "tamper_move_count": 280,
        "accepted_truth_count": 56,
        "rejected_tamper_count": 280,
        "unexpected_accept_count": 0,
        "unexpected_reject_count": 0,
        "verifier_payoff_total": 336,
        "prover_payoff_total": 56,
        "payoff_label_count": 4,
        "transcript_count": 56,
        "opening_count": 56,
        "word_count": 56,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23game observable {name} mismatch")

    game_rows = csv_rows["game_rows.csv"]
    payoff_rows = csv_rows["payoff_rows.csv"]
    if int_tuple(game_rows[0], GAME_COLUMNS) != EXPECTED_FIRST_GAME:
        raise AssertionError("long_k23game first game row mismatch")
    if int_tuple(game_rows[-1], GAME_COLUMNS) != EXPECTED_LAST_GAME:
        raise AssertionError("long_k23game last game row mismatch")
    if tuple(row_tuple(row, PAYOFF_COLUMNS) for row in payoff_rows) != EXPECTED_PAYOFF_ROWS:
        raise AssertionError("long_k23game payoff table mismatch")
    if any(int(row["expected_accept_flag"]) != int(row["actual_accept_flag"]) for row in game_rows):
        raise AssertionError("long_k23game expected/actual mismatch")
    if any(int(row["verifier_payoff"]) != 1 for row in game_rows):
        raise AssertionError("long_k23game verifier payoff mismatch")

    payoff_numeric_rows = rows_from_table(
        np.asarray(tables["payoff_numeric_table"]), PAYOFF_NUMERIC_COLUMNS
    )
    if len(payoff_numeric_rows) != len(payoff_rows):
        raise AssertionError("long_k23game payoff numeric row count mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23game index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23game.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23game(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
