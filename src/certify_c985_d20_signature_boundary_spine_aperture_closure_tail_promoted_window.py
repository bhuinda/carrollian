from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window import (
        CELL_COLUMNS,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FLOW_WINDOW_REPORT,
        FLOW_WINDOW_TABLES,
        INDEX_PATH,
        NATIVE_CLASS_COLUMNS,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        POINCARE_COLUMNS,
        PROMOTED_BLOCK,
        PROMOTED_OBSERVABLE_CODES,
        RECURRENT_CLASS_COLUMNS,
        REPAIRED_AUTOMATON_REPORT,
        REPAIRED_AUTOMATON_TABLES,
        SKIP_WINDOW_REPORT,
        SKIP_WINDOW_TABLES,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window import (
        CELL_COLUMNS,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FLOW_WINDOW_REPORT,
        FLOW_WINDOW_TABLES,
        INDEX_PATH,
        NATIVE_CLASS_COLUMNS,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        POINCARE_COLUMNS,
        PROMOTED_BLOCK,
        PROMOTED_OBSERVABLE_CODES,
        RECURRENT_CLASS_COLUMNS,
        REPAIRED_AUTOMATON_REPORT,
        REPAIRED_AUTOMATON_TABLES,
        SKIP_WINDOW_REPORT,
        SKIP_WINDOW_TABLES,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    promoted_window = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_window.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate.json"
    )
    cells_csv = (OUT_DIR / "aperture_closure_tail_promoted_window_cells.csv").read_text(
        encoding="utf-8"
    )
    components_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_window_components.csv"
    ).read_text(encoding="utf-8")
    path_csv = (OUT_DIR / "aperture_closure_tail_promoted_window_path.csv").read_text(
        encoding="utf-8"
    )
    states_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_window_states.csv"
    ).read_text(encoding="utf-8")
    edges_csv = (OUT_DIR / "aperture_closure_tail_promoted_window_edges.csv").read_text(
        encoding="utf-8"
    )
    classes_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_window_recurrent_classes.csv"
    ).read_text(encoding="utf-8")
    native_classes_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_window_native_recurrent_classes.csv"
    ).read_text(encoding="utf-8")
    spectral_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_window_spectral_cut.csv"
    ).read_text(encoding="utf-8")
    poincare_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_window_poincare.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_window_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_window_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        promoted_window
        != expected[
            "signature_boundary_spine_aperture_closure_tail_promoted_window"
        ]
    ):
        raise AssertionError("promoted-window JSON is not reproducible")
    if cells_csv != expected["promoted_window_cells_csv"]:
        raise AssertionError("promoted-window cells CSV is not reproducible")
    if components_csv != expected["promoted_window_components_csv"]:
        raise AssertionError("promoted-window components CSV is not reproducible")
    if path_csv != expected["promoted_window_path_csv"]:
        raise AssertionError("promoted-window path CSV is not reproducible")
    if states_csv != expected["promoted_window_states_csv"]:
        raise AssertionError("promoted-window states CSV is not reproducible")
    if edges_csv != expected["promoted_window_edges_csv"]:
        raise AssertionError("promoted-window edges CSV is not reproducible")
    if classes_csv != expected["promoted_window_recurrent_classes_csv"]:
        raise AssertionError("promoted-window classes CSV is not reproducible")
    if native_classes_csv != expected["promoted_window_native_recurrent_classes_csv"]:
        raise AssertionError("promoted-window native classes CSV is not reproducible")
    if spectral_csv != expected["promoted_window_spectral_cut_csv"]:
        raise AssertionError("promoted-window spectral CSV is not reproducible")
    if poincare_csv != expected["promoted_window_poincare_csv"]:
        raise AssertionError("promoted-window Poincare CSV is not reproducible")
    if observables_csv != expected["promoted_window_observables_csv"]:
        raise AssertionError("promoted-window observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_promoted_window_certificate"
        ]
    ):
        raise AssertionError("promoted-window certificate is not reproducible")

    for name in [
        "cell_table",
        "component_table",
        "path_table",
        "state_table",
        "edge_table",
        "recurrent_class_table",
        "native_recurrent_class_table",
        "spectral_cut_table",
        "poincare_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"promoted-window table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_promoted_window@1"
    ):
        raise AssertionError("promoted-window report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("promoted-window layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("promoted-window all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("promoted-window checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("promoted-window report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("promoted-window report is not reproducible")

    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    path_table = np.asarray(tables["path_table"], dtype=np.int64)
    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    recurrent_class_table = np.asarray(tables["recurrent_class_table"], dtype=np.int64)
    native_class_table = np.asarray(
        tables["native_recurrent_class_table"],
        dtype=np.int64,
    )
    spectral_table = np.asarray(tables["spectral_cut_table"], dtype=np.int64)
    poincare_table = np.asarray(tables["poincare_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if tuple(cell_table.shape) != (855, len(CELL_COLUMNS)):
        raise AssertionError("promoted cell table shape mismatch")
    if component_table.shape[1] != len(COMPONENT_COLUMNS):
        raise AssertionError("promoted component table codebook mismatch")
    if tuple(path_table.shape) != (3, len(PATH_COLUMNS)):
        raise AssertionError("promoted path table shape mismatch")
    if tuple(state_table.shape) != (855, len(STATE_COLUMNS)):
        raise AssertionError("promoted state table shape mismatch")
    if edge_table.shape[1] != len(EDGE_COLUMNS):
        raise AssertionError("promoted edge table codebook mismatch")
    if recurrent_class_table.shape[1] != len(RECURRENT_CLASS_COLUMNS):
        raise AssertionError("promoted recurrent-class table codebook mismatch")
    if native_class_table.shape[1] != len(NATIVE_CLASS_COLUMNS):
        raise AssertionError("promoted native-class table codebook mismatch")
    if tuple(spectral_table.shape) != (1, len(SPECTRAL_CUT_COLUMNS)):
        raise AssertionError("promoted spectral table shape mismatch")
    if poincare_table.shape[1] != len(POINCARE_COLUMNS):
        raise AssertionError("promoted Poincare table codebook mismatch")
    if tuple(observable_table.shape) != (
        len(PROMOTED_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("promoted observable table shape mismatch")

    state_rows = table_rows(state_table, STATE_COLUMNS)
    edge_rows = table_rows(edge_table, EDGE_COLUMNS)
    spectral = table_rows(spectral_table, SPECTRAL_CUT_COLUMNS)[0]
    observables = {
        row["observable_code"]: row["value_x1e12"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sum(row["promoted_only_flag"] for row in state_rows) != 9:
        raise AssertionError("promoted-only state count mismatch")
    if sum(row["promoted_window_repair_flag"] for row in state_rows) != 89:
        raise AssertionError("promoted-window state count mismatch")
    if sum(row["old_spectral_cut_edge_flag"] for row in edge_rows) != 6:
        raise AssertionError("old spectral cut edge lineage mismatch")
    if spectral["old_cut_edge_count"] != 6:
        raise AssertionError("old cut edge count mismatch")
    if spectral["old_cut_edge_survival_count"] != 6:
        raise AssertionError("old cut survival count mismatch")
    if spectral["cut_edge_count"] <= 0:
        raise AssertionError("new spectral cut is empty")
    if spectral["lambda_2_x1e12"] <= 0:
        raise AssertionError("new lambda_2 is not positive")
    if spectral["lambda_3_x1e12"] <= spectral["lambda_2_x1e12"]:
        raise AssertionError("new spectral ordering mismatch")
    if tuple(PROMOTED_BLOCK) != (5, 5, 2, 5):
        raise AssertionError("promoted block constant mismatch")

    required_observables = {
        "boundary_union_word_count": 234_678,
        "trace_failure_word_count": 68_103,
        "bad_metric_word_count": 140_378,
        "metric_ok_word_count": 26_197,
        "closed_positive_metric_word_count": 984,
        "state_count": 855,
        "native_state_count": 562,
        "skip_derived_state_count": 846,
        "promoted_window_state_count": 89,
        "promoted_only_state_count": 9,
        "new_state_count_vs_skip": 9,
        "left_to_right_path_exists": 1,
        "shortest_path_length": 2,
        "old_cut_edge_count": 6,
        "old_cut_edge_survival_count": 6,
        "selected_block_code": 5_525,
        "flow_selected_candidate_word_count": 12,
    }
    for key, value in required_observables.items():
        code = PROMOTED_OBSERVABLE_CODES[key]
        if observables.get(code) != value * 10**12:
            raise AssertionError(f"observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("promoted_block") != [5, 5, 2, 5]:
        raise AssertionError("promoted block witness mismatch")
    if witness.get("promotion_profile", {}).get("promoted_only_state_count") != 9:
        raise AssertionError("promoted-only witness mismatch")
    if witness.get("old_cut_lineage", {}).get("old_cut_edge_survival_count") != 6:
        raise AssertionError("old-cut lineage witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("promoted-window certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("skip_window_report", {}), SKIP_WINDOW_REPORT, "skip report input")
    assert_file_hash(inputs.get("skip_window_tables", {}), SKIP_WINDOW_TABLES, "skip tables input")
    assert_file_hash(
        inputs.get("repaired_automaton_report", {}),
        REPAIRED_AUTOMATON_REPORT,
        "repaired report input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_tables", {}),
        REPAIRED_AUTOMATON_TABLES,
        "repaired tables input",
    )
    assert_file_hash(inputs.get("flow_window_report", {}), FLOW_WINDOW_REPORT, "flow report input")
    assert_file_hash(inputs.get("flow_window_tables", {}), FLOW_WINDOW_TABLES, "flow tables input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_promoted_window_manifest@1"
    ):
        raise AssertionError("promoted-window manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("promoted-window manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("promoted-window manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("promoted-window missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("promoted-window index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("promoted-window index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_promoted_window@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_window()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
