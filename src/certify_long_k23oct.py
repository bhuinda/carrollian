from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23oct import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OCTAD_COLUMNS,
        OCTAD_TEXT_HASH,
        OUT_DIR,
        PLACEMENT_COLUMNS,
        PLACEMENT_TEXT_HASH,
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
    from derive_long_k23oct import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OCTAD_COLUMNS,
        OCTAD_TEXT_HASH,
        OUT_DIR,
        PLACEMENT_COLUMNS,
        PLACEMENT_TEXT_HASH,
        STATUS,
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


def validate_long_k23oct() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23oct_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23oct seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23oct cert mismatch")
    for filename, key in {
        "placement_rows.csv": "placement_csv",
        "octad_rows.csv": "octad_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23oct {filename} mismatch")
    for key, expected_array in {
        "placement_table": expected["placement_table"],
        "octad_table": expected["octad_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23oct table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23oct matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23oct.report@1":
        raise AssertionError("long_k23oct report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23oct report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23oct all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23oct checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23oct report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23oct report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("placement_rows.csv", PLACEMENT_COLUMNS, 24),
        ("octad_rows.csv", OCTAD_COLUMNS, 8),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23oct {filename} shape mismatch")

    assert_locked_hash(
        "placement rows",
        hashlib.sha256(digest_text(PLACEMENT_COLUMNS, csv_rows["placement_rows.csv"]).encode("ascii")).hexdigest(),
        PLACEMENT_TEXT_HASH,
    )
    assert_locked_hash(
        "octad rows",
        hashlib.sha256(digest_text(OCTAD_COLUMNS, csv_rows["octad_rows.csv"]).encode("ascii")).hexdigest(),
        OCTAD_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["placement_matrix", "target_octad_vector", "support_edge_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23_certified_flag": 1,
        "w24_code_certified_flag": 1,
        "delete_contract_input_certified_flag": 1,
        "compatible_record_count": 70,
        "nontrivial_compatible_record_count": 15,
        "unique_nonzero_support_count": 1,
        "selected_record_id": 0,
        "selected_extra_removed": 5,
        "selected_effective_contract_count": 3,
        "remaining_column_count": 24,
        "pair_family_code": 0,
        "assignment_edge_count": 24,
        "support_edge_count": 8,
        "h6_balance_flag": 1,
        "mapped_coordinate_count": 24,
        "mapped_coordinate_bijection_flag": 1,
        "target_octad_weight": 8,
        "target_octad_in_w24_code_flag": 1,
        "mapped_support_matches_target_octad_flag": 1,
        "rowspace_equality_certified_flag": 0,
        "full_morphism_certified_flag": 0,
        "m23_module_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23oct observable {name} mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23oct.manifest@1":
        raise AssertionError("long_k23oct manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23oct manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23oct manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23oct index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23oct index report sha mismatch")

    return {
        "schema": "long.k23oct.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23oct(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
