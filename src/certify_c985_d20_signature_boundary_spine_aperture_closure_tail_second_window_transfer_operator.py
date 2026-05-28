from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SECOND_WINDOW_PROMOTION_CERTIFICATE,
        SECOND_WINDOW_PROMOTION_EDGES,
        SECOND_WINDOW_PROMOTION_POINCARE,
        SECOND_WINDOW_PROMOTION_REPORT,
        SECOND_WINDOW_PROMOTION_SPECTRAL_CUT,
        SECOND_WINDOW_PROMOTION_STATES,
        SECOND_WINDOW_PROMOTION_TABLES,
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
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SECOND_WINDOW_PROMOTION_CERTIFICATE,
        SECOND_WINDOW_PROMOTION_EDGES,
        SECOND_WINDOW_PROMOTION_POINCARE,
        SECOND_WINDOW_PROMOTION_REPORT,
        SECOND_WINDOW_PROMOTION_SPECTRAL_CUT,
        SECOND_WINDOW_PROMOTION_STATES,
        SECOND_WINDOW_PROMOTION_TABLES,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    transfer_operator = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_certificate.json"
    )
    states_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_transfer_states.csv"
    ).read_text(encoding="utf-8")
    edges_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_transfer_edges.csv"
    ).read_text(encoding="utf-8")
    side_flow_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_transfer_side_flow.csv"
    ).read_text(encoding="utf-8")
    centers_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_transfer_centers.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_second_window_transfer_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if transfer_operator != expected["second_window_transfer_operator"]:
        raise AssertionError("second-window transfer JSON is not reproducible")
    if states_csv != expected["second_window_transfer_states_csv"]:
        raise AssertionError("second-window transfer states CSV is not reproducible")
    if edges_csv != expected["second_window_transfer_edges_csv"]:
        raise AssertionError("second-window transfer edges CSV is not reproducible")
    if side_flow_csv != expected["second_window_transfer_side_flow_csv"]:
        raise AssertionError("second-window transfer side-flow CSV is not reproducible")
    if centers_csv != expected["second_window_transfer_centers_csv"]:
        raise AssertionError("second-window transfer centers CSV is not reproducible")
    if observables_csv != expected["second_window_transfer_observables_csv"]:
        raise AssertionError(
            "second-window transfer observables CSV is not reproducible"
        )
    if certificate != expected["second_window_transfer_certificate"]:
        raise AssertionError("second-window transfer certificate is not reproducible")

    for name in [
        "state_table",
        "edge_table",
        "side_table",
        "center_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"second-window transfer table {name} is not reproducible"
            )

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator@1"
    ):
        raise AssertionError("second-window transfer report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("second-window transfer layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("second-window transfer all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("second-window transfer checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window transfer report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("second-window transfer report is not reproducible")

    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    side_table = np.asarray(tables["side_table"], dtype=np.int64)
    center_table = np.asarray(tables["center_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(state_table.shape) != (798, len(TRANSFER_STATE_COLUMNS)):
        raise AssertionError("second-window transfer state table shape mismatch")
    if tuple(edge_table.shape) != (2_523, len(TRANSFER_EDGE_COLUMNS)):
        raise AssertionError("second-window transfer edge table shape mismatch")
    if tuple(side_table.shape) != (2, len(SIDE_FLOW_COLUMNS)):
        raise AssertionError("second-window transfer side table shape mismatch")
    if tuple(center_table.shape) != (6, len(CENTER_COLUMNS)):
        raise AssertionError("second-window transfer center table shape mismatch")
    if tuple(observable_table.shape) != (
        len(TRANSFER_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("second-window transfer observable table shape mismatch")

    state_rows = table_rows(state_table, TRANSFER_STATE_COLUMNS)
    edge_rows = table_rows(edge_table, TRANSFER_EDGE_COLUMNS)
    side_rows = table_rows(side_table, SIDE_FLOW_COLUMNS)
    center_rows = table_rows(center_table, CENTER_COLUMNS)
    observables = {
        row["observable_code"]: row["value_x1e12"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sum(row["stationary_mass_x1e12"] for row in state_rows) != 10**12:
        raise AssertionError("second-window stationary masses do not sum to one")
    if sum(row["undirected_stationary_flux_x1e12"] for row in edge_rows) != 10**12:
        raise AssertionError("second-window edge fluxes do not sum to one")
    if sum(row["weighted_degree"] for row in state_rows) != 11_718:
        raise AssertionError("second-window weighted degree total mismatch")
    if sum(row["edge_weight"] for row in edge_rows) != 5_859:
        raise AssertionError("second-window edge weight total mismatch")
    if sum(row["native_transition_flag"] for row in edge_rows) != 1_668:
        raise AssertionError("second-window native edge count mismatch")
    if sum(row["derived_transition_flag"] for row in edge_rows) != 855:
        raise AssertionError("second-window derived edge count mismatch")
    if sum(row["promoted_transition_flag"] for row in edge_rows) != 481:
        raise AssertionError("second-window promoted-support edge count mismatch")
    if sum(row["promoted_only_transition_flag"] for row in edge_rows) != 22:
        raise AssertionError("second-window promoted-only edge count mismatch")
    if sum(row["spectral_cut_edge_flag"] for row in edge_rows) != 6:
        raise AssertionError("second-window spectral cut edge count mismatch")
    cut_flux = sum(
        row["undirected_stationary_flux_x1e12"]
        for row in edge_rows
        if row["spectral_cut_edge_flag"] == 1
    )
    old_cut_flux = sum(
        row["undirected_stationary_flux_x1e12"]
        for row in edge_rows
        if row["old_spectral_cut_edge_flag"] == 1
    )
    promoted_cut_flux = sum(
        row["undirected_stationary_flux_x1e12"]
        for row in edge_rows
        if row["spectral_cut_edge_flag"] == 1
        and row["promoted_transition_flag"] == 1
    )
    if (cut_flux, old_cut_flux, promoted_cut_flux) != (
        1_024_065_540,
        1_024_065_540,
        1_024_065_540,
    ):
        raise AssertionError("second-window cut flux lineage mismatch")
    side_masses = {
        row["spectral_side_code"]: row["stationary_mass_x1e12"]
        for row in side_rows
    }
    if side_masses != {-1: 118_279_569_876, 1: 881_720_430_124}:
        raise AssertionError("second-window spectral side mass mismatch")
    center = next(row for row in center_rows if row["center_code"] == 0)
    cut_center = next(row for row in center_rows if row["center_code"] == 2)
    promoted_cut_center = next(row for row in center_rows if row["center_code"] == 4)
    if (
        center["center_x_x1e12"],
        center["center_y_x1e12"],
        center["center_radius_x1e12"],
        center["distance_to_cut_center_x1e12"],
        center["distance_to_promoted_cut_center_x1e12"],
        center["distance_to_right_boundary_x1e12"],
    ) != (
        67_572_661_820,
        4_522_140_858,
        67_723_810_000,
        224_107_159_000,
        224_107_159_000,
        119_531_550_000,
    ):
        raise AssertionError("second-window flow center witness mismatch")
    if (
        cut_center["center_x_x1e12"],
        cut_center["center_y_x1e12"],
        cut_center["center_radius_x1e12"],
    ) != (-38_651_644_583, 39_576_416_917, 55_319_458_000):
        raise AssertionError("second-window cut center witness mismatch")
    if (
        promoted_cut_center["center_x_x1e12"],
        promoted_cut_center["center_y_x1e12"],
        promoted_cut_center["center_radius_x1e12"],
    ) != (-38_651_644_583, 39_576_416_917, 55_319_458_000):
        raise AssertionError("second-window promoted cut center witness mismatch")
    boundary = report.get("witness", {}).get("boundary_masses", {})
    if (
        boundary.get("left_mass_x1e12"),
        boundary.get("gate_mass_x1e12"),
        boundary.get("right_mass_x1e12"),
    ) != (2_133_469_876, 768_049_155, 1_621_437_105):
        raise AssertionError("second-window boundary mass witness mismatch")
    if report.get("witness", {}).get("top_stationary_state_id") != 450:
        raise AssertionError("second-window top stationary state mismatch")
    if report.get("witness", {}).get("top_stationary_mass_x1e12") != 7_595_152_757:
        raise AssertionError("second-window top stationary mass mismatch")

    required_observables = {
        "transfer_state_count": 798,
        "transfer_edge_count": 2_523,
        "total_edge_weight": 5_859,
        "total_weighted_degree": 11_718,
        "native_edge_count": 1_668,
        "derived_edge_count": 855,
        "promoted_edge_count": 481,
        "promoted_only_edge_count": 22,
        "native_edge_weight": 5_004,
        "derived_edge_weight": 855,
        "promoted_edge_weight": 1_095,
        "spectral_cut_edge_count": 6,
        "spectral_cut_weight": 6,
        "old_cut_edge_count": 6,
        "old_cut_weight": 6,
        "promoted_cut_edge_count": 6,
        "promoted_cut_weight": 6,
        "top_stationary_state_id": 450,
    }
    for key, value in required_observables.items():
        code = TRANSFER_OBSERVABLE_CODES[key]
        if observables.get(code) != value * 10**12:
            raise AssertionError(f"observable {key} mismatch")

    if certificate.get("status") != STATUS:
        raise AssertionError("second-window transfer certificate status mismatch")
    inputs = report.get("inputs", {})
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
        inputs.get("second_window_promotion_states", {}),
        SECOND_WINDOW_PROMOTION_STATES,
        "second-window promotion states input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_edges", {}),
        SECOND_WINDOW_PROMOTION_EDGES,
        "second-window promotion edges input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_poincare", {}),
        SECOND_WINDOW_PROMOTION_POINCARE,
        "second-window promotion Poincare input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_spectral_cut", {}),
        SECOND_WINDOW_PROMOTION_SPECTRAL_CUT,
        "second-window promotion spectral-cut input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_tables", {}),
        SECOND_WINDOW_PROMOTION_TABLES,
        "second-window promotion tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator_manifest@1"
    ):
        raise AssertionError("second-window transfer manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window transfer manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("second-window transfer manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("second-window transfer missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("second-window transfer index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("second-window transfer index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_second_window_transfer_operator()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
