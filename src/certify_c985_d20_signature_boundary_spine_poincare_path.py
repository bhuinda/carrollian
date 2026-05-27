from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_poincare_path import (
        CONDUCTANCE_SPINE_CERTIFICATE,
        CONDUCTANCE_SPINE_EDGES,
        CONDUCTANCE_SPINE_JSON,
        CONDUCTANCE_SPINE_REPORT,
        CONDUCTANCE_SPINE_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_JSON,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_TABLES,
        SPINE_POINCARE_EDGE_COLUMNS,
        SPINE_POINCARE_OBSERVABLE_COLUMNS,
        SPINE_POLYLINE_TRANSITION_COLUMNS,
        SPINE_POLYLINE_VERTEX_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_poincare_path import (
        CONDUCTANCE_SPINE_CERTIFICATE,
        CONDUCTANCE_SPINE_EDGES,
        CONDUCTANCE_SPINE_JSON,
        CONDUCTANCE_SPINE_REPORT,
        CONDUCTANCE_SPINE_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OUT_DIR,
        RESIDUAL_CHART_CARRIER_CSV,
        RESIDUAL_CHART_CERTIFICATE,
        RESIDUAL_CHART_JSON,
        RESIDUAL_CHART_REPORT,
        RESIDUAL_CHART_TABLES,
        SPINE_POINCARE_EDGE_COLUMNS,
        SPINE_POINCARE_OBSERVABLE_COLUMNS,
        SPINE_POLYLINE_TRANSITION_COLUMNS,
        SPINE_POLYLINE_VERTEX_COLUMNS,
        STATUS,
        THEOREM_ID,
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
        raise AssertionError(f"{label} path mismatch: {entry.get('path')} != {expected_rel}")
    if entry.get("sha256") != h_file(expected_path):
        raise AssertionError(f"{label} sha256 mismatch")


def validate_c985_d20_signature_boundary_spine_poincare_path() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    path_readout = load_json(OUT_DIR / "signature_boundary_spine_poincare_path.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_poincare_path_certificate.json"
    )
    edge_csv = (OUT_DIR / "boundary_spine_poincare_edges.csv").read_text(
        encoding="utf-8"
    )
    vertex_csv = (OUT_DIR / "boundary_spine_poincare_polyline_vertices.csv").read_text(
        encoding="utf-8"
    )
    transition_csv = (
        OUT_DIR / "boundary_spine_poincare_polyline_transitions.csv"
    ).read_text(encoding="utf-8")
    observable_csv = (OUT_DIR / "boundary_spine_poincare_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_poincare_path_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if path_readout != expected["signature_boundary_spine_poincare_path"]:
        raise AssertionError("boundary spine Poincare path JSON is not reproducible")
    if edge_csv != expected["boundary_spine_poincare_edges_csv"]:
        raise AssertionError("boundary spine Poincare edge CSV is not reproducible")
    if vertex_csv != expected["boundary_spine_poincare_polyline_vertices_csv"]:
        raise AssertionError("boundary spine Poincare vertex CSV is not reproducible")
    if transition_csv != expected["boundary_spine_poincare_polyline_transitions_csv"]:
        raise AssertionError("boundary spine Poincare transition CSV is not reproducible")
    if observable_csv != expected["boundary_spine_poincare_observables_csv"]:
        raise AssertionError("boundary spine Poincare observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_poincare_path_certificate"]:
        raise AssertionError("boundary spine Poincare path certificate is not reproducible")

    table_names = [
        "spine_poincare_edge_table",
        "spine_polyline_vertex_table",
        "spine_polyline_transition_table",
        "spine_poincare_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"boundary spine Poincare table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_poincare_path@1":
        raise AssertionError("C985 d20 boundary spine Poincare report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary spine Poincare path is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary spine Poincare all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary spine Poincare checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine Poincare report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary spine Poincare report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "conductance_spine_report_certified",
        "conductance_spine_certificate_certified",
        "residual_chart_report_certified",
        "residual_chart_certificate_certified",
        "boundary_edge_count_is_16",
        "polyline_vertex_count_is_16",
        "polyline_transition_count_is_15",
        "spine_order_matches_conductance_spine",
        "top_spine_edge_axis_dominant",
        "top_spine_edge_metrics_match_expected",
        "top_five_edge_cloud_axis_dominant",
        "top_five_edge_cloud_metrics_match_expected",
        "full_edge_cloud_residual_bending",
        "full_edge_cloud_metrics_match_expected",
        "residual_dominant_edge_set_matches_expected",
        "residual_dominant_entropy_fraction_matches_expected",
        "entropy_midpoint_polyline_residual_bends",
        "entropy_midpoint_polyline_metrics_match_expected",
        "top_five_midpoint_polyline_residual_bends",
        "top_five_midpoint_polyline_metrics_match_expected",
        "polyline_spans_match_expected",
        "edge_table_shape_is_16_by_25",
        "polyline_vertex_table_shape_is_16_by_9",
        "polyline_transition_table_shape_is_15_by_13",
        "observable_table_shape_matches_codebook",
        "conductance_spine_json_schema_available",
        "residual_chart_json_schema_available",
        "conductance_spine_tables_available",
        "residual_chart_tables_available",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary spine Poincare missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("boundary_edge_count") != 16:
        raise AssertionError("boundary spine Poincare edge count mismatch")
    if witness.get("polyline_vertex_count") != 16:
        raise AssertionError("boundary spine Poincare vertex count mismatch")
    if witness.get("polyline_transition_count") != 15:
        raise AssertionError("boundary spine Poincare transition count mismatch")
    if witness.get("spine_order_boundary_mask_edge_ids") != [
        14,
        15,
        2,
        6,
        3,
        7,
        8,
        11,
        9,
        13,
        12,
        5,
        10,
        4,
        1,
        0,
    ]:
        raise AssertionError("boundary spine Poincare order mismatch")
    if witness.get("top_spine_edge") != {
        "boundary_mask_edge_id": 14,
        "axis_delta_abs_x1e12": 269936014924,
        "residual_delta_abs_x1e12": 172424508261,
        "residual_bend_fraction_x1e12": 389782765920,
        "hyperbolic_edge_length_x1e12": 321097465327,
        "axis_dominant": True,
    }:
        raise AssertionError("boundary spine Poincare top edge mismatch")
    if witness.get("top_five_edge_cloud") != {
        "boundary_mask_edge_ids": [14, 15, 2, 6, 3],
        "entropy_weighted_axis_delta_x1e12": 169799011239,
        "entropy_weighted_residual_delta_x1e12": 94652654063,
        "entropy_weighted_bend_fraction_x1e12": 357920431149,
        "entropy_weighted_hyperbolic_length_x1e12": 206224183865,
        "axis_dominant": True,
    }:
        raise AssertionError("boundary spine Poincare top-five edge cloud mismatch")
    if witness.get("full_edge_cloud") != {
        "entropy_weighted_axis_delta_x1e12": 127563694032,
        "entropy_weighted_residual_delta_x1e12": 159064775410,
        "entropy_weighted_bend_fraction_x1e12": 554951068607,
        "entropy_weighted_hyperbolic_length_x1e12": 228645586683,
        "residual_bending": True,
    }:
        raise AssertionError("boundary spine Poincare full cloud mismatch")
    if witness.get("residual_dominant_edges") != {
        "boundary_mask_edge_ids": [6, 7, 8, 11, 9, 12, 5, 10, 4],
        "edge_count": 9,
        "entropy_fraction_x1e12": 488542794331,
    }:
        raise AssertionError("boundary spine Poincare residual edge set mismatch")
    if witness.get("entropy_midpoint_polyline") != {
        "axis_travel_x1e12": 950955396598,
        "residual_travel_x1e12": 2431519629877,
        "residual_bend_fraction_x1e12": 718858117457,
        "hyperbolic_length_x1e12": 2701324116998,
        "axis_span_x1e12": 257126409278,
        "residual_span_x1e12": 575309726652,
    }:
        raise AssertionError("boundary spine Poincare polyline mismatch")
    if witness.get("top_five_entropy_midpoint_polyline") != {
        "axis_travel_x1e12": 261932815628,
        "residual_travel_x1e12": 480761936246,
        "residual_bend_fraction_x1e12": 647321036042,
        "hyperbolic_length_x1e12": 548672938221,
        "axis_span_x1e12": 171860556085,
        "residual_span_x1e12": 300700062647,
    }:
        raise AssertionError("boundary spine Poincare top-five polyline mismatch")

    edge_table = np.asarray(tables["spine_poincare_edge_table"], dtype=np.int64)
    vertex_table = np.asarray(tables["spine_polyline_vertex_table"], dtype=np.int64)
    transition_table = np.asarray(tables["spine_polyline_transition_table"], dtype=np.int64)
    observable_table = np.asarray(tables["spine_poincare_observable_table"], dtype=np.int64)

    if edge_table.shape != (16, len(SPINE_POINCARE_EDGE_COLUMNS)):
        raise AssertionError("boundary spine Poincare edge table shape mismatch")
    if vertex_table.shape != (16, len(SPINE_POLYLINE_VERTEX_COLUMNS)):
        raise AssertionError("boundary spine Poincare vertex table shape mismatch")
    if transition_table.shape != (15, len(SPINE_POLYLINE_TRANSITION_COLUMNS)):
        raise AssertionError("boundary spine Poincare transition table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(SPINE_POINCARE_OBSERVABLE_COLUMNS)):
        raise AssertionError("boundary spine Poincare observable table shape mismatch")
    if edge_table[:, 1].tolist() != witness.get("spine_order_boundary_mask_edge_ids"):
        raise AssertionError("boundary spine Poincare edge order table mismatch")
    if int(edge_table[:, 16].sum()) != 2750163397428:
        raise AssertionError("boundary spine Poincare residual-delta sum mismatch")
    if int(transition_table[:, 10].sum()) != 2431519629877:
        raise AssertionError("boundary spine Poincare polyline residual sum mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("boundary spine Poincare observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("conductance_spine_report", {}),
        CONDUCTANCE_SPINE_REPORT,
        "conductance spine report input",
    )
    assert_file_hash(
        inputs.get("conductance_spine", {}),
        CONDUCTANCE_SPINE_JSON,
        "conductance spine JSON input",
    )
    assert_file_hash(
        inputs.get("conductance_spine_tables", {}),
        CONDUCTANCE_SPINE_TABLES,
        "conductance spine tables input",
    )
    assert_file_hash(
        inputs.get("conductance_spine_certificate", {}),
        CONDUCTANCE_SPINE_CERTIFICATE,
        "conductance spine certificate input",
    )
    assert_file_hash(
        inputs.get("conductance_spine_edges", {}),
        CONDUCTANCE_SPINE_EDGES,
        "conductance spine edges input",
    )
    assert_file_hash(
        inputs.get("residual_chart_report", {}),
        RESIDUAL_CHART_REPORT,
        "residual chart report input",
    )
    assert_file_hash(inputs.get("residual_chart", {}), RESIDUAL_CHART_JSON, "residual chart JSON input")
    assert_file_hash(
        inputs.get("residual_chart_tables", {}),
        RESIDUAL_CHART_TABLES,
        "residual chart tables input",
    )
    assert_file_hash(
        inputs.get("residual_chart_certificate", {}),
        RESIDUAL_CHART_CERTIFICATE,
        "residual chart certificate input",
    )
    assert_file_hash(
        inputs.get("residual_chart_carriers", {}),
        RESIDUAL_CHART_CARRIER_CSV,
        "residual chart carriers input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_poincare_path_manifest@1":
        raise AssertionError("C985 d20 boundary spine Poincare manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine Poincare manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary spine Poincare manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 boundary spine Poincare missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine Poincare index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary spine Poincare index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_poincare_path@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "top_spine_edge": witness.get("top_spine_edge"),
        "top_five_edge_cloud": witness.get("top_five_edge_cloud"),
        "full_edge_cloud": witness.get("full_edge_cloud"),
        "entropy_midpoint_polyline": witness.get("entropy_midpoint_polyline"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_poincare_path()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
