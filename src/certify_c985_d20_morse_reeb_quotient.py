from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_morse_reeb_quotient import (
        CHAMBER_SPINE_CERTIFICATE,
        CHAMBER_SPINE_JSON,
        CHAMBER_SPINE_REPORT,
        CHAMBER_SPINE_TABLES,
        CORE_BASIN_COLUMNS,
        DIRECTED_COMPOSITION_COLUMNS,
        DIRECTED_INTERVAL_COLUMNS,
        DIRECTED_PATH_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        SPINE_BASIN_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_morse_reeb_quotient import (
        CHAMBER_SPINE_CERTIFICATE,
        CHAMBER_SPINE_JSON,
        CHAMBER_SPINE_REPORT,
        CHAMBER_SPINE_TABLES,
        CORE_BASIN_COLUMNS,
        DIRECTED_COMPOSITION_COLUMNS,
        DIRECTED_INTERVAL_COLUMNS,
        DIRECTED_PATH_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        SPINE_BASIN_COLUMNS,
        STATUS,
        THEOREM_ID,
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


def validate_c985_d20_morse_reeb_quotient() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    morse_reeb = load_json(OUT_DIR / "morse_reeb_quotient.json")
    certificate = load_json(OUT_DIR / "morse_reeb_certificate.json")
    core_basin_csv = (OUT_DIR / "core_basin_nodes.csv").read_text(encoding="utf-8")
    spine_basin_csv = (OUT_DIR / "spine_basin_nodes.csv").read_text(encoding="utf-8")
    directed_paths_csv = (OUT_DIR / "directed_interval_paths.csv").read_text(
        encoding="utf-8"
    )
    directed_intervals_csv = (OUT_DIR / "directed_intervals.csv").read_text(
        encoding="utf-8"
    )
    directed_compositions_csv = (OUT_DIR / "directed_compositions.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(OUT_DIR / "morse_reeb_tables.npz", allow_pickle=False)
    index = load_json(INDEX_PATH)

    if morse_reeb != expected["morse_reeb_quotient"]:
        raise AssertionError("d20 Morse/Reeb quotient JSON is not reproducible")
    if core_basin_csv != expected["core_basin_nodes_csv"]:
        raise AssertionError("d20 Morse/Reeb core basin CSV is not reproducible")
    if spine_basin_csv != expected["spine_basin_nodes_csv"]:
        raise AssertionError("d20 Morse/Reeb spine basin CSV is not reproducible")
    if directed_paths_csv != expected["directed_interval_paths_csv"]:
        raise AssertionError("d20 Morse/Reeb directed paths CSV is not reproducible")
    if directed_intervals_csv != expected["directed_intervals_csv"]:
        raise AssertionError("d20 Morse/Reeb directed intervals CSV is not reproducible")
    if directed_compositions_csv != expected["directed_compositions_csv"]:
        raise AssertionError("d20 Morse/Reeb directed compositions CSV is not reproducible")
    if certificate != expected["morse_reeb_certificate"]:
        raise AssertionError("d20 Morse/Reeb certificate is not reproducible")

    table_names = [
        "core_basin_table",
        "spine_basin_table",
        "directed_path_table",
        "directed_interval_table",
        "directed_composition_table",
        "source_reachability_matrix",
        "basin_label_vector",
        "region_10_nodes",
        "region_43_nodes",
        "boundary_nodes",
        "region_10_adjacency",
        "region_43_adjacency",
        "boundary_adjacency",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"d20 Morse/Reeb table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_morse_reeb_quotient@1":
        raise AssertionError("C985 d20 Morse/Reeb report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 Morse/Reeb quotient is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 Morse/Reeb all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 Morse/Reeb checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Morse/Reeb report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 Morse/Reeb report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "chamber_spine_report_certified",
        "chamber_spine_certificate_certified",
        "core_node_count_is_12",
        "directed_edge_count_is_31",
        "sources_are_10_43",
        "sink_is_44",
        "source_10_reach_count_is_7",
        "source_43_reach_count_is_9",
        "exclusive_10_lobe_is_10_17_32",
        "exclusive_43_lobe_is_13_28_38_41_43",
        "overlap_rejoin_is_19_34_42_44",
        "source_reachability_matrix_shape_is_2_by_12",
        "source_sink_path_count_is_42",
        "source_sink_path_counts_are_10_and_32",
        "directed_morphism_count_is_176",
        "nonidentity_morphism_count_is_164",
        "directed_interval_count_is_57",
        "reachable_nonidentity_pair_count_is_45",
        "directed_path_length_histogram_matches",
        "source_sink_path_length_histogram_matches",
        "directed_interval_path_count_histogram_matches",
        "directed_interval_node_count_histogram_matches",
        "max_path_interval_is_43_to_44_with_32_paths",
        "composition_pair_count_is_603",
        "associativity_triple_count_is_1480",
        "associativity_has_zero_failures",
        "identity_has_zero_failures",
        "core_basin_table_shape_is_12_by_9",
        "spine_basin_table_shape_is_50_by_9",
        "directed_path_table_shape_is_176_by_16",
        "directed_interval_table_shape_is_57_by_17",
        "directed_composition_table_shape_is_603_by_10",
        "spine_basin_counts_are_16_20_14",
        "boundary_nodes_are_expected",
        "boundary_contains_all_core_retraction_obstructions",
        "region_10_connected_edges_diameter_delta",
        "region_43_connected_edges_diameter_delta",
        "boundary_connected_edges_diameter_delta",
        "spine_edge_label_counts_match",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 Morse/Reeb missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("core_node_count") != 12:
        raise AssertionError("Morse/Reeb core node count mismatch")
    if witness.get("directed_edge_count") != 31:
        raise AssertionError("Morse/Reeb directed edge count mismatch")
    if witness.get("source_node_ids") != [10, 43]:
        raise AssertionError("Morse/Reeb source nodes mismatch")
    if witness.get("sink_node_ids") != [44]:
        raise AssertionError("Morse/Reeb sink nodes mismatch")
    if witness.get("source_10_reach_node_ids") != [10, 17, 19, 32, 34, 42, 44]:
        raise AssertionError("Morse/Reeb source 10 reachability mismatch")
    if witness.get("source_43_reach_node_ids") != [13, 19, 28, 34, 38, 41, 42, 43, 44]:
        raise AssertionError("Morse/Reeb source 43 reachability mismatch")
    if witness.get("exclusive_10_lobe_node_ids") != [10, 17, 32]:
        raise AssertionError("Morse/Reeb source 10 lobe mismatch")
    if witness.get("exclusive_43_lobe_node_ids") != [13, 28, 38, 41, 43]:
        raise AssertionError("Morse/Reeb source 43 lobe mismatch")
    if witness.get("overlap_rejoin_node_ids") != [19, 34, 42, 44]:
        raise AssertionError("Morse/Reeb overlap/rejoin mismatch")
    if witness.get("directed_path_morphism_count") != 176:
        raise AssertionError("Morse/Reeb directed morphism count mismatch")
    if witness.get("nonidentity_morphism_count") != 164:
        raise AssertionError("Morse/Reeb nonidentity morphism count mismatch")
    if witness.get("directed_interval_count") != 57:
        raise AssertionError("Morse/Reeb directed interval count mismatch")
    if witness.get("reachable_nonidentity_pair_count") != 45:
        raise AssertionError("Morse/Reeb reachable nonidentity pair count mismatch")
    if witness.get("source_sink_path_count") != 42:
        raise AssertionError("Morse/Reeb source-sink path count mismatch")
    if [row.get("path_count") for row in witness.get("source_sink_path_counts", [])] != [10, 32]:
        raise AssertionError("Morse/Reeb source-sink source counts mismatch")
    if witness.get("composition_pair_count") != 603:
        raise AssertionError("Morse/Reeb composition pair count mismatch")
    if witness.get("associativity_triple_count") != 1480:
        raise AssertionError("Morse/Reeb associativity triple count mismatch")
    if witness.get("associativity_failure_count") != 0:
        raise AssertionError("Morse/Reeb associativity failures mismatch")
    if witness.get("left_identity_failure_count") != 0 or witness.get("right_identity_failure_count") != 0:
        raise AssertionError("Morse/Reeb identity failures mismatch")
    if witness.get("spine_basin_node_counts") != {"10": 16, "43": 20, "boundary": 14}:
        raise AssertionError("Morse/Reeb spine basin counts mismatch")
    if witness.get("spine_boundary_node_ids") != [19, 34, 42, 7, 9, 12, 14, 16, 27, 29, 31, 45, 50, 54]:
        raise AssertionError("Morse/Reeb spine boundary mismatch")
    if witness.get("spine_boundary_edge_count") != 37:
        raise AssertionError("Morse/Reeb spine boundary edge count mismatch")
    if witness.get("spine_region_10_edge_count") != 48:
        raise AssertionError("Morse/Reeb source 10 region edge count mismatch")
    if witness.get("spine_region_43_edge_count") != 58:
        raise AssertionError("Morse/Reeb source 43 region edge count mismatch")
    if witness.get("spine_boundary_diameter") != 3:
        raise AssertionError("Morse/Reeb boundary diameter mismatch")
    if witness.get("spine_boundary_gromov_delta_twice") != 2:
        raise AssertionError("Morse/Reeb boundary delta mismatch")
    if witness.get("core_retraction_obstruction_node_ids") != [7, 9, 12, 14, 16, 27, 29, 31, 50]:
        raise AssertionError("Morse/Reeb obstruction nodes mismatch")
    if witness.get("boundary_contains_core_retraction_obstructions") is not True:
        raise AssertionError("Morse/Reeb boundary obstruction containment mismatch")

    core_basin_table = np.asarray(tables["core_basin_table"], dtype=np.int64)
    spine_basin_table = np.asarray(tables["spine_basin_table"], dtype=np.int64)
    directed_path_table = np.asarray(tables["directed_path_table"], dtype=np.int64)
    directed_interval_table = np.asarray(tables["directed_interval_table"], dtype=np.int64)
    directed_composition_table = np.asarray(tables["directed_composition_table"], dtype=np.int64)
    source_matrix = np.asarray(tables["source_reachability_matrix"], dtype=np.int8)
    basin_label_vector = np.asarray(tables["basin_label_vector"], dtype=np.int64)
    region_10_adjacency = np.asarray(tables["region_10_adjacency"], dtype=np.int8)
    region_43_adjacency = np.asarray(tables["region_43_adjacency"], dtype=np.int8)
    boundary_adjacency = np.asarray(tables["boundary_adjacency"], dtype=np.int8)

    if core_basin_table.shape != (12, len(CORE_BASIN_COLUMNS)):
        raise AssertionError("Morse/Reeb core basin table shape mismatch")
    if spine_basin_table.shape != (50, len(SPINE_BASIN_COLUMNS)):
        raise AssertionError("Morse/Reeb spine basin table shape mismatch")
    if directed_path_table.shape != (176, len(DIRECTED_PATH_COLUMNS)):
        raise AssertionError("Morse/Reeb directed path table shape mismatch")
    if directed_interval_table.shape != (57, len(DIRECTED_INTERVAL_COLUMNS)):
        raise AssertionError("Morse/Reeb directed interval table shape mismatch")
    if directed_composition_table.shape != (603, len(DIRECTED_COMPOSITION_COLUMNS)):
        raise AssertionError("Morse/Reeb directed composition table shape mismatch")
    if source_matrix.shape != (2, 12):
        raise AssertionError("Morse/Reeb source reachability matrix shape mismatch")
    if basin_label_vector.shape != (50,):
        raise AssertionError("Morse/Reeb basin label vector shape mismatch")
    if int(np.sum(basin_label_vector == 10)) != 16:
        raise AssertionError("Morse/Reeb basin label 10 count mismatch")
    if int(np.sum(basin_label_vector == 43)) != 20:
        raise AssertionError("Morse/Reeb basin label 43 count mismatch")
    if int(np.sum(basin_label_vector == 0)) != 14:
        raise AssertionError("Morse/Reeb basin boundary label count mismatch")
    for label, adjacency in [
        ("region 10", region_10_adjacency),
        ("region 43", region_43_adjacency),
        ("boundary", boundary_adjacency),
    ]:
        if not np.array_equal(adjacency, adjacency.T):
            raise AssertionError(f"Morse/Reeb {label} adjacency is not symmetric")

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
    assert_file_hash(
        inputs.get("chamber_spine_report", {}),
        CHAMBER_SPINE_REPORT,
        "chamber spine report input",
    )
    assert_file_hash(inputs.get("chamber_spine", {}), CHAMBER_SPINE_JSON, "chamber spine input")
    assert_file_hash(
        inputs.get("chamber_spine_tables", {}),
        CHAMBER_SPINE_TABLES,
        "chamber spine tables input",
    )
    assert_file_hash(
        inputs.get("chamber_spine_certificate", {}),
        CHAMBER_SPINE_CERTIFICATE,
        "chamber spine certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_morse_reeb_quotient_manifest@1":
        raise AssertionError("C985 d20 Morse/Reeb manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Morse/Reeb manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 Morse/Reeb manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 Morse/Reeb missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 Morse/Reeb index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 Morse/Reeb index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_morse_reeb_quotient@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "source_node_ids": witness.get("source_node_ids"),
        "sink_node_ids": witness.get("sink_node_ids"),
        "exclusive_10_lobe_node_ids": witness.get("exclusive_10_lobe_node_ids"),
        "exclusive_43_lobe_node_ids": witness.get("exclusive_43_lobe_node_ids"),
        "overlap_rejoin_node_ids": witness.get("overlap_rejoin_node_ids"),
        "directed_path_morphism_count": witness.get("directed_path_morphism_count"),
        "directed_interval_count": witness.get("directed_interval_count"),
        "composition_pair_count": witness.get("composition_pair_count"),
        "associativity_triple_count": witness.get("associativity_triple_count"),
        "spine_basin_node_counts": witness.get("spine_basin_node_counts"),
        "spine_boundary_node_ids": witness.get("spine_boundary_node_ids"),
        "spine_boundary_edge_count": witness.get("spine_boundary_edge_count"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_morse_reeb_quotient()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
