from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23sdet import (
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SOURCE_COLUMNS,
        SOURCE_TEXT_HASH,
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
    from derive_long_k23sdet import (
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SOURCE_COLUMNS,
        SOURCE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_SOURCE = (0, 0, 1, 1, 0, 0, 0, 0, 0, 1)
EXPECTED_LAST_SOURCE = (4, 4, 1, 1, 1, 1, 1, 0, 0, 1)
EXPECTED_FIRST_LIMIT = (0, 0, 0, 0, 0, 1)
EXPECTED_LAST_LIMIT = (7, 7, 0, 0, 0, 1)


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


def validate_long_k23sdet() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23sdet_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23sdet seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23sdet cert mismatch")
    for filename, key in {
        "source_rows.csv": "source_csv",
        "limit_rows.csv": "limit_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23sdet {filename} mismatch")
    for key, expected_array in {
        "source_table": expected["source_table"],
        "limit_table": expected["limit_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23sdet table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23sdet matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23sdet.report@1":
        raise AssertionError("long_k23sdet report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23sdet report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23sdet all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23sdet checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23sdet report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23sdet report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("source_rows.csv", SOURCE_COLUMNS, 5),
        ("limit_rows.csv", LIMIT_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23sdet {filename} shape mismatch")

    assert_locked_hash(
        "source rows",
        hashlib.sha256(digest_text(SOURCE_COLUMNS, csv_rows["source_rows.csv"]).encode("ascii")).hexdigest(),
        SOURCE_TEXT_HASH,
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
        for key in ["source_table", "limit_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    source_rows = csv_rows["source_rows.csv"]
    if int_tuple(source_rows[0], SOURCE_COLUMNS) != EXPECTED_FIRST_SOURCE:
        raise AssertionError("long_k23sdet first source row mismatch")
    if int_tuple(source_rows[-1], SOURCE_COLUMNS) != EXPECTED_LAST_SOURCE:
        raise AssertionError("long_k23sdet last source row mismatch")
    if any(int(row["certified_flag"]) != 1 for row in source_rows):
        raise AssertionError("long_k23sdet uncertified source row")
    if any(int(row["external_randomness_claim_flag"]) != 0 for row in source_rows):
        raise AssertionError("long_k23sdet external randomness claim mismatch")
    if any(int(row["hardness_claim_flag"]) != 0 for row in source_rows):
        raise AssertionError("long_k23sdet hardness claim mismatch")

    limit_rows = csv_rows["limit_rows.csv"]
    if int_tuple(limit_rows[0], LIMIT_COLUMNS) != EXPECTED_FIRST_LIMIT:
        raise AssertionError("long_k23sdet first limit row mismatch")
    if int_tuple(limit_rows[-1], LIMIT_COLUMNS) != EXPECTED_LAST_LIMIT:
        raise AssertionError("long_k23sdet last limit row mismatch")
    if any(int(row["open_flag"]) != 1 or int(row["claim_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23sdet open limit mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 5,
        "certified_input_count": 5,
        "source_row_count": 5,
        "certified_source_row_count": 5,
        "deterministic_source_row_count": 5,
        "finite_game_source_row_count": 4,
        "bounded_soundness_source_row_count": 2,
        "authority_closure_source_row_count": 1,
        "external_randomness_claim_count": 0,
        "hardness_claim_count": 0,
        "challenge_count": 56,
        "selected_opening_unique_count": 56,
        "game_row_count": 336,
        "rejected_tamper_count": 280,
        "max_round_depth": 8,
        "all_depth_false_accept_strategy_words": 0,
        "all_depth_tamper_reject_strategy_words": 112_869_680,
        "bounded_soundness_error_numerator": 0,
        "authority_row_count": 56,
        "accepted_authority_count": 56,
        "external_randomness_required_count": 0,
        "finite_authority_closure_flag": 1,
        "limit_row_count": 8,
        "open_limit_count": 8,
        "superdeterministic_cryptologic_boundary_flag": 1,
        "randomness_independence_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "unbounded_adversary_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23sdet observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23sdet index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23sdet.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23sdet(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
