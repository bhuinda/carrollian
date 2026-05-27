from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry import (
        ANCHOR_NODE_COLUMNS,
        BRANCH_PROFILE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        COMPARISON_COLUMNS,
        DERIVE_SCRIPT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_BEST_STRONG_WORD,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SKIPPED_NODE_COLUMNS,
        STATUS,
        STRONGIFICATION_GAP_CERTIFICATE,
        STRONGIFICATION_GAP_JSON,
        STRONGIFICATION_GAP_REPORT,
        STRONGIFICATION_GAP_TABLES,
        STRONGIFICATION_GAP_WITNESSES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        row_trace,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry import (
        ANCHOR_NODE_COLUMNS,
        BRANCH_PROFILE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        COMPARISON_COLUMNS,
        DERIVE_SCRIPT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_BEST_STRONG_WORD,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SKIPPED_NODE_COLUMNS,
        STATUS,
        STRONGIFICATION_GAP_CERTIFICATE,
        STRONGIFICATION_GAP_JSON,
        STRONGIFICATION_GAP_REPORT,
        STRONGIFICATION_GAP_TABLES,
        STRONGIFICATION_GAP_WITNESSES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        row_trace,
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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def word_from_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS[: row["word_length"]])


def skipped_nodes_from_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[column]
        for column in SKIPPED_NODE_COLUMNS[: row["geodesic_skipped_node_count"]]
    )


def score_from_row(row: dict[str, int]) -> tuple[int, int, int, int]:
    return (
        row["trace_detour_overhead"],
        row["signature_valley_depth"],
        row["metric_gromov_delta_twice"],
        row["trace_signature_total_variation"],
    )


