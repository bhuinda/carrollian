from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction import (
        BLOCK_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SECOND_WINDOW_PROMOTION_CERTIFICATE,
        SECOND_WINDOW_PROMOTION_EDGES,
        SECOND_WINDOW_PROMOTION_REPORT,
        SECOND_WINDOW_PROMOTION_STATES,
        SECOND_WINDOW_PROMOTION_TABLES,
        SIXJ_FRAME_CERTIFICATE,
        SIXJ_FRAME_CUT_EDGES,
        SIXJ_FRAME_REPORT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        parent,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction import (
        BLOCK_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SECOND_WINDOW_PROMOTION_CERTIFICATE,
        SECOND_WINDOW_PROMOTION_EDGES,
        SECOND_WINDOW_PROMOTION_REPORT,
        SECOND_WINDOW_PROMOTION_STATES,
        SECOND_WINDOW_PROMOTION_TABLES,
        SIXJ_FRAME_CERTIFICATE,
        SIXJ_FRAME_CUT_EDGES,
        SIXJ_FRAME_REPORT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        parent,
    )


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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    obstruction = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_certificate.json"
    )
    blocks_csv = (OUT_DIR / "sixj_recoupling_touch_blocks.csv").read_text(
        encoding="utf-8"
    )
    interventions_csv = (
        OUT_DIR / "sixj_recoupling_pair_interventions.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (OUT_DIR / "sixj_recoupling_pair_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if obstruction != expected["recoupling_pair_obstruction"]:
        raise AssertionError("sixj recoupling obstruction JSON is not reproducible")
    if blocks_csv != expected["recoupling_touch_blocks_csv"]:
        raise AssertionError("sixj recoupling touch-block CSV is not reproducible")
    if interventions_csv != expected["recoupling_interventions_csv"]:
        raise AssertionError("sixj recoupling intervention CSV is not reproducible")
    if observables_csv != expected["recoupling_observables_csv"]:
        raise AssertionError("sixj recoupling observable CSV is not reproducible")
    if certificate != expected["recoupling_certificate"]:
        raise AssertionError("sixj recoupling certificate is not reproducible")

    for name in ["block_table", "intervention_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"sixj recoupling table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction@1"
    ):
        raise AssertionError("sixj recoupling report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("sixj recoupling pair obstruction is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sixj recoupling all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("sixj recoupling checks mismatch")
    if parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("sixj recoupling report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("sixj recoupling report hash is not reproducible")

    block_table = np.asarray(tables["block_table"], dtype=np.int64)
    intervention_table = np.asarray(tables["intervention_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(block_table.shape) != (15, len(BLOCK_COLUMNS)):
        raise AssertionError("sixj recoupling block table shape mismatch")
    if tuple(intervention_table.shape) != (45, len(INTERVENTION_COLUMNS)):
        raise AssertionError("sixj recoupling intervention table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("sixj recoupling observable table shape mismatch")

    block_rows = table_rows(block_table, BLOCK_COLUMNS)
    intervention_rows = table_rows(intervention_table, INTERVENTION_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    candidate_codes = [
        row["block_code"] for row in block_rows if row["candidate_flag"] == 1
    ]
    if candidate_codes != [1451, 4512, 4552, 5125, 1255, 5255, 1252, 2145, 5252]:
        raise AssertionError("sixj recoupling candidate block order mismatch")
    if sum(row["already_promoted_flag"] for row in block_rows) != 2:
        raise AssertionError("sixj recoupling promoted base block count mismatch")
    if sum(row["candidate_flag"] for row in block_rows) != 9:
        raise AssertionError("sixj recoupling candidate block count mismatch")
    if any(row["support_changed_flag"] for row in intervention_rows):
        raise AssertionError("sixj recoupling support-changing row found")
    if not all(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        for row in intervention_rows
    ):
        raise AssertionError("sixj recoupling old cut support mismatch")

    selected = [
        row for row in intervention_rows if row["selected_best_flag"] == 1
    ]
    if len(selected) != 1:
        raise AssertionError("sixj recoupling selected best row count mismatch")
    best = selected[0]
    if (
        best["block_code_a"],
        best["block_code_b"],
        best["state_count"],
        best["edge_count"],
        best["cut_edge_count"],
        best["old_cut_edge_still_cut_count"],
        best["cut_conductance_x1e12"],
        best["conductance_reduction_x1e12"],
    ) != (5255, 5252, 894, 2695, 6, 6, 3_708_282_000, 620_722_000):
        raise AssertionError("sixj recoupling selected best witness mismatch")

    required_observables = {
        "base_state_count": 860,
        "base_edge_count": 2_571,
        "base_cut_edge_count": 6,
        "base_cut_conductance_x1e12": 4_329_004_000,
        "touch_block_count": 15,
        "candidate_block_count": 9,
        "single_intervention_count": 9,
        "pair_intervention_count": 36,
        "total_intervention_count": 45,
        "support_changing_intervention_count": 0,
        "best_block_code_a": 5_255,
        "best_block_code_b": 5_252,
        "best_state_count": 894,
        "best_edge_count": 2_695,
        "best_cut_edge_count": 6,
        "best_old_cut_edge_still_cut_count": 6,
        "best_lambda_2_x1e12": 2_451_808_000,
        "best_cut_conductance_x1e12": 3_708_282_000,
        "best_conductance_reduction_x1e12": 620_722_000,
        "closed_metric_word_count": 984,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"sixj recoupling observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("sixj_frame_report", {}),
        SIXJ_FRAME_REPORT,
        "sixj frame report input",
    )
    assert_file_hash(
        inputs.get("sixj_frame_certificate", {}),
        SIXJ_FRAME_CERTIFICATE,
        "sixj frame certificate input",
    )
    assert_file_hash(
        inputs.get("sixj_frame_cut_edges", {}),
        SIXJ_FRAME_CUT_EDGES,
        "sixj frame cut-edge input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_report", {}),
        SECOND_WINDOW_PROMOTION_REPORT,
        "second-window promotion report input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_certificate", {}),
        SECOND_WINDOW_PROMOTION_CERTIFICATE,
        "second-window promotion certificate input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_tables", {}),
        SECOND_WINDOW_PROMOTION_TABLES,
        "second-window promotion tables input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_states", {}),
        SECOND_WINDOW_PROMOTION_STATES,
        "second-window promotion states input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_edges", {}),
        SECOND_WINDOW_PROMOTION_EDGES,
        "second-window promotion edges input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction_manifest@1"
    ):
        raise AssertionError("sixj recoupling manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj recoupling manifest report hash mismatch")
    if parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("sixj recoupling manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("sixj recoupling missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj recoupling index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sixj recoupling index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_pair_obstruction()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
