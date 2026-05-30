from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59e import (
        EDGE_FLUX_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59X,
        LONG_C59X_ROUTE,
        LONG_C59X_SENTINEL,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        MODE_COLUMNS,
        NODE_BALANCE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        ROUTE_FLUX_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59e import (
        EDGE_FLUX_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59X,
        LONG_C59X_ROUTE,
        LONG_C59X_SENTINEL,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        MODE_COLUMNS,
        NODE_BALANCE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        ROUTE_FLUX_COLUMNS,
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


def validate_long_c59e() -> dict[str, Any]:
    expected = build_payloads()
    c59e = load_json(OUT_DIR / "c59e.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59e != expected["c59e"]:
        raise AssertionError("long_c59e JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59e cert mismatch")
    for filename, key in {
        "route_flux.csv": "route_flux_csv",
        "edge_flux.csv": "edge_flux_csv",
        "node_balance.csv": "node_balance_csv",
        "mode.csv": "mode_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59e {filename} mismatch")

    for key, expected_array in {
        "route_flux_table": expected["route_flux_table"],
        "edge_flux_table": expected["edge_flux_table"],
        "node_balance_table": expected["node_balance_table"],
        "mode_table": expected["mode_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59e table mismatch: {key}")

    if report.get("schema") != "long.c59e.report@1":
        raise AssertionError("long_c59e report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59e report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59e all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59e checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59e report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59e report hash mismatch")

    route_rows_expected = 118
    edge_rows_expected = expected["report"]["witness"]["summary"]["edge_flux_row_count"]
    csv_shapes = [
        ("route_flux.csv", ROUTE_FLUX_COLUMNS, route_rows_expected),
        ("edge_flux.csv", EDGE_FLUX_COLUMNS, edge_rows_expected),
        ("node_balance.csv", NODE_BALANCE_COLUMNS, 20),
        ("mode.csv", MODE_COLUMNS, 2),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59e {filename} shape mismatch")

    table_shapes = {
        "route_flux_table": (route_rows_expected, len(ROUTE_FLUX_COLUMNS)),
        "edge_flux_table": (edge_rows_expected, len(EDGE_FLUX_COLUMNS)),
        "node_balance_table": (20, len(NODE_BALANCE_COLUMNS)),
        "mode_table": (2, len(MODE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59e {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 2,
        "input_certified_count": 2,
        "route_row_count": 118,
        "node_balance_row_count": 20,
        "sentinel_mode_count": 2,
        "positive_route_count": 59,
        "negative_route_count": 59,
        "global_divergence_scaled": 0,
        "global_conservation_flag": 1,
        "controlled_defect_flag": 1,
        "formal_edge_ansatz_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59e observable {key} mismatch")
    if obs[OBS_CODES["defect_node_count"]] <= 0:
        raise AssertionError("long_c59e defect node count mismatch")
    if obs[OBS_CODES["total_abs_defect_scaled"]] <= 0:
        raise AssertionError("long_c59e total defect mismatch")
    if obs[OBS_CODES["max_abs_defect_scaled"]] <= 0:
        raise AssertionError("long_c59e max defect mismatch")
    if obs[OBS_CODES["node_outgoing_total_scaled"]] != obs[
        OBS_CODES["node_incoming_total_scaled"]
    ]:
        raise AssertionError("long_c59e node total mismatch")

    route_flux_rows = rows_from_table(
        np.asarray(tables["route_flux_table"]), ROUTE_FLUX_COLUMNS
    )
    if [row["route_id"] for row in route_flux_rows] != list(range(118)):
        raise AssertionError("long_c59e route id order mismatch")
    if any(row["formal_ansatz_flag"] != 1 for row in route_flux_rows):
        raise AssertionError("long_c59e route ansatz flag mismatch")
    if any(
        row["route_flux_scaled"] != row["sentinel_sign"] * row["route_weight_scaled"]
        for row in route_flux_rows
    ):
        raise AssertionError("long_c59e route flux sign mismatch")

    node_rows = rows_from_table(
        np.asarray(tables["node_balance_table"]), NODE_BALANCE_COLUMNS
    )
    if [row["atom_id"] for row in node_rows] != list(range(20)):
        raise AssertionError("long_c59e node order mismatch")
    if sum(row["divergence_scaled"] for row in node_rows) != 0:
        raise AssertionError("long_c59e divergence sum mismatch")
    if sum(row["abs_divergence_scaled"] for row in node_rows) <= 0:
        raise AssertionError("long_c59e defect table mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 0, 1, 0, 0, 0]:
        raise AssertionError("long_c59e gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59e gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59e manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59e manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59e manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59x": LONG_C59X,
        "long_c59x_route": LONG_C59X_ROUTE,
        "long_c59x_sentinel": LONG_C59X_SENTINEL,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59e index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59e index report hash mismatch")

    return {
        "schema": "long.c59e.verification@1",
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
    print(json.dumps(validate_long_c59e(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
