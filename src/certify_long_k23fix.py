from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23fix import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OBSTRUCTION_COLUMNS,
        OBSTRUCTION_TEXT_HASH,
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
    from derive_long_k23fix import (
        DERIVE_SCRIPT,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OBSTRUCTION_COLUMNS,
        OBSTRUCTION_TEXT_HASH,
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


EXPECTED_OBSTRUCTION_ROWS = {
    0: (126508, 9144, 124563, 12, 40272, 124441, 12, 0, 5, 886, 155, 160, 1, 0),
    1: (127386, 8488, 125386, 12, 40272, 125169, 12, 0, 5, 886, 155, 160, 500001, 0),
    2: (119638, 8602, 117552, 12, 40272, 117378, 12, 0, 5, 886, 155, 160, 11, 0),
    3: (126830, 10086, 124628, 12, 40272, 123233, 12, 0, 5, 886, 155, 160, 1, 0),
    4: (85096, 9144, 83864, 12, 40272, 83822, 12, 0, 5, 886, 155, 160, 3, 0),
    5: (84139, 9144, 83428, 12, 40272, 83382, 12, 2, 5, 886, 157, 160, 999992, 0),
    6: (87136, 9144, 86697, 12, 40272, 86655, 12, 0, 5, 886, 155, 160, 1000002, 0),
    7: (98299, 9144, 97149, 12, 40272, 97107, 12, 0, 5, 886, 155, 160, 1000000, 0),
    8: (81629, 9144, 80990, 12, 40272, 80954, 12, 0, 5, 886, 155, 160, 1, 0),
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


def validate_long_k23fix() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23fix_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23fix seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23fix cert mismatch")
    for filename, key in {
        "fixed_obstructions.csv": "obstructions_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23fix {filename} mismatch")
    for key, expected_array in {
        "obstruction_table": expected["obstruction_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23fix table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23fix matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23fix.report@1":
        raise AssertionError("long_k23fix report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23fix report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23fix all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23fix checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23fix report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23fix report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("fixed_obstructions.csv", OBSTRUCTION_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23fix {filename} shape mismatch")

    assert_locked_hash(
        "fixed obstructions",
        hashlib.sha256(digest_text(OBSTRUCTION_COLUMNS, csv_rows["fixed_obstructions.csv"]).encode("ascii")).hexdigest(),
        OBSTRUCTION_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["obstruction_table", "observable_vector", "exact_impossible_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23cl_certified_flag": 1,
        "long_k23ext_certified_flag": 1,
        "long_k23rh_certified_flag": 1,
        "generator_count": 9,
        "old_dimension": 56,
        "new_dimension": 4,
        "closure_dimension": 60,
        "old_slice_equation_count": 175616,
        "target_residual_nonzero_total": 936661,
        "linear_impossible_total": 924257,
        "linear_impossible_min": 80990,
        "linear_impossible_max": 125386,
        "exact_impossible_total": 922141,
        "exact_impossible_min": 80954,
        "exact_impossible_max": 125169,
        "failed_generator_count": 9,
        "fixed_old_extension_obstructed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23fix observable {name} mismatch")

    for row in csv_rows["fixed_obstructions.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_OBSTRUCTION_ROWS[generator_id]
        actual_tuple = (
            int(row["target_residual_nonzero_count"]),
            int(row["linear_support_row_count"]),
            int(row["linear_impossible_row_count"]),
            int(row["quadratic_target_row_count"]),
            int(row["exact_support_row_count"]),
            int(row["exact_impossible_row_count"]),
            int(row["first_impossible_target_row"]),
            int(row["first_impossible_left_row"]),
            int(row["first_impossible_right_row"]),
            int(row["first_impossible_target_relation"]),
            int(row["first_impossible_left_relation"]),
            int(row["first_impossible_right_relation"]),
            int(row["first_impossible_required_value"]),
            int(row["fixed_old_extension_possible_flag"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23fix obstruction row mismatch: {generator_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23fix index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23fix.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23fix(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
