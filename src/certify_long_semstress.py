from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_semstress import (
        COMPLEMENT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_STRESS20,
        LONG_STRESS20_NODE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SOURCE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_semstress import (
        COMPLEMENT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_RSEM,
        LONG_RSEM_RELATION,
        LONG_STRESS20,
        LONG_STRESS20_NODE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        SOURCE_COLUMNS,
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


def validate_long_semstress() -> dict[str, Any]:
    expected = build_payloads()
    semstress = load_json(OUT_DIR / "semstress.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if semstress != expected["semstress"]:
        raise AssertionError("long_semstress JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_semstress cert mismatch")
    for filename, key in {
        "source.csv": "source_csv",
        "complement.csv": "complement_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_semstress {filename} mismatch")

    for key, expected_array in {
        "source_table": expected["source_table"],
        "complement_table": expected["complement_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_semstress table mismatch: {key}")

    if report.get("schema") != "long.semstress.report@1":
        raise AssertionError("long_semstress report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_semstress report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_semstress all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_semstress checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_semstress report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_semstress report hash mismatch")

    csv_shapes = [
        ("source.csv", SOURCE_COLUMNS, 20),
        ("complement.csv", COMPLEMENT_COLUMNS, 10),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_semstress {filename} shape mismatch")

    table_shapes = {
        "source_table": (20, len(SOURCE_COLUMNS)),
        "complement_table": (10, len(COMPLEMENT_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_semstress {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "semantic_relation_row_count": 59,
        "stress_node_count": 20,
        "stress_edge_row_count": 100,
        "semantic_source_node_count": 20,
        "relation_to_node_map_count": 59,
        "relation_to_edge_map_count": 0,
        "source_total_mass": 59,
        "normalized_source_measure_flag": 1,
        "all_semantic_rows_node_mapped_flag": 1,
        "all_stress_nodes_hit_flag": 1,
        "complement_pair_count": 10,
        "complement_tension_zero_pair_count": 10,
        "node_source_bridge_flag": 1,
        "edge_coupling_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_semstress observable {key} mismatch")

    source_rows = rows_from_table(np.asarray(tables["source_table"]), SOURCE_COLUMNS)
    if [row["atom_id"] for row in source_rows] != list(range(20)):
        raise AssertionError("long_semstress source atom order mismatch")
    if sum(row["semantic_row_count"] for row in source_rows) != 59:
        raise AssertionError("long_semstress source mass mismatch")
    if any(row["thermal_weight_den"] != 59 for row in source_rows):
        raise AssertionError("long_semstress source denominator mismatch")
    if any(row["source_present_flag"] != 1 for row in source_rows):
        raise AssertionError("long_semstress source coverage mismatch")
    if any(row["stress_node_present_flag"] != 1 for row in source_rows):
        raise AssertionError("long_semstress stress node coverage mismatch")

    complement_rows = rows_from_table(
        np.asarray(tables["complement_table"]), COMPLEMENT_COLUMNS
    )
    if [row["pair_id"] for row in complement_rows] != list(range(10)):
        raise AssertionError("long_semstress complement pair order mismatch")
    if any(row["signed_tension_sum_scaled"] != 0 for row in complement_rows):
        raise AssertionError("long_semstress complement tension mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 1, 0, 0, 0, 0]:
        raise AssertionError("long_semstress gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 0, 1, 0, 0, 0]:
        raise AssertionError("long_semstress gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_semstress manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_semstress manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_semstress manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_rsem": LONG_RSEM,
        "long_rsem_relation": LONG_RSEM_RELATION,
        "long_stress20": LONG_STRESS20,
        "long_stress20_node": LONG_STRESS20_NODE,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_semstress index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_semstress index report hash mismatch")

    return {
        "schema": "long.semstress.verification@1",
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
    print(json.dumps(validate_long_semstress(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
