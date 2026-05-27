from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_chamber_spine import (
        FOLD_COLUMNS,
        MAXIMAL_CHAMBER_COLUMNS,
        ORIENTED_EDGE_COLUMNS,
        OUT_DIR,
        PRESERVED_CORE_CERTIFICATE,
        PRESERVED_CORE_JSON,
        PRESERVED_CORE_REPORT,
        PRESERVED_CORE_TABLES,
        RETRACTION_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        THEOREM_ID,
        TRANSITIVE_REDUCTION_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_chamber_spine import (
        FOLD_COLUMNS,
        MAXIMAL_CHAMBER_COLUMNS,
        ORIENTED_EDGE_COLUMNS,
        OUT_DIR,
        PRESERVED_CORE_CERTIFICATE,
        PRESERVED_CORE_JSON,
        PRESERVED_CORE_REPORT,
        PRESERVED_CORE_TABLES,
        RETRACTION_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        THEOREM_ID,
        TRANSITIVE_REDUCTION_COLUMNS,
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


def validate_c985_d20_chamber_spine() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    chamber_spine = load_json(OUT_DIR / "chamber_spine.json")
    certificate = load_json(OUT_DIR / "chamber_spine_certificate.json")
    oriented_csv = (OUT_DIR / "oriented_core_edges.csv").read_text(encoding="utf-8")
    reduction_csv = (OUT_DIR / "transitive_reduction_edges.csv").read_text(encoding="utf-8")
    chambers_csv = (OUT_DIR / "maximal_chambers.csv").read_text(encoding="utf-8")
    folds_csv = (OUT_DIR / "spine_folds.csv").read_text(encoding="utf-8")
    retraction_csv = (OUT_DIR / "spine_retraction.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "chamber_spine_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if chamber_spine != expected["chamber_spine"]:
        raise AssertionError("d20 chamber-spine JSON is not reproducible")
    if oriented_csv != expected["oriented_core_edges_csv"]:
        raise AssertionError("d20 oriented core edges CSV is not reproducible")
    if reduction_csv != expected["transitive_reduction_edges_csv"]:
        raise AssertionError("d20 transitive reduction CSV is not reproducible")
    if chambers_csv != expected["maximal_chambers_csv"]:
        raise AssertionError("d20 maximal chambers CSV is not reproducible")
    if folds_csv != expected["spine_folds_csv"]:
        raise AssertionError("d20 spine folds CSV is not reproducible")
    if retraction_csv != expected["spine_retraction_csv"]:
        raise AssertionError("d20 spine retraction CSV is not reproducible")
    if certificate != expected["chamber_spine_certificate"]:
        raise AssertionError("d20 chamber-spine certificate is not reproducible")

    table_names = [
        "chamber_node_potential_table",
        "oriented_edge_table",
        "directed_adjacency",
        "transitive_reduction_table",
        "transitive_reduction_adjacency",
        "maximal_chamber_table",
        "fold_table",
        "full_fold_table",
        "retraction_table",
        "spine_nodes",
        "spine_adjacency",
        "spine_distances",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"d20 chamber-spine table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_chamber_spine@1":
        raise AssertionError("C985 d20 chamber-spine report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 chamber-spine is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 chamber-spine all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 chamber-spine checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 chamber-spine report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 chamber-spine report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "preserved_core_report_certified",
        "preserved_core_certificate_certified",
        "high_signature_threshold_matches_preserved_core",
        "core_node_count_is_12",
        "core_edge_count_is_31",
        "oriented_edge_count_is_31",
        "oriented_edge_table_shape_is_31_by_11",
        "directed_adjacency_shape_is_12_by_12",
        "orientation_reason_histogram_is_30_signature_1_poincare",
        "poincare_flow_histogram_is_23_inward_8_outward",
        "directed_orientation_is_acyclic",
        "directed_cycle_count_is_zero",
        "sources_are_10_43",
        "sink_is_44",
        "source_sink_path_count_is_42",
        "all_directed_path_count_is_176",
        "longest_source_sink_path_is_43_38_13_41_28_34_44",
        "transitive_reduction_edge_count_is_15",
        "transitive_reduction_table_shape_is_15_by_6",
        "maximal_chamber_count_is_10",
        "maximal_chamber_size_histogram_is_9_triangles_1_six",
        "triangle_count_is_29",
        "cyclic_directed_triangle_count_is_zero",
        "clique_complex_euler_characteristic_is_zero",
        "largest_chamber_is_13_28_38_41_43_44",
        "undirected_cycle_rank_is_20",
        "boundary_band_node_count_is_52",
        "boundary_band_fold_count_is_2",
        "boundary_band_fold_steps_are_36_to_38_and_52_to_43",
        "fold_table_shape_is_2_by_8",
        "spine_node_count_is_50",
        "spine_edge_count_is_285",
        "spine_diameter_is_3",
        "spine_gromov_delta_is_1",
        "spine_degree_histogram_is_30_nine_20_fifteen",
        "spine_has_no_residual_dominated_pairs",
        "fold_retraction_has_no_graph_failures",
        "retraction_table_shape_is_52_by_5",
        "core_retraction_obstruction_count_is_9",
        "core_retraction_obstruction_nodes_are_expected",
        "full_rewrite_complex_fold_count_is_6",
        "full_rewrite_complex_spine_matches_boundary_spine",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 chamber-spine missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("core_node_count") != 12:
        raise AssertionError("chamber-spine core node count mismatch")
    if witness.get("core_edge_count") != 31:
        raise AssertionError("chamber-spine core edge count mismatch")
    if witness.get("oriented_edge_count") != 31:
        raise AssertionError("chamber-spine oriented edge count mismatch")
    if witness.get("directed_acyclic") is not True or witness.get("directed_cycle_count") != 0:
        raise AssertionError("chamber-spine acyclicity mismatch")
    if witness.get("source_node_ids") != [10, 43]:
        raise AssertionError("chamber-spine source nodes mismatch")
    if witness.get("sink_node_ids") != [44]:
        raise AssertionError("chamber-spine sink nodes mismatch")
    if witness.get("source_sink_path_count") != 42:
        raise AssertionError("chamber-spine source-sink path count mismatch")
    if witness.get("all_directed_path_count") != 176:
        raise AssertionError("chamber-spine all-directed path count mismatch")
    if witness.get("longest_source_sink_path") != [43, 38, 13, 41, 28, 34, 44]:
        raise AssertionError("chamber-spine longest source-sink path mismatch")
    if witness.get("transitive_reduction_edge_count") != 15:
        raise AssertionError("chamber-spine transitive reduction count mismatch")
    if witness.get("maximal_chamber_count") != 10:
        raise AssertionError("chamber-spine maximal chamber count mismatch")
    if witness.get("triangle_count") != 29:
        raise AssertionError("chamber-spine triangle count mismatch")
    if witness.get("cyclic_directed_triangle_count") != 0:
        raise AssertionError("chamber-spine directed triangle cycle mismatch")
    if witness.get("largest_chamber_node_ids") != [13, 28, 38, 41, 43, 44]:
        raise AssertionError("chamber-spine largest chamber mismatch")
    if witness.get("undirected_cycle_rank") != 20:
        raise AssertionError("chamber-spine undirected cycle rank mismatch")
    if witness.get("boundary_band_fold_steps") != [[36, 38], [52, 43]]:
        raise AssertionError("chamber-spine fold steps mismatch")
    if witness.get("spine_node_count") != 50:
        raise AssertionError("chamber-spine node count mismatch")
    if witness.get("spine_edge_count") != 285:
        raise AssertionError("chamber-spine edge count mismatch")
    if witness.get("spine_diameter") != 3:
        raise AssertionError("chamber-spine diameter mismatch")
    if witness.get("spine_gromov_delta_twice") != 2:
        raise AssertionError("chamber-spine delta mismatch")
    if witness.get("fold_retraction_failure_count") != 0:
        raise AssertionError("chamber-spine fold retraction failure mismatch")
    if witness.get("residual_dominated_pair_count") != 0:
        raise AssertionError("chamber-spine residual dominated pair mismatch")
    if witness.get("core_retraction_obstruction_node_ids") != [7, 9, 12, 14, 16, 27, 29, 31, 50]:
        raise AssertionError("chamber-spine core retraction obstruction mismatch")
    if witness.get("full_rewrite_complex_fold_count") != 6:
        raise AssertionError("chamber-spine full rewrite fold count mismatch")
    if witness.get("full_rewrite_complex_spine_matches_boundary_spine") is not True:
        raise AssertionError("chamber-spine full rewrite spine mismatch")

    oriented_edge_table = np.asarray(tables["oriented_edge_table"], dtype=np.int64)
    directed_adjacency = np.asarray(tables["directed_adjacency"], dtype=np.int8)
    reduction_table = np.asarray(tables["transitive_reduction_table"], dtype=np.int64)
    chamber_table = np.asarray(tables["maximal_chamber_table"], dtype=np.int64)
    fold_table = np.asarray(tables["fold_table"], dtype=np.int64)
    retraction_table = np.asarray(tables["retraction_table"], dtype=np.int64)
    spine_adjacency = np.asarray(tables["spine_adjacency"], dtype=np.int8)
    spine_distances = np.asarray(tables["spine_distances"], dtype=np.int64)

    if oriented_edge_table.shape != (31, len(ORIENTED_EDGE_COLUMNS)):
        raise AssertionError("chamber-spine oriented edge table shape mismatch")
    if directed_adjacency.shape != (12, 12):
        raise AssertionError("chamber-spine directed adjacency shape mismatch")
    if int(np.trace(directed_adjacency)) != 0:
        raise AssertionError("chamber-spine directed self-loop detected")
    if reduction_table.shape != (15, len(TRANSITIVE_REDUCTION_COLUMNS)):
        raise AssertionError("chamber-spine reduction table shape mismatch")
    if chamber_table.shape != (10, len(MAXIMAL_CHAMBER_COLUMNS)):
        raise AssertionError("chamber-spine chamber table shape mismatch")
    if fold_table.shape != (2, len(FOLD_COLUMNS)):
        raise AssertionError("chamber-spine fold table shape mismatch")
    if retraction_table.shape != (52, len(RETRACTION_COLUMNS)):
        raise AssertionError("chamber-spine retraction table shape mismatch")
    if spine_adjacency.shape != (50, 50):
        raise AssertionError("chamber-spine adjacency shape mismatch")
    if not np.array_equal(spine_adjacency, spine_adjacency.T):
        raise AssertionError("chamber-spine adjacency is not symmetric")
    if spine_distances.shape != (50, 50) or int(np.max(spine_distances)) != 3:
        raise AssertionError("chamber-spine distance table mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("rewrite_complex_report", {}),
        REWRITE_COMPLEX_REPORT,
        "rewrite complex report input",
    )
    assert_file_hash(inputs.get("rewrite_complex", {}), REWRITE_COMPLEX_JSON, "rewrite complex input")
    assert_file_hash(
        inputs.get("rewrite_complex_tables", {}),
        REWRITE_COMPLEX_TABLES,
        "rewrite complex tables input",
    )
    assert_file_hash(
        inputs.get("rewrite_complex_certificate", {}),
        REWRITE_COMPLEX_CERTIFICATE,
        "rewrite complex certificate input",
    )
    assert_file_hash(
        inputs.get("preserved_core_report", {}),
        PRESERVED_CORE_REPORT,
        "preserved core report input",
    )
    assert_file_hash(inputs.get("preserved_core", {}), PRESERVED_CORE_JSON, "preserved core input")
    assert_file_hash(
        inputs.get("preserved_core_tables", {}),
        PRESERVED_CORE_TABLES,
        "preserved core tables input",
    )
    assert_file_hash(
        inputs.get("preserved_core_certificate", {}),
        PRESERVED_CORE_CERTIFICATE,
        "preserved core certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_chamber_spine_manifest@1":
        raise AssertionError("C985 d20 chamber-spine manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 chamber-spine manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 chamber-spine manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 chamber-spine missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 chamber-spine index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 chamber-spine index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_chamber_spine@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "oriented_edge_count": witness.get("oriented_edge_count"),
        "source_node_ids": witness.get("source_node_ids"),
        "sink_node_ids": witness.get("sink_node_ids"),
        "directed_cycle_count": witness.get("directed_cycle_count"),
        "source_sink_path_count": witness.get("source_sink_path_count"),
        "longest_source_sink_path": witness.get("longest_source_sink_path"),
        "maximal_chamber_count": witness.get("maximal_chamber_count"),
        "triangle_count": witness.get("triangle_count"),
        "undirected_cycle_rank": witness.get("undirected_cycle_rank"),
        "spine_node_count": witness.get("spine_node_count"),
        "spine_edge_count": witness.get("spine_edge_count"),
        "spine_gromov_delta": witness.get("spine_gromov_delta"),
        "core_retraction_obstruction_node_ids": witness.get(
            "core_retraction_obstruction_node_ids"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_chamber_spine()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
