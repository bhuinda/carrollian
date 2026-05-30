from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23sound import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        MOVE_COLUMNS,
        MOVE_NUMERIC_COLUMNS,
        MOVE_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SOUNDNESS_COLUMNS,
        SOUNDNESS_TEXT_HASH,
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
    from derive_long_k23sound import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        MOVE_COLUMNS,
        MOVE_NUMERIC_COLUMNS,
        MOVE_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SOUNDNESS_COLUMNS,
        SOUNDNESS_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_MOVE_LABELS = ("honest", "tamper_1", "tamper_2", "tamper_3", "tamper_4", "tamper_5")
EXPECTED_FINAL_ROUND = (
    8,
    56,
    6,
    5,
    1_679_616,
    1,
    1_679_615,
    0,
    1_679_615,
    94_058_496,
    56,
    0,
    94_058_440,
    1,
    1_679_616,
    0,
    1_679_615,
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


def validate_long_k23sound() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23sound_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23sound seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23sound cert mismatch")
    for filename, key in {
        "move_rows.csv": "move_csv",
        "soundness_rows.csv": "soundness_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23sound {filename} mismatch")
    for key, expected_array in {
        "move_numeric_table": expected["move_numeric_table"],
        "soundness_table": expected["soundness_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23sound table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23sound matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23sound.report@1":
        raise AssertionError("long_k23sound report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23sound report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23sound all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23sound checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23sound report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23sound report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("move_rows.csv", MOVE_COLUMNS, 6),
        ("soundness_rows.csv", SOUNDNESS_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23sound {filename} shape mismatch")

    assert_locked_hash(
        "move rows",
        hashlib.sha256(digest_text(MOVE_COLUMNS, csv_rows["move_rows.csv"]).encode("ascii")).hexdigest(),
        MOVE_TEXT_HASH,
    )
    assert_locked_hash(
        "soundness rows",
        hashlib.sha256(digest_text(SOUNDNESS_COLUMNS, csv_rows["soundness_rows.csv"]).encode("ascii")).hexdigest(),
        SOUNDNESS_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["move_numeric_table", "soundness_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    if tuple(row["move_label"] for row in csv_rows["move_rows.csv"]) != EXPECTED_MOVE_LABELS:
        raise AssertionError("long_k23sound move labels mismatch")
    if any(int(row["bad_accept_count"]) != 0 for row in csv_rows["move_rows.csv"]):
        raise AssertionError("long_k23sound bad accept count mismatch")
    if int_tuple(csv_rows["soundness_rows.csv"][-1], SOUNDNESS_COLUMNS) != EXPECTED_FINAL_ROUND:
        raise AssertionError("long_k23sound final round mismatch")
    for row in csv_rows["soundness_rows.csv"]:
        depth = int(row["round_depth"])
        denominator = int(row["acceptance_denominator"])
        if denominator != 6**depth:
            raise AssertionError("long_k23sound acceptance denominator mismatch")
        if int(row["false_accept_strategy_words"]) != 0:
            raise AssertionError("long_k23sound false accept mismatch")
        if int(row["tamper_error_numerator"]) != 0:
            raise AssertionError("long_k23sound tamper error numerator mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 4,
        "certified_input_count": 4,
        "move_family_count": 6,
        "honest_move_family_count": 1,
        "tamper_move_family_count": 5,
        "round_depth_count": 8,
        "max_round_depth": 8,
        "transcript_count": 56,
        "one_round_game_row_count": 336,
        "bad_accept_count": 0,
        "bad_reject_count": 0,
        "tamper_false_accept_count": 0,
        "final_tamper_words_per_transcript": 1_679_615,
        "final_tamper_reject_strategy_words": 94_058_440,
        "final_honest_accept_strategy_words": 56,
        "final_acceptance_numerator": 1,
        "final_acceptance_denominator": 1_679_616,
        "all_depth_false_accept_strategy_words": 0,
        "all_depth_tamper_reject_strategy_words": 112_869_680,
        "bounded_soundness_error_numerator": 0,
        "bounded_soundness_error_denominator": 112_869_680,
        "uniform_counting_law_flag": 1,
        "external_randomness_claim_flag": 0,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "unbounded_adversary_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23sound observable {name} mismatch")

    for key, columns in {
        "move_numeric_table": MOVE_NUMERIC_COLUMNS,
        "soundness_table": SOUNDNESS_COLUMNS,
    }.items():
        table_rows = rows_from_table(np.asarray(tables[key]), columns)
        if not table_rows:
            raise AssertionError(f"long_k23sound {key} empty")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23sound index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23sound.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23sound(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
