from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23mledger import (
        DERIVE_SCRIPT,
        LEDGER_COLUMNS,
        LEDGER_TEXT_HASH,
        MATRIX_SHA256,
        NONCLAIM_COLUMNS,
        NONCLAIM_TEXT_HASH,
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
    from derive_long_k23mledger import (
        DERIVE_SCRIPT,
        LEDGER_COLUMNS,
        LEDGER_TEXT_HASH,
        MATRIX_SHA256,
        NONCLAIM_COLUMNS,
        NONCLAIM_TEXT_HASH,
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


EXPECTED_FIRST_LEDGER = (0, 0, 1, 1, 0, 0, 0, 0, 0, 1)
EXPECTED_LAST_LEDGER = (11, 11, 1, 0, 1, 1, 0, 0, 0, 1)
EXPECTED_FIRST_NONCLAIM = (0, 0, 0, 1, 1, 0, 0, 0)
EXPECTED_BROAD_NONCLAIM = (5, 5, 0, 1, 1, 0, 1, 0)
EXPECTED_LAST_NONCLAIM = (7, 7, 0, 1, 1, 0, 0, 0)


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


def validate_long_k23mledger() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23mledger_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23mledger seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23mledger cert mismatch")
    for filename, key in {
        "ledger_rows.csv": "ledger_csv",
        "nonclaim_rows.csv": "nonclaim_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23mledger {filename} mismatch")
    for key, expected_array in {
        "ledger_table": expected["ledger_table"],
        "nonclaim_table": expected["nonclaim_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23mledger table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23mledger matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23mledger.report@1":
        raise AssertionError("long_k23mledger report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23mledger report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23mledger all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23mledger checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23mledger report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23mledger report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("ledger_rows.csv", LEDGER_COLUMNS, 12),
        ("nonclaim_rows.csv", NONCLAIM_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23mledger {filename} shape mismatch")

    assert_locked_hash(
        "ledger rows",
        hashlib.sha256(digest_text(LEDGER_COLUMNS, csv_rows["ledger_rows.csv"]).encode("ascii")).hexdigest(),
        LEDGER_TEXT_HASH,
    )
    assert_locked_hash(
        "nonclaim rows",
        hashlib.sha256(digest_text(NONCLAIM_COLUMNS, csv_rows["nonclaim_rows.csv"]).encode("ascii")).hexdigest(),
        NONCLAIM_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["ledger_table", "nonclaim_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    ledger_rows = csv_rows["ledger_rows.csv"]
    if int_tuple(ledger_rows[0], LEDGER_COLUMNS) != EXPECTED_FIRST_LEDGER:
        raise AssertionError("long_k23mledger first ledger row mismatch")
    if int_tuple(ledger_rows[-1], LEDGER_COLUMNS) != EXPECTED_LAST_LEDGER:
        raise AssertionError("long_k23mledger last ledger row mismatch")
    if any(int(row["certified_flag"]) != 1 for row in ledger_rows):
        raise AssertionError("long_k23mledger uncertified ledger row")
    if any(int(row["proof_of_mandate_contribution_flag"]) != 1 for row in ledger_rows):
        raise AssertionError("long_k23mledger contribution mismatch")
    if any(int(row["broad_integration_run_flag"]) != 0 for row in ledger_rows):
        raise AssertionError("long_k23mledger broad-run mismatch")

    nonclaim_rows = csv_rows["nonclaim_rows.csv"]
    if int_tuple(nonclaim_rows[0], NONCLAIM_COLUMNS) != EXPECTED_FIRST_NONCLAIM:
        raise AssertionError("long_k23mledger first nonclaim row mismatch")
    if int_tuple(nonclaim_rows[5], NONCLAIM_COLUMNS) != EXPECTED_BROAD_NONCLAIM:
        raise AssertionError("long_k23mledger broad nonclaim row mismatch")
    if int_tuple(nonclaim_rows[-1], NONCLAIM_COLUMNS) != EXPECTED_LAST_NONCLAIM:
        raise AssertionError("long_k23mledger last nonclaim row mismatch")
    if any(int(row["claim_flag"]) != 0 or int(row["open_flag"]) != 1 for row in nonclaim_rows):
        raise AssertionError("long_k23mledger nonclaim openness mismatch")
    if any(int(row["overclaim_flag"]) != 0 for row in nonclaim_rows):
        raise AssertionError("long_k23mledger overclaim mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 12,
        "certified_input_count": 12,
        "ledger_row_count": 12,
        "certified_ledger_count": 12,
        "game_support_count": 5,
        "mandate_core_count": 5,
        "frontier_support_count": 4,
        "source_decision_count": 1,
        "authority_closure_count": 1,
        "broad_integration_run_count": 0,
        "proof_mandate_contribution_count": 12,
        "nonclaim_row_count": 8,
        "open_nonclaim_count": 8,
        "preserved_nonclaim_count": 8,
        "required_nonclaim_count": 0,
        "broad_required_nonclaim_count": 1,
        "overclaim_count": 0,
        "challenge_count": 56,
        "selected_opening_unique_count": 56,
        "game_row_count": 336,
        "all_depth_false_accept_strategy_words": 0,
        "all_depth_tamper_reject_strategy_words": 112_869_680,
        "accepted_authority_count": 56,
        "finite_authority_closure_flag": 1,
        "proof_source_decision_flag": 1,
        "route_blocking_count": 0,
        "frontier_route_flag": 1,
        "frontier_ingestion_flag": 1,
        "proof_of_mandate_ledger_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23mledger observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23mledger index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23mledger.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23mledger(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
