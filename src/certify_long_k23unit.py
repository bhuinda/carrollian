from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23unit import (
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
        UNIT_COLUMNS,
        UNIT_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23unit import (
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
        UNIT_COLUMNS,
        UNIT_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_UNIT_ROWS = {
    0: (8, 163, 1),
    1: (14, 893, 1),
}
EXPECTED_GENERATOR_ROWS = {
    0: (33, 7, 1000001, 5, 1, 0, 0),
    1: (33, 7, 999999, 4, 1, 0, 0),
    2: (33, 7, 1000001, 5, 1, 0, 0),
    3: (33, 6, 0, 6, 1000002, 0, 0),
    4: (33, 2, 999999, 6, 1000001, 0, 0),
    5: (33, 2, 999997, 6, 1000001, 0, 0),
    6: (33, 1, 1000001, 6, 1000001, 0, 0),
    7: (33, 3, 999995, 6, 1000001, 0, 0),
    8: (33, 2, 999999, 10, 1000001, 0, 0),
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


def validate_long_k23unit() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23unit_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23unit seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23unit cert mismatch")
    for filename, key in {
        "unit_rows.csv": "unit_csv",
        "generator_rows.csv": "generator_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23unit {filename} mismatch")
    for key, expected_array in {
        "unit_table": expected["unit_table"],
        "generator_table": expected["generator_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23unit table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23unit matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23unit.report@1":
        raise AssertionError("long_k23unit report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23unit report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23unit all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23unit checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23unit report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23unit report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("unit_rows.csv", UNIT_COLUMNS, 2),
        ("generator_rows.csv", GENERATOR_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23unit {filename} shape mismatch")

    assert_locked_hash(
        "unit rows",
        hashlib.sha256(digest_text(UNIT_COLUMNS, csv_rows["unit_rows.csv"]).encode("ascii")).hexdigest(),
        UNIT_TEXT_HASH,
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
        for key in ["unit_vector", "projected_unit_vector", "generator_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23cl_certified_flag": 1,
        "long_k23fix_certified_flag": 1,
        "long_k23rh_certified_flag": 1,
        "closure_dimension": 60,
        "projection_rank": 33,
        "target_dimension": 33,
        "generator_count": 9,
        "unit_system_rank": 60,
        "unit_system_inconsistent_count": 0,
        "unit_free_dimension": 0,
        "unit_support_count": 2,
        "unit_left_residual_nonzero_count": 0,
        "unit_right_residual_nonzero_count": 0,
        "projected_unit_support_count": 4,
        "r_foam_rank_sum": 297,
        "unit_projection_fixed_generator_count": 0,
        "unit_projection_moved_generator_count": 9,
        "automorphism_obstructed_generator_count": 9,
        "closure60_quotient_automorphism_obstructed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23unit observable {name} mismatch")

    for row in csv_rows["unit_rows.csv"]:
        unit_row_id = int(row["unit_row_id"])
        expected_tuple = EXPECTED_UNIT_ROWS[unit_row_id]
        actual_tuple = (
            int(row["closure_row_id"]),
            int(row["relation_id"]),
            int(row["coefficient_mod"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23unit unit row mismatch: {unit_row_id}")
    for row in csv_rows["generator_rows.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_GENERATOR_ROWS[generator_id]
        actual_tuple = (
            int(row["r_foam_rank"]),
            int(row["projected_unit_residual_nonzero_count"]),
            int(row["projected_unit_residual_sum_mod_p"]),
            int(row["first_residual_row"]),
            int(row["first_residual_value"]),
            int(row["unit_projection_fixed_flag"]),
            int(row["quotient_action_automorphism_possible_flag"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23unit generator row mismatch: {generator_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23unit index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23unit.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23unit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
