from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        ATOM_TRADEOFF_CANDIDATES,
        ATOM_TRADEOFF_CERTIFICATE,
        ATOM_TRADEOFF_JSON,
        ATOM_TRADEOFF_REPORT,
        ATOM_TRADEOFF_TABLES,
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        HYBRID_CANDIDATE_COLUMNS,
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
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        ATOM_TRADEOFF_CANDIDATES,
        ATOM_TRADEOFF_CERTIFICATE,
        ATOM_TRADEOFF_JSON,
        ATOM_TRADEOFF_REPORT,
        ATOM_TRADEOFF_TABLES,
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        HYBRID_CANDIDATE_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    hybrid_search = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_tail_hybrid_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_tail_hybrid_search_certificate.json"
    )
    candidates_csv = (OUT_DIR / "aperture_tail_hybrid_candidates.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "aperture_tail_hybrid_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_tail_hybrid_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if hybrid_search != expected["signature_boundary_spine_aperture_tail_hybrid_search"]:
        raise AssertionError("tail-hybrid search JSON is not reproducible")
    if candidates_csv != expected["aperture_tail_hybrid_candidates_csv"]:
        raise AssertionError("tail-hybrid candidate CSV is not reproducible")
    if observables_csv != expected["aperture_tail_hybrid_observables_csv"]:
        raise AssertionError("tail-hybrid observable CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_tail_hybrid_search_certificate"
        ]
    ):
        raise AssertionError("tail-hybrid certificate is not reproducible")

    for name in ["candidate_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"tail-hybrid table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_tail_hybrid_search@1":
        raise AssertionError("C985 d20 tail-hybrid report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 tail-hybrid search is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 tail-hybrid all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 tail-hybrid checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 tail-hybrid report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 tail-hybrid report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 tail-hybrid missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("node44_hybrid_candidate_count") != 127:
        raise AssertionError("tail-hybrid candidate count mismatch")
    if witness.get("candidate_count_by_length") != {"5": 19, "6": 108}:
        raise AssertionError("tail-hybrid length split mismatch")
    if witness.get("overhead_histogram") != {"3": 27, "4": 44, "5": 56}:
        raise AssertionError("tail-hybrid overhead histogram mismatch")
    if witness.get("best_hybrid_count") != 11:
        raise AssertionError("tail-hybrid best-count mismatch")
    if witness.get("best_hybrid_count_by_length") != {"5": 3, "6": 8}:
        raise AssertionError("tail-hybrid best length split mismatch")
    if witness.get("best_hybrid_score") != {
        "trace_detour_overhead": BASELINE_TAIL_OVERHEAD,
        "signature_valley_depth": BASELINE_TAIL_VALLEY,
        "metric_gromov_delta": float(BASELINE_TAIL_DELTA_TWICE / 2.0),
        "trace_signature_total_variation": BASELINE_TAIL_VARIATION,
    }:
        raise AssertionError("tail-hybrid best score mismatch")
    if witness.get("best_hybrid_edge_cycles", [])[:3] != [
        [14, 11, 33, 40, 39],
        [14, 11, 33, 42, 41],
        [41, 31, 33, 40, 39],
    ]:
        raise AssertionError("tail-hybrid best edge-cycle prefix mismatch")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if candidate_table.shape != (127, len(HYBRID_CANDIDATE_COLUMNS)):
        raise AssertionError("tail-hybrid candidate table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("tail-hybrid observable table shape mismatch")

    length_idx = HYBRID_CANDIDATE_COLUMNS.index("cycle_length")
    overhead_idx = HYBRID_CANDIDATE_COLUMNS.index("trace_detour_overhead")
    first_x2_idx = HYBRID_CANDIDATE_COLUMNS.index("first_selected_x2_flag")
    immediate_x1_idx = HYBRID_CANDIDATE_COLUMNS.index("immediate_x1_tail_flag")
    node44_idx = HYBRID_CANDIDATE_COLUMNS.index("node44_realization_flag")
    improvement_idx = HYBRID_CANDIDATE_COLUMNS.index("improves_tail_overhead_flag")
    baseline_match_idx = HYBRID_CANDIDATE_COLUMNS.index(
        "matches_baseline_tail_score_flag"
    )
    best_idx = HYBRID_CANDIDATE_COLUMNS.index("best_hybrid_flag")
    if int(np.sum(candidate_table[:, length_idx] == 5)) != 19:
        raise AssertionError("tail-hybrid length-5 table count mismatch")
    if int(np.sum(candidate_table[:, length_idx] == 6)) != 108:
        raise AssertionError("tail-hybrid length-6 table count mismatch")
    if int(np.min(candidate_table[:, overhead_idx])) != BASELINE_TAIL_OVERHEAD:
        raise AssertionError("tail-hybrid minimum overhead mismatch")
    if {
        str(value): int(np.sum(candidate_table[:, overhead_idx] == value))
        for value in sorted(set(candidate_table[:, overhead_idx].tolist()))
    } != {"3": 27, "4": 44, "5": 56}:
        raise AssertionError("tail-hybrid overhead table histogram mismatch")
    if not np.all(candidate_table[:, first_x2_idx] == 1):
        raise AssertionError("tail-hybrid first selected x2 flag mismatch")
    if not np.all(candidate_table[:, immediate_x1_idx] == 1):
        raise AssertionError("tail-hybrid immediate x1 flag mismatch")
    if not np.all(candidate_table[:, node44_idx] == 1):
        raise AssertionError("tail-hybrid node44 flag mismatch")
    if int(np.sum(candidate_table[:, improvement_idx])) != 0:
        raise AssertionError("tail-hybrid improvement flag mismatch")
    if int(np.sum(candidate_table[:, baseline_match_idx])) != 11:
        raise AssertionError("tail-hybrid baseline match count mismatch")
    if int(np.sum(candidate_table[:, best_idx])) != 11:
        raise AssertionError("tail-hybrid best flag count mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("atom_tradeoff_report", {}), ATOM_TRADEOFF_REPORT, "atom tradeoff report input")
    assert_file_hash(inputs.get("atom_tradeoff_json", {}), ATOM_TRADEOFF_JSON, "atom tradeoff JSON input")
    assert_file_hash(inputs.get("atom_tradeoff_candidates", {}), ATOM_TRADEOFF_CANDIDATES, "atom tradeoff candidates input")
    assert_file_hash(inputs.get("atom_tradeoff_tables", {}), ATOM_TRADEOFF_TABLES, "atom tradeoff tables input")
    assert_file_hash(inputs.get("atom_tradeoff_certificate", {}), ATOM_TRADEOFF_CERTIFICATE, "atom tradeoff certificate input")
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

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_tail_hybrid_search_manifest@1":
        raise AssertionError("C985 d20 tail-hybrid manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 tail-hybrid manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 tail-hybrid manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 tail-hybrid missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 tail-hybrid index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 tail-hybrid index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_tail_hybrid_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "node44_hybrid_candidate_count": witness.get(
            "node44_hybrid_candidate_count"
        ),
        "candidate_count_by_length": witness.get("candidate_count_by_length"),
        "overhead_histogram": witness.get("overhead_histogram"),
        "best_hybrid_count": witness.get("best_hybrid_count"),
        "best_hybrid_score": witness.get("best_hybrid_score"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
