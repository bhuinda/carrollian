from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_min import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        COVER_COLUMNS,
        COVER_DIGEST_COLUMNS,
        COVER_TEXT_HASH,
        DERIVE_SCRIPT,
        FORCE_COLUMNS,
        FORCE_TEXT_HASH,
        INDEX_PATH,
        LONG_UNIV_LAW,
        LONG_UNIV_REPORT,
        LONG_UNIV_SQUARE,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_min import (
        BASIS_COLUMNS,
        BASIS_TEXT_HASH,
        COVER_COLUMNS,
        COVER_DIGEST_COLUMNS,
        COVER_TEXT_HASH,
        DERIVE_SCRIPT,
        FORCE_COLUMNS,
        FORCE_TEXT_HASH,
        INDEX_PATH,
        LONG_UNIV_LAW,
        LONG_UNIV_REPORT,
        LONG_UNIV_SQUARE,
        LONG_UNIV_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        digest_text,
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


def validate_long_min() -> dict[str, Any]:
    expected = build_payloads()
    min_payload = load_json(OUT_DIR / "min.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if min_payload != expected["min"]:
        raise AssertionError("long_min min JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_min cert mismatch")
    for filename, key in {
        "basis.csv": "basis_csv",
        "force.csv": "force_csv",
        "cover.csv": "cover_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_min {filename} mismatch")

    for key, expected_array in {
        "basis_table": expected["basis_table"],
        "force_table": expected["force_table"],
        "cover_table": expected["cover_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_min table mismatch: {key}")

    if report.get("schema") != "long.min.report@1":
        raise AssertionError("long_min report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_min report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_min all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_min checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_min report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_min report hash mismatch")

    csv_shapes = [
        ("basis.csv", BASIS_COLUMNS, 74),
        ("force.csv", FORCE_COLUMNS, 232),
        ("cover.csv", COVER_COLUMNS, 6),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_min {filename} shape mismatch")

    table_shapes = {
        "basis_table": (74, len(BASIS_COLUMNS)),
        "force_table": (232, len(FORCE_COLUMNS)),
        "cover_table": (6, len(COVER_DIGEST_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_min {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "total_law_count": 306,
        "basis_law_count": 74,
        "forced_law_count": 232,
        "basis_equal_count": 74,
        "forced_equal_count": 232,
        "violation_count": 0,
        "row_sum_forced_count": 9,
        "readout_forced_count": 223,
        "prof_conv_basis_count": 72,
        "stationary_basis_count": 2,
        "mean_forced_count": 16,
        "moment_forced_count": 48,
        "tail_forced_count": 144,
        "shrink_forced_count": 15,
        "dependency_total": 2_264,
        "dependency_max": 33,
        "basis_fraction_num": 74,
        "basis_fraction_den": 306,
        "cover_square_count": 6,
        "basis_irredundant_count": 74,
        "long_univ_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_min observable {key} mismatch")

    if hashlib.sha256(
        digest_text(BASIS_COLUMNS, csv_rows["basis.csv"]).encode("ascii")
    ).hexdigest() != BASIS_TEXT_HASH:
        raise AssertionError("long_min basis hash mismatch")
    if hashlib.sha256(
        digest_text(FORCE_COLUMNS, csv_rows["force.csv"]).encode("ascii")
    ).hexdigest() != FORCE_TEXT_HASH:
        raise AssertionError("long_min force hash mismatch")
    if hashlib.sha256(
        digest_text(COVER_COLUMNS, csv_rows["cover.csv"]).encode("ascii")
    ).hexdigest() != COVER_TEXT_HASH:
        raise AssertionError("long_min cover hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_univ_report": LONG_UNIV_REPORT,
        "long_univ_law": LONG_UNIV_LAW,
        "long_univ_square": LONG_UNIV_SQUARE,
        "long_univ_tables": LONG_UNIV_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.min.manifest@1":
        raise AssertionError("long_min manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_min manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_min manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_min missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_min index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_min index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.min.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "basis": witness.get("basis"),
            "forced": witness.get("forced"),
            "cover": witness.get("cover"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_min(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
