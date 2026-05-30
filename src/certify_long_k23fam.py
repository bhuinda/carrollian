from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23fam import (
        CANDIDATE_COLUMNS,
        CANDIDATE_TEXT_HASH,
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
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
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23fam import (
        CANDIDATE_COLUMNS,
        CANDIDATE_TEXT_HASH,
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
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
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIRST_CANDIDATE = (0, 0, 8, 163, 56, 151, 6, 32, 33, 27, 0, 0, 1009706, 79106, 147893, 0)
EXPECTED_BEST_CANDIDATE = (10, 1, 8, 163, 58, 153, 6, 32, 33, 27, 0, 0, 958530, 82435, 134753, 0)
EXPECTED_LAST_CANDIDATE = (23, 17, 14, 893, 59, 154, 10, 32, 33, 27, 0, 0, 1012847, 82837, 138671, 0)


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


def candidate_tuple(row: dict[str, str]) -> tuple[int, ...]:
    return (
        int(row["candidate_id"]),
        int(row["fixed_target_row"]),
        int(row["changed_unit_column"]),
        int(row["changed_unit_relation"]),
        int(row["appended_column"]),
        int(row["appended_relation"]),
        int(row["appended_target_row"]),
        int(row["unit_repaired_base_rank"]),
        int(row["repaired_projection_rank"]),
        int(row["kernel_dimension"]),
        int(row["quotient_residual_total"]),
        int(row["unit_residual_total"]),
        int(row["product_residual_total"]),
        int(row["product_residual_min"]),
        int(row["product_residual_max"]),
        int(row["product_preserved_generator_count"]),
    )


def validate_long_k23fam() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23fam_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23fam seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23fam cert mismatch")
    for filename, key in {
        "candidate_rows.csv": "candidate_csv",
        "generator_rows.csv": "generator_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23fam {filename} mismatch")
    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "generator_table": expected["generator_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23fam table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23fam matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23fam.report@1":
        raise AssertionError("long_k23fam report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23fam report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23fam all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23fam checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23fam report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23fam report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("candidate_rows.csv", CANDIDATE_COLUMNS, 24),
        ("generator_rows.csv", GENERATOR_COLUMNS, 216),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23fam {filename} shape mismatch")

    assert_locked_hash(
        "candidate rows",
        hashlib.sha256(digest_text(CANDIDATE_COLUMNS, csv_rows["candidate_rows.csv"]).encode("ascii")).hexdigest(),
        CANDIDATE_TEXT_HASH,
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
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["candidate_table", "generator_table", "candidate_product_residual_vector", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23cl_certified_flag": 1,
        "long_k23unit_certified_flag": 1,
        "long_k23tgt_certified_flag": 1,
        "long_k23proj_certified_flag": 1,
        "long_k23rh_certified_flag": 1,
        "closure_dimension": 60,
        "target_dimension": 33,
        "fixed_target_row_count": 3,
        "old_unit_column_count": 2,
        "appended_column_count": 4,
        "raw_candidate_count": 792,
        "rank_restoring_candidate_count": 24,
        "generator_count": 9,
        "candidate_generator_row_count": 216,
        "quotient_residual_total": 0,
        "unit_residual_total": 0,
        "product_residual_total_min": 958530,
        "product_residual_total_max": 1014453,
        "best_candidate_id": 10,
        "best_candidate_product_residual_total": 958530,
        "product_preserved_candidate_count": 0,
        "product_obstructed_candidate_count": 24,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23fam observable {name} mismatch")

    candidates = csv_rows["candidate_rows.csv"]
    if candidate_tuple(candidates[0]) != EXPECTED_FIRST_CANDIDATE:
        raise AssertionError("long_k23fam first candidate mismatch")
    if candidate_tuple(candidates[10]) != EXPECTED_BEST_CANDIDATE:
        raise AssertionError("long_k23fam best candidate mismatch")
    if candidate_tuple(candidates[-1]) != EXPECTED_LAST_CANDIDATE:
        raise AssertionError("long_k23fam last candidate mismatch")
    if any(int(row["product_preserved_flag"]) for row in csv_rows["generator_rows.csv"]):
        raise AssertionError("long_k23fam unexpected preserved generator")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23fam index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23fam.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23fam(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
