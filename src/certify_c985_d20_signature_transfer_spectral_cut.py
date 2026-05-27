from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_transfer_spectral_cut import (
        ATOM_EIGENMODE_COLUMNS,
        ATOM_FLOW_CERTIFICATE,
        ATOM_FLOW_JSON,
        ATOM_FLOW_NODE_CONTRIBUTIONS,
        ATOM_FLOW_REPORT,
        ATOM_FLOW_TABLES,
        BASIN_EIGENMODE_COLUMNS,
        EIGENMODE_CUT_EDGE_COLUMNS,
        EIGENMODE_OBSERVABLE_COLUMNS,
        EIGENMODE_VERTEX_COLUMNS,
        INDEX_PATH,
        MASK_EIGENMODE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SIGNATURE_TRANSFER_CERTIFICATE,
        SIGNATURE_TRANSFER_JSON,
        SIGNATURE_TRANSFER_REPORT,
        SIGNATURE_TRANSFER_TABLES,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_transfer_spectral_cut import (
        ATOM_EIGENMODE_COLUMNS,
        ATOM_FLOW_CERTIFICATE,
        ATOM_FLOW_JSON,
        ATOM_FLOW_NODE_CONTRIBUTIONS,
        ATOM_FLOW_REPORT,
        ATOM_FLOW_TABLES,
        BASIN_EIGENMODE_COLUMNS,
        EIGENMODE_CUT_EDGE_COLUMNS,
        EIGENMODE_OBSERVABLE_COLUMNS,
        EIGENMODE_VERTEX_COLUMNS,
        INDEX_PATH,
        MASK_EIGENMODE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SIGNATURE_TRANSFER_CERTIFICATE,
        SIGNATURE_TRANSFER_JSON,
        SIGNATURE_TRANSFER_REPORT,
        SIGNATURE_TRANSFER_TABLES,
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


def validate_c985_d20_signature_transfer_spectral_cut() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    spectral_cut = load_json(OUT_DIR / "signature_transfer_spectral_cut.json")
    certificate = load_json(OUT_DIR / "signature_transfer_spectral_cut_certificate.json")
    vertex_csv = (OUT_DIR / "signature_eigenmode_vertices.csv").read_text(
        encoding="utf-8"
    )
    cut_csv = (OUT_DIR / "signature_eigenmode_cut_edges.csv").read_text(
        encoding="utf-8"
    )
    mask_csv = (OUT_DIR / "carrier_mask_eigenmode_summary.csv").read_text(
        encoding="utf-8"
    )
    atom_csv = (OUT_DIR / "atom_eigenmode_summary.csv").read_text(encoding="utf-8")
    basin_csv = (OUT_DIR / "core_basin_eigenmode_summary.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "signature_transfer_spectral_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_transfer_spectral_cut_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if spectral_cut != expected["signature_transfer_spectral_cut"]:
        raise AssertionError("signature transfer spectral cut JSON is not reproducible")
    if vertex_csv != expected["signature_eigenmode_vertices_csv"]:
        raise AssertionError("signature eigenmode vertex CSV is not reproducible")
    if cut_csv != expected["signature_eigenmode_cut_edges_csv"]:
        raise AssertionError("signature eigenmode cut CSV is not reproducible")
    if mask_csv != expected["carrier_mask_eigenmode_summary_csv"]:
        raise AssertionError("carrier-mask eigenmode CSV is not reproducible")
    if atom_csv != expected["atom_eigenmode_summary_csv"]:
        raise AssertionError("atom eigenmode CSV is not reproducible")
    if basin_csv != expected["core_basin_eigenmode_summary_csv"]:
        raise AssertionError("core-basin eigenmode CSV is not reproducible")
    if observable_csv != expected["signature_transfer_spectral_observables_csv"]:
        raise AssertionError("signature spectral observable CSV is not reproducible")
    if certificate != expected["signature_transfer_spectral_cut_certificate"]:
        raise AssertionError("signature transfer spectral cut certificate is not reproducible")

    table_names = [
        "eigenmode_vertex_table",
        "eigenmode_cut_edge_table",
        "mask_eigenmode_table",
        "atom_eigenmode_table",
        "basin_eigenmode_table",
        "eigenmode_observable_table",
        "second_eigenfunction_x1e12",
        "nodal_signs",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature spectral cut table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_transfer_spectral_cut@1":
        raise AssertionError("C985 d20 signature spectral cut report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature spectral cut is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature spectral cut all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature spectral cut checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature spectral cut report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature spectral cut report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "signature_transfer_report_certified",
        "signature_transfer_certificate_certified",
        "signature_subboundary_report_certified",
        "signature_subboundary_certificate_certified",
        "atom_flow_report_certified",
        "atom_flow_certificate_certified",
        "lambda_2_matches_transfer_second_modulus",
        "lambda_2_matches_expected",
        "lambda_3_matches_expected",
        "lambda_2_minus_lambda_3_matches_expected",
        "spectral_gap_matches_transfer",
        "lambda_min_matches_expected",
        "eigen_residual_is_zero_at_x1e12",
        "stationary_orthogonality_is_zero_at_x1e12",
        "stationary_norm_residual_is_zero_at_x1e12",
        "positive_vertex_count_is_121",
        "negative_vertex_count_is_100",
        "positive_stationary_mass_matches_expected",
        "negative_stationary_mass_matches_expected",
        "cut_edge_count_is_4007",
        "within_edge_counts_match_expected",
        "cut_flux_matches_expected",
        "one_way_cut_flux_matches_expected",
        "cut_conductance_matches_expected",
        "all_mask_classes_are_pure_sign",
        "positive_mask_classes_match_expected",
        "negative_mask_classes_match_expected",
        "mask_cut_edges_match_expected",
        "mask_within_edges_match_expected",
        "top_positive_atom_is_7",
        "top_negative_atom_is_12",
        "atom_7_is_pure_positive",
        "atom_12_is_pure_negative",
        "basin_positive_fractions_match_expected",
        "vertex_table_shape_is_221_by_10",
        "cut_edge_table_shape_is_4007_by_12",
        "mask_table_shape_is_14_by_16",
        "atom_table_shape_is_6_by_7",
        "basin_table_shape_is_3_by_7",
        "observable_table_shape_matches_codebook",
        "second_eigenfunction_shape_is_221",
        "nodal_sign_shape_is_221",
        "transfer_json_schema_available",
        "subboundary_json_schema_available",
        "atom_flow_json_schema_available",
        "atom_flow_signature_table_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 signature spectral cut missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("lambda_2_x1e12") != 587252536214:
        raise AssertionError("signature spectral cut lambda_2 mismatch")
    if witness.get("lambda_3_x1e12") != 348829795192:
        raise AssertionError("signature spectral cut lambda_3 mismatch")
    if witness.get("lambda_2_minus_lambda_3_x1e12") != 238422741021:
        raise AssertionError("signature spectral cut eigen gap mismatch")
    if witness.get("spectral_gap_x1e12") != 412747463786:
        raise AssertionError("signature spectral cut transfer gap mismatch")
    if witness.get("lambda_min_x1e12") != -23107307402:
        raise AssertionError("signature spectral cut lambda min mismatch")
    if witness.get("positive_vertex_count") != 121 or witness.get("negative_vertex_count") != 100:
        raise AssertionError("signature spectral cut vertex counts mismatch")
    if witness.get("positive_stationary_mass_x1e12") != 626107108209:
        raise AssertionError("signature spectral cut positive mass mismatch")
    if witness.get("negative_stationary_mass_x1e12") != 373892891791:
        raise AssertionError("signature spectral cut negative mass mismatch")
    if witness.get("cut_edge_count") != 4007:
        raise AssertionError("signature spectral cut edge count mismatch")
    if witness.get("within_positive_edge_count") != 5968:
        raise AssertionError("signature spectral cut positive edge count mismatch")
    if witness.get("within_negative_edge_count") != 3060:
        raise AssertionError("signature spectral cut negative edge count mismatch")
    if witness.get("undirected_cut_flux_x1e12") != 238962451389:
        raise AssertionError("signature spectral cut flux mismatch")
    if witness.get("one_way_cut_flux_x1e12") != 119481225694:
        raise AssertionError("signature spectral cut one-way flux mismatch")
    if witness.get("cut_conductance_x1e12") != 319560035288:
        raise AssertionError("signature spectral cut conductance mismatch")
    if witness.get("positive_mask_class_ids") != [0, 1, 2, 3, 10, 11, 12]:
        raise AssertionError("signature spectral cut positive mask classes mismatch")
    if witness.get("negative_mask_class_ids") != [4, 5, 6, 7, 8, 9, 13]:
        raise AssertionError("signature spectral cut negative mask classes mismatch")
    if witness.get("mask_cut_edge_count") != 16:
        raise AssertionError("signature spectral cut mask edge count mismatch")
    if witness.get("top_positive_atom_id") != 7:
        raise AssertionError("signature spectral cut top positive atom mismatch")
    if witness.get("top_negative_atom_id") != 12:
        raise AssertionError("signature spectral cut top negative atom mismatch")
    if witness.get("basin_positive_fraction_x1e12") != {
        "10": 684970520566,
        "43": 624064619314,
        "0": 598273462377,
    }:
        raise AssertionError("signature spectral cut basin fractions mismatch")

    vertex_table = np.asarray(tables["eigenmode_vertex_table"], dtype=np.int64)
    cut_table = np.asarray(tables["eigenmode_cut_edge_table"], dtype=np.int64)
    mask_table = np.asarray(tables["mask_eigenmode_table"], dtype=np.int64)
    atom_table = np.asarray(tables["atom_eigenmode_table"], dtype=np.int64)
    basin_table = np.asarray(tables["basin_eigenmode_table"], dtype=np.int64)
    observable_table = np.asarray(tables["eigenmode_observable_table"], dtype=np.int64)
    eigenfunction = np.asarray(tables["second_eigenfunction_x1e12"], dtype=np.int64)
    signs = np.asarray(tables["nodal_signs"], dtype=np.int64)

    if vertex_table.shape != (221, len(EIGENMODE_VERTEX_COLUMNS)):
        raise AssertionError("signature spectral vertex table shape mismatch")
    if cut_table.shape != (4007, len(EIGENMODE_CUT_EDGE_COLUMNS)):
        raise AssertionError("signature spectral cut edge table shape mismatch")
    if mask_table.shape != (14, len(MASK_EIGENMODE_COLUMNS)):
        raise AssertionError("signature spectral mask table shape mismatch")
    if atom_table.shape != (6, len(ATOM_EIGENMODE_COLUMNS)):
        raise AssertionError("signature spectral atom table shape mismatch")
    if basin_table.shape != (3, len(BASIN_EIGENMODE_COLUMNS)):
        raise AssertionError("signature spectral basin table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(EIGENMODE_OBSERVABLE_COLUMNS)):
        raise AssertionError("signature spectral observable table shape mismatch")
    if eigenfunction.shape != (221,):
        raise AssertionError("signature spectral eigenfunction shape mismatch")
    if signs.shape != (221,):
        raise AssertionError("signature spectral signs shape mismatch")
    if int(np.count_nonzero(signs == 1)) != 121 or int(np.count_nonzero(signs == -1)) != 100:
        raise AssertionError("signature spectral sign vector count mismatch")
    if not np.all(mask_table[:, 2] != 0):
        raise AssertionError("signature spectral mask signs are not pure")
    if int(cut_table[:, 9].sum()) != 238962451389:
        raise AssertionError("signature spectral cut flux table sum mismatch")
    if int(atom_table[:, 1].sum()) != 1_000_000_000_000:
        raise AssertionError("signature spectral atom table mass sum mismatch")
    if int(basin_table[:, 1].sum()) != 1_000_000_000_000:
        raise AssertionError("signature spectral basin table mass sum mismatch")

    inputs = report.get("inputs", {})
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
        inputs.get("signature_subboundary_report", {}),
        SIGNATURE_SUBBOUNDARY_REPORT,
        "signature subboundary report input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary", {}),
        SIGNATURE_SUBBOUNDARY_JSON,
        "signature subboundary JSON input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary_tables", {}),
        SIGNATURE_SUBBOUNDARY_TABLES,
        "signature subboundary tables input",
    )
    assert_file_hash(
        inputs.get("signature_subboundary_certificate", {}),
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        "signature subboundary certificate input",
    )
    assert_file_hash(inputs.get("atom_flow_report", {}), ATOM_FLOW_REPORT, "atom-flow report input")
    assert_file_hash(inputs.get("atom_flow", {}), ATOM_FLOW_JSON, "atom-flow JSON input")
    assert_file_hash(inputs.get("atom_flow_tables", {}), ATOM_FLOW_TABLES, "atom-flow tables input")
    assert_file_hash(
        inputs.get("atom_flow_certificate", {}),
        ATOM_FLOW_CERTIFICATE,
        "atom-flow certificate input",
    )
    assert_file_hash(
        inputs.get("atom_flow_node_contributions", {}),
        ATOM_FLOW_NODE_CONTRIBUTIONS,
        "atom-flow contribution input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_transfer_spectral_cut_manifest@1":
        raise AssertionError("C985 d20 signature spectral cut manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature spectral cut manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature spectral cut manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature spectral cut missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature spectral cut index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature spectral cut index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_transfer_spectral_cut@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "lambda_2_x1e12": witness.get("lambda_2_x1e12"),
        "lambda_3_x1e12": witness.get("lambda_3_x1e12"),
        "positive_vertex_count": witness.get("positive_vertex_count"),
        "negative_vertex_count": witness.get("negative_vertex_count"),
        "cut_edge_count": witness.get("cut_edge_count"),
        "positive_mask_class_ids": witness.get("positive_mask_class_ids"),
        "negative_mask_class_ids": witness.get("negative_mask_class_ids"),
        "top_positive_atom_id": witness.get("top_positive_atom_id"),
        "top_negative_atom_id": witness.get("top_negative_atom_id"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_transfer_spectral_cut()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
