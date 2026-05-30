from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3t import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        JOIN_CODES,
        JOIN_COLUMNS,
        LONG_C59P3A,
        LONG_C59P3A_OVERLAP,
        LONG_CONTACT_CSV,
        LONG_CONTACT_LIFT,
        LONG_ENDPOINT_CSV,
        LONG_STRESS_COUPLE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        SURFACE_CODES,
        SURFACE_COLUMNS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3t import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        JOIN_CODES,
        JOIN_COLUMNS,
        LONG_C59P3A,
        LONG_C59P3A_OVERLAP,
        LONG_CONTACT_CSV,
        LONG_CONTACT_LIFT,
        LONG_ENDPOINT_CSV,
        LONG_STRESS_COUPLE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        SURFACE_CODES,
        SURFACE_COLUMNS,
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


def validate_long_c59p3t() -> dict[str, Any]:
    expected = build_payloads()
    c59p3t = load_json(OUT_DIR / "c59p3t.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3t != expected["c59p3t"]:
        raise AssertionError("long_c59p3t JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3t cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "join.csv": "join_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3t {filename} mismatch")

    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "join_table": expected["join_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3t table mismatch: {key}")

    if report.get("schema") != "long.c59p3t.report@1":
        raise AssertionError("long_c59p3t report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3t report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3t all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3t checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3t report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3t report hash mismatch")

    csv_shapes = [
        ("surface.csv", SURFACE_COLUMNS, len(SURFACE_CODES)),
        ("join.csv", JOIN_COLUMNS, len(JOIN_CODES)),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3t {filename} shape mismatch")

    table_shapes = {
        "surface_table": (len(SURFACE_CODES), len(SURFACE_COLUMNS)),
        "join_table": (len(JOIN_CODES), len(JOIN_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3t {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "overlap_row_count": 14,
        "transition_row_count": 642,
        "contact_row_count": 642,
        "endpoint_row_count": 259,
        "stress_edge_row_count": 100,
        "overlap_stress_shared_key_count": 5,
        "transition_contact_shared_key_count": 7,
        "contact_endpoint_bridge_flag": 1,
        "transition_stress_shared_key_count": 0,
        "transition_overlap_shared_key_count": 0,
        "contact_overlap_shared_key_count": 0,
        "endpoint_overlap_shared_key_count": 0,
        "transition_atom_column_count": 0,
        "transition_stress_edge_column_count": 0,
        "contact_atom_column_count": 0,
        "endpoint_atom_column_count": 0,
        "atom_overlap_orientation_candidate_flag": 1,
        "atom_transition_bridge_flag": 0,
        "transition_stress_map_certified_flag": 0,
        "semantic_transition_operation_flag": 0,
        "current_schema_consumes_atom_score_flag": 0,
        "physical_selector_axiom_flag": 0,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3t observable {key} mismatch")

    surface_rows = rows_from_table(np.asarray(tables["surface_table"]), SURFACE_COLUMNS)
    if [row["row_count"] for row in surface_rows] != [14, 642, 642, 259, 100]:
        raise AssertionError("long_c59p3t surface row counts mismatch")
    if [row["has_source_atom"] for row in surface_rows] != [1, 0, 0, 0, 1]:
        raise AssertionError("long_c59p3t source atom vector mismatch")
    if [row["has_stress_edge_id"] for row in surface_rows] != [1, 0, 0, 0, 1]:
        raise AssertionError("long_c59p3t stress edge id vector mismatch")

    join_rows = rows_from_table(np.asarray(tables["join_table"]), JOIN_COLUMNS)
    if [row["join_id"] for row in join_rows] != list(range(len(JOIN_CODES))):
        raise AssertionError("long_c59p3t join order mismatch")
    if [row["certified_flag"] for row in join_rows] != [1, 1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3t join certified vector mismatch")
    if [row["obstruction_flag"] for row in join_rows] != [0, 0, 0, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3t join obstruction vector mismatch")
    if [row["shared_key_count"] for row in join_rows] != [5, 7, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3t shared key vector mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59p3t decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3t decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 1, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3t decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3t gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3t gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3t manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3t manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3t manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3a": LONG_C59P3A,
        "long_c59p3a_overlap": LONG_C59P3A_OVERLAP,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_contact_lift": LONG_CONTACT_LIFT,
        "long_contact_csv": LONG_CONTACT_CSV,
        "long_endpoint_csv": LONG_ENDPOINT_CSV,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
        "long_stress_couple": LONG_STRESS_COUPLE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3t index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3t index report hash mismatch")

    return {
        "schema": "long.c59p3t.verification@1",
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
    print(json.dumps(validate_long_c59p3t(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
