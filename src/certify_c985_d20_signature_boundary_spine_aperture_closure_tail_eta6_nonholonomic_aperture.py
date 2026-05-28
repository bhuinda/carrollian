from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture import (
        BOUNDARY_COLUMNS,
        DERIVE_SCRIPT,
        DINI_REPORT,
        DINI_TABLES,
        DISTRIBUTION_COLUMNS,
        HANDOFF_NOTE,
        HOLONOMY_REPORT,
        HOLONOMY_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PRESERVATION_REPORT,
        PRESERVATION_TABLES,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        TRUNCATED_REPORT,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
        preservation,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture import (
        BOUNDARY_COLUMNS,
        DERIVE_SCRIPT,
        DINI_REPORT,
        DINI_TABLES,
        DISTRIBUTION_COLUMNS,
        HANDOFF_NOTE,
        HOLONOMY_REPORT,
        HOLONOMY_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PRESERVATION_REPORT,
        PRESERVATION_TABLES,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        TRUNCATED_REPORT,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
        preservation,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    nonholonomic = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_certificate.json"
    )
    boundary_csv = (OUT_DIR / "eta6_nonholonomic_boundary_complex.csv").read_text(
        encoding="utf-8"
    )
    distribution_csv = (OUT_DIR / "eta6_nonholonomic_distribution.csv").read_text(
        encoding="utf-8"
    )
    state_csv = (OUT_DIR / "eta6_nonholonomic_automaton_states.csv").read_text(
        encoding="utf-8"
    )
    transition_csv = (
        OUT_DIR / "eta6_nonholonomic_automaton_transitions.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (OUT_DIR / "eta6_nonholonomic_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_tables.npz",
        allow_pickle=False,
    )
    index = load_json(preservation.INDEX_PATH)

    if nonholonomic != expected["nonholonomic"]:
        raise AssertionError("eta6 nonholonomic aperture JSON mismatch")
    if boundary_csv != expected["boundary_csv"]:
        raise AssertionError("eta6 nonholonomic boundary CSV mismatch")
    if distribution_csv != expected["distribution_csv"]:
        raise AssertionError("eta6 nonholonomic distribution CSV mismatch")
    if state_csv != expected["state_csv"]:
        raise AssertionError("eta6 nonholonomic state CSV mismatch")
    if transition_csv != expected["transition_csv"]:
        raise AssertionError("eta6 nonholonomic transition CSV mismatch")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 nonholonomic observables CSV mismatch")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 nonholonomic certificate mismatch")

    for name in [
        "boundary_table",
        "distribution_table",
        "state_table",
        "transition_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 nonholonomic table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture@1"
    ):
        raise AssertionError("eta6 nonholonomic report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 nonholonomic report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 nonholonomic all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 nonholonomic checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 nonholonomic report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 nonholonomic report hash mismatch")

    boundary_table = np.asarray(tables["boundary_table"], dtype=np.int64)
    distribution_table = np.asarray(tables["distribution_table"], dtype=np.int64)
    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    transition_table = np.asarray(tables["transition_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    expected_shapes = {
        "boundary": (3, len(BOUNDARY_COLUMNS)),
        "distribution": (7, len(DISTRIBUTION_COLUMNS)),
        "state": (5, len(STATE_COLUMNS)),
        "transition": (4, len(TRANSITION_COLUMNS)),
        "observable": (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }
    actual_shapes = {
        "boundary": tuple(boundary_table.shape),
        "distribution": tuple(distribution_table.shape),
        "state": tuple(state_table.shape),
        "transition": tuple(transition_table.shape),
        "observable": tuple(observable_table.shape),
    }
    if actual_shapes != expected_shapes:
        raise AssertionError(f"eta6 nonholonomic table shapes: {actual_shapes}")

    boundary_rows = table_rows(boundary_table, BOUNDARY_COLUMNS)
    distribution_rows = table_rows(distribution_table, DISTRIBUTION_COLUMNS)
    state_rows = table_rows(state_table, STATE_COLUMNS)
    transition_rows = table_rows(transition_table, TRANSITION_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }

    if (
        boundary_rows[0]["vertex_count"],
        boundary_rows[0]["edge_count"],
        boundary_rows[0]["face_count"],
        boundary_rows[1]["vertex_count"],
        boundary_rows[1]["edge_count"],
        boundary_rows[1]["face_count"],
        boundary_rows[1]["eta6_carrier_flag"],
        boundary_rows[1]["exterior_circuit_matrix_available_flag"],
    ) != (20, 30, 12, 60, 90, 32, 1, 0):
        raise AssertionError("eta6 nonholonomic boundary rows mismatch")

    source_counts = {
        row["source_code"]: (
            row["row_count"],
            row["horizontal_row_count"],
            row["conductance_decreasing_row_count"],
            row["conductance_decreasing_horizontal_count"],
            row["support_changing_count"],
            row["eta6_delta_rank"],
            row["metric_image_nonzero_flag"],
        )
        for row in distribution_rows
    }
    if source_counts != {
        0: (45, 45, 16, 16, 0, 0, 1),
        1: (84, 84, 25, 25, 0, 0, 1),
        2: (382, 382, 63, 63, 0, 0, 1),
        3: (21, 21, 3, 3, 0, 0, 1),
        4: (28, 28, 24, 24, 0, 0, 1),
        5: (26, 26, 22, 22, 0, 0, 1),
        6: (20, 20, 0, 0, 0, 0, 0),
    }:
        raise AssertionError("eta6 nonholonomic distribution rows mismatch")

    if [row["height_x1e12"] for row in state_rows] != [
        4_329_004_000,
        3_649_635_000,
        2_645_503_000,
        2_615_519_000,
        2_610_966_000,
    ]:
        raise AssertionError("eta6 nonholonomic state conductance chain mismatch")
    if [row["eta6_holonomy_pairing"] for row in state_rows] != [1, 1, 1, 1, 1]:
        raise AssertionError("eta6 nonholonomic state eta6 chain mismatch")
    if any(row["surgery_certified_flag"] for row in state_rows):
        raise AssertionError("eta6 nonholonomic unexpectedly certified surgery")
    if any(row["support_changed_flag"] for row in state_rows):
        raise AssertionError("eta6 nonholonomic state support changed")

    if (
        len(transition_rows),
        sum(row["horizontal_flag"] for row in transition_rows),
        sum(row["metric_nonzero_flag"] for row in transition_rows),
        sum(row["surgery_flag"] for row in transition_rows),
        sum(abs(row["holonomy_delta"]) for row in transition_rows),
    ) != (4, 4, 4, 0, 0):
        raise AssertionError("eta6 nonholonomic transition rows mismatch")

    required_observables = {
        "handoff_note_present_flag": 1,
        "public_boundary_vertex_count": 20,
        "public_boundary_edge_count": 30,
        "public_boundary_face_count": 12,
        "truncated_vertex_count": 60,
        "truncated_edge_count": 90,
        "truncated_face_count": 32,
        "relative_h1_dimension": 1,
        "relative_cohomology_dimension": 1,
        "eta6_holonomy_pairing": 1,
        "aggregate_distribution_row_count": 606,
        "horizontal_distribution_row_count": 606,
        "conductance_decreasing_row_count": 153,
        "support_changing_row_count": 0,
        "conductance_decreasing_support_changing_count": 0,
        "all_rows_aperture_preserved_count": 606,
        "distribution_eta6_delta_rank": 0,
        "distribution_metric_nonzero_flag": 1,
        "automaton_state_count": 5,
        "automaton_transition_count": 4,
        "positive_height_state_count": 5,
        "horizontal_transition_count": 4,
        "metric_nonzero_transition_count": 4,
        "surgery_transition_count": 0,
        "strict_conductance_descent_flag": 1,
        "holonomy_delta_total": 0,
        "base_to_final_drop_x1e12": 1_718_038_000,
        "final_height_x1e12": 2_610_966_000,
        "discriminant_state_count": 5,
        "positive_cone_proxy_available_flag": 1,
        "exterior_circuit_matrix_available_flag": 0,
        "surgery_certificate_available_flag": 0,
        "nonholonomic_aperture_model_flag": 1,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 nonholonomic observable {key} mismatch")
    if observables[OBSERVABLE_CODES["handoff_note_length"]] <= 1000:
        raise AssertionError("eta6 nonholonomic handoff note is too short")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("handoff_note", {}), HANDOFF_NOTE, "handoff note")
    assert_file_hash(
        inputs.get("truncated_skeleton_report", {}),
        TRUNCATED_REPORT,
        "truncated skeleton report input",
    )
    assert_file_hash(
        inputs.get("truncated_skeleton_tables", {}),
        TRUNCATED_TABLES,
        "truncated skeleton tables input",
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
    assert_file_hash(
        inputs.get("eta6_holonomy_report", {}),
        HOLONOMY_REPORT,
        "eta6 holonomy report input",
    )
    assert_file_hash(
        inputs.get("eta6_holonomy_tables", {}),
        HOLONOMY_TABLES,
        "eta6 holonomy tables input",
    )
    assert_file_hash(
        inputs.get("dini_torsion_report", {}),
        DINI_REPORT,
        "Dini torsion report input",
    )
    assert_file_hash(
        inputs.get("dini_torsion_tables", {}),
        DINI_TABLES,
        "Dini torsion tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture_manifest@1"
    ):
        raise AssertionError("eta6 nonholonomic manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 nonholonomic manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 nonholonomic manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 nonholonomic missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 nonholonomic index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 nonholonomic index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_nonholonomic_aperture()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
