from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_flow import (
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        LONG_CUT_REPORT,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        SHELL_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_COLUMNS,
        build_payloads,
        edge_flow_text,
        owner_flow_text,
        rows_from_table,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_flow import (
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        LONG_CUT_REPORT,
        LONG_LAP_REPORT,
        LONG_LAP_TABLES,
        LONG_REC_REPORT,
        LONG_REC_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OWNER_COLUMNS,
        SHELL_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_COLUMNS,
        build_payloads,
        edge_flow_text,
        owner_flow_text,
        rows_from_table,
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


def validate_long_flow() -> dict[str, Any]:
    expected = build_payloads()
    flow = load_json(OUT_DIR / "flow.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if flow != expected["flow"]:
        raise AssertionError("long_flow flow JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_flow cert mismatch")
    for filename, key in {
        "component.csv": "component_csv",
        "edge.csv": "edge_csv",
        "owner.csv": "owner_csv",
        "weak.csv": "weak_csv",
        "shell.csv": "shell_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_flow {filename} mismatch")

    for key, expected_array in {
        "component_table": expected["component_table"],
        "edge_table": expected["edge_table"],
        "owner_table": expected["owner_table"],
        "weak_table": expected["weak_table"],
        "shell_table": expected["shell_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_flow table mismatch: {key}")

    if report.get("schema") != "long.flow.report@1":
        raise AssertionError("long_flow report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_flow report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_flow all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_flow checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_flow report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_flow report hash mismatch")

    csv_shapes = [
        ("component.csv", COMPONENT_COLUMNS, 3),
        ("edge.csv", EDGE_COLUMNS, 76),
        ("owner.csv", OWNER_COLUMNS, 52),
        ("weak.csv", WEAK_COLUMNS, 2),
        ("shell.csv", SHELL_COLUMNS, 8),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_flow {filename} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "line_point_count": 985,
        "full_owner_count": 259,
        "active_owner_count": 51,
        "inactive_owner_count": 208,
        "shell_count": 8,
        "shell_max_distance": 7,
        "shell1_owner_count": 52,
        "flow_edge_count": 76,
        "flow_boundary_count": 4_584,
        "flow_source0_boundary_count": 2_407,
        "flow_source1_boundary_count": 2_177,
        "component_count": 3,
        "component_external_positive_count": 3,
        "inactive_flow_owner_count": 52,
        "inactive_multi_component_owner_count": 2,
        "inactive_multi_edge_owner_count": 18,
        "inactive_flow_weight_min": 1,
        "inactive_flow_weight_max": 732,
        "inactive_flow_weight_square_sum": 2_031_134,
        "inactive_flow_edge_count_min": 1,
        "inactive_flow_edge_count_max": 5,
        "inactive_active_neighbor_count_min": 1,
        "inactive_active_neighbor_count_max": 5,
        "weak_flow_class_count": 2,
        "weak11_flow_owner_count": 48,
        "weak12_flow_owner_count": 4,
        "weak11_boundary_count": 3_541,
        "weak12_boundary_count": 1_043,
        "shell_owner_count_sum": 259,
        "shell0_within_boundary_count": 5_629,
        "shell1_prev_boundary_count": 4_584,
        "shell7_owner_count": 2,
        "shell7_next_boundary_count": 0,
        "long_cut_input_certified": 1,
        "long_lap_input_certified": 1,
        "long_rec_input_certified": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_flow observable {key} mismatch")

    component_table = np.asarray(tables["component_table"])
    expected_component_rows = [
        [0, 33, 47, 29, 1_342, 128, 1_214, 0, 155, 1_898, 177_232, 671, 1_512],
        [1, 1, 4, 4, 864, 733, 131, 4, 11, 34, 318, 1, 1],
        [2, 17, 25, 21, 2_378, 1_546, 832, 25, 212, 2_666, 397_160, 1_189, 5_977],
    ]
    if component_table.tolist() != expected_component_rows:
        raise AssertionError("long_flow component table fingerprint mismatch")

    edge_rows = rows_from_table(np.asarray(tables["edge_table"]), EDGE_COLUMNS)
    owner_rows = rows_from_table(np.asarray(tables["owner_table"]), OWNER_COLUMNS)
    if edge_flow_text(edge_rows) != edge_flow_text(
        rows_from_table(expected["edge_table"], EDGE_COLUMNS)
    ):
        raise AssertionError("long_flow edge text mismatch")
    if owner_flow_text(owner_rows) != owner_flow_text(
        rows_from_table(expected["owner_table"], OWNER_COLUMNS)
    ):
        raise AssertionError("long_flow owner text mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_cut_report": LONG_CUT_REPORT,
        "long_lap_report": LONG_LAP_REPORT,
        "long_lap_tables": LONG_LAP_TABLES,
        "long_rec_report": LONG_REC_REPORT,
        "long_rec_tables": LONG_REC_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.flow.manifest@1":
        raise AssertionError("long_flow manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_flow manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_flow manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_flow missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_flow index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("long_flow index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.flow.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": {
            "ambient_flow": witness.get("ambient_flow"),
            "component_flow": witness.get("component_flow"),
            "inactive_owner_flow": witness.get("inactive_owner_flow"),
            "weak_flow": witness.get("weak_flow"),
            "shell_flow": witness.get("shell_flow"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_flow(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
