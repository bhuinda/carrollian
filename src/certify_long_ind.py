from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_ind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LINF_CONE,
        LONG_LINF_LEVEL,
        LONG_LINF_REPORT,
        LONG_LINF_TABLES,
        MARGIN_COLUMNS,
        MARGIN_TEXT_HASH,
        NEGATIVE_CONTROL_COLUMNS,
        NEGATIVE_CONTROL_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RULE_COLUMNS,
        RULE_TEXT_HASH,
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
    from derive_long_ind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_LINF_CONE,
        LONG_LINF_LEVEL,
        LONG_LINF_REPORT,
        LONG_LINF_TABLES,
        MARGIN_COLUMNS,
        MARGIN_TEXT_HASH,
        NEGATIVE_CONTROL_COLUMNS,
        NEGATIVE_CONTROL_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RULE_COLUMNS,
        RULE_TEXT_HASH,
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


def validate_long_ind() -> dict[str, Any]:
    expected = build_payloads()
    ind_payload = load_json(OUT_DIR / "ind.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if ind_payload != expected["ind"]:
        raise AssertionError("long_ind ind JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_ind cert mismatch")
    for filename, key in {
        "rule.csv": "rule_csv",
        "margin.csv": "margin_csv",
        "bridge.csv": "bridge_csv",
        "negative_control.csv": "negative_control_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_ind {filename} mismatch")

    for key, expected_array in {
        "rule_table": expected["rule_table"],
        "margin_table": expected["margin_table"],
        "bridge_table": expected["bridge_table"],
        "negative_control_table": expected["negative_control_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_ind table mismatch: {key}")

    if report.get("schema") != "long.ind.report@1":
        raise AssertionError("long_ind report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_ind report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_ind all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_ind checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ind report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_ind report hash mismatch")

    csv_shapes = [
        ("rule.csv", RULE_COLUMNS, 8),
        ("margin.csv", MARGIN_COLUMNS, 8),
        ("bridge.csv", BRIDGE_COLUMNS, 1),
        ("negative_control.csv", NEGATIVE_CONTROL_COLUMNS, 1),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_ind {filename} shape mismatch")

    table_shapes = {
        "rule_table": (8, len(RULE_COLUMNS)),
        "margin_table": (8, len(MARGIN_COLUMNS)),
        "bridge_table": (1, len(BRIDGE_COLUMNS)),
        "negative_control_table": (1, len(NEGATIVE_CONTROL_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_ind {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "rule_row_count": 8,
        "margin_row_count": 8,
        "bridge_row_count": 1,
        "negative_control_row_count": 1,
        "induction_start": 16,
        "linf_lift_horizon": 128,
        "linf_state_count": 16_383,
        "linf_negative_count": 1,
        "linf_extension_negative_count": 0,
        "margin_nonnegative_count": 8,
        "margin_strict_positive_count": 6,
        "margin_equality_rule_count": 2,
        "negative_control_state_count": 4_095,
        "negative_control_negative_count": 1_115,
        "negative_control_zero_count": 0,
        "first_negative_sample_count": 1,
        "first_negative_sum_value": 2,
        "first_negative_drift_num_mod_1000000007": 1_000_000_002,
        "first_negative_drift_den_mod_1000000007": 26,
        "measure_match_flag": 1,
        "input_long_linf_certified": 1,
        "current_symbolic_margin_flag": 1,
        "current_negative_control_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_ind observable {key} mismatch")

    if hashlib.sha256(
        digest_text(RULE_COLUMNS, csv_rows["rule.csv"]).encode("ascii")
    ).hexdigest() != RULE_TEXT_HASH:
        raise AssertionError("long_ind rule hash mismatch")
    if hashlib.sha256(
        digest_text(MARGIN_COLUMNS, csv_rows["margin.csv"]).encode("ascii")
    ).hexdigest() != MARGIN_TEXT_HASH:
        raise AssertionError("long_ind margin hash mismatch")
    if hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, csv_rows["bridge.csv"]).encode("ascii")
    ).hexdigest() != BRIDGE_TEXT_HASH:
        raise AssertionError("long_ind bridge hash mismatch")
    if hashlib.sha256(
        digest_text(
            NEGATIVE_CONTROL_COLUMNS,
            csv_rows["negative_control.csv"],
        ).encode("ascii")
    ).hexdigest() != NEGATIVE_CONTROL_TEXT_HASH:
        raise AssertionError("long_ind negative-control hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_linf_report": LONG_LINF_REPORT,
        "long_linf_level": LONG_LINF_LEVEL,
        "long_linf_cone": LONG_LINF_CONE,
        "long_linf_tables": LONG_LINF_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.ind.manifest@1":
        raise AssertionError("long_ind manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ind manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_ind manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_ind missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_ind proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_ind proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.ind.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "induction_start": witness.get("induction_start"),
            "rules": witness.get("rules"),
            "linf_bridge": witness.get("linf_bridge"),
            "negative_control": witness.get("negative_control"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_ind(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
