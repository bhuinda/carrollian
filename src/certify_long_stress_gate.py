from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import rows_from_table
    from .derive_long_stress_gate import (
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_STRESS20,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        STRESS,
        STRESS_ARTIFACT,
        STRESS_EDGE_COLUMNS,
        SURFACE_CODES,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import rows_from_table
    from derive_long_stress_gate import (
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_STRESS20,
        LONG_TRANSITION_CSV,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        STRESS,
        STRESS_ARTIFACT,
        STRESS_EDGE_COLUMNS,
        SURFACE_CODES,
        SURFACE_COLUMNS,
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


def validate_long_stress_gate() -> dict[str, Any]:
    expected = build_payloads()
    stress_gate = load_json(OUT_DIR / "stress_gate.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if stress_gate != expected["stress_gate"]:
        raise AssertionError("long_stress_gate JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_stress_gate cert mismatch")
    for filename, key in {
        "stress_edge.csv": "stress_edge_csv",
        "surface.csv": "surface_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_stress_gate {filename} mismatch")

    for key, expected_array in {
        "stress_edge_table": expected["stress_edge_table"],
        "surface_table": expected["surface_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_stress_gate table mismatch: {key}")

    if report.get("schema") != "long.stress_gate.report@1":
        raise AssertionError("long_stress_gate report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_stress_gate report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_stress_gate all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_stress_gate checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress_gate report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_stress_gate report hash mismatch")

    csv_shapes = [
        ("stress_edge.csv", STRESS_EDGE_COLUMNS, 100),
        ("surface.csv", SURFACE_COLUMNS, len(SURFACE_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_stress_gate {filename} shape mismatch")

    table_shapes = {
        "stress_edge_table": (100, len(STRESS_EDGE_COLUMNS)),
        "surface_table": (len(SURFACE_CODES), len(SURFACE_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_stress_gate {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "transition_row_count": 642,
        "transition_delta_sum": 642,
        "semantic_transition_realized_count": 0,
        "stress_node_count": 20,
        "stress_directed_edge_count": 100,
        "stress_undirected_edge_count": 64,
        "stress_row_degree_min": 5,
        "stress_row_degree_max": 5,
        "stress_complement_pair_count": 10,
        "stress_complement_directed_edge_count": 18,
        "stress_cycle_directed_overlap_count": 14,
        "stress_cycle_undirected_overlap_count": 10,
        "stress_equals_20gon_flag": 0,
        "finite_stress_readout_flag": 1,
        "transition_stress_edge_map_count": 0,
        "transition_stress_coupling_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "curvature_einstein_tensor_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["stress_transition_coupling_map"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_stress_gate observable {key} mismatch")

    stress_edge_rows = rows_from_table(
        np.asarray(tables["stress_edge_table"]), STRESS_EDGE_COLUMNS
    )
    if [row["stress_edge_id"] for row in stress_edge_rows] != list(range(100)):
        raise AssertionError("long_stress_gate stress edge ids mismatch")
    source_counts = {
        atom: sum(1 for row in stress_edge_rows if row["source_atom"] == atom)
        for atom in range(20)
    }
    if set(source_counts.values()) != {5}:
        raise AssertionError("long_stress_gate source degree mismatch")
    if sum(row["complement_edge_flag"] for row in stress_edge_rows) != 18:
        raise AssertionError("long_stress_gate complement directed edge mismatch")
    if sum(row["cycle_edge_flag"] for row in stress_edge_rows) != 14:
        raise AssertionError("long_stress_gate cycle directed edge mismatch")

    surface_rows = rows_from_table(
        np.asarray(tables["surface_table"]), SURFACE_COLUMNS
    )
    if [row["surface_id"] for row in surface_rows] != list(range(len(SURFACE_CODES))):
        raise AssertionError("long_stress_gate surface ids mismatch")
    obstruction_rows = [
        row for row in surface_rows if row["obstruction_flag"] == 1
    ]
    if len(obstruction_rows) != 4:
        raise AssertionError("long_stress_gate obstruction surface count mismatch")
    coupling_rows = [
        row
        for row in surface_rows
        if row["surface_code"] == SURFACE_CODES["transition_to_stress_coupling_law"]
    ]
    if (
        len(coupling_rows) != 1
        or coupling_rows[0]["count_value"] != 0
        or coupling_rows[0]["obstruction_flag"] != 1
    ):
        raise AssertionError("long_stress_gate coupling surface mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["gap_code"] != GAP_CODES["stress_transition_coupling_map"]
    ):
        raise AssertionError("long_stress_gate next gap mismatch")
    closed_rows = [
        row for row in gap_rows if row["gap_code"] == GAP_CODES["finite_stress_readout"]
    ]
    if (
        len(closed_rows) != 1
        or closed_rows[0]["open_flag"] != 0
        or closed_rows[0]["obstruction_flag"] != 0
    ):
        raise AssertionError("long_stress_gate finite stress closure mismatch")
    if sum(row["open_flag"] for row in gap_rows) != 5:
        raise AssertionError("long_stress_gate open gap count mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_transition_csv": LONG_TRANSITION_CSV,
        "long_stress20": LONG_STRESS20,
        "stress": STRESS,
        "stress_artifact": STRESS_ARTIFACT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.stress_gate.manifest@1":
        raise AssertionError("long_stress_gate manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress_gate manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_stress_gate manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_stress_gate missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_stress_gate proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_stress_gate proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.stress_gate.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "surface_code_map": witness.get("surface_code_map"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_stress_gate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
