from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_CERTIFICATE,
        BOUNDED_BACKTRACK_JSON,
        BOUNDED_BACKTRACK_REPORT,
        BOUNDED_BACKTRACK_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_MATCH_COLUMNS,
        REPAIR_CLASS_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TAIL_CLOSURE_CERTIFICATE,
        TAIL_CLOSURE_CLOSED_PATHS,
        TAIL_CLOSURE_JSON,
        TAIL_CLOSURE_REPAIRS,
        TAIL_CLOSURE_REPORT,
        TAIL_CLOSURE_TABLES,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_CERTIFICATE,
        BOUNDED_BACKTRACK_JSON,
        BOUNDED_BACKTRACK_REPORT,
        BOUNDED_BACKTRACK_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        DERIVE_SCRIPT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_MATCH_COLUMNS,
        REPAIR_CLASS_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TAIL_CLOSURE_CERTIFICATE,
        TAIL_CLOSURE_CLOSED_PATHS,
        TAIL_CLOSURE_JSON,
        TAIL_CLOSURE_REPAIRS,
        TAIL_CLOSURE_REPORT,
        TAIL_CLOSURE_TABLES,
        THEOREM_ID,
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


def validate_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    ranking = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate.json"
    )
    classes_csv = (OUT_DIR / "aperture_overhead2_closed_repair_classes.csv").read_text(
        encoding="utf-8"
    )
    path_matches_csv = (
        OUT_DIR / "aperture_overhead2_closed_repair_path_matches.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_overhead2_closed_repair_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        ranking
        != expected[
            "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking"
        ]
    ):
        raise AssertionError("closed repair cycle ranking JSON is not reproducible")
    if classes_csv != expected["aperture_overhead2_closed_repair_classes_csv"]:
        raise AssertionError("closed repair classes CSV is not reproducible")
    if path_matches_csv != expected["aperture_overhead2_closed_repair_path_matches_csv"]:
        raise AssertionError("closed repair path matches CSV is not reproducible")
    if observables_csv != expected["aperture_overhead2_closed_repair_observables_csv"]:
        raise AssertionError("closed repair observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate"
        ]
    ):
        raise AssertionError("closed repair cycle ranking certificate is not reproducible")

    for name in ["repair_class_table", "path_match_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"closed repair cycle ranking table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking@1":
        raise AssertionError("C985 d20 closed repair ranking report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 closed repair ranking layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 closed repair ranking all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 closed repair ranking checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 closed repair ranking report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 closed repair ranking report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 closed repair ranking missing true checks: {missing}")

    repair_class_table = np.asarray(tables["repair_class_table"], dtype=np.int64)
    path_match_table = np.asarray(tables["path_match_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if repair_class_table.shape != (2, len(REPAIR_CLASS_COLUMNS)):
        raise AssertionError("closed repair class table shape mismatch")
    if path_match_table.shape != (20, len(PATH_MATCH_COLUMNS)):
        raise AssertionError("closed repair path match table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("closed repair observable table shape mismatch")

    class_rows = table_rows(repair_class_table, REPAIR_CLASS_COLUMNS)
    by_target = {row["target_word_id"]: row for row in class_rows}
    if by_target[0]["exact_bounded_match_count"] != 2:
        raise AssertionError("target0 exact bounded match count mismatch")
    if by_target[0]["outside_bounded_path_count"] != 6:
        raise AssertionError("target0 outside bounded count mismatch")
    if by_target[0]["baseline_score_alias_flag"] != 1:
        raise AssertionError("target0 baseline alias flag mismatch")
    if by_target[0]["score_rank_min"] != 1 or by_target[0]["score_rank_max"] != 103:
        raise AssertionError("target0 score rank interval mismatch")
    if by_target[0]["best_exact_bounded_rank"] != 5 or by_target[0]["worst_exact_bounded_rank"] != 9:
        raise AssertionError("target0 exact rank interval mismatch")

    if by_target[1]["exact_bounded_match_count"] != 3:
        raise AssertionError("target1 exact bounded match count mismatch")
    if by_target[1]["outside_bounded_path_count"] != 9:
        raise AssertionError("target1 outside bounded count mismatch")
    if by_target[1]["baseline_score_alias_flag"] != 0:
        raise AssertionError("target1 baseline alias flag mismatch")
    if by_target[1]["nonbaseline_overhead3_class_flag"] != 1:
        raise AssertionError("target1 nonbaseline overhead3 flag mismatch")
    if by_target[1]["score_better_candidate_count"] != 121:
        raise AssertionError("target1 score better count mismatch")
    if by_target[1]["score_rank_min"] != 122 or by_target[1]["score_rank_max"] != 124:
        raise AssertionError("target1 score rank interval mismatch")

    path_rows = table_rows(path_match_table, PATH_MATCH_COLUMNS)
    exact_count = sum(row["exact_bounded_match_flag"] for row in path_rows)
    eligible_count = sum(row["bounded_scope_eligible_flag"] for row in path_rows)
    unmatched_eligible = sum(
        1
        for row in path_rows
        if row["bounded_scope_eligible_flag"] == 1
        and row["exact_bounded_match_flag"] == 0
    )
    simple_outside = sum(1 for row in path_rows if row["outside_reason_code"] == 1)
    intermediate_outside = sum(1 for row in path_rows if row["outside_reason_code"] == 2)
    unexplained_outside = sum(1 for row in path_rows if row["outside_reason_code"] == 3)
    if exact_count != 5:
        raise AssertionError("exact bounded path match count mismatch")
    if eligible_count != 5 or unmatched_eligible != 0:
        raise AssertionError("bounded-scope eligible path match mismatch")
    if (simple_outside, intermediate_outside, unexplained_outside) != (2, 13, 0):
        raise AssertionError("outside reason split mismatch")

    witness = report.get("witness", {})
    classes = witness.get("repair_classes", {})
    if classes.get("0", {}).get("symbol_word") != [2, 1, 4, 5, 2, 5]:
        raise AssertionError("target0 symbol word witness mismatch")
    if classes.get("0", {}).get("trace_nodes") != [48, 42, 27, 28, 34, 44]:
        raise AssertionError("target0 trace witness mismatch")
    if classes.get("0", {}).get("baseline_score_alias") is not True:
        raise AssertionError("target0 baseline witness mismatch")
    if classes.get("1", {}).get("symbol_word") != [2, 1, 5, 2, 5, 4, 3]:
        raise AssertionError("target1 symbol word witness mismatch")
    if classes.get("1", {}).get("trace_nodes") != [48, 42, 27, 29, 45, 44]:
        raise AssertionError("target1 trace witness mismatch")
    if classes.get("1", {}).get("nonbaseline_overhead3_class") is not True:
        raise AssertionError("target1 nonbaseline witness mismatch")
    if witness.get("outside_reason_counts") != {
        "simple": 2,
        "intermediate_origin": 13,
        "unexplained": 0,
    }:
        raise AssertionError("outside reason witness mismatch")
    if witness.get("repair_class_table_sha256") != expected["report"]["witness"]["repair_class_table_sha256"]:
        raise AssertionError("repair class table witness hash mismatch")
    if witness.get("path_match_table_sha256") != expected["report"]["witness"]["path_match_table_sha256"]:
        raise AssertionError("path match table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("observable table witness hash mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("tail_closure_report", {}), TAIL_CLOSURE_REPORT, "tail closure report input")
    assert_file_hash(inputs.get("tail_closure_json", {}), TAIL_CLOSURE_JSON, "tail closure JSON input")
    assert_file_hash(inputs.get("tail_closure_repairs", {}), TAIL_CLOSURE_REPAIRS, "tail closure repairs input")
    assert_file_hash(inputs.get("tail_closure_closed_paths", {}), TAIL_CLOSURE_CLOSED_PATHS, "tail closure closed paths input")
    assert_file_hash(inputs.get("tail_closure_tables", {}), TAIL_CLOSURE_TABLES, "tail closure tables input")
    assert_file_hash(inputs.get("tail_closure_certificate", {}), TAIL_CLOSURE_CERTIFICATE, "tail closure certificate input")
    assert_file_hash(inputs.get("bounded_backtrack_report", {}), BOUNDED_BACKTRACK_REPORT, "bounded backtrack report input")
    assert_file_hash(inputs.get("bounded_backtrack_json", {}), BOUNDED_BACKTRACK_JSON, "bounded backtrack JSON input")
    assert_file_hash(inputs.get("bounded_backtrack_candidates", {}), BOUNDED_BACKTRACK_CANDIDATES, "bounded backtrack candidates input")
    assert_file_hash(inputs.get("bounded_backtrack_tables", {}), BOUNDED_BACKTRACK_TABLES, "bounded backtrack tables input")
    assert_file_hash(inputs.get("bounded_backtrack_certificate", {}), BOUNDED_BACKTRACK_CERTIFICATE, "bounded backtrack certificate input")
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
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_manifest@1":
        raise AssertionError("C985 d20 closed repair ranking manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 closed repair ranking manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 closed repair ranking manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 closed repair ranking missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 closed repair ranking index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 closed repair ranking index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "repair_classes": witness.get("repair_classes"),
        "outside_reason_counts": witness.get("outside_reason_counts"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
