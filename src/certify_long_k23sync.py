from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23sync import (
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        FRONTIER_NUMERIC_COLUMNS,
        FRONTIER_TEXT_HASH,
        HANDOFF_COLUMNS,
        HANDOFF_NUMERIC_COLUMNS,
        HANDOFF_TEXT_HASH,
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
    from derive_long_k23sync import (
        DERIVE_SCRIPT,
        FRONTIER_COLUMNS,
        FRONTIER_NUMERIC_COLUMNS,
        FRONTIER_TEXT_HASH,
        HANDOFF_COLUMNS,
        HANDOFF_NUMERIC_COLUMNS,
        HANDOFF_TEXT_HASH,
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


EXPECTED_HANDOFF_IDS = ("long_k23roll", "long_k23rep")
EXPECTED_FRONTIER_IDS = ("long_frontier", "long_cluster")


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


def validate_long_k23sync() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23sync_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23sync seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23sync cert mismatch")
    for filename, key in {
        "handoff_rows.csv": "handoff_csv",
        "frontier_rows.csv": "frontier_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23sync {filename} mismatch")
    for key, expected_array in {
        "handoff_numeric_table": expected["handoff_numeric_table"],
        "frontier_numeric_table": expected["frontier_numeric_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23sync table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23sync matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23sync.report@1":
        raise AssertionError("long_k23sync report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23sync report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23sync all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23sync checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23sync report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23sync report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("handoff_rows.csv", HANDOFF_COLUMNS, 2),
        ("frontier_rows.csv", FRONTIER_COLUMNS, 2),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23sync {filename} shape mismatch")

    assert_locked_hash(
        "handoff rows",
        hashlib.sha256(digest_text(HANDOFF_COLUMNS, csv_rows["handoff_rows.csv"]).encode("ascii")).hexdigest(),
        HANDOFF_TEXT_HASH,
    )
    assert_locked_hash(
        "frontier rows",
        hashlib.sha256(digest_text(FRONTIER_COLUMNS, csv_rows["frontier_rows.csv"]).encode("ascii")).hexdigest(),
        FRONTIER_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["handoff_numeric_table", "frontier_numeric_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    if tuple(row["proof_id"] for row in csv_rows["handoff_rows.csv"]) != EXPECTED_HANDOFF_IDS:
        raise AssertionError("long_k23sync handoff proof order mismatch")
    if tuple(row["proof_id"] for row in csv_rows["frontier_rows.csv"]) != EXPECTED_FRONTIER_IDS:
        raise AssertionError("long_k23sync frontier proof order mismatch")
    if any(int(row["certified_flag"]) != 1 for row in csv_rows["handoff_rows.csv"]):
        raise AssertionError("long_k23sync uncertified handoff row")
    if any(int(row["ready_for_frontier_flag"]) != 1 for row in csv_rows["handoff_rows.csv"]):
        raise AssertionError("long_k23sync unready handoff row")
    if any(int(row["certified_flag"]) != 1 for row in csv_rows["frontier_rows.csv"]):
        raise AssertionError("long_k23sync uncertified frontier row")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 4,
        "certified_input_count": 4,
        "handoff_row_count": 2,
        "ready_handoff_count": 2,
        "frontier_row_count": 2,
        "frontier_guardrail_count": 2,
        "rollup_merge_point_flag": 1,
        "repeated_round_accounting_flag": 1,
        "repeated_round_max_depth": 8,
        "repeated_round_final_total": 94_058_496,
        "frontier_open_count": 1,
        "cluster_reopen_count": 6,
        "cluster_seam_candidate_count": 49,
        "current_frontier_preserved_flag": 1,
        "broad_integration_run_flag": 0,
        "broad_integration_required_flag": 1,
        "hardness_claim_flag": 0,
        "zero_knowledge_claim_flag": 0,
        "final_goal_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23sync observable {name} mismatch")

    for key, columns in {
        "handoff_numeric_table": HANDOFF_NUMERIC_COLUMNS,
        "frontier_numeric_table": FRONTIER_NUMERIC_COLUMNS,
    }.items():
        table_rows = rows_from_table(np.asarray(tables[key]), columns)
        if len(table_rows) != 2:
            raise AssertionError(f"long_k23sync {key} row count mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23sync index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23sync.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23sync(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
