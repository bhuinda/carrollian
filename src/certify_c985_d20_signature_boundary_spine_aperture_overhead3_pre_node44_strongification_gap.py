from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        ENDPOINT_HISTOGRAM_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_CLASS_COLUMNS,
        PREFIX_SYMBOL_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SEARCH_COST_COLUMNS,
        STATUS,
        STRONGIFICATION_WITNESS_COLUMNS,
        STRONG_WORD_SYMBOL_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_PROMOTION_CERTIFICATE,
        WEAK_PROMOTION_JSON,
        WEAK_PROMOTION_REPAIRS,
        WEAK_PROMOTION_REPORT,
        WEAK_PROMOTION_TABLES,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        ENDPOINT_HISTOGRAM_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_CLASS_COLUMNS,
        PREFIX_SYMBOL_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SEARCH_COST_COLUMNS,
        STATUS,
        STRONGIFICATION_WITNESS_COLUMNS,
        STRONG_WORD_SYMBOL_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WEAK_PROMOTION_CERTIFICATE,
        WEAK_PROMOTION_JSON,
        WEAK_PROMOTION_REPAIRS,
        WEAK_PROMOTION_REPORT,
        WEAK_PROMOTION_TABLES,
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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def strong_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[column] for column in STRONG_WORD_SYMBOL_COLUMNS[: row["strong_word_length"]]
    )


def prefix_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in PREFIX_SYMBOL_COLUMNS[: row["prefix_length"]])


