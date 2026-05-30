from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_k23q import (
        CANDIDATE_COLUMNS,
        CANDIDATE_TEXT_HASH,
        COMPONENT_COLUMNS,
        COMPONENT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEIGHT_COLUMNS,
        WEIGHT_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_k23q import (
        CANDIDATE_COLUMNS,
        CANDIDATE_TEXT_HASH,
        COMPONENT_COLUMNS,
        COMPONENT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        MATRIX_SHA256,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEIGHT_COLUMNS,
        WEIGHT_TEXT_HASH,
        build_payloads,
        digest_text,
        matrix_payload_hash,
        self_hash,
    )
    from derive_long_raw import rows_from_table


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


def validate_long_k23q() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    matrices = np.load(OUT_DIR / "k23q_matrices.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_k23q seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_k23q cert mismatch")
    for filename, key in {
        "component_rows.csv": "component_csv",
        "pair_rows.csv": "pair_csv",
        "candidate_rows.csv": "candidate_csv",
        "weight_rows.csv": "weight_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_k23q {filename} mismatch")
    for key, expected_array in {
        "component_table": expected["component_table"],
        "pair_table": expected["pair_table"],
        "candidate_table": expected["candidate_table"],
        "weight_table": expected["weight_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_k23q table mismatch: {key}")
    for key, expected_array in expected["matrix_payload"].items():
        if not np.array_equal(np.asarray(matrices[key]), expected_array):
            raise AssertionError(f"long_k23q matrix payload mismatch: {key}")

    if report.get("schema") != "long.k23q.report@1":
        raise AssertionError("long_k23q report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_k23q report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_k23q all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_k23q checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23q report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_k23q report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("component_rows.csv", COMPONENT_COLUMNS, 37),
        ("pair_rows.csv", PAIR_COLUMNS, 19),
        ("candidate_rows.csv", CANDIDATE_COLUMNS, 560),
        ("weight_rows.csv", WEIGHT_COLUMNS, 25),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_k23q {filename} shape mismatch")

    assert_locked_hash(
        "component rows",
        hashlib.sha256(digest_text(COMPONENT_COLUMNS, csv_rows["component_rows.csv"]).encode("ascii")).hexdigest(),
        COMPONENT_TEXT_HASH,
    )
    assert_locked_hash(
        "pair rows",
        hashlib.sha256(digest_text(PAIR_COLUMNS, csv_rows["pair_rows.csv"]).encode("ascii")).hexdigest(),
        PAIR_TEXT_HASH,
    )
    assert_locked_hash(
        "candidate rows",
        hashlib.sha256(digest_text(CANDIDATE_COLUMNS, csv_rows["candidate_rows.csv"]).encode("ascii")).hexdigest(),
        CANDIDATE_TEXT_HASH,
    )
    assert_locked_hash(
        "weight rows",
        hashlib.sha256(digest_text(WEIGHT_COLUMNS, csv_rows["weight_rows.csv"]).encode("ascii")).hexdigest(),
        WEIGHT_TEXT_HASH,
    )
    assert_locked_hash(
        "observable rows",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    matrix_payload = {
        key: np.asarray(matrices[key])
        for key in [
            "support_normalized_kernel",
            "component_projection",
            "component_activity",
            "quotient_rref",
            "rowspace_weight_histogram",
            "observable_vector",
        ]
    }
    assert_locked_hash("matrix payload", matrix_payload_hash(matrix_payload), MATRIX_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "long_k23_certified_flag": 1,
        "long_k23bin_certified_flag": 1,
        "w24_code_certified_flag": 1,
        "support_input_row_count": 56,
        "support_normalized_rank": 23,
        "two_support_relation_count": 19,
        "quotient_component_count": 37,
        "component_size_1_count": 26,
        "component_size_2_count": 7,
        "component_size_4_count": 4,
        "active_component_count": 21,
        "pad_eligible_component_count": 16,
        "candidate_family_count": 560,
        "quotient_length": 24,
        "quotient_rank": 4,
        "rowspace_word_count": 16,
        "min_nonzero_weight": 2,
        "forbidden_weight_class_count": 5,
        "forbidden_word_count": 12,
        "coordinate_permutation_obstruction_flag": 1,
        "candidate_w24_subcode_count": 0,
        "pair_collapse_family_closed_flag": 1,
        "non_pair_quotient_open_flag": 1,
        "k23_equality_certified_flag": 0,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_k23q observable {name} mismatch")

    weight_hist = {
        int(row["weight"]): int(row["rowspace_word_count"])
        for row in rows_from_table(np.asarray(tables["weight_table"]), WEIGHT_COLUMNS)
    }
    expected_hist = {0: 1, 2: 1, 6: 2, 8: 1, 10: 3, 12: 1, 14: 5, 16: 1, 18: 1}
    for weight in range(25):
        if weight_hist.get(weight, 0) != expected_hist.get(weight, 0):
            raise AssertionError(f"long_k23q weight histogram mismatch at {weight}")

    if np.asarray(matrices["support_normalized_kernel"]).shape != (23, 56):
        raise AssertionError("long_k23q support-normalized kernel shape mismatch")
    if int(np.asarray(matrices["support_normalized_kernel"]).sum()) != 90:
        raise AssertionError("long_k23q support-normalized kernel nonzero count mismatch")
    if np.asarray(matrices["component_projection"]).shape != (23, 37):
        raise AssertionError("long_k23q component projection shape mismatch")
    if int(np.asarray(matrices["component_projection"]).sum()) != 52:
        raise AssertionError("long_k23q component projection nonzero count mismatch")
    component_activity = np.asarray(matrices["component_activity"], dtype=np.int64)
    if int((component_activity > 0).sum()) != 21 or int((component_activity == 0).sum()) != 16:
        raise AssertionError("long_k23q component activity count mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.k23q.manifest@1":
        raise AssertionError("long_k23q manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23q manifest report sha mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_k23q manifest self hash mismatch")
    matching = [
        row
        for row in index.get("obligations", [])
        if isinstance(row, dict) and row.get("id") == THEOREM_ID
    ]
    if len(matching) != 1:
        raise AssertionError("long_k23q index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_k23q index report sha mismatch")

    return {
        "schema": "long.k23q.verification@1",
        "status": "PASS",
        "report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace("\\", "/"),
        "certificate_sha256": report.get("certificate_sha256"),
        "summary": report.get("witness", {}).get("summary", {}),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_k23q(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
