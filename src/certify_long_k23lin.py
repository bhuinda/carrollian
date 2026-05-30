from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23lin import (
        COEFF_COLUMNS,
        COEFF_TEXT_HASH,
        COMPLEMENT_COLUMNS,
        COMPLEMENT_TEXT_HASH,
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
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
        gf_rank_mod,
        matrix_order,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23lin import (
        COEFF_COLUMNS,
        COEFF_TEXT_HASH,
        COMPLEMENT_COLUMNS,
        COMPLEMENT_TEXT_HASH,
        DERIVE_SCRIPT,
        GENERATOR_COLUMNS,
        GENERATOR_TEXT_HASH,
        MATRIX_SHA256,
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
        gf_rank_mod,
        matrix_order,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


EXPECTED_GENERATOR_ROWS = {
    0: (2, 56, 0, 218, 218, 0, 0, 0, 2),
    1: (15, 56, 0, 235, 198, 0, 0, 0, 15),
    2: (3, 56, 0, 193, 217, 0, 0, 0, 3),
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


def validate_long_k23lin() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(OUT_DIR.parent / "index.json")
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23lin_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23lin seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23lin cert mismatch")
    for filename, key in {
        "complement_rows.csv": "complement_csv",
        "generator_rows.csv": "generator_csv",
        "coefficient_histogram.csv": "coeff_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23lin {filename} mismatch")
    for key, expected_array in {
        "complement_table": expected["complement_table"],
        "generator_table": expected["generator_table"],
        "coeff_table": expected["coeff_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23lin table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23lin matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23lin.report@1":
        raise AssertionError("long_k23lin report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23lin report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23lin all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23lin checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23lin report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23lin report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("complement_rows.csv", COMPLEMENT_COLUMNS, 33),
        ("generator_rows.csv", GENERATOR_COLUMNS, 3),
        ("coefficient_histogram.csv", COEFF_COLUMNS, 44),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23lin {filename} shape mismatch")

    assert_locked_hash(
        "complement rows",
        hashlib.sha256(digest_text(COMPLEMENT_COLUMNS, csv_rows["complement_rows.csv"]).encode("ascii")).hexdigest(),
        COMPLEMENT_TEXT_HASH,
    )
    assert_locked_hash(
        "generator rows",
        hashlib.sha256(digest_text(GENERATOR_COLUMNS, csv_rows["generator_rows.csv"]).encode("ascii")).hexdigest(),
        GENERATOR_TEXT_HASH,
    )
    assert_locked_hash(
        "coefficient rows",
        hashlib.sha256(digest_text(COEFF_COLUMNS, csv_rows["coefficient_histogram.csv"]).encode("ascii")).hexdigest(),
        COEFF_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "prime_kernel",
            "frame_lift_mod",
            "kernel_complement",
            "basis_change",
            "basis_change_inverse",
            "generator_permutations",
            "k23_action_matrices",
            "frame_permutation_matrices",
            "support_intertwiners",
            "support_intertwiner_inverses",
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
        "long_k23act_certified_flag": 1,
        "prime_field": PRIME,
        "support_row_count": 56,
        "frame_coordinate_count": 24,
        "k23_basis_row_count": 23,
        "frame_lift_syzygy_rank": 23,
        "kernel_complement_dimension": 33,
        "kernel_complement_rank": 33,
        "kernel_complement_residual_nonzero_count": 0,
        "basis_change_rank": 56,
        "basis_change_inverse_residual_nonzero_count": 0,
        "generator_count": 3,
        "linear_lift_generator_count": 3,
        "invertible_support_operator_count": 3,
        "k23_intertwiner_residual_nonzero_count": 0,
        "frame_intertwiner_residual_nonzero_count": 0,
        "inverse_residual_nonzero_count": 0,
        "support_operator_rank_sum": 168,
        "support_operator_nullity_sum": 0,
        "row_action_obstruction_preserved_flag": 1,
        "prime_linear_lift_certified_flag": 1,
        "m23_k23_module_action_certified_flag": 1,
        "unique_lift_proven_flag": 0,
        "row_permutation_lift_proven_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23lin observable {name} mismatch")

    generator_rows = rows_from_table(np.asarray(tables["generator_table"]), GENERATOR_COLUMNS)
    for row in generator_rows:
        generator_id = int(row["generator_id"])
        expected_tuple = EXPECTED_GENERATOR_ROWS[generator_id]
        actual_tuple = (
            int(row["action_order"]),
            int(row["support_operator_rank"]),
            int(row["support_operator_nullity"]),
            int(row["support_operator_nonzero_count"]),
            int(row["support_inverse_nonzero_count"]),
            int(row["k23_residual_nonzero_count"]),
            int(row["frame_residual_nonzero_count"]),
            int(row["inverse_residual_nonzero_count"]),
            int(row["support_operator_order"]),
        )
        if actual_tuple != expected_tuple:
            raise AssertionError(f"long_k23lin generator {generator_id} summary mismatch")
    kernel = np.asarray(matrices["prime_kernel"], dtype=np.int64)
    frame_lift = np.asarray(matrices["frame_lift_mod"], dtype=np.int64)
    complement = np.asarray(matrices["kernel_complement"], dtype=np.int64)
    basis_change = np.asarray(matrices["basis_change"], dtype=np.int64)
    basis_change_inverse = np.asarray(matrices["basis_change_inverse"], dtype=np.int64)
    if gf_rank_mod(complement) != 33 or int(np.count_nonzero((kernel @ complement) % PRIME)) != 0:
        raise AssertionError("long_k23lin complement check mismatch")
    if gf_rank_mod(basis_change) != 56:
        raise AssertionError("long_k23lin basis change is not full rank")
    if int(np.count_nonzero((basis_change @ basis_change_inverse - np.eye(56, dtype=np.int64)) % PRIME)) != 0:
        raise AssertionError("long_k23lin basis inverse mismatch")
    support_ops = np.asarray(matrices["support_intertwiners"], dtype=np.int64)
    inverse_ops = np.asarray(matrices["support_intertwiner_inverses"], dtype=np.int64)
    action_ops = np.asarray(matrices["k23_action_matrices"], dtype=np.int64)
    frame_ops = np.asarray(matrices["frame_permutation_matrices"], dtype=np.int64)
    for generator_id in range(3):
        support = support_ops[generator_id]
        if gf_rank_mod(support) != 56:
            raise AssertionError(f"long_k23lin support operator {generator_id} not invertible")
        if matrix_order(support) != EXPECTED_GENERATOR_ROWS[generator_id][-1]:
            raise AssertionError(f"long_k23lin support operator {generator_id} order mismatch")
        if int(np.count_nonzero((kernel @ support - action_ops[generator_id] @ kernel) % PRIME)) != 0:
            raise AssertionError(f"long_k23lin K residual mismatch for generator {generator_id}")
        if int(np.count_nonzero((support @ frame_lift - frame_lift @ frame_ops[generator_id]) % PRIME)) != 0:
            raise AssertionError(f"long_k23lin frame residual mismatch for generator {generator_id}")
        if int(np.count_nonzero((support @ inverse_ops[generator_id] - np.eye(56, dtype=np.int64)) % PRIME)) != 0:
            raise AssertionError(f"long_k23lin inverse residual mismatch for generator {generator_id}")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23lin.manifest@1":
        raise AssertionError("long_k23lin manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23lin manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23lin manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23lin index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23lin index report sha mismatch")

    return {
        "schema": "long.k23lin.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23lin(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
