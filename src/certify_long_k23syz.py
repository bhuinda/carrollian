from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23syz import (
        COEFF_COLUMNS,
        COEFF_TEXT_HASH,
        ENTRY_COLUMNS,
        ENTRY_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PRIME,
        ROW_CHECK_COLUMNS,
        ROW_CHECK_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        DERIVE_SCRIPT,
        build_payloads,
        digest_text,
        gf_rank_mod,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23syz import (
        COEFF_COLUMNS,
        COEFF_TEXT_HASH,
        ENTRY_COLUMNS,
        ENTRY_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PRIME,
        ROW_CHECK_COLUMNS,
        ROW_CHECK_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        DERIVE_SCRIPT,
        build_payloads,
        digest_text,
        gf_rank_mod,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_PIVOTS = [0, 2, 12, 15, 16, 17, 19, 20, 21, 23, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 41, 53]
EXPECTED_COEFF_HIST = {-500001: 2, -2: 4, -1: 23, 1: 11, 2: 3}


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


def validate_long_k23syz() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23syz_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23syz seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23syz cert mismatch")
    for filename, key in {
        "support_frame_rows.csv": "support_csv",
        "coefficient_rows.csv": "entry_csv",
        "row_check_rows.csv": "row_check_csv",
        "coefficient_histogram.csv": "coeff_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23syz {filename} mismatch")
    for key, expected_array in {
        "support_table": expected["support_table"],
        "entry_table": expected["entry_table"],
        "row_check_table": expected["row_check_table"],
        "coeff_table": expected["coeff_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23syz table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23syz matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23syz.report@1":
        raise AssertionError("long_k23syz report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23syz report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23syz all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23syz checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23syz report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23syz report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("support_frame_rows.csv", SUPPORT_COLUMNS, 56),
        ("coefficient_rows.csv", ENTRY_COLUMNS, 43),
        ("row_check_rows.csv", ROW_CHECK_COLUMNS, 23),
        ("coefficient_histogram.csv", COEFF_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23syz {filename} shape mismatch")

    assert_locked_hash(
        "support rows",
        hashlib.sha256(digest_text(SUPPORT_COLUMNS, csv_rows["support_frame_rows.csv"]).encode("ascii")).hexdigest(),
        SUPPORT_TEXT_HASH,
    )
    assert_locked_hash(
        "entry rows",
        hashlib.sha256(digest_text(ENTRY_COLUMNS, csv_rows["coefficient_rows.csv"]).encode("ascii")).hexdigest(),
        ENTRY_TEXT_HASH,
    )
    assert_locked_hash(
        "row check rows",
        hashlib.sha256(digest_text(ROW_CHECK_COLUMNS, csv_rows["row_check_rows.csv"]).encode("ascii")).hexdigest(),
        ROW_CHECK_TEXT_HASH,
    )
    assert_locked_hash(
        "coefficient rows",
        hashlib.sha256(digest_text(COEFF_COLUMNS, csv_rows["coefficient_histogram.csv"]).encode("ascii")).hexdigest(),
        COEFF_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "prime_kernel",
            "row_operation_matrix",
            "pivot_columns",
            "frame_lift_mod",
            "frame_lift_signed",
            "target_frame_table",
            "reconstructed_frame_table",
            "residual_table",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23_certified_flag": 1,
        "long_k23lift_certified_flag": 1,
        "canonical_frame_certified_flag": 1,
        "prime_field": PRIME,
        "support_row_count": 56,
        "k23_basis_row_count": 23,
        "canonical_coordinate_count": 24,
        "euler_coordinate_count": 1,
        "syzygy_coordinate_count": 23,
        "target_euler_nonzero_count": 0,
        "target_syzygy_rank": 23,
        "prime_rank": 23,
        "pivot_column_count": 23,
        "frame_lift_row_count": 56,
        "frame_lift_column_count": 24,
        "active_frame_support_row_count": 23,
        "inactive_frame_support_row_count": 33,
        "frame_lift_nonzero_entry_count": 43,
        "euler_lift_nonzero_entry_count": 0,
        "syzygy_lift_nonzero_entry_count": 43,
        "zero_residual_row_count": 23,
        "prime_residual_nonzero_entry_count": 0,
        "reconstructed_syzygy_rank": 23,
        "rowspace_identity_certified_flag": 1,
        "coefficient_distinct_count": 5,
        "coefficient_min_signed": -500001,
        "coefficient_max_signed": 2,
        "negative_coefficient_count": 29,
        "positive_coefficient_count": 14,
        "half_residue_entry_count": 2,
        "signed_l1_total": 1000050,
        "golay_selector_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23syz observable {name} mismatch")

    pivots = [int(value) for value in np.asarray(matrices["pivot_columns"]).tolist()]
    if pivots != EXPECTED_PIVOTS:
        raise AssertionError("long_k23syz pivot list mismatch")
    coeff_hist = {
        int(row["coefficient_signed"]): int(row["entry_count"])
        for row in rows_from_table(np.asarray(tables["coeff_table"]), COEFF_COLUMNS)
    }
    if coeff_hist != EXPECTED_COEFF_HIST:
        raise AssertionError("long_k23syz coefficient histogram mismatch")
    target = np.asarray(matrices["target_frame_table"], dtype=np.int64)
    reconstructed = np.asarray(matrices["reconstructed_frame_table"], dtype=np.int64)
    if not np.array_equal(reconstructed, target):
        raise AssertionError("long_k23syz identity reconstruction mismatch")
    if int(np.asarray(matrices["residual_table"]).sum()) != 0:
        raise AssertionError("long_k23syz residual table mismatch")
    if int(np.count_nonzero(np.asarray(matrices["frame_lift_mod"])[:, 0])) != 0:
        raise AssertionError("long_k23syz Euler column not killed")
    if gf_rank_mod(reconstructed[:, 1:]) != 23:
        raise AssertionError("long_k23syz reconstructed syzygy rank mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23syz.manifest@1":
        raise AssertionError("long_k23syz manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23syz manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23syz manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23syz index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23syz index report sha mismatch")

    return {
        "schema": "long.k23syz.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23syz(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
