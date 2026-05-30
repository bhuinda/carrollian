from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23poly import (
        DERIVE_SCRIPT,
        FINGERPRINT_COLUMNS,
        FINGERPRINT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        WORD_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23poly import (
        DERIVE_SCRIPT,
        FINGERPRINT_COLUMNS,
        FINGERPRINT_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        WORD_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_PRODUCT_PRESERVED_WORDS = (
    (0, 0, -1, -1),
    (10, 2, 0, 0),
    (20, 2, 1, 1),
    (30, 2, 2, 2),
    (40, 2, 3, 3),
    (50, 2, 4, 4),
    (60, 2, 5, 5),
    (70, 2, 6, 6),
    (80, 2, 7, 7),
    (90, 2, 8, 8),
)


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


def preserved_word_tuple(row: dict[str, str]) -> tuple[int, int, int, int]:
    return (
        int(row["word_id"]),
        int(row["word_length"]),
        int(row["first_generator_id"]),
        int(row["second_generator_id"]),
    )


def validate_long_k23poly() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23poly_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23poly seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23poly cert mismatch")
    for filename, key in {
        "word_rows.csv": "word_csv",
        "fingerprint_rows.csv": "fingerprint_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23poly {filename} mismatch")
    for key, expected_array in {
        "word_table": expected["word_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23poly table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23poly matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23poly.report@1":
        raise AssertionError("long_k23poly report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23poly report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23poly all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23poly checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23poly report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23poly report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("word_rows.csv", WORD_COLUMNS, 91),
        ("fingerprint_rows.csv", FINGERPRINT_COLUMNS, 182),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23poly {filename} shape mismatch")

    assert_locked_hash(
        "word rows",
        hashlib.sha256(digest_text(WORD_COLUMNS, csv_rows["word_rows.csv"]).encode("ascii")).hexdigest(),
        WORD_TEXT_HASH,
    )
    assert_locked_hash(
        "fingerprint rows",
        hashlib.sha256(
            digest_text(FINGERPRINT_COLUMNS, csv_rows["fingerprint_rows.csv"]).encode("ascii")
        ).hexdigest(),
        FINGERPRINT_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "generator_lifts",
            "target_generators",
            "word_table",
            "word_product_residual_vector",
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
        "long_k23unit_certified_flag": 1,
        "long_k23rh_certified_flag": 1,
        "long_k23fam_certified_flag": 1,
        "best_candidate_id": 10,
        "closure_dimension": 60,
        "target_dimension": 33,
        "generator_count": 9,
        "word_depth": 2,
        "word_count": 91,
        "identity_word_count": 1,
        "length_one_word_count": 9,
        "length_two_word_count": 81,
        "fingerprint_row_count": 182,
        "quotient_residual_total": 0,
        "unit_residual_total": 0,
        "identity_product_residual": 0,
        "length_one_product_preserved_count": 0,
        "length_two_product_preserved_count": 9,
        "nonidentity_product_preserved_count": 9,
        "square_word_count": 9,
        "square_return_word_count": 9,
        "offdiagonal_length_two_word_count": 72,
        "offdiagonal_product_preserved_count": 0,
        "unique_lift_fingerprint_count": 56,
        "unique_target_fingerprint_count": 56,
        "word_product_residual_min": 0,
        "word_product_residual_max": 142733,
        "nonidentity_product_residual_min": 0,
        "nonidentity_product_residual_max": 142733,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23poly observable {name} mismatch")

    preserved_words = tuple(
        preserved_word_tuple(row)
        for row in csv_rows["word_rows.csv"]
        if int(row["product_preserved_flag"])
    )
    if preserved_words != EXPECTED_PRODUCT_PRESERVED_WORDS:
        raise AssertionError("long_k23poly preserved word profile mismatch")

    fingerprints = csv_rows["fingerprint_rows.csv"]
    identity_lift = fingerprints[0]["sha256"]
    identity_target = fingerprints[1]["sha256"]
    by_word_role = {
        (int(row["word_id"]), int(row["matrix_role_code"])): row["sha256"]
        for row in fingerprints
    }
    for word_id, _length, _first, _second in EXPECTED_PRODUCT_PRESERVED_WORDS:
        if by_word_role[(word_id, 0)] != identity_lift:
            raise AssertionError("long_k23poly preserved lift fingerprint is not identity")
        if by_word_role[(word_id, 1)] != identity_target:
            raise AssertionError("long_k23poly preserved target fingerprint is not identity")

    if any(
        int(row["word_length"]) == 1 and int(row["product_preserved_flag"])
        for row in csv_rows["word_rows.csv"]
    ):
        raise AssertionError("long_k23poly unexpected generator product preservation")
    if any(
        int(row["word_length"]) == 2
        and int(row["first_generator_id"]) != int(row["second_generator_id"])
        and int(row["product_preserved_flag"])
        for row in csv_rows["word_rows.csv"]
    ):
        raise AssertionError("long_k23poly unexpected off-diagonal product preservation")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23poly index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23poly.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23poly(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
