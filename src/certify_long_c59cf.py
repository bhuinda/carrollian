from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59cf import (
        CORRECTED_EDGE_COLUMNS,
        CORRECTED_NODE_COLUMNS,
        COUNTERFLOW_COLUMNS,
        DUAL_EDGE_COLUMNS,
        DUAL_POTENTIAL_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59E,
        LONG_C59E_EDGE_FLUX,
        LONG_C59E_NODE_BALANCE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
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
    from derive_long_c59cf import (
        CORRECTED_EDGE_COLUMNS,
        CORRECTED_NODE_COLUMNS,
        COUNTERFLOW_COLUMNS,
        DUAL_EDGE_COLUMNS,
        DUAL_POTENTIAL_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59E,
        LONG_C59E_EDGE_FLUX,
        LONG_C59E_NODE_BALANCE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
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


def validate_long_c59cf() -> dict[str, Any]:
    expected = build_payloads()
    c59cf = load_json(OUT_DIR / "c59cf.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59cf != expected["c59cf"]:
        raise AssertionError("long_c59cf JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59cf cert mismatch")
    for filename, key in {
        "counterflow.csv": "counterflow_csv",
        "corrected_edge.csv": "corrected_edge_csv",
        "corrected_node.csv": "corrected_node_csv",
        "dual_potential.csv": "dual_potential_csv",
        "dual_edge.csv": "dual_edge_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59cf {filename} mismatch")

    for key, expected_array in {
        "counterflow_table": expected["counterflow_table"],
        "corrected_edge_table": expected["corrected_edge_table"],
        "corrected_node_table": expected["corrected_node_table"],
        "dual_potential_table": expected["dual_potential_table"],
        "dual_edge_table": expected["dual_edge_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59cf table mismatch: {key}")

    if report.get("schema") != "long.c59cf.report@1":
        raise AssertionError("long_c59cf report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59cf report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59cf all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59cf checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59cf report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59cf report hash mismatch")

    summary = expected["report"]["witness"]["summary"]
    csv_shapes = [
        ("counterflow.csv", COUNTERFLOW_COLUMNS, summary["counterflow_row_count"]),
        ("corrected_edge.csv", CORRECTED_EDGE_COLUMNS, 100),
        ("corrected_node.csv", CORRECTED_NODE_COLUMNS, 20),
        ("dual_potential.csv", DUAL_POTENTIAL_COLUMNS, 20),
        ("dual_edge.csv", DUAL_EDGE_COLUMNS, 100),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59cf {filename} shape mismatch")

    table_shapes = {
        "counterflow_table": (
            summary["counterflow_row_count"],
            len(COUNTERFLOW_COLUMNS),
        ),
        "corrected_edge_table": (100, len(CORRECTED_EDGE_COLUMNS)),
        "corrected_node_table": (20, len(CORRECTED_NODE_COLUMNS)),
        "dual_potential_table": (20, len(DUAL_POTENTIAL_COLUMNS)),
        "dual_edge_table": (100, len(DUAL_EDGE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59cf {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "stress_node_count": 20,
        "stress_directed_edge_count": 100,
        "initial_defect_node_count": 20,
        "supply_node_count": 11,
        "demand_node_count": 9,
        "counterflow_row_count": 19,
        "corrected_local_conserved_node_count": 20,
        "corrected_defect_node_count": 0,
        "corrected_total_abs_defect_scaled": 0,
        "corrected_max_abs_defect_scaled": 0,
        "corrected_global_divergence_scaled": 0,
        "corrected_local_conservation_flag": 1,
        "finite_conserved_edge_current_flag": 1,
        "dual_feasible_flag": 1,
        "complementary_slackness_flag": 1,
        "minimal_counterflow_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59cf observable {key} mismatch")
    if obs[OBS_CODES["supply_total_scaled"]] != obs[OBS_CODES["demand_total_scaled"]]:
        raise AssertionError("long_c59cf supply/demand mismatch")
    if obs[OBS_CODES["counterflow_total_scaled"]] != obs[
        OBS_CODES["supply_total_scaled"]
    ]:
        raise AssertionError("long_c59cf counterflow total mismatch")
    if obs[OBS_CODES["primal_cost_scaled"]] != obs[OBS_CODES["dual_bound_scaled"]]:
        raise AssertionError("long_c59cf primal/dual mismatch")
    if obs[OBS_CODES["primal_dual_gap_scaled"]] != 0:
        raise AssertionError("long_c59cf primal/dual gap mismatch")

    counterflow_rows = rows_from_table(
        np.asarray(tables["counterflow_table"]), COUNTERFLOW_COLUMNS
    )
    if [row["counterflow_id"] for row in counterflow_rows] != list(
        range(len(counterflow_rows))
    ):
        raise AssertionError("long_c59cf counterflow id order mismatch")
    if any(row["counterflow_scaled"] <= 0 for row in counterflow_rows):
        raise AssertionError("long_c59cf nonpositive counterflow mismatch")
    if any(row["unit_cost"] != 1 for row in counterflow_rows):
        raise AssertionError("long_c59cf unit cost mismatch")
    if any(
        row["cost_scaled"] != row["counterflow_scaled"] for row in counterflow_rows
    ):
        raise AssertionError("long_c59cf counterflow cost mismatch")
    if any(row["existing_edge_flag"] != 1 for row in counterflow_rows):
        raise AssertionError("long_c59cf existing-edge flag mismatch")
    if any(row["tight_dual_flag"] != 1 for row in counterflow_rows):
        raise AssertionError("long_c59cf counterflow tightness mismatch")

    corrected_node_rows = rows_from_table(
        np.asarray(tables["corrected_node_table"]), CORRECTED_NODE_COLUMNS
    )
    if [row["atom_id"] for row in corrected_node_rows] != list(range(20)):
        raise AssertionError("long_c59cf node order mismatch")
    for row in corrected_node_rows:
        if row["counterflow_divergence_scaled"] != -row[
            "initial_divergence_scaled"
        ]:
            raise AssertionError("long_c59cf counterflow node balance mismatch")
        if row["corrected_divergence_scaled"] != 0:
            raise AssertionError("long_c59cf corrected divergence mismatch")
        if row["corrected_local_conserved_flag"] != 1:
            raise AssertionError("long_c59cf local conservation flag mismatch")

    dual_edge_rows = rows_from_table(
        np.asarray(tables["dual_edge_table"]), DUAL_EDGE_COLUMNS
    )
    if [row["stress_edge_id"] for row in dual_edge_rows] != list(range(100)):
        raise AssertionError("long_c59cf dual edge order mismatch")
    if any(row["dual_slack"] < 0 for row in dual_edge_rows):
        raise AssertionError("long_c59cf dual feasibility mismatch")
    if any(row["dual_feasible_flag"] != 1 for row in dual_edge_rows):
        raise AssertionError("long_c59cf dual flag mismatch")
    if any(row["complementary_slackness_flag"] != 1 for row in dual_edge_rows):
        raise AssertionError("long_c59cf slackness flag mismatch")
    for row in dual_edge_rows:
        if row["counterflow_scaled"] > 0 and row["dual_slack"] != 0:
            raise AssertionError("long_c59cf positive-flow dual slack mismatch")

    dual_potential_rows = rows_from_table(
        np.asarray(tables["dual_potential_table"]), DUAL_POTENTIAL_COLUMNS
    )
    if [row["atom_id"] for row in dual_potential_rows] != list(range(20)):
        raise AssertionError("long_c59cf potential order mismatch")
    dual_bound = sum(row["dual_contribution_scaled"] for row in dual_potential_rows)
    if dual_bound != obs[OBS_CODES["dual_bound_scaled"]]:
        raise AssertionError("long_c59cf dual bound row mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59cf gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 0, 0, 1, 0, 0]:
        raise AssertionError("long_c59cf gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59cf manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59cf manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59cf manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59e": LONG_C59E,
        "long_c59e_edge_flux": LONG_C59E_EDGE_FLUX,
        "long_c59e_node_balance": LONG_C59E_NODE_BALANCE,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59cf index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59cf index report hash mismatch")

    return {
        "schema": "long.c59cf.verification@1",
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
    print(json.dumps(validate_long_c59cf(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
