from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_formind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        CHECK_COLUMNS,
        CHECK_TEXT_HASH,
        CLASS_COLUMNS,
        CLASS_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_RECIND_REPORT,
        LONG_RECIND_TABLES,
        LONG_RECIND_TRANSITION,
        LONG_RECIND_TYPE_SUMMARY,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        TERM_COLUMNS,
        TERM_TEXT_HASH,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_formind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        CHECK_COLUMNS,
        CHECK_TEXT_HASH,
        CLASS_COLUMNS,
        CLASS_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_RECIND_REPORT,
        LONG_RECIND_TABLES,
        LONG_RECIND_TRANSITION,
        LONG_RECIND_TYPE_SUMMARY,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        TERM_COLUMNS,
        TERM_TEXT_HASH,
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


def validate_long_formind() -> dict[str, Any]:
    expected = build_payloads()
    formind_payload = load_json(OUT_DIR / "formind.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if formind_payload != expected["formind"]:
        raise AssertionError("long_formind formind JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_formind cert mismatch")
    for filename, key in {
        "class.csv": "class_csv",
        "term.csv": "term_csv",
        "check.csv": "check_csv",
        "bridge.csv": "bridge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_formind {filename} mismatch")

    for key, expected_array in {
        "class_table": expected["class_table"],
        "term_table": expected["term_table"],
        "check_table": expected["check_table"],
        "bridge_table": expected["bridge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_formind table mismatch: {key}")

    if report.get("schema") != "long.formind.report@1":
        raise AssertionError("long_formind report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_formind report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_formind all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_formind checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_formind report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_formind report hash mismatch")

    csv_shapes = [
        ("class.csv", CLASS_COLUMNS, 13),
        ("term.csv", TERM_COLUMNS, 581),
        ("check.csv", CHECK_COLUMNS, 26),
        ("bridge.csv", BRIDGE_COLUMNS, 1),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_formind {filename} shape mismatch")

    table_shapes = {
        "class_table": (13, len(CLASS_COLUMNS)),
        "term_table": (581, len(TERM_COLUMNS)),
        "check_table": (26, len(CHECK_COLUMNS)),
        "bridge_table": (1, len(BRIDGE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_formind {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "probe_start_sample_count": 128,
        "probe_end_sample_count": 256,
        "transition_type_count": 10,
        "formula_class_count": 13,
        "formula_count": 26,
        "term_count": 581,
        "certified_transition_count": 16_095,
        "certified_formula_eval_count": 32_190,
        "certified_formula_match_count": 32_190,
        "certified_formula_integral_count": 32_190,
        "certified_formula_nonnegative_count": 32_190,
        "probe_state_count": 49_665,
        "probe_formula_eval_count": 99_330,
        "probe_formula_integral_count": 99_330,
        "probe_formula_nonnegative_count": 99_330,
        "probe_formula_zero_count": 258,
        "formula_class_split_count": 3,
        "long_recind_certified_flag": 1,
        "current_formula_match_flag": 1,
        "current_probe_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_formind observable {key} mismatch")

    if hashlib.sha256(
        digest_text(CLASS_COLUMNS, csv_rows["class.csv"]).encode("ascii")
    ).hexdigest() != CLASS_TEXT_HASH:
        raise AssertionError("long_formind class hash mismatch")
    if hashlib.sha256(
        digest_text(TERM_COLUMNS, csv_rows["term.csv"]).encode("ascii")
    ).hexdigest() != TERM_TEXT_HASH:
        raise AssertionError("long_formind term hash mismatch")
    if hashlib.sha256(
        digest_text(CHECK_COLUMNS, csv_rows["check.csv"]).encode("ascii")
    ).hexdigest() != CHECK_TEXT_HASH:
        raise AssertionError("long_formind check hash mismatch")
    if hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, csv_rows["bridge.csv"]).encode("ascii")
    ).hexdigest() != BRIDGE_TEXT_HASH:
        raise AssertionError("long_formind bridge hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_recind_report": LONG_RECIND_REPORT,
        "long_recind_transition": LONG_RECIND_TRANSITION,
        "long_recind_type_summary": LONG_RECIND_TYPE_SUMMARY,
        "long_recind_tables": LONG_RECIND_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.formind.manifest@1":
        raise AssertionError("long_formind manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_formind manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_formind manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_formind missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_formind proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_formind proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.formind.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "formula_surface": witness.get("formula_surface"),
            "certified_match": witness.get("certified_match"),
            "probe": witness.get("probe"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_formind(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
