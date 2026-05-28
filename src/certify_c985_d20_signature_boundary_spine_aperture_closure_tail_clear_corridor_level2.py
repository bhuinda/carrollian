from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2 import (
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        CLEAR_CORRIDOR_CERTIFICATE,
        CLEAR_CORRIDOR_REPORT,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        GATE_PATH_COLUMNS,
        INDEX_PATH,
        LEVEL2_OBSERVABLE_CODES,
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
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2 import (
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        CLEAR_CORRIDOR_CERTIFICATE,
        CLEAR_CORRIDOR_REPORT,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        GATE_PATH_COLUMNS,
        INDEX_PATH,
        LEVEL2_OBSERVABLE_CODES,
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
    "radius0_word_count": 3,
    "radius1_word_count": 288,
    "radius2_word_count": 12463,
    "radius2_total_word_count": 12754,
    "trace_valid_word_count": 9625,
    "delta2_variation_le223_word_count": 1436,
    "repair_chord_candidate_count": 958,
    "no_repair_gate_candidate_count": 478,
    "no_closed_repair_candidate_count": 820,
    "good_cell_count": 138,
    "good_edge_count": 377,
    "good_component_count": 4,
    "selected_component_cell_count": 81,
    "oversplitter_component_cell_count": 55,
    "target_cell_count": 9,
    "radius2_new_target_count": 8,
    "clear_cell_count": 20,
    "oversplitter_component_target_count": 0,
    "selected_to_oversplitter_good_path_exists": 0,
    "no_repair_one_gate_path_count": 2,
    "no_repair_gate_path_length_edges": 4,
    "no_repair_gate_word_variation": 185,
    "no_repair_gate_word_closed_paths": 30,
    "no_repair_gate_word_template_count": 9,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    level2 = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate.json"
    )
    cells_csv = (
        OUT_DIR / "aperture_closure_tail_clear_corridor_level2_cells.csv"
    ).read_text(encoding="utf-8")
    components_csv = (
        OUT_DIR / "aperture_closure_tail_clear_corridor_level2_components.csv"
    ).read_text(encoding="utf-8")
    gate_paths_csv = (
        OUT_DIR / "aperture_closure_tail_clear_corridor_level2_gate_paths.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_clear_corridor_level2_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        level2
        != expected[
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2"
        ]
    ):
        raise AssertionError("level-two clear-corridor JSON is not reproducible")
    if cells_csv != expected["aperture_closure_tail_clear_corridor_level2_cells_csv"]:
        raise AssertionError("level-two clear-corridor cells CSV is not reproducible")
    if (
        components_csv
        != expected["aperture_closure_tail_clear_corridor_level2_components_csv"]
    ):
        raise AssertionError(
            "level-two clear-corridor components CSV is not reproducible"
        )
    if (
        gate_paths_csv
        != expected["aperture_closure_tail_clear_corridor_level2_gate_paths_csv"]
    ):
        raise AssertionError(
            "level-two clear-corridor gate paths CSV is not reproducible"
        )
    if (
        observables_csv
        != expected["aperture_closure_tail_clear_corridor_level2_observables_csv"]
    ):
        raise AssertionError(
            "level-two clear-corridor observables CSV is not reproducible"
        )
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_certificate"
        ]
    ):
        raise AssertionError(
            "level-two clear-corridor certificate is not reproducible"
        )

    for name in [
        "cell_table",
        "component_table",
        "gate_path_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(
                f"level-two clear-corridor table {name} is not reproducible"
            )

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2@1"
    ):
        raise AssertionError("level-two clear-corridor report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("level-two clear-corridor layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("level-two clear-corridor all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("level-two clear-corridor checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("level-two clear-corridor report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("level-two clear-corridor report is not reproducible")

    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    gate_path_table = np.asarray(tables["gate_path_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if cell_table.shape != (138, len(CELL_COLUMNS)):
        raise AssertionError("level-two cell table shape mismatch")
    if component_table.shape != (4, len(COMPONENT_COLUMNS)):
        raise AssertionError("level-two component table shape mismatch")
    if gate_path_table.shape != (10, len(GATE_PATH_COLUMNS)):
        raise AssertionError("level-two gate path table shape mismatch")
    if observable_table.shape != (
        len(LEVEL2_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("level-two observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        LEVEL2_OBSERVABLE_CODES[key]: value
        for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("level-two observables mismatch")

    cell_rows = table_rows(cell_table, CELL_COLUMNS)
    component_rows = table_rows(component_table, COMPONENT_COLUMNS)
    gate_path_rows = table_rows(gate_path_table, GATE_PATH_COLUMNS)
    if sum(row["exact24_six_all_four_flag"] for row in cell_rows) != 9:
        raise AssertionError("level-two target count mismatch")
    if sum(row["clear_flag"] for row in cell_rows) != 20:
        raise AssertionError("level-two clear count mismatch")
    if [row["cell_count"] for row in component_rows] != [81, 55, 1, 1]:
        raise AssertionError("level-two component sizes mismatch")
    selected_component = next(
        row for row in component_rows if row["selected_anchor_flag"] == 1
    )
    oversplitter_component = next(
        row for row in component_rows if row["oversplitter_anchor_count"] == 2
    )
    if selected_component["target_cell_count"] != 9:
        raise AssertionError("level-two selected target count mismatch")
    if oversplitter_component["target_cell_count"] != 0:
        raise AssertionError("level-two oversplitter target count mismatch")
    if selected_component["component_id"] == oversplitter_component["component_id"]:
        raise AssertionError("level-two good components unexpectedly coincide")
    if sum(row["gate_flag"] for row in gate_path_rows) != 2:
        raise AssertionError("level-two gate count mismatch")
    if any(
        row["word_class_code"] == 1 and row["repair_chord_flag"] != 0
        for row in gate_path_rows
    ):
        raise AssertionError("level-two gate unexpectedly has repair-chord support")

    witness = report.get("witness", {})
    if witness.get("good_component_sizes") != [81, 55, 1, 1]:
        raise AssertionError("level-two component-size witness mismatch")
    if witness.get("radius2_new_target_count") != 8:
        raise AssertionError("level-two radius-two target witness mismatch")
    if witness.get("no_repair_gate_profile", {}).get("variation") != 185:
        raise AssertionError("level-two gate witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("level-two certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("clear_corridor_report", {}),
        CLEAR_CORRIDOR_REPORT,
        "clear-corridor report input",
    )
    assert_file_hash(
        inputs.get("clear_corridor_certificate", {}),
        CLEAR_CORRIDOR_CERTIFICATE,
        "clear-corridor certificate input",
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
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2_manifest@1"
    ):
        raise AssertionError("level-two manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("level-two manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("level-two manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("level-two clear-corridor missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("level-two index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("level-two index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_level2()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
