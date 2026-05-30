from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_l63 import (
        BRIDGE_CODES,
        BRIDGE_COLUMNS,
        FIXED63,
        INDEX_PATH,
        LAZY63_REPORT,
        LONG_C2UF,
        LONG_PSEL,
        LONG_RIM,
        LONG_RIM_CLASS,
        LONG_RIM_ORBIT,
        LONG_RIM_PHASE,
        LONG_RIM_SELECT,
        LONG_SEL,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OVERLAP_CODES,
        OVERLAP_COLUMNS,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
        SELECTOR_LOOKUP,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_l63 import (
        BRIDGE_CODES,
        BRIDGE_COLUMNS,
        FIXED63,
        INDEX_PATH,
        LAZY63_REPORT,
        LONG_C2UF,
        LONG_PSEL,
        LONG_RIM,
        LONG_RIM_CLASS,
        LONG_RIM_ORBIT,
        LONG_RIM_PHASE,
        LONG_RIM_SELECT,
        LONG_SEL,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OVERLAP_CODES,
        OVERLAP_COLUMNS,
        SCHEMA_CODES,
        SCHEMA_COLUMNS,
        SELECTOR_LOOKUP,
        STATUS,
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


def validate_long_l63() -> dict[str, Any]:
    expected = build_payloads()
    l63 = load_json(OUT_DIR / "l63.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if l63 != expected["l63"]:
        raise AssertionError("long_l63 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_l63 cert mismatch")
    for filename, key in {
        "bridge.csv": "bridge_csv",
        "schema.csv": "schema_csv",
        "overlap.csv": "overlap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_l63 {filename} mismatch")

    for key, expected_array in {
        "bridge_table": expected["bridge_table"],
        "schema_table": expected["schema_table"],
        "overlap_table": expected["overlap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_l63 table mismatch: {key}")

    if report.get("schema") != "long.l63.report@1":
        raise AssertionError("long_l63 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_l63 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_l63 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_l63 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_l63 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_l63 report hash mismatch")

    csv_shapes = [
        ("bridge.csv", BRIDGE_COLUMNS, len(BRIDGE_CODES)),
        ("schema.csv", SCHEMA_COLUMNS, len(SCHEMA_CODES)),
        ("overlap.csv", OVERLAP_COLUMNS, len(OVERLAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_l63 {filename} shape mismatch")

    table_shapes = {
        "bridge_table": (len(BRIDGE_CODES), len(BRIDGE_COLUMNS)),
        "schema_table": (len(SCHEMA_CODES), len(SCHEMA_COLUMNS)),
        "overlap_table": (len(OVERLAP_CODES), len(OVERLAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_l63 {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "selector_lookup_rows": 1086,
        "selector_family_count": 3,
        "raw543_selector_rows": 543,
        "lazy63_selector_rows": 63,
        "paired_lazy480_selector_rows": 480,
        "fixed63_rows": 63,
        "rim_class_rows": 63,
        "rim_orbit_rows": 124,
        "rim_phase_rows": 63,
        "lazy63_rim_count_match_flag": 1,
        "selector_to_rim_class_shared_column_count": 0,
        "fixed63_to_rim_class_shared_column_count": 0,
        "fixed63_to_rim_orbit_domain_compatible_flag": 0,
        "semantic_bridge_key_count": 0,
        "row_bridge_present_flag": 0,
        "golden_class_count": 1,
        "golden_unoriented_rim_count": 144,
        "golden_selector_backed_flag": 0,
        "physical_selector_axiom_flag": 0,
        "physical_selector_candidate_count": 0,
        "psel_first_failure_clause_code": 4,
        "bridge_obstruction_count": 5,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_l63 observable {key} mismatch")
    if obs[OBS_CODES["fixed63_to_rim_orbit_raw_overlap_count"]] <= 0:
        raise AssertionError("long_l63 expected a visible but unusable numeric overlap")

    bridge_rows = rows_from_table(np.asarray(tables["bridge_table"]), BRIDGE_COLUMNS)
    if sum(row["count_match_flag"] for row in bridge_rows) != 2:
        raise AssertionError("long_l63 count-match marker mismatch")
    if any(row["row_bridge_present_flag"] != 0 for row in bridge_rows):
        raise AssertionError("long_l63 row bridge marker mismatch")
    if any(row["obstruction_flag"] != 1 for row in bridge_rows):
        raise AssertionError("long_l63 obstruction marker mismatch")

    overlap_rows = rows_from_table(np.asarray(tables["overlap_table"]), OVERLAP_COLUMNS)
    if any(row["bridge_usable_flag"] != 0 for row in overlap_rows):
        raise AssertionError("long_l63 usable overlap marker mismatch")
    if any(row["domain_compatible_flag"] != 0 for row in overlap_rows):
        raise AssertionError("long_l63 domain compatibility marker mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_l63 manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_l63 manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_l63 manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c2uf": LONG_C2UF,
        "long_sel": LONG_SEL,
        "long_psel": LONG_PSEL,
        "long_rim": LONG_RIM,
        "long_rim_select": LONG_RIM_SELECT,
        "lazy63_report": LAZY63_REPORT,
        "selector_lookup": SELECTOR_LOOKUP,
        "fixed63": FIXED63,
        "rim_class": LONG_RIM_CLASS,
        "rim_orbit": LONG_RIM_ORBIT,
        "rim_phase": LONG_RIM_PHASE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_l63 index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_l63 index report hash mismatch")

    return {
        "schema": "long.l63.verification@1",
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
    print(json.dumps(validate_long_l63(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
