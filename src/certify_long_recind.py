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
    from .derive_long_recind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_SUPPIND_REPORT,
        LONG_SUPPIND_RULE_SUMMARY,
        LONG_SUPPIND_SUPPORT,
        LONG_SUPPIND_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SEED_COLUMNS,
        SEED_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        TRANSITION_TEXT_HASH,
        TYPE_SUMMARY_COLUMNS,
        TYPE_SUMMARY_TEXT_HASH,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import rows_from_table
    from derive_long_recind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_SUPPIND_REPORT,
        LONG_SUPPIND_RULE_SUMMARY,
        LONG_SUPPIND_SUPPORT,
        LONG_SUPPIND_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SEED_COLUMNS,
        SEED_TEXT_HASH,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        TRANSITION_TEXT_HASH,
        TYPE_SUMMARY_COLUMNS,
        TYPE_SUMMARY_TEXT_HASH,
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


def validate_long_recind() -> dict[str, Any]:
    expected = build_payloads()
    recind_payload = load_json(OUT_DIR / "recind.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if recind_payload != expected["recind"]:
        raise AssertionError("long_recind recind JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_recind cert mismatch")
    for filename, key in {
        "seed.csv": "seed_csv",
        "transition.csv": "transition_csv",
        "type_summary.csv": "type_summary_csv",
        "bridge.csv": "bridge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_recind {filename} mismatch")

    for key, expected_array in {
        "seed_table": expected["seed_table"],
        "transition_table": expected["transition_table"],
        "type_summary_table": expected["type_summary_table"],
        "bridge_table": expected["bridge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_recind table mismatch: {key}")

    if report.get("schema") != "long.recind.report@1":
        raise AssertionError("long_recind report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_recind report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_recind all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_recind checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_recind report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_recind report hash mismatch")

    csv_shapes = [
        ("seed.csv", SEED_COLUMNS, 33),
        ("transition.csv", TRANSITION_COLUMNS, 16_095),
        ("type_summary.csv", TYPE_SUMMARY_COLUMNS, 10),
        ("bridge.csv", BRIDGE_COLUMNS, 1),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_recind {filename} shape mismatch")

    table_shapes = {
        "seed_table": (33, len(SEED_COLUMNS)),
        "transition_table": (16_095, len(TRANSITION_COLUMNS)),
        "type_summary_table": (10, len(TYPE_SUMMARY_COLUMNS)),
        "bridge_table": (1, len(BRIDGE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_recind {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "induction_start": 16,
        "source_end_sample_count": 127,
        "recurrence_factor": 12,
        "seed_count": 33,
        "transition_count": 16_095,
        "transition_type_count": 10,
        "seed_certificate_count": 33,
        "transition_certificate_count": 16_095,
        "lower_delta_nonnegative_count": 16_095,
        "upper_delta_nonnegative_count": 16_095,
        "lower_delta_zero_count": 111,
        "upper_delta_zero_count": 111,
        "type_certificate_count": 10,
        "support_state_count": 16_128,
        "long_suppind_support_state_count": 16_128,
        "long_suppind_certified_flag": 1,
        "support_row_count_match_flag": 1,
        "current_recurrence_graph_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_recind observable {key} mismatch")

    if hashlib.sha256(
        digest_text(SEED_COLUMNS, csv_rows["seed.csv"]).encode("ascii")
    ).hexdigest() != SEED_TEXT_HASH:
        raise AssertionError("long_recind seed hash mismatch")
    if hashlib.sha256(
        digest_text(TRANSITION_COLUMNS, csv_rows["transition.csv"]).encode("ascii")
    ).hexdigest() != TRANSITION_TEXT_HASH:
        raise AssertionError("long_recind transition hash mismatch")
    if hashlib.sha256(
        digest_text(
            TYPE_SUMMARY_COLUMNS,
            csv_rows["type_summary.csv"],
        ).encode("ascii")
    ).hexdigest() != TYPE_SUMMARY_TEXT_HASH:
        raise AssertionError("long_recind type-summary hash mismatch")
    if hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, csv_rows["bridge.csv"]).encode("ascii")
    ).hexdigest() != BRIDGE_TEXT_HASH:
        raise AssertionError("long_recind bridge hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_suppind_report": LONG_SUPPIND_REPORT,
        "long_suppind_support": LONG_SUPPIND_SUPPORT,
        "long_suppind_rule_summary": LONG_SUPPIND_RULE_SUMMARY,
        "long_suppind_tables": LONG_SUPPIND_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.recind.manifest@1":
        raise AssertionError("long_recind manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_recind manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_recind manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_recind missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_recind proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_recind proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.recind.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "recurrence": witness.get("recurrence"),
            "bridge": witness.get("bridge"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_recind(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
