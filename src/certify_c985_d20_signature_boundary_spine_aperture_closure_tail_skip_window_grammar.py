from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LEFT_REPAIR_BOUNDARY_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        REPAIR_SPLIT_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        RIGHT_REPAIR_BOUNDARY_WORD,
        SKIP_WINDOW_OBSERVABLE_CODES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_WINDOW_CERTIFICATE,
        SYMBOLIC_WINDOW_REPORT,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar import (
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        LEFT_REPAIR_BOUNDARY_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        REPAIR_SPLIT_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        RIGHT_REPAIR_BOUNDARY_WORD,
        SKIP_WINDOW_OBSERVABLE_CODES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_WINDOW_CERTIFICATE,
        SYMBOLIC_WINDOW_REPORT,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "alphabet_size": 6,
    "four_symbol_block_count": 1_296,
    "valid_split_count": 1_800,
    "valid_split_block_count": 1_170,
    "valid_variation_preserving_split_count": 556,
    "repair_split_count": 32,
    "repair_split_block_count": 32,
    "repair_31_28_split_count": 16,
    "repair_50_34_split_count": 16,
    "repair_variation_preserving_split_count": 4,
    "boundary_union_word_count": 234_678,
    "trace_failure_word_count": 68_103,
    "bad_metric_word_count": 140_378,
    "metric_ok_word_count": 26_197,
    "native_repair_metric_count": 11_637,
    "derived_repair_metric_count": 20_744,
    "native_good_cell_count": 562,
    "derived_closed_cell_count": 846,
    "grammar_good_cell_count": 846,
    "derived_only_closed_cell_count": 284,
    "virtual_candidate_count": 422,
    "grammar_graph_edge_count": 2_549,
    "grammar_component_count": 22,
    "merged_component_size": 787,
    "merged_native_cell_count": 532,
    "merged_derived_only_cell_count": 255,
    "left_to_right_path_exists": 1,
    "shortest_path_length": 2,
    "gate_native_repair_flag": 0,
    "gate_derived_repair_flag": 1,
    "gate_closed_path_count": 30,
    "gate_template_count": 9,
}

EXPECTED_COMPONENT_SIZES = [
    787,
    15,
    11,
    6,
    4,
    2,
    2,
    2,
    2,
    2,
    2,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
]


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


def row_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in CELL_COLUMNS if column.startswith("word_symbol") and row[column] != -1)


