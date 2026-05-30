from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcsupp import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROFILE_COLUMNS,
        PROFILE_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TABLE_SHA256,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_hcsupp import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PROFILE_COLUMNS,
        PROFILE_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TABLE_SHA256,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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


def sha_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


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


def validate_long_hcsupp() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcsupp seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcsupp cert mismatch")
    for filename, key in {
        "support_rows.csv": "support_csv",
        "profile.csv": "profile_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcsupp {filename} mismatch")
    for key, expected_array in {
        "support_table": expected["support_table"],
        "profile_table": expected["profile_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcsupp table mismatch: {key}")

    if report.get("schema") != "long.hcsupp.report@1":
        raise AssertionError("long_hcsupp report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcsupp report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcsupp all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcsupp checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcsupp report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcsupp report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("support_rows.csv", SUPPORT_COLUMNS, 56),
        ("profile.csv", PROFILE_COLUMNS, 2),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcsupp {filename} shape mismatch")

    assert_locked_hash(
        "support",
        hashlib.sha256(digest_text(SUPPORT_COLUMNS, csv_rows["support_rows.csv"]).encode("ascii")).hexdigest(),
        SUPPORT_TEXT_HASH,
    )
    assert_locked_hash(
        "profile",
        hashlib.sha256(digest_text(PROFILE_COLUMNS, csv_rows["profile.csv"]).encode("ascii")).hexdigest(),
        PROFILE_TEXT_HASH,
    )
    assert_locked_hash(
        "observable",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    assert_locked_hash("support table", sha_array(np.asarray(tables["support_table"])), SUPPORT_TABLE_SHA256)

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "e33_support": 56,
        "e33_positive_count": 28,
        "e33_negative_count": 28,
        "e33_signed_sum": 0,
        "raw_block_profile_count": 2,
        "bplus_block_support": 12,
        "splus_block_support": 44,
        "sector33_profile_support": 56,
        "sector33_public_zero_flag": 1,
        "sector33_q42_nonzero_count": 0,
        "sector33_q12_nonzero_count": 0,
        "sector33_pre_idempotent_support_size": 2,
        "sector33_bplus_local_pre_idempotent": 12,
        "sector33_splus_local_pre_idempotent": 6,
        "e33_reconstruction_bplus_candidate": 3,
        "e33_reconstruction_splus_candidate": 17,
        "abstract_domain_dimension": 56,
        "abstract_visible_count": 20,
        "abstract_twoform_count": 30,
        "abstract_hidden_pair_count": 6,
        "abstract_candidate_rank": 33,
        "abstract_candidate_kernel_dimension": 23,
        "relation_support_table_materialized_flag": 1,
        "relation_to_lambda3_binding_materialized_flag": 0,
        "block_counts_match_abstract_partition_flag": 0,
        "count_only_binding_possible_flag": 0,
        "focused_hcsupp_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcsupp observable {name} mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcsupp.manifest@1":
        raise AssertionError("long_hcsupp manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcsupp manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcsupp manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("long_hcsupp missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcsupp proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcsupp proof obligation index status mismatch")
    index_without_hash = {key: value for key, value in index.items() if key != "registry_sha256"}
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcsupp.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "sector33_local_pre_idempotent_keys": witness.get("sector33_local_pre_idempotent_keys"),
            "support_table_sha256": witness.get("support_table_sha256"),
            "boundary": witness.get("boundary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcsupp(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
