from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_raw import rows_from_table
    from .derive_long_sfork import (
        BRANCH_CODES,
        BRANCH_COLUMNS,
        CLASS_COLUMNS,
        FAILURE_CODES,
        INDEX_PATH,
        LONG_FRIM,
        LONG_FRIM_SELECTOR,
        LONG_GLAW,
        LONG_TLIFT,
        LONG_ABMAP,
        LONG_RTICK,
        LONG_RSEM,
        LONG_PSEL,
        LONG_RIM_CLASS,
        LONG_RIM_PHASE,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_raw import rows_from_table
    from derive_long_sfork import (
        BRANCH_CODES,
        BRANCH_COLUMNS,
        CLASS_COLUMNS,
        FAILURE_CODES,
        INDEX_PATH,
        LONG_FRIM,
        LONG_FRIM_SELECTOR,
        LONG_GLAW,
        LONG_TLIFT,
        LONG_ABMAP,
        LONG_RTICK,
        LONG_RSEM,
        LONG_PSEL,
        LONG_RIM_CLASS,
        LONG_RIM_PHASE,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
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


def validate_long_sfork() -> dict[str, Any]:
    expected = build_payloads()
    sfork = load_json(OUT_DIR / "sfork.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if sfork != expected["sfork"]:
        raise AssertionError("long_sfork JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_sfork cert mismatch")
    for filename, key in {
        "branch.csv": "branch_csv",
        "class.csv": "class_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_sfork {filename} mismatch")

    for key, expected_array in {
        "branch_table": expected["branch_table"],
        "class_table": expected["class_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_sfork table mismatch: {key}")

    if report.get("schema") != "long.sfork.report@1":
        raise AssertionError("long_sfork report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_sfork report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_sfork all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_sfork checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sfork report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_sfork report hash mismatch")

    csv_shapes = [
        ("branch.csv", BRANCH_COLUMNS, len(BRANCH_CODES)),
        ("class.csv", CLASS_COLUMNS, 3),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_sfork {filename} shape mismatch")

    table_shapes = {
        "branch_table": (len(BRANCH_CODES), len(BRANCH_COLUMNS)),
        "class_table": (3, len(CLASS_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_sfork {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 8,
        "input_certified_count": 8,
        "branch_count": 7,
        "viable_branch_count": 0,
        "golden_class_id": 0,
        "directed_stress_class_id": 41,
        "weight_stress_class_id": 58,
        "undirected_stress_class_count": 19,
        "existing_selector_class_count": 0,
        "transition_shared_key_count": 0,
        "semantic_transition_operation_flag": 0,
        "physical_selector_axiom_flag": 0,
        "physical_selector_candidate_count": 1,
        "golden_selector_law_flag": 1,
        "affine_tick_full_lift_candidate_count": 0,
        "affine_tick_best_candidate_covered_ticks": 7,
        "affine_tick_lift_obstruction_flag": 1,
        "golden_atom_basis_lift_ready_flag": 0,
        "atom_basis_relation_cover_flag": 1,
        "atom_basis_functor_obstruction_flag": 1,
        "golden_atom_basis_functor_ready_flag": 0,
        "relation_tick_cover_flag": 1,
        "relation_valued_semantic_law_flag": 1,
        "golden_relation_semantic_ready_flag": 1,
        "non_golden_physical_policy_flag": 0,
        "stress_branch_ready_count": 0,
        "golden_branch_ready_flag": 0,
        "common_transition_blocker_flag": 1,
        "common_physical_selector_blocker_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_sfork observable {key} mismatch")

    branch_rows = rows_from_table(np.asarray(tables["branch_table"]), BRANCH_COLUMNS)
    if any(row["viable_flag"] != 0 for row in branch_rows):
        raise AssertionError("long_sfork viable marker mismatch")
    expected_failures = [
        FAILURE_CODES["physical_selector_axiom_absent"],
        FAILURE_CODES["non_golden_policy_absent"],
        FAILURE_CODES["non_golden_policy_absent"],
        FAILURE_CODES["unique_selector_absent"],
        FAILURE_CODES["existing_selector_absent"],
        FAILURE_CODES["existing_selector_absent"],
        FAILURE_CODES["physical_selector_axiom_absent"],
    ]
    if [row["first_failure_code"] for row in branch_rows] != expected_failures:
        raise AssertionError("long_sfork first-failure vector mismatch")

    class_rows = rows_from_table(np.asarray(tables["class_table"]), CLASS_COLUMNS)
    if [row["class_id"] for row in class_rows] != [0, 41, 58]:
        raise AssertionError("long_sfork branch class order mismatch")
    if [row["golden_flag"] for row in class_rows] != [1, 0, 0]:
        raise AssertionError("long_sfork branch golden marker mismatch")
    if [row["stress_global_flag_count"] for row in class_rows] != [0, 2, 2]:
        raise AssertionError("long_sfork stress flag count mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_sfork manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_sfork manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sfork manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_frim": LONG_FRIM,
        "long_frim_selector": LONG_FRIM_SELECTOR,
        "long_glaw": LONG_GLAW,
        "long_tlift": LONG_TLIFT,
        "long_abmap": LONG_ABMAP,
        "long_rtick": LONG_RTICK,
        "long_rsem": LONG_RSEM,
        "long_rim_class": LONG_RIM_CLASS,
        "long_rim_phase": LONG_RIM_PHASE,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_psel": LONG_PSEL,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_sfork index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_sfork index report hash mismatch")

    return {
        "schema": "long.sfork.verification@1",
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
    print(json.dumps(validate_long_sfork(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
