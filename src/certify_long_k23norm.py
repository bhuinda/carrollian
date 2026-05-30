from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23norm import (
        DERIVE_SCRIPT,
        EQUATION_COLUMNS,
        EQUATION_TEXT_HASH,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        NORM_COLUMNS,
        NORM_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PARAM_COLUMNS,
        PARAM_TEXT_HASH,
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
    from derive_long_k23norm import (
        DERIVE_SCRIPT,
        EQUATION_COLUMNS,
        EQUATION_TEXT_HASH,
        LIMIT_COLUMNS,
        LIMIT_TEXT_HASH,
        MATRIX_SHA256,
        NORM_COLUMNS,
        NORM_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PARAM_COLUMNS,
        PARAM_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_PARAM = (0, 0, 512, 256, 3329, 2, 3, 2, 10, 4, 128, 800, 1632, 768, 32, 1)
EXPECTED_NORM = (0, 3, 3, 0, 512, 56, 56, 56, 32, 3, 4, 5376, 7168, 1568, 3232, 1, 1, 0)
EXPECTED_FIRST_EQUATION = (0, 0, 5376, 5376, 1, 0)
EXPECTED_LAST_EQUATION = (4, 4, 3808, 3808, 1, 0)
EXPECTED_FIRST_LIMIT = (0, 0, 1, 1, 0)
EXPECTED_LAST_LIMIT = (4, 4, 1, 1, 0)


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


def int_tuple(row: dict[str, str], columns: list[str]) -> tuple[int, ...]:
    return tuple(int(row[column]) for column in columns)


def validate_long_k23norm() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23norm_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23norm seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23norm cert mismatch")
    for filename, key in {
        "parameter_rows.csv": "param_csv",
        "normalization_rows.csv": "norm_csv",
        "equation_rows.csv": "equation_csv",
        "limit_rows.csv": "limit_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23norm {filename} mismatch")
    for key, expected_array in {
        "param_table": expected["param_table"],
        "norm_table": expected["norm_table"],
        "equation_table": expected["equation_table"],
        "limit_table": expected["limit_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23norm table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23norm matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23norm.report@1":
        raise AssertionError("long_k23norm report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23norm report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23norm all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23norm checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23norm report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23norm report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("parameter_rows.csv", PARAM_COLUMNS, 1),
        ("normalization_rows.csv", NORM_COLUMNS, 1),
        ("equation_rows.csv", EQUATION_COLUMNS, 5),
        ("limit_rows.csv", LIMIT_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23norm {filename} shape mismatch")

    assert_locked_hash(
        "parameter rows",
        hashlib.sha256(digest_text(PARAM_COLUMNS, csv_rows["parameter_rows.csv"]).encode("ascii")).hexdigest(),
        PARAM_TEXT_HASH,
    )
    assert_locked_hash(
        "normalization rows",
        hashlib.sha256(digest_text(NORM_COLUMNS, csv_rows["normalization_rows.csv"]).encode("ascii")).hexdigest(),
        NORM_TEXT_HASH,
    )
    assert_locked_hash(
        "equation rows",
        hashlib.sha256(digest_text(EQUATION_COLUMNS, csv_rows["equation_rows.csv"]).encode("ascii")).hexdigest(),
        EQUATION_TEXT_HASH,
    )
    assert_locked_hash(
        "limit rows",
        hashlib.sha256(digest_text(LIMIT_COLUMNS, csv_rows["limit_rows.csv"]).encode("ascii")).hexdigest(),
        LIMIT_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in ["param_table", "norm_table", "equation_table", "limit_table", "observable_vector"]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    if int_tuple(csv_rows["parameter_rows.csv"][0], PARAM_COLUMNS) != EXPECTED_PARAM:
        raise AssertionError("long_k23norm parameter row mismatch")
    if int_tuple(csv_rows["normalization_rows.csv"][0], NORM_COLUMNS) != EXPECTED_NORM:
        raise AssertionError("long_k23norm normalization row mismatch")
    equation_rows = csv_rows["equation_rows.csv"]
    if int_tuple(equation_rows[0], EQUATION_COLUMNS) != EXPECTED_FIRST_EQUATION:
        raise AssertionError("long_k23norm first equation row mismatch")
    if int_tuple(equation_rows[-1], EQUATION_COLUMNS) != EXPECTED_LAST_EQUATION:
        raise AssertionError("long_k23norm last equation row mismatch")
    if any(int(row["equality_flag"]) != 1 for row in equation_rows):
        raise AssertionError("long_k23norm equation mismatch")
    if any(int(row["improvement_claim_flag"]) != 0 for row in equation_rows):
        raise AssertionError("long_k23norm equation overclaim")

    limit_rows = csv_rows["limit_rows.csv"]
    if int_tuple(limit_rows[0], LIMIT_COLUMNS) != EXPECTED_FIRST_LIMIT:
        raise AssertionError("long_k23norm first limit row mismatch")
    if int_tuple(limit_rows[-1], LIMIT_COLUMNS) != EXPECTED_LAST_LIMIT:
        raise AssertionError("long_k23norm last limit row mismatch")
    if any(int(row["open_flag"]) != 1 for row in limit_rows):
        raise AssertionError("long_k23norm limit openness mismatch")
    if any(int(row["overclaim_flag"]) != 0 for row in limit_rows):
        raise AssertionError("long_k23norm limit overclaim")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "input_report_count": 1,
        "certified_input_count": 1,
        "selected_candidate_id": 3,
        "selected_potential_code": 3,
        "selected_baseline_spec_code": 0,
        "bench_candidate_count": 6,
        "parameter_row_count": 1,
        "official_parameter_source_count": 1,
        "parameter_set_code": 512,
        "required_rbg_strength_bits": 128,
        "encapsulation_key_bytes": 800,
        "decapsulation_key_bytes": 1632,
        "ciphertext_bytes": 768,
        "shared_secret_bytes": 32,
        "baseline_public_exchange_bytes": 1568,
        "baseline_total_material_bytes": 3232,
        "digest_bytes": 32,
        "public_digest_columns": 3,
        "opening_digest_columns": 4,
        "internal_operation_count": 56,
        "internal_transcript_rows": 56,
        "internal_verification_path_count": 56,
        "internal_public_digest_bytes": 5376,
        "internal_opening_digest_bytes": 7168,
        "comparison_delta_public_bytes": 3808,
        "public_ratio_numerator": 24,
        "public_ratio_denominator": 7,
        "equation_row_count": 5,
        "equation_pass_count": 5,
        "external_numeric_baseline_count": 1,
        "improvement_claim_count": 0,
        "limit_row_count": 5,
        "open_limit_count": 5,
        "overclaim_count": 0,
        "normalization_surface_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23norm observable {name} mismatch")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23norm index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23norm.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23norm(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
