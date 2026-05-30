from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23ifc import (
        AUDIT_COLUMNS,
        AUDIT_TEXT_HASH,
        DERIVE_SCRIPT,
        FIELD_COLUMNS,
        FIELD_TEXT_HASH,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REJECTION_COLUMNS,
        REJECTION_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        TOOL_COLUMNS,
        TOOL_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23ifc import (
        AUDIT_COLUMNS,
        AUDIT_TEXT_HASH,
        DERIVE_SCRIPT,
        FIELD_COLUMNS,
        FIELD_TEXT_HASH,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        REJECTION_COLUMNS,
        REJECTION_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        TOOL_COLUMNS,
        TOOL_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_TOOL = (0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0)
EXPECTED_LAST_TOOL = (4, 5, 1, 0, 4, 1, 1, 1, 1, 1, 0)
EXPECTED_FIRST_FIELD = (0, 0, 0, 1, 1, 1, 1, 256)
EXPECTED_LAST_FIELD = (9, 9, 2, 2, 1, 1, 0, 56)
EXPECTED_FIRST_REJECTION = (0, 0, 1, 56, 0, 1, 1)
EXPECTED_LAST_REJECTION = (3, 3, 0, 1, 1, 0, 1)
EXPECTED_FIRST_AUDIT = (0, 0, 0, 1, 256, 1)
EXPECTED_LAST_AUDIT = (7, 7, 9, 2, 56, 1)
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


def validate_long_k23ifc() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23ifc_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23ifc seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23ifc cert mismatch")
    for filename, key in {
        "tool_rows.csv": "tool_csv",
        "field_rows.csv": "field_csv",
        "rejection_rows.csv": "rejection_csv",
        "audit_rows.csv": "audit_csv",
        "gate_rows.csv": "gate_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23ifc {filename} mismatch")
    for key, expected_array in {
        "tool_table": expected["tool_table"],
        "field_table": expected["field_table"],
        "rejection_table": expected["rejection_table"],
        "audit_table": expected["audit_table"],
        "gate_table": expected["gate_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23ifc table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23ifc matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23ifc.report@1":
        raise AssertionError("long_k23ifc report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23ifc report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23ifc all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23ifc checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23ifc report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23ifc report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("tool_rows.csv", TOOL_COLUMNS, 5),
        ("field_rows.csv", FIELD_COLUMNS, 10),
        ("rejection_rows.csv", REJECTION_COLUMNS, 4),
        ("audit_rows.csv", AUDIT_COLUMNS, 8),
        ("gate_rows.csv", GATE_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23ifc {filename} shape mismatch")

    assert_locked_hash("tool rows", hashlib.sha256(digest_text(TOOL_COLUMNS, csv_rows["tool_rows.csv"]).encode("ascii")).hexdigest(), TOOL_TEXT_HASH)
    assert_locked_hash("field rows", hashlib.sha256(digest_text(FIELD_COLUMNS, csv_rows["field_rows.csv"]).encode("ascii")).hexdigest(), FIELD_TEXT_HASH)
    assert_locked_hash("rejection rows", hashlib.sha256(digest_text(REJECTION_COLUMNS, csv_rows["rejection_rows.csv"]).encode("ascii")).hexdigest(), REJECTION_TEXT_HASH)
    assert_locked_hash("audit rows", hashlib.sha256(digest_text(AUDIT_COLUMNS, csv_rows["audit_rows.csv"]).encode("ascii")).hexdigest(), AUDIT_TEXT_HASH)
    assert_locked_hash("gate rows", hashlib.sha256(digest_text(GATE_COLUMNS, csv_rows["gate_rows.csv"]).encode("ascii")).hexdigest(), GATE_TEXT_HASH)
    assert_locked_hash("observable rows", hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(), OBS_TEXT_HASH)
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "tool_table",
            "field_table",
            "rejection_table",
            "audit_table",
            "gate_table",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    if int_tuple(csv_rows["tool_rows.csv"][0], TOOL_COLUMNS) != EXPECTED_FIRST_TOOL:
        raise AssertionError("long_k23ifc first tool row mismatch")
    if int_tuple(csv_rows["tool_rows.csv"][-1], TOOL_COLUMNS) != EXPECTED_LAST_TOOL:
        raise AssertionError("long_k23ifc last tool row mismatch")
    if any(int(row["hardness_claim_flag"]) != 0 for row in csv_rows["tool_rows.csv"]):
        raise AssertionError("long_k23ifc tool overclaim")
    if int_tuple(csv_rows["field_rows.csv"][0], FIELD_COLUMNS) != EXPECTED_FIRST_FIELD:
        raise AssertionError("long_k23ifc first field row mismatch")
    if int_tuple(csv_rows["field_rows.csv"][-1], FIELD_COLUMNS) != EXPECTED_LAST_FIELD:
        raise AssertionError("long_k23ifc last field row mismatch")
    if int_tuple(csv_rows["rejection_rows.csv"][0], REJECTION_COLUMNS) != EXPECTED_FIRST_REJECTION:
        raise AssertionError("long_k23ifc first rejection row mismatch")
    if int_tuple(csv_rows["rejection_rows.csv"][-1], REJECTION_COLUMNS) != EXPECTED_LAST_REJECTION:
        raise AssertionError("long_k23ifc last rejection row mismatch")
    if int_tuple(csv_rows["audit_rows.csv"][0], AUDIT_COLUMNS) != EXPECTED_FIRST_AUDIT:
        raise AssertionError("long_k23ifc first audit row mismatch")
    if int_tuple(csv_rows["audit_rows.csv"][-1], AUDIT_COLUMNS) != EXPECTED_LAST_AUDIT:
        raise AssertionError("long_k23ifc last audit row mismatch")
    if int_tuple(csv_rows["gate_rows.csv"][0], GATE_COLUMNS) != EXPECTED_FIRST_GATE:
        raise AssertionError("long_k23ifc first gate row mismatch")
    if int_tuple(csv_rows["gate_rows.csv"][-1], GATE_COLUMNS) != EXPECTED_LAST_GATE:
        raise AssertionError("long_k23ifc last gate row mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 5,
        "certified_input_count": 5,
        "input_csv_count": 3,
        "tool_row_count": 5,
        "public_tool_count": 5,
        "deterministic_tool_count": 5,
        "integrity_check_tool_count": 5,
        "audit_transcript_tool_count": 5,
        "hardness_claim_count": 0,
        "field_row_count": 10,
        "required_field_count": 10,
        "public_field_count": 10,
        "one_byte_field_count": 1,
        "input_field_count": 3,
        "output_field_count": 5,
        "audit_field_count": 2,
        "rejection_row_count": 4,
        "reject_code_count": 3,
        "terminal_code_count": 3,
        "public_code_count": 4,
        "accept_valid_count": 56,
        "invalid_reject_count": 200,
        "nonhardness_reject_count": 2,
        "missing_reduction_boundary_count": 1,
        "audit_row_count": 8,
        "required_audit_field_count": 8,
        "valid_decode_count": 56,
        "decode_match_count": 56,
        "verifier_accept_count": 56,
        "one_byte_namespace_size": 256,
        "package_row_count": 147,
        "mandate_row_count": 56,
        "selector_match_count": 56,
        "digest_bound_count": 56,
        "external_randomness_used_count": 0,
        "materialized_version_count": 2,
        "migration_pass_count": 1,
        "transcript_index_bytes": 56,
        "integrity_tooling_ready_flag": 1,
        "interface_contract_ready_flag": 1,
        "deploy_ready_flag": 0,
        "gate_row_count": 5,
        "satisfied_gate_count": 4,
        "blocking_gate_count": 1,
        "claim_gate_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23ifc observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23ifc index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23ifc manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23ifc manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23ifc.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23ifc(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
