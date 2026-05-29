from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import rows_from_table
    from .derive_long_suppind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_IND_REPORT,
        LONG_IND_RULE,
        LONG_IND_TABLES,
        LONG_LINF_REPORT,
        LONG_LINF_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RULE_SUMMARY_COLUMNS,
        RULE_SUMMARY_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import rows_from_table
    from derive_long_suppind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_IND_REPORT,
        LONG_IND_RULE,
        LONG_IND_TABLES,
        LONG_LINF_REPORT,
        LONG_LINF_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RULE_SUMMARY_COLUMNS,
        RULE_SUMMARY_TEXT_HASH,
        STATUS,
        SUPPORT_COLUMNS,
        SUPPORT_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )


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


def validate_long_suppind() -> dict[str, Any]:
    expected = build_payloads()
    suppind_payload = load_json(OUT_DIR / "suppind.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if suppind_payload != expected["suppind"]:
        raise AssertionError("long_suppind suppind JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_suppind cert mismatch")
    for filename, key in {
        "support.csv": "support_csv",
        "rule_summary.csv": "rule_summary_csv",
        "bridge.csv": "bridge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_suppind {filename} mismatch")

    for key, expected_array in {
        "support_table": expected["support_table"],
        "rule_summary_table": expected["rule_summary_table"],
        "bridge_table": expected["bridge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_suppind table mismatch: {key}")

    if report.get("schema") != "long.suppind.report@1":
        raise AssertionError("long_suppind report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_suppind report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_suppind all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_suppind checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_suppind report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_suppind report hash mismatch")

    csv_shapes = [
        ("support.csv", SUPPORT_COLUMNS, 16_128),
        ("rule_summary.csv", RULE_SUMMARY_COLUMNS, 8),
        ("bridge.csv", BRIDGE_COLUMNS, 1),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_suppind {filename} shape mismatch")

    table_shapes = {
        "support_table": (16_128, len(SUPPORT_COLUMNS)),
        "rule_summary_table": (8, len(RULE_SUMMARY_COLUMNS)),
        "bridge_table": (1, len(BRIDGE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_suppind {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "induction_start": 16,
        "source_end_sample_count": 127,
        "lift_horizon": 128,
        "support_state_count": 16_128,
        "rule_summary_count": 8,
        "bridge_row_count": 1,
        "lower_gap_nonnegative_count": 16_128,
        "upper_gap_nonnegative_count": 16_128,
        "lower_gap_zero_count": 112,
        "upper_gap_zero_count": 112,
        "support_inside_count": 16_128,
        "target_count_match_count": 16_128,
        "cumulative_certificate_count": 16_128,
        "rule_certificate_count": 8,
        "actual_target_count_min": 1,
        "actual_target_count_max": 3,
        "rule0_state_count": 112,
        "rule4_state_count": 7_448,
        "rule6_state_count": 8_008,
        "input_long_ind_certified": 1,
        "input_long_linf_certified": 1,
        "long_ind_rule_hash_match_flag": 1,
        "current_support_rule_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_suppind observable {key} mismatch")

    if hashlib.sha256(
        digest_text(SUPPORT_COLUMNS, csv_rows["support.csv"]).encode("ascii")
    ).hexdigest() != SUPPORT_TEXT_HASH:
        raise AssertionError("long_suppind support hash mismatch")
    if hashlib.sha256(
        digest_text(
            RULE_SUMMARY_COLUMNS,
            csv_rows["rule_summary.csv"],
        ).encode("ascii")
    ).hexdigest() != RULE_SUMMARY_TEXT_HASH:
        raise AssertionError("long_suppind rule-summary hash mismatch")
    if hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, csv_rows["bridge.csv"]).encode("ascii")
    ).hexdigest() != BRIDGE_TEXT_HASH:
        raise AssertionError("long_suppind bridge hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_ind_report": LONG_IND_REPORT,
        "long_ind_rule": LONG_IND_RULE,
        "long_ind_tables": LONG_IND_TABLES,
        "long_linf_report": LONG_LINF_REPORT,
        "long_linf_tables": LONG_LINF_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.suppind.manifest@1":
        raise AssertionError("long_suppind manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_suppind manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_suppind manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_suppind missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_suppind proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_suppind proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.suppind.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "support": witness.get("support"),
            "rules": witness.get("rules"),
            "bridge": witness.get("bridge"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_suppind(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
