from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23osint import (
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROUTE_COLUMNS,
        ROUTE_TEXT_HASH,
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
    from derive_long_k23osint import (
        DERIVE_SCRIPT,
        GATE_COLUMNS,
        GATE_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROUTE_COLUMNS,
        ROUTE_TEXT_HASH,
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


EXPECTED_SELECTED_ROUTE = (1, 1, 1, 1, 1, 1, 1, 1, 0, 0)
EXPECTED_OPEN_TOOL = (3, 3, 3, 5, 0, 0, 0, 0, 0, 1)
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


def validate_long_k23osint() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23osint_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23osint seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23osint cert mismatch")
    for filename, key in {
        "route_rows.csv": "route_csv",
        "tool_rows.csv": "tool_csv",
        "gate_rows.csv": "gate_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23osint {filename} mismatch")
    for key, expected_array in {
        "route_table": expected["route_table"],
        "tool_table": expected["tool_table"],
        "gate_table": expected["gate_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23osint table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23osint matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23osint.report@1":
        raise AssertionError("long_k23osint report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23osint report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23osint all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23osint checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23osint report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23osint report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("route_rows.csv", ROUTE_COLUMNS, 3),
        ("tool_rows.csv", TOOL_COLUMNS, 6),
        ("gate_rows.csv", GATE_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23osint {filename} shape mismatch")

    assert_locked_hash(
        "route rows",
        hashlib.sha256(digest_text(ROUTE_COLUMNS, csv_rows["route_rows.csv"]).encode("ascii")).hexdigest(),
        ROUTE_TEXT_HASH,
    )
    assert_locked_hash(
        "tool rows",
        hashlib.sha256(digest_text(TOOL_COLUMNS, csv_rows["tool_rows.csv"]).encode("ascii")).hexdigest(),
        TOOL_TEXT_HASH,
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
        for key in ["route_table", "tool_table", "gate_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    selected_routes = [row for row in csv_rows["route_rows.csv"] if int(row["selected_flag"]) == 1]
    if len(selected_routes) != 1:
        raise AssertionError("long_k23osint selected route count mismatch")
    if int_tuple(selected_routes[0], ROUTE_COLUMNS) != EXPECTED_SELECTED_ROUTE:
        raise AssertionError("long_k23osint selected route mismatch")
    if any(int(row["deploy_security_claim_flag"]) != 0 for row in csv_rows["route_rows.csv"]):
        raise AssertionError("long_k23osint route overclaim")

    open_tools = [row for row in csv_rows["tool_rows.csv"] if int(row["open_boundary_flag"]) == 1]
    if len(open_tools) != 1:
        raise AssertionError("long_k23osint open tool count mismatch")
    if int_tuple(open_tools[0], TOOL_COLUMNS) != EXPECTED_OPEN_TOOL:
        raise AssertionError("long_k23osint open tool row mismatch")
    if any(int(row["hardness_claim_flag"]) != 0 for row in csv_rows["tool_rows.csv"]):
        raise AssertionError("long_k23osint tool overclaim")

    gate_rows = csv_rows["gate_rows.csv"]
    if int_tuple(gate_rows[0], GATE_COLUMNS) != EXPECTED_FIRST_GATE:
        raise AssertionError("long_k23osint first gate row mismatch")
    if int_tuple(gate_rows[-1], GATE_COLUMNS) != EXPECTED_LAST_GATE:
        raise AssertionError("long_k23osint last gate row mismatch")
    if any(int(row["claim_flag"]) != 0 for row in gate_rows):
        raise AssertionError("long_k23osint gate overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 6,
        "certified_input_count": 6,
        "route_row_count": 3,
        "selected_route_count": 1,
        "integrity_route_selected_flag": 1,
        "reduction_route_selected_flag": 0,
        "external_route_selected_flag": 0,
        "route_blocking_count": 2,
        "deploy_security_claim_count": 0,
        "tool_row_count": 6,
        "public_tool_count": 5,
        "deterministic_tool_count": 5,
        "integrity_check_tool_count": 5,
        "rejection_feedback_tool_count": 3,
        "open_tool_boundary_count": 1,
        "hardness_claim_count": 0,
        "proof_of_mandate_flag": 1,
        "proof_of_mandate_ledger_flag": 1,
        "mandate_row_count": 56,
        "ledger_row_count": 12,
        "valid_decode_count": 56,
        "invalid_reject_count": 200,
        "bounded_soundness_error_numerator": 0,
        "bounded_soundness_error_denominator": 112_869_680,
        "transcript_index_bytes": 56,
        "saved_vs_baseline_bytes": 1512,
        "saved_vs_baseline_num": 27,
        "saved_vs_baseline_den": 28,
        "public_table_trivial_problem_count": 2,
        "materialized_reduction_count": 0,
        "native_singularity_theory_flag": 1,
        "open_source_integrity_route_flag": 1,
        "integrity_tooling_ready_flag": 1,
        "deploy_ready_flag": 0,
        "gate_row_count": 6,
        "satisfied_gate_count": 4,
        "blocking_gate_count": 2,
        "claim_gate_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23osint observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23osint index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator")
    if manifest.get("report_sha256") != report["certificate_sha256"]:
        raise AssertionError("long_k23osint manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23osint manifest self hash mismatch")

    return {
        "status": "PASS",
        "schema": "long.k23osint.verification@1",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": expected["report"]["witness"]["summary"],
        "next_highest_yield_item": expected["report"]["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23osint(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
