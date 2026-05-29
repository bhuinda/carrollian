from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import rows_from_table
    from .derive_long_time_sem import raw_tensor_path_from_index
    from .derive_long_transition_sem import (
        DERIVE_SCRIPT,
        ENDPOINT_RAW_COLUMNS,
        EVIDENCE_CODES,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_CONTACT_CONTACT,
        LONG_CONTACT_ENDPOINT,
        LONG_CONTACT_LIFT,
        LONG_METRIC_GATE,
        LONG_TIME_EDGE,
        LONG_TIME_MAP,
        OBS_CODES,
        OBS_COLUMNS,
        OBSTRUCTION_CODES,
        OUT_DIR,
        RAW_INDEX,
        SCHEMA_GAP_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_raw import rows_from_table
    from derive_long_time_sem import raw_tensor_path_from_index
    from derive_long_transition_sem import (
        DERIVE_SCRIPT,
        ENDPOINT_RAW_COLUMNS,
        EVIDENCE_CODES,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_CONTACT_CONTACT,
        LONG_CONTACT_ENDPOINT,
        LONG_CONTACT_LIFT,
        LONG_METRIC_GATE,
        LONG_TIME_EDGE,
        LONG_TIME_MAP,
        OBS_CODES,
        OBS_COLUMNS,
        OBSTRUCTION_CODES,
        OUT_DIR,
        RAW_INDEX,
        SCHEMA_GAP_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
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


def validate_long_transition_sem() -> dict[str, Any]:
    expected = build_payloads()
    transition_sem = load_json(OUT_DIR / "transition_sem.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if transition_sem != expected["transition_sem"]:
        raise AssertionError("long_transition_sem JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_transition_sem cert mismatch")
    for filename, key in {
        "endpoint_raw.csv": "endpoint_raw_csv",
        "transition.csv": "transition_csv",
        "schema_gap.csv": "schema_gap_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_transition_sem {filename} mismatch")

    for key, expected_array in {
        "raw_tensor": expected["raw_tensor"],
        "endpoint_table": expected["endpoint_table"],
        "transition_table": expected["transition_table"],
        "schema_gap_table": expected["schema_gap_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_transition_sem table mismatch: {key}")

    if report.get("schema") != "long.transition_sem.report@1":
        raise AssertionError("long_transition_sem report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_transition_sem report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_transition_sem all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_transition_sem checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_transition_sem report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_transition_sem report hash mismatch")

    csv_shapes = [
        ("endpoint_raw.csv", ENDPOINT_RAW_COLUMNS, 259),
        ("transition.csv", TRANSITION_COLUMNS, 642),
        ("schema_gap.csv", SCHEMA_GAP_COLUMNS, len(EVIDENCE_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_transition_sem {filename} shape mismatch")

    table_shapes = {
        "raw_tensor": (1_414_965, 4),
        "endpoint_table": (259, len(ENDPOINT_RAW_COLUMNS)),
        "transition_table": (642, len(TRANSITION_COLUMNS)),
        "schema_gap_table": (len(EVIDENCE_CODES), len(SCHEMA_GAP_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_transition_sem {key} shape mismatch")

    raw_tensor = np.asarray(tables["raw_tensor"])
    if int(raw_tensor[:, 3].sum()) != 2_537_360:
        raise AssertionError("long_transition_sem raw tensor coefficient mass mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "raw_tensor_row_count": 1_414_965,
        "raw_tensor_coeff_mass": 2_537_360,
        "endpoint_row_count": 259,
        "endpoint_raw_row_id_count": 259,
        "contact_edge_count": 642,
        "normal_form_time_edge_count": 642,
        "transition_row_count": 642,
        "endpoint_pair_raw_row_count": 642,
        "contact_lift_edge_count": 642,
        "normal_form_delta_sum": 642,
        "operation_row_materialized_count": 0,
        "semantic_transition_realized_count": 0,
        "semantic_transition_obstructed_count": 642,
        "finite_guard_transition_flag": 1,
        "semantic_transition_operation_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["physical_stress_energy_tensor"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_transition_sem observable {key} mismatch")

    endpoint_rows = rows_from_table(
        np.asarray(tables["endpoint_table"]), ENDPOINT_RAW_COLUMNS
    )
    if [row["basis_id"] for row in endpoint_rows] != list(range(259)):
        raise AssertionError("long_transition_sem endpoint ids mismatch")
    if any(row["raw_row_id"] < 0 or row["raw_row_id_flag"] != 1 for row in endpoint_rows):
        raise AssertionError("long_transition_sem endpoint raw id mismatch")

    transition_rows = rows_from_table(
        np.asarray(tables["transition_table"]), TRANSITION_COLUMNS
    )
    if [row["edge_id"] for row in transition_rows] != list(range(642)):
        raise AssertionError("long_transition_sem edge ids mismatch")
    if any(row["left_raw_row_id"] < 0 for row in transition_rows):
        raise AssertionError("long_transition_sem left raw id mismatch")
    if any(row["right_raw_row_id"] < 0 for row in transition_rows):
        raise AssertionError("long_transition_sem right raw id mismatch")
    if any(row["endpoint_pair_raw_row_flag"] != 1 for row in transition_rows):
        raise AssertionError("long_transition_sem endpoint pair flag mismatch")
    if any(row["contact_lift_flag"] != 1 for row in transition_rows):
        raise AssertionError("long_transition_sem contact lift flag mismatch")
    if any(row["normal_form_delta_t"] != 1 for row in transition_rows):
        raise AssertionError("long_transition_sem delta_t mismatch")
    if any(row["operation_row_id"] != -1 for row in transition_rows):
        raise AssertionError("long_transition_sem operation row should be absent")
    if any(row["semantic_transition_flag"] != 0 for row in transition_rows):
        raise AssertionError("long_transition_sem semantic transition flag mismatch")
    if any(
        row["obstruction_code"]
        != OBSTRUCTION_CODES["contact_lift_is_boundary_adjacency_not_operation_row"]
        for row in transition_rows
    ):
        raise AssertionError("long_transition_sem obstruction code mismatch")

    schema_gap_rows = rows_from_table(
        np.asarray(tables["schema_gap_table"]), SCHEMA_GAP_COLUMNS
    )
    absent_rows = [
        row
        for row in schema_gap_rows
        if row["evidence_code"]
        in {
            EVIDENCE_CODES["semantic_operation_rows_absent"],
            EVIDENCE_CODES["transition_composition_law_absent"],
        }
    ]
    if len(absent_rows) != 2 or any(row["obstruction_flag"] != 1 for row in absent_rows):
        raise AssertionError("long_transition_sem schema obstruction mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    semantic_rows = [
        row
        for row in gap_rows
        if row["obligation_code"] == GAP_CODES["semantic_operation_from_contact_lift"]
    ]
    if len(semantic_rows) != 1 or semantic_rows[0]["obstruction_flag"] != 1:
        raise AssertionError("long_transition_sem semantic gap mismatch")
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["obligation_code"]
        != GAP_CODES["physical_stress_energy_tensor"]
    ):
        raise AssertionError("long_transition_sem next gap mismatch")

    raw_index = load_json(RAW_INDEX)
    raw_tensor_path = raw_tensor_path_from_index(raw_index)
    inputs = report.get("inputs", {})
    for key, path in {
        "raw_index": RAW_INDEX,
        "raw_tensor": raw_tensor_path,
        "long_contact_lift": LONG_CONTACT_LIFT,
        "long_contact_endpoint": LONG_CONTACT_ENDPOINT,
        "long_contact_contact": LONG_CONTACT_CONTACT,
        "long_metric_gate": LONG_METRIC_GATE,
        "long_time_map": LONG_TIME_MAP,
        "long_time_edge": LONG_TIME_EDGE,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.transition_sem.manifest@1":
        raise AssertionError("long_transition_sem manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_transition_sem manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_transition_sem manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_transition_sem missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_transition_sem proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_transition_sem proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.transition_sem.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "evidence_code_map": witness.get("evidence_code_map"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_transition_sem(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
