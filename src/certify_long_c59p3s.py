from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3s import (
        CANDIDATE_COLUMNS,
        CLAUSE_CODES,
        CONTRACT_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59NP3,
        LONG_DIM4_GATE,
        LONG_SEL,
        LONG_STRESS_COUPLE,
        LONG_TIME_MAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3s import (
        CANDIDATE_COLUMNS,
        CLAUSE_CODES,
        CONTRACT_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59NP3,
        LONG_DIM4_GATE,
        LONG_SEL,
        LONG_STRESS_COUPLE,
        LONG_TIME_MAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
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


def validate_long_c59p3s() -> dict[str, Any]:
    expected = build_payloads()
    c59p3s = load_json(OUT_DIR / "c59p3s.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3s != expected["c59p3s"]:
        raise AssertionError("long_c59p3s JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3s cert mismatch")
    for filename, key in {
        "candidate.csv": "candidate_csv",
        "contract.csv": "contract_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3s {filename} mismatch")

    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "contract_table": expected["contract_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3s table mismatch: {key}")

    if report.get("schema") != "long.c59p3s.report@1":
        raise AssertionError("long_c59p3s report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3s report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3s all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3s checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3s report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3s report hash mismatch")

    csv_shapes = [
        ("candidate.csv", CANDIDATE_COLUMNS, 2),
        ("contract.csv", CONTRACT_COLUMNS, len(CLAUSE_CODES)),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3s {filename} shape mismatch")

    table_shapes = {
        "candidate_table": (2, len(CANDIDATE_COLUMNS)),
        "contract_table": (len(CLAUSE_CODES), len(CONTRACT_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3s {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 6,
        "input_certified_count": 6,
        "candidate_count": 2,
        "selected_candidate_count": 0,
        "formal_plane_selector_candidate_count": 2,
        "nonprincipal_definite_plane_count": 2,
        "positive_plane_candidate_a": 20,
        "positive_plane_candidate_b": 54,
        "positive_plane_candidate_c": 153,
        "negative_plane_candidate_a": 21,
        "negative_plane_candidate_b": 55,
        "negative_plane_candidate_c": 171,
        "normal_form_time_map_flag": 1,
        "semantic_edge_operation_flag": 0,
        "finite_guard_transition_flag": 1,
        "semantic_transition_operation_flag": 0,
        "stress_coupling_map_certified_flag": 0,
        "shared_stress_coupling_key_count": 0,
        "physical_selector_axiom_flag": 0,
        "dim4_reduction_certified_flag": 0,
        "physical_stress_energy_flag": 0,
        "contract_clause_count": len(CLAUSE_CODES),
        "contract_pass_count": 3,
        "contract_fail_count": len(CLAUSE_CODES) - 3,
        "first_failure_clause_code": CLAUSE_CODES["physical_selector_axiom_present"],
        "downstream_blocked_clause_count": 4,
        "canonical_physical_selection_flag": 0,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3s observable {key} mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if [row["candidate_id"] for row in candidate_rows] != [0, 1]:
        raise AssertionError("long_c59p3s candidate id order mismatch")
    if [
        (row["candidate_a"], row["candidate_b"], row["candidate_c"])
        for row in candidate_rows
    ] != [(20, 54, 153), (21, 55, 171)]:
        raise AssertionError("long_c59p3s candidate triples mismatch")
    if [
        (row["inertia_positive"], row["inertia_negative"])
        for row in candidate_rows
    ] != [(3, 0), (0, 3)]:
        raise AssertionError("long_c59p3s candidate inertia mismatch")
    if [row["selected_physical_flag"] for row in candidate_rows] != [0, 0]:
        raise AssertionError("long_c59p3s candidate selected flag mismatch")

    contract_rows = rows_from_table(
        np.asarray(tables["contract_table"]), CONTRACT_COLUMNS
    )
    if [row["clause_id"] for row in contract_rows] != list(range(len(CLAUSE_CODES))):
        raise AssertionError("long_c59p3s contract order mismatch")
    if [row["pass_flag"] for row in contract_rows] != [1, 1, 1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3s contract pass vector mismatch")
    if [row["first_failure_flag"] for row in contract_rows] != [
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
    ]:
        raise AssertionError("long_c59p3s first failure vector mismatch")
    if [row["downstream_blocked_flag"] for row in contract_rows] != [
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
    ]:
        raise AssertionError("long_c59p3s downstream vector mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59p3s decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3s decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 1, 1, 1, 1]:
        raise AssertionError("long_c59p3s decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3s gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3s gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3s manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3s manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3s manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59np3": LONG_C59NP3,
        "long_time_map": LONG_TIME_MAP,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_stress_couple": LONG_STRESS_COUPLE,
        "long_sel": LONG_SEL,
        "long_dim4_gate": LONG_DIM4_GATE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3s index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3s index report hash mismatch")

    return {
        "schema": "long.c59p3s.verification@1",
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
    print(json.dumps(validate_long_c59p3s(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
