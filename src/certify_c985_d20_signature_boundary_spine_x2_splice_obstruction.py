from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_x2_splice_obstruction import (
        APERTURE_INSERTION_CANDIDATES,
        APERTURE_INSERTION_CERTIFICATE,
        APERTURE_INSERTION_JSON,
        APERTURE_INSERTION_REPORT,
        APERTURE_INSERTION_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        SLOT_AUDIT_COLUMNS,
        SPLICE_CANDIDATE_COLUMNS,
        SPLICE_OBSERVABLE_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_JSON,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X2_NEAR_MISS_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_x2_splice_obstruction import (
        APERTURE_INSERTION_CANDIDATES,
        APERTURE_INSERTION_CERTIFICATE,
        APERTURE_INSERTION_JSON,
        APERTURE_INSERTION_REPORT,
        APERTURE_INSERTION_TABLES,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_JSON,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        SLOT_AUDIT_COLUMNS,
        SPLICE_CANDIDATE_COLUMNS,
        SPLICE_OBSERVABLE_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_JSON,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        X2_NEAR_MISS_COLUMNS,
        build_payloads,
        self_hash,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def assert_file_hash(entry: dict[str, Any], expected_path: Path, label: str) -> None:
    expected_rel = expected_path.relative_to(ROOT).as_posix()
    if entry.get("path") != expected_rel:
        raise AssertionError(f"{label} path mismatch: {entry.get('path')} != {expected_rel}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_c985_d20_signature_boundary_spine_x2_splice_obstruction() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    obstruction = load_json(
        OUT_DIR / "signature_boundary_spine_x2_splice_obstruction.json"
    )
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_x2_splice_obstruction_certificate.json"
    )
    candidates_csv = (OUT_DIR / "x2_splice_candidate_edges.csv").read_text(
        encoding="utf-8"
    )
    near_misses_csv = (OUT_DIR / "x2_splice_near_misses.csv").read_text(
        encoding="utf-8"
    )
    slot_audit_csv = (OUT_DIR / "x2_splice_slot_audit.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "x2_splice_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_x2_splice_obstruction_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if obstruction != expected["signature_boundary_spine_x2_splice_obstruction"]:
        raise AssertionError("x2 splice obstruction JSON is not reproducible")
    if candidates_csv != expected["x2_splice_candidate_edges_csv"]:
        raise AssertionError("x2 splice candidate CSV is not reproducible")
    if near_misses_csv != expected["x2_splice_near_misses_csv"]:
        raise AssertionError("x2 splice near miss CSV is not reproducible")
    if slot_audit_csv != expected["x2_splice_slot_audit_csv"]:
        raise AssertionError("x2 splice slot audit CSV is not reproducible")
    if observables_csv != expected["x2_splice_observables_csv"]:
        raise AssertionError("x2 splice observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_x2_splice_obstruction_certificate"]:
        raise AssertionError("x2 splice obstruction certificate is not reproducible")

    table_names = [
        "candidate_table",
        "near_miss_table",
        "slot_audit_table",
        "observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"x2 splice obstruction table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_splice_obstruction@1":
        raise AssertionError("C985 d20 x2 splice obstruction report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 x2 splice obstruction is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 x2 splice obstruction all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 x2 splice obstruction checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 splice obstruction report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 x2 splice obstruction report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "aperture_insertion_report_certified",
        "aperture_insertion_certificate_certified",
        "typed_corridor_report_certified",
        "typed_corridor_certificate_certified",
        "cell_complex_report_certified",
        "cell_complex_certificate_certified",
        "aperture_insertion_schema_available",
        "typed_corridor_schema_available",
        "cell_complex_schema_available",
        "insertion_candidate_table_shape_is_15_by_15",
        "typed_corridor_edge_table_shape_is_16_by_23",
        "cell_complex_edge_table_shape_is_44_by_13",
        "selected_insertion_is_after_state_14",
        "selected_virtual_window_is_node_42",
        "slot_contact_is_positive_12_negative_4",
        "slot_contact_shared_symbol_is_x3",
        "carrier_pair_edge_count_is_44",
        "positive_negative_boundary_edge_count_is_16",
        "shared_x2_edge_count_is_10",
        "boundary_shared_x2_edge_count_is_0",
        "slot_eligible_x2_edge_count_is_0",
        "slot_positive_incident_x2_edge_count_is_4",
        "slot_negative_incident_x2_edge_count_is_0",
        "single_shared_x2_edge_count_is_6",
        "positive_internal_x2_edge_count_is_10",
        "existing_spine_x2_gate_count_is_0",
        "post_branch_tail_x2_contact_count_is_0",
        "post_branch_tail_symbols_are_x1_x0",
        "all_x2_near_misses_are_within_central_positive_region",
        "x2_near_miss_edges_match_expected",
        "slot_positive_incident_near_miss_edges_match_expected",
        "candidate_table_shape_is_44_by_20",
        "near_miss_table_shape_is_10_by_14",
        "slot_audit_table_shape_is_3_by_9",
        "observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 x2 splice obstruction missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("actual_splice_possible") is not False:
        raise AssertionError("x2 splice obstruction possible flag mismatch")
    if witness.get("shared_x2_edge_count") != 10:
        raise AssertionError("x2 splice shared x2 edge count mismatch")
    if witness.get("boundary_shared_x2_edge_count") != 0:
        raise AssertionError("x2 splice boundary x2 edge count mismatch")
    if witness.get("slot_eligible_x2_edge_count") != 0:
        raise AssertionError("x2 splice slot eligible edge count mismatch")
    if witness.get("slot_positive_incident_x2_edge_ids") != [9, 14, 39, 41]:
        raise AssertionError("x2 splice slot positive near misses mismatch")
    if witness.get("slot_negative_incident_x2_edge_ids") != []:
        raise AssertionError("x2 splice slot negative near misses mismatch")
    if witness.get("x2_near_miss_edge_ids") != [6, 7, 8, 9, 12, 13, 14, 38, 39, 41]:
        raise AssertionError("x2 splice near miss edge ids mismatch")
    if witness.get("x2_near_miss_partition_histogram") != [{"value": 1, "count": 10}]:
        raise AssertionError("x2 splice near miss partition histogram mismatch")
    if witness.get("slot_audit_rows") != [
        {
            "boundary_mask_edge_id": 4,
            "boundary_spine_rank": 14,
            "negative_carrier_mask_class_id": 4,
            "positive_carrier_mask_class_id": 12,
            "post_branch_tail_flag": 0,
            "selected_slot_boundary_flag": 1,
            "shared_symbol_id": 3,
            "slot_audit_id": 0,
            "x2_contact_flag": 0,
        },
        {
            "boundary_mask_edge_id": 1,
            "boundary_spine_rank": 15,
            "negative_carrier_mask_class_id": 8,
            "positive_carrier_mask_class_id": 1,
            "post_branch_tail_flag": 1,
            "selected_slot_boundary_flag": 0,
            "shared_symbol_id": 1,
            "slot_audit_id": 1,
            "x2_contact_flag": 0,
        },
        {
            "boundary_mask_edge_id": 0,
            "boundary_spine_rank": 16,
            "negative_carrier_mask_class_id": 7,
            "positive_carrier_mask_class_id": 0,
            "post_branch_tail_flag": 1,
            "selected_slot_boundary_flag": 0,
            "shared_symbol_id": 0,
            "slot_audit_id": 2,
            "x2_contact_flag": 0,
        },
    ]:
        raise AssertionError("x2 splice slot audit rows mismatch")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    near_miss_table = np.asarray(tables["near_miss_table"], dtype=np.int64)
    slot_audit_table = np.asarray(tables["slot_audit_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if candidate_table.shape != (44, len(SPLICE_CANDIDATE_COLUMNS)):
        raise AssertionError("x2 splice candidate table shape mismatch")
    if near_miss_table.shape != (10, len(X2_NEAR_MISS_COLUMNS)):
        raise AssertionError("x2 splice near miss table shape mismatch")
    if slot_audit_table.shape != (3, len(SLOT_AUDIT_COLUMNS)):
        raise AssertionError("x2 splice slot audit table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(SPLICE_OBSERVABLE_COLUMNS)):
        raise AssertionError("x2 splice observable table shape mismatch")
    if int(np.sum(candidate_table[:, 17])) != 0:
        raise AssertionError("x2 splice candidate boundary realizable flags mismatch")
    if int(np.sum(candidate_table[:, 18])) != 0:
        raise AssertionError("x2 splice eligible flags mismatch")
    if near_miss_table[:, 1].tolist() != [6, 7, 8, 9, 12, 13, 14, 38, 39, 41]:
        raise AssertionError("x2 splice near miss table ids mismatch")
    if slot_audit_table[:, 5].tolist() != [3, 1, 0]:
        raise AssertionError("x2 splice slot audit shared symbols mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("aperture_insertion_report", {}), APERTURE_INSERTION_REPORT, "aperture insertion report input")
    assert_file_hash(inputs.get("aperture_insertion", {}), APERTURE_INSERTION_JSON, "aperture insertion JSON input")
    assert_file_hash(inputs.get("aperture_insertion_candidates", {}), APERTURE_INSERTION_CANDIDATES, "aperture insertion candidate input")
    assert_file_hash(inputs.get("aperture_insertion_tables", {}), APERTURE_INSERTION_TABLES, "aperture insertion table input")
    assert_file_hash(inputs.get("aperture_insertion_certificate", {}), APERTURE_INSERTION_CERTIFICATE, "aperture insertion certificate input")
    assert_file_hash(inputs.get("typed_corridor_report", {}), TYPED_CORRIDOR_REPORT, "typed corridor report input")
    assert_file_hash(inputs.get("typed_corridors", {}), TYPED_CORRIDOR_JSON, "typed corridor JSON input")
    assert_file_hash(inputs.get("typed_corridor_edges", {}), TYPED_CORRIDOR_EDGES, "typed corridor edge input")
    assert_file_hash(inputs.get("typed_corridor_tables", {}), TYPED_CORRIDOR_TABLES, "typed corridor table input")
    assert_file_hash(inputs.get("typed_corridor_certificate", {}), TYPED_CORRIDOR_CERTIFICATE, "typed corridor certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex", {}), CELL_COMPLEX_JSON, "cell complex JSON input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edge input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex table input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("residual_chart_carriers", {}), RESIDUAL_CHART_CARRIER_CSV, "residual chart carrier input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_x2_splice_obstruction_manifest@1":
        raise AssertionError("C985 d20 x2 splice obstruction manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 splice obstruction manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 x2 splice obstruction manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 x2 splice obstruction missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 x2 splice obstruction index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 x2 splice obstruction index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_x2_splice_obstruction@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "actual_splice_possible": witness.get("actual_splice_possible"),
        "shared_x2_edge_count": witness.get("shared_x2_edge_count"),
        "boundary_shared_x2_edge_count": witness.get("boundary_shared_x2_edge_count"),
        "slot_positive_incident_x2_edge_ids": witness.get(
            "slot_positive_incident_x2_edge_ids"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_x2_splice_obstruction()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
