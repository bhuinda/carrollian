from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search import (
        BRIDGE_OBSERVABLE_CODES,
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        GATE_REPAIR_CERTIFICATE,
        GATE_REPAIR_REPORT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        STRICT_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search import (
        BRIDGE_OBSERVABLE_CODES,
        CELL_COLUMNS,
        CELL_COMPLEX_EDGES,
        COMPONENT_COLUMNS,
        DERIVE_SCRIPT,
        GATE_REPAIR_CERTIFICATE,
        GATE_REPAIR_REPORT,
        INDEX_PATH,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        STRICT_COLUMNS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "left_radius0_word_count": 1,
    "left_radius1_word_count": 103,
    "left_radius2_word_count": 4_810,
    "left_radius3_word_count": 136_869,
    "right_radius0_word_count": 1,
    "right_radius1_word_count": 94,
    "right_radius2_word_count": 3_971,
    "right_radius3_word_count": 101_567,
    "left_total_word_count": 141_783,
    "right_total_word_count": 105_633,
    "union_word_count": 234_678,
    "intersection_word_count": 12_738,
    "trace_valid_word_count": 166_575,
    "delta2_variation_le223_word_count": 26_197,
    "repair_chord_candidate_count": 11_637,
    "no_repair_candidate_count": 14_560,
    "no_closed_repair_candidate_count": 11_075,
    "good_cell_count": 562,
    "good_edge_count": 1_694,
    "good_component_count": 13,
    "left_component_cell_count": 347,
    "right_component_cell_count": 185,
    "target_cell_count": 19,
    "left_component_target_count": 18,
    "right_component_target_count": 0,
    "min_target_variation": 137,
    "clear_cell_count": 39,
    "left_neighbor_good_count": 8,
    "right_neighbor_good_count": 6,
    "strict_two_cell_bridge_count": 0,
    "left_to_right_good_path_exists": 0,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    bridge = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate.json"
    )
    cells_csv = (OUT_DIR / "aperture_closure_tail_boundary_bridge_cells.csv").read_text(
        encoding="utf-8"
    )
    components_csv = (
        OUT_DIR / "aperture_closure_tail_boundary_bridge_components.csv"
    ).read_text(encoding="utf-8")
    strict_csv = (
        OUT_DIR / "aperture_closure_tail_boundary_bridge_strict_candidates.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_boundary_bridge_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        bridge
        != expected[
            "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search"
        ]
    ):
        raise AssertionError("boundary-bridge JSON is not reproducible")
    if cells_csv != expected["aperture_closure_tail_boundary_bridge_cells_csv"]:
        raise AssertionError("boundary-bridge cells CSV is not reproducible")
    if components_csv != expected["aperture_closure_tail_boundary_bridge_components_csv"]:
        raise AssertionError("boundary-bridge components CSV is not reproducible")
    if (
        strict_csv
        != expected["aperture_closure_tail_boundary_bridge_strict_candidates_csv"]
    ):
        raise AssertionError("boundary-bridge strict candidates CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_closure_tail_boundary_bridge_observables_csv"]
    ):
        raise AssertionError("boundary-bridge observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_certificate"
        ]
    ):
        raise AssertionError("boundary-bridge certificate is not reproducible")

    for name in [
        "cell_table",
        "component_table",
        "strict_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"boundary-bridge table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search@1"
    ):
        raise AssertionError("boundary-bridge report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("boundary-bridge layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("boundary-bridge all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("boundary-bridge checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("boundary-bridge report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("boundary-bridge report is not reproducible")

    cell_table = np.asarray(tables["cell_table"], dtype=np.int64)
    component_table = np.asarray(tables["component_table"], dtype=np.int64)
    strict_table = np.asarray(tables["strict_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if cell_table.shape != (562, len(CELL_COLUMNS)):
        raise AssertionError("boundary-bridge cell table shape mismatch")
    if component_table.shape != (13, len(COMPONENT_COLUMNS)):
        raise AssertionError("boundary-bridge component table shape mismatch")
    if strict_table.shape != (0, len(STRICT_COLUMNS)):
        raise AssertionError("boundary-bridge strict table shape mismatch")
    if observable_table.shape != (
        len(BRIDGE_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("boundary-bridge observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        BRIDGE_OBSERVABLE_CODES[key]: value
        for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("boundary-bridge observables mismatch")

    cell_rows = table_rows(cell_table, CELL_COLUMNS)
    component_rows = table_rows(component_table, COMPONENT_COLUMNS)
    strict_rows = table_rows(strict_table, STRICT_COLUMNS)
    component_sizes = [row["cell_count"] for row in component_rows]
    if component_sizes != [347, 185, 15, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1]:
        raise AssertionError("boundary-bridge component sizes mismatch")
    left_component = next(row for row in component_rows if row["left_boundary_flag"] == 1)
    right_component = next(
        row for row in component_rows if row["right_boundary_flag"] == 1
    )
    if left_component["component_id"] == right_component["component_id"]:
        raise AssertionError("boundary-bridge left/right components unexpectedly coincide")
    if left_component["cell_count"] != 347:
        raise AssertionError("boundary-bridge left component size mismatch")
    if right_component["cell_count"] != 185:
        raise AssertionError("boundary-bridge right component size mismatch")
    if left_component["target_cell_count"] != 18:
        raise AssertionError("boundary-bridge left target count mismatch")
    if right_component["target_cell_count"] != 0:
        raise AssertionError("boundary-bridge right target count mismatch")
    if sum(row["exact24_six_all_four_flag"] for row in cell_rows) != 19:
        raise AssertionError("boundary-bridge target count mismatch")
    if min(
        row["trace_signature_total_variation"]
        for row in cell_rows
        if row["exact24_six_all_four_flag"] == 1
    ) != 137:
        raise AssertionError("boundary-bridge min target variation mismatch")
    if sum(row["clear_flag"] for row in cell_rows) != 39:
        raise AssertionError("boundary-bridge clear count mismatch")
    if sum(row["left_neighbor_flag"] for row in cell_rows) != 8:
        raise AssertionError("boundary-bridge left neighbor count mismatch")
    if sum(row["right_neighbor_flag"] for row in cell_rows) != 6:
        raise AssertionError("boundary-bridge right neighbor count mismatch")
    if strict_rows:
        raise AssertionError("boundary-bridge unexpectedly has strict candidates")

    witness = report.get("witness", {})
    if witness.get("good_component_sizes") != component_sizes:
        raise AssertionError("boundary-bridge component-size witness mismatch")
    if witness.get("strict_two_cell_bridge_count") != 0:
        raise AssertionError("boundary-bridge strict bridge witness mismatch")
    if witness.get("target_count") != 19:
        raise AssertionError("boundary-bridge target-count witness mismatch")
    if witness.get("left_component_target_count") != 18:
        raise AssertionError("boundary-bridge left target witness mismatch")
    if witness.get("right_component_target_count") != 0:
        raise AssertionError("boundary-bridge right target witness mismatch")
    if witness.get("min_target_variation") != 137:
        raise AssertionError("boundary-bridge target variation witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("boundary-bridge certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("gate_repair_report", {}),
        GATE_REPAIR_REPORT,
        "gate-repair report input",
    )
    assert_file_hash(
        inputs.get("gate_repair_certificate", {}),
        GATE_REPAIR_CERTIFICATE,
        "gate-repair certificate input",
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
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search_manifest@1"
    ):
        raise AssertionError("boundary-bridge manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("boundary-bridge manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("boundary-bridge manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("boundary-bridge missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("boundary-bridge index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("boundary-bridge index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_boundary_bridge_search()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
