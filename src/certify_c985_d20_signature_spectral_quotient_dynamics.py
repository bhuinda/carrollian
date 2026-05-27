from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_spectral_quotient_dynamics import (
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        QUOTIENT_BASIN_COMPARISON_COLUMNS,
        QUOTIENT_OBSERVABLE_COLUMNS,
        QUOTIENT_STATE_COLUMNS,
        QUOTIENT_TRANSITION_COLUMNS,
        SIGNATURE_TRANSFER_CERTIFICATE,
        SIGNATURE_TRANSFER_JSON,
        SIGNATURE_TRANSFER_REPORT,
        SIGNATURE_TRANSFER_TABLES,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_spectral_quotient_dynamics import (
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        QUOTIENT_BASIN_COMPARISON_COLUMNS,
        QUOTIENT_OBSERVABLE_COLUMNS,
        QUOTIENT_STATE_COLUMNS,
        QUOTIENT_TRANSITION_COLUMNS,
        SIGNATURE_TRANSFER_CERTIFICATE,
        SIGNATURE_TRANSFER_JSON,
        SIGNATURE_TRANSFER_REPORT,
        SIGNATURE_TRANSFER_TABLES,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        STATUS,
        THEOREM_ID,
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
        raise AssertionError(f"{label} path mismatch: {entry.get('path')} != {expected_rel}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_c985_d20_signature_spectral_quotient_dynamics() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    quotient = load_json(OUT_DIR / "signature_spectral_quotient_dynamics.json")
    certificate = load_json(OUT_DIR / "signature_spectral_quotient_certificate.json")
    states_csv = (OUT_DIR / "quotient_states.csv").read_text(encoding="utf-8")
    transitions_csv = (OUT_DIR / "quotient_transitions.csv").read_text(
        encoding="utf-8"
    )
    basin_csv = (OUT_DIR / "quotient_basin_comparison.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "quotient_observables.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "signature_spectral_quotient_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if quotient != expected["signature_spectral_quotient_dynamics"]:
        raise AssertionError("signature spectral quotient JSON is not reproducible")
    if states_csv != expected["quotient_states_csv"]:
        raise AssertionError("signature spectral quotient state CSV is not reproducible")
    if transitions_csv != expected["quotient_transitions_csv"]:
        raise AssertionError("signature spectral quotient transition CSV is not reproducible")
    if basin_csv != expected["quotient_basin_comparison_csv"]:
        raise AssertionError("signature spectral quotient basin CSV is not reproducible")
    if observable_csv != expected["quotient_observables_csv"]:
        raise AssertionError("signature spectral quotient observable CSV is not reproducible")
    if certificate != expected["signature_spectral_quotient_certificate"]:
        raise AssertionError("signature spectral quotient certificate is not reproducible")

    table_names = [
        "quotient_state_table",
        "quotient_transition_table",
        "quotient_basin_table",
        "quotient_observable_table",
        "quotient_transition_matrix",
        "quotient_stationary_vector",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature spectral quotient table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_spectral_quotient_dynamics@1":
        raise AssertionError("C985 d20 spectral quotient report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 spectral quotient is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 spectral quotient all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 spectral quotient checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 spectral quotient report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 spectral quotient report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "spectral_cut_report_certified",
        "spectral_cut_certificate_certified",
        "signature_transfer_report_certified",
        "signature_transfer_certificate_certified",
        "boundary_transfer_report_certified",
        "boundary_transfer_certificate_certified",
        "state_count_is_2",
        "state_masses_sum_to_one",
        "state_masses_match_spectral_cut",
        "cut_flux_matches_spectral_cut",
        "transition_matrix_matches_expected",
        "transition_rows_sum_to_one",
        "exact_stationary_law_holds",
        "quotient_lambda_2_matches_expected",
        "quotient_spectral_gap_matches_expected",
        "stationary_stay_probability_matches_expected",
        "signature_lambda_2_drop_matches_expected",
        "positive_exit_probability_matches_expected",
        "negative_exit_probability_matches_expected",
        "mask_edge_counts_match_spectral_cut",
        "signature_edge_counts_match_spectral_cut",
        "core_basin_masses_match_boundary_transfer",
        "induced_basin_masses_match_spectral_cut",
        "core_induced_tv_twice_matches_expected",
        "core_positive_tv_twice_matches_expected",
        "core_negative_tv_twice_matches_expected",
        "state_table_shape_is_2_by_13",
        "transition_table_shape_is_4_by_7",
        "basin_table_shape_is_3_by_10",
        "observable_table_shape_matches_codebook",
        "spectral_cut_json_schema_available",
        "signature_transfer_json_schema_available",
        "boundary_transfer_json_schema_available",
        "signature_transfer_tables_available",
        "boundary_transfer_tables_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 spectral quotient missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("positive_stationary_mass_x1e12") != 626107108209:
        raise AssertionError("spectral quotient positive mass mismatch")
    if witness.get("negative_stationary_mass_x1e12") != 373892891791:
        raise AssertionError("spectral quotient negative mass mismatch")
    if witness.get("undirected_cut_flux_x1e12") != 238962451389:
        raise AssertionError("spectral quotient cut flux mismatch")
    if witness.get("directed_cross_flux_twice_x1e12") != 238962451389:
        raise AssertionError("spectral quotient twice-flow mismatch")
    if witness.get("transition_matrix_x1e12") != [
        [809168073437, 190831926563],
        [319560035288, 680439964712],
    ]:
        raise AssertionError("spectral quotient transition matrix mismatch")
    if witness.get("quotient_lambda_2_x1e12") != 489608038149:
        raise AssertionError("spectral quotient lambda_2 mismatch")
    if witness.get("quotient_spectral_gap_x1e12") != 510391961851:
        raise AssertionError("spectral quotient gap mismatch")
    if witness.get("stationary_stay_probability_x1e12") != 761037548611:
        raise AssertionError("spectral quotient stay probability mismatch")
    if witness.get("positive_to_negative_probability_x1e12") != 190831926563:
        raise AssertionError("spectral quotient positive exit mismatch")
    if witness.get("negative_to_positive_probability_x1e12") != 319560035288:
        raise AssertionError("spectral quotient negative exit mismatch")
    if witness.get("signature_lambda_2_minus_quotient_lambda_2_x1e12") != 97644498065:
        raise AssertionError("spectral quotient lambda drop mismatch")
    if witness.get("core_basin_masses_x1e12") != {
        "10": 121358270826,
        "43": 488349486805,
        "boundary": 390292242370,
    }:
        raise AssertionError("spectral quotient core basin masses mismatch")
    if witness.get("induced_basin_masses_x1e12") != {
        "10": 200037326277,
        "43": 406767255209,
        "boundary": 393195418514,
    }:
        raise AssertionError("spectral quotient induced basin masses mismatch")
    if witness.get("core_induced_tv_twice_x1e12") != 163164463191:
        raise AssertionError("spectral quotient core induced TV mismatch")

    state_table = np.asarray(tables["quotient_state_table"], dtype=np.int64)
    transition_table = np.asarray(tables["quotient_transition_table"], dtype=np.int64)
    basin_table = np.asarray(tables["quotient_basin_table"], dtype=np.int64)
    observable_table = np.asarray(tables["quotient_observable_table"], dtype=np.int64)
    transition_matrix = np.asarray(tables["quotient_transition_matrix"], dtype=np.int64)
    stationary_vector = np.asarray(tables["quotient_stationary_vector"], dtype=np.int64)

    if state_table.shape != (2, len(QUOTIENT_STATE_COLUMNS)):
        raise AssertionError("spectral quotient state table shape mismatch")
    if transition_table.shape != (4, len(QUOTIENT_TRANSITION_COLUMNS)):
        raise AssertionError("spectral quotient transition table shape mismatch")
    if basin_table.shape != (3, len(QUOTIENT_BASIN_COMPARISON_COLUMNS)):
        raise AssertionError("spectral quotient basin table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(QUOTIENT_OBSERVABLE_COLUMNS)):
        raise AssertionError("spectral quotient observable table shape mismatch")
    if transition_matrix.shape != (2, 2):
        raise AssertionError("spectral quotient transition matrix shape mismatch")
    if not np.all(transition_matrix.sum(axis=1) == 1_000_000_000_000):
        raise AssertionError("spectral quotient transition rows mismatch")
    if stationary_vector.tolist() != [626107108209, 373892891791]:
        raise AssertionError("spectral quotient stationary vector mismatch")
    if int(stationary_vector.sum()) != 1_000_000_000_000:
        raise AssertionError("spectral quotient stationary sum mismatch")
    if int(transition_table[:, 5].sum()) != 2_000_000_000_000:
        raise AssertionError("spectral quotient twice-flow table sum mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("spectral_cut_report", {}), SPECTRAL_CUT_REPORT, "spectral cut report input")
    assert_file_hash(inputs.get("spectral_cut", {}), SPECTRAL_CUT_JSON, "spectral cut JSON input")
    assert_file_hash(inputs.get("spectral_cut_tables", {}), SPECTRAL_CUT_TABLES, "spectral cut tables input")
    assert_file_hash(
        inputs.get("spectral_cut_certificate", {}),
        SPECTRAL_CUT_CERTIFICATE,
        "spectral cut certificate input",
    )
    assert_file_hash(
        inputs.get("signature_transfer_report", {}),
        SIGNATURE_TRANSFER_REPORT,
        "signature transfer report input",
    )
    assert_file_hash(
        inputs.get("signature_transfer", {}),
        SIGNATURE_TRANSFER_JSON,
        "signature transfer JSON input",
    )
    assert_file_hash(
        inputs.get("signature_transfer_tables", {}),
        SIGNATURE_TRANSFER_TABLES,
        "signature transfer tables input",
    )
    assert_file_hash(
        inputs.get("signature_transfer_certificate", {}),
        SIGNATURE_TRANSFER_CERTIFICATE,
        "signature transfer certificate input",
    )
    assert_file_hash(
        inputs.get("boundary_transfer_report", {}),
        BOUNDARY_TRANSFER_REPORT,
        "boundary transfer report input",
    )
    assert_file_hash(inputs.get("boundary_transfer", {}), BOUNDARY_TRANSFER_JSON, "boundary transfer JSON input")
    assert_file_hash(
        inputs.get("boundary_transfer_tables", {}),
        BOUNDARY_TRANSFER_TABLES,
        "boundary transfer tables input",
    )
    assert_file_hash(
        inputs.get("boundary_transfer_certificate", {}),
        BOUNDARY_TRANSFER_CERTIFICATE,
        "boundary transfer certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_spectral_quotient_dynamics_manifest@1":
        raise AssertionError("C985 d20 spectral quotient manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 spectral quotient manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 spectral quotient manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 spectral quotient missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 spectral quotient index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 spectral quotient index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_spectral_quotient_dynamics@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "transition_matrix_x1e12": witness.get("transition_matrix_x1e12"),
        "quotient_lambda_2_x1e12": witness.get("quotient_lambda_2_x1e12"),
        "quotient_spectral_gap_x1e12": witness.get("quotient_spectral_gap_x1e12"),
        "stationary_stay_probability_x1e12": witness.get("stationary_stay_probability_x1e12"),
        "core_induced_tv_twice_x1e12": witness.get("core_induced_tv_twice_x1e12"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_spectral_quotient_dynamics()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
