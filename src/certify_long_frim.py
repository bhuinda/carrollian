from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_frim import (
        INDEX_PATH,
        LONG_F63,
        LONG_F63_ATOM,
        LONG_PSEL,
        LONG_RIM,
        LONG_RIM_ORBIT,
        LONG_RIM_PHASE,
        LONG_RIM_SELECT,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RIM_COLUMNS,
        SELECTOR_CODES,
        SELECTOR_COLUMNS,
        SPINE_COLUMNS,
        STATUS,
        STRUCTURE_CODES,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_frim import (
        INDEX_PATH,
        LONG_F63,
        LONG_F63_ATOM,
        LONG_PSEL,
        LONG_RIM,
        LONG_RIM_ORBIT,
        LONG_RIM_PHASE,
        LONG_RIM_SELECT,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RIM_COLUMNS,
        SELECTOR_CODES,
        SELECTOR_COLUMNS,
        SPINE_COLUMNS,
        STATUS,
        STRUCTURE_CODES,
        THEOREM_ID,
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


def validate_long_frim() -> dict[str, Any]:
    expected = build_payloads()
    frim = load_json(OUT_DIR / "frim.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if frim != expected["frim"]:
        raise AssertionError("long_frim JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_frim cert mismatch")
    for filename, key in {
        "spine.csv": "spine_csv",
        "selector.csv": "selector_csv",
        "rim.csv": "rim_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_frim {filename} mismatch")

    for key, expected_array in {
        "spine_table": expected["spine_table"],
        "selector_table": expected["selector_table"],
        "rim_table": expected["rim_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_frim table mismatch: {key}")

    if report.get("schema") != "long.frim.report@1":
        raise AssertionError("long_frim report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_frim report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_frim all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_frim checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_frim report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_frim report hash mismatch")

    csv_shapes = [
        ("spine.csv", SPINE_COLUMNS, len(STRUCTURE_CODES)),
        ("selector.csv", SELECTOR_COLUMNS, len(SELECTOR_CODES)),
        ("rim.csv", RIM_COLUMNS, 124),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_frim {filename} shape mismatch")

    table_shapes = {
        "spine_table": (len(STRUCTURE_CODES), len(SPINE_COLUMNS)),
        "selector_table": (len(SELECTOR_CODES), len(SELECTOR_COLUMNS)),
        "rim_table": (124, len(RIM_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_frim {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "atom_count": 20,
        "johnson_pair_count": 90,
        "nonedge_pair_count": 90,
        "complement_pair_count": 10,
        "s6_coordinate_permutation_count": 720,
        "s6_preserves_grade_three_count": 720,
        "s6_preserves_johnson_count": 720,
        "s6_preserves_complement_count": 720,
        "rim_orbit_count": 124,
        "rim_edge_fail_count": 0,
        "rim_complement_fail_count": 0,
        "defect_class_count": 63,
        "golden_class_id": 0,
        "directed_stress_selected_class_id": 41,
        "undirected_stress_selected_class_count": 19,
        "weight_stress_selected_class_id": 58,
        "golden_selected_by_stress_flag": 0,
        "stress_unique_selector_count": 2,
        "stress_selector_count": 3,
        "transition_shared_key_count": 0,
        "semantic_transition_operation_flag": 0,
        "physical_selector_axiom_flag": 0,
        "physical_selector_candidate_count": 0,
        "coordinate_spine_rim_lift_flag": 1,
        "physical_rim_selector_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_frim observable {key} mismatch")

    spine_rows = rows_from_table(np.asarray(tables["spine_table"]), SPINE_COLUMNS)
    if any(row["pass_flag"] != 1 for row in spine_rows):
        raise AssertionError("long_frim spine pass marker mismatch")

    selector_rows = rows_from_table(
        np.asarray(tables["selector_table"]), SELECTOR_COLUMNS
    )
    if any(row["physical_selector_flag"] != 0 for row in selector_rows):
        raise AssertionError("long_frim physical selector marker mismatch")
    if any(row["transition_coupled_flag"] != 0 for row in selector_rows):
        raise AssertionError("long_frim transition coupling marker mismatch")
    if sum(row["stress_flag"] for row in selector_rows) != 3:
        raise AssertionError("long_frim stress selector marker mismatch")
    if any(row["obstruction_flag"] != 1 for row in selector_rows):
        raise AssertionError("long_frim obstruction marker mismatch")

    rim_rows = rows_from_table(np.asarray(tables["rim_table"]), RIM_COLUMNS)
    if any(row["pass_flag"] != 1 for row in rim_rows):
        raise AssertionError("long_frim rim pass marker mismatch")
    if any(row["edge_fail_count"] != 0 or row["complement_fail_count"] != 0 for row in rim_rows):
        raise AssertionError("long_frim rim failure count mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_frim manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_frim manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_frim manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_f63": LONG_F63,
        "long_f63_atom": LONG_F63_ATOM,
        "long_rim": LONG_RIM,
        "long_rim_orbit": LONG_RIM_ORBIT,
        "long_rim_select": LONG_RIM_SELECT,
        "long_rim_phase": LONG_RIM_PHASE,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_psel": LONG_PSEL,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_frim index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_frim index report hash mismatch")

    return {
        "schema": "long.frim.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_frim(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
