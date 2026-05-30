from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23froute import (
        DERIVE_SCRIPT,
        GUARD_COLUMNS,
        GUARD_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROUTE_COLUMNS,
        ROUTE_TEXT_HASH,
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
    from derive_long_k23froute import (
        DERIVE_SCRIPT,
        GUARD_COLUMNS,
        GUARD_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROUTE_COLUMNS,
        ROUTE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_ROUTE = (0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1)
EXPECTED_LAST_ROUTE = (3, 3, 3, 4, 1, 1, 1, 1, 0, 1, 1)
EXPECTED_FIRST_GUARD = (0, 0, 1, 0, 1, 0, 1)
EXPECTED_BROAD_GUARD = (4, 4, 1, 0, 1, 1, 1)
EXPECTED_LAST_GUARD = (7, 7, 1, 0, 1, 0, 1)


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


def validate_long_k23froute() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23froute_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23froute seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23froute cert mismatch")
    for filename, key in {
        "route_rows.csv": "route_csv",
        "guard_rows.csv": "guard_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23froute {filename} mismatch")
    for key, expected_array in {
        "route_table": expected["route_table"],
        "guard_table": expected["guard_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23froute table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23froute matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23froute.report@1":
        raise AssertionError("long_k23froute report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23froute report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23froute all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23froute checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23froute report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23froute report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("route_rows.csv", ROUTE_COLUMNS, 4),
        ("guard_rows.csv", GUARD_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23froute {filename} shape mismatch")

    assert_locked_hash(
        "route rows",
        hashlib.sha256(digest_text(ROUTE_COLUMNS, csv_rows["route_rows.csv"]).encode("ascii")).hexdigest(),
        ROUTE_TEXT_HASH,
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
        for key in ["route_table", "guard_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    route_rows = csv_rows["route_rows.csv"]
    if int_tuple(route_rows[0], ROUTE_COLUMNS) != EXPECTED_FIRST_ROUTE:
        raise AssertionError("long_k23froute first route row mismatch")
    if int_tuple(route_rows[-1], ROUTE_COLUMNS) != EXPECTED_LAST_ROUTE:
        raise AssertionError("long_k23froute last route row mismatch")
    if any(int(row["route_ready_flag"]) != 1 for row in route_rows):
        raise AssertionError("long_k23froute route readiness mismatch")
    if any(int(row["broad_integration_run_flag"]) != 0 for row in route_rows):
        raise AssertionError("long_k23froute broad-run mismatch")

    guard_rows = csv_rows["guard_rows.csv"]
    if int_tuple(guard_rows[0], GUARD_COLUMNS) != EXPECTED_FIRST_GUARD:
        raise AssertionError("long_k23froute first guard row mismatch")
    if int_tuple(guard_rows[4], GUARD_COLUMNS) != EXPECTED_BROAD_GUARD:
        raise AssertionError("long_k23froute broad guard row mismatch")
    if int_tuple(guard_rows[-1], GUARD_COLUMNS) != EXPECTED_LAST_GUARD:
        raise AssertionError("long_k23froute last guard row mismatch")
    if any(int(row["claim_closed_flag"]) != 0 or int(row["claim_open_flag"]) != 1 for row in guard_rows):
        raise AssertionError("long_k23froute guard openness mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 5,
        "certified_input_count": 5,
        "route_row_count": 4,
        "ready_route_count": 4,
        "proof_mandate_route_count": 4,
        "frontier_preserved_route_count": 4,
        "broad_integration_run_count": 0,
        "challenge_source_extension_open_count": 4,
        "guard_row_count": 8,
        "open_guard_count": 8,
        "broad_required_guard_count": 1,
        "accepted_authority_count": 56,
        "finite_authority_closure_flag": 1,
        "deterministic_boundary_flag": 1,
        "external_randomness_required_count": 0,
        "randomness_independence_claim_flag": 0,
        "current_frontier_preserved_flag": 1,
        "frontier_open_count": 1,
        "cluster_reopen_count": 6,
        "cluster_seam_candidate_count": 49,
        "highest_yield_target_code": 12,
        "proof_of_mandate_frontier_route_flag": 1,
        "broad_integration_required_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23froute observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23froute index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23froute.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23froute(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
