from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_metric_rank_gate import (
        DECISION_CODES,
        DECISION_COLUMNS,
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_LOR,
        LONG_METRIC_GATE,
        LONG_STRESS_COUPLE,
        LONG_STRESS_GATE,
        LONG_TIME_MAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RANK_CODES,
        RANK_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_metric_rank_gate import (
        DECISION_CODES,
        DECISION_COLUMNS,
        DERIVE_SCRIPT,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_LOR,
        LONG_METRIC_GATE,
        LONG_STRESS_COUPLE,
        LONG_STRESS_GATE,
        LONG_TIME_MAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RANK_CODES,
        RANK_COLUMNS,
        STATUS,
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


def validate_long_metric_rank_gate() -> dict[str, Any]:
    expected = build_payloads()
    metric_rank_gate = load_json(OUT_DIR / "metric_rank_gate.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if metric_rank_gate != expected["metric_rank_gate"]:
        raise AssertionError("long_metric_rank_gate JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_metric_rank_gate cert mismatch")
    for filename, key in {
        "rank.csv": "rank_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_metric_rank_gate {filename} mismatch")

    for key, expected_array in {
        "rank_table": expected["rank_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_metric_rank_gate table mismatch: {key}")

    if report.get("schema") != "long.metric_rank_gate.report@1":
        raise AssertionError("long_metric_rank_gate report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_metric_rank_gate report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_metric_rank_gate all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_metric_rank_gate checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_metric_rank_gate report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_metric_rank_gate report hash mismatch")

    csv_shapes = [
        ("rank.csv", RANK_COLUMNS, len(RANK_CODES)),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_metric_rank_gate {filename} shape mismatch")

    table_shapes = {
        "rank_table": (len(RANK_CODES), len(RANK_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_metric_rank_gate {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 6,
        "input_certified_count": 6,
        "operation_algebra_dimension": 36,
        "integrity_kernel_dimension": 35,
        "time_rank": 1,
        "public_rank": 20,
        "public_kernel_dimension": 19,
        "public_quotient_dimension": 1,
        "rho_rank": 20,
        "normal_form_tick_count": 642,
        "transition_row_count": 642,
        "finite_stress_node_count": 20,
        "finite_stress_edge_count": 100,
        "finite_rank_split_flag": 1,
        "one_plus_nineteen_formal_split_flag": 1,
        "three_spatial_rank_flag": 0,
        "four_dimensional_spacetime_flag": 0,
        "smooth_metric_signature_flag": 0,
        "stress_energy_flag": 0,
        "curvature_einstein_flag": 0,
        "gr_derivation_flag": 0,
        "open_gap_count": 5,
        "next_gap_code": GAP_CODES["four_dimensional_spacetime_reduction"],
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_metric_rank_gate observable {key} mismatch")

    rank_rows = rows_from_table(np.asarray(tables["rank_table"]), RANK_COLUMNS)
    if [row["rank_row_id"] for row in rank_rows] != list(range(len(RANK_CODES))):
        raise AssertionError("long_metric_rank_gate rank ids mismatch")
    public_rows = [
        row
        for row in rank_rows
        if row["rank_code"] == RANK_CODES["public_integral_trace_rank"]
    ]
    if (
        len(public_rows) != 1
        or public_rows[0]["ambient_rank"] != 20
        or public_rows[0]["kernel_rank"] != 19
        or public_rows[0]["quotient_rank"] != 1
    ):
        raise AssertionError("long_metric_rank_gate public rank row mismatch")
    four_rows = [
        row
        for row in rank_rows
        if row["rank_code"] == RANK_CODES["four_dimensional_reduction_candidate"]
    ]
    if (
        len(four_rows) != 1
        or four_rows[0]["certified_flag"] != 0
        or four_rows[0]["obstruction_flag"] != 1
    ):
        raise AssertionError("long_metric_rank_gate 4d rank row mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if any(row["pass_flag"] != 1 for row in decision_rows):
        raise AssertionError("long_metric_rank_gate decision pass mismatch")
    obstructed_decisions = [
        DECISION_CODES["four_dimensional_reduction_certified"],
        DECISION_CODES["smooth_lorentzian_signature_certified"],
        DECISION_CODES["stress_energy_source_certified"],
        DECISION_CODES["gr_derivation_certified"],
    ]
    if any(
        decision_rows[code]["certified_flag"] != 0
        or decision_rows[code]["obstruction_flag"] != 1
        for code in obstructed_decisions
    ):
        raise AssertionError("long_metric_rank_gate obstructed decision mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    next_rows = [row for row in gap_rows if row["next_flag"] == 1]
    if (
        len(next_rows) != 1
        or next_rows[0]["gap_code"]
        != GAP_CODES["four_dimensional_spacetime_reduction"]
    ):
        raise AssertionError("long_metric_rank_gate next gap mismatch")
    if sum(row["open_flag"] for row in gap_rows) != 5:
        raise AssertionError("long_metric_rank_gate open gap count mismatch")
    closed_rows = [
        row for row in gap_rows if row["gap_code"] == GAP_CODES["finite_rank_split"]
    ]
    if (
        len(closed_rows) != 1
        or closed_rows[0]["open_flag"] != 0
        or closed_rows[0]["obstruction_flag"] != 0
    ):
        raise AssertionError("long_metric_rank_gate finite split gap mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_lor": LONG_LOR,
        "long_time_map": LONG_TIME_MAP,
        "long_metric_gate": LONG_METRIC_GATE,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_couple": LONG_STRESS_COUPLE,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.metric_rank_gate.manifest@1":
        raise AssertionError("long_metric_rank_gate manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_metric_rank_gate manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_metric_rank_gate manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_metric_rank_gate missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError(
            "long_metric_rank_gate proof obligation index hash mismatch"
        )
    if entry.get("status") != STATUS:
        raise AssertionError(
            "long_metric_rank_gate proof obligation index status mismatch"
        )
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.metric_rank_gate.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "rank_code_map": witness.get("rank_code_map"),
            "gap_code_map": witness.get("gap_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_metric_rank_gate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
