from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge import (
        BOUNDARY_BRIDGE_CERTIFICATE,
        BOUNDARY_BRIDGE_REPORT,
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        GRAFT_COLUMNS,
        INDEX_PATH,
        MODE_COLUMNS,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        VIRTUAL_GRAFT_OBSERVABLE_CODES,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge import (
        BOUNDARY_BRIDGE_CERTIFICATE,
        BOUNDARY_BRIDGE_REPORT,
        CELL_COMPLEX_EDGES,
        DERIVE_SCRIPT,
        GRAFT_COLUMNS,
        INDEX_PATH,
        MODE_COLUMNS,
        NO_REPAIR_GATE_WORD,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PATH_COLUMNS,
        REWRITE_COMPLEX_EDGES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        VIRTUAL_GRAFT_OBSERVABLE_CODES,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
    )


EXPECTED_OBSERVABLES = {
    "metric_ok_word_count": 26_197,
    "native_good_cell_count": 562,
    "native_no_closed_count": 11_075,
    "virtual_graft_candidate_count": 422,
    "no_repair_no_closed_count": 14_138,
    "native_good_edge_count": 1_694,
    "native_good_component_count": 13,
    "native_left_component_size": 347,
    "native_right_component_size": 185,
    "native_left_to_right_path_exists": 0,
    "virtual_graph_node_count": 984,
    "virtual_graph_edge_count": 3_134,
    "virtual_graph_component_count": 23,
    "virtual_left_to_right_path_exists": 1,
    "virtual_merged_component_size": 925,
    "virtual_merged_native_cell_count": 534,
    "virtual_merged_graft_cell_count": 391,
    "left_right_graft_bridge_candidate_count": 25,
    "direct_boundary_graft_bridge_count": 1,
    "direct_common_neighbor_count": 2,
    "single_31_28_graft_path_exists": 1,
    "single_50_34_graft_path_exists": 1,
    "shortest_graft_path_length": 2,
    "gate_word_variation": 185,
    "gate_word_closed_path_count": 30,
    "gate_word_template_count": 9,
    "exact_virtual_graft_candidate_count": 1,
    "clear_virtual_graft_candidate_count": 4,
    "closed_ge24_template_ge6_graft_candidate_count": 249,
    "min_bridge_candidate_variation": 143,
    "min_virtual_graft_candidate_variation": 143,
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


def row_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS if row[column] != -1)


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    graft = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate.json"
    )
    cells_csv = (OUT_DIR / "aperture_closure_tail_virtual_graft_cells.csv").read_text(
        encoding="utf-8"
    )
    modes_csv = (OUT_DIR / "aperture_closure_tail_virtual_graft_modes.csv").read_text(
        encoding="utf-8"
    )
    paths_csv = (OUT_DIR / "aperture_closure_tail_virtual_graft_paths.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_virtual_graft_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        graft
        != expected[
            "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge"
        ]
    ):
        raise AssertionError("virtual-graft JSON is not reproducible")
    if cells_csv != expected["aperture_closure_tail_virtual_graft_cells_csv"]:
        raise AssertionError("virtual-graft cells CSV is not reproducible")
    if modes_csv != expected["aperture_closure_tail_virtual_graft_modes_csv"]:
        raise AssertionError("virtual-graft modes CSV is not reproducible")
    if paths_csv != expected["aperture_closure_tail_virtual_graft_paths_csv"]:
        raise AssertionError("virtual-graft paths CSV is not reproducible")
    if (
        observables_csv
        != expected["aperture_closure_tail_virtual_graft_observables_csv"]
    ):
        raise AssertionError("virtual-graft observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_certificate"
        ]
    ):
        raise AssertionError("virtual-graft certificate is not reproducible")

    for name in [
        "graft_table",
        "mode_table",
        "path_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"virtual-graft table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge@1"
    ):
        raise AssertionError("virtual-graft report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("virtual-graft layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("virtual-graft all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("virtual-graft checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("virtual-graft report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("virtual-graft report is not reproducible")

    graft_table = np.asarray(tables["graft_table"], dtype=np.int64)
    mode_table = np.asarray(tables["mode_table"], dtype=np.int64)
    path_table = np.asarray(tables["path_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if graft_table.shape != (422, len(GRAFT_COLUMNS)):
        raise AssertionError("virtual-graft cell table shape mismatch")
    if mode_table.shape != (3, len(MODE_COLUMNS)):
        raise AssertionError("virtual-graft mode table shape mismatch")
    if path_table.shape != (6, len(PATH_COLUMNS)):
        raise AssertionError("virtual-graft path table shape mismatch")
    if observable_table.shape != (
        len(VIRTUAL_GRAFT_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("virtual-graft observable table shape mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    expected_observables = {
        VIRTUAL_GRAFT_OBSERVABLE_CODES[key]: value
        for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("virtual-graft observables mismatch")

    graft_rows = table_rows(graft_table, GRAFT_COLUMNS)
    mode_rows = table_rows(mode_table, MODE_COLUMNS)
    path_rows = table_rows(path_table, PATH_COLUMNS)
    native_mode = next(row for row in mode_rows if row["mode_code"] == 0)
    graft_31_mode = next(row for row in mode_rows if row["mode_code"] == 1)
    graft_50_mode = next(row for row in mode_rows if row["mode_code"] == 2)
    if native_mode["left_to_right_path_exists"] != 0:
        raise AssertionError("native mode unexpectedly bridges")
    for mode in [graft_31_mode, graft_50_mode]:
        if mode["left_to_right_path_exists"] != 1:
            raise AssertionError("single virtual-graft mode does not bridge")
        if mode["shortest_left_to_right_path_length"] != 2:
            raise AssertionError("single virtual-graft mode path length mismatch")
        if mode["merged_component_size"] != 925:
            raise AssertionError("single virtual-graft merged size mismatch")

    if sum(row["left_right_bridge_flag"] for row in graft_rows) != 25:
        raise AssertionError("virtual-graft bridge candidate count mismatch")
    if sum(row["direct_boundary_bridge_flag"] for row in graft_rows) != 1:
        raise AssertionError("virtual-graft direct bridge count mismatch")
    if sum(row["exact24_six_all_four_flag"] for row in graft_rows) != 1:
        raise AssertionError("virtual-graft exact target count mismatch")
    if sum(row["clear_flag"] for row in graft_rows) != 4:
        raise AssertionError("virtual-graft clear count mismatch")
    if sum(row["closed_ge24_template_ge6_flag"] for row in graft_rows) != 249:
        raise AssertionError("virtual-graft closed/template count mismatch")

    gate_rows = [row for row in graft_rows if row_word(row) == NO_REPAIR_GATE_WORD]
    if len(gate_rows) != 1:
        raise AssertionError("virtual-graft gate row count mismatch")
    gate_row = gate_rows[0]
    if gate_row["direct_boundary_bridge_flag"] != 1:
        raise AssertionError("virtual-graft gate is not direct boundary bridge")
    if gate_row["left_right_bridge_flag"] != 1:
        raise AssertionError("virtual-graft gate does not bridge left/right")
    if (
        gate_row["trace_signature_total_variation"],
        gate_row["first_return_closed_path_count"],
        gate_row["normalized_tail_template_count"],
    ) != (185, 30, 9):
        raise AssertionError("virtual-graft gate profile mismatch")

    if [row_word(row) for row in path_rows[:3]] != [
        tuple(report["witness"]["shortest_path_words"][0]),
        tuple(report["witness"]["shortest_path_words"][1]),
        tuple(report["witness"]["shortest_path_words"][2]),
    ]:
        raise AssertionError("virtual-graft path witness mismatch")
    if row_word(path_rows[1]) != NO_REPAIR_GATE_WORD:
        raise AssertionError("virtual-graft path does not pass through gate")
    if path_rows[1]["virtual_31_28_flag"] != 1:
        raise AssertionError("virtual-graft 31--28 path flag mismatch")
    if path_rows[4]["virtual_50_34_flag"] != 1:
        raise AssertionError("virtual-graft 50--34 path flag mismatch")

    witness = report.get("witness", {})
    if witness.get("native_component_sizes") != [347, 185, 15, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1]:
        raise AssertionError("virtual-graft native component witness mismatch")
    if witness.get("virtual_component_sizes", [])[:4] != [925, 15, 11, 6]:
        raise AssertionError("virtual-graft virtual component witness mismatch")
    if witness.get("virtual_graft_candidate_count") != 422:
        raise AssertionError("virtual-graft count witness mismatch")
    if witness.get("left_right_graft_bridge_candidate_count") != 25:
        raise AssertionError("virtual-graft bridge witness mismatch")
    if witness.get("shortest_graft_path_length") != 2:
        raise AssertionError("virtual-graft shortest path witness mismatch")
    if witness.get("gate_profile", {}).get("closed_paths") != 30:
        raise AssertionError("virtual-graft gate witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("virtual-graft certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("boundary_bridge_report", {}),
        BOUNDARY_BRIDGE_REPORT,
        "boundary-bridge report input",
    )
    assert_file_hash(
        inputs.get("boundary_bridge_certificate", {}),
        BOUNDARY_BRIDGE_CERTIFICATE,
        "boundary-bridge certificate input",
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
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge_manifest@1"
    ):
        raise AssertionError("virtual-graft manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("virtual-graft manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("virtual-graft manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("virtual-graft missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("virtual-graft index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("virtual-graft index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_virtual_graft_bridge()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
