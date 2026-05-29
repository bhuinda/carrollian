from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import rows_from_table
    from .derive_long_stress20 import (
        COMPLEMENT_COLUMNS,
        CYCLE_EDGE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NODE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        STRESS,
        STRESS_ARTIFACT,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import rows_from_table
    from derive_long_stress20 import (
        COMPLEMENT_COLUMNS,
        CYCLE_EDGE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NODE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        STRESS,
        STRESS_ARTIFACT,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
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


def validate_long_stress20() -> dict[str, Any]:
    expected = build_payloads()
    stress20 = load_json(OUT_DIR / "stress20.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if stress20 != expected["stress20"]:
        raise AssertionError("long_stress20 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_stress20 cert mismatch")
    for filename, key in {
        "node.csv": "node_csv",
        "cycle_edge.csv": "cycle_edge_csv",
        "complement.csv": "complement_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_stress20 {filename} mismatch")

    for key, expected_array in {
        "node_table": expected["node_table"],
        "cycle_edge_table": expected["cycle_edge_table"],
        "complement_table": expected["complement_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_stress20 table mismatch: {key}")

    if report.get("schema") != "long.stress20.report@1":
        raise AssertionError("long_stress20 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_stress20 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_stress20 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_stress20 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress20 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_stress20 report hash mismatch")

    csv_shapes = [
        ("node.csv", NODE_COLUMNS, 20),
        ("cycle_edge.csv", CYCLE_EDGE_COLUMNS, 20),
        ("complement.csv", COMPLEMENT_COLUMNS, 10),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_stress20 {filename} shape mismatch")

    table_shapes = {
        "node_table": (20, len(NODE_COLUMNS)),
        "cycle_edge_table": (20, len(CYCLE_EDGE_COLUMNS)),
        "complement_table": (10, len(COMPLEMENT_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_stress20 {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "stress_node_count": 20,
        "stress_directed_edge_count": 100,
        "stress_undirected_edge_count": 64,
        "stress_row_degree_min": 5,
        "stress_row_degree_max": 5,
        "stress_undirected_degree_min": 5,
        "stress_undirected_degree_max": 9,
        "stress_undirected_diameter": 4,
        "stress_connected_flag": 1,
        "cycle_node_count": 20,
        "cycle_directed_edge_count": 40,
        "cycle_undirected_edge_count": 20,
        "cycle_diameter": 10,
        "cycle_directed_overlap_count": 14,
        "cycle_undirected_overlap_count": 10,
        "cycle_undirected_missing_count": 10,
        "complement_pair_count": 10,
        "complement_cycle_edge_overlap_count": 2,
        "complement_cycle_antipode_pair_count": 0,
        "complement_stress_undirected_overlap_count": 10,
        "complement_stress_directed_overlap_count": 18,
        "stress_equals_20gon_flag": 0,
        "stress_contains_cycle_flag": 0,
        "stress_contains_all_complements_flag": 1,
        "comparison_certified_flag": 1,
        "physical_spacetime_20gon_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_stress20 observable {key} mismatch")

    node_rows = rows_from_table(np.asarray(tables["node_table"]), NODE_COLUMNS)
    if [row["atom_id"] for row in node_rows] != list(range(20)):
        raise AssertionError("long_stress20 atom ids mismatch")
    if any(row["stress_neighbor_count"] != 5 for row in node_rows):
        raise AssertionError("long_stress20 row degree mismatch")
    if any(row["complement_is_cycle_antipode_flag"] != 0 for row in node_rows):
        raise AssertionError("long_stress20 complement antipode mismatch")
    if sum(row["cycle_neighbor_hit_count"] for row in node_rows) != 14:
        raise AssertionError("long_stress20 directed cycle hit mismatch")

    cycle_rows = rows_from_table(
        np.asarray(tables["cycle_edge_table"]), CYCLE_EDGE_COLUMNS
    )
    present_cycle_edges = [
        (row["atom_a"], row["atom_b"])
        for row in cycle_rows
        if row["stress_undirected_flag"] == 1
    ]
    if sorted(present_cycle_edges) != [
        (0, 19),
        (1, 2),
        (4, 5),
        (7, 8),
        (8, 9),
        (9, 10),
        (10, 11),
        (11, 12),
        (14, 15),
        (17, 18),
    ]:
        raise AssertionError("long_stress20 cycle-overlap edge list mismatch")
    if sum(row["stress_forward_flag"] + row["stress_reverse_flag"] for row in cycle_rows) != 14:
        raise AssertionError("long_stress20 directed cycle overlap mismatch")

    complement_rows = rows_from_table(
        np.asarray(tables["complement_table"]), COMPLEMENT_COLUMNS
    )
    if sum(row["stress_undirected_flag"] for row in complement_rows) != 10:
        raise AssertionError("long_stress20 complement stress overlap mismatch")
    if sum(row["cycle_antipode_pair_flag"] for row in complement_rows) != 0:
        raise AssertionError("long_stress20 complement antipode pair mismatch")
    if sum(row["cycle_edge_flag"] for row in complement_rows) != 2:
        raise AssertionError("long_stress20 complement cycle overlap mismatch")
    if sum(row["stress_forward_flag"] + row["stress_reverse_flag"] for row in complement_rows) != 18:
        raise AssertionError("long_stress20 complement directed overlap mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "stress": STRESS,
        "stress_artifact": STRESS_ARTIFACT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.stress20.manifest@1":
        raise AssertionError("long_stress20 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress20 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_stress20 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_stress20 missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress20 proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_stress20 proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.stress20.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_stress20(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
