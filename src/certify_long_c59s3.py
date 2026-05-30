from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c59s3 import (
        CANDIDATE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        DETERMINANT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59PK,
        LONG_C59PK_BASIS,
        LONG_C59PK_RESTRICTED,
        LONG_DIM4_GATE,
        LONG_SEL,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        SUBFORM_COLUMNS,
        SUMMARY_COLUMNS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c59s3 import (
        CANDIDATE_COLUMNS,
        DECISION_CODES,
        DECISION_COLUMNS,
        DETERMINANT_COLUMNS,
        GAP_CODES,
        GAP_COLUMNS,
        INDEX_PATH,
        LONG_C59PK,
        LONG_C59PK_BASIS,
        LONG_C59PK_RESTRICTED,
        LONG_DIM4_GATE,
        LONG_SEL,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        STATUS,
        SUBFORM_COLUMNS,
        SUMMARY_COLUMNS,
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


def validate_long_c59s3() -> dict[str, Any]:
    expected = build_payloads()
    c59s3 = load_json(OUT_DIR / "c59s3.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c59s3 != expected["c59s3"]:
        raise AssertionError("long_c59s3 JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c59s3 cert mismatch")
    for filename, key in {
        "subform.csv": "subform_csv",
        "determinant.csv": "determinant_csv",
        "candidate.csv": "candidate_csv",
        "summary.csv": "summary_csv",
        "decision.csv": "decision_csv",
        "gap.csv": "gap_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c59s3 {filename} mismatch")

    for key, expected_array in {
        "subform_table": expected["subform_table"],
        "candidate_table": expected["candidate_table"],
        "summary_table": expected["summary_table"],
        "decision_table": expected["decision_table"],
        "gap_table": expected["gap_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c59s3 table mismatch: {key}")

    if report.get("schema") != "long.c59s3.report@1":
        raise AssertionError("long_c59s3 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c59s3 report status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c59s3 all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c59s3 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59s3 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c59s3 report hash mismatch")

    csv_shapes = [
        ("subform.csv", SUBFORM_COLUMNS, 816),
        ("determinant.csv", DETERMINANT_COLUMNS, 816),
        ("candidate.csv", CANDIDATE_COLUMNS, 11),
        ("summary.csv", SUMMARY_COLUMNS, 1),
        ("decision.csv", DECISION_COLUMNS, len(DECISION_CODES)),
        ("gap.csv", GAP_COLUMNS, len(GAP_CODES)),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c59s3 {filename} shape mismatch")

    table_shapes = {
        "subform_table": (816, len(SUBFORM_COLUMNS)),
        "candidate_table": (11, len(CANDIDATE_COLUMNS)),
        "summary_table": (1, len(SUMMARY_COLUMNS)),
        "decision_table": (len(DECISION_CODES), len(DECISION_COLUMNS)),
        "gap_table": (len(GAP_CODES), len(GAP_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c59s3 {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 3,
        "input_certified_count": 3,
        "restricted_dimension": 18,
        "principal_three_subform_count": 816,
        "rank3_subform_count": 11,
        "rank2_subform_count": 426,
        "rank1_subform_count": 0,
        "rank0_subform_count": 379,
        "positive_definite_count": 0,
        "negative_definite_count": 0,
        "definite_spatial_count": 0,
        "inertia_210_count": 8,
        "inertia_120_count": 3,
        "unique_max_abs_det_flag": 1,
        "max_abs_det_subform_id": 119,
        "max_abs_det_inertia_positive": 2,
        "max_abs_det_inertia_negative": 1,
        "physical_selector_axiom_flag": 0,
        "dim4_reduction_certified_flag": 0,
        "canonical_three_spatial_selection_flag": 0,
        "four_dimensional_metric_flag": 0,
        "physical_stress_energy_flag": 0,
        "smooth_metric_flag": 0,
        "thermal_gravity_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c59s3 observable {key} mismatch")

    subform_rows = rows_from_table(np.asarray(tables["subform_table"]), SUBFORM_COLUMNS)
    if [row["subform_id"] for row in subform_rows] != list(range(816)):
        raise AssertionError("long_c59s3 subform id order mismatch")
    if sum(row["nondegenerate_flag"] for row in subform_rows) != 11:
        raise AssertionError("long_c59s3 nondegenerate count mismatch")
    if sum(row["definite_spatial_flag"] for row in subform_rows) != 0:
        raise AssertionError("long_c59s3 definite spatial count mismatch")
    max_rows = [row for row in subform_rows if row["max_abs_det_flag"] == 1]
    if len(max_rows) != 1 or max_rows[0]["subform_id"] != 119:
        raise AssertionError("long_c59s3 max determinant row mismatch")

    _det_header, determinant_rows = read_csv(OUT_DIR / "determinant.csv")
    if [int(row["subform_id"]) for row in determinant_rows] != list(range(816)):
        raise AssertionError("long_c59s3 determinant id order mismatch")
    max_det = max(abs(int(row["determinant_exact"])) for row in determinant_rows)
    max_det_rows = [
        row for row in determinant_rows if abs(int(row["determinant_exact"])) == max_det
    ]
    if len(max_det_rows) != 1 or int(max_det_rows[0]["subform_id"]) != 119:
        raise AssertionError("long_c59s3 determinant max mismatch")
    if len(str(max_det)) != obs[OBS_CODES["max_abs_det_digit_count"]]:
        raise AssertionError("long_c59s3 determinant digit count mismatch")
    if max_det % 1_000_000_007 != obs[OBS_CODES["max_abs_det_mod_1000000007"]]:
        raise AssertionError("long_c59s3 determinant mod 1000000007 mismatch")

    candidate_rows = rows_from_table(
        np.asarray(tables["candidate_table"]), CANDIDATE_COLUMNS
    )
    if [row["candidate_id"] for row in candidate_rows] != list(range(11)):
        raise AssertionError("long_c59s3 candidate id order mismatch")
    if sum(row["max_abs_det_flag"] for row in candidate_rows) != 1:
        raise AssertionError("long_c59s3 candidate max flag mismatch")
    if sum(row["definite_spatial_flag"] for row in candidate_rows) != 0:
        raise AssertionError("long_c59s3 candidate definite flag mismatch")

    summary_rows = rows_from_table(
        np.asarray(tables["summary_table"]), SUMMARY_COLUMNS
    )
    summary = summary_rows[0]
    if summary["subform_count"] != 816 or summary["rank3_count"] != 11:
        raise AssertionError("long_c59s3 summary mismatch")
    if summary["positive_definite_count"] != 0 or summary["negative_definite_count"] != 0:
        raise AssertionError("long_c59s3 summary definite mismatch")

    decision_rows = rows_from_table(
        np.asarray(tables["decision_table"]), DECISION_COLUMNS
    )
    if [row["decision_id"] for row in decision_rows] != list(
        range(len(DECISION_CODES))
    ):
        raise AssertionError("long_c59s3 decision order mismatch")
    if [row["certified_flag"] for row in decision_rows] != [1, 1, 1, 0, 0, 0]:
        raise AssertionError("long_c59s3 decision certified vector mismatch")
    if [row["obstruction_flag"] for row in decision_rows] != [0, 0, 0, 1, 1, 1]:
        raise AssertionError("long_c59s3 decision obstruction vector mismatch")

    gap_rows = rows_from_table(np.asarray(tables["gap_table"]), GAP_COLUMNS)
    if [row["certified_flag"] for row in gap_rows] != [1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c59s3 gap certified vector mismatch")
    if [row["next_flag"] for row in gap_rows] != [0, 1, 0, 0, 0, 0]:
        raise AssertionError("long_c59s3 gap next vector mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c59s3 manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c59s3 manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59s3 manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c59pk": LONG_C59PK,
        "long_c59pk_basis": LONG_C59PK_BASIS,
        "long_c59pk_restricted": LONG_C59PK_RESTRICTED,
        "long_sel": LONG_SEL,
        "long_dim4_gate": LONG_DIM4_GATE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c59s3 index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c59s3 index report hash mismatch")

    return {
        "schema": "long.c59s3.verification@1",
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
    print(json.dumps(validate_long_c59s3(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
