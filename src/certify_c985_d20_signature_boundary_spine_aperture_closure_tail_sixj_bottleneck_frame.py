from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame import (
        CENTER_COORDINATE_KEYS,
        CUT_EDGE_COLUMNS,
        DERIVE_SCRIPT,
        FINAL_MULTIFUSION_REPORT,
        INDEX_PATH,
        MOG_EDGE_COLUMNS,
        MOG_RESOLVENT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SECOND_WINDOW_PROMOTION_STATES,
        SECOND_WINDOW_TRANSFER_CERTIFICATE,
        SECOND_WINDOW_TRANSFER_CENTERS,
        SECOND_WINDOW_TRANSFER_EDGES,
        SECOND_WINDOW_TRANSFER_REPORT,
        SECOND_WINDOW_TRANSFER_STATES,
        SECOND_WINDOW_TRANSFER_TABLES,
        SECTOR_FRAME_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WU_SPINH_6J_MARKING,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame import (
        CENTER_COORDINATE_KEYS,
        CUT_EDGE_COLUMNS,
        DERIVE_SCRIPT,
        FINAL_MULTIFUSION_REPORT,
        INDEX_PATH,
        MOG_EDGE_COLUMNS,
        MOG_RESOLVENT,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SECOND_WINDOW_PROMOTION_STATES,
        SECOND_WINDOW_TRANSFER_CERTIFICATE,
        SECOND_WINDOW_TRANSFER_CENTERS,
        SECOND_WINDOW_TRANSFER_EDGES,
        SECOND_WINDOW_TRANSFER_REPORT,
        SECOND_WINDOW_TRANSFER_STATES,
        SECOND_WINDOW_TRANSFER_TABLES,
        SECTOR_FRAME_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WU_SPINH_6J_MARKING,
        build_payloads,
        self_hash,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    frame = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_certificate.json"
    )
    cut_edges_csv = (OUT_DIR / "sixj_bottleneck_cut_edges.csv").read_text(
        encoding="utf-8"
    )
    sector_frame_csv = (OUT_DIR / "sixj_abstract_sector_frame.csv").read_text(
        encoding="utf-8"
    )
    mog_edges_csv = (OUT_DIR / "sixj_mog_k4_edges.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "sixj_frame_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if frame != expected["sixj_frame"]:
        raise AssertionError("sixj bottleneck frame JSON is not reproducible")
    if cut_edges_csv != expected["sixj_cut_edges_csv"]:
        raise AssertionError("sixj cut-edge CSV is not reproducible")
    if sector_frame_csv != expected["sixj_abstract_sector_frame_csv"]:
        raise AssertionError("sixj abstract sector-frame CSV is not reproducible")
    if mog_edges_csv != expected["sixj_mog_k4_edges_csv"]:
        raise AssertionError("sixj MOG K4 edge CSV is not reproducible")
    if observables_csv != expected["sixj_observables_csv"]:
        raise AssertionError("sixj observable CSV is not reproducible")
    if certificate != expected["sixj_certificate"]:
        raise AssertionError("sixj certificate is not reproducible")

    for name in [
        "sector_table",
        "mog_table",
        "cut_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"sixj table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame@1"
    ):
        raise AssertionError("sixj report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("sixj bottleneck frame is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sixj all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("sixj checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("sixj report hash is not reproducible")

    sector_table = np.asarray(tables["sector_table"], dtype=np.int64)
    mog_table = np.asarray(tables["mog_table"], dtype=np.int64)
    cut_table = np.asarray(tables["cut_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(sector_table.shape) != (6, len(SECTOR_FRAME_COLUMNS)):
        raise AssertionError("sixj sector table shape mismatch")
    if tuple(mog_table.shape) != (6, len(MOG_EDGE_COLUMNS)):
        raise AssertionError("sixj MOG table shape mismatch")
    if tuple(cut_table.shape) != (6, len(CUT_EDGE_COLUMNS)):
        raise AssertionError("sixj cut table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("sixj observable table shape mismatch")

    sector_rows = table_rows(sector_table, SECTOR_FRAME_COLUMNS)
    mog_rows = table_rows(mog_table, MOG_EDGE_COLUMNS)
    cut_rows = table_rows(cut_table, CUT_EDGE_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sorted((row["tetra_edge_u"], row["tetra_edge_v"]) for row in sector_rows) != [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    ]:
        raise AssertionError("sixj abstract sector frame is not K4")
    if sorted((row["column_a"], row["column_b"]) for row in mog_rows) != [
        (1, 3),
        (1, 4),
        (1, 5),
        (3, 4),
        (3, 5),
        (4, 5),
    ]:
        raise AssertionError("sixj MOG carrier is not the certified K4")
    if sum(row["wu_radical_edge_flag"] for row in mog_rows) != 1:
        raise AssertionError("sixj MOG carrier radical edge mismatch")
    if sum(row["wu_radical_opposite_edge_flag"] for row in mog_rows) != 1:
        raise AssertionError("sixj MOG carrier radical-opposite edge mismatch")

    cut_flux = sum(row["undirected_stationary_flux_x1e12"] for row in cut_rows)
    if cut_flux != 1_024_065_540:
        raise AssertionError("sixj cut flux sum mismatch")
    if {
        row["undirected_stationary_flux_x1e12"] for row in cut_rows
    } != {170_677_590}:
        raise AssertionError("sixj cut flux is not uniform across six edges")
    if not all(
        row["derived_transition_flag"] == 1
        and row["promoted_transition_flag"] == 1
        and row["old_spectral_cut_edge_flag"] == 1
        and row["spectral_cut_edge_flag"] == 1
        for row in cut_rows
    ):
        raise AssertionError("sixj cut-edge lineage mismatch")
    if not all(
        row["source_side_code"] == 1 and row["target_side_code"] == -1
        for row in cut_rows
    ):
        raise AssertionError("sixj cut edges do not cross positive to negative side")
    if sorted(row["target_edit_length"] for row in cut_rows) != [1, 1, 1, 1, 1, 1]:
        raise AssertionError("sixj cut-edge edit target lengths changed")

    required_observables = {
        "h6_sector_count": 6,
        "abstract_tetrahedron_vertex_count": 4,
        "abstract_tetrahedron_edge_count": 6,
        "lambda2_h6_address_count": 15,
        "spin12_big_cell_dimension": 16,
        "d20_boundary_face_count": 20,
        "symbolic_canonical_triple_count": 56,
        "c985_simple_count": 985,
        "c985_object_count": 6,
        "second_window_transfer_state_count": 798,
        "second_window_transfer_edge_count": 2_523,
        "second_window_cut_edge_count": 6,
        "second_window_cut_flux_x1e12": 1_024_065_540,
        "per_cut_edge_flux_x1e12": 170_677_590,
        "old_cut_edge_count": 6,
        "promoted_cut_edge_count": 6,
        "cut_centers_coincide": 1,
        "all_spin_one_6j_numerator": 1,
        "all_spin_one_6j_denominator": 6,
        "all_spin_one_f_numerator": 1,
        "all_spin_one_f_denominator": 2,
        "w_d6_order": 23_040,
        "be3_order": 9_216,
        "mog_k4_vertex_count": 4,
        "mog_k4_edge_count": 6,
        "final_multifusion_certified": 1,
        "pentagon_length_four_chain_count": 16_837_352_591_360,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"sixj observable {key} mismatch")

    transfer_report = load_json(SECOND_WINDOW_TRANSFER_REPORT)
    if not all(
        transfer_report["witness"]["cut_center"][key]
        == transfer_report["witness"]["promoted_cut_center"][key]
        for key in CENTER_COORDINATE_KEYS
    ):
        raise AssertionError("sixj input transfer centers do not coincide")
    if certificate.get("status") != STATUS:
        raise AssertionError("sixj certificate status mismatch")
    if "C985 integration into the normal lowered-scene JSON compiler pathway" not in (
        report.get("closure_boundary", {})
        .get("does_not_certify_because_not_required", [])
    ):
        raise AssertionError("sixj compiler boundary is not explicit")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("second_window_transfer_report", {}),
        SECOND_WINDOW_TRANSFER_REPORT,
        "second-window transfer report input",
    )
    assert_file_hash(
        inputs.get("second_window_transfer_certificate", {}),
        SECOND_WINDOW_TRANSFER_CERTIFICATE,
        "second-window transfer certificate input",
    )
    assert_file_hash(
        inputs.get("second_window_transfer_states", {}),
        SECOND_WINDOW_TRANSFER_STATES,
        "second-window transfer states input",
    )
    assert_file_hash(
        inputs.get("second_window_transfer_edges", {}),
        SECOND_WINDOW_TRANSFER_EDGES,
        "second-window transfer edges input",
    )
    assert_file_hash(
        inputs.get("second_window_transfer_centers", {}),
        SECOND_WINDOW_TRANSFER_CENTERS,
        "second-window transfer centers input",
    )
    assert_file_hash(
        inputs.get("second_window_transfer_tables", {}),
        SECOND_WINDOW_TRANSFER_TABLES,
        "second-window transfer tables input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_states", {}),
        SECOND_WINDOW_PROMOTION_STATES,
        "second-window promotion states input",
    )
    assert_file_hash(
        inputs.get("final_multifusion_report", {}),
        FINAL_MULTIFUSION_REPORT,
        "final multifusion report input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity_report", {}),
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        "symbolic associativity report input",
    )
    assert_file_hash(inputs.get("mog_resolvent", {}), MOG_RESOLVENT, "MOG input")
    assert_file_hash(
        inputs.get("wu_spinh_6j_marking", {}),
        WU_SPINH_6J_MARKING,
        "Wu/SpinH 6j input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame_manifest@1"
    ):
        raise AssertionError("sixj manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("sixj manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("sixj frame missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sixj index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_bottleneck_frame()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
