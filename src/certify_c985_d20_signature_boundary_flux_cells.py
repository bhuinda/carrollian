from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_flux_cells import (
        BOUNDARY_FLUX_OBSERVABLE_COLUMNS,
        BOUNDARY_MASK_EDGE_COLUMNS,
        BOUNDARY_PARTITION_COLUMNS,
        BOUNDARY_SIGNATURE_EDGE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CELL_COMPLEX_VERTICES,
        OBSERVABLE_CODES,
        OUT_DIR,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_EDGES,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        SPECTRAL_MASK_SUMMARY,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_flux_cells import (
        BOUNDARY_FLUX_OBSERVABLE_COLUMNS,
        BOUNDARY_MASK_EDGE_COLUMNS,
        BOUNDARY_PARTITION_COLUMNS,
        BOUNDARY_SIGNATURE_EDGE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CELL_COMPLEX_VERTICES,
        OBSERVABLE_CODES,
        OUT_DIR,
        SPECTRAL_CUT_CERTIFICATE,
        SPECTRAL_CUT_EDGES,
        SPECTRAL_CUT_JSON,
        SPECTRAL_CUT_REPORT,
        SPECTRAL_CUT_TABLES,
        SPECTRAL_MASK_SUMMARY,
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


def validate_c985_d20_signature_boundary_flux_cells() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    boundary_flux = load_json(OUT_DIR / "signature_boundary_flux_cells.json")
    certificate = load_json(OUT_DIR / "signature_boundary_flux_cells_certificate.json")
    signature_csv = (OUT_DIR / "boundary_signature_edges.csv").read_text(encoding="utf-8")
    mask_csv = (OUT_DIR / "boundary_mask_edges.csv").read_text(encoding="utf-8")
    partition_csv = (OUT_DIR / "boundary_partition_summary.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "boundary_flux_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(OUT_DIR / "signature_boundary_flux_cells_tables.npz", allow_pickle=False)
    index = load_json(Path(OUT_DIR).parents[0] / "index.json")

    if boundary_flux != expected["signature_boundary_flux_cells"]:
        raise AssertionError("signature boundary flux JSON is not reproducible")
    if signature_csv != expected["boundary_signature_edges_csv"]:
        raise AssertionError("boundary signature edge CSV is not reproducible")
    if mask_csv != expected["boundary_mask_edges_csv"]:
        raise AssertionError("boundary mask edge CSV is not reproducible")
    if partition_csv != expected["boundary_partition_summary_csv"]:
        raise AssertionError("boundary partition CSV is not reproducible")
    if observable_csv != expected["boundary_flux_observables_csv"]:
        raise AssertionError("boundary flux observable CSV is not reproducible")
    if certificate != expected["signature_boundary_flux_cells_certificate"]:
        raise AssertionError("signature boundary flux certificate is not reproducible")

    table_names = [
        "boundary_signature_edge_table",
        "boundary_mask_edge_table",
        "boundary_partition_table",
        "boundary_flux_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"signature boundary flux table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_flux_cells@1":
        raise AssertionError("C985 d20 signature boundary flux report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 signature boundary flux is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 signature boundary flux all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 signature boundary flux checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature boundary flux report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 signature boundary flux report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "cell_complex_report_certified",
        "cell_complex_certificate_certified",
        "spectral_cut_report_certified",
        "spectral_cut_certificate_certified",
        "signature_cut_edge_count_is_4007",
        "carrier_boundary_edge_count_is_16",
        "total_cut_flux_matches_spectral_cut",
        "all_signature_cut_edges_have_shared_active_atom_one",
        "shared_active_atom_sum_matches_cut_edge_count",
        "boundary_pair_set_matches_cell_complex",
        "boundary_degrees_match_spectral_mask_summary",
        "unexpected_boundary_partition_count_is_zero",
        "high_negative_partition_matches_expected",
        "central_negative_partition_matches_expected",
        "central_negative_carries_flux_majority",
        "top_boundary_pair_matches_expected",
        "boundary_pair_flux_rows_match_expected",
        "signature_edge_table_shape_is_4007_by_13",
        "mask_edge_table_shape_is_16_by_12",
        "partition_table_shape_is_2_by_9",
        "observable_table_shape_matches_codebook",
        "cell_complex_tables_available",
        "spectral_cut_tables_available",
        "cell_complex_json_schema_available",
        "spectral_cut_json_schema_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 signature boundary flux missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("signature_cut_edge_count") != 4007:
        raise AssertionError("signature boundary flux cut edge count mismatch")
    if witness.get("carrier_boundary_edge_count") != 16:
        raise AssertionError("signature boundary flux carrier boundary count mismatch")
    if witness.get("total_undirected_cut_flux_x1e12") != 238962451389:
        raise AssertionError("signature boundary flux total flux mismatch")
    if witness.get("high_negative") != {
        "mask_edge_count": 2,
        "signature_cut_edge_count": 198,
        "undirected_cut_flux_x1e12": 3712054656,
        "flux_fraction_x1e12": 15534049950,
    }:
        raise AssertionError("signature boundary flux high-negative mismatch")
    if witness.get("central_negative") != {
        "mask_edge_count": 14,
        "signature_cut_edge_count": 3809,
        "undirected_cut_flux_x1e12": 235250396733,
        "flux_fraction_x1e12": 984465950050,
    }:
        raise AssertionError("signature boundary flux central-negative mismatch")
    if witness.get("top_boundary_pair") != {
        "boundary_partition_code": 5,
        "flux_fraction_of_total_cut_x1e12": 182318772789,
        "signature_cut_edge_count": 420,
        "source_carrier_mask_class_id": 11,
        "target_carrier_mask_class_id": 13,
        "undirected_stationary_flux_x1e12": 43567340880,
    }:
        raise AssertionError("signature boundary flux top boundary pair mismatch")
    if witness.get("shared_active_atom_sum") != 4007:
        raise AssertionError("signature boundary flux shared atom sum mismatch")
    if witness.get("boundary_degree_l1_delta") != 0:
        raise AssertionError("signature boundary flux boundary degree mismatch")

    signature_table = np.asarray(tables["boundary_signature_edge_table"], dtype=np.int64)
    mask_table = np.asarray(tables["boundary_mask_edge_table"], dtype=np.int64)
    partition_table = np.asarray(tables["boundary_partition_table"], dtype=np.int64)
    observable_table = np.asarray(tables["boundary_flux_observable_table"], dtype=np.int64)

    if signature_table.shape != (4007, len(BOUNDARY_SIGNATURE_EDGE_COLUMNS)):
        raise AssertionError("signature boundary flux signature table shape mismatch")
    if mask_table.shape != (16, len(BOUNDARY_MASK_EDGE_COLUMNS)):
        raise AssertionError("signature boundary flux mask table shape mismatch")
    if partition_table.shape != (2, len(BOUNDARY_PARTITION_COLUMNS)):
        raise AssertionError("signature boundary flux partition table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(BOUNDARY_FLUX_OBSERVABLE_COLUMNS)):
        raise AssertionError("signature boundary flux observable table shape mismatch")
    if int(signature_table[:, 9].sum()) != 4007:
        raise AssertionError("signature boundary flux shared count table mismatch")
    if int(signature_table[:, 10].sum()) != 238962451389:
        raise AssertionError("signature boundary flux signature flux table mismatch")
    if int(mask_table[:, 7].sum()) != 238962451389:
        raise AssertionError("signature boundary flux mask flux table mismatch")
    if int(partition_table[:, 3].sum()) != 238962451389:
        raise AssertionError("signature boundary flux partition flux table mismatch")
    if partition_table[:, 0].tolist() != [4, 5]:
        raise AssertionError("signature boundary flux partition order mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("signature boundary flux observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex", {}), CELL_COMPLEX_JSON, "cell complex JSON input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(
        inputs.get("cell_complex_certificate", {}),
        CELL_COMPLEX_CERTIFICATE,
        "cell complex certificate input",
    )
    assert_file_hash(inputs.get("cell_complex_vertices", {}), CELL_COMPLEX_VERTICES, "cell complex vertices input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("spectral_cut_report", {}), SPECTRAL_CUT_REPORT, "spectral cut report input")
    assert_file_hash(inputs.get("spectral_cut", {}), SPECTRAL_CUT_JSON, "spectral cut JSON input")
    assert_file_hash(inputs.get("spectral_cut_tables", {}), SPECTRAL_CUT_TABLES, "spectral cut tables input")
    assert_file_hash(
        inputs.get("spectral_cut_certificate", {}),
        SPECTRAL_CUT_CERTIFICATE,
        "spectral cut certificate input",
    )
    assert_file_hash(inputs.get("spectral_cut_edges", {}), SPECTRAL_CUT_EDGES, "spectral cut edges input")
    assert_file_hash(inputs.get("spectral_mask_summary", {}), SPECTRAL_MASK_SUMMARY, "spectral mask input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_flux_cells_manifest@1":
        raise AssertionError("C985 d20 signature boundary flux manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature boundary flux manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 signature boundary flux manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 signature boundary flux missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 signature boundary flux index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 signature boundary flux index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_flux_cells@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "signature_cut_edge_count": witness.get("signature_cut_edge_count"),
        "total_undirected_cut_flux_x1e12": witness.get("total_undirected_cut_flux_x1e12"),
        "high_negative": witness.get("high_negative"),
        "central_negative": witness.get("central_negative"),
        "top_boundary_pair": witness.get("top_boundary_pair"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_flux_cells()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
