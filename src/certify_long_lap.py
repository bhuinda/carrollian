from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_lap import (
        COMPONENT_COLUMNS,
        COMPONENT_INT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        ETA6_CORE_REPORT,
        INDEX_PATH,
        LONG_ETA2_REPORT,
        LONG_ETA2_TABLES,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        NODE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_lap import (
        COMPONENT_COLUMNS,
        COMPONENT_INT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        ETA6_CORE_REPORT,
        INDEX_PATH,
        LONG_ETA2_REPORT,
        LONG_ETA2_TABLES,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        NODE_COLUMNS,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
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


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_long_lap() -> dict[str, Any]:
    expected = build_payloads()
    lap = load_json(OUT_DIR / "lap.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if lap != expected["lap"]:
        raise AssertionError("long_lap lap JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_lap cert mismatch")
    for filename, key in {
        "node.csv": "node_csv",
        "component.csv": "component_csv",
        "edge.csv": "edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_lap {filename} mismatch")

    for key, expected_array in {
        "node_table": expected["node_table"],
        "component_table": expected["component_table"],
        "edge_table": expected["edge_table"],
        "observable_table": expected["observable_table"],
        "laplacian": expected["laplacian"],
        "component_ids": expected["component_ids"],
        "active_owner_ids": expected["active_owner_ids"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_lap table mismatch: {key}")

    if report.get("schema") != "long.lap.report@1":
        raise AssertionError("long_lap report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_lap report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_lap all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_lap checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_lap report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_lap report hash mismatch")

    node_header, node_rows = read_csv(OUT_DIR / "node.csv")
    component_header, component_rows = read_csv(OUT_DIR / "component.csv")
    edge_header, edge_rows = read_csv(OUT_DIR / "edge.csv")
    if node_header != NODE_COLUMNS or len(node_rows) != 51:
        raise AssertionError("long_lap node CSV shape mismatch")
    if component_header != COMPONENT_COLUMNS or len(component_rows) != 3:
        raise AssertionError("long_lap component CSV shape mismatch")
    if edge_header != EDGE_COLUMNS or len(edge_rows) != 91:
        raise AssertionError("long_lap edge CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "active_owner_count": 51,
        "induced_edge_count": 91,
        "induced_component_count": 3,
        "induced_component_min_size": 1,
        "induced_component_max_size": 33,
        "internal_weight_total": 5_629,
        "source0_internal_weight_total": 4_938,
        "source1_internal_weight_total": 691,
        "internal_degree_sum": 11_258,
        "ambient_degree_sum": 15_842,
        "external_boundary_total": 4_584,
        "full_graph_edge_count": 642,
        "full_graph_boundary_contact_count": 18_117,
        "full_graph_directed_boundary_contact_count": 36_234,
        "active_external_conductance_num": 4_584,
        "active_external_conductance_den": 15_842,
        "active_external_conductance_reduced_num": 2_292,
        "active_external_conductance_reduced_den": 7_921,
        "zero_internal_conductance_flag": 1,
        "laplacian_trace": 11_258,
        "laplacian_rank": 48,
        "laplacian_nullity": 3,
        "laplacian_rank_mod_1000000007": 48,
        "laplacian_rank_mod_1000000009": 48,
        "laplacian_row_sum_zero_flag": 1,
        "component_rank_sum": 48,
        "component_nullity_sum": 3,
        "active_support_occurrence_total": 16_261_179_264,
        "active_mult_occurrence_total": 88_155_095_040,
        "active_owner_cell_mass": 749_239,
        "eta6_hpol_margin": 1,
        "eta6_packet_min_margin": 1,
        "eta6_gate_floor": 492_736,
        "eta6_gate_preserved_count": 6,
        "long_eta2_input_certified": 1,
        "long_rec_input_certified": 1,
        "eta6_core_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_lap observable {key} mismatch")

    component_table = np.asarray(tables["component_table"])
    expected_component_rows = [
        [0, 33, 61, 841, 502, 339, 1682, 3024, 1342, 1342, 3024, 671, 1512, 3175424320, 15292956672, 36560, 32, 1],
        [1, 1, 0, 0, 0, 0, 0, 864, 864, 864, 864, 1, 1, 1601231360, 9154068480, 96023, 0, 1],
        [2, 17, 30, 4788, 4436, 352, 9576, 11954, 2378, 2378, 11954, 1189, 5977, 11484523584, 63708069888, 616656, 16, 1],
    ]
    prefix_width = 18
    for row, expected_prefix in zip(component_table.tolist(), expected_component_rows):
        if row[:prefix_width] != expected_prefix:
            raise AssertionError("long_lap component numeric fingerprint mismatch")

    if component_table.shape != (3, len(COMPONENT_INT_COLUMNS)):
        raise AssertionError("long_lap component table shape mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_eta2_report": LONG_ETA2_REPORT,
        "long_eta2_tables": LONG_ETA2_TABLES,
        "long_rec_report": LONG_REC_REPORT,
        "long_rec_tables": LONG_REC_TABLES,
        "eta6_core_report": ETA6_CORE_REPORT,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.lap.manifest@1":
        raise AssertionError("long_lap manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_lap manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_lap manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_lap missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_lap index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_lap index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.lap.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "active_subgraph": witness.get("active_subgraph"),
            "laplacian": witness.get("laplacian"),
            "conductance": {
                "internal_weight": witness.get("conductance", {}).get(
                    "internal_weight"
                ),
                "ambient_degree": witness.get("conductance", {}).get(
                    "ambient_degree"
                ),
                "external_boundary": witness.get("conductance", {}).get(
                    "external_boundary"
                ),
                "active_external_ratio": witness.get("conductance", {}).get(
                    "active_external_ratio"
                ),
                "internal_conductance_zero": witness.get("conductance", {}).get(
                    "internal_conductance_zero"
                ),
            },
            "mass": witness.get("mass"),
            "eta6_context": witness.get("eta6_context"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_lap(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
