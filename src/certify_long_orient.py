from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_orient import (
        CUT_COLUMNS,
        CUT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_ALL_INTERVAL,
        LONG_ALL_REPORT,
        LONG_ALL_SPLIT,
        LONG_ALL_TABLES,
        MOBIUS_COLUMNS,
        MOBIUS_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        STALK_COLUMNS,
        STALK_TEXT_HASH,
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
    from derive_long_orient import (
        CUT_COLUMNS,
        CUT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_ALL_INTERVAL,
        LONG_ALL_REPORT,
        LONG_ALL_SPLIT,
        LONG_ALL_TABLES,
        MOBIUS_COLUMNS,
        MOBIUS_TEXT_HASH,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        PAIR_TEXT_HASH,
        STALK_COLUMNS,
        STALK_TEXT_HASH,
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


def validate_long_orient() -> dict[str, Any]:
    expected = build_payloads()
    orient_payload = load_json(OUT_DIR / "orient.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if orient_payload != expected["orient"]:
        raise AssertionError("long_orient orient JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_orient cert mismatch")
    for filename, key in {
        "pair.csv": "pair_csv",
        "stalk.csv": "stalk_csv",
        "cut.csv": "cut_csv",
        "mobius.csv": "mobius_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_orient {filename} mismatch")

    for key, expected_array in {
        "pair_table": expected["pair_table"],
        "stalk_table": expected["stalk_table"],
        "cut_table": expected["cut_table"],
        "mobius_table": expected["mobius_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_orient table mismatch: {key}")

    if report.get("schema") != "long.orient.report@1":
        raise AssertionError("long_orient report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_orient report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_orient all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_orient checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_orient report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_orient report hash mismatch")

    csv_shapes = [
        ("pair.csv", PAIR_COLUMNS, 131_765),
        ("stalk.csv", STALK_COLUMNS, 985),
        ("cut.csv", CUT_COLUMNS, 984),
        ("mobius.csv", MOBIUS_COLUMNS, 12),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_orient {filename} shape mismatch")

    table_shapes = {
        "pair_table": (131_765, len(PAIR_COLUMNS)),
        "stalk_table": (985, len(STALK_COLUMNS)),
        "cut_table": (984, len(CUT_COLUMNS)),
        "mobius_table": (12, len(MOBIUS_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_orient {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "absolute_pair_count": 131_765,
        "positive_only_pair_count": 11_349,
        "reverse_only_pair_count": 79_785,
        "overlap_pair_count": 40_631,
        "positive_pair_count": 51_980,
        "reverse_pair_count": 120_416,
        "raw_section_count": 1_414_965,
        "positive_section_count": 477_589,
        "reverse_section_count": 937_376,
        "signed_section_count": -459_787,
        "raw_coeff_sum": 2_537_360,
        "positive_coeff_sum": 915_271,
        "reverse_coeff_sum": 1_622_089,
        "signed_coeff_sum": -706_818,
        "raw_coeff_square_sum": 8_119_976,
        "positive_coeff_square_sum": 3_655_871,
        "reverse_coeff_square_sum": 4_464_105,
        "signed_coeff_square_sum": -808_234,
        "pair_projection_count_flag_count": 131_765,
        "pair_projection_coeff_flag_count": 131_765,
        "pair_projection_coeff_square_flag_count": 131_765,
        "stalk_row_count": 985,
        "stalk_projection_count_flag_count": 985,
        "positive_stalk_count_min": 2,
        "positive_stalk_count_max": 85_108,
        "reverse_stalk_count_min": 482,
        "reverse_stalk_count_max": 378_338,
        "total_stalk_count_max": 453_822,
        "signed_stalk_count_min": -353_258,
        "signed_stalk_count_max": -480,
        "signed_stalk_nonzero_count": 985,
        "cut_row_count": 984,
        "cut_projection_count_flag_count": 984,
        "positive_crossing_count_max": 84_076,
        "reverse_crossing_count_max": 376_869,
        "total_crossing_count_max": 451_244,
        "signed_crossing_count_min": -353_264,
        "signed_crossing_count_max": -480,
        "signed_crossing_negative_cut_count": 984,
        "mobius_row_count": 12,
        "mobius_roundtrip_flag_count": 12,
        "orientation_involution_flag": 1,
        "component_projection_exact_flag": 1,
        "mobius_separation_exact_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_orient observable {key} mismatch")

    if hashlib.sha256(
        digest_text(PAIR_COLUMNS, csv_rows["pair.csv"]).encode("ascii")
    ).hexdigest() != PAIR_TEXT_HASH:
        raise AssertionError("long_orient pair hash mismatch")
    if hashlib.sha256(
        digest_text(STALK_COLUMNS, csv_rows["stalk.csv"]).encode("ascii")
    ).hexdigest() != STALK_TEXT_HASH:
        raise AssertionError("long_orient stalk hash mismatch")
    if hashlib.sha256(
        digest_text(CUT_COLUMNS, csv_rows["cut.csv"]).encode("ascii")
    ).hexdigest() != CUT_TEXT_HASH:
        raise AssertionError("long_orient cut hash mismatch")
    if hashlib.sha256(
        digest_text(MOBIUS_COLUMNS, csv_rows["mobius.csv"]).encode("ascii")
    ).hexdigest() != MOBIUS_TEXT_HASH:
        raise AssertionError("long_orient mobius hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_all_report": LONG_ALL_REPORT,
        "long_all_interval": LONG_ALL_INTERVAL,
        "long_all_split": LONG_ALL_SPLIT,
        "long_all_tables": LONG_ALL_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.orient.manifest@1":
        raise AssertionError("long_orient manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_orient manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_orient manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_orient missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_orient proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_orient proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.orient.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "operator": witness.get("operator"),
            "pair_split": witness.get("pair_split"),
            "component_moments": witness.get("component_moments"),
            "stalk_profile": witness.get("stalk_profile"),
            "cut_profile": witness.get("cut_profile"),
            "mobius": {
                key: value
                for key, value in witness.get("mobius", {}).items()
                if key != "dense_hashes"
            },
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_orient(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
