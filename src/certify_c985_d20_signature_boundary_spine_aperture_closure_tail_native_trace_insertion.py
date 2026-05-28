from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion import (
        CANDIDATE_COLUMNS,
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NATIVE_INSERTION_OBSERVABLE_CODES,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        STATUS,
        SUMMARY_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        VIRTUAL_GRAFT_CERTIFICATE,
        VIRTUAL_GRAFT_REPORT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion import (
        CANDIDATE_COLUMNS,
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NATIVE_INSERTION_OBSERVABLE_CODES,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        STATUS,
        SUMMARY_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        VIRTUAL_GRAFT_CERTIFICATE,
        VIRTUAL_GRAFT_REPORT,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "gate_trace_node_count": 11,
    "gate_trace_variation": 185,
    "gate_delta_twice": 2,
    "gate_closed_path_count": 30,
    "gate_template_count": 9,
    "gate_native_repair_flag": 0,
    "substitution_attempt_count": 495,
    "substitution_valid_path_count": 49,
    "substitution_repair_candidate_count": 0,
    "substitution_delta2_variation_le223_count": 0,
    "insertion_attempt_count": 540,
    "insertion_valid_path_count": 57,
    "insertion_repair_candidate_count": 4,
    "insertion_delta2_variation_le223_count": 3,
    "insertion_variation185_count": 1,
    "selected_insert_after_trace_rank": 2,
    "selected_inserted_node_id": 31,
    "selected_trace_variation": 185,
    "selected_trace_delta_twice": 2,
    "selected_trace_node_count": 12,
    "selected_31_28_repair_flag": 1,
    "selected_50_34_repair_flag": 0,
    "accepted_31_28_candidate_count": 3,
    "accepted_50_34_candidate_count": 0,
}

SELECTED_TRACE = (48, 42, 27, 31, 28, 34, 29, 45, 29, 28, 34, 44)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def trace_from_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in TRACE_NODE_COLUMNS if row[column] != -1)


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    insertion = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate.json"
    )
    summary_csv = (
        OUT_DIR / "aperture_closure_tail_native_trace_insertion_summary.csv"
    ).read_text(encoding="utf-8")
    candidates_csv = (
        OUT_DIR / "aperture_closure_tail_native_trace_insertion_candidates.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_native_trace_insertion_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        insertion
        != expected[
            "signature_boundary_spine_aperture_closure_tail_native_trace_insertion"
        ]
    ):
        raise AssertionError("native-trace-insertion JSON is not reproducible")
    if summary_csv != expected["aperture_closure_tail_native_trace_insertion_summary_csv"]:
        raise AssertionError("native-trace-insertion summary CSV is not reproducible")
    if (
        candidates_csv
        != expected["aperture_closure_tail_native_trace_insertion_candidates_csv"]
    ):
        raise AssertionError("native-trace-insertion candidates CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_closure_tail_native_trace_insertion_observables_csv"]
    ):
        raise AssertionError("native-trace-insertion observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_native_trace_insertion_certificate"
        ]
    ):
        raise AssertionError("native-trace-insertion certificate is not reproducible")

    for name in ["summary_table", "candidate_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"native-trace-insertion table {name} is not reproducible"
            )

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion@1"
    ):
        raise AssertionError("native-trace-insertion report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("native-trace-insertion layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("native-trace-insertion all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("native-trace-insertion checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("native-trace-insertion report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("native-trace-insertion report is not reproducible")

    summary_table = np.asarray(tables["summary_table"], dtype=np.int64)
    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if summary_table.shape != (2, len(SUMMARY_COLUMNS)):
        raise AssertionError("native-trace-insertion summary table shape mismatch")
    if candidate_table.shape != (3, len(CANDIDATE_COLUMNS)):
        raise AssertionError("native-trace-insertion candidate table shape mismatch")
    if observable_table.shape != (
        len(NATIVE_INSERTION_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("native-trace-insertion observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        NATIVE_INSERTION_OBSERVABLE_CODES[key]: value
        for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("native-trace-insertion observables mismatch")

    summary_rows = table_rows(summary_table, SUMMARY_COLUMNS)
    candidate_rows = table_rows(candidate_table, CANDIDATE_COLUMNS)
    substitution = next(row for row in summary_rows if row["operation_code"] == 0)
    insertion_summary = next(row for row in summary_rows if row["operation_code"] == 1)
    if (
        substitution["attempt_count"],
        substitution["valid_rewrite_path_count"],
        substitution["repair_edge_candidate_count"],
        substitution["delta2_variation_le223_count"],
    ) != (495, 49, 0, 0):
        raise AssertionError("native-trace-insertion substitution summary mismatch")
    if (
        insertion_summary["attempt_count"],
        insertion_summary["valid_rewrite_path_count"],
        insertion_summary["repair_edge_candidate_count"],
        insertion_summary["delta2_variation_le223_count"],
        insertion_summary["variation185_count"],
    ) != (540, 57, 4, 3, 1):
        raise AssertionError("native-trace-insertion insertion summary mismatch")

    selected_rows = [
        row for row in candidate_rows if row["selected_realization_flag"] == 1
    ]
    if len(selected_rows) != 1:
        raise AssertionError("native-trace-insertion selected row count mismatch")
    selected = selected_rows[0]
    if trace_from_row(selected) != SELECTED_TRACE:
        raise AssertionError("native-trace-insertion selected trace mismatch")
    if (
        selected["insert_after_trace_rank"],
        selected["patch_node_id"],
        selected["trace_signature_total_variation"],
        selected["metric_gromov_delta_twice"],
        selected["repair_31_28_flag"],
        selected["repair_50_34_flag"],
    ) != (2, 31, 185, 2, 1, 0):
        raise AssertionError("native-trace-insertion selected profile mismatch")
    if sum(row["repair_31_28_flag"] for row in candidate_rows) != 3:
        raise AssertionError("native-trace-insertion accepted 31--28 count mismatch")
    if sum(row["repair_50_34_flag"] for row in candidate_rows) != 0:
        raise AssertionError("native-trace-insertion accepted 50--34 count mismatch")

    witness = report.get("witness", {})
    if witness.get("gate_word") != list(NO_REPAIR_GATE_WORD):
        raise AssertionError("native-trace-insertion gate word witness mismatch")
    if witness.get("selected_trace") != list(SELECTED_TRACE):
        raise AssertionError("native-trace-insertion selected trace witness mismatch")
    if witness.get("gate_profile", {}).get("closed_paths") != 30:
        raise AssertionError("native-trace-insertion gate closure witness mismatch")
    if witness.get("gate_profile", {}).get("templates") != 9:
        raise AssertionError("native-trace-insertion gate template witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("native-trace-insertion certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("virtual_graft_report", {}),
        VIRTUAL_GRAFT_REPORT,
        "virtual-graft report input",
    )
    assert_file_hash(
        inputs.get("virtual_graft_certificate", {}),
        VIRTUAL_GRAFT_CERTIFICATE,
        "virtual-graft certificate input",
    )
    assert_file_hash(
        inputs.get("symbolic_alphabet", {}),
        SYMBOLIC_ALPHABET_CSV,
        "symbolic alphabet input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity", {}),
        SYMBOLIC_ASSOCIATIVITY_CSV,
        "symbolic associativity input",
    )
    assert_file_hash(
        inputs.get("rewrite_complex_nodes", {}),
        REWRITE_COMPLEX_NODES,
        "rewrite complex nodes input",
    )
    assert_file_hash(
        inputs.get("rewrite_complex_edges", {}),
        REWRITE_COMPLEX_EDGES,
        "rewrite complex edges input",
    )
    assert_file_hash(
        inputs.get("cell_complex_edges", {}),
        CELL_COMPLEX_EDGES,
        "cell complex edges input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion_manifest@1"
    ):
        raise AssertionError("native-trace-insertion manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("native-trace-insertion manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("native-trace-insertion manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("native-trace-insertion missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("native-trace-insertion index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("native-trace-insertion index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_native_trace_insertion()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
