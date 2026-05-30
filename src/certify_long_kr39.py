from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_kr39 import (
        CENTRAL_NPZ,
        CENTRAL_REPORT,
        CENTRAL_TABLE,
        FIELD_PRIME,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_KREIN,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        TARGET_COLUMNS,
        TARGET_MOD,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_kr39 import (
        CENTRAL_NPZ,
        CENTRAL_REPORT,
        CENTRAL_TABLE,
        FIELD_PRIME,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_KREIN,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        TARGET_COLUMNS,
        TARGET_MOD,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from derive_long_raw import rows_from_table


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_long_kr39() -> dict[str, Any]:
    expected = build_payloads()
    kr39 = load_json(OUT_DIR / "kr39.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if kr39 != expected["kr39"]:
        raise AssertionError("long_kr39 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_kr39 cert mismatch")
    for filename, key in {
        "pair.csv": "pair_csv",
        "target.csv": "target_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_kr39 {filename} mismatch")

    for key, expected_array in {
        "pair_table": expected["pair_table"],
        "target_table": expected["target_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_kr39 table mismatch: {key}")

    if report.get("schema") != "long.kr39.report@1":
        raise AssertionError("long_kr39 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_kr39 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_kr39 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_kr39 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_kr39 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_kr39 report hash mismatch")

    csv_shapes = [
        ("pair.csv", PAIR_COLUMNS, 1_521),
        ("target.csv", TARGET_COLUMNS, 4),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_kr39 {filename} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "field_prime": FIELD_PRIME,
        "sector_count": 39,
        "relation_count": 985,
        "pair_count": 1_521,
        "closed_pair_count": 402,
        "not_closed_pair_count": 1_119,
        "zero_product_pair_count": 370,
        "nonzero_product_pair_count": 1_151,
        "target_pair_count": 4,
        "target_closed_pair_count": 2,
        "target_zero_product_pair_count": 2,
        "target_verified_135_over_2_count": 0,
        "target_projection_coeff_2_nonzero_count": 0,
        "sector5_support": 12,
        "sector6_support": 133,
        "sector5_sector6_overlap": 0,
        "direct_label_mismatch_flag": 1,
        "next_gap_code": 3,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_kr39 observable {key} mismatch")

    pair_rows = rows_from_table(np.asarray(tables["pair_table"]), PAIR_COLUMNS)
    if [row["pair_id"] for row in pair_rows] != list(range(1_521)):
        raise AssertionError("long_kr39 pair ids mismatch")
    if sum(row["closed_in_sector_span_flag"] for row in pair_rows) != 402:
        raise AssertionError("long_kr39 closed pair count mismatch")
    if sum(row["target_135_over_2_verified_flag"] for row in pair_rows) != 0:
        raise AssertionError("long_kr39 target flag mismatch")

    target_rows = rows_from_table(np.asarray(tables["target_table"]), TARGET_COLUMNS)
    if [(row["i"], row["j"], row["k"]) for row in target_rows] != [
        (5, 5, 2),
        (5, 6, 2),
        (6, 5, 2),
        (6, 6, 2),
    ]:
        raise AssertionError("long_kr39 target triples mismatch")
    if [row["product_support"] for row in target_rows] != [12, 0, 0, 133]:
        raise AssertionError("long_kr39 target support mismatch")
    if [row["closed_in_sector_span_flag"] for row in target_rows] != [0, 1, 1, 0]:
        raise AssertionError("long_kr39 target closure vector mismatch")
    if [row["projection_coeff_k_mod"] for row in target_rows] != [0, 0, 0, 0]:
        raise AssertionError("long_kr39 target projection coefficient mismatch")
    if [row["expected_mod"] for row in target_rows] != [TARGET_MOD] * 4:
        raise AssertionError("long_kr39 target expected mod mismatch")
    if sum(row["direct_sector_target_verified_flag"] for row in target_rows) != 0:
        raise AssertionError("long_kr39 verified target mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 0, 0]:
        raise AssertionError("long_kr39 gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 1, 0]:
        raise AssertionError("long_kr39 gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_kr39 manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_kr39 manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_kr39 manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_krein": LONG_KREIN,
        "central_report": CENTRAL_REPORT,
        "central_npz": CENTRAL_NPZ,
        "central_table": CENTRAL_TABLE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_kr39 index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_kr39 index report hash mismatch")

    return {
        "schema": "long.kr39.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_kr39(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
