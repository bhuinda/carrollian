from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23src import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        DERIVE_SCRIPT,
        EXTENSION_COLUMNS,
        EXTENSION_TEXT_HASH,
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
        gf2_rank,
        matrix_payload_hash,
        self_hash,
        span_from_basis_masks,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23src import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        DERIVE_SCRIPT,
        EXTENSION_COLUMNS,
        EXTENSION_TEXT_HASH,
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
        gf2_rank,
        matrix_payload_hash,
        self_hash,
        span_from_basis_masks,
    )
    from derive_long_raw import rows_from_table


EXPECTED_BASIS_ROW_IDS = [0, 2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11]
EXPECTED_ADDED_SOURCE_MASKS = {
    255,
    3945,
    13071,
    21845,
    38451,
    333604,
    591182,
    1119352,
    2164253,
    4260666,
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


def validate_long_k23src() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23src_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23src seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23src cert mismatch")
    for filename, key in {
        "extension_rows.csv": "extension_csv",
        "basis_rows.csv": "basis_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23src {filename} mismatch")
    for key, expected_array in {
        "extension_table": expected["extension_table"],
        "basis_table": expected["basis_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23src table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23src matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23src.report@1":
        raise AssertionError("long_k23src report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23src report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23src all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23src checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23src report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23src report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("extension_rows.csv", EXTENSION_COLUMNS, 23),
        ("basis_rows.csv", BASIS_COLUMNS, 12),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23src {filename} shape mismatch")

    assert_locked_hash(
        "extension rows",
        hashlib.sha256(digest_text(EXTENSION_COLUMNS, csv_rows["extension_rows.csv"]).encode("ascii")).hexdigest(),
        EXTENSION_TEXT_HASH,
    )
    assert_locked_hash(
        "basis rows",
        hashlib.sha256(digest_text(BASIS_COLUMNS, csv_rows["basis_rows.csv"]).encode("ascii")).hexdigest(),
        BASIS_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "original_source_images",
            "extension_source_images",
            "extension_target_images",
            "basis_source_masks",
            "basis_target_masks",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23merge_certified_flag": 1,
        "long_rm13map_certified_flag": 1,
        "external_w24_certified_flag": 1,
        "source_endpoint_word_count": 4096,
        "target_w24_word_count": 4096,
        "original_image_row_count": 23,
        "original_nonzero_image_row_count": 2,
        "original_source_image_rank": 2,
        "fixed_original_nonzero_row_count": 2,
        "added_extension_row_count": 10,
        "extension_row_count": 23,
        "extension_nonzero_row_count": 12,
        "extension_source_member_row_count": 23,
        "extension_target_member_row_count": 23,
        "extension_source_rank": 12,
        "extension_target_rank": 12,
        "extension_rowspace_word_count": 4096,
        "extension_rowspace_equals_source_endpoint_flag": 1,
        "extension_target_rowspace_equals_w24_flag": 1,
        "support_binding_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23src observable {name} mismatch")

    basis_rows = rows_from_table(np.asarray(tables["basis_table"]), BASIS_COLUMNS)
    basis_row_ids = [int(row["k23_basis_row_id"]) for row in basis_rows]
    if basis_row_ids != EXPECTED_BASIS_ROW_IDS:
        raise AssertionError("long_k23src basis row id sequence mismatch")
    basis_source_masks = [int(row["source_mask"]) for row in basis_rows]
    if gf2_rank(basis_source_masks) != 12:
        raise AssertionError("long_k23src basis source rank mismatch")
    added_masks = {
        int(row["extension_source_mask"])
        for row in rows_from_table(np.asarray(tables["extension_table"]), EXTENSION_COLUMNS)
        if int(row["added_extension_flag"]) == 1
    }
    if added_masks != EXPECTED_ADDED_SOURCE_MASKS:
        raise AssertionError("long_k23src added source mask set mismatch")
    if len(span_from_basis_masks(basis_source_masks)) != 4096:
        raise AssertionError("long_k23src source span size mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23src.manifest@1":
        raise AssertionError("long_k23src manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23src manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23src manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23src index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23src index report sha mismatch")

    return {
        "schema": "long.k23src.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23src(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
