from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23roll import (
        CHAIN_COLUMNS,
        CHAIN_NUMERIC_COLUMNS,
        CHAIN_TEXT_HASH,
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_NUMERIC_COLUMNS,
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
    from derive_long_k23roll import (
        CHAIN_COLUMNS,
        CHAIN_NUMERIC_COLUMNS,
        CHAIN_TEXT_HASH,
        DERIVE_SCRIPT,
        LIMIT_COLUMNS,
        LIMIT_NUMERIC_COLUMNS,
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


EXPECTED_CHAIN_IDS = (
    "long_k23fam",
    "long_k23poly",
    "long_k23rew",
    "long_k23cop",
    "long_k23chal",
    "long_k23game",
)
EXPECTED_LIMIT_NAMES = (
    "hash_collision_resistance",
    "repository_witness_secrecy",
    "zero_knowledge",
    "probabilistic_repeated_soundness",
    "deeper_word_depth",
    "bundle_wide_integration",
    "final_broad_goal_closure",
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


def validate_long_k23roll() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23roll_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23roll seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23roll cert mismatch")
    for filename, key in {
        "chain_rows.csv": "chain_csv",
        "limit_rows.csv": "limit_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23roll {filename} mismatch")
    for key, expected_array in {
        "chain_numeric_table": expected["chain_numeric_table"],
        "limit_numeric_table": expected["limit_numeric_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23roll table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23roll matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23roll.report@1":
        raise AssertionError("long_k23roll report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23roll report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23roll all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23roll checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23roll report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23roll report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("chain_rows.csv", CHAIN_COLUMNS, 6),
        ("limit_rows.csv", LIMIT_COLUMNS, 7),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23roll {filename} shape mismatch")

    assert_locked_hash(
        "chain rows",
        hashlib.sha256(digest_text(CHAIN_COLUMNS, csv_rows["chain_rows.csv"]).encode("ascii")).hexdigest(),
        CHAIN_TEXT_HASH,
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
        for key in ["chain_numeric_table", "limit_numeric_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 6,
        "certified_input_count": 6,
        "chain_stage_count": 6,
        "merge_layer_count": 5,
        "minimal_family_obstructed_flag": 1,
        "word_carrier_certified_flag": 1,
        "rewrite_obstructed_flag": 1,
        "commit_open_certified_flag": 1,
        "challenge_certified_flag": 1,
        "game_payoff_certified_flag": 1,
        "certified_merge_point_flag": 1,
        "open_limit_count": 7,
        "hardness_claim_flag": 0,
        "secrecy_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "repeated_soundness_claim_flag": 0,
        "bundle_integration_claim_flag": 0,
        "final_goal_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23roll observable {name} mismatch")

    chain_rows = csv_rows["chain_rows.csv"]
    limit_rows = csv_rows["limit_rows.csv"]
    if tuple(row["proof_id"] for row in chain_rows) != EXPECTED_CHAIN_IDS:
        raise AssertionError("long_k23roll chain proof order mismatch")
    if any(int(row["certified_flag"]) != 1 for row in chain_rows):
        raise AssertionError("long_k23roll uncertified chain row")
    if tuple(row["limit_name"] for row in limit_rows) != EXPECTED_LIMIT_NAMES:
        raise AssertionError("long_k23roll limit order mismatch")
    if any(int(row["claim_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23roll unexpected open-limit claim")
    if any(int(row["certified_negative_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23roll unexpected negative limit certification")

    chain_numeric_rows = rows_from_table(np.asarray(tables["chain_numeric_table"]), CHAIN_NUMERIC_COLUMNS)
    limit_numeric_rows = rows_from_table(np.asarray(tables["limit_numeric_table"]), LIMIT_NUMERIC_COLUMNS)
    if len(chain_numeric_rows) != len(chain_rows):
        raise AssertionError("long_k23roll chain numeric row count mismatch")
    if len(limit_numeric_rows) != len(limit_rows):
        raise AssertionError("long_k23roll limit numeric row count mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23roll index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23roll.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23roll(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
