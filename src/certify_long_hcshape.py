from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_hcshape import (
        DERIVE_SCRIPT,
        DOMAIN_COLUMNS,
        DOMAIN_TEXT_HASH,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        TARGET_COLUMNS,
        TARGET_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_hcshape import (
        DERIVE_SCRIPT,
        DOMAIN_COLUMNS,
        DOMAIN_TEXT_HASH,
        INDEX_PATH,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        TARGET_COLUMNS,
        TARGET_TEXT_HASH,
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


def validate_long_hcshape() -> dict[str, Any]:
    expected = build_payloads()
    seam_payload = load_json(OUT_DIR / "seam.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)
    skeleton = np.load(OUT_DIR / "projection_skeleton.npz", allow_pickle=False)

    if seam_payload != expected["seam"]:
        raise AssertionError("long_hcshape seam mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_hcshape cert mismatch")
    for filename, key in {
        "domain.csv": "domain_csv",
        "target.csv": "target_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_hcshape {filename} mismatch")
    for key, expected_array in {
        "domain_table": expected["domain_table"],
        "target_table": expected["target_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_hcshape table mismatch: {key}")
    if not np.array_equal(np.asarray(skeleton["skeleton"]), expected["skeleton"]):
        raise AssertionError("long_hcshape skeleton mismatch")

    if report.get("schema") != "long.hcshape.report@1":
        raise AssertionError("long_hcshape report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_hcshape report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_hcshape all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_hcshape checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcshape report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_hcshape report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("domain.csv", DOMAIN_COLUMNS, 56),
        ("target.csv", TARGET_COLUMNS, 33),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_hcshape {filename} shape mismatch")

    assert_locked_hash(
        "domain",
        hashlib.sha256(digest_text(DOMAIN_COLUMNS, csv_rows["domain.csv"]).encode("ascii")).hexdigest(),
        DOMAIN_TEXT_HASH,
    )
    assert_locked_hash(
        "target",
        hashlib.sha256(digest_text(TARGET_COLUMNS, csv_rows["target.csv"]).encode("ascii")).hexdigest(),
        TARGET_TEXT_HASH,
    )
    assert_locked_hash(
        "observable",
        hashlib.sha256(digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")).hexdigest(),
        OBS_TEXT_HASH,
    )

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    exact_counts = {
        "a8_dimension": 8,
        "h6_dimension": 6,
        "hidden_dimension": 2,
        "lambda3_a8_dimension": 56,
        "visible_triple_count": 20,
        "copy0_twoform_count": 15,
        "copy1_twoform_count": 15,
        "hidden_pair_h6_count": 6,
        "foam16_dimension": 16,
        "foam33_dimension": 33,
        "forced_twoform_rank": 30,
        "residual_domain_dimension": 26,
        "required_projection_rank": 33,
        "required_kernel_dimension": 23,
        "residual_scalar_rank_needed": 3,
        "skeleton_rank": 30,
        "skeleton_kernel_dimension": 26,
        "rank_gap_to_target": 3,
        "e33_basis_binding_materialized_flag": 0,
        "scalar_functionals_materialized_flag": 0,
        "focused_hcshape_closed_flag": 1,
        "complete_goal_claim_flag": 0,
    }
    for name, expected_value in exact_counts.items():
        if obs.get(OBS_CODES[name]) != expected_value:
            raise AssertionError(f"long_hcshape observable {name} mismatch")

    inputs = report.get("inputs", {})
    for label, expected_entry in expected["report"]["inputs"].items():
        if "sha256" in expected_entry:
            assert_file_hash(inputs.get(label, {}), ROOT / expected_entry["path"], label)
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if manifest.get("schema") != "long.hcshape.manifest@1":
        raise AssertionError("long_hcshape manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcshape manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_hcshape manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("long_hcshape missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_hcshape proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_hcshape proof obligation index status mismatch")
    index_without_hash = {key: value for key, value in index.items() if key != "registry_sha256"}
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.hcshape.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "skeleton_sha256": witness.get("skeleton_sha256"),
            "remaining_projection_data": witness.get("remaining_projection_data"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_hcshape(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
