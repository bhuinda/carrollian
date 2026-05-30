from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59x import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_SEMSTRESS,
        LONG_SEMSTRESS_SOURCE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        ROUTE_COLUMNS,
        SENTINEL_COLUMNS,
        SENTINEL_CODES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59x import (
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_SEMSTRESS,
        LONG_SEMSTRESS_SOURCE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        ROUTE_COLUMNS,
        SENTINEL_COLUMNS,
        SENTINEL_CODES,
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


def validate_long_c59x() -> dict[str, Any]:
    expected = build_payloads()
    c59x = load_json(OUT_DIR / "c59x.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59x != expected["c59x"]:
        raise AssertionError("long_c59x JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59x cert mismatch")
    for filename, key in {
        "sentinel.csv": "sentinel_csv",
        "route.csv": "route_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59x {filename} mismatch")

    for key, expected_array in {
        "sentinel_table": expected["sentinel_table"],
        "route_table": expected["route_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59x table mismatch: {key}")

    if report.get("schema") != "long.c59x.report@1":
        raise AssertionError("long_c59x report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59x report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59x all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59x checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59x report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59x report hash mismatch")

    csv_shapes = [
        ("sentinel.csv", SENTINEL_COLUMNS, len(SENTINEL_CODES)),
        ("route.csv", ROUTE_COLUMNS, 118),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59x {filename} shape mismatch")

    table_shapes = {
        "sentinel_table": (len(SENTINEL_CODES), len(SENTINEL_COLUMNS)),
        "route_table": (118, len(ROUTE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59x {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "semantic_carrier_count": 59,
        "sentinel_count": 1,
        "closure_total": 60,
        "sentinel_mode_count": 2,
        "signed_route_row_count": 118,
        "expected_signed_route_row_count": 118,
        "positive_route_row_count": 59,
        "negative_route_row_count": 59,
        "source_node_count": 20,
        "positive_source_node_count": 20,
        "negative_source_node_count": 20,
        "all_routes_materialized_flag": 1,
        "all_routes_outgoing_flag": 1,
        "all_routes_sign_matched_flag": 1,
        "formal_edge_routing_flag": 1,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59x observable {key} mismatch")

    sentinel_rows = rows_from_table(
        np.asarray(tables["sentinel_table"]), SENTINEL_COLUMNS
    )
    if [row["sentinel_sign"] for row in sentinel_rows] != [1, -1]:
        raise AssertionError("long_c59x sentinel sign order mismatch")
    if any(row["closure_total"] != 60 for row in sentinel_rows):
        raise AssertionError("long_c59x sentinel closure mismatch")

    route_rows = rows_from_table(np.asarray(tables["route_table"]), ROUTE_COLUMNS)
    if [row["route_id"] for row in route_rows] != list(range(118)):
        raise AssertionError("long_c59x route id order mismatch")
    if any(row["outgoing_source_flag"] != 1 for row in route_rows):
        raise AssertionError("long_c59x route source mismatch")
    if any(row["sign_match_flag"] != 1 for row in route_rows):
        raise AssertionError("long_c59x route sign mismatch")
    if any(row["physical_stress_energy_flag"] != 0 for row in route_rows):
        raise AssertionError("long_c59x physical boundary mismatch")
    if len({row["source_atom"] for row in route_rows if row["sentinel_sign"] == 1}) != 20:
        raise AssertionError("long_c59x positive source coverage mismatch")
    if len({row["source_atom"] for row in route_rows if row["sentinel_sign"] == -1}) != 20:
        raise AssertionError("long_c59x negative source coverage mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 0, 0, 0]:
        raise AssertionError("long_c59x gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 1, 0, 0]:
        raise AssertionError("long_c59x gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59x manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59x manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59x manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_semstress": LONG_SEMSTRESS,
        "long_semstress_source": LONG_SEMSTRESS_SOURCE,
        "long_rsem": LONG_RSEM,
        "long_rsem_relation": LONG_RSEM_RELATION,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59x index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59x index report hash mismatch")

    return {
        "schema": "long.c59x.verification@1",
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
    print(json.dumps(validate_long_c59x(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
