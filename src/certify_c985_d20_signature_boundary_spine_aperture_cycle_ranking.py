from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_CYCLE_CERTIFICATE,
        APERTURE_CYCLE_JSON,
        APERTURE_CYCLE_REPORT,
        APERTURE_CYCLE_TABLES,
        CANDIDATE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_WINDOW_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_CYCLE_CERTIFICATE,
        APERTURE_CYCLE_JSON,
        APERTURE_CYCLE_REPORT,
        APERTURE_CYCLE_TABLES,
        CANDIDATE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_WINDOW_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_cycle_ranking() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    ranking = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking.json"
    )
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking_certificate.json"
    )
    candidates_csv = (OUT_DIR / "aperture_cycle_ranked_candidates.csv").read_text(
        encoding="utf-8"
    )
    windows_csv = (
        OUT_DIR / "aperture_cycle_candidate_trace_windows.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (OUT_DIR / "aperture_cycle_ranking_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_ranking_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if ranking != expected["signature_boundary_spine_aperture_cycle_ranking"]:
        raise AssertionError("aperture cycle ranking JSON is not reproducible")
    if candidates_csv != expected["aperture_cycle_ranked_candidates_csv"]:
        raise AssertionError("aperture cycle candidate CSV is not reproducible")
    if windows_csv != expected["aperture_cycle_candidate_trace_windows_csv"]:
        raise AssertionError("aperture cycle trace-window CSV is not reproducible")
    if observables_csv != expected["aperture_cycle_ranking_observables_csv"]:
        raise AssertionError("aperture cycle ranking observable CSV is not reproducible")
    if (
        certificate
        != expected["signature_boundary_spine_aperture_cycle_ranking_certificate"]
    ):
        raise AssertionError("aperture cycle ranking certificate is not reproducible")

    for name in ["candidate_table", "trace_window_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"aperture cycle ranking table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_ranking@1":
        raise AssertionError("C985 d20 aperture cycle ranking report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 aperture cycle ranking is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 aperture cycle ranking all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 aperture cycle ranking checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle ranking report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 aperture cycle ranking report is not reproducible")

    checks = report.get("checks", {})
    missing = sorted(
        key for key in expected["report"]["checks"] if checks.get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 aperture cycle ranking missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("rooted_x2_cycle_count") != 10:
        raise AssertionError("aperture cycle ranking cycle count mismatch")
    if witness.get("distinct_symbol_cycles") != [[2, 0, 4, 5], [2, 1, 4, 5], [2, 5, 4, 3]]:
        raise AssertionError("aperture cycle ranking symbol cycles mismatch")
    if witness.get("best_candidate_count") != 6:
        raise AssertionError("aperture cycle ranking best candidate count mismatch")
    if witness.get("best_candidate_symbol_cycle") != [2, 5, 4, 3]:
        raise AssertionError("aperture cycle ranking best symbol cycle mismatch")
    if witness.get("best_candidate_edge_cycles") != [
        [39, 40, 26, 25],
        [39, 40, 30, 29],
        [39, 40, 33, 32],
        [41, 42, 26, 25],
        [41, 42, 30, 29],
        [41, 42, 33, 32],
    ]:
        raise AssertionError("aperture cycle ranking best edge cycles mismatch")
    if witness.get("selected_tail_cycle_rank_order") != 7:
        raise AssertionError("aperture cycle ranking selected rank mismatch")
    if witness.get("selected_tail_cycle_metrics") != {
        "metric_gromov_delta": 0.5,
        "signature_valley_depth": 37,
        "trace_detour_overhead": 3,
        "trace_signature_total_variation": 127,
    }:
        raise AssertionError("aperture cycle ranking selected metrics mismatch")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    trace_window_table = np.asarray(tables["trace_window_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if candidate_table.shape != (10, len(CANDIDATE_COLUMNS)):
        raise AssertionError("aperture cycle candidate table shape mismatch")
    if trace_window_table.shape != (38, len(TRACE_WINDOW_COLUMNS)):
        raise AssertionError("aperture cycle trace-window table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("aperture cycle observable table shape mismatch")
    if candidate_table[:, 21].tolist() != [0, 0, 0, 0, 0, 0, 3, 3, 3, 3]:
        raise AssertionError("aperture cycle trace overhead ordering mismatch")
    if candidate_table[:, 23].tolist() != [0, 0, 0, 0, 0, 0, 37, 37, 41, 41]:
        raise AssertionError("aperture cycle valley ordering mismatch")
    if candidate_table[:, 33].tolist() != [1, 1, 1, 1, 1, 1, 0, 0, 0, 0]:
        raise AssertionError("aperture cycle best-rank flags mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("aperture_cycle_report", {}), APERTURE_CYCLE_REPORT, "aperture cycle report input")
    assert_file_hash(inputs.get("aperture_cycle_language", {}), APERTURE_CYCLE_JSON, "aperture cycle JSON input")
    assert_file_hash(inputs.get("aperture_cycle_tables", {}), APERTURE_CYCLE_TABLES, "aperture cycle table input")
    assert_file_hash(inputs.get("aperture_cycle_certificate", {}), APERTURE_CYCLE_CERTIFICATE, "aperture cycle certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edge input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex table input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_nodes", {}), REWRITE_COMPLEX_NODES, "rewrite complex nodes input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex table input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity table input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_ranking_manifest@1":
        raise AssertionError("C985 d20 aperture cycle ranking manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle ranking manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 aperture cycle ranking manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 aperture cycle ranking missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture cycle ranking index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 aperture cycle ranking index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_cycle_ranking@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "rooted_x2_cycle_count": witness.get("rooted_x2_cycle_count"),
        "best_candidate_count": witness.get("best_candidate_count"),
        "best_candidate_symbol_cycle": witness.get("best_candidate_symbol_cycle"),
        "selected_tail_cycle_rank_order": witness.get(
            "selected_tail_cycle_rank_order"
        ),
        "selected_tail_cycle_metrics": witness.get("selected_tail_cycle_metrics"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_cycle_ranking()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
