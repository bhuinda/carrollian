from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23epoch import (
        DERIVE_SCRIPT,
        EPOCH_COLUMNS,
        EPOCH_TEXT_HASH,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        MIGRATION_COLUMNS,
        MIGRATION_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        VERSION_COLUMNS,
        VERSION_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23epoch import (
        DERIVE_SCRIPT,
        EPOCH_COLUMNS,
        EPOCH_TEXT_HASH,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        MIGRATION_COLUMNS,
        MIGRATION_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        VERSION_COLUMNS,
        VERSION_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_EPOCH = (0, 0, 1, 0, 0, 0, 1, 2, 1, 0)
EXPECTED_FIRST_VERSION = (0, 0, 0, 4, 0, 0, 1, 56, 0, 1, 1)
EXPECTED_LAST_VERSION = (1, 0, 1, 1, 1, 1, 1, 56, 200, 1, 1)
EXPECTED_FIRST_MIGRATION = (0, 0, 1, 1, 56, 56, 0, 1, 0)
EXPECTED_FIRST_GATE = (0, 0, 1, 0, 0)
EXPECTED_LAST_GATE = (4, 4, 0, 1, 0)


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


def validate_long_k23epoch() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23epoch_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23epoch seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23epoch cert mismatch")
    for filename, key in {
        "epoch_rows.csv": "epoch_csv",
        "version_rows.csv": "version_csv",
        "migration_rows.csv": "migration_csv",
        "gate_rows.csv": "gate_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23epoch {filename} mismatch")
    for key, expected_array in {
        "epoch_table": expected["epoch_table"],
        "version_table": expected["version_table"],
        "migration_table": expected["migration_table"],
        "gate_table": expected["gate_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23epoch table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23epoch matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23epoch.report@1":
        raise AssertionError("long_k23epoch report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23epoch report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23epoch all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23epoch checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23epoch report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23epoch report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("epoch_rows.csv", EPOCH_COLUMNS, 1),
        ("version_rows.csv", VERSION_COLUMNS, 2),
        ("migration_rows.csv", MIGRATION_COLUMNS, 1),
        ("gate_rows.csv", GATE_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23epoch {filename} shape mismatch")

    assert_locked_hash(
        "epoch rows",
        hashlib.sha256(digest_text(EPOCH_COLUMNS, csv_rows["epoch_rows.csv"]).encode("ascii")).hexdigest(),
        EPOCH_TEXT_HASH,
    )
    assert_locked_hash(
        "version rows",
        hashlib.sha256(digest_text(VERSION_COLUMNS, csv_rows["version_rows.csv"]).encode("ascii")).hexdigest(),
        VERSION_TEXT_HASH,
    )
    assert_locked_hash(
        "migration rows",
        hashlib.sha256(digest_text(MIGRATION_COLUMNS, csv_rows["migration_rows.csv"]).encode("ascii")).hexdigest(),
        MIGRATION_TEXT_HASH,
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
        for key in ["epoch_table", "version_table", "migration_table", "gate_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    if int_tuple(csv_rows["epoch_rows.csv"][0], EPOCH_COLUMNS) != EXPECTED_FIRST_EPOCH:
        raise AssertionError("long_k23epoch epoch row mismatch")
    version_rows = csv_rows["version_rows.csv"]
    if int_tuple(version_rows[0], VERSION_COLUMNS) != EXPECTED_FIRST_VERSION:
        raise AssertionError("long_k23epoch first version row mismatch")
    if int_tuple(version_rows[-1], VERSION_COLUMNS) != EXPECTED_LAST_VERSION:
        raise AssertionError("long_k23epoch last version row mismatch")
    if int_tuple(csv_rows["migration_rows.csv"][0], MIGRATION_COLUMNS) != EXPECTED_FIRST_MIGRATION:
        raise AssertionError("long_k23epoch migration row mismatch")
    gate_rows = csv_rows["gate_rows.csv"]
    if int_tuple(gate_rows[0], GATE_COLUMNS) != EXPECTED_FIRST_GATE:
        raise AssertionError("long_k23epoch first gate row mismatch")
    if int_tuple(gate_rows[-1], GATE_COLUMNS) != EXPECTED_LAST_GATE:
        raise AssertionError("long_k23epoch last gate row mismatch")
    if any(int(row["claim_flag"]) != 0 for row in gate_rows):
        raise AssertionError("long_k23epoch overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 2,
        "certified_input_count": 2,
        "epoch_row_count": 1,
        "real_epoch_count": 1,
        "simulated_epoch_count": 0,
        "third_party_epoch_count": 0,
        "future_epoch_count": 0,
        "manifest_present_count": 1,
        "version_row_count": 2,
        "materialized_version_count": 2,
        "compact_version_byte_surface": 4,
        "index_version_byte_surface": 1,
        "byte_surface_ratio_num": 1,
        "byte_surface_ratio_den": 4,
        "valid_decode_count": 56,
        "invalid_reject_count": 200,
        "canonical_pair_row_count": 56,
        "decode_equiv_count": 56,
        "same_mint_normal_form_count": 56,
        "canonicality_failure_count": 0,
        "migration_row_count": 1,
        "migration_pass_count": 1,
        "external_epoch_claim_count": 0,
        "external_manifest_ready_flag": 1,
        "real_external_artifact_count": 0,
        "gate_row_count": 5,
        "satisfied_gate_count": 3,
        "blocking_gate_count": 2,
        "claim_gate_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23epoch observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23epoch index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23epoch manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23epoch manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23epoch.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23epoch(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
