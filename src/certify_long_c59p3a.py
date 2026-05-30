from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59p3a import (
        COEFF_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3O,
        LONG_C59P3V,
        LONG_C59P3V_SUPPORT,
        LONG_STRESS_COUPLE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OVERLAP_COLUMNS,
        SCORE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59p3a import (
        COEFF_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59P3O,
        LONG_C59P3V,
        LONG_C59P3V_SUPPORT,
        LONG_STRESS_COUPLE,
        LONG_STRESS_EDGE,
        LONG_STRESS_GATE,
        LONG_TRANSITION_SEM,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        OVERLAP_COLUMNS,
        SCORE_COLUMNS,
        STATUS,
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


def validate_long_c59p3a() -> dict[str, Any]:
    expected = build_payloads()
    c59p3a = load_json(OUT_DIR / "c59p3a.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59p3a != expected["c59p3a"]:
        raise AssertionError("long_c59p3a JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59p3a cert mismatch")
    for filename, key in {
        "coeff.csv": "coeff_csv",
        "overlap.csv": "overlap_csv",
        "score.csv": "score_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59p3a {filename} mismatch")

    for key, expected_array in {
        "coeff_table": expected["coeff_table"],
        "overlap_table": expected["overlap_table"],
        "score_table": expected["score_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59p3a table mismatch: {key}")

    if report.get("schema") != "long.c59p3a.report@1":
        raise AssertionError("long_c59p3a report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59p3a report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59p3a all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59p3a checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3a report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59p3a report hash mismatch")

    csv_shapes = [
        ("coeff.csv", COEFF_COLUMNS, 12),
        ("overlap.csv", OVERLAP_COLUMNS, 14),
        ("score.csv", SCORE_COLUMNS, 2),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59p3a {filename} shape mismatch")

    table_shapes = {
        "coeff_table": (12, len(COEFF_COLUMNS)),
        "overlap_table": (14, len(OVERLAP_COLUMNS)),
        "score_table": (2, len(SCORE_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59p3a {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 5,
        "input_certified_count": 5,
        "selector_count": 2,
        "support_row_count": 12,
        "shared_support_atom_count": 6,
        "overlap_row_count": 14,
        "positive_overlap_edge_count": 7,
        "negative_overlap_edge_count": 7,
        "positive_signed_tension_score_scaled": 13_946_765_269,
        "negative_signed_tension_score_scaled": -15_571_590_835,
        "signed_tension_score_difference_scaled": 29_518_356_104,
        "positive_weight_score_scaled": 2_091_452_573,
        "negative_weight_score_scaled": -570_092_413,
        "positive_abs_tension_score_scaled": -4_212_866_815,
        "negative_abs_tension_score_scaled": 5_837_692_381,
        "selected_selector_id": 0,
        "selected_selector_code": 0,
        "atom_overlap_orientation_candidate_flag": 1,
        "transition_stress_map_certified_flag": 0,
        "semantic_transition_operation_flag": 0,
        "physical_selector_axiom_flag": 0,
        "four_dimensional_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59p3a observable {key} mismatch")

    coeff_rows = rows_from_table(np.asarray(tables["coeff_table"]), COEFF_COLUMNS)
    if sorted({row["source_atom"] for row in coeff_rows if row["selector_id"] == 0}) != [
        1,
        7,
        10,
        11,
        14,
        18,
    ]:
        raise AssertionError("long_c59p3a positive support atoms mismatch")
    if sorted({row["source_atom"] for row in coeff_rows if row["selector_id"] == 1}) != [
        1,
        7,
        10,
        11,
        14,
        18,
    ]:
        raise AssertionError("long_c59p3a negative support atoms mismatch")

    overlap_rows = rows_from_table(
        np.asarray(tables["overlap_table"]), OVERLAP_COLUMNS
    )
    if [row["stress_edge_id"] for row in overlap_rows if row["selector_id"] == 0] != [
        5,
        38,
        52,
        56,
        72,
        74,
        90,
    ]:
        raise AssertionError("long_c59p3a positive overlap edges mismatch")
    if [row["stress_edge_id"] for row in overlap_rows if row["selector_id"] == 1] != [
        5,
        38,
        52,
        56,
        72,
        74,
        90,
    ]:
        raise AssertionError("long_c59p3a negative overlap edges mismatch")
    if sum(
        row["signed_tension_contribution_scaled"]
        for row in overlap_rows
        if row["selector_id"] == 0
    ) != 13_946_765_269:
        raise AssertionError("long_c59p3a positive score mismatch")
    if sum(
        row["signed_tension_contribution_scaled"]
        for row in overlap_rows
        if row["selector_id"] == 1
    ) != -15_571_590_835:
        raise AssertionError("long_c59p3a negative score mismatch")

    score_rows = rows_from_table(np.asarray(tables["score_table"]), SCORE_COLUMNS)
    if [row["selected_by_signed_tension_flag"] for row in score_rows] != [1, 0]:
        raise AssertionError("long_c59p3a score selected vector mismatch")
    if [row["transition_stress_map_flag"] for row in score_rows] != [0, 0]:
        raise AssertionError("long_c59p3a transition-stress flag mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59p3a decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59p3a decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 1, 1, 1]:
        raise AssertionError("long_c59p3a decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3a gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59p3a gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59p3a manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59p3a manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3a manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59p3o": LONG_C59P3O,
        "long_c59p3v": LONG_C59P3V,
        "long_c59p3v_support": LONG_C59P3V_SUPPORT,
        "long_stress_gate": LONG_STRESS_GATE,
        "long_stress_edge": LONG_STRESS_EDGE,
        "long_stress_couple": LONG_STRESS_COUPLE,
        "long_transition_sem": LONG_TRANSITION_SEM,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59p3a index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59p3a index report hash mismatch")

    return {
        "schema": "long.c59p3a.verification@1",
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
    print(json.dumps(validate_long_c59p3a(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
