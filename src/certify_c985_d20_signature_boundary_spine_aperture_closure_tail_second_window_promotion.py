from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion import (
        CELL_COLUMNS,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FIRST_WINDOW_BLOCK,
        NATIVE_CLASS_COLUMNS,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        POINCARE_COLUMNS,
        PROMOTED_WINDOW_CERTIFICATE,
        PROMOTED_WINDOW_REPORT,
        PROMOTED_WINDOW_TABLES,
        RECURRENT_CLASS_COLUMNS,
        SCALE,
        SECOND_WINDOW_BLOCK,
        SECOND_WINDOW_CERTIFICATE,
        SECOND_WINDOW_PROMOTION_OBSERVABLE_CODES,
        SECOND_WINDOW_REPORT,
        SECOND_WINDOW_TABLES,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        X1E12_OBSERVABLES,
        build_payloads,
        parent,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion import (
        CELL_COLUMNS,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        FIRST_WINDOW_BLOCK,
        NATIVE_CLASS_COLUMNS,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        POINCARE_COLUMNS,
        PROMOTED_WINDOW_CERTIFICATE,
        PROMOTED_WINDOW_REPORT,
        PROMOTED_WINDOW_TABLES,
        RECURRENT_CLASS_COLUMNS,
        SCALE,
        SECOND_WINDOW_BLOCK,
        SECOND_WINDOW_CERTIFICATE,
        SECOND_WINDOW_PROMOTION_OBSERVABLE_CODES,
        SECOND_WINDOW_REPORT,
        SECOND_WINDOW_TABLES,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        X1E12_OBSERVABLES,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    promotion = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_promotion.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_certificate.json"
    )
    cells_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_cells.csv"
    ).read_text(encoding="utf-8")
    components_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_components.csv"
    ).read_text(encoding="utf-8")
    path_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_path.csv"
    ).read_text(encoding="utf-8")
    states_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_states.csv"
    ).read_text(encoding="utf-8")
    edges_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_edges.csv"
    ).read_text(encoding="utf-8")
    classes_csv = (
        OUT_DIR
        / "aperture_closure_tail_second_window_promotion_recurrent_classes.csv"
    ).read_text(encoding="utf-8")
    native_classes_csv = (
        OUT_DIR
        / "aperture_closure_tail_second_window_promotion_native_recurrent_classes.csv"
    ).read_text(encoding="utf-8")
    spectral_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_spectral_cut.csv"
    ).read_text(encoding="utf-8")
    poincare_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_poincare.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_promotion_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_promotion_tables.npz",
        allow_pickle=False,
    )
    index = load_json(parent.INDEX_PATH)

    if promotion != expected["second_window_promotion"]:
        raise AssertionError("second-window promotion JSON is not reproducible")
    if cells_csv != expected["second_window_promotion_cells_csv"]:
        raise AssertionError("second-window promotion cells CSV is not reproducible")
    if components_csv != expected["second_window_promotion_components_csv"]:
        raise AssertionError(
            "second-window promotion components CSV is not reproducible"
        )
    if path_csv != expected["second_window_promotion_path_csv"]:
        raise AssertionError("second-window promotion path CSV is not reproducible")
    if states_csv != expected["second_window_promotion_states_csv"]:
        raise AssertionError("second-window promotion states CSV is not reproducible")
    if edges_csv != expected["second_window_promotion_edges_csv"]:
        raise AssertionError("second-window promotion edges CSV is not reproducible")
    if classes_csv != expected["second_window_promotion_recurrent_classes_csv"]:
        raise AssertionError("second-window promotion classes CSV is not reproducible")
    if (
        native_classes_csv
        != expected["second_window_promotion_native_recurrent_classes_csv"]
    ):
        raise AssertionError(
            "second-window promotion native classes CSV is not reproducible"
        )
    if spectral_csv != expected["second_window_promotion_spectral_cut_csv"]:
        raise AssertionError("second-window promotion spectral CSV is not reproducible")
    if poincare_csv != expected["second_window_promotion_poincare_csv"]:
        raise AssertionError("second-window promotion Poincare CSV is not reproducible")
    if observables_csv != expected["second_window_promotion_observables_csv"]:
        raise AssertionError(
            "second-window promotion observables CSV is not reproducible"
        )
    if certificate != expected["second_window_promotion_certificate"]:
        raise AssertionError("second-window promotion certificate is not reproducible")

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
            raise AssertionError(
                f"second-window promotion table {name} is not reproducible"
            )

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion@1"
    ):
        raise AssertionError("second-window promotion report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("second-window promotion layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("second-window promotion all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("second-window promotion checks mismatch")
    if parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("second-window promotion report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("second-window promotion report is not reproducible")

    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    path_table = np.asarray(tables["path_table"], dtype=np.int64)
    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    recurrent_class_table = np.asarray(
        tables["recurrent_class_table"],
        dtype=np.int64,
    )
    native_class_table = np.asarray(
        tables["native_recurrent_class_table"],
        dtype=np.int64,
    )
    spectral_table = np.asarray(tables["spectral_cut_table"], dtype=np.int64)
    poincare_table = np.asarray(tables["poincare_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(cell_table.shape) != (860, len(CELL_COLUMNS)):
        raise AssertionError("second-window promotion cell table shape mismatch")
    if tuple(component_table.shape) != (25, len(COMPONENT_COLUMNS)):
        raise AssertionError("second-window promotion component table shape mismatch")
    if tuple(path_table.shape) != (3, len(PATH_COLUMNS)):
        raise AssertionError("second-window promotion path table shape mismatch")
    if tuple(state_table.shape) != (860, len(STATE_COLUMNS)):
        raise AssertionError("second-window promotion state table shape mismatch")
    if tuple(edge_table.shape) != (2_571, len(EDGE_COLUMNS)):
        raise AssertionError("second-window promotion edge table shape mismatch")
    if tuple(recurrent_class_table.shape) != (25, len(RECURRENT_CLASS_COLUMNS)):
        raise AssertionError(
            "second-window promotion recurrent-class table shape mismatch"
        )
    if native_class_table.shape[1] != len(NATIVE_CLASS_COLUMNS):
        raise AssertionError(
            "second-window promotion native-class table codebook mismatch"
        )
    if tuple(spectral_table.shape) != (1, len(SPECTRAL_CUT_COLUMNS)):
        raise AssertionError("second-window promotion spectral table shape mismatch")
    if poincare_table.shape[1] != len(POINCARE_COLUMNS):
        raise AssertionError("second-window promotion Poincare table codebook mismatch")
    if tuple(observable_table.shape) != (
        len(SECOND_WINDOW_PROMOTION_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("second-window promotion observable table shape mismatch")

    state_rows = table_rows(state_table, STATE_COLUMNS)
    edge_rows = table_rows(edge_table, EDGE_COLUMNS)
    spectral = table_rows(spectral_table, SPECTRAL_CUT_COLUMNS)[0]
    observables = {
        row["observable_code"]: row["value_x1e12"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if tuple(FIRST_WINDOW_BLOCK) != (5, 5, 2, 5):
        raise AssertionError("first promoted block constant mismatch")
    if tuple(SECOND_WINDOW_BLOCK) != (1, 4, 5, 5):
        raise AssertionError("second promoted block constant mismatch")
    if sum(row["promoted_window_repair_flag"] for row in state_rows) != 132:
        raise AssertionError("combined promoted state count mismatch")
    if sum(row["promoted_only_flag"] for row in state_rows) != 14:
        raise AssertionError("combined promoted-only state count mismatch")
    if sum(row["old_spectral_cut_edge_flag"] for row in edge_rows) != 6:
        raise AssertionError("parent spectral cut lineage mismatch")
    if sum(row["new_spectral_cut_edge_flag"] for row in edge_rows) != 6:
        raise AssertionError("fresh spectral cut edge count mismatch")
    if (
        spectral["old_cut_edge_count"],
        spectral["old_cut_edge_survival_count"],
        spectral["old_cut_edge_still_cut_count"],
        spectral["old_cut_edge_same_side_count"],
    ) != (6, 6, 6, 0):
        raise AssertionError("parent cut survival witness mismatch")
    if (
        spectral["cut_edge_count"],
        spectral["derived_cut_edge_count"],
        spectral["promoted_cut_edge_count"],
        spectral["promoted_only_cut_edge_count"],
    ) != (6, 6, 6, 0):
        raise AssertionError("fresh cut promoted-support witness mismatch")
    if (
        spectral["state_count"],
        spectral["lambda_2_x1e12"],
        spectral["lambda_3_x1e12"],
        spectral["cut_conductance_x1e12"],
        spectral["positive_state_count"],
        spectral["negative_state_count"],
        spectral["positive_volume"],
        spectral["negative_volume"],
    ) != (
        798,
        2_422_953_000,
        9_097_373_000,
        4_329_004_000,
        594,
        204,
        3_660,
        1_386,
    ):
        raise AssertionError("second-window promotion spectral witness mismatch")

    required_observables = {
        "boundary_union_word_count": 234_678,
        "trace_failure_word_count": 68_103,
        "bad_metric_word_count": 140_378,
        "metric_ok_word_count": 26_197,
        "closed_positive_metric_word_count": 984,
        "parent_state_count": 855,
        "state_count": 860,
        "new_state_count_vs_parent": 5,
        "parent_edge_count": 2_561,
        "undirected_edge_count": 2_571,
        "new_edge_count_vs_parent": 10,
        "component_count": 25,
        "combined_promoted_state_count": 132,
        "combined_promoted_only_state_count": 14,
        "merged_recurrent_class_size": 798,
        "merged_promoted_only_state_count": 11,
        "left_to_right_path_exists": 1,
        "shortest_path_length": 2,
        "parent_cut_edge_count": 6,
        "parent_cut_edge_survival_count": 6,
        "parent_cut_edge_still_cut_count": 6,
        "spectral_cut_edge_count": 6,
        "spectral_cut_promoted_edge_count": 6,
        "spectral_cut_promoted_only_edge_count": 0,
        "merged_lambda_2": 2_422_953_000,
        "merged_lambda_3": 9_097_373_000,
        "merged_cut_conductance": 4_329_004_000,
        "first_block_code": 5_525,
        "second_block_code": 1_455,
        "second_window_candidate_word_count": 1,
        "second_window_target_transfer_edge_id": 2_447,
    }
    for key, value in required_observables.items():
        code = SECOND_WINDOW_PROMOTION_OBSERVABLE_CODES[key]
        expected_value = int(value) if key in X1E12_OBSERVABLES else int(value) * SCALE
        if observables.get(code) != expected_value:
            raise AssertionError(f"second-window promotion observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("promotion_blocks") != [[5, 5, 2, 5], [1, 4, 5, 5]]:
        raise AssertionError("promotion block witness mismatch")
    if witness.get("promotion_profile", {}).get("new_state_count_vs_parent") != 5:
        raise AssertionError("promotion profile state witness mismatch")
    if witness.get("parent_cut_lineage", {}).get("parent_cut_edge_still_cut_count") != 6:
        raise AssertionError("parent cut lineage report witness mismatch")
    if witness.get("spectral_cut", {}).get("promoted_cut_edge_count") != 6:
        raise AssertionError("promoted cut support report witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("second-window promotion certificate status mismatch")

    inputs = report.get("inputs", {})
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
    assert_file_hash(
        inputs.get("second_window_report", {}),
        SECOND_WINDOW_REPORT,
        "second-window report input",
    )
    assert_file_hash(
        inputs.get("second_window_certificate", {}),
        SECOND_WINDOW_CERTIFICATE,
        "second-window certificate input",
    )
    assert_file_hash(
        inputs.get("second_window_tables", {}),
        SECOND_WINDOW_TABLES,
        "second-window tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion_manifest@1"
    ):
        raise AssertionError("second-window promotion manifest schema mismatch")
    if manifest.get("status") != STATUS:
        raise AssertionError("second-window promotion manifest status mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window promotion manifest report hash mismatch")
    if parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("second-window promotion manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("second-window promotion missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window promotion index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("second-window promotion index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_promotion()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
