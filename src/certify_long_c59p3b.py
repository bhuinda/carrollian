from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3b import (
        BRIDGE_CODES,
        BRIDGE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_ABMAP,
        LONG_ABMAP_CSP,
        LONG_ABMAP_MATCH,
        LONG_ABMAP_OBS,
        LONG_C59P3A,
        LONG_C59P3T,
        LONG_C59P3T_JOIN,
        LONG_C59P3T_OBS,
        LONG_CONTACT_LIFT,
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
    from derive_long_c59p3b import (
        BRIDGE_CODES,
        BRIDGE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_ABMAP,
        LONG_ABMAP_CSP,
        LONG_ABMAP_MATCH,
        LONG_ABMAP_OBS,
        LONG_C59P3A,
        LONG_C59P3T,
        LONG_C59P3T_JOIN,
        LONG_C59P3T_OBS,
        LONG_CONTACT_LIFT,
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


def validate_long_c59p3b() -> dict[str, Any]:
    expected = build_payloads()
    c59p3b = load_json(OUT_DIR / "c59p3b.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3b != expected["c59p3b"]:
        raise AssertionError("long_c59p3b JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3b cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "bridge.csv": "bridge_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3b {filename} mismatch")

    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "bridge_table": expected["bridge_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3b table mismatch: {key}")

    if report.get("schema") != "long.c59p3b.report@1":
        raise AssertionError("long_c59p3b report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3b report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3b all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3b checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3b report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3b report hash mismatch")

    csv_shapes = [
        ("surface.csv", SURFACE_COLUMNS, len(SURFACE_CODES)),
        ("bridge.csv", BRIDGE_COLUMNS, len(BRIDGE_CODES)),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3b {filename} shape mismatch")

    table_shapes = {
        "surface_table": (len(SURFACE_CODES), len(SURFACE_COLUMNS)),
        "bridge_table": (len(BRIDGE_CODES), len(BRIDGE_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3b {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "transition_row_count": 642,
        "contact_row_count": 642,
        "endpoint_row_count": 259,
        "stress_edge_row_count": 100,
        "atom_overlap_row_count": 14,
        "atom_basis_domain_row_count": 90,
        "atom_basis_match_row_count": 83,
        "directed_edge_covered_count": 15,
        "directed_candidate_pair_count": 24,
        "directed_cover_complete_flag": 0,
        "directed_functorial_map_exists_flag": 0,
        "undirected_edge_covered_count": 20,
        "undirected_candidate_pair_count": 59,
        "undirected_max_pair_multiplicity": 6,
        "undirected_relation_cover_flag": 1,
        "undirected_functorial_map_exists_flag": 0,
        "atom_to_basis_function_certified_flag": 0,
        "contact_endpoint_bridge_flag": 1,
        "endpoint_atom_column_count": 0,
        "endpoint_overlap_shared_key_count": 0,
        "transition_overlap_shared_key_count": 0,
        "atom_transition_bridge_flag": 0,
        "basis_stress_atom_bridge_flag": 0,
        "raw_endpoint_stress_atom_bridge_flag": 0,
        "transition_stress_map_certified_flag": 0,
        "current_schema_consumes_atom_score_flag": 0,
        "semantic_transition_operation_flag": 0,
        "physical_selector_axiom_flag": 0,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
        "next_gap_code": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3b observable {key} mismatch")

    surface_rows = rows_from_table(
        np.asarray(tables["surface_table"]), SURFACE_COLUMNS
    )
    if [row["surface_id"] for row in surface_rows] != list(range(len(SURFACE_CODES))):
        raise AssertionError("long_c59p3b surface order mismatch")
    if [row["row_count"] for row in surface_rows] != [14, 100, 642, 642, 259, 83, 2]:
        raise AssertionError("long_c59p3b surface row counts mismatch")
    if [row["schema_atom_key_flag"] for row in surface_rows] != [1, 1, 0, 0, 0, 1, 1]:
        raise AssertionError("long_c59p3b surface atom-key vector mismatch")
    if [row["functorial_map_flag"] for row in surface_rows] != [0, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3b surface functor vector mismatch")

    bridge_rows = rows_from_table(np.asarray(tables["bridge_table"]), BRIDGE_COLUMNS)
    if [row["bridge_id"] for row in bridge_rows] != list(range(len(BRIDGE_CODES))):
        raise AssertionError("long_c59p3b bridge order mismatch")
    if [row["candidate_count"] for row in bridge_rows] != [24, 59, 259, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3b bridge candidate vector mismatch")
    if [row["certified_map_flag"] for row in bridge_rows] != [0, 0, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3b bridge certified vector mismatch")
    if [row["obstruction_flag"] for row in bridge_rows] != [1, 1, 0, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3b bridge obstruction vector mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59p3b decision order mismatch")
    if [row["value"] for row in decision_rows] != [1, 0, 0, 0, 0, 0, 0, 0, 1]:
        raise AssertionError("long_c59p3b decision value vector mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 0, 0, 0, 0, 0, 0, 0, 1]:
        raise AssertionError("long_c59p3b decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 1, 1, 1, 1, 1, 1, 1, 0]:
        raise AssertionError("long_c59p3b decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3b gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3b gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3b manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3b manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3b manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3t": LONG_C59P3T,
        "long_c59p3t_join": LONG_C59P3T_JOIN,
        "long_c59p3t_obs": LONG_C59P3T_OBS,
        "long_abmap": LONG_ABMAP,
        "long_abmap_csp": LONG_ABMAP_CSP,
        "long_abmap_match": LONG_ABMAP_MATCH,
        "long_abmap_obs": LONG_ABMAP_OBS,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_contact_lift": LONG_CONTACT_LIFT,
        "long_c59p3a": LONG_C59P3A,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3b index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3b index report hash mismatch")

    return {
        "schema": "long.c59p3b.verification@1",
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
    print(json.dumps(validate_long_c59p3b(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
