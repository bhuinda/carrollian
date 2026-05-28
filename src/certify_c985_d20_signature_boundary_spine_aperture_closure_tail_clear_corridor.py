from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor import (
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_REPORT,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARTIAL_SPLITTER_CERTIFICATE,
        PARTIAL_SPLITTER_REPORT,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        TRIM_NEIGHBORHOOD_CERTIFICATE,
        TRIM_NEIGHBORHOOD_REPORT,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor import (
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_REPORT,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARTIAL_SPLITTER_CERTIFICATE,
        PARTIAL_SPLITTER_REPORT,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        TRIM_NEIGHBORHOOD_CERTIFICATE,
        TRIM_NEIGHBORHOOD_REPORT,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "anchor_word_count": 3,
    "radius1_total_word_count": 291,
    "trace_valid_word_count": 246,
    "delta2_variation_le223_word_count": 51,
    "repair_chord_admissible_word_count": 45,
    "closed_positive_cell_count": 25,
    "corridor_edge_count": 40,
    "connected_component_count": 2,
    "selected_component_cell_count": 10,
    "oversplitter_component_cell_count": 15,
    "target_cell_count": 1,
    "clear_cell_count": 2,
    "selected_component_clear_count": 2,
    "oversplitter_component_clear_count": 0,
    "underclosed_endpoint13_free_all_four_count": 5,
    "selected_to_oversplitter_path_exists": 0,
    "non_anchor_exact24_six_all_four_count": 0,
    "best_clear_nontarget_variation": 137,
    "best_clear_nontarget_closed_paths": 36,
    "best_clear_nontarget_template_count": 9,
    "oversplitter_underclosed_clearing_min_variation": 175,
    "oversplitter_underclosed_clearing_closed_paths": 8,
    "oversplitter_underclosed_clearing_template_count": 2,
}


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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    corridor = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_closure_tail_clear_corridor.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate.json"
    )
    cells_csv = (OUT_DIR / "aperture_closure_tail_clear_corridor_cells.csv").read_text(
        encoding="utf-8"
    )
    edges_csv = (OUT_DIR / "aperture_closure_tail_clear_corridor_edges.csv").read_text(
        encoding="utf-8"
    )
    components_csv = (
        OUT_DIR / "aperture_closure_tail_clear_corridor_components.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_clear_corridor_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        corridor
        != expected["signature_boundary_spine_aperture_closure_tail_clear_corridor"]
    ):
        raise AssertionError("clear-corridor JSON is not reproducible")
    if cells_csv != expected["aperture_closure_tail_clear_corridor_cells_csv"]:
        raise AssertionError("clear-corridor cells CSV is not reproducible")
    if edges_csv != expected["aperture_closure_tail_clear_corridor_edges_csv"]:
        raise AssertionError("clear-corridor edges CSV is not reproducible")
    if (
        components_csv
        != expected["aperture_closure_tail_clear_corridor_components_csv"]
    ):
        raise AssertionError("clear-corridor components CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_closure_tail_clear_corridor_observables_csv"]
    ):
        raise AssertionError("clear-corridor observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate"
        ]
    ):
        raise AssertionError("clear-corridor certificate is not reproducible")

    for name in [
        "cell_table",
        "edge_table",
        "component_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"clear-corridor table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor@1"
    ):
        raise AssertionError("clear-corridor report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("clear-corridor layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("clear-corridor all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("clear-corridor checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("clear-corridor report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("clear-corridor report is not reproducible")

    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if cell_table.shape != (25, len(CELL_COLUMNS)):
        raise AssertionError("clear-corridor cell table shape mismatch")
    if edge_table.shape != (40, len(EDGE_COLUMNS)):
        raise AssertionError("clear-corridor edge table shape mismatch")
    if component_table.shape != (2, len(COMPONENT_COLUMNS)):
        raise AssertionError("clear-corridor component table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("clear-corridor observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("clear-corridor observables mismatch")

    cell_rows = table_rows(cell_table, CELL_COLUMNS)
    component_rows = table_rows(component_table, COMPONENT_COLUMNS)
    if sum(row["exact24_six_all_four_flag"] for row in cell_rows) != 1:
        raise AssertionError("clear-corridor target count mismatch")
    target = next(row for row in cell_rows if row["exact24_six_all_four_flag"] == 1)
    if target["anchor_selected_flag"] != 1 or target["angel_local_mass"] != 0:
        raise AssertionError("clear-corridor target is not the selected anchor")
    if sum(row["clear_flag"] for row in cell_rows) != 2:
        raise AssertionError("clear-corridor clear-cell count mismatch")
    if any(
        row["source_component_id"] != row["target_component_id"]
        for row in table_rows(edge_table, EDGE_COLUMNS)
    ):
        raise AssertionError("clear-corridor has a cross-component edge")

    selected_component = next(
        row for row in component_rows if row["selected_anchor_flag"] == 1
    )
    oversplitter_component = next(
        row for row in component_rows if row["oversplitter_anchor_count"] == 2
    )
    if selected_component["cell_count"] != 10:
        raise AssertionError("clear-corridor selected component size mismatch")
    if oversplitter_component["cell_count"] != 15:
        raise AssertionError("clear-corridor oversplitter component size mismatch")
    if selected_component["component_id"] == oversplitter_component["component_id"]:
        raise AssertionError("clear-corridor components unexpectedly coincide")
    if selected_component["clear_cell_count"] != 2:
        raise AssertionError("clear-corridor selected clear count mismatch")
    if oversplitter_component["clear_cell_count"] != 0:
        raise AssertionError("clear-corridor oversplitter clear count mismatch")

    witness = report.get("witness", {})
    if witness.get("component_sizes") != [10, 15]:
        raise AssertionError("clear-corridor component-size witness mismatch")
    if witness.get("best_clear_nontarget", {}).get("variation") != 137:
        raise AssertionError("clear-corridor best clear nontarget mismatch")
    if (
        witness.get("best_oversplitter_endpoint13_clearing", {}).get(
            "closed_paths"
        )
        != 8
    ):
        raise AssertionError("clear-corridor oversplitter clearing witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("clear-corridor certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("carrier_splice_report", {}),
        CARRIER_SPLICE_REPORT,
        "carrier splice report input",
    )
    assert_file_hash(
        inputs.get("carrier_splice_certificate", {}),
        CARRIER_SPLICE_CERTIFICATE,
        "carrier splice certificate input",
    )
    assert_file_hash(
        inputs.get("partial_splitter_report", {}),
        PARTIAL_SPLITTER_REPORT,
        "partial splitter report input",
    )
    assert_file_hash(
        inputs.get("partial_splitter_certificate", {}),
        PARTIAL_SPLITTER_CERTIFICATE,
        "partial splitter certificate input",
    )
    assert_file_hash(
        inputs.get("trim_neighborhood_report", {}),
        TRIM_NEIGHBORHOOD_REPORT,
        "trim-neighborhood report input",
    )
    assert_file_hash(
        inputs.get("trim_neighborhood_certificate", {}),
        TRIM_NEIGHBORHOOD_CERTIFICATE,
        "trim-neighborhood certificate input",
    )
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_associativity", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_manifest@1"
    ):
        raise AssertionError("clear-corridor manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("clear-corridor manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("clear-corridor manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("clear-corridor missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("clear-corridor index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("clear-corridor index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
