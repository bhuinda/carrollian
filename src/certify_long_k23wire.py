from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23wire import (
        DERIVE_SCRIPT,
        EQUATION_COLUMNS,
        EQUATION_TEXT_HASH,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WIRE_COLUMNS,
        WIRE_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23wire import (
        DERIVE_SCRIPT,
        EQUATION_COLUMNS,
        EQUATION_TEXT_HASH,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WIRE_COLUMNS,
        WIRE_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_WIRE = (0, 0, 5, 27, 5, 1, 1, 1, 1, 4, 1, 1, 0, 0)
EXPECTED_LAST_WIRE = (55, 55, 90, 39, 0, 1, 1, 1, 1, 4, 1, 1, 0, 0)
EXPECTED_FIRST_EQUATION = (0, 0, 224, 224, 1, 0, 0)
EXPECTED_BASELINE_EQUATION = (3, 3, 224, 1568, 0, 1, 0)
EXPECTED_LAST_EQUATION = (4, 4, -1344, -1344, 1, 0, 0)
EXPECTED_FIRST_LIMIT = (0, 0, 1, 1, 0)
EXPECTED_LAST_LIMIT = (3, 3, 1, 1, 0)


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


def validate_long_k23wire() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23wire_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23wire seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23wire cert mismatch")
    for filename, key in {
        "wire_rows.csv": "wire_csv",
        "equation_rows.csv": "equation_csv",
        "limit_rows.csv": "limit_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23wire {filename} mismatch")
    for key, expected_array in {
        "wire_table": expected["wire_table"],
        "equation_table": expected["equation_table"],
        "limit_table": expected["limit_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23wire table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23wire matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23wire.report@1":
        raise AssertionError("long_k23wire report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23wire report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23wire all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23wire checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23wire report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23wire report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("wire_rows.csv", WIRE_COLUMNS, 56),
        ("equation_rows.csv", EQUATION_COLUMNS, 5),
        ("limit_rows.csv", LIMIT_COLUMNS, 4),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23wire {filename} shape mismatch")

    assert_locked_hash(
        "wire rows",
        hashlib.sha256(digest_text(WIRE_COLUMNS, csv_rows["wire_rows.csv"]).encode("ascii")).hexdigest(),
        WIRE_TEXT_HASH,
    )
    assert_locked_hash(
        "equation rows",
        hashlib.sha256(digest_text(EQUATION_COLUMNS, csv_rows["equation_rows.csv"]).encode("ascii")).hexdigest(),
        EQUATION_TEXT_HASH,
    )
    assert_locked_hash(
        "limit rows",
        hashlib.sha256(digest_text(LIMIT_COLUMNS, csv_rows["limit_rows.csv"]).encode("ascii")).hexdigest(),
        LIMIT_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["wire_table", "equation_table", "limit_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    wire_rows = csv_rows["wire_rows.csv"]
    if int_tuple(wire_rows[0], WIRE_COLUMNS) != EXPECTED_FIRST_WIRE:
        raise AssertionError("long_k23wire first wire row mismatch")
    if int_tuple(wire_rows[-1], WIRE_COLUMNS) != EXPECTED_LAST_WIRE:
        raise AssertionError("long_k23wire last wire row mismatch")
    if any(int(row["wire_row_bytes"]) != 4 for row in wire_rows):
        raise AssertionError("long_k23wire row-byte mismatch")
    if any(int(row["table_index_dependency_flag"]) != 1 for row in wire_rows):
        raise AssertionError("long_k23wire table-dependency mismatch")
    if any(int(row["digest_free_wire_flag"]) != 1 for row in wire_rows):
        raise AssertionError("long_k23wire digest-free mismatch")
    if any(int(row["wire_equivalence_claim_flag"]) != 0 for row in wire_rows):
        raise AssertionError("long_k23wire equivalence overclaim")
    if any(int(row["external_improvement_claim_flag"]) != 0 for row in wire_rows):
        raise AssertionError("long_k23wire improvement overclaim")

    equation_rows = csv_rows["equation_rows.csv"]
    if int_tuple(equation_rows[0], EQUATION_COLUMNS) != EXPECTED_FIRST_EQUATION:
        raise AssertionError("long_k23wire first equation mismatch")
    if int_tuple(equation_rows[3], EQUATION_COLUMNS) != EXPECTED_BASELINE_EQUATION:
        raise AssertionError("long_k23wire baseline equation mismatch")
    if int_tuple(equation_rows[-1], EQUATION_COLUMNS) != EXPECTED_LAST_EQUATION:
        raise AssertionError("long_k23wire last equation mismatch")
    if any(int(row["claim_flag"]) != 0 for row in equation_rows):
        raise AssertionError("long_k23wire equation claim mismatch")

    limit_rows = csv_rows["limit_rows.csv"]
    if int_tuple(limit_rows[0], LIMIT_COLUMNS) != EXPECTED_FIRST_LIMIT:
        raise AssertionError("long_k23wire first limit row mismatch")
    if int_tuple(limit_rows[-1], LIMIT_COLUMNS) != EXPECTED_LAST_LIMIT:
        raise AssertionError("long_k23wire last limit row mismatch")
    if any(int(row["open_flag"]) != 1 for row in limit_rows):
        raise AssertionError("long_k23wire limit openness mismatch")
    if any(int(row["overclaim_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23wire limit overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 2,
        "certified_input_count": 2,
        "wire_row_count": 56,
        "max_transcript_id": 55,
        "max_selected_opening_id": 90,
        "max_residual_class_code": 55,
        "max_selector_value_mod": 5,
        "one_byte_field_count": 4,
        "wire_row_bytes": 4,
        "wire_total_bytes": 224,
        "norm_internal_public_digest_bytes": 5376,
        "norm_baseline_public_exchange_bytes": 1568,
        "saved_vs_internal_digest_bytes": 5152,
        "delta_vs_baseline_public_bytes": -1344,
        "compact_vs_internal_digest_flag": 1,
        "compact_vs_baseline_public_flag": 1,
        "digest_free_wire_count": 56,
        "table_index_dependency_count": 56,
        "wire_equivalence_claim_count": 0,
        "external_improvement_claim_count": 0,
        "equation_row_count": 5,
        "equation_pass_count": 5,
        "limit_row_count": 4,
        "open_limit_count": 4,
        "overclaim_count": 0,
        "compact_wire_map_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23wire observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23wire index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23wire.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23wire(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
