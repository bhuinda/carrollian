from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3o import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3V,
        LONG_C59P3V_MAX,
        LONG_C59P3V_SUPPORT,
        LONG_C59PK,
        LONG_STRESS_COUPLE,
        LONG_TIME_MAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        TEST_CODES,
        TEST_COLUMNS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3o import (
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3V,
        LONG_C59P3V_MAX,
        LONG_C59P3V_SUPPORT,
        LONG_C59PK,
        LONG_STRESS_COUPLE,
        LONG_TIME_MAP,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        PAIR_COLUMNS,
        STATUS,
        TEST_CODES,
        TEST_COLUMNS,
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


def validate_long_c59p3o() -> dict[str, Any]:
    expected = build_payloads()
    c59p3o = load_json(OUT_DIR / "c59p3o.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3o != expected["c59p3o"]:
        raise AssertionError("long_c59p3o JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3o cert mismatch")
    for filename, key in {
        "pair.csv": "pair_csv",
        "test.csv": "test_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3o {filename} mismatch")

    for key, expected_array in {
        "pair_table": expected["pair_table"],
        "test_table": expected["test_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3o table mismatch: {key}")

    if report.get("schema") != "long.c59p3o.report@1":
        raise AssertionError("long_c59p3o report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3o report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3o all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3o checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3o report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3o report hash mismatch")

    csv_shapes = [
        ("pair.csv", PAIR_COLUMNS, 1),
        ("test.csv", TEST_COLUMNS, len(TEST_CODES)),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3o {filename} shape mismatch")

    table_shapes = {
        "pair_table": (1, len(PAIR_COLUMNS)),
        "test_table": (len(TEST_CODES), len(TEST_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3o {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "orientation_candidate_count": 2,
        "same_support_flag": 1,
        "opposite_det_sign_flag": 1,
        "equal_abs_volume_flag": 1,
        "sign_dual_pair_flag": 1,
        "time_trace_removed_flag": 1,
        "normal_form_time_map_flag": 1,
        "time_orientation_distinguishing_flag": 0,
        "semantic_transition_operation_flag": 0,
        "semantic_transition_orientation_distinguishing_flag": 0,
        "stress_coupling_map_certified_flag": 0,
        "shared_stress_coupling_key_count": 0,
        "stress_orientation_distinguishing_flag": 0,
        "physical_orientation_selector_flag": 0,
        "current_orientation_obstruction_flag": 1,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3o observable {key} mismatch")

    pair_rows = rows_from_table(np.asarray(tables["pair_table"]), PAIR_COLUMNS)
    pair = pair_rows[0]
    if [
        pair["positive_candidate_a"],
        pair["positive_candidate_b"],
        pair["positive_candidate_c"],
    ] != [48, 180, 235]:
        raise AssertionError("long_c59p3o positive candidate mismatch")
    if [
        pair["negative_candidate_a"],
        pair["negative_candidate_b"],
        pair["negative_candidate_c"],
    ] != [49, 181, 234]:
        raise AssertionError("long_c59p3o negative candidate mismatch")
    if [
        pair["same_support_flag"],
        pair["opposite_det_sign_flag"],
        pair["equal_abs_volume_flag"],
        pair["sign_dual_pair_flag"],
    ] != [1, 1, 1, 1]:
        raise AssertionError("long_c59p3o pair flag mismatch")

    test_rows = rows_from_table(np.asarray(tables["test_table"]), TEST_COLUMNS)
    if [row["test_id"] for row in test_rows] != list(range(len(TEST_CODES))):
        raise AssertionError("long_c59p3o test order mismatch")
    if [row["distinguishes_flag"] for row in test_rows] != [0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3o distinguish vector mismatch")
    if [row["certified_flag"] for row in test_rows] != [1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3o certified test vector mismatch")
    if [row["next_flag"] for row in test_rows] != [0, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3o next test vector mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59p3o decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 0, 0, 0, 0, 1]:
        raise AssertionError("long_c59p3o decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 1, 1, 1, 1, 0]:
        raise AssertionError("long_c59p3o decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3o gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3o gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3o manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3o manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3o manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3v": LONG_C59P3V,
        "long_c59p3v_max": LONG_C59P3V_MAX,
        "long_c59p3v_support": LONG_C59P3V_SUPPORT,
        "long_c59pk": LONG_C59PK,
        "long_time_map": LONG_TIME_MAP,
        "long_transition_sem": LONG_TRANSITION_SEM,
        "long_stress_couple": LONG_STRESS_COUPLE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3o index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3o index report hash mismatch")

    return {
        "schema": "long.c59p3o.verification@1",
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
    print(json.dumps(validate_long_c59p3o(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
