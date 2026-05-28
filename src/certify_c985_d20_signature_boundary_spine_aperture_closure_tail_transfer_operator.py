from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REPAIRED_AUTOMATON_CERTIFICATE,
        REPAIRED_AUTOMATON_POINCARE,
        REPAIRED_AUTOMATON_REPORT,
        REPAIRED_AUTOMATON_SPECTRAL_CUT,
        REPAIRED_AUTOMATON_STATES,
        REPAIRED_AUTOMATON_TABLES,
        REPAIRED_AUTOMATON_TRANSITIONS,
        SIDE_FLOW_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_OBSERVABLE_CODES,
        TRANSFER_STATE_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REPAIRED_AUTOMATON_CERTIFICATE,
        REPAIRED_AUTOMATON_POINCARE,
        REPAIRED_AUTOMATON_REPORT,
        REPAIRED_AUTOMATON_SPECTRAL_CUT,
        REPAIRED_AUTOMATON_STATES,
        REPAIRED_AUTOMATON_TABLES,
        REPAIRED_AUTOMATON_TRANSITIONS,
        SIDE_FLOW_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSFER_EDGE_COLUMNS,
        TRANSFER_OBSERVABLE_CODES,
        TRANSFER_STATE_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    transfer_operator = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_transfer_operator.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate.json"
    )
    states_csv = (OUT_DIR / "aperture_closure_tail_transfer_states.csv").read_text(
        encoding="utf-8"
    )
    edges_csv = (OUT_DIR / "aperture_closure_tail_transfer_edges.csv").read_text(
        encoding="utf-8"
    )
    side_flow_csv = (
        OUT_DIR / "aperture_closure_tail_transfer_side_flow.csv"
    ).read_text(encoding="utf-8")
    centers_csv = (OUT_DIR / "aperture_closure_tail_transfer_centers.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_transfer_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_transfer_operator_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        transfer_operator
        != expected[
            "signature_boundary_spine_aperture_closure_tail_transfer_operator"
        ]
    ):
        raise AssertionError("transfer operator JSON is not reproducible")
    if states_csv != expected["transfer_states_csv"]:
        raise AssertionError("transfer states CSV is not reproducible")
    if edges_csv != expected["transfer_edges_csv"]:
        raise AssertionError("transfer edges CSV is not reproducible")
    if side_flow_csv != expected["transfer_side_flow_csv"]:
        raise AssertionError("transfer side-flow CSV is not reproducible")
    if centers_csv != expected["transfer_centers_csv"]:
        raise AssertionError("transfer centers CSV is not reproducible")
    if observables_csv != expected["transfer_observables_csv"]:
        raise AssertionError("transfer observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_transfer_operator_certificate"
        ]
    ):
        raise AssertionError("transfer certificate is not reproducible")

    for name in [
        "state_table",
        "edge_table",
        "side_table",
        "center_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"transfer table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator@1"
    ):
        raise AssertionError("transfer report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("transfer layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("transfer all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("transfer checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("transfer report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("transfer report is not reproducible")

    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    side_table = np.asarray(tables["side_table"], dtype=np.int64)
    center_table = np.asarray(tables["center_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if state_table.shape != (787, len(TRANSFER_STATE_COLUMNS)):
        raise AssertionError("transfer state table shape mismatch")
    if edge_table.shape != (2_501, len(TRANSFER_EDGE_COLUMNS)):
        raise AssertionError("transfer edge table shape mismatch")
    if side_table.shape != (2, len(SIDE_FLOW_COLUMNS)):
        raise AssertionError("transfer side table shape mismatch")
    if center_table.shape != (4, len(CENTER_COLUMNS)):
        raise AssertionError("transfer center table shape mismatch")
    if observable_table.shape != (
        len(TRANSFER_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("transfer observable table shape mismatch")

    state_rows = table_rows(state_table, TRANSFER_STATE_COLUMNS)
    edge_rows = table_rows(edge_table, TRANSFER_EDGE_COLUMNS)
    side_rows = table_rows(side_table, SIDE_FLOW_COLUMNS)
    center_rows = table_rows(center_table, CENTER_COLUMNS)
    observables = {
        row["observable_code"]: row["value_x1e12"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sum(row["stationary_mass_x1e12"] for row in state_rows) != 10**12:
        raise AssertionError("stationary masses do not sum to one")
    if sum(row["undirected_stationary_flux_x1e12"] for row in edge_rows) != 10**12:
        raise AssertionError("edge fluxes do not sum to one")
    if sum(row["weighted_degree"] for row in state_rows) != 11_674:
        raise AssertionError("weighted degree total mismatch")
    if sum(row["edge_weight"] for row in edge_rows) != 5_837:
        raise AssertionError("edge weight total mismatch")
    if sum(row["native_transition_flag"] for row in edge_rows) != 1_668:
        raise AssertionError("native transfer edge count mismatch")
    if sum(row["derived_transition_flag"] for row in edge_rows) != 833:
        raise AssertionError("derived transfer edge count mismatch")
    if sum(row["derived_only_transition_flag"] for row in edge_rows) != 746:
        raise AssertionError("derived-only transfer edge count mismatch")
    if sum(row["spectral_cut_edge_flag"] for row in edge_rows) != 6:
        raise AssertionError("spectral cut edge count mismatch")
    if (
        sum(
            row["undirected_stationary_flux_x1e12"]
            for row in edge_rows
            if row["spectral_cut_edge_flag"] == 1
        )
        != 1_027_925_304
    ):
        raise AssertionError("spectral cut flux mismatch")
    side_masses = {
        row["spectral_side_code"]: row["stationary_mass_x1e12"]
        for row in side_rows
    }
    if side_masses != {-1: 115_127_634_054, 1: 884_872_365_946}:
        raise AssertionError("spectral side mass mismatch")
    center = next(row for row in center_rows if row["center_code"] == 0)
    cut_center = next(row for row in center_rows if row["center_code"] == 2)
    if (
        center["center_x_x1e12"],
        center["center_y_x1e12"],
        center["center_radius_x1e12"],
        center["distance_to_cut_center_x1e12"],
        center["distance_to_right_boundary_x1e12"],
    ) != (
        46_510_986_546,
        -16_614_954_352,
        49_389_559_000,
        294_814_140_000,
        41_209_484_000,
    ):
        raise AssertionError("flow center witness mismatch")
    if (
        cut_center["center_x_x1e12"],
        cut_center["center_y_x1e12"],
        cut_center["center_radius_x1e12"],
    ) != (-4_400_616_000, 120_940_603_250, 121_020_638_000):
        raise AssertionError("cut center witness mismatch")
    boundary = report.get("witness", {}).get("boundary_masses", {})
    if (
        boundary.get("left_mass_x1e12"),
        boundary.get("gate_mass_x1e12"),
        boundary.get("right_mass_x1e12"),
    ) != (2_141_511_051, 770_943_978, 1_627_548_398):
        raise AssertionError("boundary mass witness mismatch")
    if report.get("witness", {}).get("top_stationary_state_id") != 443:
        raise AssertionError("top stationary state mismatch")
    if report.get("witness", {}).get("top_stationary_mass_x1e12") != 7_623_779_339:
        raise AssertionError("top stationary mass mismatch")

    required_observables = {
        "transfer_state_count": 787,
        "transfer_edge_count": 2_501,
        "total_edge_weight": 5_837,
        "total_weighted_degree": 11_674,
        "native_edge_count": 1_668,
        "derived_edge_count": 833,
        "derived_only_edge_count": 746,
        "native_edge_weight": 5_004,
        "derived_edge_weight": 833,
        "spectral_cut_edge_count": 6,
        "spectral_cut_weight": 6,
        "top_stationary_state_id": 443,
    }
    for key, value in required_observables.items():
        code = TRANSFER_OBSERVABLE_CODES[key]
        if observables.get(code) != value * 10**12:
            raise AssertionError(f"observable {key} mismatch")

    if certificate.get("status") != STATUS:
        raise AssertionError("transfer certificate status mismatch")
    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("repaired_automaton_report", {}),
        REPAIRED_AUTOMATON_REPORT,
        "repaired automaton report input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_certificate", {}),
        REPAIRED_AUTOMATON_CERTIFICATE,
        "repaired automaton certificate input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_states", {}),
        REPAIRED_AUTOMATON_STATES,
        "repaired automaton states input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_transitions", {}),
        REPAIRED_AUTOMATON_TRANSITIONS,
        "repaired automaton transitions input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_poincare", {}),
        REPAIRED_AUTOMATON_POINCARE,
        "repaired automaton Poincare input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_spectral_cut", {}),
        REPAIRED_AUTOMATON_SPECTRAL_CUT,
        "repaired automaton spectral-cut input",
    )
    assert_file_hash(
        inputs.get("repaired_automaton_tables", {}),
        REPAIRED_AUTOMATON_TABLES,
        "repaired automaton tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator_manifest@1"
    ):
        raise AssertionError("transfer manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("transfer manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("transfer manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("transfer missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("transfer index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("transfer index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_transfer_operator@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_transfer_operator()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
