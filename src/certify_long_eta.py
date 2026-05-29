from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_eta import (
        BRIDGE_COLUMNS,
        DERIVE_SCRIPT,
        ETA6_CORE_REPORT,
        ETA6_F4_TABLES,
        ETA6_P21_REPORT,
        ETA6_P21_TABLES,
        ETA6_P5_TABLES,
        GATE_COLUMNS_OUT,
        INDEX_PATH,
        INDUCED_EDGE_COLUMNS,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_BRIDGE_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_eta import (
        BRIDGE_COLUMNS,
        DERIVE_SCRIPT,
        ETA6_CORE_REPORT,
        ETA6_F4_TABLES,
        ETA6_P21_REPORT,
        ETA6_P21_TABLES,
        ETA6_P5_TABLES,
        GATE_COLUMNS_OUT,
        INDEX_PATH,
        INDUCED_EDGE_COLUMNS,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_BRIDGE_COLUMNS,
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


def validate_long_eta() -> dict[str, Any]:
    expected = build_payloads()
    eta = load_json(OUT_DIR / "eta.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if eta != expected["eta"]:
        raise AssertionError("long_eta eta JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_eta cert mismatch")
    for filename, key in {
        "bridge.csv": "bridge_csv",
        "gate.csv": "gate_csv",
        "owner.csv": "owner_csv",
        "edge.csv": "edge_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_eta {filename} mismatch")

    for key, expected_array in {
        "bridge_table": expected["bridge_table"],
        "gate_table": expected["gate_table"],
        "owner_bridge_table": expected["owner_bridge_table"],
        "induced_edge_table": expected["induced_edge_table"],
        "observable_table": expected["observable_table"],
        "bridge_owner_ids": expected["bridge_owner_ids"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_eta table mismatch: {key}")

    if report.get("schema") != "long.eta.report@1":
        raise AssertionError("long_eta report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_eta report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_eta all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_eta checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_eta report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_eta report hash mismatch")

    bridge_header, bridge_rows = read_csv(OUT_DIR / "bridge.csv")
    gate_header, gate_rows = read_csv(OUT_DIR / "gate.csv")
    owner_header, owner_rows = read_csv(OUT_DIR / "owner.csv")
    edge_header, edge_rows = read_csv(OUT_DIR / "edge.csv")
    if bridge_header != BRIDGE_COLUMNS or len(bridge_rows) != 24:
        raise AssertionError("long_eta bridge CSV shape mismatch")
    if gate_header != GATE_COLUMNS_OUT or len(gate_rows) != 6:
        raise AssertionError("long_eta gate CSV shape mismatch")
    if owner_header != OWNER_BRIDGE_COLUMNS or len(owner_rows) != 11:
        raise AssertionError("long_eta owner CSV shape mismatch")
    if edge_header != INDUCED_EDGE_COLUMNS or len(edge_rows) != 6:
        raise AssertionError("long_eta edge CSV shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in table_rows(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "gate_count": 6,
        "gate_id_sum": 422,
        "bridge_pair_cell_count": 24,
        "bridge_pair_role_count": 4,
        "p5_gate_ids_match": 1,
        "eta6_preserved_gate_count": 6,
        "bridge_output_closure_pass_count": 24,
        "bridge_closure_slack_min": 0,
        "bridge_closure_slack_max": 176,
        "bridge_closure_slack_sum": 774,
        "bridge_unique_owner_count": 11,
        "bridge_owner_cell_mass": 726_003,
        "bridge_owner_component_count": 1,
        "bridge_owner_weak_class_count": 2,
        "bridge_pair_weak11_count": 22,
        "bridge_pair_weak12_count": 2,
        "bridge_induced_edge_count": 6,
        "bridge_induced_boundary_count": 2620,
        "bridge_induced_source0_boundary_count": 2199,
        "bridge_induced_source1_boundary_count": 421,
        "bridge_unique_owner_pair_count": 55,
        "bridge_unique_owner_distance_min": 1,
        "bridge_unique_owner_distance_max": 10,
        "bridge_unique_owner_distance_sum": 258,
        "gate_span_distance_max": 9,
        "gate_span_distance_sum": 71,
        "f4_sample_row_count": 6,
        "face_count": 3,
        "label_mask_count": 3,
        "sample_level_bridge_flag": 1,
        "eta6_core_input_certified": 1,
        "eta6_p21_input_certified": 1,
        "long_rec_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_eta observable {key} mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "eta6_core_report": ETA6_CORE_REPORT,
        "eta6_p21_report": ETA6_P21_REPORT,
        "eta6_p21_tables": ETA6_P21_TABLES,
        "eta6_p5_tables": ETA6_P5_TABLES,
        "eta6_f4_tables": ETA6_F4_TABLES,
        "long_rec_report": LONG_REC_REPORT,
        "long_rec_tables": LONG_REC_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.eta.manifest@1":
        raise AssertionError("long_eta manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_eta manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_eta manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_eta missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_eta index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_eta index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.eta.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "bridge_scope": witness.get("bridge_scope"),
            "gate": witness.get("gate"),
            "projection": witness.get("projection"),
            "owners": witness.get("owners"),
            "transition": witness.get("transition"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_eta(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
