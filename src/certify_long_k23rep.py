from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23rep import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROUND_COLUMNS,
        ROUND_TEXT_HASH,
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
    from derive_long_k23rep import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROUND_COLUMNS,
        ROUND_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_ROUND = (1, 56, 6, 1, 5, 6, 1, 5, 336, 56, 280, 336, 56, 1, 6)
EXPECTED_LAST_ROUND = (
    8,
    56,
    6,
    1,
    5,
    1_679_616,
    1,
    1_679_615,
    94_058_496,
    56,
    94_058_440,
    94_058_496,
    56,
    1,
    1_679_616,
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


def validate_long_k23rep() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23rep_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23rep seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23rep cert mismatch")
    for filename, key in {
        "round_rows.csv": "round_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23rep {filename} mismatch")
    for key, expected_array in {
        "round_table": expected["round_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23rep table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23rep matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23rep.report@1":
        raise AssertionError("long_k23rep report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23rep report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23rep all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23rep checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23rep report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23rep report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("round_rows.csv", ROUND_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23rep {filename} shape mismatch")

    assert_locked_hash(
        "round rows",
        hashlib.sha256(digest_text(ROUND_COLUMNS, csv_rows["round_rows.csv"]).encode("ascii")).hexdigest(),
        ROUND_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["round_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23game_certified_flag": 1,
        "round_depth_count": 8,
        "max_round_depth": 8,
        "transcript_count": 56,
        "move_family_count": 6,
        "honest_move_family_count": 1,
        "tamper_move_family_count": 5,
        "one_round_game_row_count": 336,
        "final_depth_total_strategy_words": 94_058_496,
        "final_depth_accepted_strategy_words": 56,
        "final_depth_rejected_strategy_words": 94_058_440,
        "all_depth_total_strategy_words": 112_870_128,
        "all_depth_accepted_strategy_words": 448,
        "all_depth_rejected_strategy_words": 112_869_680,
        "probability_soundness_claim_flag": 0,
        "hardness_claim_flag": 0,
        "strategy_exhaustiveness_beyond_bounded_moves_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23rep observable {name} mismatch")

    round_rows = csv_rows["round_rows.csv"]
    if int_tuple(round_rows[0], ROUND_COLUMNS) != EXPECTED_FIRST_ROUND:
        raise AssertionError("long_k23rep first round mismatch")
    if int_tuple(round_rows[-1], ROUND_COLUMNS) != EXPECTED_LAST_ROUND:
        raise AssertionError("long_k23rep last round mismatch")
    for row in round_rows:
        depth = int(row["round_depth"])
        if int(row["strategy_words_per_transcript"]) != 6**depth:
            raise AssertionError("long_k23rep strategy power mismatch")
        if int(row["accepted_words_per_transcript"]) != 1:
            raise AssertionError("long_k23rep accepted word count mismatch")
        if int(row["rejected_words_per_transcript"]) != 6**depth - 1:
            raise AssertionError("long_k23rep rejected word count mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23rep index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23rep.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23rep(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
