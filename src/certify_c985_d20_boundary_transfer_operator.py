from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_boundary_transfer_operator import (
        FLOW_OBSERVABLE_COLUMNS,
        MORSE_REEB_CERTIFICATE,
        MORSE_REEB_JSON,
        MORSE_REEB_PATHS_CSV,
        MORSE_REEB_REPORT,
        MORSE_REEB_TABLES,
        OUT_DIR,
        POINCARE_CERTIFICATE,
        POINCARE_JSON,
        POINCARE_REPORT,
        POINCARE_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        SOURCE_SINK_PATH_WEIGHT_COLUMNS,
        STATIONARY_DISTRIBUTION_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSFER_EDGE_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_boundary_transfer_operator import (
        FLOW_OBSERVABLE_COLUMNS,
        MORSE_REEB_CERTIFICATE,
        MORSE_REEB_JSON,
        MORSE_REEB_PATHS_CSV,
        MORSE_REEB_REPORT,
        MORSE_REEB_TABLES,
        OUT_DIR,
        POINCARE_CERTIFICATE,
        POINCARE_JSON,
        POINCARE_REPORT,
        POINCARE_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        SOURCE_SINK_PATH_WEIGHT_COLUMNS,
        STATIONARY_DISTRIBUTION_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSFER_EDGE_COLUMNS,
        build_payloads,
        self_hash,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH


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


def validate_c985_d20_boundary_transfer_operator() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    boundary_transfer = load_json(OUT_DIR / "boundary_transfer_operator.json")
    certificate = load_json(OUT_DIR / "boundary_transfer_certificate.json")
    path_weights_csv = (OUT_DIR / "source_sink_path_weights.csv").read_text(
        encoding="utf-8"
    )
    transfer_edges_csv = (OUT_DIR / "core_transfer_edges.csv").read_text(encoding="utf-8")
    stationary_csv = (OUT_DIR / "stationary_distribution.csv").read_text(encoding="utf-8")
    observables_csv = (OUT_DIR / "boundary_flow_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(OUT_DIR / "boundary_transfer_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if boundary_transfer != expected["boundary_transfer_operator"]:
        raise AssertionError("d20 boundary transfer JSON is not reproducible")
    if path_weights_csv != expected["source_sink_path_weights_csv"]:
        raise AssertionError("d20 boundary transfer path weights CSV is not reproducible")
    if transfer_edges_csv != expected["core_transfer_edges_csv"]:
        raise AssertionError("d20 boundary transfer edges CSV is not reproducible")
    if stationary_csv != expected["stationary_distribution_csv"]:
        raise AssertionError("d20 boundary transfer stationary CSV is not reproducible")
    if observables_csv != expected["boundary_flow_observables_csv"]:
        raise AssertionError("d20 boundary transfer observables CSV is not reproducible")
    if certificate != expected["boundary_transfer_certificate"]:
        raise AssertionError("d20 boundary transfer certificate is not reproducible")

    table_names = [
        "path_weight_table",
        "transfer_edge_table",
        "stationary_distribution_table",
        "flow_observable_table",
        "transition_matrix",
        "transition_matrix_x1e12",
        "edge_flux_matrix",
        "stationary_distribution",
        "stationary_distribution_x1e12",
        "transition_support",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"d20 boundary transfer table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_boundary_transfer_operator@1":
        raise AssertionError("C985 d20 boundary transfer report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary transfer operator is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary transfer all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary transfer checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary transfer report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary transfer report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "poincare_report_certified",
        "poincare_certificate_certified",
        "morse_reeb_report_certified",
        "morse_reeb_certificate_certified",
        "source_sink_path_count_is_42",
        "source_path_counts_are_10_and_32",
        "path_weight_table_shape_is_42_by_17",
        "transfer_matrix_shape_is_12_by_12",
        "transfer_row_sums_are_stochastic",
        "transfer_edge_count_is_33",
        "flow_edge_count_is_31",
        "return_edge_count_is_2",
        "return_probabilities_match",
        "support_is_strongly_connected",
        "recurrent_support_is_all_12_core_nodes",
        "stationary_distribution_sums_to_one",
        "stationary_max_node_is_44",
        "stationary_min_node_is_32",
        "stationary_vector_matches_expected",
        "stationary_basin_masses_match_expected",
        "spectral_gap_matches_expected",
        "path_entropy_perplexity_is_broad",
        "weighted_poincare_center_matches_expected",
        "weighted_center_radius_below_uniform_mean_radius",
        "stationary_mean_radius_above_uniform_mean_radius",
        "stationary_negative_radius_correlation_is_negative",
        "transfer_edge_table_shape_is_33_by_9",
        "stationary_distribution_table_shape_is_12_by_9",
        "observable_table_shape_matches_codebook",
        "morse_reeb_tables_available",
        "poincare_tables_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary transfer missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("source_sink_path_count") != 42:
        raise AssertionError("boundary transfer source-sink path count mismatch")
    if witness.get("source_path_count") != {"10": 10, "43": 32}:
        raise AssertionError("boundary transfer source path counts mismatch")
    if witness.get("transfer_edge_count") != 33:
        raise AssertionError("boundary transfer edge count mismatch")
    if witness.get("flow_edge_count") != 31 or witness.get("return_edge_count") != 2:
        raise AssertionError("boundary transfer edge-kind count mismatch")
    if witness.get("return_probabilities_x1e12") != {"10": 283062070620, "43": 716937929380}:
        raise AssertionError("boundary transfer return probabilities mismatch")
    if witness.get("support_strongly_connected") is not True:
        raise AssertionError("boundary transfer support is not strongly connected")
    if witness.get("recurrent_support_node_count") != 12:
        raise AssertionError("boundary transfer recurrent support mismatch")
    if witness.get("stationary_mass_sum_x1e12") != 1_000_000_000_000:
        raise AssertionError("boundary transfer stationary mass sum mismatch")
    if witness.get("stationary_max_node_id") != 44:
        raise AssertionError("boundary transfer stationary max node mismatch")
    if witness.get("stationary_min_node_id") != 32:
        raise AssertionError("boundary transfer stationary min node mismatch")
    if witness.get("stationary_distribution_x1e12") != {
        "10": 60964383817,
        "13": 91448650143,
        "17": 33776644764,
        "19": 45863301091,
        "28": 79786909943,
        "32": 26617242245,
        "34": 88173593812,
        "38": 83222089120,
        "41": 79481608761,
        "42": 40880734813,
        "43": 154410228837,
        "44": 215374612654,
    }:
        raise AssertionError("boundary transfer stationary distribution mismatch")
    if witness.get("stationary_basin_masses_x1e12") != {
        "10": 121358270826,
        "43": 488349486805,
        "boundary": 390292242370,
    }:
        raise AssertionError("boundary transfer basin mass mismatch")
    if witness.get("spectral_gap_x1e12") != 173671525179:
        raise AssertionError("boundary transfer spectral gap mismatch")
    geometry = witness.get("geometric_observables", {})
    center = geometry.get("weighted_poincare_center", {})
    if center.get("radius_x1e12") != 50308637915:
        raise AssertionError("boundary transfer weighted center radius mismatch")
    if center.get("x_x1e12") != -50213137809 or center.get("y_x1e12") != -3098360902:
        raise AssertionError("boundary transfer weighted center coordinate mismatch")
    if geometry.get("stationary_negative_radius_correlation_x1e12", 0) >= 0:
        raise AssertionError("boundary transfer negative radius correlation sign mismatch")

    path_weight_table = np.asarray(tables["path_weight_table"], dtype=np.int64)
    transfer_edge_table = np.asarray(tables["transfer_edge_table"], dtype=np.int64)
    stationary_table = np.asarray(tables["stationary_distribution_table"], dtype=np.int64)
    observable_table = np.asarray(tables["flow_observable_table"], dtype=np.int64)
    transition_matrix = np.asarray(tables["transition_matrix"], dtype=np.float64)
    transition_support = np.asarray(tables["transition_support"], dtype=np.int8)
    stationary = np.asarray(tables["stationary_distribution"], dtype=np.float64)
    stationary_x1e12 = np.asarray(tables["stationary_distribution_x1e12"], dtype=np.int64)

    if path_weight_table.shape != (42, len(SOURCE_SINK_PATH_WEIGHT_COLUMNS)):
        raise AssertionError("boundary transfer path weight table shape mismatch")
    if transfer_edge_table.shape != (33, len(TRANSFER_EDGE_COLUMNS)):
        raise AssertionError("boundary transfer edge table shape mismatch")
    if stationary_table.shape != (12, len(STATIONARY_DISTRIBUTION_COLUMNS)):
        raise AssertionError("boundary transfer stationary table shape mismatch")
    if observable_table.shape != (19, len(FLOW_OBSERVABLE_COLUMNS)):
        raise AssertionError("boundary transfer observable table shape mismatch")
    if transition_matrix.shape != (12, 12):
        raise AssertionError("boundary transfer matrix shape mismatch")
    if float(np.max(np.abs(np.sum(transition_matrix, axis=1) - 1.0))) > 1e-12:
        raise AssertionError("boundary transfer matrix is not row stochastic")
    if transition_support.shape != (12, 12) or int(np.sum(transition_support)) != 33:
        raise AssertionError("boundary transfer support mismatch")
    if stationary.shape != (12,) or abs(float(np.sum(stationary)) - 1.0) > 1e-12:
        raise AssertionError("boundary transfer stationary vector mismatch")
    if int(np.sum(stationary_x1e12)) != 1_000_000_000_000:
        raise AssertionError("boundary transfer stationary scaled vector mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("rewrite_complex_report", {}),
        REWRITE_COMPLEX_REPORT,
        "rewrite complex report input",
    )
    assert_file_hash(inputs.get("rewrite_complex", {}), REWRITE_COMPLEX_JSON, "rewrite complex input")
    assert_file_hash(
        inputs.get("rewrite_complex_certificate", {}),
        REWRITE_COMPLEX_CERTIFICATE,
        "rewrite complex certificate input",
    )
    assert_file_hash(inputs.get("poincare_report", {}), POINCARE_REPORT, "Poincare report input")
    assert_file_hash(inputs.get("poincare_embedding", {}), POINCARE_JSON, "Poincare input")
    assert_file_hash(inputs.get("poincare_tables", {}), POINCARE_TABLES, "Poincare tables input")
    assert_file_hash(
        inputs.get("poincare_certificate", {}),
        POINCARE_CERTIFICATE,
        "Poincare certificate input",
    )
    assert_file_hash(
        inputs.get("morse_reeb_report", {}),
        MORSE_REEB_REPORT,
        "Morse/Reeb report input",
    )
    assert_file_hash(inputs.get("morse_reeb", {}), MORSE_REEB_JSON, "Morse/Reeb input")
    assert_file_hash(
        inputs.get("morse_reeb_tables", {}),
        MORSE_REEB_TABLES,
        "Morse/Reeb tables input",
    )
    assert_file_hash(
        inputs.get("morse_reeb_certificate", {}),
        MORSE_REEB_CERTIFICATE,
        "Morse/Reeb certificate input",
    )
    assert_file_hash(
        inputs.get("morse_reeb_directed_paths_csv", {}),
        MORSE_REEB_PATHS_CSV,
        "Morse/Reeb directed paths CSV input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_boundary_transfer_operator_manifest@1":
        raise AssertionError("C985 d20 boundary transfer manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary transfer manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary transfer manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 boundary transfer missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary transfer index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary transfer index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_boundary_transfer_operator@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "source_sink_path_count": witness.get("source_sink_path_count"),
        "transfer_edge_count": witness.get("transfer_edge_count"),
        "recurrent_support_node_count": witness.get("recurrent_support_node_count"),
        "stationary_max_node_id": witness.get("stationary_max_node_id"),
        "stationary_basin_masses_x1e12": witness.get("stationary_basin_masses_x1e12"),
        "spectral_gap_x1e12": witness.get("spectral_gap_x1e12"),
        "weighted_poincare_center": center,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_boundary_transfer_operator()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
