from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23tgt import (
        DERIVE_SCRIPT,
        FIXED_COLUMNS,
        FIXED_TEXT_HASH,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROJECTED_UNIT_COLUMNS,
        PROJECTED_UNIT_TEXT_HASH,
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
    from derive_long_k23tgt import (
        DERIVE_SCRIPT,
        FIXED_COLUMNS,
        FIXED_TEXT_HASH,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROJECTED_UNIT_COLUMNS,
        PROJECTED_UNIT_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_FIXED_ROWS = {
    0: (0, 0, 1, 1),
    1: (1, 1, 1, 1),
    2: (2, 17, 1, 1),
}
EXPECTED_PROJECTED_UNIT_ROWS = {
    0: (0, 0, 1, 0),
    1: (1, 0, 1, 0),
    2: (6, 1, 0, 1),
    3: (10, 1, 0, 1),
    4: (17, 0, 1, 0),
    5: (28, 2, 0, 1),
    6: (32, 1, 0, 1),
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


def validate_long_k23tgt() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23tgt_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23tgt seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23tgt cert mismatch")
    for filename, key in {
        "fixed_basis.csv": "fixed_csv",
        "projected_unit.csv": "projected_unit_csv",
        "generator_rows.csv": "generator_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23tgt {filename} mismatch")
    for key, expected_array in {
        "fixed_table": expected["fixed_table"],
        "projected_unit_table": expected["projected_unit_table"],
        "generator_table": expected["generator_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23tgt table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23tgt matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23tgt.report@1":
        raise AssertionError("long_k23tgt report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23tgt report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23tgt all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23tgt checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23tgt report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23tgt report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("fixed_basis.csv", FIXED_COLUMNS, 3),
        ("projected_unit.csv", PROJECTED_UNIT_COLUMNS, 7),
        ("generator_rows.csv", GENERATOR_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23tgt {filename} shape mismatch")

    assert_locked_hash(
        "fixed rows",
        hashlib.sha256(digest_text(FIXED_COLUMNS, csv_rows["fixed_basis.csv"]).encode("ascii")).hexdigest(),
        FIXED_TEXT_HASH,
    )
    assert_locked_hash(
        "projected unit rows",
        hashlib.sha256(digest_text(PROJECTED_UNIT_COLUMNS, csv_rows["projected_unit.csv"]).encode("ascii")).hexdigest(),
        PROJECTED_UNIT_TEXT_HASH,
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
        for key in ["common_fixed_basis", "projected_unit_vector", "generator_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23unit_certified_flag": 1,
        "long_k23rh_certified_flag": 1,
        "target_dimension": 33,
        "generator_count": 9,
        "stacked_fixed_equation_row_count": 297,
        "stacked_fixed_equation_rank": 30,
        "common_fixed_dimension": 3,
        "common_fixed_basis_row_count": 3,
        "individual_fixed_dimension_min": 17,
        "individual_fixed_dimension_max": 17,
        "r_foam_rank_sum": 297,
        "projected_unit_support_count": 4,
        "projected_unit_common_fixed_coordinate_count": 0,
        "projected_unit_residual_nonzero_total": 37,
        "projected_unit_in_common_fixed_space_flag": 0,
        "target_has_unit_aperture_flag": 1,
        "new_projection_columns_can_repair_flag": 0,
        "old_projection_must_change_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23tgt observable {name} mismatch")

    for row_id, row in enumerate(csv_rows["fixed_basis.csv"]):
        actual_tuple = (
            int(row["basis_id"]),
            int(row["target_row_id"]),
            int(row["coordinate_mod"]),
            int(row["support_count"]),
        )
        if actual_tuple != EXPECTED_FIXED_ROWS[row_id]:
            raise AssertionError(f"long_k23tgt fixed row mismatch: {row_id}")
    for row_id, row in enumerate(csv_rows["projected_unit.csv"]):
        actual_tuple = (
            int(row["target_row_id"]),
            int(row["projected_unit_value"]),
            int(row["common_fixed_basis_row_flag"]),
            int(row["projected_unit_support_flag"]),
        )
        if actual_tuple != EXPECTED_PROJECTED_UNIT_ROWS[row_id]:
            raise AssertionError(f"long_k23tgt projected unit row mismatch: {row_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23tgt index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23tgt.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23tgt(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
