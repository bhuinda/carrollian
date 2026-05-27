from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        EDIT_REPAIR_CANDIDATES,
        EDIT_REPAIR_CERTIFICATE,
        EDIT_REPAIR_JSON,
        EDIT_REPAIR_REPORT,
        EDIT_REPAIR_TABLES,
        EXISTING_POST44_SYMBOL_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_SYMBOL_COLUMNS,
        PROMOTION_REPAIR_COLUMNS,
        PROMOTION_SUFFIX_COLUMNS,
        RANK104_CERTIFICATE,
        RANK104_REPORT,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOL_COLUMNS,
        THEOREM_ID,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_JSON,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        EDIT_REPAIR_CANDIDATES,
        EDIT_REPAIR_CERTIFICATE,
        EDIT_REPAIR_JSON,
        EDIT_REPAIR_REPORT,
        EDIT_REPAIR_TABLES,
        EXISTING_POST44_SYMBOL_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_SYMBOL_COLUMNS,
        PROMOTION_REPAIR_COLUMNS,
        PROMOTION_SUFFIX_COLUMNS,
        RANK104_CERTIFICATE,
        RANK104_REPORT,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOL_COLUMNS,
        THEOREM_ID,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_JSON,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        VALIDATOR_SCRIPT,
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


def row_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[column] for column in SYMBOL_COLUMNS[: row["word_length"]]
    )


def row_prefix(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[column] for column in PREFIX_SYMBOL_COLUMNS[: row["promotion_prefix_length"]]
    )


def row_existing_post44(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[column]
        for column in EXISTING_POST44_SYMBOL_COLUMNS[
            : row["existing_post_node44_suffix_length"]
        ]
    )


def row_promotion_suffix(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[column]
        for column in PROMOTION_SUFFIX_COLUMNS[
            : max(row["minimal_promotion_suffix_length"], 0)
        ]
    )


