from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23bin import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        COLUMN_COLUMNS,
        COLUMN_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEIGHT_COLUMNS,
        WEIGHT_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23bin import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        COLUMN_COLUMNS,
        COLUMN_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEIGHT_COLUMNS,
        WEIGHT_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


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


def validate_long_k23bin() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23bin_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23bin seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23bin cert mismatch")
    for filename, key in {
        "basis_rows.csv": "basis_csv",
        "column_rows.csv": "column_csv",
        "weight_rows.csv": "weight_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23bin {filename} mismatch")
    for key, expected_array in {
        "basis_table": expected["basis_table"],
        "column_table": expected["column_table"],
        "weight_table": expected["weight_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23bin table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23bin matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23bin.report@1":
        raise AssertionError("long_k23bin report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23bin report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23bin all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23bin checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23bin report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23bin report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("basis_rows.csv", BASIS_COLUMNS, 23),
        ("column_rows.csv", COLUMN_COLUMNS, 56),
        ("weight_rows.csv", WEIGHT_COLUMNS, 57),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23bin {filename} shape mismatch")

    assert_locked_hash(
        "basis rows",
        hashlib.sha256(digest_text(BASIS_COLUMNS, csv_rows["basis_rows.csv"]).encode("ascii")).hexdigest(),
        BASIS_TEXT_HASH,
    )
    assert_locked_hash(
        "column rows",
        hashlib.sha256(digest_text(COLUMN_COLUMNS, csv_rows["column_rows.csv"]).encode("ascii")).hexdigest(),
        COLUMN_TEXT_HASH,
    )
    assert_locked_hash(
        "weight rows",
        hashlib.sha256(digest_text(WEIGHT_COLUMNS, csv_rows["weight_rows.csv"]).encode("ascii")).hexdigest(),
        WEIGHT_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["kernel_mod2", "rref_mod2", "rowspace_weight_histogram", "column_activity", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23_certified_flag": 1,
        "support_input_row_count": 56,
        "kernel_basis_row_count": 23,
        "kernel_basis_column_count": 56,
        "binary_rank": 23,
        "binary_rowspace_word_count": 8388608,
        "min_nonzero_weight": 1,
        "max_weight": 29,
        "weight_one_word_count": 19,
        "zero_column_count": 24,
        "active_column_count": 32,
        "odd_column_count": 27,
        "even_nonzero_column_count": 5,
        "binary_even_code_flag": 0,
        "binary_doubly_even_code_flag": 0,
        "quotient_collapse_required_flag": 1,
        "k23_equality_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23bin observable {name} mismatch")

    weight_hist = {
        int(row["weight"]): int(row["rowspace_word_count"])
        for row in rows_from_table(np.asarray(tables["weight_table"]), WEIGHT_COLUMNS)
    }
    expected_hist = {
        0: 1,
        1: 19,
        2: 172,
        3: 988,
        4: 4048,
        5: 12616,
        6: 31181,
        7: 63029,
        8: 107048,
        9: 157398,
        10: 209039,
        11: 267159,
        12: 352241,
        13: 490637,
        14: 689282,
        15: 911506,
        16: 1081081,
        17: 1122919,
        18: 1011978,
        19: 788938,
        20: 531354,
        21: 308314,
        22: 153121,
        23: 64297,
        24: 22382,
        25: 6272,
        26: 1355,
        27: 211,
        28: 21,
        29: 1,
    }
    for weight in range(57):
        if weight_hist.get(weight, 0) != expected_hist.get(weight, 0):
            raise AssertionError(f"long_k23bin weight histogram mismatch at {weight}")

    column_activity = np.asarray(matrices["column_activity"], dtype=np.int64)
    if column_activity.shape != (56,):
        raise AssertionError("long_k23bin column activity shape mismatch")
    if int((column_activity == 0).sum()) != 24:
        raise AssertionError("long_k23bin zero column count mismatch")
    if np.asarray(matrices["kernel_mod2"]).shape != (23, 56):
        raise AssertionError("long_k23bin kernel mod2 shape mismatch")
    if int(np.asarray(matrices["kernel_mod2"]).sum()) != 45:
        raise AssertionError("long_k23bin kernel mod2 nonzero count mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23bin.manifest@1":
        raise AssertionError("long_k23bin manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23bin manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23bin manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23bin index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23bin index report sha mismatch")

    return {
        "schema": "long.k23bin.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23bin(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
