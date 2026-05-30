from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_b3mod import (
        CLASS_COLUMNS,
        COORIENT_FORMULA,
        COORIENT_NPZ,
        DOCS_REAL,
        E_COLUMNS,
        EXPECTED_GROUP_ORDER,
        EXPECTED_POINTS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_KR39,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PERMCHAR_COLUMNS,
        SOURCE_CACHE_REPORT,
        STATUS,
        STRICT_REPLAY_REPORT,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_b3mod import (
        CLASS_COLUMNS,
        COORIENT_FORMULA,
        COORIENT_NPZ,
        DOCS_REAL,
        E_COLUMNS,
        EXPECTED_GROUP_ORDER,
        EXPECTED_POINTS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_KR39,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PERMCHAR_COLUMNS,
        SOURCE_CACHE_REPORT,
        STATUS,
        STRICT_REPLAY_REPORT,
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


def validate_long_b3mod() -> dict[str, Any]:
    expected = build_payloads()
    b3mod = load_json(OUT_DIR / "b3mod.json")
    source_json = load_json(OUT_DIR / "widetildeB3_character_table.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if b3mod != expected["b3mod"]:
        raise AssertionError("long_b3mod JSON mismatch")
    if source_json != expected["source_json"]:
        raise AssertionError("long_b3mod character source JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_b3mod cert mismatch")
    for filename, key in {
        "class.csv": "class_csv",
        "permutation_character.csv": "permutation_character_csv",
        "balanced_Ei_irrep_decomposition.csv": "e_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_b3mod {filename} mismatch")

    for key, expected_array in {
        "class_table": expected["class_table"],
        "permchar_table": expected["permchar_table"],
        "e_table": expected["e_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_b3mod table mismatch: {key}")

    if report.get("schema") != "long.b3mod.report@1":
        raise AssertionError("long_b3mod report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_b3mod report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_b3mod all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_b3mod checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_b3mod report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_b3mod report hash mismatch")

    class_count = report["witness"]["summary"]["class_count"]
    csv_shapes = [
        ("class.csv", CLASS_COLUMNS, class_count),
        ("permutation_character.csv", PERMCHAR_COLUMNS, class_count),
        ("balanced_Ei_irrep_decomposition.csv", E_COLUMNS, 8),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_b3mod {filename} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "generator_count": 3,
        "degree": EXPECTED_POINTS,
        "group_order": EXPECTED_GROUP_ORDER,
        "point_orbit_count": 6,
        "object_size_sum": EXPECTED_POINTS,
        "class_size_sum": EXPECTED_GROUP_ORDER,
        "permutation_character_count": 6,
        "permutation_character_constant_flag": 1,
        "e_module_row_count": 8,
        "e_module_decomposition_present_count": 0,
        "c2_projection_present_count": 0,
        "acceptance_completion_flag": 0,
        "next_gap_code": 3,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_b3mod observable {key} mismatch")
    if obs.get(OBS_CODES["class_count"]) != class_count:
        raise AssertionError("long_b3mod class count observable mismatch")
    if obs.get(OBS_CODES["max_class_size"], 0) <= 0:
        raise AssertionError("long_b3mod max class size invalid")

    class_rows = rows_from_table(np.asarray(tables["class_table"]), CLASS_COLUMNS)
    if [row["class_id"] for row in class_rows] != list(range(class_count)):
        raise AssertionError("long_b3mod class ids mismatch")
    if sum(row["class_size"] for row in class_rows) != EXPECTED_GROUP_ORDER:
        raise AssertionError("long_b3mod class partition mismatch")
    if class_rows[0]["representative_index"] != 0 or class_rows[0]["class_size"] != 1:
        raise AssertionError("long_b3mod identity class mismatch")

    permchar_rows = rows_from_table(
        np.asarray(tables["permchar_table"]), PERMCHAR_COLUMNS
    )
    if [row["class_id"] for row in permchar_rows] != list(range(class_count)):
        raise AssertionError("long_b3mod permutation character ids mismatch")
    first = permchar_rows[0]
    if [
        first["character_B_minus"],
        first["character_B_plus"],
        first["character_V_minus"],
        first["character_V_plus"],
        first["character_S_minus"],
        first["character_S_plus"],
    ] != [384, 192, 144, 576, 512, 768]:
        raise AssertionError("long_b3mod identity character values mismatch")

    e_rows = rows_from_table(np.asarray(tables["e_table"]), E_COLUMNS)
    if [row["e_id"] for row in e_rows] != list(range(8)):
        raise AssertionError("long_b3mod E ids mismatch")
    if sum(row["open_flag"] for row in e_rows) != 8:
        raise AssertionError("long_b3mod E open vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_b3mod gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 1, 0, 0, 0]:
        raise AssertionError("long_b3mod gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_b3mod manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_b3mod manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_b3mod manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "docs_real": DOCS_REAL,
        "coorient_npz": COORIENT_NPZ,
        "coorient_formula": COORIENT_FORMULA,
        "source_cache_report": SOURCE_CACHE_REPORT,
        "strict_replay_report": STRICT_REPLAY_REPORT,
        "long_kr39": LONG_KR39,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_b3mod index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_b3mod index report hash mismatch")

    return {
        "schema": "long.b3mod.verification@1",
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
    print(json.dumps(validate_long_b3mod(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
