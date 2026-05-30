from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23hprob import (
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROBLEM_COLUMNS,
        PROBLEM_TEXT_HASH,
        REDUCTION_COLUMNS,
        REDUCTION_TEXT_HASH,
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
    from derive_long_k23hprob import (
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROBLEM_COLUMNS,
        PROBLEM_TEXT_HASH,
        REDUCTION_COLUMNS,
        REDUCTION_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_PROBLEM = (0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0)
EXPECTED_LAST_PROBLEM = (3, 3, 3, 0, 3, 3, 1, 0, 1, 0, 0)
EXPECTED_FIRST_REDUCTION = (0, 0, 0, 0, 0, 0, 1, 0)
EXPECTED_LAST_REDUCTION = (3, 2, 3, 2, 3, 0, 1, 0)
EXPECTED_FIRST_GATE = (0, 0, 1, 0, 0)
EXPECTED_LAST_GATE = (5, 5, 0, 1, 0)


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


def validate_long_k23hprob() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23hprob_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23hprob seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23hprob cert mismatch")
    for filename, key in {
        "problem_rows.csv": "problem_csv",
        "reduction_rows.csv": "reduction_csv",
        "gate_rows.csv": "gate_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23hprob {filename} mismatch")
    for key, expected_array in {
        "problem_table": expected["problem_table"],
        "reduction_table": expected["reduction_table"],
        "gate_table": expected["gate_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23hprob table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23hprob matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23hprob.report@1":
        raise AssertionError("long_k23hprob report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23hprob report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23hprob all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23hprob checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23hprob report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23hprob report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("problem_rows.csv", PROBLEM_COLUMNS, 4),
        ("reduction_rows.csv", REDUCTION_COLUMNS, 4),
        ("gate_rows.csv", GATE_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23hprob {filename} shape mismatch")

    assert_locked_hash(
        "problem rows",
        hashlib.sha256(digest_text(PROBLEM_COLUMNS, csv_rows["problem_rows.csv"]).encode("ascii")).hexdigest(),
        PROBLEM_TEXT_HASH,
    )
    assert_locked_hash(
        "reduction rows",
        hashlib.sha256(digest_text(REDUCTION_COLUMNS, csv_rows["reduction_rows.csv"]).encode("ascii")).hexdigest(),
        REDUCTION_TEXT_HASH,
    )
    assert_locked_hash(
        "gate rows",
        hashlib.sha256(digest_text(GATE_COLUMNS, csv_rows["gate_rows.csv"]).encode("ascii")).hexdigest(),
        GATE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["problem_table", "reduction_table", "gate_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    problem_rows = csv_rows["problem_rows.csv"]
    if int_tuple(problem_rows[0], PROBLEM_COLUMNS) != EXPECTED_FIRST_PROBLEM:
        raise AssertionError("long_k23hprob first problem row mismatch")
    if int_tuple(problem_rows[-1], PROBLEM_COLUMNS) != EXPECTED_LAST_PROBLEM:
        raise AssertionError("long_k23hprob last problem row mismatch")
    if sum(int(row["trivial_under_public_table_flag"]) for row in problem_rows) != 2:
        raise AssertionError("long_k23hprob trivial target count mismatch")
    if any(int(row["hardness_claim_flag"]) != 0 for row in problem_rows):
        raise AssertionError("long_k23hprob hardness overclaim")

    reduction_rows = csv_rows["reduction_rows.csv"]
    if int_tuple(reduction_rows[0], REDUCTION_COLUMNS) != EXPECTED_FIRST_REDUCTION:
        raise AssertionError("long_k23hprob first reduction row mismatch")
    if int_tuple(reduction_rows[-1], REDUCTION_COLUMNS) != EXPECTED_LAST_REDUCTION:
        raise AssertionError("long_k23hprob last reduction row mismatch")
    if sum(int(row["blocking_flag"]) for row in reduction_rows) != 4:
        raise AssertionError("long_k23hprob blocking reduction count mismatch")
    if any(int(row["proof_claim_flag"]) != 0 for row in reduction_rows):
        raise AssertionError("long_k23hprob proof overclaim")

    gate_rows = csv_rows["gate_rows.csv"]
    if int_tuple(gate_rows[0], GATE_COLUMNS) != EXPECTED_FIRST_GATE:
        raise AssertionError("long_k23hprob first gate row mismatch")
    if int_tuple(gate_rows[-1], GATE_COLUMNS) != EXPECTED_LAST_GATE:
        raise AssertionError("long_k23hprob last gate row mismatch")
    if any(int(row["claim_flag"]) != 0 for row in gate_rows):
        raise AssertionError("long_k23hprob gate overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 4,
        "certified_input_count": 4,
        "problem_row_count": 4,
        "finite_evidence_problem_count": 4,
        "public_table_trivial_problem_count": 2,
        "nontrivial_problem_candidate_count": 2,
        "reduction_target_required_count": 2,
        "reduction_target_present_count": 0,
        "hardness_claim_count": 0,
        "reduction_row_count": 4,
        "materialized_reduction_count": 0,
        "blocking_reduction_count": 4,
        "proof_claim_count": 0,
        "gate_row_count": 6,
        "satisfied_gate_count": 3,
        "blocking_gate_count": 3,
        "claim_gate_count": 0,
        "bounded_soundness_error_numerator": 0,
        "bounded_soundness_error_denominator": 112_869_680,
        "valid_decode_count": 56,
        "invalid_reject_count": 200,
        "transcript_index_bytes": 56,
        "objective_byte_improvement_flag": 1,
        "hardness_problem_defined_flag": 1,
        "deploy_ready_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23hprob observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23hprob index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23hprob manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23hprob manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23hprob.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23hprob(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
