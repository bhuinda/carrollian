from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        CANDIDATE_MOVE_COLUMNS,
        CANDIDATE_WORD_COLUMNS,
        CUT_WINDOW_COLUMNS,
        DERIVE_SCRIPT,
        FLOW_WINDOW_OBSERVABLE_CODES,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REPAIRED_AUTOMATON_REPORT,
        REPAIRED_AUTOMATON_TABLES,
        SKIP_WINDOW_REPORT,
        SKIP_WINDOW_TABLES,
        STATUS,
        THEOREM_ID,
        TRANSFER_CERTIFICATE,
        TRANSFER_EDGES,
        TRANSFER_REPORT,
        TRANSFER_STATES,
        TRANSFER_TABLES,
        VALIDATOR_SCRIPT,
        WINDOW_PRESSURE_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift import (
        CANDIDATE_MOVE_COLUMNS,
        CANDIDATE_WORD_COLUMNS,
        CUT_WINDOW_COLUMNS,
        DERIVE_SCRIPT,
        FLOW_WINDOW_OBSERVABLE_CODES,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REPAIRED_AUTOMATON_REPORT,
        REPAIRED_AUTOMATON_TABLES,
        SKIP_WINDOW_REPORT,
        SKIP_WINDOW_TABLES,
        STATUS,
        THEOREM_ID,
        TRANSFER_CERTIFICATE,
        TRANSFER_EDGES,
        TRANSFER_REPORT,
        TRANSFER_STATES,
        TRANSFER_TABLES,
        VALIDATOR_SCRIPT,
        WINDOW_PRESSURE_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    flow_window = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_flow_window_lift.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate.json"
    )
    pressure_csv = (
        OUT_DIR / "aperture_closure_tail_flow_window_pressure.csv"
    ).read_text(encoding="utf-8")
    cut_windows_csv = (
        OUT_DIR / "aperture_closure_tail_flow_cut_windows.csv"
    ).read_text(encoding="utf-8")
    candidate_moves_csv = (
        OUT_DIR / "aperture_closure_tail_flow_candidate_moves.csv"
    ).read_text(encoding="utf-8")
    candidate_words_csv = (
        OUT_DIR / "aperture_closure_tail_flow_candidate_words.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_flow_window_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_flow_window_lift_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        flow_window
        != expected[
            "signature_boundary_spine_aperture_closure_tail_flow_window_lift"
        ]
    ):
        raise AssertionError("flow-window JSON is not reproducible")
    if pressure_csv != expected["flow_window_pressure_csv"]:
        raise AssertionError("flow-window pressure CSV is not reproducible")
    if cut_windows_csv != expected["flow_cut_windows_csv"]:
        raise AssertionError("flow cut-window CSV is not reproducible")
    if candidate_moves_csv != expected["flow_candidate_moves_csv"]:
        raise AssertionError("flow candidate-move CSV is not reproducible")
    if candidate_words_csv != expected["flow_candidate_words_csv"]:
        raise AssertionError("flow candidate-word CSV is not reproducible")
    if observables_csv != expected["flow_window_observables_csv"]:
        raise AssertionError("flow-window observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_flow_window_lift_certificate"
        ]
    ):
        raise AssertionError("flow-window certificate is not reproducible")

    for name in [
        "pressure_table",
        "cut_window_table",
        "candidate_move_table",
        "candidate_word_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"flow-window table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift@1"
    ):
        raise AssertionError("flow-window report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("flow-window layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("flow-window all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("flow-window checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("flow-window report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("flow-window report is not reproducible")

    pressure_table = np.asarray(tables["pressure_table"], dtype=np.int64)
    cut_window_table = np.asarray(tables["cut_window_table"], dtype=np.int64)
    candidate_move_table = np.asarray(tables["candidate_move_table"], dtype=np.int64)
    candidate_word_table = np.asarray(tables["candidate_word_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if pressure_table.shape != (173, len(WINDOW_PRESSURE_COLUMNS)):
        raise AssertionError("flow pressure table shape mismatch")
    if cut_window_table.shape != (48, len(CUT_WINDOW_COLUMNS)):
        raise AssertionError("flow cut-window table shape mismatch")
    if candidate_move_table.shape != (15, len(CANDIDATE_MOVE_COLUMNS)):
        raise AssertionError("flow candidate-move table shape mismatch")
    if candidate_word_table.shape != (12, len(CANDIDATE_WORD_COLUMNS)):
        raise AssertionError("flow candidate-word table shape mismatch")
    if observable_table.shape != (
        len(FLOW_WINDOW_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("flow observable table shape mismatch")

    pressure_rows = table_rows(pressure_table, WINDOW_PRESSURE_COLUMNS)
    cut_rows = table_rows(cut_window_table, CUT_WINDOW_COLUMNS)
    move_rows = table_rows(candidate_move_table, CANDIDATE_MOVE_COLUMNS)
    candidate_rows = table_rows(candidate_word_table, CANDIDATE_WORD_COLUMNS)
    observables = {
        row["observable_code"]: row["value_x1e12"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sum(row["stationary_mass_x1e12"] for row in pressure_rows) != 10**12:
        raise AssertionError("window pressure mass does not sum to one")
    if sum(row["cut_flux_share_x1e12"] for row in cut_rows) != 1_027_925_304:
        raise AssertionError("cut-window flux total mismatch")
    selected = [row for row in move_rows if row["selected_move_flag"] == 1]
    if len(selected) != 1:
        raise AssertionError("selected move row count mismatch")
    selected_move = selected[0]
    if (
        selected_move["block_symbol_0_id"],
        selected_move["block_symbol_1_id"],
        selected_move["block_symbol_2_id"],
        selected_move["block_symbol_3_id"],
        selected_move["candidate_word_count"],
        selected_move["negative_side_edge_count"],
        selected_move["new_cut_flux_x1e12"],
        selected_move["new_weighted_conductance_x1e12"],
    ) != (5, 5, 2, 5, 12, 12, 1_025_816_379, 4_385_964_912):
        raise AssertionError("selected move witness mismatch")
    if any(row["assigned_side_code"] != -1 for row in candidate_rows):
        raise AssertionError("selected candidate words are not all negative-side")
    if sum(row["neighbor_state_count"] for row in candidate_rows) != 12:
        raise AssertionError("selected candidate neighbor count mismatch")

    required_observables = {
        "cut_endpoint_state_count": 12,
        "cut_endpoint_neighbor_candidate_count": 1_150,
        "metric_closed_virtual_candidate_count": 26,
        "cut_window_block_count": 15,
        "candidate_move_count": 15,
        "clean_candidate_move_count": 12,
        "selected_candidate_word_count": 12,
        "selected_same_side_edge_count": 12,
        "selected_negative_side_edge_count": 12,
        "selected_block_code": 5_525,
    }
    for key, value in required_observables.items():
        code = FLOW_WINDOW_OBSERVABLE_CODES[key]
        if observables.get(code) != value * 10**12:
            raise AssertionError(f"observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("selected_move", {}).get("block") != [5, 5, 2, 5]:
        raise AssertionError("selected move witness block mismatch")
    if witness.get("selected_move", {}).get("conductance_reduction_x1e12") != 78_320_802:
        raise AssertionError("selected move conductance reduction mismatch")
    if witness.get("candidate_stats", {}).get("trace_failure_count") != 258:
        raise AssertionError("candidate trace failure count mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("flow-window certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("transfer_report", {}), TRANSFER_REPORT, "transfer report input")
    assert_file_hash(
        inputs.get("transfer_certificate", {}),
        TRANSFER_CERTIFICATE,
        "transfer certificate input",
    )
    assert_file_hash(inputs.get("transfer_states", {}), TRANSFER_STATES, "transfer states input")
    assert_file_hash(inputs.get("transfer_edges", {}), TRANSFER_EDGES, "transfer edges input")
    assert_file_hash(inputs.get("transfer_tables", {}), TRANSFER_TABLES, "transfer tables input")
    assert_file_hash(
        inputs.get("repaired_automaton_report", {}),
        REPAIRED_AUTOMATON_REPORT,
        "repaired automaton report input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_tables", {}),
        REPAIRED_AUTOMATON_TABLES,
        "repaired automaton tables input",
    )
    assert_file_hash(
        inputs.get("skip_window_report", {}),
        SKIP_WINDOW_REPORT,
        "skip-window report input",
    )
    assert_file_hash(
        inputs.get("skip_window_tables", {}),
        SKIP_WINDOW_TABLES,
        "skip-window tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift_manifest@1"
    ):
        raise AssertionError("flow-window manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("flow-window manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("flow-window manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("flow-window missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("flow-window index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("flow-window index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_flow_window_lift()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
