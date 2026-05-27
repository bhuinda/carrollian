from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_geodesic_interval_sheaf import (
        HIGH_SIGNATURE_THRESHOLD,
        INTERVAL_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_REWRITE_REPORT,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_geodesic_interval_sheaf import (
        HIGH_SIGNATURE_THRESHOLD,
        INTERVAL_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_JSON,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_REWRITE_REPORT,
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


def validate_c985_d20_geodesic_interval_sheaf() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    interval_sheaf = load_json(OUT_DIR / "geodesic_interval_sheaf.json")
    certificate = load_json(OUT_DIR / "geodesic_interval_certificate.json")
    intervals_csv = (OUT_DIR / "geodesic_intervals.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "geodesic_interval_tables.npz", allow_pickle=False)
    interval_table = np.asarray(tables["interval_table"], dtype=np.int64)
    interval_membership = np.asarray(tables["interval_membership"], dtype=np.int8)
    index = load_json(INDEX_PATH)

    if interval_sheaf != expected["geodesic_interval_sheaf"]:
        raise AssertionError("d20 geodesic interval sheaf JSON is not reproducible")
    if intervals_csv != expected["geodesic_intervals_csv"]:
        raise AssertionError("d20 geodesic intervals CSV is not reproducible")
    if not np.array_equal(interval_table, expected["interval_table"]):
        raise AssertionError("d20 geodesic interval table is not reproducible")
    if not np.array_equal(interval_membership, expected["interval_membership"]):
        raise AssertionError("d20 geodesic interval membership is not reproducible")
    if certificate != expected["geodesic_interval_certificate"]:
        raise AssertionError("d20 geodesic interval certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_geodesic_interval_sheaf@1":
        raise AssertionError("C985 d20 geodesic interval sheaf report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 geodesic interval sheaf is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 geodesic interval sheaf all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 geodesic interval sheaf checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 geodesic interval sheaf report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 geodesic interval sheaf report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "rewrite_complex_report_certified",
        "rewrite_complex_certificate_certified",
        "symbolic_rewrite_report_certified",
        "high_signature_threshold_matches_binary_rewrite_max",
        "node_table_shape_is_56_by_17",
        "edge_table_shape_is_315_by_13",
        "adjacency_shape_is_56_by_56",
        "graph_distance_shape_is_56_by_56",
        "node_poincare_coordinate_shape_is_56_by_7",
        "node_poincare_distance_shape_is_56_by_56",
        "interval_count_is_1596",
        "interval_table_shape_is_1596_by_18",
        "interval_membership_shape_is_1596_by_56",
        "interval_distance_histogram_is_56_315_720_505",
        "interval_node_count_histogram_matches",
        "shortest_path_count_histogram_matches",
        "max_shortest_path_count_is_36",
        "max_interval_node_count_is_20",
        "all_interval_stalks_nonempty",
        "interval_membership_counts_match_table",
        "full_sector_preserving_interval_count_is_59",
        "high_signature_preserving_interval_count_is_69",
        "full_high_preserving_interval_count_is_46",
        "full_high_preserving_distance_histogram_is_12_zero_31_one_3_two",
        "longest_full_high_graph_distance_is_2",
        "longest_full_high_interval_count_is_3",
        "top_full_high_poincare_interval_is_13_44",
        "top_full_high_poincare_distance_is_0_2453959784",
        "poincare_diameter_interval_is_0_55",
        "poincare_diameter_interval_graph_distance_is_3",
        "poincare_diameter_interval_not_full_or_high_preserving",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 geodesic interval sheaf missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("node_count") != 56:
        raise AssertionError("geodesic interval node count mismatch")
    if witness.get("interval_count") != 1596:
        raise AssertionError("geodesic interval count mismatch")
    if witness.get("high_signature_threshold") != HIGH_SIGNATURE_THRESHOLD:
        raise AssertionError("geodesic interval high-signature threshold mismatch")
    if witness.get("full_sector_preserving_interval_count") != 59:
        raise AssertionError("geodesic interval full-sector count mismatch")
    if witness.get("high_signature_preserving_interval_count") != 69:
        raise AssertionError("geodesic interval high-signature count mismatch")
    if witness.get("full_high_preserving_interval_count") != 46:
        raise AssertionError("geodesic interval full-high count mismatch")
    if witness.get("longest_full_high_graph_distance") != 2:
        raise AssertionError("geodesic interval longest full-high distance mismatch")
    if witness.get("max_shortest_path_count") != 36:
        raise AssertionError("geodesic interval max shortest-path count mismatch")
    if witness.get("max_interval_node_count") != 20:
        raise AssertionError("geodesic interval max interval-node count mismatch")
    top = witness.get("top_full_high_poincare_interval", {})
    if [top.get("source_node_id"), top.get("target_node_id")] != [13, 44]:
        raise AssertionError("geodesic interval top full-high Poincare interval mismatch")
    if top.get("endpoint_poincare_distance") != 0.2453959784:
        raise AssertionError("geodesic interval top full-high Poincare distance mismatch")
    diameter = witness.get("poincare_diameter_interval", {})
    if [diameter.get("source_node_id"), diameter.get("target_node_id")] != [0, 55]:
        raise AssertionError("geodesic interval Poincare diameter interval mismatch")
    if diameter.get("full_sector_preserved") != 0 or diameter.get("high_signature_preserved") != 0:
        raise AssertionError("geodesic interval Poincare diameter preservation mismatch")

    if interval_table.shape != (1596, len(INTERVAL_COLUMNS)):
        raise AssertionError("geodesic interval table shape mismatch")
    if interval_membership.shape != (1596, 56):
        raise AssertionError("geodesic interval membership shape mismatch")
    if int(np.min(np.sum(interval_membership, axis=1))) <= 0:
        raise AssertionError("geodesic interval empty stalk detected")
    if not np.array_equal(np.sum(interval_membership, axis=1), interval_table[:, 4]):
        raise AssertionError("geodesic interval membership count mismatch")
    if int(np.count_nonzero(interval_table[:, 11] != HIGH_SIGNATURE_THRESHOLD)) != 0:
        raise AssertionError("geodesic interval threshold column mismatch")
    if int(np.count_nonzero((interval_table[:, 8] == 1) & (interval_table[:, 6] != 6))) != 0:
        raise AssertionError("geodesic interval full-sector flag mismatch")
    if int(np.count_nonzero((interval_table[:, 12] == 1) & (interval_table[:, 9] < HIGH_SIGNATURE_THRESHOLD))) != 0:
        raise AssertionError("geodesic interval high-signature flag mismatch")
    if int(np.count_nonzero(interval_table[:, 13] == 1)) != 46:
        raise AssertionError("geodesic interval full-high flag count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex", {}), REWRITE_COMPLEX_JSON, "rewrite complex input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(
        inputs.get("rewrite_complex_certificate", {}),
        REWRITE_COMPLEX_CERTIFICATE,
        "rewrite complex certificate input",
    )
    assert_file_hash(
        inputs.get("symbolic_rewrite_report", {}),
        SYMBOLIC_REWRITE_REPORT,
        "symbolic rewrite report input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_geodesic_interval_sheaf_manifest@1":
        raise AssertionError("C985 d20 geodesic interval sheaf manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 geodesic interval sheaf manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 geodesic interval sheaf manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 geodesic interval sheaf missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 geodesic interval sheaf index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 geodesic interval sheaf index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_geodesic_interval_sheaf@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "interval_count": witness.get("interval_count"),
        "high_signature_threshold": witness.get("high_signature_threshold"),
        "full_sector_preserving_interval_count": witness.get("full_sector_preserving_interval_count"),
        "high_signature_preserving_interval_count": witness.get("high_signature_preserving_interval_count"),
        "full_high_preserving_interval_count": witness.get("full_high_preserving_interval_count"),
        "longest_full_high_graph_distance": witness.get("longest_full_high_graph_distance"),
        "top_full_high_poincare_interval": witness.get("top_full_high_poincare_interval"),
        "poincare_diameter_interval": witness.get("poincare_diameter_interval"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_geodesic_interval_sheaf()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
