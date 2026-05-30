from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23op import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        GRADE_COLUMNS,
        GRADE_TEXT_HASH,
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
    from derive_long_k23op import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        GRADE_COLUMNS,
        GRADE_TEXT_HASH,
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


EXPECTED_GENERATOR_ROWS = {
    0: (798, 787, 56, 1, 53, 1, 18, 34, 2, 294, 504, 33, 0, 1),
    1: (785, 769, 56, 1, 53, 1, 19, 32, 2, 219, 566, 57, 0, 1),
    2: (737, 729, 56, 1, 50, 1, 18, 30, 4, 316, 421, 35, 0, 1),
    3: (836, 822, 56, 1, 51, 1, 20, 30, 4, 184, 652, 43, 0, 1),
    4: (437, 401, 56, 1, 35, 1, 16, 34, 22, 267, 170, 18, 0, 1),
    5: (442, 408, 56, 1, 36, 1, 15, 37, 19, 238, 204, 19, 0, 1),
    6: (515, 482, 56, 1, 39, 1, 15, 38, 12, 350, 165, 8, 0, 1),
    7: (560, 526, 56, 1, 43, 1, 15, 36, 10, 354, 206, 16, 0, 1),
    8: (398, 364, 56, 1, 39, 1, 15, 37, 12, 239, 159, 20, 0, 1),
}
EXPECTED_FAMILY_LEAKS = {
    0: 787,
    1: 3526,
    2: 2557,
    3: 2066,
    4: 3745,
}


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


def validate_long_k23op() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23op_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23op seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23op cert mismatch")
    for filename, key in {
        "generator_rows.csv": "generator_csv",
        "grade_rows.csv": "grade_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23op {filename} mismatch")
    for key, expected_array in {
        "generator_table": expected["generator_table"],
        "grade_table": expected["grade_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23op table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23op matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23op.report@1":
        raise AssertionError("long_k23op report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23op report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23op all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23op checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23op report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23op report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("generator_rows.csv", GENERATOR_COLUMNS, 9),
        ("grade_rows.csv", GRADE_COLUMNS, 45),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23op {filename} shape mismatch")

    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "grade rows",
        hashlib.sha256(digest_text(GRADE_COLUMNS, csv_rows["grade_rows.csv"]).encode("ascii")).hexdigest(),
        GRADE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "r_hc_lifts",
            "family_label_matrix",
            "generator_table",
            "grade_table",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23rh_certified_flag": 1,
        "long_hcsupp_certified_flag": 1,
        "long_hcperm_certified_flag": 1,
        "support_row_count": 56,
        "generator_count": 9,
        "grading_family_count": 5,
        "generator_row_count": 9,
        "grade_row_count": 45,
        "signed_monomial_generator_count": 0,
        "dense_obstruction_generator_count": 9,
        "total_nonzero_count": 5508,
        "total_nonidentity_count": 5288,
        "row_singleton_total": 308,
        "column_singleton_total": 87,
        "signed_unit_entry_total": 2461,
        "nonunit_entry_total": 3047,
        "max_row_nonzero_count": 53,
        "max_column_nonzero_count": 20,
        "block_i_total_leak_nonzero_count": 787,
        "rep4_total_leak_nonzero_count": 3526,
        "sign_total_leak_nonzero_count": 2557,
        "abs_coeff_total_leak_nonzero_count": 2066,
        "block_rep4_total_leak_nonzero_count": 3745,
        "all_gradings_preserved_generator_count": 0,
        "signed_operation_support_obstruction_flag": 1,
        "multiplication_preservation_tested_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23op observable {name} mismatch")

    for row in csv_rows["generator_rows.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_GENERATOR_ROWS[generator_id]
        actual_tuple = (
            int(row["source_lift_nonzero_count"]),
            int(row["source_lift_nonidentity_count"]),
            int(row["source_lift_rank"]),
            int(row["row_nonzero_min"]),
            int(row["row_nonzero_max"]),
            int(row["column_nonzero_min"]),
            int(row["column_nonzero_max"]),
            int(row["row_singleton_count"]),
            int(row["column_singleton_count"]),
            int(row["signed_unit_entry_count"]),
            int(row["nonunit_entry_count"]),
            int(row["distinct_nonzero_value_count"]),
            int(row["signed_monomial_flag"]),
            int(row["dense_support_obstruction_flag"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23op generator row mismatch: {generator_id}")

    for family_id, expected_leak in EXPECTED_FAMILY_LEAKS.items():
        actual_leak = sum(
            int(row["leak_nonzero_count"])
            for row in csv_rows["grade_rows.csv"]
            if int(row["family_id"]) == family_id
        )
        if actual_leak != expected_leak:
            raise AssertionError(f"long_k23op family leak mismatch: {family_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23op index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23op.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23op(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
