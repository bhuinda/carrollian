from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file
    from .derive_long_c60negf import (
        CASE_COLUMNS,
        CLAIM_COLUMNS,
        CONTROL_COLUMNS,
        INDEX_PATH,
        JOB_CARD_COLUMNS,
        LONG_C60OP,
        LONG_C60OP_OPCODE,
        OBSERVABLE_CLASS_COLUMNS,
        OBSERVABLE_CLASS_CODES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RESULT_STATUS,
        STATUS,
        SUCCESS_COLUMNS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_long_raw import rows_from_table
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file
    from derive_long_c60negf import (
        CASE_COLUMNS,
        CLAIM_COLUMNS,
        CONTROL_COLUMNS,
        INDEX_PATH,
        JOB_CARD_COLUMNS,
        LONG_C60OP,
        LONG_C60OP_OPCODE,
        OBSERVABLE_CLASS_COLUMNS,
        OBSERVABLE_CLASS_CODES,
        OBS_CODES,
        OBS_COLUMNS,
        OUT_DIR,
        RESULT_STATUS,
        STATUS,
        SUCCESS_COLUMNS,
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


def validate_long_c60negf() -> dict[str, Any]:
    expected = build_payloads()
    c60negf = load_json(OUT_DIR / "c60negf.json")
    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    cert = load_json(OUT_DIR / "cert.json")
    index = load_json(INDEX_PATH)
    tables = np.load(OUT_DIR / "tables.npz", allow_pickle=False)

    if c60negf != expected["c60negf"]:
        raise AssertionError("long_c60negf JSON mismatch")
    if cert != expected["cert"]:
        raise AssertionError("long_c60negf cert mismatch")
    for filename, key in {
        "case.csv": "case_csv",
        "control.csv": "control_csv",
        "observable_class.csv": "observable_class_csv",
        "job_card.csv": "job_card_csv",
        "success.csv": "success_csv",
        "claim.csv": "claim_csv",
        "obs.csv": "obs_csv",
    }.items():
        if (OUT_DIR / filename).read_text(encoding="utf-8") != expected[key]:
            raise AssertionError(f"long_c60negf {filename} mismatch")

    for key, expected_array in {
        "case_table": expected["case_table"],
        "control_table": expected["control_table"],
        "observable_class_table": expected["observable_class_table"],
        "job_card_table": expected["job_card_table"],
        "success_table": expected["success_table"],
        "claim_table": expected["claim_table"],
        "observable_table": expected["observable_table"],
    }.items():
        if not np.array_equal(np.asarray(tables[key]), expected_array):
            raise AssertionError(f"long_c60negf table mismatch: {key}")

    if report.get("schema") != "long.c60negf.report@1":
        raise AssertionError("long_c60negf report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("long_c60negf report status mismatch")
    if report.get("result_status") != RESULT_STATUS:
        raise AssertionError("long_c60negf result status mismatch")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("long_c60negf all_checks_pass mismatch")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("long_c60negf checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c60negf report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("long_c60negf report hash mismatch")

    csv_shapes = [
        ("case.csv", CASE_COLUMNS, 13),
        ("control.csv", CONTROL_COLUMNS, 6),
        ("observable_class.csv", OBSERVABLE_CLASS_COLUMNS, 8),
        ("job_card.csv", JOB_CARD_COLUMNS, 78),
        ("success.csv", SUCCESS_COLUMNS, 8),
        ("claim.csv", CLAIM_COLUMNS, 6),
        ("obs.csv", OBS_COLUMNS, len(OBS_CODES)),
    ]
    for filename, columns, row_count in csv_shapes:
        header, rows = read_csv(OUT_DIR / filename)
        if header != columns or len(rows) != row_count:
            raise AssertionError(f"long_c60negf {filename} shape mismatch")

    table_shapes = {
        "case_table": (13, len(CASE_COLUMNS)),
        "control_table": (6, len(CONTROL_COLUMNS)),
        "observable_class_table": (8, len(OBSERVABLE_CLASS_COLUMNS)),
        "job_card_table": (78, len(JOB_CARD_COLUMNS)),
        "success_table": (8, len(SUCCESS_COLUMNS)),
        "claim_table": (6, len(CLAIM_COLUMNS)),
        "observable_table": (len(OBS_CODES), len(OBS_COLUMNS)),
    }
    for key, shape in table_shapes.items():
        if tuple(np.asarray(tables[key]).shape) != shape:
            raise AssertionError(f"long_c60negf {key} shape mismatch")

    obs = {
        row["observable_code"]: row["value"]
        for row in rows_from_table(np.asarray(tables["observable_table"]), OBS_COLUMNS)
    }
    required = {
        "input_report_count": 1,
        "input_certified_count": 1,
        "stage5_result_present_flag": 1,
        "semantic_opcode_rows_carried_forward": 59,
        "golden_ticks_carried_forward": 20,
        "c60_transition_edges_carried_forward": 30,
        "stage5_adjacent_composition_failures": 0,
        "minimal_validation_case_count": 13,
        "dft_negf_job_card_count": 78,
        "control_experiment_count": 6,
        "observable_class_count": 8,
        "success_criterion_count": 8,
        "claim_update_count": 6,
        "dft_result_row_count": 0,
        "negf_result_row_count": 0,
        "protocol_only_flag": 1,
        "physical_signature_validated_flag": 0,
        "conductance_validated_flag": 0,
        "manufacturability_validation_flag": 0,
    }
    for key, value in required.items():
        if obs.get(OBS_CODES[key]) != value:
            raise AssertionError(f"long_c60negf observable {key} mismatch")

    case_rows = rows_from_table(np.asarray(tables["case_table"]), CASE_COLUMNS)
    if [row["validation_case_id"] for row in case_rows] != list(range(13)):
        raise AssertionError("long_c60negf case id order mismatch")
    if any(row["required_dft_flag"] != 1 for row in case_rows):
        raise AssertionError("long_c60negf DFT case requirement mismatch")
    if any(row["required_negf_flag"] != 1 for row in case_rows):
        raise AssertionError("long_c60negf NEGF case requirement mismatch")

    job_rows = rows_from_table(np.asarray(tables["job_card_table"]), JOB_CARD_COLUMNS)
    if [row["job_id"] for row in job_rows] != list(range(78)):
        raise AssertionError("long_c60negf job id order mismatch")
    if any(row["dft_job_flag"] != 1 or row["negf_job_flag"] != 1 for row in job_rows):
        raise AssertionError("long_c60negf DFT/NEGF job flag mismatch")
    if any(row["protocol_only_flag"] != 1 for row in job_rows):
        raise AssertionError("long_c60negf protocol-only flag mismatch")
    if any(row["physical_result_present_flag"] != 0 for row in job_rows):
        raise AssertionError("long_c60negf result boundary mismatch")

    success_rows = rows_from_table(np.asarray(tables["success_table"]), SUCCESS_COLUMNS)
    if len(success_rows) != len(OBSERVABLE_CLASS_CODES):
        raise AssertionError("long_c60negf success criterion count mismatch")
    if any(row["quantitative_result_present_flag"] != 0 for row in success_rows):
        raise AssertionError("long_c60negf quantitative result boundary mismatch")

    claim_rows = rows_from_table(np.asarray(tables["claim_table"]), CLAIM_COLUMNS)
    if [row["claim_update_id"] for row in claim_rows] != list(range(6)):
        raise AssertionError("long_c60negf claim row order mismatch")
    if [row["claim_ready_flag"] for row in claim_rows] != [1, 0, 0, 0, 0, 0]:
        raise AssertionError("long_c60negf claim readiness boundary mismatch")
    if [row["requires_physical_validation_flag"] for row in claim_rows] != [
        0,
        1,
        1,
        1,
        1,
        1,
    ]:
        raise AssertionError("long_c60negf claim physical gate mismatch")

    if manifest != expected["manifest"]:
        raise AssertionError("long_c60negf manifest mismatch")
    if manifest.get("manifest_sha256") != self_hash(manifest, "manifest_sha256"):
        raise AssertionError("long_c60negf manifest self hash mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c60negf manifest report hash mismatch")

    inputs = report.get("inputs", {})
    for label, path in {
        "long_c60op": LONG_C60OP,
        "long_c60op_opcode": LONG_C60OP_OPCODE,
    }.items():
        assert_file_hash(inputs[label], path, label)

    obligations = index.get("obligations", [])
    matching = [row for row in obligations if row.get("id") == THEOREM_ID]
    if len(matching) != 1:
        raise AssertionError("long_c60negf index entry missing")
    if matching[0].get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("long_c60negf index report hash mismatch")

    return {
        "schema": "long.c60negf.verification@1",
        "status": "PASS",
        "verified_report": str((OUT_DIR / "report.json").relative_to(ROOT)).replace(
            "\\", "/"
        ),
        "certificate_sha256": report["certificate_sha256"],
        "result_status": report["result_status"],
        "summary": report["witness"]["summary"],
        "closure_boundary": report["closure_boundary"],
        "next_highest_yield_item": report["next_highest_yield_item"],
    }


def main() -> None:
    print(json.dumps(validate_long_c60negf(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
