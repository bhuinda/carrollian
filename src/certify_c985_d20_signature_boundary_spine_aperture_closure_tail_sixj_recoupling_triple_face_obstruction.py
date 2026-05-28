from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction import (
        DERIVE_SCRIPT,
        FACE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PAIR_OBSTRUCTION_CERTIFICATE,
        PAIR_OBSTRUCTION_REPORT,
        PAIR_OBSTRUCTION_TABLES,
        STATUS,
        THEOREM_ID,
        TRIPLE_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction import (
        DERIVE_SCRIPT,
        FACE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PAIR_OBSTRUCTION_CERTIFICATE,
        PAIR_OBSTRUCTION_REPORT,
        PAIR_OBSTRUCTION_TABLES,
        STATUS,
        THEOREM_ID,
        TRIPLE_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    obstruction = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_certificate.json"
    )
    triple_csv = (OUT_DIR / "sixj_recoupling_triple_interventions.csv").read_text(
        encoding="utf-8"
    )
    face_csv = (OUT_DIR / "sixj_recoupling_face_cover.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "sixj_recoupling_triple_face_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if obstruction != expected["triple_face_obstruction"]:
        raise AssertionError("sixj triple obstruction JSON is not reproducible")
    if triple_csv != expected["triple_interventions_csv"]:
        raise AssertionError("sixj triple intervention CSV is not reproducible")
    if face_csv != expected["face_cover_csv"]:
        raise AssertionError("sixj face cover CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("sixj triple observable CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("sixj triple certificate is not reproducible")

    for name in ["triple_table", "face_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"sixj triple table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction@1"
    ):
        raise AssertionError("sixj triple report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("sixj triple face obstruction is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sixj triple all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("sixj triple checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("sixj triple report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("sixj triple report hash is not reproducible")

    triple_table = np.asarray(tables["triple_table"], dtype=np.int64)
    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(triple_table.shape) != (84, len(TRIPLE_COLUMNS)):
        raise AssertionError("sixj triple table shape mismatch")
    if tuple(face_table.shape) != (4, len(FACE_COLUMNS)):
        raise AssertionError("sixj face table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("sixj triple observable table shape mismatch")

    triple_rows = table_rows(triple_table, TRIPLE_COLUMNS)
    face_rows = table_rows(face_table, FACE_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if any(row["support_changed_flag"] for row in triple_rows):
        raise AssertionError("sixj triple support-changing row found")
    if not all(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        for row in triple_rows
    ):
        raise AssertionError("sixj triple old cut support mismatch")
    if not all(row["covered_triple_count"] > 0 for row in face_rows):
        raise AssertionError("sixj face cover table has uncovered face")
    if not all(
        row["best_triple_old_cut_edge_still_cut_count"] == 6 for row in face_rows
    ):
        raise AssertionError("sixj face best row old cut support mismatch")

    selected = [row for row in triple_rows if row["selected_best_flag"] == 1]
    if len(selected) != 1:
        raise AssertionError("sixj triple selected best row count mismatch")
    best = selected[0]
    if (
        best["block_code_a"],
        best["block_code_b"],
        best["block_code_c"],
        best["state_count"],
        best["edge_count"],
        best["cut_edge_count"],
        best["old_cut_edge_still_cut_count"],
        best["cut_conductance_x1e12"],
        best["conductance_reduction_x1e12"],
        best["full_face_count"],
    ) != (5_255, 1_252, 5_252, 900, 2_711, 6, 6, 3_649_635_000, 679_369_000, 2):
        raise AssertionError("sixj triple selected best witness mismatch")

    required_observables = {
        "base_state_count": 860,
        "base_edge_count": 2_571,
        "base_cut_edge_count": 6,
        "base_cut_conductance_x1e12": 4_329_004_000,
        "candidate_block_count": 9,
        "triple_intervention_count": 84,
        "face_count": 4,
        "face_covered_count": 4,
        "support_changing_triple_count": 0,
        "best_block_code_a": 5_255,
        "best_block_code_b": 1_252,
        "best_block_code_c": 5_252,
        "best_state_count": 900,
        "best_edge_count": 2_711,
        "best_cut_edge_count": 6,
        "best_old_cut_edge_still_cut_count": 6,
        "best_lambda_2_x1e12": 2_443_681_000,
        "best_cut_conductance_x1e12": 3_649_635_000,
        "best_conductance_reduction_x1e12": 679_369_000,
        "best_full_face_count": 2,
        "closed_metric_word_count": 984,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"sixj triple observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("pair_obstruction_report", {}),
        PAIR_OBSTRUCTION_REPORT,
        "pair obstruction report input",
    )
    assert_file_hash(
        inputs.get("pair_obstruction_certificate", {}),
        PAIR_OBSTRUCTION_CERTIFICATE,
        "pair obstruction certificate input",
    )
    assert_file_hash(
        inputs.get("pair_obstruction_tables", {}),
        PAIR_OBSTRUCTION_TABLES,
        "pair obstruction tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction_manifest@1"
    ):
        raise AssertionError("sixj triple manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj triple manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("sixj triple manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("sixj triple missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj triple index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sixj triple index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_recoupling_triple_face_obstruction()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
