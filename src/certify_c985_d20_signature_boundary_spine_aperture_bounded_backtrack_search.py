from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
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
        TAIL_HYBRID_CANDIDATES,
        TAIL_HYBRID_CERTIFICATE,
        TAIL_HYBRID_JSON,
        TAIL_HYBRID_REPORT,
        TAIL_HYBRID_TABLES,
        THEOREM_ID,
        TRACE_BOUNDARY_NODE_ID,
        STRICT_APERTURE_NODE_ID,
        TAIL_VALLEY_NODE_ID,
        WALK_CANDIDATE_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
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
        TAIL_HYBRID_CANDIDATES,
        TAIL_HYBRID_CERTIFICATE,
        TAIL_HYBRID_JSON,
        TAIL_HYBRID_REPORT,
        TAIL_HYBRID_TABLES,
        THEOREM_ID,
        TRACE_BOUNDARY_NODE_ID,
        STRICT_APERTURE_NODE_ID,
        TAIL_VALLEY_NODE_ID,
        WALK_CANDIDATE_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    bounded_search = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_bounded_backtrack_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_bounded_backtrack_search_certificate.json"
    )
    candidates_csv = (OUT_DIR / "aperture_bounded_backtrack_candidates.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_bounded_backtrack_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_bounded_backtrack_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        bounded_search
        != expected["signature_boundary_spine_aperture_bounded_backtrack_search"]
    ):
        raise AssertionError("bounded-backtrack search JSON is not reproducible")
    if candidates_csv != expected["aperture_bounded_backtrack_candidates_csv"]:
        raise AssertionError("bounded-backtrack candidate CSV is not reproducible")
    if observables_csv != expected["aperture_bounded_backtrack_observables_csv"]:
        raise AssertionError("bounded-backtrack observable CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_bounded_backtrack_search_certificate"
        ]
    ):
        raise AssertionError("bounded-backtrack certificate is not reproducible")

    for name in ["candidate_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"bounded-backtrack table {name} is not reproducible"
            )

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1":
        raise AssertionError("C985 d20 bounded-backtrack report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 bounded-backtrack search is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 bounded-backtrack all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 bounded-backtrack checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 bounded-backtrack report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 bounded-backtrack report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 bounded-backtrack missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("rooted_closed_walk_counts") != {
        "5": 1680,
        "6": 10004,
        "7": 59548,
    }:
        raise AssertionError("bounded-backtrack closed-walk counts mismatch")
    if witness.get("simple_walk_counts") != {"5": 938, "6": 3326, "7": 9980}:
        raise AssertionError("bounded-backtrack simple-walk counts mismatch")
    if witness.get("nonsimple_walk_counts") != {
        "5": 742,
        "6": 6678,
        "7": 49568,
    }:
        raise AssertionError("bounded-backtrack non-simple counts mismatch")
    if witness.get("node44_candidate_count") != 1287:
        raise AssertionError("bounded-backtrack node44 candidate count mismatch")
    if witness.get("candidate_count_by_length") != {"5": 1, "6": 77, "7": 1209}:
        raise AssertionError("bounded-backtrack length split mismatch")
    if witness.get("overhead_histogram") != {"3": 240, "4": 157, "5": 604, "6": 286}:
        raise AssertionError("bounded-backtrack overhead histogram mismatch")
    if witness.get("immediate_backtrack_histogram") != {"0": 406, "1": 736, "2": 145}:
        raise AssertionError("bounded-backtrack immediate-backtrack histogram mismatch")
    if witness.get("repeated_interior_carrier_histogram") != {
        "1": 993,
        "2": 290,
        "3": 4,
    }:
        raise AssertionError("bounded-backtrack repeated-carrier histogram mismatch")
    if witness.get("best_backtrack_count") != 103:
        raise AssertionError("bounded-backtrack best-count mismatch")
    if witness.get("best_backtrack_count_by_length") != {
        "5": 1,
        "6": 8,
        "7": 94,
    }:
        raise AssertionError("bounded-backtrack best length split mismatch")
    if witness.get("best_immediate_backtrack_histogram") != {"0": 63, "1": 40}:
        raise AssertionError("bounded-backtrack best immediate-backtrack mismatch")
    if witness.get("best_repeated_interior_carrier_histogram") != {
        "1": 71,
        "2": 31,
        "3": 1,
    }:
        raise AssertionError("bounded-backtrack best repeated-carrier mismatch")
    if witness.get("forced_trace_prefix") != [
        TRACE_BOUNDARY_NODE_ID,
        STRICT_APERTURE_NODE_ID,
        TAIL_VALLEY_NODE_ID,
    ]:
        raise AssertionError("bounded-backtrack forced trace prefix mismatch")
    if witness.get("best_trace_node_sequence") != [48, 42, 27, 28, 34, 44]:
        raise AssertionError("bounded-backtrack best trace sequence mismatch")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if candidate_table.shape != (1287, len(WALK_CANDIDATE_COLUMNS)):
        raise AssertionError("bounded-backtrack candidate table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("bounded-backtrack observable table shape mismatch")

    length_idx = WALK_CANDIDATE_COLUMNS.index("walk_length")
    overhead_idx = WALK_CANDIDATE_COLUMNS.index("trace_detour_overhead")
    backtrack_idx = WALK_CANDIDATE_COLUMNS.index("immediate_backtrack_count")
    repeated_idx = WALK_CANDIDATE_COLUMNS.index("repeated_interior_carrier_count")
    first_x2_idx = WALK_CANDIDATE_COLUMNS.index("first_selected_x2_flag")
    immediate_x1_idx = WALK_CANDIDATE_COLUMNS.index("immediate_x1_tail_flag")
    node44_idx = WALK_CANDIDATE_COLUMNS.index("node44_realization_flag")
    nonsimple_idx = WALK_CANDIDATE_COLUMNS.index("nonsimple_walk_flag")
    first_return_idx = WALK_CANDIDATE_COLUMNS.index("no_intermediate_origin_flag")
    improvement_idx = WALK_CANDIDATE_COLUMNS.index("improves_tail_overhead_flag")
    node27_idx = WALK_CANDIDATE_COLUMNS.index("contains_node27_after_node42_flag")
    baseline_match_idx = WALK_CANDIDATE_COLUMNS.index(
        "matches_baseline_tail_score_flag"
    )
    best_idx = WALK_CANDIDATE_COLUMNS.index("best_backtrack_flag")
    if [int(np.sum(candidate_table[:, length_idx] == length)) for length in [5, 6, 7]] != [
        1,
        77,
        1209,
    ]:
        raise AssertionError("bounded-backtrack table length counts mismatch")
    if int(np.min(candidate_table[:, overhead_idx])) != 3:
        raise AssertionError("bounded-backtrack minimum overhead mismatch")
    if {
        str(value): int(np.sum(candidate_table[:, overhead_idx] == value))
        for value in sorted(set(candidate_table[:, overhead_idx].tolist()))
    } != {"3": 240, "4": 157, "5": 604, "6": 286}:
        raise AssertionError("bounded-backtrack table overhead histogram mismatch")
    if {
        str(value): int(np.sum(candidate_table[:, backtrack_idx] == value))
        for value in sorted(set(candidate_table[:, backtrack_idx].tolist()))
    } != {"0": 406, "1": 736, "2": 145}:
        raise AssertionError("bounded-backtrack table backtrack histogram mismatch")
    if {
        str(value): int(np.sum(candidate_table[:, repeated_idx] == value))
        for value in sorted(set(candidate_table[:, repeated_idx].tolist()))
    } != {"1": 993, "2": 290, "3": 4}:
        raise AssertionError("bounded-backtrack table repeated histogram mismatch")
    if not np.all(candidate_table[:, first_x2_idx] == 1):
        raise AssertionError("bounded-backtrack first selected x2 flag mismatch")
    if not np.all(candidate_table[:, immediate_x1_idx] == 1):
        raise AssertionError("bounded-backtrack immediate x1 flag mismatch")
    if not np.all(candidate_table[:, node44_idx] == 1):
        raise AssertionError("bounded-backtrack node44 flag mismatch")
    if not np.all(candidate_table[:, nonsimple_idx] == 1):
        raise AssertionError("bounded-backtrack non-simple flag mismatch")
    if not np.all(candidate_table[:, first_return_idx] == 1):
        raise AssertionError("bounded-backtrack first-return flag mismatch")
    if int(np.sum(candidate_table[:, improvement_idx])) != 0:
        raise AssertionError("bounded-backtrack improvement flag mismatch")
    if int(np.sum(candidate_table[:, node27_idx])) != 1287:
        raise AssertionError("bounded-backtrack node27 prefix flag mismatch")
    if int(np.sum(candidate_table[:, baseline_match_idx])) != 103:
        raise AssertionError("bounded-backtrack baseline match count mismatch")
    if int(np.sum(candidate_table[:, best_idx])) != 103:
        raise AssertionError("bounded-backtrack best flag count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("tail_hybrid_report", {}), TAIL_HYBRID_REPORT, "tail hybrid report input")
    assert_file_hash(inputs.get("tail_hybrid_json", {}), TAIL_HYBRID_JSON, "tail hybrid JSON input")
    assert_file_hash(inputs.get("tail_hybrid_candidates", {}), TAIL_HYBRID_CANDIDATES, "tail hybrid candidates input")
    assert_file_hash(inputs.get("tail_hybrid_tables", {}), TAIL_HYBRID_TABLES, "tail hybrid tables input")
    assert_file_hash(inputs.get("tail_hybrid_certificate", {}), TAIL_HYBRID_CERTIFICATE, "tail hybrid certificate input")
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_bounded_backtrack_search_manifest@1":
        raise AssertionError("C985 d20 bounded-backtrack manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 bounded-backtrack manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 bounded-backtrack manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 bounded-backtrack missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 bounded-backtrack index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 bounded-backtrack index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "node44_candidate_count": witness.get("node44_candidate_count"),
        "candidate_count_by_length": witness.get("candidate_count_by_length"),
        "overhead_histogram": witness.get("overhead_histogram"),
        "best_backtrack_count": witness.get("best_backtrack_count"),
        "best_backtrack_score": witness.get("best_backtrack_score"),
        "forced_trace_prefix": witness.get("forced_trace_prefix"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
