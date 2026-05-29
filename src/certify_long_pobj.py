from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_long_pobj import (
        CANDIDATE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_COMP_PAIR,
        LONG_COMP_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_long_pobj import (
        CANDIDATE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LONG_COMP_PAIR,
        LONG_COMP_PATH,
        LONG_COMP_REPORT,
        LONG_COMP_TABLES,
        LONG_COMP_TRANSITION,
        LONG_PATH_COMPONENT,
        LONG_PATH_PATH,
        LONG_PATH_REPORT,
        LONG_PATH_STEP,
        LONG_PATH_TABLES,
        LONG_TENS_FIBER,
        LONG_TENS_REPORT,
        LONG_TENS_TABLES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
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


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def validate_long_pobj() -> dict[str, Any]:
    expected = build_payloads()
    pobj_payload = load_json(OUT_DIR / "pobj.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if pobj_payload != expected["pobj"]:
        raise AssertionError("long_pobj pobj JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_pobj cert mismatch")
    for filename, key in {
        "candidate.csv": "candidate_csv",
        "pair.csv": "pair_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_pobj {filename} mismatch")

    for key, expected_array in {
        "candidate_table": expected["candidate_table"],
        "pair_table": expected["pair_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_pobj table mismatch: {key}")

    if report.get("schema") != "long.pobj.report@1":
        raise AssertionError("long_pobj report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_pobj report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_pobj all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_pobj checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_pobj report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_pobj report hash mismatch")

    csv_shapes = [
        ("candidate.csv", CANDIDATE_COLUMNS, 3),
        ("pair.csv", PAIR_COLUMNS, 9),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_pobj {filename} shape mismatch")

    table_shapes = {
        "candidate_table": (3, len(CANDIDATE_COLUMNS)),
        "pair_table": (9, len(PAIR_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_pobj {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "candidate_row_count": 3,
        "component_count": 3,
        "component_pair_count": 9,
        "zeta_component_pair_count": 7,
        "exact_component_pair_count": 0,
        "identity_component_count": 0,
        "path_count": 288,
        "gap_path_count": 208,
        "existing_path_count": 80,
        "step_row_count": 3_128,
        "transition_count": 2_840,
        "zeta_transition_count": 2_840,
        "zeta_path_count": 288,
        "exact_transition_count": 0,
        "exact_path_count": 0,
        "total_component_path_count": 64_570_080,
        "selected_component_path_count": 288,
        "missing_component_path_count": 64_569_792,
        "gap_component_path_count": 64_560_240,
        "selected_gap_path_count": 208,
        "closed_path_object_flag": 0,
        "sample_zeta_section_flag": 1,
        "full_component_path_materialized_flag": 0,
        "next_target_code": 4,
        "complete_goal_claim_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_pobj observable {key} mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if [row["candidate_code"] for row in candidate_rows] != [0, 1, 2]:
        raise AssertionError("long_pobj candidate code order mismatch")
    if any(row["closed_path_object_flag"] != 0 for row in candidate_rows):
        raise AssertionError("long_pobj candidate unexpectedly closes")
    pair_rows = rows_from_table(np.asarray(tables["pair_table"]), PAIR_COLUMNS)
    if sum(row["zeta_both_flag"] for row in pair_rows) != 7:
        raise AssertionError("long_pobj zeta pair count mismatch")
    if sum(row["exact_any_flag"] for row in pair_rows) != 0:
        raise AssertionError("long_pobj exact pair count mismatch")

    inputs = report.get("inputs", {})
    for key, path in {
        "long_path_report": LONG_PATH_REPORT,
        "long_path_component": LONG_PATH_COMPONENT,
        "long_path_path": LONG_PATH_PATH,
        "long_path_step": LONG_PATH_STEP,
        "long_path_tables": LONG_PATH_TABLES,
        "long_comp_report": LONG_COMP_REPORT,
        "long_comp_path": LONG_COMP_PATH,
        "long_comp_pair": LONG_COMP_PAIR,
        "long_comp_transition": LONG_COMP_TRANSITION,
        "long_comp_tables": LONG_COMP_TABLES,
        "long_tens_report": LONG_TENS_REPORT,
        "long_tens_fiber": LONG_TENS_FIBER,
        "long_tens_tables": LONG_TENS_TABLES,
        "derive_script": DERIVE_SCRIPT,
        "validator": VALIDATOR_SCRIPT,
    }.items():
        assert_file_hash(inputs.get(key, {}), path, key)

    if manifest.get("schema") != "long.pobj.manifest@1":
        raise AssertionError("long_pobj manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_pobj manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("long_pobj manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("long_pobj missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_pobj proof obligation index hash mismatch")
    if entry.get("status") != STATUS:
        raise AssertionError("long_pobj proof obligation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    witness = report.get("witness", {})
    return {
        "schema": "long.pobj.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report["certificate_sha256"],
        "witness": {
            "classification": witness.get("classification"),
            "summary": witness.get("summary"),
            "candidate_code_map": witness.get("candidate_code_map"),
        },
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    print(json.dumps(validate_long_pobj(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
