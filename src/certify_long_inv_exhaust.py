from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_inv_exhaust import (
        C985_FINAL_REPORT,
        COVER_COLUMNS,
        COVER_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_H16_REPORT,
        LONG_MEASURE_REPORT,
        LONG_PATHS_REPORT,
        LONG_THM_BOUNDARY,
        LONG_THM_REPORT,
        LONG_THM_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_inv_exhaust import (
        C985_FINAL_REPORT,
        COVER_COLUMNS,
        COVER_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_H16_REPORT,
        LONG_MEASURE_REPORT,
        LONG_PATHS_REPORT,
        LONG_THM_BOUNDARY,
        LONG_THM_REPORT,
        LONG_THM_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OBS_TEXT_HASH,
        OUT_DIR,
        STATUS,
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


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_inv_exhaust() -> dict[str, Any]:
    expected = build_payloads()
    inv_payload = load_json(OUT_DIR / "inv_exhaust.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if inv_payload != expected["inv_exhaust"]:
        raise AssertionError("long_inv_exhaust JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_inv_exhaust cert mismatch")
    for filename, key in {"cover.csv": "cover_csv", "obs.csv": "obs_csv"}.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_inv_exhaust {filename} mismatch")
    for key, expected_array in {
        "cover_table": expected["cover_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_inv_exhaust table mismatch: {key}")

    if report.get("schema") != "long.inv_exhaust.report@1":
        raise AssertionError("long_inv_exhaust report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_inv_exhaust report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_inv_exhaust all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_inv_exhaust checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_inv_exhaust report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_inv_exhaust report hash mismatch")

    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in [
        ("cover.csv", COVER_COLUMNS, 5),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_inv_exhaust {filename} shape mismatch")

    if tuple(np.asarray(tables["cover_table"]).shape) != (5, len(COVER_COLUMNS)):
        raise AssertionError("long_inv_exhaust cover table shape mismatch")
    if tuple(np.asarray(tables["observable_table"]).shape) != (
        len(OBS_CODES),
        len(OBS_COLUMNS),
    ):
        raise AssertionError("long_inv_exhaust observable table shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "source_boundary_count": 5,
        "cover_row_count": 5,
        "covered_boundary_count": 5,
        "active_goal_closed_count": 5,
        "absolute_claim_count": 0,
        "input_certified_count": 5,
        "input_report_count": 5,
        "current_inventory_exhaustive_flag": 1,
        "absolute_exhaustiveness_claim_flag": 0,
        "active_frontier_remaining_count": 0,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_inv_exhaust observable {key} mismatch")

    if hashlib.sha256(
        digest_text(COVER_COLUMNS, csv_rows["cover.csv"]).encode("ascii")
    ).hexdigest() != COVER_TEXT_HASH:
        raise AssertionError("long_inv_exhaust cover hash mismatch")
    if hashlib.sha256(
        digest_text(OBS_COLUMNS, csv_rows["obs.csv"]).encode("ascii")
    ).hexdigest() != OBS_TEXT_HASH:
        raise AssertionError("long_inv_exhaust observable hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_thm_report": LONG_THM_REPORT,
        "long_thm_boundary": LONG_THM_BOUNDARY,
        "long_thm_tables": LONG_THM_TABLES,
        "c985_final_report": C985_FINAL_REPORT,
        "long_paths_report": LONG_PATHS_REPORT,
        "long_measure_report": LONG_MEASURE_REPORT,
        "long_h16_report": LONG_H16_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.inv_exhaust.manifest@1":
        raise AssertionError("long_inv_exhaust manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_inv_exhaust manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_inv_exhaust manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_inv_exhaust missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_inv_exhaust proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_inv_exhaust proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.inv_exhaust.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "certificate_code_map": witness.get("certificate_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_inv_exhaust(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