def validate_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    geometry = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate.json"
    )
    branch_profiles_csv = (
        OUT_DIR / "aperture_rank104_strongification_branch_profiles.csv"
    ).read_text(encoding="utf-8")
    branch_comparison_csv = (
        OUT_DIR / "aperture_rank104_strongification_branch_comparison.csv"
    ).read_text(encoding="utf-8")
    anchor_nodes_csv = (
        OUT_DIR / "aperture_rank104_strongification_anchor_nodes.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_rank104_strongification_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        geometry
        != expected[
            "signature_boundary_spine_aperture_rank104_strongification_branch_geometry"
        ]
    ):
        raise AssertionError("rank104 branch-geometry JSON is not reproducible")
    if (
        branch_profiles_csv
        != expected["aperture_rank104_strongification_branch_profiles_csv"]
    ):
        raise AssertionError("rank104 branch profiles CSV is not reproducible")
    if (
        branch_comparison_csv
        != expected["aperture_rank104_strongification_branch_comparison_csv"]
    ):
        raise AssertionError("rank104 branch comparison CSV is not reproducible")
    if anchor_nodes_csv != expected["aperture_rank104_strongification_anchor_nodes_csv"]:
        raise AssertionError("rank104 anchor nodes CSV is not reproducible")
    if observables_csv != expected["aperture_rank104_strongification_observables_csv"]:
        raise AssertionError("rank104 observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate"
        ]
    ):
        raise AssertionError("rank104 branch-geometry certificate is not reproducible")

    for name in [
        "branch_profile_table",
        "comparison_table",
        "anchor_node_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"rank104 branch-geometry table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry@1":
        raise AssertionError("rank104 branch-geometry report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("rank104 branch-geometry layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("rank104 branch-geometry all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("rank104 branch-geometry checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("rank104 branch-geometry report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("rank104 branch-geometry report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"rank104 branch-geometry missing true checks: {missing}")

    branch_table = np.asarray(tables["branch_profile_table"], dtype=np.int64)
    comparison_table = np.asarray(tables["comparison_table"], dtype=np.int64)
    anchor_table = np.asarray(tables["anchor_node_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if branch_table.shape != (2, len(BRANCH_PROFILE_COLUMNS)):
        raise AssertionError("rank104 branch profile table shape mismatch")
    if comparison_table.shape != (1, len(COMPARISON_COLUMNS)):
        raise AssertionError("rank104 comparison table shape mismatch")
    if anchor_table.shape != (6, len(ANCHOR_NODE_COLUMNS)):
        raise AssertionError("rank104 anchor table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("rank104 observable table shape mismatch")

    branch_rows = table_rows(branch_table, BRANCH_PROFILE_COLUMNS)
    comparison_rows = table_rows(comparison_table, COMPARISON_COLUMNS)
    anchor_rows = table_rows(anchor_table, ANCHOR_NODE_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)

    if [row["branch_id"] for row in branch_rows] != [0, 1]:
        raise AssertionError("rank104 branch ids mismatch")
    if [word_from_row(row) for row in branch_rows] != [
        (2, 1, 5, 2, 5, 4, 3),
        RANK104_BEST_STRONG_WORD,
    ]:
        raise AssertionError("rank104 branch words mismatch")
    if [row_trace(row) for row in branch_rows] != [
        (48, 42, 27, 29, 45, 44),
        (48, 42, 27, 31, 34, 29, 28, 34, 44),
    ]:
        raise AssertionError("rank104 branch traces mismatch")
    if [score_from_row(row) for row in branch_rows] != [
        (3, 37, 1, 169),
        (6, 37, 1, 143),
    ]:
        raise AssertionError("rank104 branch scores mismatch")
    if [row["closed_path_count"] for row in branch_rows] != [3, 8]:
        raise AssertionError("rank104 closed path counts mismatch")
    if [skipped_nodes_from_row(row) for row in branch_rows] != [
        (27, 29, 45),
        (27, 31, 34, 29, 28, 34),
    ]:
        raise AssertionError("rank104 skipped-node profiles mismatch")
    if any(
        row["strong_first_hit_flag"] != 1
        or row["shortcut_saved_edge_count"] != row["trace_detour_overhead"]
        for row in branch_rows
    ):
        raise AssertionError("rank104 strong branch shortcut invariant mismatch")

    comparison = comparison_rows[0]
    expected_comparison = {
        "common_prefix_node_count": 3,
        "common_suffix_node_count": 1,
        "source_divergent_node_count": 2,
        "target_divergent_node_count": 5,
        "trace_node_edit_distance": 4,
        "trace_edge_edit_distance": 6,
        "target_extra_trace_edge_count": 3,
        "target_overhead_gap": 3,
        "target_variation_advantage": 26,
        "same_valley_depth_flag": 1,
        "same_gromov_delta_flag": 1,
        "target_closed_path_advantage": 5,
        "source_divergent_node_0_id": 29,
        "source_divergent_node_1_id": 45,
        "target_divergent_node_0_id": 31,
        "target_divergent_node_1_id": 34,
        "target_divergent_node_2_id": 29,
        "target_divergent_node_3_id": 28,
        "target_divergent_node_4_id": 34,
    }
    for key, value in expected_comparison.items():
        if comparison[key] != value:
            raise AssertionError(f"rank104 comparison {key} mismatch")

    anchor_occurrences = {
        row["anchor_node_id"]: row["rank104_strong_occurrence_count"]
        for row in anchor_rows
    }
    if anchor_occurrences != {28: 1, 29: 1, 31: 1, 34: 2, 45: 0, 50: 0}:
        raise AssertionError("rank104 hybrid anchor occurrences mismatch")
    if Counter(row["node_role_code"] for row in anchor_rows) != Counter({2: 2, 0: 1, 1: 1, 3: 1, 4: 1}):
        raise AssertionError("rank104 hybrid anchor role codes mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES["branch_count"]: 2,
        OBSERVABLE_CODES["target1_trace_overhead"]: 3,
        OBSERVABLE_CODES["rank104_strong_trace_overhead"]: 6,
        OBSERVABLE_CODES["rank104_overhead_gap"]: 3,
        OBSERVABLE_CODES["target1_variation"]: 169,
        OBSERVABLE_CODES["rank104_strong_variation"]: 143,
        OBSERVABLE_CODES["rank104_variation_advantage"]: 26,
        OBSERVABLE_CODES["same_valley_depth_flag"]: 1,
        OBSERVABLE_CODES["same_gromov_delta_flag"]: 1,
        OBSERVABLE_CODES["target1_closed_path_count"]: 3,
        OBSERVABLE_CODES["rank104_closed_path_count"]: 8,
        OBSERVABLE_CODES["rank104_closed_path_advantage"]: 5,
        OBSERVABLE_CODES["target1_skipped_node_count"]: 3,
        OBSERVABLE_CODES["rank104_skipped_node_count"]: 6,
        OBSERVABLE_CODES["rank104_hybrid_anchor_node_count"]: 4,
    }
    if observables != expected_observables:
        raise AssertionError("rank104 observables mismatch")

    witness = report.get("witness", {})
    if witness.get("target1_branch", {}).get("score") != [3, 37, 1, 169]:
        raise AssertionError("rank104 target1 witness score mismatch")
    if witness.get("rank104_strongification_branch", {}).get("score") != [6, 37, 1, 143]:
        raise AssertionError("rank104 strongification witness score mismatch")
    if witness.get("rank104_strongification_branch", {}).get("trace") != [
        48,
        42,
        27,
        31,
        34,
        29,
        28,
        34,
        44,
    ]:
        raise AssertionError("rank104 strongification witness trace mismatch")
    if witness.get("anchor_node_occurrences") != {
        "28": 1,
        "29": 1,
        "31": 1,
        "34": 2,
        "45": 0,
        "50": 0,
    }:
        raise AssertionError("rank104 witness anchor occurrences mismatch")
    if witness.get("branch_table_sha256") != expected["report"]["witness"]["branch_table_sha256"]:
        raise AssertionError("rank104 branch table witness hash mismatch")
    if witness.get("comparison_table_sha256") != expected["report"]["witness"]["comparison_table_sha256"]:
        raise AssertionError("rank104 comparison table witness hash mismatch")
    if witness.get("anchor_table_sha256") != expected["report"]["witness"]["anchor_table_sha256"]:
        raise AssertionError("rank104 anchor table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("rank104 observable table witness hash mismatch")

    if geometry.get("summary", {}).get("rank104_strongification_score") != [6, 37, 1, 143]:
        raise AssertionError("rank104 geometry summary score mismatch")
    if geometry.get("summary", {}).get("rank104_variation_advantage") != 26:
        raise AssertionError("rank104 geometry summary variation mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("rank104 branch-geometry certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("strongification_gap_report", {}), STRONGIFICATION_GAP_REPORT, "strongification gap report input")
    assert_file_hash(inputs.get("strongification_gap_json", {}), STRONGIFICATION_GAP_JSON, "strongification gap JSON input")
    assert_file_hash(inputs.get("strongification_gap_witnesses", {}), STRONGIFICATION_GAP_WITNESSES, "strongification gap witnesses input")
    assert_file_hash(inputs.get("strongification_gap_tables", {}), STRONGIFICATION_GAP_TABLES, "strongification gap tables input")
    assert_file_hash(inputs.get("strongification_gap_certificate", {}), STRONGIFICATION_GAP_CERTIFICATE, "strongification gap certificate input")
    assert_file_hash(inputs.get("trace_quotient_report", {}), TRACE_QUOTIENT_REPORT, "trace quotient report input")
    assert_file_hash(inputs.get("trace_quotient_classes", {}), TRACE_QUOTIENT_CLASSES, "trace quotient classes input")
    assert_file_hash(inputs.get("trace_quotient_tables", {}), TRACE_QUOTIENT_TABLES, "trace quotient tables input")
    assert_file_hash(inputs.get("trace_quotient_certificate", {}), TRACE_QUOTIENT_CERTIFICATE, "trace quotient certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity tables input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry_manifest@1":
        raise AssertionError("rank104 branch-geometry manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("rank104 branch-geometry manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("rank104 branch-geometry manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("rank104 branch-geometry missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("rank104 branch-geometry index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("rank104 branch-geometry index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "target1_score": witness.get("target1_branch", {}).get("score"),
        "rank104_strongification_score": witness.get(
            "rank104_strongification_branch", {}
        ).get("score"),
        "comparison": witness.get("comparison"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
