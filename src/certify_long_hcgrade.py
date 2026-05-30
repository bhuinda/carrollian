from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcgrade import (
        CENTER_COLUMNS,
        CENTER_TEXT_HASH,
        DERIVE_SCRIPT,
        FEATURE_COLUMNS,
        FEATURE_TEXT_HASH,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SELECTED_COLUMNS,
        SELECTED_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_hcgrade import (
        CENTER_COLUMNS,
        CENTER_TEXT_HASH,
        DERIVE_SCRIPT,
        FEATURE_COLUMNS,
        FEATURE_TEXT_HASH,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        SELECTED_COLUMNS,
        SELECTED_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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


def matrix_payload_hash(payload: np.lib.npyio.NpzFile) -> str:
    keys = [
        "center_matrix",
        "feature_matrix",
        "feature_residual_matrix",
        "selected_feature_matrix",
        "projection_matrix",
    ]
    return hashlib.sha256(b"".join(np.ascontiguousarray(payload[key]).tobytes() for key in keys)).hexdigest()


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


def validate_long_hcgrade() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "center_grade_projection.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcgrade seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcgrade cert mismatch")
    for filename, key in {
        "center_rows.csv": "center_csv",
        "feature_rows.csv": "feature_csv",
        "selected_grade_rows.csv": "selected_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcgrade {filename} mismatch")
    for key, expected_array in {
        "center_table": expected["center_table"],
        "feature_table": expected["feature_table"],
        "selected_table": expected["selected_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcgrade table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_hcgrade matrix payload mismatch: {key}")

    if report.get("schema") != "long.hcgrade.report@1":
        raise AssertionError("long_hcgrade report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcgrade report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcgrade all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcgrade checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcgrade report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcgrade report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("center_rows.csv", CENTER_COLUMNS, 28),
        ("feature_rows.csv", FEATURE_COLUMNS, 24),
        ("selected_grade_rows.csv", SELECTED_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcgrade {filename} shape mismatch")

    assert_locked_hash(
        "center rows",
        hashlib.sha256(digest_text(CENTER_COLUMNS, csv_rows["center_rows.csv"]).encode("ascii")).hexdigest(),
        CENTER_TEXT_HASH,
    )
    assert_locked_hash(
        "feature rows",
        hashlib.sha256(digest_text(FEATURE_COLUMNS, csv_rows["feature_rows.csv"]).encode("ascii")).hexdigest(),
        FEATURE_TEXT_HASH,
    )
    assert_locked_hash(
        "selected rows",
        hashlib.sha256(digest_text(SELECTED_COLUMNS, csv_rows["selected_grade_rows.csv"]).encode("ascii")).hexdigest(),
        SELECTED_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    assert_locked_hash("matrix payload", matrix_payload_hash(matrices), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "support_dimension": 56,
        "center_coordinate_row_count": 28,
        "center_projection_rank": 28,
        "center_kernel_dimension": 28,
        "feature_family_row_count": 24,
        "feature_residual_rank": 5,
        "minimum_grade_row_count": 5,
        "rank33_combo_count": 256,
        "selected_grade_row_count": 5,
        "selected_projection_rank": 33,
        "selected_kernel_dimension": 23,
        "target_projection_rank": 33,
        "target_kernel_dimension": 23,
        "rank_matches_target_flag": 1,
        "kernel_matches_target_flag": 1,
        "center_grade_projection_materialized_flag": 1,
        "lambda3_binding_accepted_flag": 0,
        "pi_foam33_accepted_flag": 0,
        "r_hc_materialized_flag": 0,
        "full_intertwiner_claim_flag": 0,
        "focused_hcgrade_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcgrade observable {name} mismatch")

    selected_rows = csv_rows["selected_grade_rows.csv"]
    selected_signature = [
        (
            int(row["feature_id"]),
            int(row["feature_family_code"]),
            int(row["object_filter"]),
            int(row["feature_value"]),
            int(row["rank_after_addition"]),
        )
        for row in selected_rows
    ]
    if selected_signature != [
        (2, 1, -1, 1, 29),
        (3, 1, -1, 3, 30),
        (4, 1, -1, 6, 31),
        (7, 2, -1, 164063, 32),
        (10, 3, -1, -1, 33),
    ]:
        raise AssertionError("long_hcgrade selected feature signature mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcgrade.manifest@1":
        raise AssertionError("long_hcgrade manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcgrade manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcgrade manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("long_hcgrade missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcgrade proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcgrade proof obligation index status mismatch")
    index_without_hash = {key: value for key, value in index.items() if key != "registry_sha256"}
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcgrade.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "selected_feature_ids": witness.get("selected_feature_ids"),
            "matrix_sha256": witness.get("matrix_sha256"),
            "boundary": witness.get("boundary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcgrade(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
