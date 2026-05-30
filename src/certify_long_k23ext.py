from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23ext import (
        DERIVE_SCRIPT,
        FINGERPRINT_COLUMNS,
        FINGERPRINT_TEXT_HASH,
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
    from derive_long_k23ext import (
        DERIVE_SCRIPT,
        FINGERPRINT_COLUMNS,
        FINGERPRINT_TEXT_HASH,
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


EXPECTED_RESIDUAL_ROWS = {
    0: (126508, 2964, 56, 0, 1),
    1: (127386, 2964, 56, 0, 1),
    2: (119638, 2962, 56, 0, 1),
    3: (126830, 2992, 56, 0, 1),
    4: (85096, 2722, 56, 0, 1),
    5: (84139, 2590, 56, 0, 1),
    6: (87136, 2404, 56, 0, 1),
    7: (98299, 2602, 56, 0, 1),
    8: (81629, 2402, 54, 0, 1),
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


def validate_long_k23ext() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23ext_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23ext seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23ext cert mismatch")
    for filename, key in {
        "relation_fingerprints.csv": "fingerprints_csv",
        "extension_obstructions.csv": "obstructions_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23ext {filename} mismatch")
    for key, expected_array in {
        "fingerprint_table": expected["fingerprint_table"],
        "obstruction_table": expected["obstruction_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23ext table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23ext matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23ext.report@1":
        raise AssertionError("long_k23ext report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23ext report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23ext all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23ext checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23ext report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23ext report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("relation_fingerprints.csv", FINGERPRINT_COLUMNS, 60),
        ("extension_obstructions.csv", OBSTRUCTION_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23ext {filename} shape mismatch")

    assert_locked_hash(
        "relation fingerprints",
        hashlib.sha256(digest_text(FINGERPRINT_COLUMNS, csv_rows["relation_fingerprints.csv"]).encode("ascii")).hexdigest(),
        FINGERPRINT_TEXT_HASH,
    )
    assert_locked_hash(
        "extension obstructions",
        hashlib.sha256(digest_text(OBSTRUCTION_COLUMNS, csv_rows["extension_obstructions.csv"]).encode("ascii")).hexdigest(),
        OBSTRUCTION_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "fingerprint_table",
            "obstruction_table",
            "old_slice_residual_vector",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23cl_certified_flag": 1,
        "long_k23rh_certified_flag": 1,
        "closure_support_row_count": 60,
        "added_relation_count": 4,
        "generator_count": 9,
        "old_source_dimension": 56,
        "closure_dimension": 60,
        "old_pair_count": 3136,
        "old_target_count": 56,
        "old_slice_residual_nonzero_total": 936661,
        "old_slice_residual_nonzero_min": 81629,
        "old_slice_residual_nonzero_max": 127386,
        "old_slice_failed_generator_count": 9,
        "old_pair_residual_column_min": 2402,
        "old_pair_residual_column_max": 2992,
        "old_target_residual_row_min": 54,
        "old_target_residual_row_max": 56,
        "cross_boundary_required_generator_count": 9,
        "fingerprint_class_count": 20,
        "added_relation_fingerprint_class_count": 4,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23ext observable {name} mismatch")

    for row in csv_rows["extension_obstructions.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_RESIDUAL_ROWS[generator_id]
        actual_tuple = (
            int(row["old_target_old_pair_residual_nonzero_count"]),
            int(row["old_pair_columns_with_residual"]),
            int(row["old_target_rows_with_residual"]),
            int(row["block_only_extension_possible_flag"]),
            int(row["cross_boundary_mixing_required_flag"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23ext obstruction row mismatch: {generator_id}")

    added_classes = {
        int(row["fingerprint_class_id"])
        for row in csv_rows["relation_fingerprints.csv"]
        if int(row["added_by_leak_flag"]) == 1
    }
    if len(added_classes) != 4:
        raise AssertionError("long_k23ext added relation fingerprint class mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23ext index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23ext.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23ext(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
