from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23bind import (
        COORDINATE_COLUMNS,
        COORDINATE_TEXT_HASH,
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROW_CHECK_COLUMNS,
        ROW_CHECK_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        gf2_rank,
        matrix_payload_hash,
        row_mask,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23bind import (
        COORDINATE_COLUMNS,
        COORDINATE_TEXT_HASH,
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        ROW_CHECK_COLUMNS,
        ROW_CHECK_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        gf2_rank,
        matrix_payload_hash,
        row_mask,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_PIVOTS = [0, 2, 12, 15, 16, 17, 19, 20, 21, 23, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 41, 53]
EXPECTED_ACTIVE_SUPPORT_MASKS = {
    0: 255,
    2: 204095,
    12: 21845,
    16: 21845,
    17: 4260666,
    19: 10817331,
    20: 23100,
    23: 26202,
    28: 4297993,
    34: 333604,
    36: 591182,
    37: 1119352,
    39: 2164253,
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


def validate_long_k23bind() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23bind_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23bind seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23bind cert mismatch")
    for filename, key in {
        "support_binding_rows.csv": "support_csv",
        "coordinate_preimage_rows.csv": "coordinate_csv",
        "row_check_rows.csv": "row_check_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23bind {filename} mismatch")
    for key, expected_array in {
        "support_table": expected["support_table"],
        "coordinate_table": expected["coordinate_table"],
        "row_check_table": expected["row_check_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23bind table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23bind matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23bind.report@1":
        raise AssertionError("long_k23bind report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23bind report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23bind all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23bind checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23bind report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23bind report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("support_binding_rows.csv", SUPPORT_COLUMNS, 56),
        ("coordinate_preimage_rows.csv", COORDINATE_COLUMNS, 24),
        ("row_check_rows.csv", ROW_CHECK_COLUMNS, 23),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23bind {filename} shape mismatch")

    assert_locked_hash(
        "support rows",
        hashlib.sha256(digest_text(SUPPORT_COLUMNS, csv_rows["support_binding_rows.csv"]).encode("ascii")).hexdigest(),
        SUPPORT_TEXT_HASH,
    )
    assert_locked_hash(
        "coordinate rows",
        hashlib.sha256(
            digest_text(COORDINATE_COLUMNS, csv_rows["coordinate_preimage_rows.csv"]).encode("ascii")
        ).hexdigest(),
        COORDINATE_TEXT_HASH,
    )
    assert_locked_hash(
        "row check rows",
        hashlib.sha256(digest_text(ROW_CHECK_COLUMNS, csv_rows["row_check_rows.csv"]).encode("ascii")).hexdigest(),
        ROW_CHECK_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "support_kernel",
            "row_operation_matrix",
            "pivot_columns",
            "binding_matrix",
            "target_source_images",
            "reconstructed_source_images",
            "residual_source_images",
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
        "long_k23src_certified_flag": 1,
        "support_row_count": 56,
        "k23_basis_row_count": 23,
        "source_coordinate_count": 24,
        "support_normalized_rank": 23,
        "pivot_column_count": 23,
        "binding_matrix_row_count": 56,
        "binding_matrix_column_count": 24,
        "active_binding_support_row_count": 13,
        "inactive_binding_support_row_count": 43,
        "binding_nonzero_entry_count": 112,
        "coordinate_preimage_nonempty_count": 24,
        "row_check_count": 23,
        "zero_residual_row_count": 23,
        "max_residual_weight": 0,
        "reconstructed_image_rank": 12,
        "reconstructed_nonzero_row_count": 12,
        "binary_support_binding_certified_flag": 1,
        "signed_integral_binding_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23bind observable {name} mismatch")

    pivots = [int(value) for value in np.asarray(matrices["pivot_columns"]).tolist()]
    if pivots != EXPECTED_PIVOTS:
        raise AssertionError("long_k23bind pivot list mismatch")
    binding = np.asarray(matrices["binding_matrix"], dtype=np.uint8)
    active_masks = {
        row_id: row_mask(binding[row_id])
        for row_id in range(binding.shape[0])
        if int(binding[row_id].sum()) > 0
    }
    if active_masks != EXPECTED_ACTIVE_SUPPORT_MASKS:
        raise AssertionError("long_k23bind active support mask mismatch")
    support_kernel = np.asarray(matrices["support_kernel"], dtype=np.uint8)
    reconstructed = (support_kernel @ binding) % 2
    if gf2_rank(support_kernel) != 23:
        raise AssertionError("long_k23bind support rank mismatch")
    if not np.array_equal(
        reconstructed,
        np.asarray([[((int(mask) >> coord) & 1) for coord in range(24)] for mask in matrices["target_source_images"]], dtype=np.uint8),
    ):
        raise AssertionError("long_k23bind reconstruction mismatch")
    if int(np.asarray(matrices["residual_source_images"]).sum()) != 0:
        raise AssertionError("long_k23bind residual mask mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23bind.manifest@1":
        raise AssertionError("long_k23bind manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23bind manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23bind manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23bind index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23bind index report sha mismatch")

    return {
        "schema": "long.k23bind.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23bind(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
