from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search import (
        CANDIDATE_MOVE_COLUMNS,
        CANDIDATE_WORD_COLUMNS,
        CUT_EDGE_COLUMNS,
        CUT_WINDOW_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROMOTED_TRANSFER_CERTIFICATE,
        PROMOTED_TRANSFER_REPORT,
        PROMOTED_TRANSFER_TABLES,
        PROMOTED_WINDOW_CERTIFICATE,
        PROMOTED_WINDOW_REPORT,
        PROMOTED_WINDOW_TABLES,
        SCALE,
        SECOND_WINDOW_OBSERVABLE_CODES,
        SOURCE_WORD_COLUMNS,
        STATUS,
        TARGET_WORD_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search import (
        CANDIDATE_MOVE_COLUMNS,
        CANDIDATE_WORD_COLUMNS,
        CUT_EDGE_COLUMNS,
        CUT_WINDOW_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROMOTED_TRANSFER_CERTIFICATE,
        PROMOTED_TRANSFER_REPORT,
        PROMOTED_TRANSFER_TABLES,
        PROMOTED_WINDOW_CERTIFICATE,
        PROMOTED_WINDOW_REPORT,
        PROMOTED_WINDOW_TABLES,
        SCALE,
        SECOND_WINDOW_OBSERVABLE_CODES,
        SOURCE_WORD_COLUMNS,
        STATUS,
        TARGET_WORD_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
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


def block_code_from_row(row: dict[str, int]) -> int:
    return (
        row["block_symbol_0_id"] * 1_000
        + row["block_symbol_1_id"] * 100
        + row["block_symbol_2_id"] * 10
        + row["block_symbol_3_id"]
    )


def word_from_row(row: dict[str, int], columns: list[str]) -> tuple[int, ...]:
    return tuple(row[column] for column in columns if row[column] != -1)


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    second_window_search = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_search_certificate.json"
    )
    cut_edges_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_cut_edges.csv"
    ).read_text(encoding="utf-8")
    target_windows_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_target_windows.csv"
    ).read_text(encoding="utf-8")
    candidate_moves_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_candidate_moves.csv"
    ).read_text(encoding="utf-8")
    candidate_words_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_candidate_words.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if second_window_search != expected["second_window_search"]:
        raise AssertionError("second-window search JSON is not reproducible")
    if cut_edges_csv != expected["cut_edges_csv"]:
        raise AssertionError("second-window cut-edge CSV is not reproducible")
    if target_windows_csv != expected["target_cut_windows_csv"]:
        raise AssertionError("second-window target-window CSV is not reproducible")
    if candidate_moves_csv != expected["candidate_moves_csv"]:
        raise AssertionError("second-window candidate-move CSV is not reproducible")
    if candidate_words_csv != expected["candidate_words_csv"]:
        raise AssertionError("second-window candidate-word CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("second-window observable CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("second-window certificate is not reproducible")

    for name in [
        "cut_edge_table",
        "cut_window_table",
        "candidate_move_table",
        "candidate_word_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"second-window table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_search@1"
    ):
        raise AssertionError("second-window report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("second-window search layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("second-window all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("second-window checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("second-window report is not reproducible")

    cut_edge_table = np.asarray(tables["cut_edge_table"], dtype=np.int64)
    cut_window_table = np.asarray(tables["cut_window_table"], dtype=np.int64)
    candidate_move_table = np.asarray(tables["candidate_move_table"], dtype=np.int64)
    candidate_word_table = np.asarray(tables["candidate_word_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(cut_edge_table.shape) != (6, len(CUT_EDGE_COLUMNS)):
        raise AssertionError("second-window cut-edge table shape mismatch")
    if tuple(cut_window_table.shape) != (8, len(CUT_WINDOW_COLUMNS)):
        raise AssertionError("second-window target-window table shape mismatch")
    if tuple(candidate_move_table.shape) != (7, len(CANDIDATE_MOVE_COLUMNS)):
        raise AssertionError("second-window candidate-move table shape mismatch")
    if tuple(candidate_word_table.shape) != (1, len(CANDIDATE_WORD_COLUMNS)):
        raise AssertionError("second-window candidate-word table shape mismatch")
    if tuple(observable_table.shape) != (
        len(SECOND_WINDOW_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("second-window observable table shape mismatch")

    cut_edge_rows = table_rows(cut_edge_table, CUT_EDGE_COLUMNS)
    cut_window_rows = table_rows(cut_window_table, CUT_WINDOW_COLUMNS)
    candidate_move_rows = table_rows(candidate_move_table, CANDIDATE_MOVE_COLUMNS)
    candidate_word_rows = table_rows(candidate_word_table, CANDIDATE_WORD_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)

    ranked_edge_ids = [row["transfer_edge_id"] for row in cut_edge_rows]
    if ranked_edge_ids != [2447, 2459, 2473, 2480, 2484, 2488]:
        raise AssertionError("second-window cut-edge rank witness mismatch")
    if sum(row["old_spectral_cut_edge_flag"] for row in cut_edge_rows) != 6:
        raise AssertionError("second-window old-cut edge count mismatch")
    if sum(row["promoted_transition_flag"] for row in cut_edge_rows) != 5:
        raise AssertionError("second-window promoted cut-edge count mismatch")
    if sum(row["target_unpromoted_old_cut_edge_flag"] for row in cut_edge_rows) != 1:
        raise AssertionError("second-window target edge count mismatch")
    if sum(row["undirected_stationary_flux_x1e12"] for row in cut_edge_rows) != 1_025_816_382:
        raise AssertionError("second-window total cut flux mismatch")

    target_edge = next(
        row for row in cut_edge_rows if row["target_unpromoted_old_cut_edge_flag"] == 1
    )
    if (
        target_edge["transfer_edge_id"],
        target_edge["source_state_id"],
        target_edge["target_state_id"],
        target_edge["source_side_code"],
        target_edge["target_side_code"],
        target_edge["edit_position"],
        target_edge["source_symbol_id"],
        target_edge["target_symbol_id"],
        target_edge["undirected_stationary_flux_x1e12"],
    ) != (2447, 797, 828, 1, -1, 3, -1, 5, 170_969_397):
        raise AssertionError("second-window target edge witness mismatch")
    if word_from_row(target_edge, SOURCE_WORD_COLUMNS) != (
        2,
        1,
        4,
        5,
        1,
        1,
        5,
        5,
        2,
        1,
        4,
        5,
    ):
        raise AssertionError("second-window target source word mismatch")
    if word_from_row(target_edge, TARGET_WORD_COLUMNS) != (
        2,
        1,
        4,
        5,
        5,
        1,
        1,
        5,
        5,
        2,
        1,
        4,
        5,
    ):
        raise AssertionError("second-window target target word mismatch")

    if {
        row["transfer_edge_id"] for row in cut_window_rows
    } != {2447}:
        raise AssertionError("second-window target windows are not target-local")
    if sum(row["cut_flux_share_x1e12"] for row in cut_window_rows) != 170_969_397:
        raise AssertionError("second-window target-window flux split mismatch")
    if sorted({block_code_from_row(row) for row in cut_window_rows}) != [
        1451,
        1455,
        2145,
        4511,
        4551,
        5115,
        5511,
    ]:
        raise AssertionError("second-window target block witness mismatch")

    selected_moves = [
        row for row in candidate_move_rows if row["selected_move_flag"] == 1
    ]
    if len(selected_moves) != 1:
        raise AssertionError("second-window selected move count mismatch")
    selected_move = selected_moves[0]
    if (
        block_code_from_row(selected_move),
        selected_move["candidate_word_count"],
        selected_move["same_side_edge_count"],
        selected_move["positive_side_edge_count"],
        selected_move["negative_side_edge_count"],
        selected_move["cross_side_rejected_word_count"],
        selected_move["clean_move_flag"],
        selected_move["new_target_cut_flux_x1e12"],
        selected_move["target_cut_flux_reduction_x1e12"],
        selected_move["new_target_weighted_conductance_x1e12"],
        selected_move["target_conductance_reduction_x1e12"],
    ) != (1455, 1, 1, 0, 1, 0, 1, 170_940_171, 29_226, 730_994_152, 1_070_270):
        raise AssertionError("second-window selected move witness mismatch")
    if sum(row["clean_move_flag"] for row in candidate_move_rows) != 4:
        raise AssertionError("second-window clean move count mismatch")

    candidate_word = candidate_word_rows[0]
    if (
        candidate_word["candidate_move_id"],
        candidate_word["assigned_side_code"],
        candidate_word["neighbor_state_count"],
        candidate_word["closed_path_count"],
        candidate_word["template_count"],
        candidate_word["trace_variation"],
        candidate_word["word_length"],
        word_from_row(candidate_word, WORD_COLUMNS),
    ) != (
        selected_move["candidate_move_id"],
        -1,
        1,
        42,
        7,
        167,
        14,
        (2, 5, 1, 4, 5, 5, 1, 1, 5, 5, 2, 1, 4, 5),
    ):
        raise AssertionError("second-window candidate word witness mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] for row in observable_rows
    }
    required_observables = {
        "surviving_cut_edge_count": 6 * SCALE,
        "promoted_support_cut_edge_count": 5 * SCALE,
        "unpromoted_old_cut_edge_count": SCALE,
        "target_transfer_edge_id": 2447 * SCALE,
        "target_cut_flux": 170_969_397,
        "target_endpoint_state_count": 2 * SCALE,
        "target_neighbor_candidate_count": 211 * SCALE,
        "target_trace_failure_count": 46 * SCALE,
        "target_bad_metric_count": 138 * SCALE,
        "target_not_closed_count": 22 * SCALE,
        "target_already_supported_count": 2 * SCALE,
        "target_metric_closed_virtual_count": 3 * SCALE,
        "target_cut_window_block_count": 7 * SCALE,
        "candidate_move_count": 7 * SCALE,
        "clean_candidate_move_count": 4 * SCALE,
        "selected_block_code": 1455 * SCALE,
        "selected_candidate_word_count": SCALE,
        "selected_same_side_edge_count": SCALE,
        "selected_negative_side_edge_count": SCALE,
        "selected_target_cut_flux_reduction": 29_226,
        "selected_target_conductance_reduction": 1_070_270,
    }
    for key, value in required_observables.items():
        code = SECOND_WINDOW_OBSERVABLE_CODES[key]
        if observables.get(code) != value:
            raise AssertionError(f"second-window observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("target_transfer_edge_id") != 2447:
        raise AssertionError("second-window report target witness mismatch")
    if witness.get("selected_second_window_block") != [1, 4, 5, 5]:
        raise AssertionError("second-window report selected block mismatch")
    if witness.get("selected_candidate_word") != [
        2,
        5,
        1,
        4,
        5,
        5,
        1,
        1,
        5,
        5,
        2,
        1,
        4,
        5,
    ]:
        raise AssertionError("second-window report candidate word mismatch")
    if witness.get("candidate_stats") != {
        "target_already_supported_count": 2,
        "target_bad_metric_count": 138,
        "target_metric_closed_virtual_count": 3,
        "target_neighbor_candidate_count": 211,
        "target_not_closed_count": 22,
        "target_trace_failure_count": 46,
    }:
        raise AssertionError("second-window report candidate stats mismatch")

    if certificate.get("status") != STATUS:
        raise AssertionError("second-window certificate status mismatch")
    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("promoted_transfer_report", {}),
        PROMOTED_TRANSFER_REPORT,
        "promoted transfer report input",
    )
    assert_file_hash(
        inputs.get("promoted_transfer_certificate", {}),
        PROMOTED_TRANSFER_CERTIFICATE,
        "promoted transfer certificate input",
    )
    assert_file_hash(
        inputs.get("promoted_transfer_tables", {}),
        PROMOTED_TRANSFER_TABLES,
        "promoted transfer tables input",
    )
    assert_file_hash(
        inputs.get("promoted_window_report", {}),
        PROMOTED_WINDOW_REPORT,
        "promoted window report input",
    )
    assert_file_hash(
        inputs.get("promoted_window_certificate", {}),
        PROMOTED_WINDOW_CERTIFICATE,
        "promoted window certificate input",
    )
    assert_file_hash(
        inputs.get("promoted_window_tables", {}),
        PROMOTED_WINDOW_TABLES,
        "promoted window tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_search_manifest@1"
    ):
        raise AssertionError("second-window manifest schema mismatch")
    if manifest.get("status") != STATUS:
        raise AssertionError("second-window manifest status mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("second-window manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("second-window search missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("second-window index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_second_window_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_search()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
