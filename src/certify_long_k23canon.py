from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23canon import (
        CANON_COLUMNS,
        CANON_TEXT_HASH,
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
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
    from derive_long_k23canon import (
        CANON_COLUMNS,
        CANON_TEXT_HASH,
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
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


EXPECTED_FIRST_VERSION = (0, 0, 4, 56, 0, 1, 1)
EXPECTED_LAST_VERSION = (1, 1, 1, 56, 200, 1, 1)
EXPECTED_FIRST_CANON = (0, 0, 0, 0, 5, 5, 27, 27, 5, 5, 1, 1)
EXPECTED_LAST_CANON = (55, 55, 55, 55, 90, 90, 39, 39, 0, 0, 1, 1)
EXPECTED_FIRST_GATE = (0, 0, 1, 0, 0)
EXPECTED_LAST_GATE = (2, 2, 0, 1, 0)


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


def validate_long_k23canon() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23canon_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23canon seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23canon cert mismatch")
    for filename, key in {
        "version_rows.csv": "version_csv",
        "canon_rows.csv": "canon_csv",
        "gate_rows.csv": "gate_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23canon {filename} mismatch")
    for key, expected_array in {
        "version_table": expected["version_table"],
        "canon_table": expected["canon_table"],
        "gate_table": expected["gate_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23canon table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23canon matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23canon.report@1":
        raise AssertionError("long_k23canon report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23canon report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23canon all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23canon checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23canon report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23canon report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("version_rows.csv", VERSION_COLUMNS, 2),
        ("canon_rows.csv", CANON_COLUMNS, 56),
        ("gate_rows.csv", GATE_COLUMNS, 3),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23canon {filename} shape mismatch")

    assert_locked_hash(
        "version rows",
        hashlib.sha256(digest_text(VERSION_COLUMNS, csv_rows["version_rows.csv"]).encode("ascii")).hexdigest(),
        VERSION_TEXT_HASH,
    )
    assert_locked_hash(
        "canonicality rows",
        hashlib.sha256(digest_text(CANON_COLUMNS, csv_rows["canon_rows.csv"]).encode("ascii")).hexdigest(),
        CANON_TEXT_HASH,
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
        for key in ["version_table", "canon_table", "gate_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    version_rows = csv_rows["version_rows.csv"]
    if int_tuple(version_rows[0], VERSION_COLUMNS) != EXPECTED_FIRST_VERSION:
        raise AssertionError("long_k23canon first version row mismatch")
    if int_tuple(version_rows[-1], VERSION_COLUMNS) != EXPECTED_LAST_VERSION:
        raise AssertionError("long_k23canon last version row mismatch")

    canon_rows = csv_rows["canon_rows.csv"]
    if int_tuple(canon_rows[0], CANON_COLUMNS) != EXPECTED_FIRST_CANON:
        raise AssertionError("long_k23canon first canonical row mismatch")
    if int_tuple(canon_rows[-1], CANON_COLUMNS) != EXPECTED_LAST_CANON:
        raise AssertionError("long_k23canon last canonical row mismatch")
    if any(int(row["decode_equiv_flag"]) != 1 for row in canon_rows):
        raise AssertionError("long_k23canon decode equivalence mismatch")
    if any(int(row["same_mint_normal_form_flag"]) != 1 for row in canon_rows):
        raise AssertionError("long_k23canon mint normal form mismatch")

    gate_rows = csv_rows["gate_rows.csv"]
    if int_tuple(gate_rows[0], GATE_COLUMNS) != EXPECTED_FIRST_GATE:
        raise AssertionError("long_k23canon first gate row mismatch")
    if int_tuple(gate_rows[-1], GATE_COLUMNS) != EXPECTED_LAST_GATE:
        raise AssertionError("long_k23canon last gate row mismatch")
    if sum(int(row["satisfied_flag"]) for row in gate_rows) != 2:
        raise AssertionError("long_k23canon satisfied gate mismatch")
    if sum(int(row["blocking_flag"]) for row in gate_rows) != 1:
        raise AssertionError("long_k23canon blocking gate mismatch")
    if any(int(row["claim_flag"]) != 0 for row in gate_rows):
        raise AssertionError("long_k23canon claim gate overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 2,
        "certified_input_count": 2,
        "version_row_count": 2,
        "compact_version_byte_surface": 4,
        "index_version_byte_surface": 1,
        "byte_surface_ratio_num": 1,
        "byte_surface_ratio_den": 4,
        "canonical_pair_row_count": 56,
        "decode_equiv_count": 56,
        "same_mint_normal_form_count": 56,
        "canonicality_failure_count": 0,
        "valid_decode_count": 56,
        "invalid_reject_count": 200,
        "version_pair_count": 1,
        "canonical_across_versions_flag": 1,
        "real_epoch_count": 1,
        "simulated_epoch_count": 0,
        "external_epoch_claim_count": 0,
        "gate_row_count": 3,
        "satisfied_gate_count": 2,
        "blocking_gate_count": 1,
        "claim_gate_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23canon observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23canon index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23canon manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23canon manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23canon.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23canon(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
