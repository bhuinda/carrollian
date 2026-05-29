from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_sheaf import (
        CUT_COLUMNS,
        CUT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_COMP_PAIR,
        LONG_COMP_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SECTION_COLUMNS,
        SECTION_TEXT_HASH,
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
    from derive_long_sheaf import (
        CUT_COLUMNS,
        CUT_TEXT_HASH,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_COMP_PAIR,
        LONG_COMP_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_LLN_REPORT,
        LONG_LLN_TABLES,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SECTION_COLUMNS,
        SECTION_TEXT_HASH,
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


def validate_long_sheaf() -> dict[str, Any]:
    expected = build_payloads()
    sheaf_payload = load_json(OUT_DIR / "sheaf.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if sheaf_payload != expected["sheaf"]:
        raise AssertionError("long_sheaf sheaf JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_sheaf cert mismatch")
    for filename, key in {
        "section.csv": "section_csv",
        "cut.csv": "cut_csv",
        "stalk.csv": "stalk_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_sheaf {filename} mismatch")

    for key, expected_array in {
        "section_table": expected["section_table"],
        "cut_table": expected["cut_table"],
        "stalk_table": expected["stalk_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_sheaf table mismatch: {key}")

    if report.get("schema") != "long.sheaf.report@1":
        raise AssertionError("long_sheaf report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_sheaf report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_sheaf all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_sheaf checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sheaf report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_sheaf report hash mismatch")

    csv_shapes = [
        ("section.csv", SECTION_COLUMNS, 3128),
        ("cut.csv", CUT_COLUMNS, 984),
        ("stalk.csv", STALK_COLUMNS, 985),
    ]
    csv_rows: dict[str, list[dict[str, str]]] = {}
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        csv_rows[filename] = rows
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_sheaf {filename} shape mismatch")

    table_shapes = {
        "section_table": (3128, len(SECTION_COLUMNS)),
        "cut_table": (984, len(CUT_COLUMNS)),
        "stalk_table": (985, len(STALK_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_sheaf {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "section_row_count": 3128,
        "path_row_count": 288,
        "cut_row_count": 984,
        "stalk_row_count": 985,
        "section_zeta_interval_count": 3128,
        "global_section_count": 3128,
        "global_coeff_sum": 15_232,
        "global_coeff_square_sum": 102_272,
        "gap_section_count": 2684,
        "existing_section_count": 444,
        "cut_count_gluing_flag_count": 984,
        "cut_coeff_gluing_flag_count": 984,
        "cut_coeff_square_gluing_flag_count": 984,
        "closed_count_monotone_flag": 1,
        "open_count_monotone_flag": 1,
        "crossing_positive_cut_count": 146,
        "crossing_count_max": 2312,
        "active_stalk_count": 148,
        "active_stalk_min_addr": 0,
        "active_stalk_max_addr": 171,
        "active_span_zero_stalk_count": 24,
        "stalk_section_count_max": 2312,
        "stalk_coeff_sum_max": 13_600,
        "stalk_coeff_square_sum_max": 99_008,
        "current_interval_sheaf_flag": 1,
        "current_all_cuts_glue_lln_observables_flag": 1,
        "current_full_raw_tensor_sheaf_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_sheaf observable {key} mismatch")

    if hashlib.sha256(
        digest_text(SECTION_COLUMNS, csv_rows["section.csv"]).encode("ascii")
    ).hexdigest() != SECTION_TEXT_HASH:
        raise AssertionError("long_sheaf section hash mismatch")
    if hashlib.sha256(
        digest_text(CUT_COLUMNS, csv_rows["cut.csv"]).encode("ascii")
    ).hexdigest() != CUT_TEXT_HASH:
        raise AssertionError("long_sheaf cut hash mismatch")
    if hashlib.sha256(
        digest_text(STALK_COLUMNS, csv_rows["stalk.csv"]).encode("ascii")
    ).hexdigest() != STALK_TEXT_HASH:
        raise AssertionError("long_sheaf stalk hash mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_lln_report": LONG_LLN_REPORT,
        "long_lln_tables": LONG_LLN_TABLES,
        "long_path_report": LONG_PATH_REPORT,
        "long_path_component": LONG_PATH_COMPONENT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_step": LONG_PATH_STEP,
        "long_path_tables": LONG_PATH_TABLES,
        "long_comp_report": LONG_COMP_REPORT,
        "long_comp_pair": LONG_COMP_PAIR,
        "long_comp_path": LONG_COMP_PATH,
        "long_comp_transition": LONG_COMP_TRANSITION,
        "long_comp_tables": LONG_COMP_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.sheaf.manifest@1":
        raise AssertionError("long_sheaf manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sheaf manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_sheaf manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_sheaf missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sheaf proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_sheaf proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.sheaf.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "sections": witness.get("sections"),
            "cut_gluing": witness.get("cut_gluing"),
            "stalks": witness.get("stalks"),
            "current_representation": witness.get("current_representation"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_sheaf(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
