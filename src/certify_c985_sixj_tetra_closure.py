from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_sixj_tetra_closure import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SIZE_SUMMARY_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRIPLE_FACE_CERTIFICATE,
        TRIPLE_FACE_REPORT,
        TRIPLE_FACE_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_sixj_tetra_closure import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SIZE_SUMMARY_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRIPLE_FACE_CERTIFICATE,
        TRIPLE_FACE_REPORT,
        TRIPLE_FACE_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    obstruction = load_json(
        OUT_DIR
        / "sixj_tetra_closure.json"
    )
    certificate = load_json(
        OUT_DIR
        / "sixj_tetra_closure_certificate.json"
    )
    interventions_csv = (
        OUT_DIR / "sixj_recoupling_tetrahedral_closure_interventions.csv"
    ).read_text(encoding="utf-8")
    size_summary_csv = (
        OUT_DIR / "sixj_recoupling_tetrahedral_size_summary.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "sixj_recoupling_tetrahedral_closure_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "sixj_tetra_closure_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if obstruction != expected["tetrahedral_closure_obstruction"]:
        raise AssertionError("sixj tetrahedral obstruction JSON is not reproducible")
    if interventions_csv != expected["interventions_csv"]:
        raise AssertionError("sixj tetrahedral intervention CSV is not reproducible")
    if size_summary_csv != expected["size_summary_csv"]:
        raise AssertionError("sixj tetrahedral size CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("sixj tetrahedral observable CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("sixj tetrahedral certificate is not reproducible")

    for name in ["intervention_table", "size_summary_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"sixj tetrahedral table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction@1"
    ):
        raise AssertionError("sixj tetrahedral report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("sixj tetrahedral obstruction is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sixj tetrahedral all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("sixj tetrahedral checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("sixj tetrahedral report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("sixj tetrahedral report hash is not reproducible")

    intervention_table = np.asarray(tables["intervention_table"], dtype=np.int64)
    size_summary_table = np.asarray(tables["size_summary_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(intervention_table.shape) != (382, len(INTERVENTION_COLUMNS)):
        raise AssertionError("sixj tetrahedral intervention table shape mismatch")
    if tuple(size_summary_table.shape) != (6, len(SIZE_SUMMARY_COLUMNS)):
        raise AssertionError("sixj tetrahedral size table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("sixj tetrahedral observable table shape mismatch")

    intervention_rows = table_rows(intervention_table, INTERVENTION_COLUMNS)
    size_rows = table_rows(size_summary_table, SIZE_SUMMARY_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if any(row["support_changed_flag"] for row in intervention_rows):
        raise AssertionError("sixj tetrahedral support-changing row found")
    if not all(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        for row in intervention_rows
    ):
        raise AssertionError("sixj tetrahedral old cut support mismatch")
    if [row["intervention_count"] for row in size_rows] != [126, 126, 84, 36, 9, 1]:
        raise AssertionError("sixj tetrahedral rank count mismatch")
    if any(row["support_changing_count"] for row in size_rows):
        raise AssertionError("sixj tetrahedral rank support-changing mismatch")

    selected = [row for row in intervention_rows if row["selected_best_flag"] == 1]
    if len(selected) != 1:
        raise AssertionError("sixj tetrahedral selected best row count mismatch")
    best = selected[0]
    if (
        best["intervention_size"],
        best["block_code_0"],
        best["block_code_1"],
        best["block_code_2"],
        best["block_code_3"],
        best["state_count"],
        best["edge_count"],
        best["cut_edge_count"],
        best["old_cut_edge_still_cut_count"],
        best["cut_conductance_x1e12"],
        best["conductance_reduction_x1e12"],
    ) != (4, 4_552, 5_255, 1_252, 5_252, 900, 2_711, 6, 6, 3_649_635_000, 679_369_000):
        raise AssertionError("sixj tetrahedral selected best witness mismatch")

    all_nine = [row for row in intervention_rows if row["all_nine_flag"] == 1]
    if len(all_nine) != 1:
        raise AssertionError("sixj tetrahedral all-nine row count mismatch")
    all_nine_row = all_nine[0]
    if (
        all_nine_row["state_count"],
        all_nine_row["edge_count"],
        all_nine_row["cut_edge_count"],
        all_nine_row["old_cut_edge_still_cut_count"],
        all_nine_row["promoted_only_cut_edge_count"],
        all_nine_row["cut_conductance_x1e12"],
    ) != (975, 3_068, 11, 6, 5, 4_934_948_000):
        raise AssertionError("sixj tetrahedral all-nine witness mismatch")

    required_observables = {
        "base_state_count": 860,
        "base_edge_count": 2_571,
        "base_cut_edge_count": 6,
        "base_cut_conductance_x1e12": 4_329_004_000,
        "candidate_block_count": 9,
        "min_intervention_size": 4,
        "max_intervention_size": 9,
        "intervention_count": 382,
        "rank4_intervention_count": 126,
        "rank5_intervention_count": 126,
        "rank6_intervention_count": 84,
        "rank7_intervention_count": 36,
        "rank8_intervention_count": 9,
        "rank9_intervention_count": 1,
        "support_changing_intervention_count": 0,
        "best_intervention_size": 4,
        "best_block_code_0": 4_552,
        "best_block_code_1": 5_255,
        "best_block_code_2": 1_252,
        "best_block_code_3": 5_252,
        "best_state_count": 900,
        "best_edge_count": 2_711,
        "best_cut_edge_count": 6,
        "best_old_cut_edge_still_cut_count": 6,
        "best_lambda_2_x1e12": 2_443_681_000,
        "best_cut_conductance_x1e12": 3_649_635_000,
        "best_conductance_reduction_x1e12": 679_369_000,
        "all_nine_state_count": 975,
        "all_nine_edge_count": 3_068,
        "all_nine_cut_edge_count": 11,
        "all_nine_old_cut_edge_still_cut_count": 6,
        "all_nine_promoted_only_cut_edge_count": 5,
        "all_nine_cut_conductance_x1e12": 4_934_948_000,
        "closed_metric_word_count": 984,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"sixj tetrahedral observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("triple_face_report", {}),
        TRIPLE_FACE_REPORT,
        "triple-face report input",
    )
    assert_file_hash(
        inputs.get("triple_face_certificate", {}),
        TRIPLE_FACE_CERTIFICATE,
        "triple-face certificate input",
    )
    assert_file_hash(
        inputs.get("triple_face_tables", {}),
        TRIPLE_FACE_TABLES,
        "triple-face tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction_manifest@1"
    ):
        raise AssertionError("sixj tetrahedral manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj tetrahedral manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("sixj tetrahedral manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("sixj tetrahedral missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj tetrahedral index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sixj tetrahedral index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_tetrahedral_closure_obstruction()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
