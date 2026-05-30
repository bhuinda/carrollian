from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23act import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        MISMATCH_COLUMNS,
        MISMATCH_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PRIME,
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
    from derive_long_k23act import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        MISMATCH_COLUMNS,
        MISMATCH_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PRIME,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_GENERATOR_INTERSECTIONS = {
    0: (41, 8, 41, 8, 15, 15),
    1: (40, 7, 40, 7, 16, 16),
    2: (39, 6, 39, 6, 17, 17),
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


def validate_long_k23act() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23act_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23act seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23act cert mismatch")
    for filename, key in {
        "generator_lift_rows.csv": "generator_csv",
        "mismatch_rows.csv": "mismatch_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23act {filename} mismatch")
    for key, expected_array in {
        "generator_table": expected["generator_table"],
        "mismatch_table": expected["mismatch_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23act table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23act matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23act.report@1":
        raise AssertionError("long_k23act report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23act report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23act all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23act checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23act report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23act report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("generator_lift_rows.csv", GENERATOR_COLUMNS, 3),
        ("mismatch_rows.csv", MISMATCH_COLUMNS, 48),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23act {filename} shape mismatch")

    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_lift_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "mismatch rows",
        hashlib.sha256(digest_text(MISMATCH_COLUMNS, csv_rows["mismatch_rows.csv"]).encode("ascii")).hexdigest(),
        MISMATCH_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "frame_lift_mod",
            "generator_permutations",
            "action_column_permutations",
            "transformed_frame_lifts",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23syz_certified_flag": 1,
        "long_k23stab_certified_flag": 1,
        "prime_field": PRIME,
        "support_row_count": 56,
        "frame_coordinate_count": 24,
        "active_support_row_count": 23,
        "inactive_support_row_count": 33,
        "generator_count": 3,
        "plain_preserving_generator_count": 0,
        "signed_preserving_generator_count": 0,
        "pm_signed_preserving_generator_count": 0,
        "support_preserving_generator_count": 0,
        "total_exact_row_intersection_count": 120,
        "total_exact_active_row_intersection_count": 21,
        "total_support_row_intersection_count": 120,
        "total_support_active_row_intersection_count": 21,
        "total_missing_exact_row_count": 48,
        "total_missing_support_row_count": 48,
        "row_permutation_lift_exists_for_all_generators_flag": 0,
        "row_sign_lift_exists_for_all_generators_flag": 0,
        "support_pattern_lift_exists_for_all_generators_flag": 0,
        "m23_design_action_certified_flag": 1,
        "support_binding_row_action_obstructed_flag": 1,
        "general_prime_linear_lift_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23act observable {name} mismatch")

    generator_rows = rows_from_table(np.asarray(tables["generator_table"]), GENERATOR_COLUMNS)
    for row in generator_rows:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_GENERATOR_INTERSECTIONS[generator_id]
        actual_tuple = (
            int(row["exact_row_intersection_count"]),
            int(row["exact_active_row_intersection_count"]),
            int(row["support_row_intersection_count"]),
            int(row["support_active_row_intersection_count"]),
            int(row["missing_exact_row_count"]),
            int(row["missing_support_row_count"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23act generator {generator_id} intersection mismatch")
        if any(
            int(row[column]) != 0
            for column in [
                "plain_row_multiset_preserved_flag",
                "signed_row_multiset_preserved_flag",
                "pm_signed_row_multiset_preserved_flag",
                "support_row_multiset_preserved_flag",
            ]
        ):
            raise AssertionError(f"long_k23act generator {generator_id} unexpectedly preserves rows")
    if np.asarray(matrices["transformed_frame_lifts"]).shape != (3, 56, 24):
        raise AssertionError("long_k23act transformed lift shape mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23act.manifest@1":
        raise AssertionError("long_k23act manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23act manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23act manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23act index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23act index report sha mismatch")

    return {
        "schema": "long.k23act.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23act(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
