from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_raw import rows_from_table
    from .derive_long_time_map import (
        CLOCK_CODES,
        CLOCK_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_TIME_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INTEGRITY_SUMMARY,
        LONG_LOR,
        LONG_REC,
        LONG_REC_EDGE,
        MATRIX_COLUMNS,
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
    from derive_long_raw import rows_from_table
    from derive_long_time_map import (
        CLOCK_CODES,
        CLOCK_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_TIME_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        INTEGRITY_SUMMARY,
        LONG_LOR,
        LONG_REC,
        LONG_REC_EDGE,
        MATRIX_COLUMNS,
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


def validate_long_time_map() -> dict[str, Any]:
    expected = build_payloads()
    time_map = load_json(OUT_DIR / "time_map.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if time_map != expected["time_map"]:
        raise AssertionError("long_time_map JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_time_map cert mismatch")
    for filename, key in {
        "matrix.csv": "matrix_csv",
        "edge_time.csv": "edge_time_csv",
        "clock.csv": "clock_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_time_map {filename} mismatch")

    for key, expected_array in {
        "tau_int": expected["tau_int"],
        "q_pub": expected["q_pub"],
        "rho": expected["rho"],
        "compatibility": expected["compatibility"],
        "matrix_table": expected["matrix_table"],
        "edge_time_table": expected["edge_time_table"],
        "clock_table": expected["clock_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_time_map table mismatch: {key}")

    if report.get("schema") != "long.time_map.report@1":
        raise AssertionError("long_time_map report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_time_map report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_time_map all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_time_map checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_time_map report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_time_map report hash mismatch")

    csv_shapes = [
        ("matrix.csv", MATRIX_COLUMNS, 38),
        ("edge_time.csv", EDGE_TIME_COLUMNS, 642),
        ("clock.csv", CLOCK_COLUMNS, len(CLOCK_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_time_map {filename} shape mismatch")

    table_shapes = {
        "tau_int": (1, 36),
        "q_pub": (1, 20),
        "rho": (20, 36),
        "compatibility": (1, 36),
        "matrix_table": (38, len(MATRIX_COLUMNS)),
        "edge_time_table": (642, len(EDGE_TIME_COLUMNS)),
        "clock_table": (len(CLOCK_CODES), len(CLOCK_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_time_map {key} shape mismatch")

    tau_int = np.asarray(tables["tau_int"])
    q_pub = np.asarray(tables["q_pub"])
    rho = np.asarray(tables["rho"])
    compatibility = np.asarray(tables["compatibility"])
    if not np.array_equal(q_pub @ rho, tau_int):
        raise AssertionError("long_time_map compatibility identity mismatch")
    if not np.array_equal(compatibility, np.zeros((1, 36), dtype=np.int64)):
        raise AssertionError("long_time_map compatibility defect mismatch")
    if int(np.linalg.matrix_rank(rho)) != 20:
        raise AssertionError("long_time_map rho rank mismatch")
    if not (
        int(tau_int[0, 0]) == 1
        and int(q_pub[0, 0]) == 1
        and int(rho[0, 0]) == 1
        and np.all(tau_int[0, 1:] == 0)
        and np.all(q_pub[0, 1:] == 0)
        and np.all(rho[0, 1:] == 0)
    ):
        raise AssertionError("long_time_map kernel annihilation mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "operation_algebra_dimension": 36,
        "integrity_integral_codimension": 35,
        "integrity_integral_dimension": 1,
        "public_rank": 20,
        "public_kernel_dimension": 19,
        "public_quotient_dimension": 1,
        "tau_int_row_count": 1,
        "tau_int_col_count": 36,
        "q_pub_row_count": 1,
        "q_pub_col_count": 20,
        "rho_row_count": 20,
        "rho_col_count": 36,
        "rho_rank": 20,
        "compatibility_defect_l1": 0,
        "matrix_nonzero_entry_count": 38,
        "recurrence_edge_count": 642,
        "edge_time_count": 642,
        "unit_delta_edge_count": 642,
        "time_tick_total": 642,
        "packet_normalization": 32,
        "full_packet_count": 20,
        "packet_remainder": 2,
        "normal_form_time_map_flag": 1,
        "semantic_edge_operation_flag": 0,
        "smooth_lorentzian_metric_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 4,
        "next_gap_code": GAP_CODES["semantic_edge_operation_realization_from_a985"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_time_map observable {key} mismatch")

    edge_time_rows = rows_from_table(
        np.asarray(tables["edge_time_table"]), EDGE_TIME_COLUMNS
    )
    if [row["edge_id"] for row in edge_time_rows] != list(range(642)):
        raise AssertionError("long_time_map edge ids mismatch")
    if any(row["delta_t"] != 1 for row in edge_time_rows):
        raise AssertionError("long_time_map edge delta_t mismatch")
    if any(row["compatibility_flag"] != 1 for row in edge_time_rows):
        raise AssertionError("long_time_map edge compatibility mismatch")
    if edge_time_rows[-1]["accumulated_time"] != 642:
        raise AssertionError("long_time_map accumulated time mismatch")
    if edge_time_rows[-1]["packet_index"] != 20:
        raise AssertionError("long_time_map final packet index mismatch")
    if edge_time_rows[-1]["packet_phase"] != 1:
        raise AssertionError("long_time_map final packet phase mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if any(row["certified_flag"] != 0 for row in gap_rows):
        raise AssertionError("long_time_map gap closure mismatch")
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["obligation_code"]
        != GAP_CODES["semantic_edge_operation_realization_from_a985"]
    ):
        raise AssertionError("long_time_map next gap mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "integrity_summary": INTEGRITY_SUMMARY,
        "long_lor": LONG_LOR,
        "long_rec": LONG_REC,
        "long_rec_edge": LONG_REC_EDGE,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.time_map.manifest@1":
        raise AssertionError("long_time_map manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_time_map manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_time_map manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_time_map missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_time_map proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_time_map proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.time_map.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "matrix_code_map": witness.get("matrix_code_map"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_time_map(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
