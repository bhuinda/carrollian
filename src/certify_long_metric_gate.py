from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_metric_gate import (
        ATLAS,
        DECISION_CODES,
        DECISION_COLUMNS,
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        HYPERBOLIC,
        INDEX_PATH,
        LONG_GR,
        LONG_LOR,
        LONG_TIME_MAP,
        LONG_TIME_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POINCARE,
        STATUS,
        STRESS,
        SURFACE_CODES,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_metric_gate import (
        ATLAS,
        DECISION_CODES,
        DECISION_COLUMNS,
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        HYPERBOLIC,
        INDEX_PATH,
        LONG_GR,
        LONG_LOR,
        LONG_TIME_MAP,
        LONG_TIME_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        POINCARE,
        STATUS,
        STRESS,
        SURFACE_CODES,
        SURFACE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
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


def validate_long_metric_gate() -> dict[str, Any]:
    expected = build_payloads()
    metric_gate = load_json(OUT_DIR / "metric_gate.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if metric_gate != expected["metric_gate"]:
        raise AssertionError("long_metric_gate JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_metric_gate cert mismatch")
    for filename, key in {
        "surface.csv": "surface_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_metric_gate {filename} mismatch")

    for key, expected_array in {
        "surface_table": expected["surface_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_metric_gate table mismatch: {key}")

    if report.get("schema") != "long.metric_gate.report@1":
        raise AssertionError("long_metric_gate report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_metric_gate report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_metric_gate all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_metric_gate checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_metric_gate report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_metric_gate report hash mismatch")

    csv_shapes = [
        ("surface.csv", SURFACE_COLUMNS, len(SURFACE_CODES)),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_metric_gate {filename} shape mismatch")

    table_shapes = {
        "surface_table": (len(SURFACE_CODES), len(SURFACE_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_metric_gate {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 8,
        "input_certified_count": 8,
        "surface_count": 8,
        "formal_metric_surface_count": 6,
        "semantic_metric_surface_count": 0,
        "obstruction_surface_count": 1,
        "guard_required_surface_count": 5,
        "recurrence_edge_count": 642,
        "normal_form_tick_total": 642,
        "semantic_edge_operation_flag": 0,
        "semantic_obstruction_flag": 1,
        "boundary_atom_count": 20,
        "hyperbolic_johnson_edge_count": 90,
        "poincare_atom_count": 20,
        "stress_graph_node_count": 20,
        "guarded_finite_metric_gate_flag": 1,
        "a985_semantic_metric_gate_flag": 0,
        "contact_lift_required_flag": 1,
        "smooth_lorentzian_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 6,
        "next_gap_code": GAP_CODES["owner_boundary_contact_lift"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_metric_gate observable {key} mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if any(row["pass_flag"] != 1 for row in decision_rows):
        raise AssertionError("long_metric_gate decision row failure")

    surface_rows = rows_from_table(
        np.asarray(tables["surface_table"]), SURFACE_COLUMNS
    )
    if any(row["gr_claim_flag"] != 0 for row in surface_rows):
        raise AssertionError("long_metric_gate must not claim GR")
    if sum(row["semantic_metric_input_flag"] for row in surface_rows) != 0:
        raise AssertionError("long_metric_gate semantic metric input mismatch")
    obstruction_rows = [
        row
        for row in surface_rows
        if row["surface_id"] == SURFACE_CODES["semantic_edge_obstruction"]
    ]
    if len(obstruction_rows) != 1 or obstruction_rows[0]["obstruction_flag"] != 1:
        raise AssertionError("long_metric_gate obstruction surface mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["obligation_code"]
        != GAP_CODES["owner_boundary_contact_lift"]
    ):
        raise AssertionError("long_metric_gate next gap mismatch")
    semantic_rows = [
        row
        for row in gap_rows
        if row["obligation_code"]
        == GAP_CODES["semantic_edge_operation_realization_from_a985"]
    ]
    if len(semantic_rows) != 1 or semantic_rows[0]["obstruction_flag"] != 1:
        raise AssertionError("long_metric_gate semantic obstruction gap mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_gr": LONG_GR,
        "long_lor": LONG_LOR,
        "long_time_map": LONG_TIME_MAP,
        "long_time_sem": LONG_TIME_SEM,
        "atlas": ATLAS,
        "hyperbolic": HYPERBOLIC,
        "poincare": POINCARE,
        "stress": STRESS,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.metric_gate.manifest@1":
        raise AssertionError("long_metric_gate manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_metric_gate manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_metric_gate manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_metric_gate missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_metric_gate proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_metric_gate proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.metric_gate.verification@1",
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
    print(json.dumps(validate_long_metric_gate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
