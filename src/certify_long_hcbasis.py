from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcbasis import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        COORD_COLUMNS,
        COORD_TEXT_HASH,
        DERIVE_SCRIPT,
        EXPANSION_COLUMNS,
        EXPANSION_TEXT_HASH,
        INDEX_PATH,
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
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_hcbasis import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        COORD_COLUMNS,
        COORD_TEXT_HASH,
        DERIVE_SCRIPT,
        EXPANSION_COLUMNS,
        EXPANSION_TEXT_HASH,
        INDEX_PATH,
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
    keys = ["basis_obj1", "basis_obj5", "sector33_vector", "e33_vector"]
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


def validate_long_hcbasis() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "center_expansion_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcbasis seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcbasis cert mismatch")
    for filename, key in {
        "basis_summary.csv": "basis_csv",
        "center_coordinates.csv": "coord_csv",
        "expansion_rows.csv": "expansion_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcbasis {filename} mismatch")
    for key, expected_array in {
        "basis_table": expected["basis_table"],
        "coord_table": expected["coord_table"],
        "expansion_table": expected["expansion_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcbasis table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_hcbasis matrix payload mismatch: {key}")

    if report.get("schema") != "long.hcbasis.report@1":
        raise AssertionError("long_hcbasis report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcbasis report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcbasis all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcbasis checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcbasis report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcbasis report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("basis_summary.csv", BASIS_COLUMNS, 2),
        ("center_coordinates.csv", COORD_COLUMNS, 35),
        ("expansion_rows.csv", EXPANSION_COLUMNS, 56),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcbasis {filename} shape mismatch")

    assert_locked_hash(
        "basis",
        hashlib.sha256(digest_text(BASIS_COLUMNS, csv_rows["basis_summary.csv"]).encode("ascii")).hexdigest(),
        BASIS_TEXT_HASH,
    )
    assert_locked_hash(
        "coordinates",
        hashlib.sha256(digest_text(COORD_COLUMNS, csv_rows["center_coordinates.csv"]).encode("ascii")).hexdigest(),
        COORD_TEXT_HASH,
    )
    assert_locked_hash(
        "expansion",
        hashlib.sha256(digest_text(EXPANSION_COLUMNS, csv_rows["expansion_rows.csv"]).encode("ascii")).hexdigest(),
        EXPANSION_TEXT_HASH,
    )
    assert_locked_hash(
        "observable",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    assert_locked_hash("matrix payload", matrix_payload_hash(matrices), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "selected_piece_count": 2,
        "selected_object_0": 1,
        "selected_local_pre_idempotent_0": 12,
        "selected_object_1": 5,
        "selected_local_pre_idempotent_1": 6,
        "bplus_closed_loop_relation_count": 16,
        "splus_closed_loop_relation_count": 104,
        "bplus_center_dimension": 13,
        "splus_center_dimension": 22,
        "bplus_local_support_count": 12,
        "splus_local_support_count": 44,
        "total_local_support_count": 56,
        "total_positive_count": 28,
        "total_negative_count": 28,
        "total_signed_sum": 0,
        "bplus_matches_e33_flag": 1,
        "splus_matches_e33_flag": 1,
        "summed_vector_matches_e33_flag": 1,
        "bplus_idempotent_flag": 1,
        "splus_idempotent_flag": 1,
        "summed_sector33_idempotent_flag": 1,
        "center_basis_expansion_materialized_flag": 1,
        "relation_to_lambda3_binding_materialized_flag": 0,
        "pi_foam33_materialized_flag": 0,
        "r_hc_materialized_flag": 0,
        "focused_hcbasis_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcbasis observable {name} mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcbasis.manifest@1":
        raise AssertionError("long_hcbasis manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcbasis manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcbasis manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("long_hcbasis missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcbasis proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcbasis proof obligation index status mismatch")
    index_without_hash = {key: value for key, value in index.items() if key != "registry_sha256"}
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcbasis.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "pieces": witness.get("pieces"),
            "matrix_sha256": witness.get("matrix_sha256"),
            "boundary": witness.get("boundary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcbasis(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
