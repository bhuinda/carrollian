from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_rate import (
        BOUND_COLUMNS,
        BOUND_DIGEST_COLUMNS,
        BOUND_TEXT_HASH,
        CUMULANT_COLUMNS,
        CUMULANT_DIGEST_COLUMNS,
        CUMULANT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_DEV_CHERNOFF,
        LONG_DEV_REPORT,
        LONG_DEV_TABLES,
        LONG_DEV_TAIL,
        LONG_DEV_TILT,
        LONG_PROF_COMPOSE,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        bound_text,
        build_payloads,
        cumulant_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_rate import (
        BOUND_COLUMNS,
        BOUND_DIGEST_COLUMNS,
        BOUND_TEXT_HASH,
        CUMULANT_COLUMNS,
        CUMULANT_DIGEST_COLUMNS,
        CUMULANT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_DEV_CHERNOFF,
        LONG_DEV_REPORT,
        LONG_DEV_TABLES,
        LONG_DEV_TAIL,
        LONG_DEV_TILT,
        LONG_PROF_COMPOSE,
        LONG_PROF_REPORT,
        LONG_PROF_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        bound_text,
        build_payloads,
        cumulant_text,
        rows_from_table,
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


def validate_long_rate() -> dict[str, Any]:
    expected = build_payloads()
    rate = load_json(OUT_DIR / "rate.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if rate != expected["rate"]:
        raise AssertionError("long_rate rate JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rate cert mismatch")
    for filename, key in {
        "cumulant.csv": "cumulant_csv",
        "bound.csv": "bound_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rate {filename} mismatch")

    for key, expected_array in {
        "cumulant_table": expected["cumulant_table"],
        "bound_table": expected["bound_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rate table mismatch: {key}")

    if report.get("schema") != "long.rate.report@1":
        raise AssertionError("long_rate report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rate report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rate all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rate checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rate report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rate report hash mismatch")

    csv_shapes = [
        ("cumulant.csv", CUMULANT_COLUMNS, 24),
        ("bound.csv", BOUND_COLUMNS, 16),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_rate {filename} shape mismatch")

    table_shapes = {
        "cumulant_table": (24, len(CUMULANT_DIGEST_COLUMNS)),
        "bound_table": (16, len(BOUND_DIGEST_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_rate {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "sample_horizon": 8,
        "tilt_count": 3,
        "profunctor_distribution_row_count": 80,
        "distribution_sum_one_count": 8,
        "cumulant_row_count": 24,
        "cumulant_mgf_match_count": 24,
        "cumulant_variance_nonnegative_count": 24,
        "cumulant_num_digit_max": 3_669,
        "cumulant_den_digit_max": 3_669,
        "bound_row_count": 16,
        "bound_match_count": 16,
        "gap_match_count": 16,
        "gap_nonnegative_count": 16,
        "bound_num_digit_max": 1_835,
        "bound_den_digit_max": 1_835,
        "prof_compose_law_count": 92,
        "prof_compose_equal_count": 92,
        "prof_compose_violation_count": 0,
        "long_prof_input_certified": 1,
        "long_dev_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_rate observable {key} mismatch")

    if hashlib.sha256(
        cumulant_text(csv_rows["cumulant.csv"]).encode("ascii")
    ).hexdigest() != CUMULANT_TEXT_HASH:
        raise AssertionError("long_rate cumulant hash mismatch")
    if hashlib.sha256(bound_text(csv_rows["bound.csv"]).encode("ascii")).hexdigest() != BOUND_TEXT_HASH:
        raise AssertionError("long_rate bound hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_prof_report": LONG_PROF_REPORT,
        "long_prof_compose": LONG_PROF_COMPOSE,
        "long_prof_tables": LONG_PROF_TABLES,
        "long_dev_report": LONG_DEV_REPORT,
        "long_dev_tilt": LONG_DEV_TILT,
        "long_dev_tail": LONG_DEV_TAIL,
        "long_dev_chernoff": LONG_DEV_CHERNOFF,
        "long_dev_tables": LONG_DEV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.rate.manifest@1":
        raise AssertionError("long_rate manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rate manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_rate manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_rate missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rate index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_rate index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.rate.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "cumulants": witness.get("cumulants"),
            "chernoff_rates": witness.get("chernoff_rates"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_rate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
