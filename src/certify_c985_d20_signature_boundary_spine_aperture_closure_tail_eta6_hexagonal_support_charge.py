from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge import (
        ABSTRACT_VERTEX_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OPPOSITE_PAIR_COLUMNS,
        OUT_DIR,
        PRESERVATION_REPORT,
        PRESERVATION_TABLES,
        SIXJ_FRAME_CUT_EDGES,
        SIXJ_FRAME_REPORT,
        SIXJ_FRAME_TABLES,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge import (
        ABSTRACT_VERTEX_COLUMNS,
        DERIVE_SCRIPT,
        EDGE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OPPOSITE_PAIR_COLUMNS,
        OUT_DIR,
        PRESERVATION_REPORT,
        PRESERVATION_TABLES,
        SIXJ_FRAME_CUT_EDGES,
        SIXJ_FRAME_REPORT,
        SIXJ_FRAME_TABLES,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )


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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    eta6 = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_certificate.json"
    )
    edge_csv = (OUT_DIR / "eta6_cut_edges.csv").read_text(encoding="utf-8")
    abstract_vertex_csv = (OUT_DIR / "eta6_abstract_vertex_incidence.csv").read_text(
        encoding="utf-8"
    )
    opposite_pair_csv = (OUT_DIR / "eta6_opposite_edge_pairs.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "eta6_hexagonal_support_charge_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if eta6 != expected["eta6"]:
        raise AssertionError("eta6 JSON is not reproducible")
    if edge_csv != expected["edge_csv"]:
        raise AssertionError("eta6 edge CSV is not reproducible")
    if abstract_vertex_csv != expected["abstract_vertex_csv"]:
        raise AssertionError("eta6 abstract vertex CSV is not reproducible")
    if opposite_pair_csv != expected["opposite_pair_csv"]:
        raise AssertionError("eta6 opposite pair CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 certificate is not reproducible")

    for name in [
        "edge_table",
        "abstract_vertex_table",
        "opposite_pair_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge@1"
    ):
        raise AssertionError("eta6 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 report hash is not reproducible")

    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    abstract_vertex_table = np.asarray(tables["abstract_vertex_table"], dtype=np.int64)
    opposite_pair_table = np.asarray(tables["opposite_pair_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(edge_table.shape) != (6, len(EDGE_COLUMNS)):
        raise AssertionError("eta6 edge table shape mismatch")
    if tuple(abstract_vertex_table.shape) != (4, len(ABSTRACT_VERTEX_COLUMNS)):
        raise AssertionError("eta6 abstract vertex table shape mismatch")
    if tuple(opposite_pair_table.shape) != (3, len(OPPOSITE_PAIR_COLUMNS)):
        raise AssertionError("eta6 opposite pair table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("eta6 observable table shape mismatch")

    edge_rows = table_rows(edge_table, EDGE_COLUMNS)
    vertex_rows = table_rows(abstract_vertex_table, ABSTRACT_VERTEX_COLUMNS)
    opposite_rows = table_rows(opposite_pair_table, OPPOSITE_PAIR_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sorted(
        int(f"{min(row['abstract_u'], row['abstract_v'])}{max(row['abstract_u'], row['abstract_v'])}")
        for row in edge_rows
    ) != [1, 2, 3, 12, 13, 23]:
        raise AssertionError("eta6 K4 edge support mismatch")
    if [row["degree"] for row in vertex_rows] != [3, 3, 3, 3]:
        raise AssertionError("eta6 abstract vertex degree mismatch")
    if [row["boundary_mod2_flag"] for row in vertex_rows] != [1, 1, 1, 1]:
        raise AssertionError("eta6 abstract boundary mismatch")
    if any(row["perfect_matching_flag"] != 1 for row in opposite_rows):
        raise AssertionError("eta6 opposite pair matching mismatch")
    if any(row["source_side_code"] != 1 or row["target_side_code"] != -1 for row in edge_rows):
        raise AssertionError("eta6 relative cut orientation mismatch")
    if {row["undirected_stationary_flux_x1e12"] for row in edge_rows} != {
        170_677_590
    }:
        raise AssertionError("eta6 uniform flux mismatch")

    required_observables = {
        "eta6_edge_count": 6,
        "eta6_nonzero_flag": 1,
        "uniform_flux_flag": 1,
        "per_edge_flux_x1e12": 170_677_590,
        "total_flux_x1e12": 1_024_065_540,
        "transfer_boundary_vertex_count": 12,
        "transfer_cycle_flag": 0,
        "abstract_vertex_count": 4,
        "abstract_edge_count": 6,
        "abstract_mod2_boundary_weight": 4,
        "abstract_cycle_flag": 0,
        "opposite_pair_count": 3,
        "perfect_matching_pair_count": 3,
        "relative_cut_charge_flag": 1,
        "preservation_aggregate_row_count": 606,
        "preservation_decreasing_row_count": 153,
        "preservation_support_changing_row_count": 0,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("sixj_frame_report", {}),
        SIXJ_FRAME_REPORT,
        "sixj frame report input",
    )
    assert_file_hash(
        inputs.get("sixj_frame_cut_edges", {}),
        SIXJ_FRAME_CUT_EDGES,
        "sixj frame cut edges input",
    )
    assert_file_hash(
        inputs.get("sixj_frame_tables", {}),
        SIXJ_FRAME_TABLES,
        "sixj frame tables input",
    )
    assert_file_hash(
        inputs.get("conductance_preservation_report", {}),
        PRESERVATION_REPORT,
        "conductance preservation report input",
    )
    assert_file_hash(
        inputs.get("conductance_preservation_tables", {}),
        PRESERVATION_TABLES,
        "conductance preservation tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge_manifest@1"
    ):
        raise AssertionError("eta6 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hexagonal_support_charge()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
