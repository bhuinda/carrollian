from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_CERTIFICATE,
        BOUNDED_BACKTRACK_JSON,
        BOUNDED_BACKTRACK_REPORT,
        BOUNDED_BACKTRACK_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLOSED_REPAIR_CERTIFICATE,
        CLOSED_REPAIR_JSON,
        CLOSED_REPAIR_REPORT,
        CLOSED_REPAIR_TABLES,
        DERIVE_SCRIPT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PAIRWISE_TRACE_EDIT_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_CLASS_COLUMNS,
        TRACE_NODE_COLUMNS,
        TRACE_NODE_READOUT_COLUMNS,
        TRANSITION_EDIT_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_CERTIFICATE,
        BOUNDED_BACKTRACK_JSON,
        BOUNDED_BACKTRACK_REPORT,
        BOUNDED_BACKTRACK_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLOSED_REPAIR_CERTIFICATE,
        CLOSED_REPAIR_JSON,
        CLOSED_REPAIR_REPORT,
        CLOSED_REPAIR_TABLES,
        DERIVE_SCRIPT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PAIRWISE_TRACE_EDIT_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRACE_CLASS_COLUMNS,
        TRACE_NODE_COLUMNS,
        TRACE_NODE_READOUT_COLUMNS,
        TRANSITION_EDIT_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    quotient = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_trace_class_quotient.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate.json"
    )
    trace_classes_csv = (OUT_DIR / "aperture_overhead3_trace_classes.csv").read_text(
        encoding="utf-8"
    )
    node_readout_csv = (
        OUT_DIR / "aperture_overhead3_trace_node_readout.csv"
    ).read_text(encoding="utf-8")
    transition_edits_csv = (
        OUT_DIR / "aperture_overhead3_transition_edits.csv"
    ).read_text(encoding="utf-8")
    pairwise_edits_csv = (
        OUT_DIR / "aperture_overhead3_pairwise_trace_edits.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_overhead3_trace_quotient_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        quotient
        != expected["signature_boundary_spine_aperture_overhead3_trace_class_quotient"]
    ):
        raise AssertionError("overhead3 trace quotient JSON is not reproducible")
    if trace_classes_csv != expected["aperture_overhead3_trace_classes_csv"]:
        raise AssertionError("overhead3 trace classes CSV is not reproducible")
    if node_readout_csv != expected["aperture_overhead3_trace_node_readout_csv"]:
        raise AssertionError("overhead3 trace node readout CSV is not reproducible")
    if transition_edits_csv != expected["aperture_overhead3_transition_edits_csv"]:
        raise AssertionError("overhead3 transition edits CSV is not reproducible")
    if pairwise_edits_csv != expected["aperture_overhead3_pairwise_trace_edits_csv"]:
        raise AssertionError("overhead3 pairwise trace edits CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_overhead3_trace_quotient_observables_csv"]
    ):
        raise AssertionError("overhead3 trace quotient observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate"
        ]
    ):
        raise AssertionError("overhead3 trace quotient certificate is not reproducible")

    for name in [
        "trace_class_table",
        "node_readout_table",
        "transition_table",
        "pairwise_trace_edit_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"overhead3 trace quotient table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient@1":
        raise AssertionError("C985 d20 overhead3 trace quotient report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 overhead3 trace quotient layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 overhead3 trace quotient all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 overhead3 trace quotient checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead3 trace quotient report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 overhead3 trace quotient report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 overhead3 trace quotient missing true checks: {missing}")

    trace_class_table = np.asarray(tables["trace_class_table"], dtype=np.int64)
    node_readout_table = np.asarray(tables["node_readout_table"], dtype=np.int64)
    transition_table = np.asarray(tables["transition_table"], dtype=np.int64)
    pairwise_table = np.asarray(tables["pairwise_trace_edit_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if trace_class_table.shape != (7, len(TRACE_CLASS_COLUMNS)):
        raise AssertionError("overhead3 trace class table shape mismatch")
    if node_readout_table.shape != (42, len(TRACE_NODE_READOUT_COLUMNS)):
        raise AssertionError("overhead3 trace node readout table shape mismatch")
    if transition_table.shape != (1, len(TRANSITION_EDIT_COLUMNS)):
        raise AssertionError("overhead3 transition edit table shape mismatch")
    if pairwise_table.shape != (21, len(PAIRWISE_TRACE_EDIT_COLUMNS)):
        raise AssertionError("overhead3 pairwise edit table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("overhead3 observable table shape mismatch")

    class_rows = table_rows(trace_class_table, TRACE_CLASS_COLUMNS)
    if [row["candidate_count"] for row in class_rows] != [103, 18, 3, 9, 51, 35, 21]:
        raise AssertionError("overhead3 trace class candidate counts mismatch")
    if [row["rank_min"] for row in class_rows] != [1, 104, 122, 125, 134, 137, 150]:
        raise AssertionError("overhead3 trace class rank minima mismatch")
    if [row["rank_max"] for row in class_rows] != [103, 121, 124, 133, 233, 240, 205]:
        raise AssertionError("overhead3 trace class rank maxima mismatch")

    baseline = class_rows[0]
    target1 = class_rows[2]
    baseline_trace = [
        baseline[column] for column in TRACE_NODE_COLUMNS if baseline[column] >= 0
    ]
    target1_trace = [
        target1[column] for column in TRACE_NODE_COLUMNS if target1[column] >= 0
    ]
    if baseline_trace != [48, 42, 27, 28, 34, 44]:
        raise AssertionError("baseline trace class witness mismatch")
    if target1_trace != [48, 42, 27, 29, 45, 44]:
        raise AssertionError("target1 trace class witness mismatch")
    if baseline["baseline_alias_flag"] != 1 or baseline["candidate_count"] != 103:
        raise AssertionError("baseline trace class flag/count mismatch")
    if baseline["distinct_symbol_word_count"] != 14:
        raise AssertionError("baseline trace class word breadth mismatch")
    if target1["target1_branch_flag"] != 1 or target1["candidate_count"] != 3:
        raise AssertionError("target1 trace class flag/count mismatch")
    if target1["distinct_symbol_word_count"] != 1:
        raise AssertionError("target1 trace class word breadth mismatch")

    transition = table_rows(transition_table, TRANSITION_EDIT_COLUMNS)[0]
    expected_transition = {
        "common_prefix_node_count": 3,
        "common_suffix_node_count": 1,
        "source_divergent_node_count": 2,
        "target_divergent_node_count": 2,
        "trace_node_edit_distance": 2,
        "trace_edge_edit_distance": 3,
        "trace_ambient_aligned_substitution_cost": 3,
        "symbol_word_min_edit_distance": 3,
        "closed_repair_word_edit_distance": 3,
        "atom_word_min_edit_distance": 3,
        "carrier_path_min_edit_distance": 3,
        "cell_edge_path_min_edit_distance": 5,
        "source_divergent_node_0_id": 28,
        "source_divergent_node_1_id": 34,
        "target_divergent_node_0_id": 29,
        "target_divergent_node_1_id": 45,
    }
    for key, value in expected_transition.items():
        if transition[key] != value:
            raise AssertionError(f"transition witness mismatch for {key}")

    witness = report.get("witness", {})
    if witness.get("trace_class_count") != 7:
        raise AssertionError("trace class count witness mismatch")
    if witness.get("overhead3_candidate_count") != 240:
        raise AssertionError("overhead3 candidate count witness mismatch")
    transition_witness = witness.get("baseline_to_target1_transition", {})
    for key, value in expected_transition.items():
        if transition_witness.get(key) != value:
            raise AssertionError(f"transition report witness mismatch for {key}")
    if witness.get("trace_class_table_sha256") != expected["report"]["witness"]["trace_class_table_sha256"]:
        raise AssertionError("trace class table witness hash mismatch")
    if witness.get("node_readout_table_sha256") != expected["report"]["witness"]["node_readout_table_sha256"]:
        raise AssertionError("node readout table witness hash mismatch")
    if witness.get("transition_table_sha256") != expected["report"]["witness"]["transition_table_sha256"]:
        raise AssertionError("transition table witness hash mismatch")
    if witness.get("pairwise_trace_edit_table_sha256") != expected["report"]["witness"]["pairwise_trace_edit_table_sha256"]:
        raise AssertionError("pairwise trace edit table witness hash mismatch")
    if witness.get("observable_table_sha256") != expected["report"]["witness"]["observable_table_sha256"]:
        raise AssertionError("observable table witness hash mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("bounded_backtrack_report", {}), BOUNDED_BACKTRACK_REPORT, "bounded backtrack report input")
    assert_file_hash(inputs.get("bounded_backtrack_json", {}), BOUNDED_BACKTRACK_JSON, "bounded backtrack JSON input")
    assert_file_hash(inputs.get("bounded_backtrack_candidates", {}), BOUNDED_BACKTRACK_CANDIDATES, "bounded backtrack candidates input")
    assert_file_hash(inputs.get("bounded_backtrack_tables", {}), BOUNDED_BACKTRACK_TABLES, "bounded backtrack tables input")
    assert_file_hash(inputs.get("bounded_backtrack_certificate", {}), BOUNDED_BACKTRACK_CERTIFICATE, "bounded backtrack certificate input")
    assert_file_hash(inputs.get("closed_repair_report", {}), CLOSED_REPAIR_REPORT, "closed repair report input")
    assert_file_hash(inputs.get("closed_repair_json", {}), CLOSED_REPAIR_JSON, "closed repair JSON input")
    assert_file_hash(inputs.get("closed_repair_tables", {}), CLOSED_REPAIR_TABLES, "closed repair tables input")
    assert_file_hash(inputs.get("closed_repair_certificate", {}), CLOSED_REPAIR_CERTIFICATE, "closed repair certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_nodes", {}), REWRITE_COMPLEX_NODES, "rewrite complex nodes input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity tables input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient_manifest@1":
        raise AssertionError("C985 d20 overhead3 trace quotient manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead3 trace quotient manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 overhead3 trace quotient manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 overhead3 trace quotient missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead3 trace quotient index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 overhead3 trace quotient index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "trace_class_count": witness.get("trace_class_count"),
        "overhead3_candidate_count": witness.get("overhead3_candidate_count"),
        "baseline_to_target1_transition": witness.get(
            "baseline_to_target1_transition"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
