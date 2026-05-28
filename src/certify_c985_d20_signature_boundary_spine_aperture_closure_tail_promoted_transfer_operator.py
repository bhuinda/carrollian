from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROMOTED_WINDOW_CERTIFICATE,
        PROMOTED_WINDOW_EDGES,
        PROMOTED_WINDOW_POINCARE,
        PROMOTED_WINDOW_REPORT,
        PROMOTED_WINDOW_SPECTRAL_CUT,
        PROMOTED_WINDOW_STATES,
        PROMOTED_WINDOW_TABLES,
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
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PROMOTED_WINDOW_CERTIFICATE,
        PROMOTED_WINDOW_EDGES,
        PROMOTED_WINDOW_POINCARE,
        PROMOTED_WINDOW_REPORT,
        PROMOTED_WINDOW_SPECTRAL_CUT,
        PROMOTED_WINDOW_STATES,
        PROMOTED_WINDOW_TABLES,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    transfer_operator = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator_certificate.json"
    )
    states_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_transfer_states.csv"
    ).read_text(encoding="utf-8")
    edges_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_transfer_edges.csv"
    ).read_text(encoding="utf-8")
    side_flow_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_transfer_side_flow.csv"
    ).read_text(encoding="utf-8")
    centers_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_transfer_centers.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_promoted_transfer_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        transfer_operator
        != expected[
            "signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator"
        ]
    ):
        raise AssertionError("promoted transfer JSON is not reproducible")
    if states_csv != expected["promoted_transfer_states_csv"]:
        raise AssertionError("promoted transfer states CSV is not reproducible")
    if edges_csv != expected["promoted_transfer_edges_csv"]:
        raise AssertionError("promoted transfer edges CSV is not reproducible")
    if side_flow_csv != expected["promoted_transfer_side_flow_csv"]:
        raise AssertionError("promoted transfer side-flow CSV is not reproducible")
    if centers_csv != expected["promoted_transfer_centers_csv"]:
        raise AssertionError("promoted transfer centers CSV is not reproducible")
    if observables_csv != expected["promoted_transfer_observables_csv"]:
        raise AssertionError("promoted transfer observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator_certificate"
        ]
    ):
        raise AssertionError("promoted transfer certificate is not reproducible")

    for name in [
        "state_table",
        "edge_table",
        "side_table",
        "center_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"promoted transfer table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator@1"
    ):
        raise AssertionError("promoted transfer report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("promoted transfer layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("promoted transfer all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("promoted transfer checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("promoted transfer report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("promoted transfer report is not reproducible")

    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    side_table = np.asarray(tables["side_table"], dtype=np.int64)
    center_table = np.asarray(tables["center_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(state_table.shape) != (794, len(TRANSFER_STATE_COLUMNS)):
        raise AssertionError("promoted transfer state table shape mismatch")
    if tuple(edge_table.shape) != (2_513, len(TRANSFER_EDGE_COLUMNS)):
        raise AssertionError("promoted transfer edge table shape mismatch")
    if tuple(side_table.shape) != (2, len(SIDE_FLOW_COLUMNS)):
        raise AssertionError("promoted transfer side table shape mismatch")
    if tuple(center_table.shape) != (6, len(CENTER_COLUMNS)):
        raise AssertionError("promoted transfer center table shape mismatch")
    if tuple(observable_table.shape) != (
        len(TRANSFER_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("promoted transfer observable table shape mismatch")

    state_rows = table_rows(state_table, TRANSFER_STATE_COLUMNS)
    edge_rows = table_rows(edge_table, TRANSFER_EDGE_COLUMNS)
    side_rows = table_rows(side_table, SIDE_FLOW_COLUMNS)
    center_rows = table_rows(center_table, CENTER_COLUMNS)
    observables = {
        row["observable_code"]: row["value_x1e12"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sum(row["stationary_mass_x1e12"] for row in state_rows) != 10**12:
        raise AssertionError("promoted transfer stationary masses do not sum to one")
    if sum(row["undirected_stationary_flux_x1e12"] for row in edge_rows) != 10**12:
        raise AssertionError("promoted transfer edge fluxes do not sum to one")
    if sum(row["weighted_degree"] for row in state_rows) != 11_698:
        raise AssertionError("promoted weighted degree total mismatch")
    if sum(row["edge_weight"] for row in edge_rows) != 5_849:
        raise AssertionError("promoted edge weight total mismatch")
    if sum(row["native_transition_flag"] for row in edge_rows) != 1_668:
        raise AssertionError("promoted native edge count mismatch")
    if sum(row["derived_transition_flag"] for row in edge_rows) != 845:
        raise AssertionError("promoted derived edge count mismatch")
    if sum(row["promoted_transition_flag"] for row in edge_rows) != 308:
        raise AssertionError("promoted-support edge count mismatch")
    if sum(row["promoted_only_transition_flag"] for row in edge_rows) != 12:
        raise AssertionError("promoted-only edge count mismatch")
    if sum(row["spectral_cut_edge_flag"] for row in edge_rows) != 6:
        raise AssertionError("promoted spectral cut edge count mismatch")
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
        1_025_816_382,
        1_025_816_382,
        854_846_985,
    ):
        raise AssertionError("promoted cut flux lineage mismatch")
    side_masses = {
        row["spectral_side_code"]: row["stationary_mass_x1e12"]
        for row in side_rows
    }
    if side_masses != {-1: 116_772_097_781, 1: 883_227_902_219}:
        raise AssertionError("promoted spectral side mass mismatch")
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
        60_312_974_186,
        1_858_169_836,
        60_341_591_000,
        196_518_833_000,
        205_642_834_000,
        97_993_795_000,
    ):
        raise AssertionError("promoted flow center witness mismatch")
    if (
        cut_center["center_x_x1e12"],
        cut_center["center_y_x1e12"],
        cut_center["center_radius_x1e12"],
    ) != (-24_633_024_750, 50_889_647_250, 56_537_970_000):
        raise AssertionError("promoted cut center witness mismatch")
    if (
        promoted_cut_center["center_x_x1e12"],
        promoted_cut_center["center_y_x1e12"],
        promoted_cut_center["center_radius_x1e12"],
    ) != (-32_092_090_000, 46_561_889_300, 56_550_082_000):
        raise AssertionError("promoted cut subcenter witness mismatch")
    boundary = report.get("witness", {}).get("boundary_masses", {})
    if (
        boundary.get("left_mass_x1e12"),
        boundary.get("gate_mass_x1e12"),
        boundary.get("right_mass_x1e12"),
    ) != (2_137_117_456, 769_362_284, 1_624_209_267):
        raise AssertionError("promoted boundary mass witness mismatch")
    if report.get("witness", {}).get("top_stationary_state_id") != 446:
        raise AssertionError("promoted top stationary state mismatch")
    if report.get("witness", {}).get("top_stationary_mass_x1e12") != 7_608_138_143:
        raise AssertionError("promoted top stationary mass mismatch")

    required_observables = {
        "transfer_state_count": 794,
        "transfer_edge_count": 2_513,
        "total_edge_weight": 5_849,
        "total_weighted_degree": 11_698,
        "native_edge_count": 1_668,
        "derived_edge_count": 845,
        "promoted_edge_count": 308,
        "promoted_only_edge_count": 12,
        "native_edge_weight": 5_004,
        "derived_edge_weight": 845,
        "promoted_edge_weight": 704,
        "spectral_cut_edge_count": 6,
        "spectral_cut_weight": 6,
        "old_cut_edge_count": 6,
        "old_cut_weight": 6,
        "promoted_cut_edge_count": 5,
        "promoted_cut_weight": 5,
        "top_stationary_state_id": 446,
    }
    for key, value in required_observables.items():
        code = TRANSFER_OBSERVABLE_CODES[key]
        if observables.get(code) != value * 10**12:
            raise AssertionError(f"observable {key} mismatch")

    if certificate.get("status") != STATUS:
        raise AssertionError("promoted transfer certificate status mismatch")
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
        inputs.get("promoted_window_states", {}),
        PROMOTED_WINDOW_STATES,
        "promoted window states input",
    )
    assert_file_hash(
        inputs.get("promoted_window_edges", {}),
        PROMOTED_WINDOW_EDGES,
        "promoted window edges input",
    )
    assert_file_hash(
        inputs.get("promoted_window_poincare", {}),
        PROMOTED_WINDOW_POINCARE,
        "promoted window Poincare input",
    )
    assert_file_hash(
        inputs.get("promoted_window_spectral_cut", {}),
        PROMOTED_WINDOW_SPECTRAL_CUT,
        "promoted window spectral-cut input",
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
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator_manifest@1"
    ):
        raise AssertionError("promoted transfer manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("promoted transfer manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("promoted transfer manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("promoted transfer missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("promoted transfer index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("promoted transfer index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_promoted_transfer_operator()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
