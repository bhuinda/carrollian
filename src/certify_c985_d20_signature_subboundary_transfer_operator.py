from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_subboundary_transfer_operator import (
        ATOM_STATIONARY_COLUMNS,
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        INDEX_PATH,
        MASK_STATIONARY_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SIGNATURE_STATIONARY_COLUMNS,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SIGNATURE_TRANSFER_EDGE_COLUMNS,
        SIGNATURE_TRANSFER_OBSERVABLE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_subboundary_transfer_operator import (
        ATOM_STATIONARY_COLUMNS,
        BOUNDARY_TRANSFER_CERTIFICATE,
        BOUNDARY_TRANSFER_JSON,
        BOUNDARY_TRANSFER_REPORT,
        BOUNDARY_TRANSFER_TABLES,
        INDEX_PATH,
        MASK_STATIONARY_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SIGNATURE_STATIONARY_COLUMNS,
        SIGNATURE_SUBBOUNDARY_CERTIFICATE,
        SIGNATURE_SUBBOUNDARY_JSON,
        SIGNATURE_SUBBOUNDARY_REPORT,
        SIGNATURE_SUBBOUNDARY_TABLES,
        SIGNATURE_TRANSFER_EDGE_COLUMNS,
        SIGNATURE_TRANSFER_OBSERVABLE_COLUMNS,
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


def validate_c985_d20_signature_subboundary_transfer_operator() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    transfer = load_json(OUT_DIR / "signature_transfer_operator.json")
    certificate = load_json(OUT_DIR / "signature_transfer_certificate.json")
    edges_csv = (OUT_DIR / "signature_transfer_edges.csv").read_text(encoding="utf-8")
    stationary_csv = (OUT_DIR / "signature_stationary_distribution.csv").read_text(
        encoding="utf-8"
    )
    mask_csv = (OUT_DIR / "signature_mask_stationary.csv").read_text(encoding="utf-8")
    atom_csv = (OUT_DIR / "signature_atom_stationary.csv").read_text(encoding="utf-8")
    observable_csv = (OUT_DIR / "signature_transfer_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(OUT_DIR / "signature_transfer_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if transfer != expected["signature_transfer_operator"]:
        raise AssertionError("signature transfer operator JSON is not reproducible")
    if edges_csv != expected["signature_transfer_edges_csv"]:
        raise AssertionError("signature transfer edge CSV is not reproducible")
    if stationary_csv != expected["signature_stationary_distribution_csv"]:
        raise AssertionError("signature stationary CSV is not reproducible")
    if mask_csv != expected["signature_mask_stationary_csv"]:
        raise AssertionError("signature mask stationary CSV is not reproducible")
    if atom_csv != expected["signature_atom_stationary_csv"]:
        raise AssertionError("signature atom stationary CSV is not reproducible")
    if observable_csv != expected["signature_transfer_observables_csv"]:
        raise AssertionError("signature transfer observable CSV is not reproducible")
    if certificate != expected["signature_transfer_certificate"]:
        raise AssertionError("signature transfer certificate is not reproducible")

    table_names = [
        "signature_transfer_edge_table",
        "signature_stationary_table",
        "signature_mask_stationary_table",
        "signature_atom_stationary_table",
        "signature_transfer_observable_table",
        "signature_transfer_matrix_x1e12",
        "symmetric_similarity_spectrum_x1e12",
        "signature_stationary_distribution_x1e12",
        "signature_shared_active_atom_matrix",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature transfer table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_subboundary_transfer_operator@1":
        raise AssertionError("C985 d20 signature transfer report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature transfer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature transfer all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature transfer checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature transfer report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature transfer report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "signature_subboundary_report_certified",
        "signature_subboundary_certificate_certified",
        "boundary_transfer_report_certified",
        "boundary_transfer_certificate_certified",
        "active_signature_count_is_221",
        "transfer_edge_count_is_13035",
        "support_matches_subboundary_adjacency",
        "support_is_connected",
        "transition_matrix_shape_is_221_by_221",
        "transition_rows_sum_to_one_x1e12",
        "stationary_distribution_sums_to_one_x1e12",
        "stationary_residual_is_zero_at_x1e12",
        "row_sum_residual_is_zero_at_x1e12",
        "spectral_gap_matches_expected",
        "spectral_second_modulus_matches_expected",
        "spectral_gap_exceeds_core_gap",
        "spectral_gap_delta_matches_expected",
        "spectral_gap_ratio_matches_expected",
        "top_stationary_signatures_are_106_to_115",
        "top_stationary_signature_mass_matches_expected",
        "top_mask_class_is_11",
        "top_mask_stationary_mass_matches_expected",
        "top_atom_is_19",
        "top_atom_stationary_mass_matches_expected",
        "stationary_flow_total_variation_matches_expected",
        "stationary_flow_correlation_matches_expected",
        "transition_probability_range_matches_expected",
        "undirected_flux_range_matches_expected",
        "signature_stationary_table_shape_is_221_by_11",
        "signature_transfer_edge_table_shape_is_13035_by_11",
        "mask_stationary_table_shape_is_14_by_13",
        "atom_stationary_table_shape_is_6_by_7",
        "observable_table_shape_matches_codebook",
        "spectrum_shape_is_221",
        "subboundary_json_schema_available",
        "boundary_transfer_json_schema_available",
        "boundary_transfer_tables_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 signature transfer missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("active_signature_class_count") != 221:
        raise AssertionError("signature transfer active signature count mismatch")
    if witness.get("transfer_edge_count") != 13035:
        raise AssertionError("signature transfer edge count mismatch")
    if witness.get("stationary_mass_sum_x1e12") != 1_000_000_000_000:
        raise AssertionError("signature transfer stationary mass sum mismatch")
    if witness.get("top_stationary_signature_class_ids") != [
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
    ]:
        raise AssertionError("signature transfer top stationary signatures mismatch")
    if witness.get("top_stationary_signature_mass_x1e12") != 11783387736:
        raise AssertionError("signature transfer top stationary mass mismatch")
    if witness.get("minimum_stationary_mass_x1e12") != 333457905:
        raise AssertionError("signature transfer minimum stationary mass mismatch")
    if witness.get("top_mask_class_ids") != [11]:
        raise AssertionError("signature transfer top mask class mismatch")
    if witness.get("top_mask_stationary_mass_x1e12") != 235667754700:
        raise AssertionError("signature transfer top mask mass mismatch")
    if witness.get("top_atom_ids") != [19]:
        raise AssertionError("signature transfer top atom mismatch")
    if witness.get("top_atom_stationary_mass_x1e12") != 215486440125:
        raise AssertionError("signature transfer top atom mass mismatch")
    if witness.get("stationary_atom_order") != [19, 7, 12, 1, 4, 11]:
        raise AssertionError("signature transfer atom order mismatch")
    if witness.get("spectral_gap_x1e12") != 412747463786:
        raise AssertionError("signature transfer spectral gap mismatch")
    if witness.get("spectral_second_modulus_x1e12") != 587252536214:
        raise AssertionError("signature transfer second modulus mismatch")
    if witness.get("core_spectral_gap_x1e12") != 173671525179:
        raise AssertionError("signature transfer core gap mismatch")
    if witness.get("spectral_gap_delta_vs_core_x1e12") != 239075938607:
        raise AssertionError("signature transfer gap delta mismatch")
    if witness.get("spectral_gap_ratio_to_core_x1e12") != 2376598370750:
        raise AssertionError("signature transfer gap ratio mismatch")
    if witness.get("stationary_entropy_x1e12") != 5041380484971:
        raise AssertionError("signature transfer stationary entropy mismatch")
    if witness.get("stationary_perplexity_x1e12") != 154683405817640:
        raise AssertionError("signature transfer stationary perplexity mismatch")
    if witness.get("stationary_flow_total_variation_x1e12") != 164666435075:
        raise AssertionError("signature transfer total variation mismatch")
    if witness.get("stationary_flow_correlation_x1e12") != 869103997875:
        raise AssertionError("signature transfer flow correlation mismatch")

    edge_table = np.asarray(tables["signature_transfer_edge_table"], dtype=np.int64)
    stationary_table = np.asarray(tables["signature_stationary_table"], dtype=np.int64)
    mask_table = np.asarray(tables["signature_mask_stationary_table"], dtype=np.int64)
    atom_table = np.asarray(tables["signature_atom_stationary_table"], dtype=np.int64)
    observable_table = np.asarray(tables["signature_transfer_observable_table"], dtype=np.int64)
    transition_matrix = np.asarray(tables["signature_transfer_matrix_x1e12"], dtype=np.int64)
    spectrum = np.asarray(tables["symmetric_similarity_spectrum_x1e12"], dtype=np.int64)
    stationary_vector = np.asarray(tables["signature_stationary_distribution_x1e12"], dtype=np.int64)
    shared_matrix = np.asarray(tables["signature_shared_active_atom_matrix"], dtype=np.int64)

    if edge_table.shape != (13035, len(SIGNATURE_TRANSFER_EDGE_COLUMNS)):
        raise AssertionError("signature transfer edge table shape mismatch")
    if stationary_table.shape != (221, len(SIGNATURE_STATIONARY_COLUMNS)):
        raise AssertionError("signature stationary table shape mismatch")
    if mask_table.shape != (14, len(MASK_STATIONARY_COLUMNS)):
        raise AssertionError("signature mask stationary table shape mismatch")
    if atom_table.shape != (6, len(ATOM_STATIONARY_COLUMNS)):
        raise AssertionError("signature atom stationary table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(SIGNATURE_TRANSFER_OBSERVABLE_COLUMNS)):
        raise AssertionError("signature observable table shape mismatch")
    if transition_matrix.shape != (221, 221):
        raise AssertionError("signature transition matrix shape mismatch")
    if not np.all(transition_matrix.sum(axis=1) == 1_000_000_000_000):
        raise AssertionError("signature transition matrix row sums mismatch")
    if stationary_vector.shape != (221,):
        raise AssertionError("signature stationary vector shape mismatch")
    if int(stationary_vector.sum()) != 1_000_000_000_000:
        raise AssertionError("signature stationary vector sum mismatch")
    if shared_matrix.shape != (221, 221):
        raise AssertionError("signature shared matrix shape mismatch")
    if int(np.sum(shared_matrix > 0) // 2) != 13035:
        raise AssertionError("signature shared matrix support mismatch")
    if spectrum.shape != (221,):
        raise AssertionError("signature spectrum shape mismatch")
    if int(spectrum[0]) != 1_000_000_000_000:
        raise AssertionError("signature spectrum top eigenvalue mismatch")
    if int(spectrum[1]) != 587252536214:
        raise AssertionError("signature spectrum second eigenvalue mismatch")
    if int(spectrum[-1]) != -23107307402:
        raise AssertionError("signature spectrum minimum eigenvalue mismatch")
    if int(stationary_table[:, 2].sum()) != 1_000_000_000_000:
        raise AssertionError("signature stationary table mass sum mismatch")
    if int(mask_table[:, 3].sum()) != 1_000_000_000_000:
        raise AssertionError("signature mask table mass sum mismatch")
    if int(atom_table[:, 1].sum()) != 1_000_000_000_000:
        raise AssertionError("signature atom table mass sum mismatch")
    if int(edge_table[:, 10].sum()) != 1_000_000_000_000:
        raise AssertionError("signature transfer edge flux sum mismatch")

    inputs = report.get("inputs", {})
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
    assert_file_hash(
        inputs.get("boundary_transfer_report", {}),
        BOUNDARY_TRANSFER_REPORT,
        "boundary transfer report input",
    )
    assert_file_hash(
        inputs.get("boundary_transfer", {}),
        BOUNDARY_TRANSFER_JSON,
        "boundary transfer JSON input",
    )
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_subboundary_transfer_operator_manifest@1":
        raise AssertionError("C985 d20 signature transfer manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature transfer manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature transfer manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature transfer missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature transfer index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature transfer index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_subboundary_transfer_operator@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "active_signature_class_count": witness.get("active_signature_class_count"),
        "transfer_edge_count": witness.get("transfer_edge_count"),
        "spectral_gap_x1e12": witness.get("spectral_gap_x1e12"),
        "core_spectral_gap_x1e12": witness.get("core_spectral_gap_x1e12"),
        "spectral_gap_ratio_to_core_x1e12": witness.get(
            "spectral_gap_ratio_to_core_x1e12"
        ),
        "top_stationary_signature_class_ids": witness.get(
            "top_stationary_signature_class_ids"
        ),
        "top_mask_class_ids": witness.get("top_mask_class_ids"),
        "top_atom_ids": witness.get("top_atom_ids"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_subboundary_transfer_operator()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