def validate_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    audit = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate.json"
    )
    repairs_csv = (OUT_DIR / "aperture_overhead3_weak_promotion_repairs.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_overhead3_weak_promotion_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        audit
        != expected["signature_boundary_spine_aperture_overhead3_weak_promotion_audit"]
    ):
        raise AssertionError("weak promotion audit JSON is not reproducible")
    if repairs_csv != expected["aperture_overhead3_weak_promotion_repairs_csv"]:
        raise AssertionError("weak promotion repairs CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_overhead3_weak_promotion_observables_csv"]
    ):
        raise AssertionError("weak promotion observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate"
        ]
    ):
        raise AssertionError("weak promotion audit certificate is not reproducible")

    for name in ["promotion_repair_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"weak promotion table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit@1":
        raise AssertionError("C985 d20 weak promotion report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 weak promotion layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 weak promotion all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 weak promotion checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 weak promotion report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 weak promotion report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 weak promotion missing true checks: {missing}")

    promotion_table = np.asarray(tables["promotion_repair_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if promotion_table.shape != (8, len(PROMOTION_REPAIR_COLUMNS)):
        raise AssertionError("weak promotion repair table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("weak promotion observable table shape mismatch")

    rows = table_rows(promotion_table, PROMOTION_REPAIR_COLUMNS)
    if [row["edit_repair_candidate_id"] for row in rows] != [20, 263, 264, 265, 270, 273, 104, 544]:
        raise AssertionError("weak promotion selected candidate ids mismatch")
    if Counter(row["trace_class_id"] for row in rows) != Counter({0: 6, 1: 1, 2: 1}):
        raise AssertionError("weak promotion trace class distribution mismatch")
    if [row["bounded_match_count"] for row in rows] != [2, 4, 4, 18, 4, 10, 4, 3]:
        raise AssertionError("weak promotion bounded match counts mismatch")
    if sum(row["bounded_match_count"] for row in rows) != 49:
        raise AssertionError("weak promotion bounded match total mismatch")

    nonstrong_rows = [row for row in rows if row["nonstrong_weak_flag"] == 1]
    strong_rows = [row for row in rows if row["pre_aperture_strong_flag"] == 1]
    if len(nonstrong_rows) != 7:
        raise AssertionError("weak promotion nonstrong row count mismatch")
    if len(strong_rows) != 1 or strong_rows[0]["edit_repair_candidate_id"] != 544:
        raise AssertionError("weak promotion strong target1 row mismatch")
    if any(row["target_word_id"] != 0 for row in nonstrong_rows):
        raise AssertionError("weak promotion nonstrong rows should all target word 0")
    if strong_rows[0]["target_word_id"] != 1:
        raise AssertionError("weak promotion strong row should target word 1")
    if sum(row["nonminimal_weak_flag"] for row in nonstrong_rows) != 6:
        raise AssertionError("weak promotion nonminimal nonstrong count mismatch")

    for row in nonstrong_rows:
        if row["minimal_promotion_suffix_length"] != 1:
            raise AssertionError("nonstrong promotion length is not one")
        if row_promotion_suffix(row) != (5,):
            raise AssertionError("nonstrong promotion suffix is not x5")
        if row["promotion_target_consumed_flag"] != 1:
            raise AssertionError("nonstrong promotion does not consume target")
        if row["promotion_closes_to_origin_flag"] != 1:
            raise AssertionError("nonstrong promotion does not close to origin")
        if row["post_suffix_can_make_pre_aperture_strong_flag"] != 0:
            raise AssertionError("post-node44 suffix unexpectedly strongifies row")
        prefix = row_prefix(row)
        existing = row_existing_post44(row)
        if row_word(row) != (*prefix, *existing):
            raise AssertionError("weak promotion prefix/post-node44 split mismatch")

    if row_promotion_suffix(strong_rows[0]) != (3,):
        raise AssertionError("strong target1 row should close with x3")
    if strong_rows[0]["minimal_promotion_suffix_length"] != 1:
        raise AssertionError("strong target1 promotion length mismatch")
    if strong_rows[0]["promotion_closed_path_count"] != 3:
        raise AssertionError("strong target1 closed path count mismatch")

    expected_closure_counts = {
        20: 4,
        263: 4,
        264: 4,
        265: 4,
        270: 4,
        273: 4,
        104: 8,
        544: 3,
    }
    actual_closure_counts = {
        row["edit_repair_candidate_id"]: row["promotion_closed_path_count"]
        for row in rows
    }
    if actual_closure_counts != expected_closure_counts:
        raise AssertionError("weak promotion closed path counts mismatch")
    if sum(row["existing_post44_suffix_strictly_longer_than_min_flag"] for row in rows) != 5:
        raise AssertionError("weak promotion existing suffix improvement count mismatch")

    witness = report.get("witness", {})
    if witness.get("selected_edit_repair_candidate_ids") != [20, 263, 264, 265, 270, 273, 104, 544]:
        raise AssertionError("weak promotion selected id witness mismatch")
    if witness.get("trace_class_distribution") != {"0": 6, "1": 1, "2": 1}:
        raise AssertionError("weak promotion class distribution witness mismatch")
    if witness.get("promotion_table_sha256") != expected["report"]["witness"]["promotion_table_sha256"]:
        raise AssertionError("weak promotion table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("weak promotion observable witness hash mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("trace_quotient_report", {}), TRACE_QUOTIENT_REPORT, "trace quotient report input")
    assert_file_hash(inputs.get("trace_quotient_json", {}), TRACE_QUOTIENT_JSON, "trace quotient JSON input")
    assert_file_hash(inputs.get("trace_quotient_classes", {}), TRACE_QUOTIENT_CLASSES, "trace quotient classes input")
    assert_file_hash(inputs.get("trace_quotient_tables", {}), TRACE_QUOTIENT_TABLES, "trace quotient tables input")
    assert_file_hash(inputs.get("trace_quotient_certificate", {}), TRACE_QUOTIENT_CERTIFICATE, "trace quotient certificate input")
    assert_file_hash(inputs.get("rank104_report", {}), RANK104_REPORT, "rank104 report input")
    assert_file_hash(inputs.get("rank104_certificate", {}), RANK104_CERTIFICATE, "rank104 certificate input")
    assert_file_hash(inputs.get("bounded_backtrack_candidates", {}), BOUNDED_BACKTRACK_CANDIDATES, "bounded backtrack candidates input")
    assert_file_hash(inputs.get("bounded_backtrack_tables", {}), BOUNDED_BACKTRACK_TABLES, "bounded backtrack tables input")
    assert_file_hash(inputs.get("edit_repair_report", {}), EDIT_REPAIR_REPORT, "edit repair report input")
    assert_file_hash(inputs.get("edit_repair_json", {}), EDIT_REPAIR_JSON, "edit repair JSON input")
    assert_file_hash(inputs.get("edit_repair_candidates", {}), EDIT_REPAIR_CANDIDATES, "edit repair candidates input")
    assert_file_hash(inputs.get("edit_repair_tables", {}), EDIT_REPAIR_TABLES, "edit repair tables input")
    assert_file_hash(inputs.get("edit_repair_certificate", {}), EDIT_REPAIR_CERTIFICATE, "edit repair certificate input")
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit_manifest@1":
        raise AssertionError("C985 d20 weak promotion manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 weak promotion manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 weak promotion manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 weak promotion missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 weak promotion index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 weak promotion index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "selected_edit_repair_candidate_ids": witness.get(
            "selected_edit_repair_candidate_ids"
        ),
        "promotion_suffix_by_candidate": witness.get(
            "promotion_suffix_by_candidate"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
