from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23pi import (
        DERIVE_SCRIPT,
        FOAM_COLUMNS,
        FOAM_TEXT_HASH,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        KERNEL_COLUMNS,
        KERNEL_TEXT_HASH,
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
    from derive_long_k23pi import (
        DERIVE_SCRIPT,
        FOAM_COLUMNS,
        FOAM_TEXT_HASH,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        KERNEL_COLUMNS,
        KERNEL_TEXT_HASH,
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


EXPECTED_GENERATOR_ROWS = {
    0: (0, 0, 286, 33, 0, 33, 1),
    1: (0, 0, 284, 33, 0, 33, 1),
    2: (0, 0, 281, 33, 0, 33, 1),
}
EXPECTED_FOAM_ROWS = {
    0: (33, 52, 0),
    1: (33, 52, 0),
    2: (33, 52, 0),
    3: (33, 52, 0),
    4: (33, 16, 0),
    5: (33, 16, 0),
    6: (33, 16, 0),
    7: (33, 16, 0),
    8: (33, 16, 0),
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


def validate_long_k23pi() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23pi_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23pi seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23pi cert mismatch")
    for filename, key in {
        "kernel_rows.csv": "kernel_csv",
        "generator_rows.csv": "generator_csv",
        "foam_rows.csv": "foam_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23pi {filename} mismatch")
    for key, expected_array in {
        "kernel_table": expected["kernel_table"],
        "generator_table": expected["generator_table"],
        "foam_table": expected["foam_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23pi table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23pi matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23pi.report@1":
        raise AssertionError("long_k23pi report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23pi report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23pi all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23pi checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23pi report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23pi report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("kernel_rows.csv", KERNEL_COLUMNS, 23),
        ("generator_rows.csv", GENERATOR_COLUMNS, 3),
        ("foam_rows.csv", FOAM_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23pi {filename} shape mismatch")

    assert_locked_hash(
        "kernel rows",
        hashlib.sha256(digest_text(KERNEL_COLUMNS, csv_rows["kernel_rows.csv"]).encode("ascii")).hexdigest(),
        KERNEL_TEXT_HASH,
    )
    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "foam rows",
        hashlib.sha256(digest_text(FOAM_COLUMNS, csv_rows["foam_rows.csv"]).encode("ascii")).hexdigest(),
        FOAM_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "projection_matrix",
            "prime_kernel",
            "support_intertwiners",
            "induced_quotient_matrices",
            "r_foam_matrices",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_hcgrade_certified_flag": 1,
        "long_k23lin_certified_flag": 1,
        "long_hcfoam_certified_flag": 1,
        "field_prime": 1000003,
        "support_dimension": 56,
        "projection_rank": 33,
        "projection_kernel_dimension": 23,
        "k23_rank": 23,
        "projection_times_k23_transpose_nonzero_count": 0,
        "projection_k23_rank_sum": 56,
        "k23_equals_projection_kernel_flag": 1,
        "generator_count": 3,
        "kernel_intertwiner_residual_nonzero_total": 0,
        "projection_transpose_fixed_generator_count": 3,
        "projection_transpose_fixed_residual_nonzero_total": 0,
        "projection_direct_rowspace_residual_nonzero_total": 851,
        "induced_identity_generator_count": 3,
        "induced_quotient_rank_sum": 99,
        "r_foam_generator_count": 9,
        "r_foam_nonidentity_generator_count": 9,
        "k23_lifts_match_r_foam_target_flag": 0,
        "r_hc_materialized_flag": 0,
        "full_intertwiner_claim_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23pi observable {name} mismatch")

    for row in csv_rows["kernel_rows.csv"]:
        if int(row["projection_residual_nonzero_count"]) != 0:
            raise AssertionError("long_k23pi kernel residual mismatch")
    for row in csv_rows["generator_rows.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_GENERATOR_ROWS[generator_id]
        actual_tuple = (
            int(row["kernel_intertwiner_residual_nonzero_count"]),
            int(row["projection_transpose_fixed_residual_nonzero_count"]),
            int(row["projection_direct_rowspace_residual_nonzero_count"]),
            int(row["induced_quotient_nonzero_count"]),
            int(row["induced_quotient_nonidentity_count"]),
            int(row["induced_quotient_rank"]),
            int(row["quotient_identity_flag"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23pi generator row mismatch: {generator_id}")
    for row in csv_rows["foam_rows.csv"]:
        generator_id = int(row["target_generator_id"])
        expected_tuple = EXPECTED_FOAM_ROWS[generator_id]
        actual_tuple = (
            int(row["r_foam_nonzero_count"]),
            int(row["r_foam_nonidentity_count"]),
            int(row["r_foam_identity_flag"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23pi foam row mismatch: {generator_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23pi index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23pi.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23pi(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
