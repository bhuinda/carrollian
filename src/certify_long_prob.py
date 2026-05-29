from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_prob import (
        DECOMP_COLUMNS,
        DECOMP_TEXT_HASH,
        DERIVE_SCRIPT,
        DIST_COLUMNS,
        DIST_TEXT_HASH,
        INDEX_PATH,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        MOMENT_COLUMNS,
        MOMENT_TEXT_HASH,
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
    from derive_long_prob import (
        DECOMP_COLUMNS,
        DECOMP_TEXT_HASH,
        DERIVE_SCRIPT,
        DIST_COLUMNS,
        DIST_TEXT_HASH,
        INDEX_PATH,
        LONG_DUAL_PATH,
        LONG_DUAL_REPORT,
        LONG_DUAL_TABLES,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_TABLES,
        MOMENT_COLUMNS,
        MOMENT_TEXT_HASH,
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


def validate_long_prob() -> dict[str, Any]:
    expected = build_payloads()
    prob_payload = load_json(OUT_DIR / "prob.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if prob_payload != expected["prob"]:
        raise AssertionError("long_prob prob JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_prob cert mismatch")
    for filename, key in {
        "dist.csv": "dist_csv",
        "moment.csv": "moment_csv",
        "decomp.csv": "decomp_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_prob {filename} mismatch")

    for key, expected_array in {
        "dist_table": expected["dist_table"],
        "moment_table": expected["moment_table"],
        "decomp_table": expected["decomp_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_prob table mismatch: {key}")

    if report.get("schema") != "long.prob.report@1":
        raise AssertionError("long_prob report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_prob report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_prob all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_prob checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_prob report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_prob report hash mismatch")

    csv_shapes = [
        ("dist.csv", DIST_COLUMNS, 288),
        ("moment.csv", MOMENT_COLUMNS, 16),
        ("decomp.csv", DECOMP_COLUMNS, 1),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_prob {filename} shape mismatch")

    table_shapes = {
        "dist_table": (288, len(DIST_COLUMNS)),
        "moment_table": (16, len(MOMENT_COLUMNS)),
        "decomp_table": (1, len(DECOMP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_prob {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "distribution_row_count": 288,
        "moment_row_count": 16,
        "decomp_row_count": 1,
        "path_count": 288,
        "sample_count_min": 1,
        "sample_count_max": 16,
        "weight_total_digits": 28,
        "weight_total_mod_1000000007": 497_101_086,
        "weight_total_mod_1000000009": 118_327_119,
        "weighted_sum_value_mod_1000000007": 558_093_655,
        "weighted_square_sum_value_mod_1000000007": 610_560_676,
        "global_mean_num_digits": 31,
        "global_mean_den_digits": 31,
        "global_mean_num_mod_1000000007": 102_643_987,
        "global_mean_den_mod_1000000007": 665_153_007,
        "global_variance_num_digits": 58,
        "global_variance_den_digits": 61,
        "global_variance_num_mod_1000000007": 328_754_671,
        "global_variance_den_mod_1000000007": 624_142_416,
        "within_variance_num_mod_1000000007": 18_093_641,
        "between_variance_num_mod_1000000007": 732_540_241,
        "variance_decomp_flag": 1,
        "variance_shrink_flag_count": 16,
        "variance_shrink_gap_num_mod_sum_1000000007": 956_356_567,
        "first_variance_num_mod_1000000007": 94,
        "first_variance_den_mod_1000000007": 169,
        "last_variance_num_mod_1000000007": 923_295_380,
        "last_variance_den_mod_1000000007": 269_357_187,
        "current_dual_probability_flag": 1,
        "current_conditional_lln_shrink_flag": 1,
        "current_variance_decomp_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_prob observable {key} mismatch")

    if hashlib.sha256(
        digest_text(DIST_COLUMNS, csv_rows["dist.csv"]).encode("ascii")
    ).hexdigest() != DIST_TEXT_HASH:
        raise AssertionError("long_prob distribution hash mismatch")
    if hashlib.sha256(
        digest_text(MOMENT_COLUMNS, csv_rows["moment.csv"]).encode("ascii")
    ).hexdigest() != MOMENT_TEXT_HASH:
        raise AssertionError("long_prob moment hash mismatch")
    if hashlib.sha256(
        digest_text(DECOMP_COLUMNS, csv_rows["decomp.csv"]).encode("ascii")
    ).hexdigest() != DECOMP_TEXT_HASH:
        raise AssertionError("long_prob decomposition hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_dual_report": LONG_DUAL_REPORT,
        "long_dual_path": LONG_DUAL_PATH,
        "long_dual_tables": LONG_DUAL_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_tables": LONG_PATH_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.prob.manifest@1":
        raise AssertionError("long_prob manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_prob manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_prob manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_prob missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_prob proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_prob proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.prob.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "measure": witness.get("measure"),
            "conditional_lln_curve": witness.get("conditional_lln_curve"),
            "variance_decomposition": witness.get("variance_decomposition"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_prob(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
