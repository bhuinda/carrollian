from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_CERTIFICATE,
        BOUNDED_BACKTRACK_JSON,
        BOUNDED_BACKTRACK_REPORT,
        BOUNDED_BACKTRACK_TABLES,
        COMPLETION_COLUMNS,
        FORBIDDEN_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        POST_X2_OUTGOING_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATE_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_CERTIFICATE,
        BOUNDED_BACKTRACK_JSON,
        BOUNDED_BACKTRACK_REPORT,
        BOUNDED_BACKTRACK_TABLES,
        COMPLETION_COLUMNS,
        FORBIDDEN_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        POST_X2_OUTGOING_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATE_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRANSITION_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    obstruction = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_symbol_state_obstruction.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_symbol_state_obstruction_certificate.json"
    )
    states_csv = (OUT_DIR / "aperture_symbol_state_states.csv").read_text(
        encoding="utf-8"
    )
    transitions_csv = (
        OUT_DIR / "aperture_symbol_state_transitions.csv"
    ).read_text(encoding="utf-8")
    outgoing_csv = (
        OUT_DIR / "aperture_symbol_state_post_x2_outgoing.csv"
    ).read_text(encoding="utf-8")
    completions_csv = (
        OUT_DIR / "aperture_symbol_state_completions.csv"
    ).read_text(encoding="utf-8")
    forbidden_csv = (
        OUT_DIR / "aperture_symbol_state_forbidden_transitions.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_symbol_state_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_symbol_state_obstruction_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        obstruction
        != expected["signature_boundary_spine_aperture_symbol_state_obstruction"]
    ):
        raise AssertionError("symbol-state obstruction JSON is not reproducible")
    if states_csv != expected["aperture_symbol_state_states_csv"]:
        raise AssertionError("symbol-state states CSV is not reproducible")
    if transitions_csv != expected["aperture_symbol_state_transitions_csv"]:
        raise AssertionError("symbol-state transitions CSV is not reproducible")
    if outgoing_csv != expected["aperture_symbol_state_post_x2_outgoing_csv"]:
        raise AssertionError("symbol-state post-x2 outgoing CSV is not reproducible")
    if completions_csv != expected["aperture_symbol_state_completions_csv"]:
        raise AssertionError("symbol-state completions CSV is not reproducible")
    if forbidden_csv != expected["aperture_symbol_state_forbidden_transitions_csv"]:
        raise AssertionError("symbol-state forbidden CSV is not reproducible")
    if observables_csv != expected["aperture_symbol_state_observables_csv"]:
        raise AssertionError("symbol-state observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_symbol_state_obstruction_certificate"
        ]
    ):
        raise AssertionError("symbol-state certificate is not reproducible")

    for name in [
        "state_table",
        "transition_table",
        "post_x2_outgoing_table",
        "completion_table",
        "forbidden_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"symbol-state table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_symbol_state_obstruction@1":
        raise AssertionError("C985 d20 symbol-state report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 symbol-state obstruction is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 symbol-state all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 symbol-state checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbol-state report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 symbol-state report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 symbol-state missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("bounded_candidate_count") != 1287:
        raise AssertionError("symbol-state bounded candidate count mismatch")
    if witness.get("observed_state_count") != 89:
        raise AssertionError("symbol-state observed state count mismatch")
    if witness.get("observed_transition_count") != 169:
        raise AssertionError("symbol-state observed transition count mismatch")
    if witness.get("observed_trace_sequence_count") != 85:
        raise AssertionError("symbol-state trace sequence count mismatch")
    if witness.get("observed_symbol_word_count") != 126:
        raise AssertionError("symbol-state word count mismatch")
    if witness.get("node27_skip_possible_with_immediate_x1") is not False:
        raise AssertionError("symbol-state node27 skip flag mismatch")
    if witness.get("post_x2_outgoing", {}).get("1") != {
        "observed_bounded_transition_count": 1287,
        "raw_target_node_id": 27,
        "signature_union_count": 146,
    }:
        raise AssertionError("symbol-state x1 outgoing witness mismatch")
    if witness.get("ambient_42_to_44_edge") != {
        "exists": True,
        "required_tail_symbol_id": 1,
        "target_added_symbol_id": 4,
    }:
        raise AssertionError("symbol-state ambient geodesic edge witness mismatch")
    if witness.get("symbolic_x1_tail_overhead2_words") != [
        [2, 1, 4, 2, 5],
        [2, 1, 5, 2, 4],
    ]:
        raise AssertionError("symbol-state lower-overhead word mismatch")
    forbidden = witness.get("minimal_forbidden_transitions", [])
    if len(forbidden) != 2:
        raise AssertionError("symbol-state forbidden transition count mismatch")
    if forbidden[0].get("source_trace_node_id") != 28 or forbidden[0].get(
        "label_symbol_id"
    ) != 2:
        raise AssertionError("symbol-state first forbidden transition mismatch")
    if forbidden[0].get("observed_transition_count") != 0:
        raise AssertionError("symbol-state first forbidden observation mismatch")

    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    transition_table = np.asarray(tables["transition_table"], dtype=np.int64)
    outgoing_table = np.asarray(tables["post_x2_outgoing_table"], dtype=np.int64)
    completion_table = np.asarray(tables["completion_table"], dtype=np.int64)
    forbidden_table = np.asarray(tables["forbidden_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if state_table.shape != (89, len(STATE_COLUMNS)):
        raise AssertionError("symbol-state state table shape mismatch")
    if transition_table.shape != (169, len(TRANSITION_COLUMNS)):
        raise AssertionError("symbol-state transition table shape mismatch")
    if outgoing_table.shape != (6, len(POST_X2_OUTGOING_COLUMNS)):
        raise AssertionError("symbol-state outgoing table shape mismatch")
    if completion_table.shape != (8, len(COMPLETION_COLUMNS)):
        raise AssertionError("symbol-state completion table shape mismatch")
    if forbidden_table.shape != (2, len(FORBIDDEN_COLUMNS)):
        raise AssertionError("symbol-state forbidden table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("symbol-state observable table shape mismatch")

    outgoing_label_idx = POST_X2_OUTGOING_COLUMNS.index("label_symbol_id")
    outgoing_target_idx = POST_X2_OUTGOING_COLUMNS.index("raw_target_node_id")
    outgoing_observed_idx = POST_X2_OUTGOING_COLUMNS.index(
        "observed_bounded_transition_count"
    )
    if outgoing_table[:, outgoing_label_idx].tolist() != [0, 1, 2, 3, 4, 5]:
        raise AssertionError("symbol-state outgoing labels mismatch")
    if outgoing_table[:, outgoing_target_idx].tolist() != [12, 27, 37, 40, 41, 42]:
        raise AssertionError("symbol-state outgoing target nodes mismatch")
    if outgoing_table[:, outgoing_observed_idx].tolist() != [0, 1287, 0, 0, 0, 0]:
        raise AssertionError("symbol-state observed outgoing counts mismatch")

    completion_overhead_idx = COMPLETION_COLUMNS.index("trace_detour_overhead")
    completion_tail_idx = COMPLETION_COLUMNS.index("preserves_x1_tail_flag")
    if int(np.sum((completion_table[:, completion_tail_idx] == 1) & (completion_table[:, completion_overhead_idx] == 2))) != 2:
        raise AssertionError("symbol-state symbolic overhead-2 count mismatch")
    if forbidden_table[:, FORBIDDEN_COLUMNS.index("observed_transition_count")].tolist() != [0, 0]:
        raise AssertionError("symbol-state forbidden observed counts mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("bounded_backtrack_report", {}), BOUNDED_BACKTRACK_REPORT, "bounded backtrack report input")
    assert_file_hash(inputs.get("bounded_backtrack_json", {}), BOUNDED_BACKTRACK_JSON, "bounded backtrack JSON input")
    assert_file_hash(inputs.get("bounded_backtrack_candidates", {}), BOUNDED_BACKTRACK_CANDIDATES, "bounded backtrack candidates input")
    assert_file_hash(inputs.get("bounded_backtrack_tables", {}), BOUNDED_BACKTRACK_TABLES, "bounded backtrack tables input")
    assert_file_hash(inputs.get("bounded_backtrack_certificate", {}), BOUNDED_BACKTRACK_CERTIFICATE, "bounded backtrack certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity tables input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_symbol_state_obstruction_manifest@1":
        raise AssertionError("C985 d20 symbol-state manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbol-state manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 symbol-state manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 symbol-state missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbol-state index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 symbol-state index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_symbol_state_obstruction@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "observed_state_count": witness.get("observed_state_count"),
        "observed_transition_count": witness.get("observed_transition_count"),
        "node27_skip_possible_with_immediate_x1": witness.get(
            "node27_skip_possible_with_immediate_x1"
        ),
        "symbolic_x1_tail_overhead2_words": witness.get(
            "symbolic_x1_tail_overhead2_words"
        ),
        "minimal_forbidden_transitions": witness.get(
            "minimal_forbidden_transitions"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
