from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        CLOSED_REPAIR_CERTIFICATE,
        CLOSED_REPAIR_REPORT,
        DERIVE_SCRIPT,
        EDIT_REPAIR_CANDIDATES,
        EDIT_REPAIR_CERTIFICATE,
        EDIT_REPAIR_REPORT,
        EDIT_REPAIR_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_PATH_COLUMNS,
        THEOREM_ID,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_JSON,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        VALIDATOR_SCRIPT,
        WORD_AUDIT_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        CLOSED_REPAIR_CERTIFICATE,
        CLOSED_REPAIR_REPORT,
        DERIVE_SCRIPT,
        EDIT_REPAIR_CANDIDATES,
        EDIT_REPAIR_CERTIFICATE,
        EDIT_REPAIR_REPORT,
        EDIT_REPAIR_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        TARGET_PATH_COLUMNS,
        THEOREM_ID,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_JSON,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        VALIDATOR_SCRIPT,
        WORD_AUDIT_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    audit = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_rank104_branch_audit.json"
    )
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_rank104_branch_audit_certificate.json"
    )
    word_audit_csv = (OUT_DIR / "aperture_rank104_word_audit.csv").read_text(
        encoding="utf-8"
    )
    target_paths_csv = (OUT_DIR / "aperture_rank104_target_paths.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "aperture_rank104_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_rank104_branch_audit_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if audit != expected["signature_boundary_spine_aperture_rank104_branch_audit"]:
        raise AssertionError("rank104 branch audit JSON is not reproducible")
    if word_audit_csv != expected["aperture_rank104_word_audit_csv"]:
        raise AssertionError("rank104 word audit CSV is not reproducible")
    if target_paths_csv != expected["aperture_rank104_target_paths_csv"]:
        raise AssertionError("rank104 target paths CSV is not reproducible")
    if observables_csv != expected["aperture_rank104_observables_csv"]:
        raise AssertionError("rank104 observables CSV is not reproducible")
    if (
        certificate
        != expected["signature_boundary_spine_aperture_rank104_branch_audit_certificate"]
    ):
        raise AssertionError("rank104 branch audit certificate is not reproducible")

    for name in ["word_audit_table", "target_path_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"rank104 branch audit table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_branch_audit@1":
        raise AssertionError("C985 d20 rank104 branch audit report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 rank104 branch audit layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 rank104 branch audit all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 rank104 branch audit checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 rank104 branch audit report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 rank104 branch audit report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 rank104 branch audit missing true checks: {missing}")

    word_table = np.asarray(tables["word_audit_table"], dtype=np.int64)
    target_path_table = np.asarray(tables["target_path_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if word_table.shape != (3, len(WORD_AUDIT_COLUMNS)):
        raise AssertionError("rank104 word audit table shape mismatch")
    if target_path_table.shape != (4, len(TARGET_PATH_COLUMNS)):
        raise AssertionError("rank104 target path table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("rank104 observable table shape mismatch")

    word_rows = table_rows(word_table, WORD_AUDIT_COLUMNS)
    counts = {tuple(row[f"symbol_{index}_id"] for index in range(row["word_length"])): row["bounded_candidate_count"] for row in word_rows}
    if counts != {
        (2, 1, 3, 4, 5, 2): 2,
        (2, 1, 3, 4, 5, 2, 2): 12,
        (2, 1, 3, 4, 5, 2, 5): 4,
    }:
        raise AssertionError("rank104 word split mismatch")
    target_word_row = next(
        row for row in word_rows if row["edit_repair_candidate_flag"] == 1
    )
    target_word = tuple(
        target_word_row[f"symbol_{index}_id"]
        for index in range(target_word_row["word_length"])
    )
    if target_word != (2, 1, 3, 4, 5, 2, 5):
        raise AssertionError("rank104 target-language word mismatch")
    if target_word_row["edit_repair_target_word_id"] != 0:
        raise AssertionError("rank104 target-language target id mismatch")
    if target_word_row["edit_repair_edit_distance"] != 2:
        raise AssertionError("rank104 target-language edit distance mismatch")
    if target_word_row["edit_repair_weak_repair_flag"] != 1:
        raise AssertionError("rank104 target-language weak flag mismatch")
    if target_word_row["edit_repair_strong_repair_flag"] != 0:
        raise AssertionError("rank104 target-language strong flag mismatch")
    if target_word_row["edit_repair_target_consumed_before_node44_flag"] != 0:
        raise AssertionError("rank104 target-language consumption flag mismatch")
    if sum(row["closed_repair_class_match_flag"] for row in word_rows) != 0:
        raise AssertionError("rank104 unexpectedly matches prior closed repair classes")

    target_paths = table_rows(target_path_table, TARGET_PATH_COLUMNS)
    if [row["bounded_candidate_id"] for row in target_paths] != [110, 114, 116, 120]:
        raise AssertionError("rank104 target bounded candidate ids mismatch")
    if [row["bounded_rank_order"] for row in target_paths] != [111, 115, 117, 121]:
        raise AssertionError("rank104 target bounded ranks mismatch")

    witness = report.get("witness", {})
    if witness.get("rank104_trace") != [48, 42, 27, 31, 50, 44]:
        raise AssertionError("rank104 trace witness mismatch")
    if witness.get("target_language_word") != [2, 1, 3, 4, 5, 2, 5]:
        raise AssertionError("rank104 target language witness mismatch")
    if witness.get("target_language_bounded_candidate_ids") != [110, 114, 116, 120]:
        raise AssertionError("rank104 target path id witness mismatch")
    if witness.get("target_language_bounded_ranks") != [111, 115, 117, 121]:
        raise AssertionError("rank104 target path rank witness mismatch")
    if witness.get("word_audit_table_sha256") != expected["report"]["witness"]["word_audit_table_sha256"]:
        raise AssertionError("word audit table witness hash mismatch")
    if witness.get("target_path_table_sha256") != expected["report"]["witness"]["target_path_table_sha256"]:
        raise AssertionError("target path table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("observable table witness hash mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("trace_quotient_report", {}), TRACE_QUOTIENT_REPORT, "trace quotient report input")
    assert_file_hash(inputs.get("trace_quotient_json", {}), TRACE_QUOTIENT_JSON, "trace quotient JSON input")
    assert_file_hash(inputs.get("trace_quotient_classes", {}), TRACE_QUOTIENT_CLASSES, "trace quotient classes input")
    assert_file_hash(inputs.get("trace_quotient_tables", {}), TRACE_QUOTIENT_TABLES, "trace quotient tables input")
    assert_file_hash(inputs.get("trace_quotient_certificate", {}), TRACE_QUOTIENT_CERTIFICATE, "trace quotient certificate input")
    assert_file_hash(inputs.get("bounded_backtrack_candidates", {}), BOUNDED_BACKTRACK_CANDIDATES, "bounded backtrack candidates input")
    assert_file_hash(inputs.get("bounded_backtrack_tables", {}), BOUNDED_BACKTRACK_TABLES, "bounded backtrack tables input")
    assert_file_hash(inputs.get("edit_repair_report", {}), EDIT_REPAIR_REPORT, "edit repair report input")
    assert_file_hash(inputs.get("edit_repair_candidates", {}), EDIT_REPAIR_CANDIDATES, "edit repair candidates input")
    assert_file_hash(inputs.get("edit_repair_tables", {}), EDIT_REPAIR_TABLES, "edit repair tables input")
    assert_file_hash(inputs.get("edit_repair_certificate", {}), EDIT_REPAIR_CERTIFICATE, "edit repair certificate input")
    assert_file_hash(inputs.get("closed_repair_report", {}), CLOSED_REPAIR_REPORT, "closed repair report input")
    assert_file_hash(inputs.get("closed_repair_certificate", {}), CLOSED_REPAIR_CERTIFICATE, "closed repair certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_rank104_branch_audit_manifest@1":
        raise AssertionError("C985 d20 rank104 branch audit manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 rank104 branch audit manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 rank104 branch audit manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 rank104 branch audit missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 rank104 branch audit index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 rank104 branch audit index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_rank104_branch_audit@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "rank104_trace": witness.get("rank104_trace"),
        "target_language_word": witness.get("target_language_word"),
        "target_language_bounded_candidate_ids": witness.get(
            "target_language_bounded_candidate_ids"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