def path_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in PATH_COLUMNS if column.startswith("word_symbol") and row[column] != -1)


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    grammar = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate.json"
    )
    repair_splits_csv = (
        OUT_DIR / "aperture_closure_tail_skip_window_repair_splits.csv"
    ).read_text(encoding="utf-8")
    cells_csv = (OUT_DIR / "aperture_closure_tail_skip_window_cells.csv").read_text(
        encoding="utf-8"
    )
    components_csv = (
        OUT_DIR / "aperture_closure_tail_skip_window_components.csv"
    ).read_text(encoding="utf-8")
    path_csv = (OUT_DIR / "aperture_closure_tail_skip_window_path.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_skip_window_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        grammar
        != expected[
            "signature_boundary_spine_aperture_closure_tail_skip_window_grammar"
        ]
    ):
        raise AssertionError("skip-window grammar JSON is not reproducible")
    if (
        repair_splits_csv
        != expected["aperture_closure_tail_skip_window_repair_splits_csv"]
    ):
        raise AssertionError("skip-window repair splits CSV is not reproducible")
    if cells_csv != expected["aperture_closure_tail_skip_window_cells_csv"]:
        raise AssertionError("skip-window cells CSV is not reproducible")
    if components_csv != expected["aperture_closure_tail_skip_window_components_csv"]:
        raise AssertionError("skip-window components CSV is not reproducible")
    if path_csv != expected["aperture_closure_tail_skip_window_path_csv"]:
        raise AssertionError("skip-window path CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_skip_window_observables_csv"]:
        raise AssertionError("skip-window observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_skip_window_grammar_certificate"
        ]
    ):
        raise AssertionError("skip-window certificate is not reproducible")

    for name in [
        "repair_split_table",
        "cell_table",
        "component_table",
        "path_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"skip-window table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar@1"
    ):
        raise AssertionError("skip-window report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("skip-window layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("skip-window all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("skip-window checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("skip-window report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("skip-window report is not reproducible")

    repair_split_table = np.asarray(tables["repair_split_table"], dtype=np.int64)
    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    path_table = np.asarray(tables["path_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if repair_split_table.shape != (32, len(REPAIR_SPLIT_COLUMNS)):
        raise AssertionError("skip-window repair split table shape mismatch")
    if cell_table.shape != (846, len(CELL_COLUMNS)):
        raise AssertionError("skip-window cell table shape mismatch")
    if component_table.shape != (22, len(COMPONENT_COLUMNS)):
        raise AssertionError("skip-window component table shape mismatch")
    if path_table.shape != (3, len(PATH_COLUMNS)):
        raise AssertionError("skip-window path table shape mismatch")
    if observable_table.shape != (
        len(SKIP_WINDOW_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("skip-window observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        SKIP_WINDOW_OBSERVABLE_CODES[key]: value
        for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("skip-window observables mismatch")

    repair_rows = table_rows(repair_split_table, REPAIR_SPLIT_COLUMNS)
    cell_rows = table_rows(cell_table, CELL_COLUMNS)
    component_rows = table_rows(component_table, COMPONENT_COLUMNS)
    path_rows = table_rows(path_table, PATH_COLUMNS)
    if sum(row["repair_31_28_flag"] for row in repair_rows) != 16:
        raise AssertionError("skip-window 31--28 repair split count mismatch")
    if sum(row["repair_50_34_flag"] for row in repair_rows) != 16:
        raise AssertionError("skip-window 50--34 repair split count mismatch")
    if sum(row["variation_preserving_flag"] for row in repair_rows) != 4:
        raise AssertionError("skip-window variation-preserving repair split mismatch")
    if [row["cell_count"] for row in component_rows] != EXPECTED_COMPONENT_SIZES:
        raise AssertionError("skip-window component sizes mismatch")
    merged = next(row for row in component_rows if row["merged_boundary_flag"] == 1)
    if (
        merged["cell_count"],
        merged["native_cell_count"],
        merged["derived_only_cell_count"],
        merged["gate_word_flag"],
    ) != (787, 532, 255, 1):
        raise AssertionError("skip-window merged component mismatch")
    if sum(row["derived_only_flag"] for row in cell_rows) != 284:
        raise AssertionError("skip-window derived-only cell count mismatch")
    gate_rows = [row for row in cell_rows if row["gate_word_flag"] == 1]
    if len(gate_rows) != 1:
        raise AssertionError("skip-window gate row count mismatch")
    gate = gate_rows[0]
    if (
        gate["native_repair_flag"],
        gate["derived_repair_flag"],
        gate["first_return_closed_path_count"],
        gate["normalized_tail_template_count"],
    ) != (0, 1, 30, 9):
        raise AssertionError("skip-window gate profile mismatch")
    if [path_word(row) for row in path_rows] != [
        LEFT_REPAIR_BOUNDARY_WORD,
        tuple(report["witness"]["gate_profile"]["word"]),
        RIGHT_REPAIR_BOUNDARY_WORD,
    ]:
        raise AssertionError("skip-window shortest path mismatch")
    if path_rows[1]["derived_only_flag"] != 1:
        raise AssertionError("skip-window path gate is not derived-only")

    witness = report.get("witness", {})
    if witness.get("repair_split_count") != 32:
        raise AssertionError("skip-window repair split witness mismatch")
    if witness.get("grammar_good_cell_count") != 846:
        raise AssertionError("skip-window grammar-good witness mismatch")
    if witness.get("derived_only_closed_cell_count") != 284:
        raise AssertionError("skip-window derived-only witness mismatch")
    if witness.get("component_sizes") != EXPECTED_COMPONENT_SIZES:
        raise AssertionError("skip-window component witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("skip-window certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("symbolic_window_report", {}),
        SYMBOLIC_WINDOW_REPORT,
        "symbolic-window report input",
    )
    assert_file_hash(
        inputs.get("symbolic_window_certificate", {}),
        SYMBOLIC_WINDOW_CERTIFICATE,
        "symbolic-window certificate input",
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
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar_manifest@1"
    ):
        raise AssertionError("skip-window manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("skip-window manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("skip-window manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("skip-window missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("skip-window index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("skip-window index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_skip_window_grammar()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
