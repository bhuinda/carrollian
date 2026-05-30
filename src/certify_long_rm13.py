from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_rm13 import (
        DERIVE_SCRIPT,
        IMAGE_COLUMNS,
        IMAGE_TEXT_HASH,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STAGE_COLUMNS,
        STAGE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_rm13 import (
        DERIVE_SCRIPT,
        IMAGE_COLUMNS,
        IMAGE_TEXT_HASH,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STAGE_COLUMNS,
        STAGE_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )


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


def validate_long_rm13() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "rm13_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_rm13 seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rm13 cert mismatch")
    for filename, key in {
        "stage_rows.csv": "stage_csv",
        "image_rows.csv": "image_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rm13 {filename} mismatch")
    for key, expected_array in {
        "stage_table": expected["stage_table"],
        "image_table": expected["image_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rm13 table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_rm13 matrix payload mismatch: {key}")

    if report.get("schema") != "long.rm13.report@1":
        raise AssertionError("long_rm13 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rm13 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rm13 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rm13 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rm13 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rm13 report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("stage_rows.csv", STAGE_COLUMNS, 4),
        ("image_rows.csv", IMAGE_COLUMNS, 4),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_rm13 {filename} shape mismatch")

    assert_locked_hash(
        "stage rows",
        hashlib.sha256(digest_text(STAGE_COLUMNS, csv_rows["stage_rows.csv"]).encode("ascii")).hexdigest(),
        STAGE_TEXT_HASH,
    )
    assert_locked_hash(
        "image rows",
        hashlib.sha256(digest_text(IMAGE_COLUMNS, csv_rows["image_rows.csv"]).encode("ascii")).hexdigest(),
        IMAGE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["stage_table", "image_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23merge_certified_flag": 1,
        "external_w24_certified_flag": 1,
        "h8_size": 16,
        "h8_dimension": 4,
        "h8_weight4_count": 14,
        "c0_size": 4096,
        "c0_root_weight4_count": 42,
        "alpha_root_weight4_count": 18,
        "beta_root_weight4_count": 6,
        "gamma_root_weight4_count": 0,
        "source_endpoint_min_nonzero_weight": 8,
        "source_endpoint_external_w24_same_enumerator_flag": 1,
        "source_endpoint_external_w24_identity_equal_flag": 0,
        "source_endpoint_external_w24_intersection_count": 4,
        "source_endpoint_external_w24_symmetric_difference_count": 8184,
        "k23merge_image_word_count": 4,
        "k23merge_image_external_w24_member_count": 4,
        "k23merge_image_source_C0_member_count": 2,
        "k23merge_image_source_endpoint_member_count": 1,
        "nonzero_k23merge_image_source_endpoint_member_count": 0,
        "coordinate_conjugacy_materialized_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_rm13 observable {name} mismatch")

    stage_rows = rows_from_table(np.asarray(tables["stage_table"]), STAGE_COLUMNS)
    root_sequence = [int(row["root_weight4_count"]) for row in stage_rows]
    if root_sequence != [42, 18, 6, 0]:
        raise AssertionError("long_rm13 source root sequence mismatch")
    if [int(row["code_size"]) for row in stage_rows] != [4096, 4096, 4096, 4096]:
        raise AssertionError("long_rm13 source stage size mismatch")
    if int(stage_rows[-1]["external_w24_intersection_count"]) != 4:
        raise AssertionError("long_rm13 endpoint intersection mismatch")

    image_rows = rows_from_table(np.asarray(tables["image_table"]), IMAGE_COLUMNS)
    expected_masks = {0, 4095, 61833, 65142}
    actual_masks = {int(row["image_mask"]) for row in image_rows}
    if actual_masks != expected_masks:
        raise AssertionError("long_rm13 image mask set mismatch")
    if any(int(row["external_w24_member_flag"]) != 1 for row in image_rows):
        raise AssertionError("long_rm13 image external W24 membership mismatch")
    if sum(int(row["source_gamma_member_flag"]) for row in image_rows) != 1:
        raise AssertionError("long_rm13 source endpoint image membership mismatch")
    if any(int(row["source_gamma_member_flag"]) and int(row["image_mask"]) != 0 for row in image_rows):
        raise AssertionError("long_rm13 nonzero source endpoint image mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.rm13.manifest@1":
        raise AssertionError("long_rm13 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rm13 manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_rm13 manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_rm13 index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rm13 index report sha mismatch")

    return {
        "schema": "long.rm13.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_rm13(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
