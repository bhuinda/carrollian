from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23fing import (
        DERIVE_SCRIPT,
        GUARD_COLUMNS,
        GUARD_TEXT_HASH,
        INGEST_COLUMNS,
        INGEST_TEXT_HASH,
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
    from derive_long_k23fing import (
        DERIVE_SCRIPT,
        GUARD_COLUMNS,
        GUARD_TEXT_HASH,
        INGEST_COLUMNS,
        INGEST_TEXT_HASH,
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


EXPECTED_FIRST_INGEST = (0, 0, 0, 1, 1, 0, 0, 0, 0, 0)
EXPECTED_LAST_INGEST = (5, 5, 5, 1, 1, 1, 0, 1, 0, 1)
EXPECTED_FIRST_GUARD = (0, 0, 1, 0, 1, 1, 0)
EXPECTED_LAST_GUARD = (7, 7, 0, 1, 1, 0, 0)


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


def validate_long_k23fing() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23fing_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23fing seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23fing cert mismatch")
    for filename, key in {
        "ingest_rows.csv": "ingest_csv",
        "guard_rows.csv": "guard_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23fing {filename} mismatch")
    for key, expected_array in {
        "ingest_table": expected["ingest_table"],
        "guard_table": expected["guard_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23fing table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23fing matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23fing.report@1":
        raise AssertionError("long_k23fing report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23fing report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23fing all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23fing checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23fing report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23fing report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("ingest_rows.csv", INGEST_COLUMNS, 6),
        ("guard_rows.csv", GUARD_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23fing {filename} shape mismatch")

    assert_locked_hash(
        "ingest rows",
        hashlib.sha256(digest_text(INGEST_COLUMNS, csv_rows["ingest_rows.csv"]).encode("ascii")).hexdigest(),
        INGEST_TEXT_HASH,
    )
    assert_locked_hash(
        "guard rows",
        hashlib.sha256(digest_text(GUARD_COLUMNS, csv_rows["guard_rows.csv"]).encode("ascii")).hexdigest(),
        GUARD_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["ingest_table", "guard_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    ingest_rows = csv_rows["ingest_rows.csv"]
    if int_tuple(ingest_rows[0], INGEST_COLUMNS) != EXPECTED_FIRST_INGEST:
        raise AssertionError("long_k23fing first ingest row mismatch")
    if int_tuple(ingest_rows[-1], INGEST_COLUMNS) != EXPECTED_LAST_INGEST:
        raise AssertionError("long_k23fing last ingest row mismatch")
    if any(int(row["ingested_flag"]) != 1 for row in ingest_rows):
        raise AssertionError("long_k23fing ingestion flag mismatch")
    if any(int(row["broad_integration_run_flag"]) != 0 for row in ingest_rows):
        raise AssertionError("long_k23fing broad-run mismatch")

    guard_rows = csv_rows["guard_rows.csv"]
    if int_tuple(guard_rows[0], GUARD_COLUMNS) != EXPECTED_FIRST_GUARD:
        raise AssertionError("long_k23fing first guard row mismatch")
    if int_tuple(guard_rows[-1], GUARD_COLUMNS) != EXPECTED_LAST_GUARD:
        raise AssertionError("long_k23fing last guard row mismatch")
    if any(int(row["preserved_flag"]) != 1 for row in guard_rows):
        raise AssertionError("long_k23fing guard preservation mismatch")
    if any(int(row["overclaim_flag"]) != 0 for row in guard_rows):
        raise AssertionError("long_k23fing overclaim mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 5,
        "certified_input_count": 5,
        "ingest_row_count": 6,
        "ingested_row_count": 6,
        "certified_ingest_count": 6,
        "open_boundary_preserved_count": 5,
        "focused_verifier_count": 1,
        "oracle_refresh_deferred_count": 1,
        "broad_integration_run_count": 0,
        "broad_integration_required_count": 1,
        "guard_row_count": 8,
        "closed_guard_count": 3,
        "open_guard_count": 5,
        "overclaim_count": 0,
        "proof_source_decision_flag": 1,
        "route_blocking_count": 0,
        "required_open_claim_count": 0,
        "frontier_route_flag": 1,
        "ready_route_count": 4,
        "current_frontier_preserved_flag": 1,
        "frontier_card_count": 13,
        "frontier_open_count": 1,
        "frontier_highest_yield_target_code": 12,
        "cluster_reopen_count": 6,
        "cluster_seam_candidate_count": 49,
        "proof_of_mandate_frontier_ingestion_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23fing observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23fing index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23fing.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23fing(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
