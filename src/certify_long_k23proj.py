from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23proj import (
        DERIVE_SCRIPT,
        EDIT_COLUMNS,
        EDIT_TEXT_HASH,
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
    from derive_long_k23proj import (
        DERIVE_SCRIPT,
        EDIT_COLUMNS,
        EDIT_TEXT_HASH,
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


EXPECTED_EDIT_ROWS = {
    0: (0, 8, 163, 0, 1, 1, 0),
    1: (6, 8, 163, 1, 0, 1000002, 0),
    2: (10, 8, 163, 0, 1000002, 1000002, 0),
    3: (28, 8, 163, 1, 1000002, 1000001, 0),
    4: (32, 8, 163, 1, 0, 1000002, 0),
    5: (6, 56, 151, 0, 1, 1, 1),
}
EXPECTED_GENERATOR_ROWS = {
    0: (0, 0, 145412, 795, 781, 0),
    1: (0, 0, 147893, 845, 826, 0),
    2: (0, 0, 128481, 704, 690, 0),
    3: (0, 0, 145895, 831, 812, 0),
    4: (0, 0, 89018, 455, 413, 0),
    5: (0, 0, 92441, 495, 457, 0),
    6: (0, 0, 79106, 427, 383, 0),
    7: (0, 0, 100645, 521, 484, 0),
    8: (0, 0, 80815, 430, 393, 0),
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


def validate_long_k23proj() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23proj_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23proj seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23proj cert mismatch")
    for filename, key in {
        "projection_edits.csv": "edits_csv",
        "generator_rows.csv": "generator_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23proj {filename} mismatch")
    for key, expected_array in {
        "edit_table": expected["edit_table"],
        "generator_table": expected["generator_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23proj table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23proj matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23proj.report@1":
        raise AssertionError("long_k23proj report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23proj report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23proj all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23proj checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23proj report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23proj report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("projection_edits.csv", EDIT_COLUMNS, 6),
        ("generator_rows.csv", GENERATOR_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23proj {filename} shape mismatch")

    assert_locked_hash(
        "projection edits",
        hashlib.sha256(digest_text(EDIT_COLUMNS, csv_rows["projection_edits.csv"]).encode("ascii")).hexdigest(),
        EDIT_TEXT_HASH,
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
        for key in ["repaired_projection", "repaired_lifts", "generator_table", "observable_vector"]
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
        "long_k23rh_certified_flag": 1,
        "closure_dimension": 60,
        "target_dimension": 33,
        "old_projection_rank": 33,
        "unit_repaired_base_rank": 32,
        "repaired_projection_rank": 33,
        "kernel_dimension": 27,
        "right_inverse_residual_nonzero_count": 0,
        "split_basis_rank": 60,
        "repaired_unit_support_count": 1,
        "repaired_unit_target_row": 0,
        "projection_edit_row_count": 6,
        "quotient_intertwiner_residual_nonzero_total": 0,
        "unit_residual_nonzero_total": 0,
        "product_residual_nonzero_total": 1009706,
        "product_residual_nonzero_min": 79106,
        "product_residual_nonzero_max": 147893,
        "product_preserved_generator_count": 0,
        "product_obstructed_generator_count": 9,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23proj observable {name} mismatch")

    for row in csv_rows["projection_edits.csv"]:
        edit_id = int(row["edit_id"])
        actual_tuple = (
            int(row["target_row_id"]),
            int(row["closure_row_id"]),
            int(row["relation_id"]),
            int(row["old_value"]),
            int(row["new_value"]),
            int(row["delta_mod"]),
            int(row["edit_role_code"]),
        )
        if actual_tuple != EXPECTED_EDIT_ROWS[edit_id]:
            raise AssertionError(f"long_k23proj edit row mismatch: {edit_id}")
    for row in csv_rows["generator_rows.csv"]:
        generator_id = int(row["generator_id"])
        actual_tuple = (
            int(row["quotient_intertwiner_residual_nonzero_count"]),
            int(row["unit_residual_nonzero_count"]),
            int(row["product_residual_nonzero_count"]),
            int(row["lift_nonzero_count"]),
            int(row["lift_nonidentity_count"]),
            int(row["product_preserved_flag"]),
        )
        if actual_tuple != EXPECTED_GENERATOR_ROWS[generator_id]:
            raise AssertionError(f"long_k23proj generator row mismatch: {generator_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23proj index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23proj.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23proj(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
