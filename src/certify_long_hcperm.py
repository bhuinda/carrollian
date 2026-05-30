from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcperm import (
        COMBO_COLUMNS,
        COMBO_TEXT_HASH,
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
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
    from derive_long_hcperm import (
        COMBO_COLUMNS,
        COMBO_TEXT_HASH,
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
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
    keys = ["selected_projection", "best_projection", "r_foam"]
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


def validate_long_hcperm() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "lift_obstruction_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcperm seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcperm cert mismatch")
    for filename, key in {
        "combo_rows.csv": "combo_csv",
        "generator_rows.csv": "generator_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcperm {filename} mismatch")
    for key, expected_array in {
        "combo_table": expected["combo_table"],
        "generator_table": expected["generator_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcperm table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_hcperm matrix payload mismatch: {key}")

    if report.get("schema") != "long.hcperm.report@1":
        raise AssertionError("long_hcperm report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcperm report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcperm all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcperm checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcperm report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcperm report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("combo_rows.csv", COMBO_COLUMNS, 256),
        ("generator_rows.csv", GENERATOR_COLUMNS, 2304),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcperm {filename} shape mismatch")

    assert_locked_hash(
        "combo rows",
        hashlib.sha256(digest_text(COMBO_COLUMNS, csv_rows["combo_rows.csv"]).encode("ascii")).hexdigest(),
        COMBO_TEXT_HASH,
    )
    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
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
        "target_dimension": 33,
        "generator_count": 9,
        "feature_row_count": 24,
        "rank33_combo_count": 256,
        "perfect_combo_count": 0,
        "selected_combo_id": 0,
        "selected_total_hit_count": 92,
        "selected_total_miss_count": 412,
        "selected_perfect_generator_count": 0,
        "best_combo_id": 251,
        "best_total_hit_count": 190,
        "best_total_miss_count": 314,
        "best_perfect_generator_count": 0,
        "best_worst_generator_miss_count": 50,
        "signed_column_lift_obstruction_flag": 1,
        "sourced_c2_surface_present_flag": 1,
        "nonmonomial_lift_still_open_flag": 1,
        "alternate_feature_family_still_open_flag": 1,
        "full_intertwiner_claim_flag": 0,
        "focused_hcperm_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcperm observable {name} mismatch")

    combo_rows = csv_rows["combo_rows.csv"]
    if sum(int(row["best_flag"]) for row in combo_rows) != 1:
        raise AssertionError("long_hcperm best flag count mismatch")
    if sum(int(row["selected_hcgrade_flag"]) for row in combo_rows) != 1:
        raise AssertionError("long_hcperm selected flag count mismatch")
    if any(int(row["perfect_generator_count"]) for row in combo_rows):
        raise AssertionError("long_hcperm unexpected perfect completion")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcperm.manifest@1":
        raise AssertionError("long_hcperm manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcperm manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcperm manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("long_hcperm missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcperm proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcperm proof obligation index status mismatch")
    index_without_hash = {key: value for key, value in index.items() if key != "registry_sha256"}
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcperm.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "matrix_sha256": witness.get("matrix_sha256"),
            "boundary": witness.get("boundary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcperm(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
