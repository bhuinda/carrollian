from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23rh import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PIVOT_COLUMNS,
        PIVOT_TEXT_HASH,
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
    from derive_long_k23rh import (
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PIVOT_COLUMNS,
        PIVOT_TEXT_HASH,
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
    0: (33, 52, 798, 787, 56, 0, 0),
    1: (33, 52, 785, 769, 56, 0, 0),
    2: (33, 52, 737, 729, 56, 0, 0),
    3: (33, 52, 836, 822, 56, 0, 0),
    4: (33, 16, 437, 401, 56, 0, 0),
    5: (33, 16, 442, 408, 56, 0, 0),
    6: (33, 16, 515, 482, 56, 0, 0),
    7: (33, 16, 560, 526, 56, 0, 0),
    8: (33, 16, 398, 364, 56, 0, 0),
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


def validate_long_k23rh() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23rh_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23rh seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23rh cert mismatch")
    for filename, key in {
        "pivot_rows.csv": "pivot_csv",
        "generator_rows.csv": "generator_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23rh {filename} mismatch")
    for key, expected_array in {
        "pivot_table": expected["pivot_table"],
        "generator_table": expected["generator_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23rh table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23rh matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23rh.report@1":
        raise AssertionError("long_k23rh report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23rh report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23rh all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23rh checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23rh report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23rh report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("pivot_rows.csv", PIVOT_COLUMNS, 33),
        ("generator_rows.csv", GENERATOR_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23rh {filename} shape mismatch")

    assert_locked_hash(
        "pivot rows",
        hashlib.sha256(digest_text(PIVOT_COLUMNS, csv_rows["pivot_rows.csv"]).encode("ascii")).hexdigest(),
        PIVOT_TEXT_HASH,
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
        for key in [
            "projection_matrix",
            "prime_kernel",
            "right_inverse",
            "split_basis",
            "split_basis_inverse",
            "r_foam_matrices",
            "r_hc_lifts",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23pi_certified_flag": 1,
        "long_hcfoam_certified_flag": 1,
        "field_prime": 1000003,
        "support_dimension": 56,
        "quotient_dimension": 33,
        "kernel_dimension": 23,
        "projection_rank": 33,
        "right_inverse_column_count": 33,
        "right_inverse_nonzero_count": 343,
        "right_inverse_residual_nonzero_count": 0,
        "split_basis_rank": 56,
        "split_basis_inverse_residual_nonzero_count": 0,
        "generator_count": 9,
        "source_lift_generator_count": 9,
        "source_lift_rank_sum": 504,
        "source_lift_nonzero_total": 5508,
        "source_lift_nonidentity_total": 5288,
        "target_nonidentity_generator_count": 9,
        "intertwiner_residual_nonzero_total": 0,
        "kernel_identity_residual_nonzero_total": 0,
        "r_hc_materialized_flag": 1,
        "candidate_projection_flag": 1,
        "final_pi_accepted_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23rh observable {name} mismatch")

    for row in csv_rows["generator_rows.csv"]:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_GENERATOR_ROWS[generator_id]
        actual_tuple = (
            int(row["target_nonzero_count"]),
            int(row["target_nonidentity_count"]),
            int(row["source_lift_nonzero_count"]),
            int(row["source_lift_nonidentity_count"]),
            int(row["source_lift_rank"]),
            int(row["intertwiner_residual_nonzero_count"]),
            int(row["kernel_identity_residual_nonzero_count"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23rh generator row mismatch: {generator_id}")

    required_index_row = {
        "id": THEOREM_ID,
        "manifest": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/manifest.json",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "report_sha256": report["certificate_sha256"],
        "status": STATUS,
    }
    if required_index_row not in index.get("obligations", []):
        raise AssertionError("long_k23rh index row missing")

    assert_file_hash(manifest["inputs"]["derive_script"], DERIVE_SCRIPT, "derive script")
    assert_file_hash(manifest["inputs"]["validator"], VALIDATOR_SCRIPT, "validator script")

    return {
        "schema": "long.k23rh.verification@1",
        "status": "PASS",
        "report": f"data/invariants/d20/proof_obligations/{THEOREM_ID}/report.json",
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_k23rh(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
