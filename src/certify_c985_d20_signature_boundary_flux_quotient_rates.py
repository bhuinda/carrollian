from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_flux_quotient_rates import (
        BOUNDARY_ENTROPY_TERM_COLUMNS,
        BOUNDARY_FLUX_CERTIFICATE,
        BOUNDARY_FLUX_JSON,
        BOUNDARY_FLUX_REPORT,
        BOUNDARY_FLUX_TABLES,
        BOUNDARY_PARTITION_SUMMARY,
        BOUNDARY_RATE_OBSERVABLE_COLUMNS,
        BOUNDARY_RATE_PARTITION_COLUMNS,
        BOUNDARY_REFINED_TRANSITION_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        QUOTIENT_CERTIFICATE,
        QUOTIENT_JSON,
        QUOTIENT_REPORT,
        QUOTIENT_STATES,
        QUOTIENT_TABLES,
        QUOTIENT_TRANSITIONS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_flux_quotient_rates import (
        BOUNDARY_ENTROPY_TERM_COLUMNS,
        BOUNDARY_FLUX_CERTIFICATE,
        BOUNDARY_FLUX_JSON,
        BOUNDARY_FLUX_REPORT,
        BOUNDARY_FLUX_TABLES,
        BOUNDARY_PARTITION_SUMMARY,
        BOUNDARY_RATE_OBSERVABLE_COLUMNS,
        BOUNDARY_RATE_PARTITION_COLUMNS,
        BOUNDARY_REFINED_TRANSITION_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        QUOTIENT_CERTIFICATE,
        QUOTIENT_JSON,
        QUOTIENT_REPORT,
        QUOTIENT_STATES,
        QUOTIENT_TABLES,
        QUOTIENT_TRANSITIONS,
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


def validate_c985_d20_signature_boundary_flux_quotient_rates() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    rate_readout = load_json(OUT_DIR / "signature_boundary_flux_quotient_rates.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_flux_quotient_rates_certificate.json"
    )
    partition_csv = (OUT_DIR / "boundary_rate_partitions.csv").read_text(
        encoding="utf-8"
    )
    transition_csv = (OUT_DIR / "boundary_refined_transition_rows.csv").read_text(
        encoding="utf-8"
    )
    entropy_csv = (OUT_DIR / "boundary_entropy_terms.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "boundary_rate_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_flux_quotient_rates_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if rate_readout != expected["signature_boundary_flux_quotient_rates"]:
        raise AssertionError("boundary flux quotient rates JSON is not reproducible")
    if partition_csv != expected["boundary_rate_partitions_csv"]:
        raise AssertionError("boundary rate partition CSV is not reproducible")
    if transition_csv != expected["boundary_refined_transition_rows_csv"]:
        raise AssertionError("boundary refined transition CSV is not reproducible")
    if entropy_csv != expected["boundary_entropy_terms_csv"]:
        raise AssertionError("boundary entropy term CSV is not reproducible")
    if observable_csv != expected["boundary_rate_observables_csv"]:
        raise AssertionError("boundary rate observable CSV is not reproducible")
    if certificate != expected["signature_boundary_flux_quotient_rates_certificate"]:
        raise AssertionError("boundary flux quotient rates certificate is not reproducible")

    table_names = [
        "boundary_rate_partition_table",
        "boundary_refined_transition_table",
        "boundary_entropy_term_table",
        "boundary_rate_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"boundary flux quotient rates table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_flux_quotient_rates@1":
        raise AssertionError("C985 d20 boundary flux quotient rates report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary flux quotient rates is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary flux quotient rates all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary flux quotient rates checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary flux quotient rates report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary flux quotient rates report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "boundary_flux_report_certified",
        "boundary_flux_certificate_certified",
        "quotient_report_certified",
        "quotient_certificate_certified",
        "state_count_is_2",
        "boundary_partition_count_is_2",
        "boundary_flux_total_matches_quotient_cut_flux",
        "boundary_partition_codes_match_expected",
        "high_negative_flux_matches_expected",
        "central_negative_flux_matches_expected",
        "boundary_flux_fractions_match_expected",
        "positive_refined_row_sums_to_one",
        "negative_refined_row_sums_to_one",
        "positive_partition_exits_sum_to_quotient_exit",
        "negative_partition_exits_sum_to_quotient_exit",
        "refined_self_probabilities_match_quotient_returns",
        "central_accounts_for_same_share_both_directions",
        "partition_flow_reversibility_holds_exactly",
        "refined_twice_flows_sum_to_source_twice_masses",
        "quotient_entropy_rate_matches_upstream",
        "refined_entropy_rate_matches_expected",
        "entropy_refinement_surplus_matches_split_formula",
        "refined_entropy_exceeds_quotient_entropy",
        "partition_table_shape_is_2_by_13",
        "refined_transition_table_shape_is_6_by_10",
        "entropy_term_table_shape_is_6_by_7",
        "observable_table_shape_matches_codebook",
        "boundary_flux_json_schema_available",
        "quotient_json_schema_available",
        "boundary_flux_tables_available",
        "quotient_tables_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(
            f"C985 d20 boundary flux quotient rates missing true checks: {missing}"
        )

    witness = report.get("witness", {})
    if witness.get("positive_stationary_mass_x1e12") != 626107108209:
        raise AssertionError("boundary rate positive mass mismatch")
    if witness.get("negative_stationary_mass_x1e12") != 373892891791:
        raise AssertionError("boundary rate negative mass mismatch")
    if witness.get("total_undirected_cut_flux_x1e12") != 238962451389:
        raise AssertionError("boundary rate cut flux mismatch")
    if witness.get("high_negative_undirected_cut_flux_x1e12") != 3712054656:
        raise AssertionError("boundary rate high-negative flux mismatch")
    if witness.get("central_negative_undirected_cut_flux_x1e12") != 235250396733:
        raise AssertionError("boundary rate central-negative flux mismatch")
    if witness.get("positive_boundary_exit_decomposition_x1e12") != {
        "self": 809168073437,
        "high_negative": 2964392679,
        "central_negative": 187867533884,
    }:
        raise AssertionError("boundary rate positive decomposition mismatch")
    if witness.get("negative_boundary_exit_decomposition_x1e12") != {
        "high_negative": 4964061550,
        "central_negative": 314595973738,
        "self": 680439964712,
    }:
        raise AssertionError("boundary rate negative decomposition mismatch")
    if witness.get("central_negative_transition_share_x1e12") != 984465950050:
        raise AssertionError("boundary rate central share mismatch")
    if witness.get("quotient_entropy_rate_x1e12") != 539439395042:
        raise AssertionError("boundary rate quotient entropy mismatch")
    if witness.get("refined_boundary_entropy_rate_x1e12") != 558582139199:
        raise AssertionError("boundary rate refined entropy mismatch")
    if witness.get("entropy_refinement_surplus_x1e12") != 19142744157:
        raise AssertionError("boundary rate entropy surplus mismatch")
    if witness.get("boundary_split_entropy_x1e12") != 80107749339:
        raise AssertionError("boundary rate split entropy mismatch")

    partition_table = np.asarray(tables["boundary_rate_partition_table"], dtype=np.int64)
    transition_table = np.asarray(
        tables["boundary_refined_transition_table"],
        dtype=np.int64,
    )
    entropy_table = np.asarray(tables["boundary_entropy_term_table"], dtype=np.int64)
    observable_table = np.asarray(tables["boundary_rate_observable_table"], dtype=np.int64)

    if partition_table.shape != (2, len(BOUNDARY_RATE_PARTITION_COLUMNS)):
        raise AssertionError("boundary rate partition table shape mismatch")
    if transition_table.shape != (6, len(BOUNDARY_REFINED_TRANSITION_COLUMNS)):
        raise AssertionError("boundary rate transition table shape mismatch")
    if entropy_table.shape != (6, len(BOUNDARY_ENTROPY_TERM_COLUMNS)):
        raise AssertionError("boundary rate entropy table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(BOUNDARY_RATE_OBSERVABLE_COLUMNS)):
        raise AssertionError("boundary rate observable table shape mismatch")
    if partition_table[:, 0].tolist() != [4, 5]:
        raise AssertionError("boundary rate partition order mismatch")
    if transition_table[:3, 7].sum() != 1_000_000_000_000:
        raise AssertionError("boundary rate positive refined row sum mismatch")
    if transition_table[3:, 7].sum() != 1_000_000_000_000:
        raise AssertionError("boundary rate negative refined row sum mismatch")
    if int(transition_table[:, 8].sum()) != 2_000_000_000_000:
        raise AssertionError("boundary rate twice-flow sum mismatch")
    if int(partition_table[:, 4].sum()) != 238962451389:
        raise AssertionError("boundary rate partition flux sum mismatch")
    if int(entropy_table[:, 6].sum()) != 558582139199:
        raise AssertionError("boundary rate entropy contribution sum mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("boundary rate observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("boundary_flux_report", {}), BOUNDARY_FLUX_REPORT, "boundary flux report input")
    assert_file_hash(inputs.get("boundary_flux", {}), BOUNDARY_FLUX_JSON, "boundary flux JSON input")
    assert_file_hash(inputs.get("boundary_flux_tables", {}), BOUNDARY_FLUX_TABLES, "boundary flux tables input")
    assert_file_hash(
        inputs.get("boundary_flux_certificate", {}),
        BOUNDARY_FLUX_CERTIFICATE,
        "boundary flux certificate input",
    )
    assert_file_hash(
        inputs.get("boundary_partition_summary", {}),
        BOUNDARY_PARTITION_SUMMARY,
        "boundary partition input",
    )
    assert_file_hash(inputs.get("quotient_report", {}), QUOTIENT_REPORT, "quotient report input")
    assert_file_hash(inputs.get("quotient", {}), QUOTIENT_JSON, "quotient JSON input")
    assert_file_hash(inputs.get("quotient_tables", {}), QUOTIENT_TABLES, "quotient tables input")
    assert_file_hash(
        inputs.get("quotient_certificate", {}),
        QUOTIENT_CERTIFICATE,
        "quotient certificate input",
    )
    assert_file_hash(inputs.get("quotient_states", {}), QUOTIENT_STATES, "quotient states input")
    assert_file_hash(
        inputs.get("quotient_transitions", {}),
        QUOTIENT_TRANSITIONS,
        "quotient transitions input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_flux_quotient_rates_manifest@1":
        raise AssertionError("C985 d20 boundary flux quotient rates manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary flux quotient rates manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary flux quotient rates manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 boundary flux quotient rates missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary flux quotient rates index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary flux quotient rates index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_flux_quotient_rates@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "positive_boundary_exit_decomposition_x1e12": witness.get(
            "positive_boundary_exit_decomposition_x1e12"
        ),
        "negative_boundary_exit_decomposition_x1e12": witness.get(
            "negative_boundary_exit_decomposition_x1e12"
        ),
        "central_negative_transition_share_x1e12": witness.get(
            "central_negative_transition_share_x1e12"
        ),
        "refined_boundary_entropy_rate_x1e12": witness.get(
            "refined_boundary_entropy_rate_x1e12"
        ),
        "entropy_refinement_surplus_x1e12": witness.get(
            "entropy_refinement_surplus_x1e12"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_flux_quotient_rates()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