def validate_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    strongification = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate.json"
    )
    prefix_classes_csv = (
        OUT_DIR / "aperture_overhead3_strongification_prefix_classes.csv"
    ).read_text(encoding="utf-8")
    search_costs_csv = (
        OUT_DIR / "aperture_overhead3_strongification_search_costs.csv"
    ).read_text(encoding="utf-8")
    witnesses_csv = (
        OUT_DIR / "aperture_overhead3_strongification_witnesses.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_overhead3_strongification_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        strongification
        != expected[
            "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap"
        ]
    ):
        raise AssertionError("pre-node44 strongification JSON is not reproducible")
    if (
        prefix_classes_csv
        != expected["aperture_overhead3_strongification_prefix_classes_csv"]
    ):
        raise AssertionError("pre-node44 prefix classes CSV is not reproducible")
    if (
        search_costs_csv
        != expected["aperture_overhead3_strongification_search_costs_csv"]
    ):
        raise AssertionError("pre-node44 search costs CSV is not reproducible")
    if witnesses_csv != expected["aperture_overhead3_strongification_witnesses_csv"]:
        raise AssertionError("pre-node44 witnesses CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_overhead3_strongification_observables_csv"]
    ):
        raise AssertionError("pre-node44 observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate"
        ]
    ):
        raise AssertionError("pre-node44 certificate is not reproducible")

    for name in [
        "prefix_class_table",
        "search_table",
        "strongification_witness_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"pre-node44 table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap@1":
        raise AssertionError("C985 d20 pre-node44 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 pre-node44 layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 pre-node44 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 pre-node44 checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 pre-node44 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 pre-node44 report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 pre-node44 missing true checks: {missing}")

    prefix_table = np.asarray(tables["prefix_class_table"], dtype=np.int64)
    search_table = np.asarray(tables["search_table"], dtype=np.int64)
    witness_table = np.asarray(tables["strongification_witness_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if prefix_table.shape != (2, len(PREFIX_CLASS_COLUMNS)):
        raise AssertionError("pre-node44 prefix class table shape mismatch")
    if search_table.shape != (8, len(SEARCH_COST_COLUMNS)):
        raise AssertionError("pre-node44 search table shape mismatch")
    if witness_table.shape != (24, len(STRONGIFICATION_WITNESS_COLUMNS)):
        raise AssertionError("pre-node44 witness table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("pre-node44 observable table shape mismatch")

    prefix_rows = table_rows(prefix_table, PREFIX_CLASS_COLUMNS)
    search_rows = table_rows(search_table, SEARCH_COST_COLUMNS)
    witness_rows = table_rows(witness_table, STRONGIFICATION_WITNESS_COLUMNS)

    if [row["member_candidate_count"] for row in prefix_rows] != [6, 1]:
        raise AssertionError("pre-node44 member collapse mismatch")
    if [prefix_word(row) for row in prefix_rows] != [
        (2, 1, 4, 5, 2),
        (2, 1, 3, 4, 5, 2),
    ]:
        raise AssertionError("pre-node44 prefix words mismatch")
    histograms = [
        [row[column] for column in ENDPOINT_HISTOGRAM_COLUMNS if row[column] > 0]
        for row in prefix_rows
    ]
    if histograms != [[6, 6, 4, 4, 4], [12, 12, 8, 8, 8]]:
        raise AssertionError("pre-node44 endpoint histograms mismatch")
    if any(
        prefix_rows[1][column] != 2 * prefix_rows[0][column]
        for column in ENDPOINT_HISTOGRAM_COLUMNS
    ):
        raise AssertionError("rank104 endpoint histogram is not double class0")
    if any(
        row["fixed_tail_substitution_strong_closed_hit_count"] != 0
        or row["unfixed_tail_substitution_strong_closed_hit_count"] != 0
        for row in prefix_rows
    ):
        raise AssertionError("pre-node44 substitution unexpectedly strongified")
    if [row["minimal_mixed_edit_cost"] for row in prefix_rows] != [3, 3]:
        raise AssertionError("pre-node44 minimal mixed edit cost mismatch")
    if [row["minimal_strongification_word_count"] for row in prefix_rows] != [10, 14]:
        raise AssertionError("pre-node44 minimal witness counts mismatch")

    hit_counts = {
        (row["prefix_class_id"], row["edit_cost"]): row["strong_closed_hit_count"]
        for row in search_rows
    }
    if any(hit_counts[(class_id, cost)] != 0 for class_id in [0, 1] for cost in [0, 1, 2]):
        raise AssertionError("pre-node44 cost below three has a hit")
    if hit_counts[(0, 3)] != 10 or hit_counts[(1, 3)] != 14:
        raise AssertionError("pre-node44 cost-three hit counts mismatch")
    candidate_counts = {
        (row["prefix_class_id"], row["edit_cost"]): row["unique_candidate_word_count"]
        for row in search_rows
    }
    if candidate_counts != {
        (0, 0): 1,
        (0, 1): 36,
        (0, 2): 597,
        (0, 3): 6401,
        (1, 0): 1,
        (1, 1): 46,
        (1, 2): 982,
        (1, 3): 13243,
    }:
        raise AssertionError("pre-node44 search candidate counts mismatch")

    best_rows = {
        row["prefix_class_id"]: row
        for row in witness_rows
        if row["best_score_flag"] == 1
    }
    if set(best_rows) != {0, 1}:
        raise AssertionError("pre-node44 best rows missing")
    if strong_word(best_rows[0]) != (2, 1, 4, 5, 1, 2, 0, 4, 5):
        raise AssertionError("class0 best strongification word mismatch")
    if strong_word(best_rows[1]) != (2, 1, 3, 4, 1, 5, 2, 1, 4, 5):
        raise AssertionError("rank104 best strongification word mismatch")
    if (
        best_rows[0]["trace_detour_overhead"],
        best_rows[0]["signature_valley_depth"],
        best_rows[0]["metric_gromov_delta_twice"],
        best_rows[0]["trace_signature_total_variation"],
    ) != (7, 45, 3, 205):
        raise AssertionError("class0 best score mismatch")
    if (
        best_rows[1]["trace_detour_overhead"],
        best_rows[1]["signature_valley_depth"],
        best_rows[1]["metric_gromov_delta_twice"],
        best_rows[1]["trace_signature_total_variation"],
    ) != (6, 37, 1, 143):
        raise AssertionError("rank104 best score mismatch")
    if Counter(row["prefix_class_id"] for row in witness_rows) != Counter({0: 10, 1: 14}):
        raise AssertionError("pre-node44 witness row distribution mismatch")

    witness = report.get("witness", {})
    if witness.get("best_strongification_words") != {
        "0": [2, 1, 4, 5, 1, 2, 0, 4, 5],
        "1": [2, 1, 3, 4, 1, 5, 2, 1, 4, 5],
    }:
        raise AssertionError("pre-node44 best word witness mismatch")
    if witness.get("prefix_class_table_sha256") != expected["report"]["witness"]["prefix_class_table_sha256"]:
        raise AssertionError("pre-node44 prefix table witness hash mismatch")
    if witness.get("search_table_sha256") != expected["report"]["witness"]["search_table_sha256"]:
        raise AssertionError("pre-node44 search table witness hash mismatch")
    if witness.get("witness_table_sha256") != expected["report"]["witness"]["witness_table_sha256"]:
        raise AssertionError("pre-node44 witness table hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("pre-node44 observable table hash mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("weak_promotion_report", {}), WEAK_PROMOTION_REPORT, "weak promotion report input")
    assert_file_hash(inputs.get("weak_promotion_json", {}), WEAK_PROMOTION_JSON, "weak promotion JSON input")
    assert_file_hash(inputs.get("weak_promotion_repairs", {}), WEAK_PROMOTION_REPAIRS, "weak promotion repairs input")
    assert_file_hash(inputs.get("weak_promotion_tables", {}), WEAK_PROMOTION_TABLES, "weak promotion tables input")
    assert_file_hash(inputs.get("weak_promotion_certificate", {}), WEAK_PROMOTION_CERTIFICATE, "weak promotion certificate input")
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_manifest@1":
        raise AssertionError("C985 d20 pre-node44 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 pre-node44 manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 pre-node44 manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 pre-node44 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 pre-node44 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 pre-node44 index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "prefix_classes": witness.get("prefix_classes"),
        "best_strongification_words": witness.get("best_strongification_words"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
