from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23merge import (
        DERIVE_SCRIPT,
        GROUP_COLUMNS,
        GROUP_TEXT_HASH,
        IMAGE_COLUMNS,
        IMAGE_TEXT_HASH,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        TARGET_COLUMNS,
        TARGET_TEXT_HASH,
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
    from derive_long_k23merge import (
        DERIVE_SCRIPT,
        GROUP_COLUMNS,
        GROUP_TEXT_HASH,
        IMAGE_COLUMNS,
        IMAGE_TEXT_HASH,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        TARGET_COLUMNS,
        TARGET_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
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


def validate_long_k23merge() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23merge_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23merge seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23merge cert mismatch")
    for filename, key in {
        "group_rows.csv": "group_csv",
        "target_rows.csv": "target_csv",
        "image_rows.csv": "image_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23merge {filename} mismatch")
    for key, expected_array in {
        "group_table": expected["group_table"],
        "target_table": expected["target_table"],
        "image_table": expected["image_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23merge table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23merge matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23merge.report@1":
        raise AssertionError("long_k23merge report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23merge report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23merge all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23merge checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23merge report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23merge report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("group_rows.csv", GROUP_COLUMNS, 17),
        ("target_rows.csv", TARGET_COLUMNS, 24),
        ("image_rows.csv", IMAGE_COLUMNS, 4),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23merge {filename} shape mismatch")

    assert_locked_hash(
        "group rows",
        hashlib.sha256(digest_text(GROUP_COLUMNS, csv_rows["group_rows.csv"]).encode("ascii")).hexdigest(),
        GROUP_TEXT_HASH,
    )
    assert_locked_hash(
        "target rows",
        hashlib.sha256(digest_text(TARGET_COLUMNS, csv_rows["target_rows.csv"]).encode("ascii")).hexdigest(),
        TARGET_TEXT_HASH,
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
        for key in ["component_projection", "merge_projection", "image_generators", "image_words", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23q_certified_flag": 1,
        "w24_code_certified_flag": 1,
        "component_count": 37,
        "active_component_count": 21,
        "merge_group_count": 17,
        "nonzero_merge_group_count": 16,
        "zero_merge_group_count": 1,
        "target_used_coordinate_count": 17,
        "image_generator_rank": 2,
        "image_rowspace_word_count": 4,
        "image_w24_member_word_count": 4,
        "image_w24_subcode_flag": 1,
        "dodecad_weight": 12,
        "octad_weight": 8,
        "intersection_weight": 4,
        "sum_weight": 12,
        "full_k23_equality_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23merge observable {name} mismatch")

    image_rows = rows_from_table(np.asarray(tables["image_table"]), IMAGE_COLUMNS)
    expected_masks = {0, 4095, 61833, 65142}
    actual_masks = {int(row["image_mask"]) for row in image_rows}
    if actual_masks != expected_masks:
        raise AssertionError("long_k23merge image mask set mismatch")
    if any(int(row["w24_member_flag"]) != 1 for row in image_rows):
        raise AssertionError("long_k23merge image W24 membership mismatch")
    if np.asarray(matrices["component_projection"]).shape != (23, 37):
        raise AssertionError("long_k23merge component projection shape mismatch")
    if np.asarray(matrices["merge_projection"]).shape != (37, 24):
        raise AssertionError("long_k23merge merge projection shape mismatch")
    if int(np.asarray(matrices["merge_projection"]).sum()) != 21:
        raise AssertionError("long_k23merge merge projection nonzero count mismatch")
    if np.asarray(matrices["image_generators"]).shape != (23, 24):
        raise AssertionError("long_k23merge image generator shape mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23merge.manifest@1":
        raise AssertionError("long_k23merge manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23merge manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23merge manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23merge index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23merge index report sha mismatch")

    return {
        "schema": "long.k23merge.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23merge(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
