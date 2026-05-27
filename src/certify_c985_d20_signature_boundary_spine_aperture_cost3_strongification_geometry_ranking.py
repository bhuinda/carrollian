from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking import (
        BRANCH_PROFILE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLASS_SUMMARY_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_BEST_STRONG_WORD,
        RANK104_GEOMETRY_CERTIFICATE,
        RANK104_GEOMETRY_JSON,
        RANK104_GEOMETRY_REPORT,
        RANK104_GEOMETRY_TABLES,
        RANKING_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SCORE_COLUMNS,
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
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking import (
        BRANCH_PROFILE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLASS_SUMMARY_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_BEST_STRONG_WORD,
        RANK104_GEOMETRY_CERTIFICATE,
        RANK104_GEOMETRY_JSON,
        RANK104_GEOMETRY_REPORT,
        RANK104_GEOMETRY_TABLES,
        RANKING_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SCORE_COLUMNS,
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


def score_from_row(row: dict[str, int]) -> tuple[int, int, int, int]:
    return tuple(row[column] for column in SCORE_COLUMNS)  # type: ignore[return-value]


def word_from_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS[: row["word_length"]])


def validate_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    ranking_json = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate.json"
    )
    branch_profiles_csv = (
        OUT_DIR / "aperture_cost3_strongification_branch_profiles.csv"
    ).read_text(encoding="utf-8")
    rankings_csv = (OUT_DIR / "aperture_cost3_strongification_rankings.csv").read_text(
        encoding="utf-8"
    )
    class_summaries_csv = (
        OUT_DIR / "aperture_cost3_strongification_prefix_class_summaries.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_cost3_strongification_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        ranking_json
        != expected[
            "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking"
        ]
    ):
        raise AssertionError("cost3 strongification ranking JSON is not reproducible")
    if (
        branch_profiles_csv
        != expected["aperture_cost3_strongification_branch_profiles_csv"]
    ):
        raise AssertionError("cost3 branch profiles CSV is not reproducible")
    if rankings_csv != expected["aperture_cost3_strongification_rankings_csv"]:
        raise AssertionError("cost3 rankings CSV is not reproducible")
    if (
        class_summaries_csv
        != expected["aperture_cost3_strongification_prefix_class_summaries_csv"]
    ):
        raise AssertionError("cost3 class summaries CSV is not reproducible")
    if observables_csv != expected["aperture_cost3_strongification_observables_csv"]:
        raise AssertionError("cost3 observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate"
        ]
    ):
        raise AssertionError("cost3 ranking certificate is not reproducible")

    for name in [
        "branch_profile_table",
        "ranking_table",
        "class_summary_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"cost3 ranking table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking@1":
        raise AssertionError("cost3 ranking report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("cost3 ranking layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("cost3 ranking all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("cost3 ranking checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("cost3 ranking report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("cost3 ranking report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"cost3 ranking missing true checks: {missing}")

    branch_table = np.asarray(tables["branch_profile_table"], dtype=np.int64)
    ranking_table = np.asarray(tables["ranking_table"], dtype=np.int64)
    class_summary_table = np.asarray(tables["class_summary_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if branch_table.shape != (24, len(BRANCH_PROFILE_COLUMNS)):
        raise AssertionError("cost3 branch profile table shape mismatch")
    if ranking_table.shape != (24, len(RANKING_COLUMNS)):
        raise AssertionError("cost3 ranking table shape mismatch")
    if class_summary_table.shape != (2, len(CLASS_SUMMARY_COLUMNS)):
        raise AssertionError("cost3 class summary table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("cost3 observable table shape mismatch")

    branch_rows = table_rows(branch_table, BRANCH_PROFILE_COLUMNS)
    ranking_rows = table_rows(ranking_table, RANKING_COLUMNS)
    class_rows = table_rows(class_summary_table, CLASS_SUMMARY_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)

    if [row["global_rank"] for row in ranking_rows] != list(range(1, 25)):
        raise AssertionError("cost3 global ranks are not contiguous")
    if [row["strongification_witness_id"] for row in ranking_rows[:7]] != [
        17,
        14,
        15,
        12,
        16,
        11,
        6,
    ]:
        raise AssertionError("cost3 top-seven ranking mismatch")

    best = ranking_rows[0]
    if best["strongification_witness_id"] != 17:
        raise AssertionError("cost3 global best witness mismatch")
    if best["prefix_class_id"] != 1 or best["prefix_class_rank"] != 1:
        raise AssertionError("cost3 global best class rank mismatch")
    if word_from_row(best) != RANK104_BEST_STRONG_WORD:
        raise AssertionError("cost3 global best word mismatch")
    if score_from_row(best) != (6, 37, 1, 143):
        raise AssertionError("cost3 global best score mismatch")
    if best["closed_path_count"] != 8:
        raise AssertionError("cost3 global best closed path count mismatch")
    if best["score_pareto_flag"] != 1 or best["closure_augmented_pareto_flag"] != 1:
        raise AssertionError("cost3 rank104 Pareto flags mismatch")

    branch_by_id = {row["branch_id"]: row for row in branch_rows}
    if row_trace(branch_by_id[17]) != (48, 42, 27, 31, 34, 29, 28, 34, 44):
        raise AssertionError("cost3 rank104 branch trace mismatch")
    if Counter(row["prefix_class_id"] for row in ranking_rows) != Counter({0: 10, 1: 14}):
        raise AssertionError("cost3 prefix-class witness distribution mismatch")

    score_pareto_ids = [
        row["strongification_witness_id"]
        for row in ranking_rows
        if row["score_pareto_flag"] == 1
    ]
    closure_pareto_ids = [
        row["strongification_witness_id"]
        for row in ranking_rows
        if row["closure_augmented_pareto_flag"] == 1
    ]
    if score_pareto_ids != [17]:
        raise AssertionError("cost3 score Pareto frontier mismatch")
    if closure_pareto_ids != [17, 9, 23]:
        raise AssertionError("cost3 closure-augmented Pareto frontier mismatch")

    if [row["lexicographic_best_witness_id"] for row in class_rows] != [6, 17]:
        raise AssertionError("cost3 class best witness ids mismatch")
    if [row["lexicographic_best_global_rank"] for row in class_rows] != [7, 1]:
        raise AssertionError("cost3 class best global ranks mismatch")
    if [row["witness_count"] for row in class_rows] != [10, 14]:
        raise AssertionError("cost3 class witness counts mismatch")
    if [row["score_pareto_count"] for row in class_rows] != [0, 1]:
        raise AssertionError("cost3 class score Pareto counts mismatch")
    if [row["closure_augmented_pareto_count"] for row in class_rows] != [1, 2]:
        raise AssertionError("cost3 class closure Pareto counts mismatch")
    if [row["max_closed_path_count"] for row in class_rows] != [12, 24]:
        raise AssertionError("cost3 class max closure counts mismatch")

    closed24 = sorted(
        row["strongification_witness_id"]
        for row in ranking_rows
        if row["closed_path_count"] == 24
    )
    if closed24 != [22, 23]:
        raise AssertionError("cost3 max-closure witness ids mismatch")
    if next(row for row in ranking_rows if row["strongification_witness_id"] == 23)[
        "closure_augmented_pareto_flag"
    ] != 1:
        raise AssertionError("cost3 witness23 closure Pareto flag mismatch")
    if next(row for row in ranking_rows if row["strongification_witness_id"] == 22)[
        "closure_augmented_pareto_flag"
    ] != 0:
        raise AssertionError("cost3 witness22 closure Pareto flag mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES["cost3_witness_count"]: 24,
        OBSERVABLE_CODES["prefix_class_count"]: 2,
        OBSERVABLE_CODES["score_pareto_count"]: 1,
        OBSERVABLE_CODES["closure_augmented_pareto_count"]: 3,
        OBSERVABLE_CODES["rank104_witness_id"]: 17,
        OBSERVABLE_CODES["rank104_global_rank"]: 1,
        OBSERVABLE_CODES["rank104_score_pareto_flag"]: 1,
        OBSERVABLE_CODES["rank104_closure_augmented_pareto_flag"]: 1,
        OBSERVABLE_CODES["class0_best_witness_id"]: 6,
        OBSERVABLE_CODES["class1_best_witness_id"]: 17,
        OBSERVABLE_CODES["class0_best_global_rank"]: 7,
        OBSERVABLE_CODES["class1_best_global_rank"]: 1,
        OBSERVABLE_CODES["closure_augmented_extra_pareto_count"]: 2,
        OBSERVABLE_CODES["max_closed_path_count"]: 24,
        OBSERVABLE_CODES["max_closed_path_best_witness_id"]: 23,
        OBSERVABLE_CODES["rank104_unique_score_pareto_flag"]: 1,
        OBSERVABLE_CODES["rank104_global_not_merely_class_flag"]: 1,
    }
    if observables != expected_observables:
        raise AssertionError("cost3 observables mismatch")

    witness = report.get("witness", {})
    if witness.get("global_best", {}).get("witness_id") != 17:
        raise AssertionError("cost3 global best witness mismatch")
    if witness.get("score_pareto_witness_ids") != [17]:
        raise AssertionError("cost3 witness score Pareto ids mismatch")
    if witness.get("closure_augmented_pareto_witness_ids") != [17, 9, 23]:
        raise AssertionError("cost3 witness closure Pareto ids mismatch")
    if witness.get("prefix_class_best_witness_ids") != {"0": 6, "1": 17}:
        raise AssertionError("cost3 witness class best ids mismatch")
    if witness.get("closure_augmented_extra_pareto_witness_ids") != [9, 23]:
        raise AssertionError("cost3 witness closure outlier ids mismatch")
    if sorted(witness.get("max_closed_path_witness_ids", [])) != [22, 23]:
        raise AssertionError("cost3 witness max-closure ids mismatch")
    if witness.get("branch_profile_table_sha256") != expected["report"]["witness"]["branch_profile_table_sha256"]:
        raise AssertionError("cost3 branch table witness hash mismatch")
    if witness.get("ranking_table_sha256") != expected["report"]["witness"]["ranking_table_sha256"]:
        raise AssertionError("cost3 ranking table witness hash mismatch")
    if witness.get("class_summary_table_sha256") != expected["report"]["witness"]["class_summary_table_sha256"]:
        raise AssertionError("cost3 class summary table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("cost3 observable table witness hash mismatch")

    if ranking_json.get("summary", {}).get("score_pareto_witness_ids") != [17]:
        raise AssertionError("cost3 ranking summary score frontier mismatch")
    if ranking_json.get("summary", {}).get("closure_augmented_pareto_witness_ids") != [17, 9, 23]:
        raise AssertionError("cost3 ranking summary closure frontier mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("cost3 ranking certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("strongification_gap_report", {}), STRONGIFICATION_GAP_REPORT, "strongification gap report input")
    assert_file_hash(inputs.get("strongification_gap_json", {}), STRONGIFICATION_GAP_JSON, "strongification gap JSON input")
    assert_file_hash(inputs.get("strongification_gap_witnesses", {}), STRONGIFICATION_GAP_WITNESSES, "strongification gap witnesses input")
    assert_file_hash(inputs.get("strongification_gap_tables", {}), STRONGIFICATION_GAP_TABLES, "strongification gap tables input")
    assert_file_hash(inputs.get("strongification_gap_certificate", {}), STRONGIFICATION_GAP_CERTIFICATE, "strongification gap certificate input")
    assert_file_hash(inputs.get("rank104_geometry_report", {}), RANK104_GEOMETRY_REPORT, "rank104 geometry report input")
    assert_file_hash(inputs.get("rank104_geometry_json", {}), RANK104_GEOMETRY_JSON, "rank104 geometry JSON input")
    assert_file_hash(inputs.get("rank104_geometry_tables", {}), RANK104_GEOMETRY_TABLES, "rank104 geometry tables input")
    assert_file_hash(inputs.get("rank104_geometry_certificate", {}), RANK104_GEOMETRY_CERTIFICATE, "rank104 geometry certificate input")
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_manifest@1":
        raise AssertionError("cost3 ranking manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("cost3 ranking manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("cost3 ranking manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("cost3 ranking missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("cost3 ranking index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("cost3 ranking index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "global_best": witness.get("global_best"),
        "score_pareto_witness_ids": witness.get("score_pareto_witness_ids"),
        "closure_augmented_pareto_witness_ids": witness.get(
            "closure_augmented_pareto_witness_ids"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
