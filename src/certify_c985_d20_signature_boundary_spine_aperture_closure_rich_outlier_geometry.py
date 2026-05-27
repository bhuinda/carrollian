from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry import (
        COST3_RANKING_BRANCH_PROFILES,
        COST3_RANKING_CERTIFICATE,
        COST3_RANKING_JSON,
        COST3_RANKING_RANKINGS,
        COST3_RANKING_REPORT,
        COST3_RANKING_TABLES,
        DIVERGENT_OUTLIER_COLUMNS,
        DIVERGENT_SOURCE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        OUTLIER_PAIR_COLUMNS,
        REFERENCE_COMPARISON_COLUMNS,
        SCORE_COLUMNS,
        SELECTED_BRANCH_COLUMNS,
        SHARED_CLOSURE_TAIL,
        STATUS,
        TAIL_NODE_COLUMNS,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        row_trace,
        row_word,
        score,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry import (
        COST3_RANKING_BRANCH_PROFILES,
        COST3_RANKING_CERTIFICATE,
        COST3_RANKING_JSON,
        COST3_RANKING_RANKINGS,
        COST3_RANKING_REPORT,
        COST3_RANKING_TABLES,
        DIVERGENT_OUTLIER_COLUMNS,
        DIVERGENT_SOURCE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        OUTLIER_PAIR_COLUMNS,
        REFERENCE_COMPARISON_COLUMNS,
        SCORE_COLUMNS,
        SELECTED_BRANCH_COLUMNS,
        SHARED_CLOSURE_TAIL,
        STATUS,
        TAIL_NODE_COLUMNS,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        WORD_COLUMNS,
        build_payloads,
        row_trace,
        row_word,
        score,
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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def validate_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    geometry = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_rich_outlier_geometry.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate.json"
    )
    selected_csv = (
        OUT_DIR / "aperture_closure_outlier_selected_branches.csv"
    ).read_text(encoding="utf-8")
    comparisons_csv = (
        OUT_DIR / "aperture_closure_outlier_reference_comparisons.csv"
    ).read_text(encoding="utf-8")
    pair_csv = (OUT_DIR / "aperture_closure_outlier_pair_comparison.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_closure_outlier_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        geometry
        != expected[
            "signature_boundary_spine_aperture_closure_rich_outlier_geometry"
        ]
    ):
        raise AssertionError("closure outlier geometry JSON is not reproducible")
    if selected_csv != expected["aperture_closure_outlier_selected_branches_csv"]:
        raise AssertionError("closure outlier selected branches CSV is not reproducible")
    if (
        comparisons_csv
        != expected["aperture_closure_outlier_reference_comparisons_csv"]
    ):
        raise AssertionError("closure outlier comparisons CSV is not reproducible")
    if pair_csv != expected["aperture_closure_outlier_pair_comparison_csv"]:
        raise AssertionError("closure outlier pair CSV is not reproducible")
    if observables_csv != expected["aperture_closure_outlier_observables_csv"]:
        raise AssertionError("closure outlier observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate"
        ]
    ):
        raise AssertionError("closure outlier certificate is not reproducible")

    for name in [
        "selected_branch_table",
        "comparison_table",
        "pair_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"closure outlier table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry@1":
        raise AssertionError("closure outlier report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("closure outlier layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("closure outlier all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("closure outlier checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure outlier report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("closure outlier report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"closure outlier missing true checks: {missing}")

    selected_table = np.asarray(tables["selected_branch_table"], dtype=np.int64)
    comparison_table = np.asarray(tables["comparison_table"], dtype=np.int64)
    pair_table = np.asarray(tables["pair_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if selected_table.shape != (3, len(SELECTED_BRANCH_COLUMNS)):
        raise AssertionError("closure outlier selected table shape mismatch")
    if comparison_table.shape != (2, len(REFERENCE_COMPARISON_COLUMNS)):
        raise AssertionError("closure outlier comparison table shape mismatch")
    if pair_table.shape != (1, len(OUTLIER_PAIR_COLUMNS)):
        raise AssertionError("closure outlier pair table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("closure outlier observable table shape mismatch")

    selected_rows = table_rows(selected_table, SELECTED_BRANCH_COLUMNS)
    comparison_rows = table_rows(comparison_table, REFERENCE_COMPARISON_COLUMNS)
    pair_rows = table_rows(pair_table, OUTLIER_PAIR_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)

    if [row["witness_id"] for row in selected_rows] != [17, 9, 23]:
        raise AssertionError("closure outlier selected witness ids mismatch")
    if [row["role_code"] for row in selected_rows] != [0, 1, 1]:
        raise AssertionError("closure outlier selected roles mismatch")
    if [score(row) for row in selected_rows] != [
        (6, 37, 1, 143),
        (8, 49, 2, 213),
        (8, 49, 4, 161),
    ]:
        raise AssertionError("closure outlier selected scores mismatch")
    if [row["closed_path_count"] for row in selected_rows] != [8, 12, 24]:
        raise AssertionError("closure outlier selected closure counts mismatch")
    if [row["score_pareto_flag"] for row in selected_rows] != [1, 0, 0]:
        raise AssertionError("closure outlier score Pareto flags mismatch")
    if [row["closure_augmented_pareto_flag"] for row in selected_rows] != [1, 1, 1]:
        raise AssertionError("closure outlier closure Pareto flags mismatch")
    if [row["shared_closure_tail_flag"] for row in selected_rows] != [0, 1, 1]:
        raise AssertionError("closure outlier shared-tail flags mismatch")
    if [row["shared_closure_tail_start_index"] for row in selected_rows] != [-1, 5, 5]:
        raise AssertionError("closure outlier shared-tail start mismatch")
    if [row_trace(row) for row in selected_rows] != [
        (48, 42, 27, 31, 34, 29, 28, 34, 44),
        (48, 42, 27, 28, 34, 54, 45, 29, 28, 34, 44),
        (48, 42, 27, 31, 50, 54, 45, 29, 28, 34, 44),
    ]:
        raise AssertionError("closure outlier selected traces mismatch")
    if [row_word(row) for row in selected_rows] != [
        (2, 1, 3, 4, 1, 5, 2, 1, 4, 5),
        (2, 1, 4, 5, 5, 2, 1, 4, 5),
        (2, 1, 3, 4, 5, 5, 2, 1, 4, 5),
    ]:
        raise AssertionError("closure outlier selected words mismatch")

    expected_comparisons = {
        9: {
            "outlier_closed_path_gain": 4,
            "outlier_overhead_penalty": 2,
            "outlier_valley_penalty": 12,
            "outlier_delta_penalty": 1,
            "outlier_variation_penalty": 70,
            "closure_gain_per_overhead_x1e6": 2000000,
            "closure_gain_per_variation_x1e6": 57142,
            "common_prefix_node_count": 3,
            "common_suffix_node_count": 4,
            "reference_divergent_node_count": 2,
            "outlier_divergent_node_count": 4,
            "trace_node_edit_distance": 3,
            "trace_edge_edit_distance": 5,
            "source_divergent": (31, 34, -1, -1),
            "outlier_divergent": (28, 34, 54, 45),
        },
        23: {
            "outlier_closed_path_gain": 16,
            "outlier_overhead_penalty": 2,
            "outlier_valley_penalty": 12,
            "outlier_delta_penalty": 3,
            "outlier_variation_penalty": 18,
            "closure_gain_per_overhead_x1e6": 8000000,
            "closure_gain_per_variation_x1e6": 888888,
            "common_prefix_node_count": 4,
            "common_suffix_node_count": 4,
            "reference_divergent_node_count": 1,
            "outlier_divergent_node_count": 3,
            "trace_node_edit_distance": 3,
            "trace_edge_edit_distance": 4,
            "source_divergent": (34, -1, -1, -1),
            "outlier_divergent": (50, 54, 45, -1),
        },
    }
    for row in comparison_rows:
        expected_row = expected_comparisons[row["outlier_witness_id"]]
        for key, value in expected_row.items():
            if key == "source_divergent":
                got = tuple(row[column] for column in DIVERGENT_SOURCE_COLUMNS)
            elif key == "outlier_divergent":
                got = tuple(row[column] for column in DIVERGENT_OUTLIER_COLUMNS)
            else:
                got = row[key]
            if got != value:
                raise AssertionError(f"closure outlier comparison {key} mismatch")
        if row["outlier_shared_closure_tail_flag"] != 1:
            raise AssertionError("closure outlier comparison shared tail flag mismatch")

    pair = pair_rows[0]
    if pair["baseline_class_outlier_witness_id"] != 9 or pair["rank104_class_outlier_witness_id"] != 23:
        raise AssertionError("closure outlier pair witness ids mismatch")
    if (
        pair["common_prefix_node_count"],
        pair["common_suffix_node_count"],
        pair["baseline_divergent_node_count"],
        pair["rank104_divergent_node_count"],
        pair["trace_node_edit_distance"],
        pair["trace_edge_edit_distance"],
        pair["rank104_outlier_closed_path_gain"],
        pair["rank104_outlier_variation_advantage"],
        pair["rank104_outlier_delta_penalty"],
    ) != (3, 6, 2, 2, 2, 3, 12, 52, 2):
        raise AssertionError("closure outlier pair metrics mismatch")
    if tuple(pair[column] for column in TAIL_NODE_COLUMNS) != SHARED_CLOSURE_TAIL:
        raise AssertionError("closure outlier pair shared tail mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES["selected_branch_count"]: 3,
        OBSERVABLE_CODES["closure_outlier_count"]: 2,
        OBSERVABLE_CODES["shared_closure_tail_node_count"]: 6,
        OBSERVABLE_CODES["reference_witness_id"]: 17,
        OBSERVABLE_CODES["baseline_outlier_witness_id"]: 9,
        OBSERVABLE_CODES["rank104_outlier_witness_id"]: 23,
        OBSERVABLE_CODES["baseline_outlier_closed_gain"]: 4,
        OBSERVABLE_CODES["rank104_outlier_closed_gain"]: 16,
        OBSERVABLE_CODES["common_outlier_overhead_penalty"]: 2,
        OBSERVABLE_CODES["common_outlier_valley_penalty"]: 12,
        OBSERVABLE_CODES["rank104_outlier_extra_closed_gain_over_baseline"]: 12,
        OBSERVABLE_CODES["rank104_outlier_variation_advantage_over_baseline"]: 52,
        OBSERVABLE_CODES["rank104_outlier_delta_penalty_over_baseline"]: 2,
        OBSERVABLE_CODES["outlier_pair_common_suffix_node_count"]: 6,
        OBSERVABLE_CODES["reference_score_pareto_flag"]: 1,
        OBSERVABLE_CODES["outlier_score_pareto_count"]: 0,
        OBSERVABLE_CODES["outlier_closure_augmented_pareto_count"]: 2,
    }
    if observables != expected_observables:
        raise AssertionError("closure outlier observables mismatch")

    witness = report.get("witness", {})
    if witness.get("reference", {}).get("witness_id") != 17:
        raise AssertionError("closure outlier witness reference mismatch")
    if [row.get("witness_id") for row in witness.get("closure_outliers", [])] != [9, 23]:
        raise AssertionError("closure outlier witness ids mismatch")
    if witness.get("outlier_pair_comparison", {}).get("common_suffix_node_count") != 6:
        raise AssertionError("closure outlier witness pair suffix mismatch")
    if witness.get("selected_table_sha256") != expected["report"]["witness"]["selected_table_sha256"]:
        raise AssertionError("closure outlier selected table hash mismatch")
    if witness.get("comparison_table_sha256") != expected["report"]["witness"]["comparison_table_sha256"]:
        raise AssertionError("closure outlier comparison table hash mismatch")
    if witness.get("pair_table_sha256") != expected["report"]["witness"]["pair_table_sha256"]:
        raise AssertionError("closure outlier pair table hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("closure outlier observable table hash mismatch")

    if geometry.get("summary", {}).get("closure_outlier_witness_ids") != [9, 23]:
        raise AssertionError("closure outlier geometry summary ids mismatch")
    if geometry.get("summary", {}).get("shared_closure_tail") != list(SHARED_CLOSURE_TAIL):
        raise AssertionError("closure outlier geometry summary tail mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("closure outlier certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("cost3_ranking_report", {}), COST3_RANKING_REPORT, "cost3 ranking report input")
    assert_file_hash(inputs.get("cost3_ranking_json", {}), COST3_RANKING_JSON, "cost3 ranking JSON input")
    assert_file_hash(inputs.get("cost3_ranking_branch_profiles", {}), COST3_RANKING_BRANCH_PROFILES, "cost3 branch profiles input")
    assert_file_hash(inputs.get("cost3_ranking_rankings", {}), COST3_RANKING_RANKINGS, "cost3 rankings input")
    assert_file_hash(inputs.get("cost3_ranking_tables", {}), COST3_RANKING_TABLES, "cost3 ranking tables input")
    assert_file_hash(inputs.get("cost3_ranking_certificate", {}), COST3_RANKING_CERTIFICATE, "cost3 ranking certificate input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry_manifest@1":
        raise AssertionError("closure outlier manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure outlier manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("closure outlier manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("closure outlier missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure outlier index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("closure outlier index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "reference": witness.get("reference"),
        "closure_outliers": witness.get("closure_outliers"),
        "outlier_pair_comparison": witness.get("outlier_pair_comparison"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
