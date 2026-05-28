from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search import (
        BRIDGE_COLUMNS,
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        GATE_OBSERVABLE_CODES,
        INDEX_PATH,
        LEVEL2_CERTIFICATE,
        LEVEL2_REPORT,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search import (
        BRIDGE_COLUMNS,
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        GATE_OBSERVABLE_CODES,
        INDEX_PATH,
        LEVEL2_CERTIFICATE,
        LEVEL2_REPORT,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "radius0_word_count": 1,
    "radius1_word_count": 94,
    "radius2_word_count": 3971,
    "radius3_word_count": 101564,
    "gate_neighborhood_total_word_count": 105630,
    "trace_valid_word_count": 75925,
    "delta2_variation_le223_word_count": 16842,
    "repair_chord_candidate_count": 1022,
    "no_repair_candidate_count": 15820,
    "no_closed_repair_candidate_count": 931,
    "good_cell_count": 91,
    "good_edge_count": 189,
    "good_component_count": 6,
    "left_component_cell_count": 52,
    "right_component_cell_count": 35,
    "target_cell_count": 3,
    "left_component_target_count": 3,
    "right_component_target_count": 0,
    "min_target_variation": 195,
    "clear_cell_count": 4,
    "left_to_right_good_path_exists": 0,
    "one_no_repair_gate_bridge_exists": 1,
    "gate_word_variation": 185,
    "gate_word_closed_paths": 30,
    "gate_word_template_count": 9,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    gate_repair = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_gate_repair_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate.json"
    )
    cells_csv = (OUT_DIR / "aperture_closure_tail_gate_repair_cells.csv").read_text(
        encoding="utf-8"
    )
    components_csv = (
        OUT_DIR / "aperture_closure_tail_gate_repair_components.csv"
    ).read_text(encoding="utf-8")
    bridge_csv = (OUT_DIR / "aperture_closure_tail_gate_repair_bridge.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_gate_repair_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_gate_repair_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        gate_repair
        != expected["signature_boundary_spine_aperture_closure_tail_gate_repair_search"]
    ):
        raise AssertionError("gate-repair JSON is not reproducible")
    if cells_csv != expected["aperture_closure_tail_gate_repair_cells_csv"]:
        raise AssertionError("gate-repair cells CSV is not reproducible")
    if components_csv != expected["aperture_closure_tail_gate_repair_components_csv"]:
        raise AssertionError("gate-repair components CSV is not reproducible")
    if bridge_csv != expected["aperture_closure_tail_gate_repair_bridge_csv"]:
        raise AssertionError("gate-repair bridge CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_gate_repair_observables_csv"]:
        raise AssertionError("gate-repair observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_gate_repair_search_certificate"
        ]
    ):
        raise AssertionError("gate-repair certificate is not reproducible")

    for name in [
        "cell_table",
        "component_table",
        "bridge_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"gate-repair table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search@1"
    ):
        raise AssertionError("gate-repair report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("gate-repair layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("gate-repair all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("gate-repair checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("gate-repair report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("gate-repair report is not reproducible")

    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    bridge_table = np.asarray(tables["bridge_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if cell_table.shape != (91, len(CELL_COLUMNS)):
        raise AssertionError("gate-repair cell table shape mismatch")
    if component_table.shape != (6, len(COMPONENT_COLUMNS)):
        raise AssertionError("gate-repair component table shape mismatch")
    if bridge_table.shape != (3, len(BRIDGE_COLUMNS)):
        raise AssertionError("gate-repair bridge table shape mismatch")
    if observable_table.shape != (len(GATE_OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("gate-repair observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        GATE_OBSERVABLE_CODES[key]: value
        for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("gate-repair observables mismatch")

    cell_rows = table_rows(cell_table, CELL_COLUMNS)
    component_rows = table_rows(component_table, COMPONENT_COLUMNS)
    bridge_rows = table_rows(bridge_table, BRIDGE_COLUMNS)
    if [row["cell_count"] for row in component_rows] != [52, 35, 1, 1, 1, 1]:
        raise AssertionError("gate-repair component sizes mismatch")
    left_component = next(row for row in component_rows if row["left_boundary_flag"] == 1)
    right_component = next(row for row in component_rows if row["right_boundary_flag"] == 1)
    if left_component["component_id"] == right_component["component_id"]:
        raise AssertionError("gate-repair left/right components unexpectedly coincide")
    if left_component["target_cell_count"] != 3:
        raise AssertionError("gate-repair left target count mismatch")
    if right_component["target_cell_count"] != 0:
        raise AssertionError("gate-repair right target count mismatch")
    if sum(row["exact24_six_all_four_flag"] for row in cell_rows) != 3:
        raise AssertionError("gate-repair target count mismatch")
    if min(
        row["trace_signature_total_variation"]
        for row in cell_rows
        if row["exact24_six_all_four_flag"] == 1
    ) != 195:
        raise AssertionError("gate-repair min target variation mismatch")
    if sum(row["gate_flag"] for row in bridge_rows) != 1:
        raise AssertionError("gate-repair bridge gate count mismatch")
    if bridge_rows[1]["repair_chord_flag"] != 0:
        raise AssertionError("gate-repair center word unexpectedly has repair chord")

    witness = report.get("witness", {})
    if witness.get("good_component_sizes") != [52, 35, 1, 1, 1, 1]:
        raise AssertionError("gate-repair component-size witness mismatch")
    if witness.get("min_target_variation") != 195:
        raise AssertionError("gate-repair target witness mismatch")
    if witness.get("gate_profile", {}).get("closed_paths") != 30:
        raise AssertionError("gate-repair profile witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("gate-repair certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("level2_report", {}), LEVEL2_REPORT, "level2 report input")
    assert_file_hash(inputs.get("level2_certificate", {}), LEVEL2_CERTIFICATE, "level2 certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_associativity", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search_manifest@1"
    ):
        raise AssertionError("gate-repair manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("gate-repair manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("gate-repair manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("gate-repair missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("gate-repair index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("gate-repair index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_gate_repair_search()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
