from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcscalar import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PI_CANDIDATE_SHA256,
        SCALAR_COLUMNS,
        SCALAR_MATRIX_SHA256,
        SCALAR_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rank_mod,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_hcscalar import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        PI_CANDIDATE_SHA256,
        SCALAR_COLUMNS,
        SCALAR_MATRIX_SHA256,
        SCALAR_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rank_mod,
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


def validate_long_hcscalar() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    projection = np.load(OUT_DIR / "projection_candidate.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcscalar seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcscalar cert mismatch")
    for filename, key in {
        "scalar_rows.csv": "scalar_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcscalar {filename} mismatch")
    for key, expected_array in {
        "scalar_table": expected["scalar_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcscalar table mismatch: {key}")
    if not np.array_equal(np.asarray(projection["pi_candidate"]), expected["candidate"]):
        raise AssertionError("long_hcscalar projection candidate mismatch")
    if not np.array_equal(np.asarray(projection["scalar_matrix"]), expected["scalar_matrix"]):
        raise AssertionError("long_hcscalar scalar matrix mismatch")

    if report.get("schema") != "long.hcscalar.report@1":
        raise AssertionError("long_hcscalar report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcscalar report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcscalar all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcscalar checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcscalar report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcscalar report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("scalar_rows.csv", SCALAR_COLUMNS, 3),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcscalar {filename} shape mismatch")

    assert_locked_hash(
        "scalar",
        hashlib.sha256(digest_text(SCALAR_COLUMNS, csv_rows["scalar_rows.csv"]).encode("ascii")).hexdigest(),
        SCALAR_TEXT_HASH,
    )
    assert_locked_hash(
        "observable",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )
    assert_locked_hash("projection candidate", sha_array(np.asarray(projection["pi_candidate"])), PI_CANDIDATE_SHA256)
    assert_locked_hash("scalar matrix", sha_array(np.asarray(projection["scalar_matrix"])), SCALAR_MATRIX_SHA256)

    candidate = np.asarray(projection["pi_candidate"], dtype=np.int64)
    scalar_matrix = np.asarray(projection["scalar_matrix"], dtype=np.int64)
    if candidate.shape != (33, 56) or scalar_matrix.shape != (3, 56):
        raise AssertionError("long_hcscalar matrix shape mismatch")
    if rank_mod(candidate) != 33:
        raise AssertionError("long_hcscalar candidate rank mismatch")
    if 56 - rank_mod(candidate) != 23:
        raise AssertionError("long_hcscalar candidate kernel mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "h6_label_count": 6,
        "active_object_count": 2,
        "active_object_0_h6_index": 1,
        "active_object_1_h6_index": 5,
        "source_domain_dimension": 56,
        "target_dimension": 33,
        "skeleton_rank": 30,
        "skeleton_kernel_dimension": 26,
        "residual_domain_dimension": 26,
        "scalar_row_count": 3,
        "scalar_rank_addition": 3,
        "candidate_projection_rank": 33,
        "candidate_kernel_dimension": 23,
        "visible_volume_support_count": 20,
        "active_hidden_support_count": 2,
        "forced_twoform_block_preserved_flag": 1,
        "selector_scalar_coordinate_flag": 1,
        "e33_basis_binding_materialized_flag": 0,
        "r_hc_materialized_flag": 0,
        "full_intertwiner_claim_flag": 0,
        "focused_hcscalar_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcscalar observable {name} mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcscalar.manifest@1":
        raise AssertionError("long_hcscalar manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcscalar manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcscalar manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("long_hcscalar missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcscalar proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcscalar proof obligation index status mismatch")
    index_without_hash = {key: value for key, value in index.items() if key != "registry_sha256"}
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcscalar.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "scalar_details": witness.get("scalar_details"),
            "pi_candidate_sha256": witness.get("pi_candidate_sha256"),
            "scalar_matrix_sha256": witness.get("scalar_matrix_sha256"),
            "boundary": witness.get("boundary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcscalar(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
