from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_gapind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_DOMIND_BRIDGE,
        LONG_DOMIND_COVER,
        LONG_DOMIND_FORMULA,
        LONG_DOMIND_REPORT,
        LONG_DOMIND_TABLES,
        LONG_FORMIND_BRIDGE,
        LONG_FORMIND_CHECK,
        LONG_FORMIND_CLASS,
        LONG_FORMIND_REPORT,
        LONG_FORMIND_TABLES,
        LONG_FORMIND_TERM,
        LONG_RECIND_BRIDGE,
        LONG_RECIND_REPORT,
        LONG_RECIND_SEED,
        LONG_RECIND_TABLES,
        LONG_RECIND_TRANSITION,
        LONG_RECIND_TYPE_SUMMARY,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REGIME_COLUMNS,
        REGIME_TEXT_HASH,
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
    from derive_long_gapind import (
        BRIDGE_COLUMNS,
        BRIDGE_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_DOMIND_BRIDGE,
        LONG_DOMIND_COVER,
        LONG_DOMIND_FORMULA,
        LONG_DOMIND_REPORT,
        LONG_DOMIND_TABLES,
        LONG_FORMIND_BRIDGE,
        LONG_FORMIND_CHECK,
        LONG_FORMIND_CLASS,
        LONG_FORMIND_REPORT,
        LONG_FORMIND_TABLES,
        LONG_FORMIND_TERM,
        LONG_RECIND_BRIDGE,
        LONG_RECIND_REPORT,
        LONG_RECIND_SEED,
        LONG_RECIND_TABLES,
        LONG_RECIND_TRANSITION,
        LONG_RECIND_TYPE_SUMMARY,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        REGIME_COLUMNS,
        REGIME_TEXT_HASH,
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


def validate_long_gapind() -> dict[str, Any]:
    expected = build_payloads()
    gapind_payload = load_json(OUT_DIR / "gapind.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if gapind_payload != expected["gapind"]:
        raise AssertionError("long_gapind gapind JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_gapind cert mismatch")
    for filename, key in {
        "regime.csv": "regime_csv",
        "bridge.csv": "bridge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_gapind {filename} mismatch")

    for key, expected_array in {
        "regime_table": expected["regime_table"],
        "bridge_table": expected["bridge_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_gapind table mismatch: {key}")

    if report.get("schema") != "long.gapind.report@1":
        raise AssertionError("long_gapind report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_gapind report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_gapind all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_gapind checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gapind report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_gapind report hash mismatch")

    csv_shapes = [
        ("regime.csv", REGIME_COLUMNS, 4),
        ("bridge.csv", BRIDGE_COLUMNS, 1),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_gapind {filename} shape mismatch")

    table_shapes = {
        "regime_table": (4, len(REGIME_COLUMNS)),
        "bridge_table": (1, len(BRIDGE_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_gapind {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "regime_count": 4,
        "induction_start": 16,
        "finite_start_sample_count": 17,
        "finite_end_sample_count": 127,
        "probe_start_sample_count": 128,
        "probe_end_sample_count": 256,
        "tail_start_sample_count": 257,
        "recurrence_factor": 12,
        "seed_state_count": 33,
        "seed_gap_nonnegative_count": 66,
        "finite_transition_count": 16_095,
        "finite_delta_nonnegative_count": 32_190,
        "finite_delta_zero_count": 222,
        "formula_class_count": 13,
        "formula_count": 26,
        "probe_state_count": 49_665,
        "probe_formula_eval_count": 99_330,
        "probe_formula_nonnegative_count": 99_330,
        "probe_formula_zero_count": 258,
        "tail_formula_nonnegative_count": 26,
        "cover_assignment_count": 306,
        "finite_gap_check_count": 131_586,
        "finite_gap_nonnegative_count": 131_586,
        "recind_certified_flag": 1,
        "formind_certified_flag": 1,
        "domind_certified_flag": 1,
        "seed_to_finite_seam_flag": 1,
        "finite_to_probe_seam_flag": 1,
        "probe_to_tail_seam_flag": 1,
        "formula_tail_match_flag": 1,
        "current_gapind_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_gapind observable {key} mismatch")

    if hashlib.sha256(
        digest_text(REGIME_COLUMNS, csv_rows["regime.csv"]).encode("ascii")
    ).hexdigest() != REGIME_TEXT_HASH:
        raise AssertionError("long_gapind regime hash mismatch")
    if hashlib.sha256(
        digest_text(BRIDGE_COLUMNS, csv_rows["bridge.csv"]).encode("ascii")
    ).hexdigest() != BRIDGE_TEXT_HASH:
        raise AssertionError("long_gapind bridge hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_recind_report": LONG_RECIND_REPORT,
        "long_recind_seed": LONG_RECIND_SEED,
        "long_recind_transition": LONG_RECIND_TRANSITION,
        "long_recind_type_summary": LONG_RECIND_TYPE_SUMMARY,
        "long_recind_bridge": LONG_RECIND_BRIDGE,
        "long_recind_tables": LONG_RECIND_TABLES,
        "long_formind_report": LONG_FORMIND_REPORT,
        "long_formind_class": LONG_FORMIND_CLASS,
        "long_formind_term": LONG_FORMIND_TERM,
        "long_formind_check": LONG_FORMIND_CHECK,
        "long_formind_bridge": LONG_FORMIND_BRIDGE,
        "long_formind_tables": LONG_FORMIND_TABLES,
        "long_domind_report": LONG_DOMIND_REPORT,
        "long_domind_formula": LONG_DOMIND_FORMULA,
        "long_domind_cover": LONG_DOMIND_COVER,
        "long_domind_bridge": LONG_DOMIND_BRIDGE,
        "long_domind_tables": LONG_DOMIND_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.gapind.manifest@1":
        raise AssertionError("long_gapind manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gapind manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_gapind manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_gapind missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_gapind proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_gapind proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.gapind.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "regimes": witness.get("regimes"),
            "gap_induction": witness.get("gap_induction"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_gapind(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
