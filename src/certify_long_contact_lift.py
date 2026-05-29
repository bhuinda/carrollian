from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_contact_lift import (
        CONTACT_COLUMNS,
        DERIVE_SCRIPT,
        ENDPOINT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_METRIC_GATE,
        LONG_REC,
        LONG_REC_EDGE,
        LONG_REC_OWNER,
        LONG_REC_TABLES,
        LONG_TIME_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_INDEX,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        _pair_key,
        build_payloads,
        raw_tensor_path_from_index,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_contact_lift import (
        CONTACT_COLUMNS,
        DERIVE_SCRIPT,
        ENDPOINT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_METRIC_GATE,
        LONG_REC,
        LONG_REC_EDGE,
        LONG_REC_OWNER,
        LONG_REC_TABLES,
        LONG_TIME_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RAW_INDEX,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        _pair_key,
        build_payloads,
        raw_tensor_path_from_index,
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


def validate_long_contact_lift() -> dict[str, Any]:
    expected = build_payloads()
    contact_lift = load_json(OUT_DIR / "contact_lift.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if contact_lift != expected["contact_lift"]:
        raise AssertionError("long_contact_lift JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_contact_lift cert mismatch")
    for filename, key in {
        "endpoint.csv": "endpoint_csv",
        "contact.csv": "contact_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_contact_lift {filename} mismatch")

    for key, expected_array in {
        "raw_tensor": expected["raw_tensor"],
        "owner_grid": expected["owner_grid"],
        "endpoint_table": expected["endpoint_table"],
        "contact_table": expected["contact_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_contact_lift table mismatch: {key}")

    if report.get("schema") != "long.contact_lift.report@1":
        raise AssertionError("long_contact_lift report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_contact_lift report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_contact_lift all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_contact_lift checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_contact_lift report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_contact_lift report hash mismatch")

    csv_shapes = [
        ("endpoint.csv", ENDPOINT_COLUMNS, 259),
        ("contact.csv", CONTACT_COLUMNS, 642),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_contact_lift {filename} shape mismatch")

    table_shapes = {
        "raw_tensor": (1_414_965, 4),
        "owner_grid": (985, 985),
        "endpoint_table": (259, len(ENDPOINT_COLUMNS)),
        "contact_table": (642, len(CONTACT_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_contact_lift {key} shape mismatch")

    raw_tensor = np.asarray(tables["raw_tensor"])
    owner_grid = np.asarray(tables["owner_grid"])
    if int(raw_tensor[:, 3].sum()) != 2_537_360:
        raise AssertionError("long_contact_lift raw tensor coefficient mass mismatch")
    if int(owner_grid.min()) != 0 or int(owner_grid.max()) != 258:
        raise AssertionError("long_contact_lift owner grid range mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "raw_tensor_row_count": 1_414_965,
        "raw_tensor_coeff_mass": 2_537_360,
        "owner_grid_row_count": 985,
        "owner_grid_col_count": 985,
        "owner_grid_min": 0,
        "owner_grid_max": 258,
        "owner_row_count": 259,
        "endpoint_raw_count": 259,
        "recurrence_edge_count": 642,
        "contact_edge_count": 642,
        "source0_contact_sum": 12_707,
        "source1_contact_sum": 5_410,
        "boundary_contact_sum": 18_117,
        "source0_verified_edge_count": 642,
        "source1_verified_edge_count": 642,
        "boundary_verified_edge_count": 642,
        "contact_lift_edge_count": 642,
        "contact_lift_certified_flag": 1,
        "semantic_edge_operation_flag": 0,
        "semantic_operation_certified_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["semantic_operation_from_contact_lift"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_contact_lift observable {key} mismatch")

    endpoint_rows = rows_from_table(
        np.asarray(tables["endpoint_table"]), ENDPOINT_COLUMNS
    )
    if [row["basis_id"] for row in endpoint_rows] != list(range(259)):
        raise AssertionError("long_contact_lift endpoint basis ids mismatch")
    if any(row["raw_tensor_flag"] != 1 for row in endpoint_rows):
        raise AssertionError("long_contact_lift endpoint raw support mismatch")

    contact_rows = rows_from_table(
        np.asarray(tables["contact_table"]), CONTACT_COLUMNS
    )
    if [row["edge_id"] for row in contact_rows] != list(range(642)):
        raise AssertionError("long_contact_lift edge ids mismatch")
    if any(row["contact_lift_flag"] != 1 for row in contact_rows):
        raise AssertionError("long_contact_lift contact flag mismatch")
    if sum(row["source0_boundary_count"] for row in contact_rows) != 12_707:
        raise AssertionError("long_contact_lift source0 total mismatch")
    if sum(row["source1_boundary_count"] for row in contact_rows) != 5_410:
        raise AssertionError("long_contact_lift source1 total mismatch")
    if sum(row["boundary_count"] for row in contact_rows) != 18_117:
        raise AssertionError("long_contact_lift boundary total mismatch")
    for row in contact_rows:
        if row["source0_boundary_count"] > 0:
            if row["source0_sample_x"] < 0:
                raise AssertionError("long_contact_lift missing source0 sample")
            if _pair_key(row["source0_sample_owner_a"], row["source0_sample_owner_b"]) != _pair_key(
                row["left_basis_id"], row["right_basis_id"]
            ):
                raise AssertionError("long_contact_lift source0 sample mismatch")
        elif row["source0_sample_x"] != -1:
            raise AssertionError("long_contact_lift zero source0 sample mismatch")
        if row["source1_boundary_count"] > 0:
            if row["source1_sample_x"] < 0:
                raise AssertionError("long_contact_lift missing source1 sample")
            if _pair_key(row["source1_sample_owner_a"], row["source1_sample_owner_b"]) != _pair_key(
                row["left_basis_id"], row["right_basis_id"]
            ):
                raise AssertionError("long_contact_lift source1 sample mismatch")
        elif row["source1_sample_x"] != -1:
            raise AssertionError("long_contact_lift zero source1 sample mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    lift_rows = [
        row
        for row in gap_rows
        if row["obligation_code"] == GAP_CODES["owner_boundary_contact_lift"]
    ]
    if len(lift_rows) != 1 or lift_rows[0]["certified_flag"] != 1:
        raise AssertionError("long_contact_lift closure gap mismatch")
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["obligation_code"]
        != GAP_CODES["semantic_operation_from_contact_lift"]
    ):
        raise AssertionError("long_contact_lift next gap mismatch")

    raw_index = load_json(RAW_INDEX)
    raw_tensor_path = raw_tensor_path_from_index(raw_index)
    inputs = report.get("inputs", {})
    for key, path in {
        "raw_index": RAW_INDEX,
        "raw_tensor": raw_tensor_path,
        "long_metric_gate": LONG_METRIC_GATE,
        "long_time_sem": LONG_TIME_SEM,
        "long_rec": LONG_REC,
        "long_rec_tables": LONG_REC_TABLES,
        "long_rec_owner": LONG_REC_OWNER,
        "long_rec_edge": LONG_REC_EDGE,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.contact_lift.manifest@1":
        raise AssertionError("long_contact_lift manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_contact_lift manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_contact_lift manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_contact_lift missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_contact_lift proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_contact_lift proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.contact_lift.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_contact_lift(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
