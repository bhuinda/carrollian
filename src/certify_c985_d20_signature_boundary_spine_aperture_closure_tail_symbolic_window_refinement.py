from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NATIVE_INSERTION_CERTIFICATE,
        NATIVE_INSERTION_REPORT,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        SPLIT_COLUMNS,
        STATUS,
        SUBWINDOW_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_WINDOW_OBSERVABLE_CODES,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement import (
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NATIVE_INSERTION_CERTIFICATE,
        NATIVE_INSERTION_REPORT,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        SPLIT_COLUMNS,
        STATUS,
        SUBWINDOW_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_WINDOW_OBSERVABLE_CODES,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "local_block_symbol_count": 4,
    "subwindow_count": 4,
    "skip_window_count": 2,
    "endpoint_window_count": 2,
    "valid_split_count": 2,
    "repair_split_count": 1,
    "neutral_split_count": 1,
    "selected_inserted_node_id": 31,
    "selected_index_mask": 13,
    "selected_trace_variation": 185,
    "selected_trace_delta_twice": 2,
    "selected_variation_preserving_flag": 1,
    "gate_closed_path_count": 30,
    "gate_template_count": 9,
    "gate_trace_variation": 185,
    "source_node_id": 27,
    "target_node_id": 28,
    "direct_variation": 23,
    "neutral_inserted_node_id": 41,
    "neutral_variation_preserving_flag": 1,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    refinement = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate.json"
    )
    subwindows_csv = (
        OUT_DIR / "aperture_closure_tail_symbolic_window_subwindows.csv"
    ).read_text(encoding="utf-8")
    splits_csv = (
        OUT_DIR / "aperture_closure_tail_symbolic_window_splits.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_symbolic_window_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        refinement
        != expected[
            "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement"
        ]
    ):
        raise AssertionError("symbolic-window-refinement JSON is not reproducible")
    if subwindows_csv != expected["aperture_closure_tail_symbolic_window_subwindows_csv"]:
        raise AssertionError("symbolic-window-refinement subwindows CSV is not reproducible")
    if splits_csv != expected["aperture_closure_tail_symbolic_window_splits_csv"]:
        raise AssertionError("symbolic-window-refinement splits CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_closure_tail_symbolic_window_observables_csv"]
    ):
        raise AssertionError("symbolic-window-refinement observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_certificate"
        ]
    ):
        raise AssertionError("symbolic-window-refinement certificate is not reproducible")

    for name in ["subwindow_table", "split_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"symbolic-window-refinement table {name} is not reproducible"
            )

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement@1"
    ):
        raise AssertionError("symbolic-window-refinement report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("symbolic-window-refinement layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("symbolic-window-refinement all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("symbolic-window-refinement checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("symbolic-window-refinement report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("symbolic-window-refinement report is not reproducible")

    subwindow_table = np.asarray(tables["subwindow_table"], dtype=np.int64)
    split_table = np.asarray(tables["split_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if subwindow_table.shape != (4, len(SUBWINDOW_COLUMNS)):
        raise AssertionError("symbolic-window-refinement subwindow table shape mismatch")
    if split_table.shape != (2, len(SPLIT_COLUMNS)):
        raise AssertionError("symbolic-window-refinement split table shape mismatch")
    if observable_table.shape != (
        len(SYMBOLIC_WINDOW_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("symbolic-window-refinement observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        SYMBOLIC_WINDOW_OBSERVABLE_CODES[key]: value
        for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("symbolic-window-refinement observables mismatch")

    subwindow_rows = table_rows(subwindow_table, SUBWINDOW_COLUMNS)
    split_rows = table_rows(split_table, SPLIT_COLUMNS)
    if [row["canonical_node_id"] for row in subwindow_rows] != [27, 41, 31, 28]:
        raise AssertionError("symbolic-window-refinement subwindow nodes mismatch")
    if [
        (
            row["first_symbol_id"],
            row["second_symbol_id"],
            row["third_symbol_id"],
        )
        for row in subwindow_rows
    ] != [(3, 2, 1), (3, 2, 4), (3, 1, 4), (2, 1, 4)]:
        raise AssertionError("symbolic-window-refinement subwindow symbols mismatch")

    selected = next(row for row in split_rows if row["selected_refinement_flag"] == 1)
    neutral = next(row for row in split_rows if row["selected_refinement_flag"] == 0)
    if (
        selected["inserted_node_id"],
        selected["index_mask"],
        selected["repair_31_28_flag"],
        selected["valid_rewrite_split_flag"],
        selected["variation_preserving_flag"],
    ) != (31, 13, 1, 1, 1):
        raise AssertionError("symbolic-window-refinement selected split mismatch")
    if trace_from_row(selected) != SELECTED_TRACE:
        raise AssertionError("symbolic-window-refinement selected trace mismatch")
    if (
        neutral["inserted_node_id"],
        neutral["index_mask"],
        neutral["repair_31_28_flag"],
        neutral["valid_rewrite_split_flag"],
        neutral["variation_preserving_flag"],
    ) != (41, 11, 0, 1, 1):
        raise AssertionError("symbolic-window-refinement neutral split mismatch")
    if sum(row["repair_31_28_flag"] for row in split_rows) != 1:
        raise AssertionError("symbolic-window-refinement repair split count mismatch")
    if sum(row["valid_rewrite_split_flag"] for row in split_rows) != 2:
        raise AssertionError("symbolic-window-refinement valid split count mismatch")

    witness = report.get("witness", {})
    if witness.get("local_block") != [3, 2, 1, 4]:
        raise AssertionError("symbolic-window-refinement local block witness mismatch")
    if witness.get("selected_refinement", {}).get("node") != 31:
        raise AssertionError("symbolic-window-refinement selected witness mismatch")
    if witness.get("selected_refinement", {}).get("trace") != list(SELECTED_TRACE):
        raise AssertionError("symbolic-window-refinement selected trace witness mismatch")
    if witness.get("neutral_refinement_node") != 41:
        raise AssertionError("symbolic-window-refinement neutral witness mismatch")
    if witness.get("gate_profile", {}).get("closed_paths") != 30:
        raise AssertionError("symbolic-window-refinement gate closure witness mismatch")
    if witness.get("gate_profile", {}).get("templates") != 9:
        raise AssertionError("symbolic-window-refinement gate template witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("symbolic-window-refinement certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("native_trace_insertion_report", {}),
        NATIVE_INSERTION_REPORT,
        "native trace insertion report input",
    )
    assert_file_hash(
        inputs.get("native_trace_insertion_certificate", {}),
        NATIVE_INSERTION_CERTIFICATE,
        "native trace insertion certificate input",
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
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement_manifest@1"
    ):
        raise AssertionError("symbolic-window-refinement manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("symbolic-window-refinement manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("symbolic-window-refinement manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("symbolic-window-refinement missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("symbolic-window-refinement index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("symbolic-window-refinement index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_symbolic_window_refinement()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
