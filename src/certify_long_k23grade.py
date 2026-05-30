from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23grade import (
        LABEL_COLUMNS,
        LABEL_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROFILE_COLUMNS,
        PROFILE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        DERIVE_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23grade import (
        LABEL_COLUMNS,
        LABEL_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROFILE_COLUMNS,
        PROFILE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        DERIVE_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_PROFILE = {
    (0, 0): (1, 0, 218),
    (0, 1): (0, 4, 231),
    (0, 2): (0, 4, 189),
    (1, 0): (0, 117, 101),
    (1, 1): (0, 126, 109),
    (1, 2): (0, 86, 107),
    (2, 0): (0, 87, 131),
    (2, 1): (0, 105, 130),
    (2, 2): (0, 71, 122),
    (3, 0): (0, 44, 174),
    (3, 1): (0, 40, 195),
    (3, 2): (0, 34, 159),
    (4, 0): (0, 117, 101),
    (4, 1): (0, 130, 105),
    (4, 2): (0, 90, 103),
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


def validate_long_k23grade() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23grade_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23grade seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23grade cert mismatch")
    for filename, key in {
        "label_rows.csv": "label_csv",
        "profile_rows.csv": "profile_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23grade {filename} mismatch")
    for key, expected_array in {
        "label_table": expected["label_table"],
        "profile_table": expected["profile_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23grade table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23grade matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23grade.report@1":
        raise AssertionError("long_k23grade report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23grade report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23grade all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23grade checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23grade report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23grade report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("label_rows.csv", LABEL_COLUMNS, 20),
        ("profile_rows.csv", PROFILE_COLUMNS, 15),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23grade {filename} shape mismatch")

    assert_locked_hash(
        "label rows",
        hashlib.sha256(digest_text(LABEL_COLUMNS, csv_rows["label_rows.csv"]).encode("ascii")).hexdigest(),
        LABEL_TEXT_HASH,
    )
    assert_locked_hash(
        "profile rows",
        hashlib.sha256(digest_text(PROFILE_COLUMNS, csv_rows["profile_rows.csv"]).encode("ascii")).hexdigest(),
        PROFILE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "support_intertwiners",
            "family_label_matrix",
            "profile_table",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23lin_certified_flag": 1,
        "long_hcsupp_certified_flag": 1,
        "support_row_count": 56,
        "generator_count": 3,
        "family_count": 5,
        "label_row_count": 20,
        "profile_row_count": 15,
        "block_i_preserving_generator_count": 1,
        "rep4_preserving_generator_count": 0,
        "sign_preserving_generator_count": 0,
        "abs_coeff_preserving_generator_count": 0,
        "block_rep4_preserving_generator_count": 0,
        "block_i_total_leak_nonzero_count": 8,
        "rep4_total_leak_nonzero_count": 329,
        "sign_total_leak_nonzero_count": 263,
        "abs_coeff_total_leak_nonzero_count": 118,
        "block_rep4_total_leak_nonzero_count": 337,
        "coarse_block_partial_preservation_flag": 1,
        "full_generator_set_preserves_block_i_flag": 0,
        "full_generator_set_preserves_rep4_flag": 0,
        "full_generator_set_preserves_sign_flag": 0,
        "full_generator_set_preserves_abs_coeff_flag": 0,
        "full_generator_set_preserves_block_rep4_flag": 0,
        "height_projection_preservation_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23grade observable {name} mismatch")

    profile_rows = rows_from_table(np.asarray(tables["profile_table"]), PROFILE_COLUMNS)
    for row in profile_rows:
        key = (int(row["family_id"]), int(row["generator_id"]))
        expected_tuple = EXPECTED_PROFILE[key]
        actual_tuple = (
            int(row["preserved_flag"]),
            int(row["leak_nonzero_count"]),
            int(row["inside_nonzero_count"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23grade profile mismatch at {key}")
    if np.asarray(matrices["family_label_matrix"]).shape != (5, 56):
        raise AssertionError("long_k23grade label matrix shape mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23grade.manifest@1":
        raise AssertionError("long_k23grade manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23grade manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23grade manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23grade index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23grade index report sha mismatch")

    return {
        "schema": "long.k23grade.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23grade(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
