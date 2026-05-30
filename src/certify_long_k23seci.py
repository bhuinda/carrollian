from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23seci import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SECURITY_COLUMNS,
        SECURITY_TEXT_HASH,
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
    from derive_long_k23seci import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SECURITY_COLUMNS,
        SECURITY_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_SECURITY = (0, 0, 0, 1, 0, 0, 1)
EXPECTED_LAST_SECURITY = (5, 5, 0, 0, 1, 0, 1)


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


def validate_long_k23seci() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23seci_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23seci seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23seci cert mismatch")
    for filename, key in {
        "security_rows.csv": "security_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23seci {filename} mismatch")
    for key, expected_array in {
        "security_table": expected["security_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23seci table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23seci matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23seci.report@1":
        raise AssertionError("long_k23seci report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23seci report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23seci all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23seci checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23seci report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23seci report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("security_rows.csv", SECURITY_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23seci {filename} shape mismatch")

    assert_locked_hash(
        "security rows",
        hashlib.sha256(digest_text(SECURITY_COLUMNS, csv_rows["security_rows.csv"]).encode("ascii")).hexdigest(),
        SECURITY_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["security_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    security_rows = csv_rows["security_rows.csv"]
    if int_tuple(security_rows[0], SECURITY_COLUMNS) != EXPECTED_FIRST_SECURITY:
        raise AssertionError("long_k23seci first security row mismatch")
    if int_tuple(security_rows[-1], SECURITY_COLUMNS) != EXPECTED_LAST_SECURITY:
        raise AssertionError("long_k23seci last security row mismatch")
    if sum(int(row["blocking_flag"]) for row in security_rows) != 3:
        raise AssertionError("long_k23seci blocking row mismatch")
    if any(int(row["claim_flag"]) != 0 for row in security_rows):
        raise AssertionError("long_k23seci overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 3,
        "certified_input_count": 3,
        "security_row_count": 6,
        "satisfied_security_count": 3,
        "blocking_security_count": 3,
        "claim_security_count": 0,
        "bounded_soundness_error_numerator": 0,
        "bounded_soundness_error_denominator": 112_869_680,
        "final_acceptance_numerator": 1,
        "final_acceptance_denominator": 1_679_616,
        "bad_accept_count": 0,
        "all_depth_false_accept_strategy_words": 0,
        "all_depth_tamper_reject_strategy_words": 112_869_680,
        "valid_decode_count": 56,
        "invalid_reject_count": 200,
        "real_epoch_count": 1,
        "materialized_version_count": 2,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "unbounded_adversary_claim_flag": 0,
        "external_randomness_claim_flag": 0,
        "finite_bounded_integrity_flag": 1,
        "security_integrity_gate_flag": 1,
        "public_security_claim_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23seci observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23seci index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23seci manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23seci manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23seci.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23seci(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
