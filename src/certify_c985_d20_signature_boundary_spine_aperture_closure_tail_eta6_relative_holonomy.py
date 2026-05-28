from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy import (
        EDGE_COLUMNS,
        ETA6_JSON,
        ETA6_REPORT,
        ETA6_TABLES,
        FACE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OPPOSITE_PAIR_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        DERIVE_SCRIPT,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy import (
        EDGE_COLUMNS,
        ETA6_JSON,
        ETA6_REPORT,
        ETA6_TABLES,
        FACE_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OPPOSITE_PAIR_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        DERIVE_SCRIPT,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    holonomy = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_certificate.json"
    )
    edge_csv = (OUT_DIR / "eta6_relative_edge_basis.csv").read_text(encoding="utf-8")
    face_csv = (OUT_DIR / "eta6_relative_face_boundaries.csv").read_text(
        encoding="utf-8"
    )
    opposite_csv = (OUT_DIR / "eta6_relative_opposite_pair_cycles.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "eta6_relative_holonomy_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if holonomy != expected["holonomy"]:
        raise AssertionError("eta6 relative holonomy JSON is not reproducible")
    if edge_csv != expected["edge_basis_csv"]:
        raise AssertionError("eta6 relative edge CSV is not reproducible")
    if face_csv != expected["face_boundary_csv"]:
        raise AssertionError("eta6 relative face CSV is not reproducible")
    if opposite_csv != expected["opposite_pair_csv"]:
        raise AssertionError("eta6 relative opposite pair CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 relative observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 relative certificate is not reproducible")

    for name in ["edge_table", "face_table", "opposite_pair_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 relative table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy@1"
    ):
        raise AssertionError("eta6 relative report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 relative report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 relative all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 relative checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 relative report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 relative report hash is not reproducible")

    edge_table = np.asarray(tables["edge_table"], dtype=np.int64)
    face_table = np.asarray(tables["face_table"], dtype=np.int64)
    opposite_pair_table = np.asarray(tables["opposite_pair_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(edge_table.shape) != (6, len(EDGE_COLUMNS)):
        raise AssertionError("eta6 relative edge table shape mismatch")
    if tuple(face_table.shape) != (4, len(FACE_COLUMNS)):
        raise AssertionError("eta6 relative face table shape mismatch")
    if tuple(opposite_pair_table.shape) != (3, len(OPPOSITE_PAIR_COLUMNS)):
        raise AssertionError("eta6 relative opposite table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("eta6 relative observable table shape mismatch")

    edge_rows = table_rows(edge_table, EDGE_COLUMNS)
    face_rows = table_rows(face_table, FACE_COLUMNS)
    opposite_rows = table_rows(opposite_pair_table, OPPOSITE_PAIR_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if [row["eta6_coeff"] for row in edge_rows] != [1, 1, 1, 1, 1, 1]:
        raise AssertionError("eta6 relative eta vector mismatch")
    if [row["holonomy_coeff"] for row in edge_rows] != [0, 0, 1, 0, 1, 1]:
        raise AssertionError("eta6 relative holonomy vector mismatch")
    if any(row["holonomy_face_pairing"] for row in face_rows):
        raise AssertionError("eta6 relative holonomy is not a cocycle")
    if any(
        row["relative_boundary_q0"]
        or row["relative_boundary_q1"]
        or row["relative_boundary_q2"]
        for row in opposite_rows
    ):
        raise AssertionError("eta6 relative opposite-pair cycle mismatch")

    required_observables = {
        "edge_count": 6,
        "face_count": 4,
        "relative_boundary_rank": 2,
        "face_boundary_rank": 3,
        "relative_cycle_space_dimension": 4,
        "relative_h1_dimension": 1,
        "relative_cohomology_dimension": 1,
        "eta6_relative_boundary_weight": 0,
        "eta6_absolute_boundary_weight": 4,
        "eta6_in_face_boundary_image_flag": 0,
        "eta6_relative_class_nonzero_flag": 1,
        "holonomy_cocycle_flag": 1,
        "holonomy_coboundary_flag": 0,
        "holonomy_eta6_pairing": 1,
        "opposite_pair_relative_cycle_count": 3,
        "eta6_report_preserved_rows": 606,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 relative observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("eta6_report", {}), ETA6_REPORT, "eta6 report input")
    assert_file_hash(inputs.get("eta6_tables", {}), ETA6_TABLES, "eta6 tables input")
    assert_file_hash(inputs.get("eta6_json", {}), ETA6_JSON, "eta6 JSON input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy_manifest@1"
    ):
        raise AssertionError("eta6 relative manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 relative manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 relative manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 relative missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 relative index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 relative index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_relative_holonomy()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
