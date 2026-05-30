from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23dist import (
        DECODE_COLUMNS,
        DECODE_TEXT_HASH,
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        INVALID_COLUMNS,
        INVALID_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PACKAGE_COLUMNS,
        PACKAGE_TEXT_HASH,
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
    from derive_long_k23dist import (
        DECODE_COLUMNS,
        DECODE_TEXT_HASH,
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        INVALID_COLUMNS,
        INVALID_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PACKAGE_COLUMNS,
        PACKAGE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_PACKAGE = (0, 0, 56, 1, 1, 1)
EXPECTED_LAST_PACKAGE = (1, 1, 91, 1, 1, 1)
EXPECTED_FIRST_DECODE = (0, 0, 1, 10, 5, 5, 50, 27, 5, 27, 5, 1, 1)
EXPECTED_LAST_DECODE = (55, 55, 1, 1, 0, 90, 85, 39, 90, 39, 0, 1, 1)
EXPECTED_FIRST_INVALID = (0, 56, 1, 0, 1)
EXPECTED_LAST_INVALID = (199, 255, 1, 0, 1)
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


def validate_long_k23dist() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23dist_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23dist seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23dist cert mismatch")
    for filename, key in {
        "package_rows.csv": "package_csv",
        "decode_rows.csv": "decode_csv",
        "invalid_rows.csv": "invalid_csv",
        "gate_rows.csv": "gate_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23dist {filename} mismatch")
    for key, expected_array in {
        "package_table": expected["package_table"],
        "decode_table": expected["decode_table"],
        "invalid_table": expected["invalid_table"],
        "gate_table": expected["gate_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23dist table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23dist matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23dist.report@1":
        raise AssertionError("long_k23dist report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23dist report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23dist all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23dist checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23dist report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23dist report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("package_rows.csv", PACKAGE_COLUMNS, 2),
        ("decode_rows.csv", DECODE_COLUMNS, 56),
        ("invalid_rows.csv", INVALID_COLUMNS, 200),
        ("gate_rows.csv", GATE_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23dist {filename} shape mismatch")

    assert_locked_hash(
        "package rows",
        hashlib.sha256(digest_text(PACKAGE_COLUMNS, csv_rows["package_rows.csv"]).encode("ascii")).hexdigest(),
        PACKAGE_TEXT_HASH,
    )
    assert_locked_hash(
        "decode rows",
        hashlib.sha256(digest_text(DECODE_COLUMNS, csv_rows["decode_rows.csv"]).encode("ascii")).hexdigest(),
        DECODE_TEXT_HASH,
    )
    assert_locked_hash(
        "invalid rows",
        hashlib.sha256(digest_text(INVALID_COLUMNS, csv_rows["invalid_rows.csv"]).encode("ascii")).hexdigest(),
        INVALID_TEXT_HASH,
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
        for key in ["package_table", "decode_table", "invalid_table", "gate_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    package_rows = csv_rows["package_rows.csv"]
    if int_tuple(package_rows[0], PACKAGE_COLUMNS) != EXPECTED_FIRST_PACKAGE:
        raise AssertionError("long_k23dist first package row mismatch")
    if int_tuple(package_rows[-1], PACKAGE_COLUMNS) != EXPECTED_LAST_PACKAGE:
        raise AssertionError("long_k23dist last package row mismatch")
    if any(int(row["runtime_public_package_flag"]) != 1 for row in package_rows):
        raise AssertionError("long_k23dist runtime package mismatch")

    decode_rows = csv_rows["decode_rows.csv"]
    if int_tuple(decode_rows[0], DECODE_COLUMNS) != EXPECTED_FIRST_DECODE:
        raise AssertionError("long_k23dist first decode row mismatch")
    if int_tuple(decode_rows[-1], DECODE_COLUMNS) != EXPECTED_LAST_DECODE:
        raise AssertionError("long_k23dist last decode row mismatch")
    if any(int(row["decode_match_flag"]) != 1 for row in decode_rows):
        raise AssertionError("long_k23dist decode mismatch")
    if any(int(row["verifier_accept_flag"]) != 1 for row in decode_rows):
        raise AssertionError("long_k23dist valid accept mismatch")

    invalid_rows = csv_rows["invalid_rows.csv"]
    if int_tuple(invalid_rows[0], INVALID_COLUMNS) != EXPECTED_FIRST_INVALID:
        raise AssertionError("long_k23dist first invalid row mismatch")
    if int_tuple(invalid_rows[-1], INVALID_COLUMNS) != EXPECTED_LAST_INVALID:
        raise AssertionError("long_k23dist last invalid row mismatch")
    if any(int(row["reject_flag"]) != 1 for row in invalid_rows):
        raise AssertionError("long_k23dist invalid reject mismatch")

    gate_rows = csv_rows["gate_rows.csv"]
    if int_tuple(gate_rows[0], GATE_COLUMNS) != EXPECTED_FIRST_GATE:
        raise AssertionError("long_k23dist first gate row mismatch")
    if int_tuple(gate_rows[-1], GATE_COLUMNS) != EXPECTED_LAST_GATE:
        raise AssertionError("long_k23dist last gate row mismatch")
    if sum(int(row["satisfied_flag"]) for row in gate_rows) != 3:
        raise AssertionError("long_k23dist satisfied gate count mismatch")
    if sum(int(row["blocking_flag"]) for row in gate_rows) != 2:
        raise AssertionError("long_k23dist blocking gate count mismatch")
    if any(int(row["claim_flag"]) != 0 for row in gate_rows):
        raise AssertionError("long_k23dist claim gate overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 3,
        "certified_input_count": 3,
        "package_table_count": 2,
        "package_row_count": 147,
        "file_hash_bound_count": 2,
        "certificate_resident_count": 2,
        "runtime_public_package_count": 2,
        "valid_decode_row_count": 56,
        "valid_decode_match_count": 56,
        "valid_verifier_accept_count": 56,
        "invalid_decode_row_count": 200,
        "invalid_reject_count": 200,
        "one_byte_namespace_size": 256,
        "valid_byte_count": 56,
        "invalid_byte_count": 200,
        "transcript_only_total_bytes": 56,
        "baseline_public_exchange_bytes": 1568,
        "saved_vs_baseline_bytes": 1512,
        "saved_vs_baseline_num": 27,
        "saved_vs_baseline_den": 28,
        "public_table_equivalence_count": 56,
        "selector_formula_count": 56,
        "max_valid_transcript_id": 55,
        "min_invalid_transcript_id": 56,
        "max_invalid_transcript_id": 255,
        "decoder_totality_flag": 1,
        "runtime_public_distribution_flag": 1,
        "public_transport_surface_flag": 1,
        "external_improvement_claim_count": 0,
        "external_interop_claim_count": 0,
        "external_benchmark_claim_count": 0,
        "gate_row_count": 5,
        "satisfied_gate_count": 3,
        "blocking_gate_count": 2,
        "claim_gate_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23dist observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23dist index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23dist manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23dist manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23dist.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23dist(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
