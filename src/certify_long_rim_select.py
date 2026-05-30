from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_rim_select import (
        INDEX_PATH,
        LONG_CONTACT_CSV,
        LONG_CONTACT_LIFT,
        LONG_RIM_CLASS,
        LONG_RIM_ORBIT,
        LONG_RIM_REPORT,
        LONG_STRESS20,
        LONG_STRESS_COUPLE,
        LONG_STRESS_COUPLE_SCHEMA,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PHASE_COLUMNS,
        SCHEMA_COLUMNS,
        SELECTOR_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_rim_select import (
        INDEX_PATH,
        LONG_CONTACT_CSV,
        LONG_CONTACT_LIFT,
        LONG_RIM_CLASS,
        LONG_RIM_ORBIT,
        LONG_RIM_REPORT,
        LONG_STRESS20,
        LONG_STRESS_COUPLE,
        LONG_STRESS_COUPLE_SCHEMA,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PHASE_COLUMNS,
        SCHEMA_COLUMNS,
        SELECTOR_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )


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


def validate_long_rim_select() -> dict[str, Any]:
    expected = build_payloads()
    rim_select = load_json(OUT_DIR / "rim_select.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if rim_select != expected["rim_select"]:
        raise AssertionError("long_rim_select JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_rim_select cert mismatch")
    for filename, key in {
        "phase.csv": "phase_csv",
        "selector.csv": "selector_csv",
        "schema.csv": "schema_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_rim_select {filename} mismatch")

    for key, expected_array in {
        "phase_table": expected["phase_table"],
        "selector_table": expected["selector_table"],
        "schema_table": expected["schema_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_rim_select table mismatch: {key}")

    if report.get("schema") != "long.rim_select.report@1":
        raise AssertionError("long_rim_select report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_rim_select report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_rim_select all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_rim_select checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rim_select report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_rim_select report hash mismatch")

    csv_shapes = [
        ("phase.csv", PHASE_COLUMNS, 63),
        ("selector.csv", SELECTOR_COLUMNS, 8),
        ("schema.csv", SCHEMA_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_rim_select {filename} shape mismatch")

    table_shapes = {
        "phase_table": (63, len(PHASE_COLUMNS)),
        "selector_table": (8, len(SELECTOR_COLUMNS)),
        "schema_table": (6, len(SCHEMA_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_rim_select {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 6,
        "input_certified_count": 6,
        "rim_phase_count": 63,
        "rim_orbit_count": 124,
        "rim_unoriented_count": 88704,
        "golden_class_count": 1,
        "golden_orbit_count": 1,
        "golden_unoriented_rim_count": 144,
        "stress_directed_edge_count": 100,
        "stress_undirected_edge_count": 64,
        "contact_row_count": 642,
        "transition_row_count": 642,
        "stress_transition_shared_key_count": 0,
        "semantic_transition_operation_flag": 0,
        "existing_golden_selector_count": 0,
        "golden_phase_selected_flag": 0,
        "rim_selection_obstruction_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_rim_select observable {key} mismatch")
    if not (
        obs[OBS_CODES["stress_overlap_global_directed_max"]]
        > obs[OBS_CODES["stress_overlap_golden_directed_max"]]
    ):
        raise AssertionError("long_rim_select directed stress comparison mismatch")
    if not (
        obs[OBS_CODES["stress_overlap_global_undirected_max"]]
        > obs[OBS_CODES["stress_overlap_golden_undirected_max"]]
    ):
        raise AssertionError("long_rim_select undirected stress comparison mismatch")
    if not (
        obs[OBS_CODES["stress_weight_global_max"]]
        > obs[OBS_CODES["stress_weight_golden_max"]]
    ):
        raise AssertionError("long_rim_select stress weight comparison mismatch")

    phase_rows = rows_from_table(np.asarray(tables["phase_table"]), PHASE_COLUMNS)
    golden_rows = [row for row in phase_rows if row["golden_flag"] == 1]
    if len(golden_rows) != 1 or golden_rows[0]["existing_selector_flag"] != 0:
        raise AssertionError("long_rim_select golden phase row mismatch")
    if sum(row["rim_count"] for row in phase_rows) != 88704:
        raise AssertionError("long_rim_select phase rim count mismatch")
    if any(row["existing_selector_flag"] != 0 for row in phase_rows):
        raise AssertionError("long_rim_select unexpected existing selector flag")

    selector_rows = rows_from_table(
        np.asarray(tables["selector_table"]), SELECTOR_COLUMNS
    )
    if any(row["certified_selector_flag"] != 0 for row in selector_rows):
        raise AssertionError("long_rim_select unexpected certified selector")
    if any(row["obstruction_flag"] != 1 for row in selector_rows):
        raise AssertionError("long_rim_select selector obstruction mismatch")

    schema_rows = rows_from_table(np.asarray(tables["schema_table"]), SCHEMA_COLUMNS)
    if sum(row["shared_selector_key_flag"] for row in schema_rows) != 1:
        raise AssertionError("long_rim_select schema shared key mismatch")
    if any(
        row["present_flag"] == 1
        and row["rim_phase_key_flag"] == 1
        and row["atom_key_flag"] == 1
        and row["obstruction_flag"] != 0
        for row in schema_rows
    ):
        raise AssertionError("long_rim_select rim schema obstruction mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_rim_select manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_rim_select manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rim_select manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_rim": LONG_RIM_REPORT,
        "long_rim_class": LONG_RIM_CLASS,
        "long_rim_orbit": LONG_RIM_ORBIT,
        "long_stress20": LONG_STRESS20,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
        "long_stress_couple": LONG_STRESS_COUPLE,
        "long_stress_couple_schema": LONG_STRESS_COUPLE_SCHEMA,
        "long_contact_lift": LONG_CONTACT_LIFT,
        "long_contact_csv": LONG_CONTACT_CSV,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_rim_select index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_rim_select index report hash mismatch")

    return {
        "schema": "long.rim_select.verification@1",
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
    print(json.dumps(validate_long_rim_select(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
