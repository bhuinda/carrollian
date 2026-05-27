from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_recurrent_signature_subboundary import (
        ATLAS_CERTIFICATE,
        ATLAS_JSON,
        ATLAS_REPORT,
        ATLAS_TABLES,
        ATOM_FLOW_CERTIFICATE,
        ATOM_FLOW_JSON,
        ATOM_FLOW_REPORT,
        ATOM_FLOW_TABLES,
        CARRIER_MASK_CLASS_COLUMNS,
        EXCLUDED_SIGNATURE_COLUMNS,
        HYPERBOLIC_GRAPH_CERTIFICATE,
        HYPERBOLIC_GRAPH_JSON,
        HYPERBOLIC_GRAPH_REPORT,
        HYPERBOLIC_GRAPH_TABLES,
        INDEX_PATH,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        SIGNATURE_EDGE_COLUMNS,
        SIGNATURE_VERTEX_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_recurrent_signature_subboundary import (
        ATLAS_CERTIFICATE,
        ATLAS_JSON,
        ATLAS_REPORT,
        ATLAS_TABLES,
        ATOM_FLOW_CERTIFICATE,
        ATOM_FLOW_JSON,
        ATOM_FLOW_REPORT,
        ATOM_FLOW_TABLES,
        CARRIER_MASK_CLASS_COLUMNS,
        EXCLUDED_SIGNATURE_COLUMNS,
        HYPERBOLIC_GRAPH_CERTIFICATE,
        HYPERBOLIC_GRAPH_JSON,
        HYPERBOLIC_GRAPH_REPORT,
        HYPERBOLIC_GRAPH_TABLES,
        INDEX_PATH,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        SIGNATURE_EDGE_COLUMNS,
        SIGNATURE_VERTEX_COLUMNS,
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


def validate_c985_d20_recurrent_signature_subboundary() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    subboundary = load_json(OUT_DIR / "recurrent_signature_subboundary.json")
    certificate = load_json(OUT_DIR / "recurrent_signature_subboundary_certificate.json")
    vertices_csv = (OUT_DIR / "signature_subboundary_vertices.csv").read_text(
        encoding="utf-8"
    )
    edges_csv = (OUT_DIR / "signature_subboundary_edges.csv").read_text(
        encoding="utf-8"
    )
    masks_csv = (OUT_DIR / "carrier_mask_classes.csv").read_text(encoding="utf-8")
    excluded_csv = (OUT_DIR / "excluded_signature_classes.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "recurrent_signature_subboundary_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if subboundary != expected["recurrent_signature_subboundary"]:
        raise AssertionError("recurrent signature subboundary JSON is not reproducible")
    if vertices_csv != expected["signature_subboundary_vertices_csv"]:
        raise AssertionError("recurrent signature vertex CSV is not reproducible")
    if edges_csv != expected["signature_subboundary_edges_csv"]:
        raise AssertionError("recurrent signature edge CSV is not reproducible")
    if masks_csv != expected["carrier_mask_classes_csv"]:
        raise AssertionError("recurrent carrier-mask CSV is not reproducible")
    if excluded_csv != expected["excluded_signature_classes_csv"]:
        raise AssertionError("recurrent excluded-signature CSV is not reproducible")
    if certificate != expected["recurrent_signature_subboundary_certificate"]:
        raise AssertionError("recurrent signature subboundary certificate is not reproducible")

    table_names = [
        "signature_vertex_table",
        "signature_edge_table",
        "carrier_mask_class_table",
        "excluded_signature_table",
        "signature_adjacency",
        "signature_distances",
        "mask_class_adjacency",
        "mask_class_distances",
        "delta_representative_indices",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"recurrent signature subboundary table {name} is not reproducible"
            )

    if report.get("schema") != "c985.proof_obligation.d20_recurrent_signature_subboundary@1":
        raise AssertionError("C985 d20 recurrent signature subboundary report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 recurrent signature subboundary is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 recurrent signature subboundary all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 recurrent signature subboundary checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 recurrent signature subboundary report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 recurrent signature subboundary report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "atom_flow_report_certified",
        "atom_flow_certificate_certified",
        "hyperbolic_graph_report_certified",
        "hyperbolic_graph_certificate_certified",
        "boundary_atlas_report_certified",
        "boundary_atlas_certificate_certified",
        "active_signature_count_is_221",
        "inactive_signature_count_is_12",
        "inactive_signature_ids_are_expected",
        "active_atoms_are_expected",
        "signature_graph_edge_count_is_13035",
        "signature_graph_is_connected",
        "signature_graph_diameter_is_3",
        "signature_distance_histogram_matches_expected",
        "degree_histogram_matches_expected",
        "active_atom_count_histogram_matches_expected",
        "carrier_mask_count_is_14",
        "carrier_mask_histogram_matches_expected",
        "mask_graph_edge_count_is_44",
        "mask_graph_diameter_is_3",
        "mask_graph_distance_histogram_matches_expected",
        "delta_representative_count_is_56",
        "signature_graph_delta_twice_is_2",
        "signature_graph_delta_witness_is_expected",
        "signature_graph_delta_witness_masks_are_expected",
        "signature_graph_delta_witness_sums_are_expected",
        "full_johnson_boundary_diameter_matches",
        "full_johnson_boundary_delta_matches",
        "subboundary_matches_full_johnson_diameter",
        "subboundary_matches_full_johnson_delta",
        "excluded_signature_full_carrier_mask_is_840",
        "excluded_signature_full_carriers_are_3_6_8_9",
        "excluded_signature_active_carrier_count_is_zero",
        "signature_vertex_table_shape_is_221_by_9",
        "signature_edge_table_shape_is_13035_by_6",
        "carrier_mask_class_table_shape_is_14_by_10",
        "excluded_signature_table_shape_is_12_by_8",
        "signature_adjacency_shape_is_221_by_221",
        "signature_distances_shape_is_221_by_221",
        "mask_class_adjacency_shape_is_14_by_14",
        "mask_class_distances_shape_is_14_by_14",
        "hyperbolic_tables_johnson_distance_available",
        "atlas_atom_table_shape_is_20_rows",
        "atom_flow_signature_table_shape_is_233_rows",
        "atom_flow_json_schema_available",
        "hyperbolic_graph_json_schema_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(
            f"C985 d20 recurrent signature subboundary missing true checks: {missing}"
        )

    witness = report.get("witness", {})
    if witness.get("active_atom_ids") != [1, 4, 7, 11, 12, 19]:
        raise AssertionError("recurrent signature active atom mismatch")
    if witness.get("active_signature_class_count") != 221:
        raise AssertionError("recurrent signature active count mismatch")
    if witness.get("inactive_signature_class_count") != 12:
        raise AssertionError("recurrent signature inactive count mismatch")
    if witness.get("inactive_signature_class_ids") != [
        39,
        40,
        41,
        42,
        43,
        44,
        184,
        185,
        186,
        187,
        188,
        189,
    ]:
        raise AssertionError("recurrent signature inactive ids mismatch")
    if witness.get("signature_graph_edge_count") != 13035:
        raise AssertionError("recurrent signature edge count mismatch")
    if witness.get("signature_graph_component_count") != 1:
        raise AssertionError("recurrent signature component count mismatch")
    if witness.get("signature_graph_diameter") != 3:
        raise AssertionError("recurrent signature diameter mismatch")
    if witness.get("signature_graph_delta_twice") != 2:
        raise AssertionError("recurrent signature delta mismatch")
    if witness.get("signature_graph_delta_fraction") != [2, 2]:
        raise AssertionError("recurrent signature delta fraction mismatch")
    if witness.get("delta_witness_signature_class_ids") != [0, 48, 126, 212]:
        raise AssertionError("recurrent signature delta witness mismatch")
    if witness.get("delta_witness_carrier_atom_masks") != [146, 6146, 524416, 528384]:
        raise AssertionError("recurrent signature delta witness masks mismatch")
    if witness.get("delta_witness_pair_sums") != [2, 2, 4]:
        raise AssertionError("recurrent signature delta witness sums mismatch")
    if witness.get("delta_representative_count") != 56:
        raise AssertionError("recurrent signature representative count mismatch")
    if witness.get("carrier_mask_count") != 14:
        raise AssertionError("recurrent signature carrier-mask count mismatch")
    if witness.get("mask_graph_edge_count") != 44:
        raise AssertionError("recurrent signature mask graph edge count mismatch")
    if witness.get("mask_graph_diameter") != 3:
        raise AssertionError("recurrent signature mask graph diameter mismatch")
    if witness.get("excluded_full_carrier_atom_ids") != [3, 6, 8, 9]:
        raise AssertionError("recurrent signature excluded carrier ids mismatch")
    if witness.get("excluded_full_carrier_atom_mask") != 840:
        raise AssertionError("recurrent signature excluded carrier mask mismatch")
    if witness.get("full_johnson_diameter") != 3:
        raise AssertionError("full Johnson diameter comparison mismatch")
    if witness.get("full_johnson_delta_fraction") != [2, 2]:
        raise AssertionError("full Johnson delta comparison mismatch")

    signature_vertex_table = np.asarray(tables["signature_vertex_table"], dtype=np.int64)
    signature_edge_table = np.asarray(tables["signature_edge_table"], dtype=np.int64)
    carrier_mask_class_table = np.asarray(tables["carrier_mask_class_table"], dtype=np.int64)
    excluded_signature_table = np.asarray(tables["excluded_signature_table"], dtype=np.int64)
    signature_adjacency = np.asarray(tables["signature_adjacency"], dtype=np.int8)
    signature_distances = np.asarray(tables["signature_distances"], dtype=np.int16)
    mask_class_adjacency = np.asarray(tables["mask_class_adjacency"], dtype=np.int8)
    mask_class_distances = np.asarray(tables["mask_class_distances"], dtype=np.int16)
    representatives = np.asarray(tables["delta_representative_indices"], dtype=np.int64)

    if signature_vertex_table.shape != (221, len(SIGNATURE_VERTEX_COLUMNS)):
        raise AssertionError("recurrent signature vertex table shape mismatch")
    if signature_edge_table.shape != (13035, len(SIGNATURE_EDGE_COLUMNS)):
        raise AssertionError("recurrent signature edge table shape mismatch")
    if carrier_mask_class_table.shape != (14, len(CARRIER_MASK_CLASS_COLUMNS)):
        raise AssertionError("recurrent signature carrier-mask table shape mismatch")
    if excluded_signature_table.shape != (12, len(EXCLUDED_SIGNATURE_COLUMNS)):
        raise AssertionError("recurrent signature excluded-signature table shape mismatch")
    if signature_adjacency.shape != (221, 221):
        raise AssertionError("recurrent signature adjacency shape mismatch")
    if signature_distances.shape != (221, 221):
        raise AssertionError("recurrent signature distance shape mismatch")
    if mask_class_adjacency.shape != (14, 14):
        raise AssertionError("recurrent signature mask adjacency shape mismatch")
    if mask_class_distances.shape != (14, 14):
        raise AssertionError("recurrent signature mask distance shape mismatch")
    if representatives.shape != (56,):
        raise AssertionError("recurrent signature representative index shape mismatch")
    if int(np.max(signature_distances)) != 3:
        raise AssertionError("recurrent signature distance matrix diameter mismatch")
    if int(np.sum(signature_adjacency) // 2) != 13035:
        raise AssertionError("recurrent signature adjacency edge count mismatch")
    if int(np.max(mask_class_distances)) != 3:
        raise AssertionError("recurrent signature mask distance matrix diameter mismatch")
    if int(np.sum(mask_class_adjacency) // 2) != 44:
        raise AssertionError("recurrent signature mask adjacency edge count mismatch")
    if not np.array_equal(excluded_signature_table[:, 1], np.full(12, 840, dtype=np.int64)):
        raise AssertionError("recurrent signature excluded carrier masks table mismatch")
    if not np.array_equal(
        excluded_signature_table[:, 4:8],
        np.tile(np.asarray([3, 6, 8, 9], dtype=np.int64), (12, 1)),
    ):
        raise AssertionError("recurrent signature excluded carrier ids table mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("stationary_atom_flow_report", {}),
        ATOM_FLOW_REPORT,
        "atom-flow report input",
    )
    assert_file_hash(
        inputs.get("stationary_atom_flow", {}),
        ATOM_FLOW_JSON,
        "atom-flow JSON input",
    )
    assert_file_hash(
        inputs.get("stationary_atom_flow_tables", {}),
        ATOM_FLOW_TABLES,
        "atom-flow tables input",
    )
    assert_file_hash(
        inputs.get("stationary_atom_flow_certificate", {}),
        ATOM_FLOW_CERTIFICATE,
        "atom-flow certificate input",
    )
    assert_file_hash(
        inputs.get("hyperbolic_graph_report", {}),
        HYPERBOLIC_GRAPH_REPORT,
        "hyperbolic graph report input",
    )
    assert_file_hash(
        inputs.get("hyperbolic_graph", {}),
        HYPERBOLIC_GRAPH_JSON,
        "hyperbolic graph JSON input",
    )
    assert_file_hash(
        inputs.get("hyperbolic_graph_tables", {}),
        HYPERBOLIC_GRAPH_TABLES,
        "hyperbolic graph tables input",
    )
    assert_file_hash(
        inputs.get("hyperbolic_graph_certificate", {}),
        HYPERBOLIC_GRAPH_CERTIFICATE,
        "hyperbolic graph certificate input",
    )
    assert_file_hash(inputs.get("boundary_atlas_report", {}), ATLAS_REPORT, "atlas report input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "atlas JSON input")
    assert_file_hash(inputs.get("boundary_atlas_tables", {}), ATLAS_TABLES, "atlas tables input")
    assert_file_hash(
        inputs.get("boundary_atlas_certificate", {}),
        ATLAS_CERTIFICATE,
        "atlas certificate input",
    )
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation geometry signatures input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_recurrent_signature_subboundary_manifest@1":
        raise AssertionError("C985 d20 recurrent signature subboundary manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 recurrent signature subboundary manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 recurrent signature subboundary manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 recurrent signature subboundary missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 recurrent signature subboundary index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 recurrent signature subboundary index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_recurrent_signature_subboundary@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "active_signature_class_count": witness.get("active_signature_class_count"),
        "signature_graph_edge_count": witness.get("signature_graph_edge_count"),
        "signature_graph_diameter": witness.get("signature_graph_diameter"),
        "signature_graph_delta_fraction": witness.get("signature_graph_delta_fraction"),
        "carrier_mask_count": witness.get("carrier_mask_count"),
        "mask_graph_edge_count": witness.get("mask_graph_edge_count"),
        "excluded_signature_class_ids": witness.get("inactive_signature_class_ids"),
        "excluded_full_carrier_atom_ids": witness.get("excluded_full_carrier_atom_ids"),
        "full_johnson_delta_fraction": witness.get("full_johnson_delta_fraction"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_recurrent_signature_subboundary()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
