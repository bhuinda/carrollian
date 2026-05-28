from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_eta6_ext_cone import (
        DERIVE_SCRIPT,
        FACE_SUPPORT_COLUMNS,
        NONHOLONOMIC_REPORT,
        NONHOLONOMIC_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SLACK_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRUNCATED_REPORT,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        VERTEX_COLUMNS,
        barycenter,
        build_payloads,
        nonholonomic,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_eta6_ext_cone import (
        DERIVE_SCRIPT,
        FACE_SUPPORT_COLUMNS,
        NONHOLONOMIC_REPORT,
        NONHOLONOMIC_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SLACK_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRUNCATED_REPORT,
        TRUNCATED_TABLES,
        VALIDATOR_SCRIPT,
        VERTEX_COLUMNS,
        barycenter,
        build_payloads,
        nonholonomic,
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


def validate_eta6_ext_cone() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    support_cone = load_json(
        OUT_DIR
        / "ext_cone.json"
    )
    certificate = load_json(
        OUT_DIR
        / "cert.json"
    )
    vertices_csv = (OUT_DIR / "vertices.csv").read_text(
        encoding="utf-8"
    )
    faces_csv = (OUT_DIR / "faces.csv").read_text(
        encoding="utf-8"
    )
    slacks_csv = (OUT_DIR / "slacks.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "obs.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "tables.npz",
        allow_pickle=False,
    )
    index = load_json(nonholonomic.preservation.INDEX_PATH)

    if support_cone != expected["support_cone"]:
        raise AssertionError("eta6 exterior support cone JSON mismatch")
    if vertices_csv != expected["vertices_csv"]:
        raise AssertionError("eta6 exterior support vertices CSV mismatch")
    if faces_csv != expected["faces_csv"]:
        raise AssertionError("eta6 exterior support faces CSV mismatch")
    if slacks_csv != expected["slacks_csv"]:
        raise AssertionError("eta6 exterior support slacks CSV mismatch")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 exterior support observables CSV mismatch")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 exterior support certificate mismatch")

    for name in [
        "vertex_table",
        "face_support_table",
        "slack_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 exterior support table {name} mismatch")

    if (
        report.get("schema")
        != "eta6.ext_cone.report@1"
    ):
        raise AssertionError("eta6 exterior support report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 exterior support report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 exterior support all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 exterior support checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 exterior support report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 exterior support report hash mismatch")

    vertex_table = np.asarray(tables["vertex_table"], dtype=np.int64)
    face_support_table = np.asarray(tables["face_support_table"], dtype=np.int64)
    slack_table = np.asarray(tables["slack_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    expected_shapes = {
        "vertex": (60, len(VERTEX_COLUMNS)),
        "face": (32, len(FACE_SUPPORT_COLUMNS)),
        "slack": (1_740, len(SLACK_COLUMNS)),
        "observable": (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }
    actual_shapes = {
        "vertex": tuple(vertex_table.shape),
        "face": tuple(face_support_table.shape),
        "slack": tuple(slack_table.shape),
        "observable": tuple(observable_table.shape),
    }
    if actual_shapes != expected_shapes:
        raise AssertionError(f"eta6 exterior support table shapes: {actual_shapes}")

    face_rows = table_rows(face_support_table, FACE_SUPPORT_COLUMNS)
    slack_rows = table_rows(slack_table, SLACK_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sum(row["face_type_code"] == 0 for row in face_rows) != 12:
        raise AssertionError("eta6 exterior support pentagon count mismatch")
    if sum(row["face_type_code"] == 1 for row in face_rows) != 20:
        raise AssertionError("eta6 exterior support hexagon count mismatch")
    if min(row["min_slack_x1e12"] for row in face_rows) != 350_487_408_079:
        raise AssertionError("eta6 exterior support min face slack mismatch")
    if max(row["max_slack_x1e12"] for row in face_rows) != 3_103_251_249_022:
        raise AssertionError("eta6 exterior support max face slack mismatch")
    if any(row["zero_slack_count"] for row in face_rows):
        raise AssertionError("eta6 exterior support has a zero face slack")
    if any(row["positive_flag"] != 1 for row in slack_rows):
        raise AssertionError("eta6 exterior support has a nonpositive slack row")
    if any(row["discriminant_equal_flag"] != 0 for row in slack_rows):
        raise AssertionError("eta6 exterior support intersects discriminant")

    required_observables = {
        "coordinate_vertex_count": 60,
        "face_count": 32,
        "pentagon_face_count": 12,
        "hexagon_face_count": 20,
        "support_inequality_count": 1_740,
        "positive_slack_count": 1_740,
        "zero_slack_count": 0,
        "min_slack_x1e12": 350_487_408_079,
        "max_slack_x1e12": 3_103_251_249_022,
        "positive_support_cone_flag": 1,
        "current_discriminant_intersection_flag": 0,
        "support_matrix_available_flag": 1,
        "affine_circuit_gordan_certificate_available_flag": 0,
        "nonholonomic_prior_exterior_matrix_available_flag": 0,
        "nonholonomic_prior_positive_proxy_flag": 1,
        "surgery_certificate_available_flag": 0,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 exterior support observable {key} mismatch")

    inputs = report.get("inputs", {})
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
        inputs.get("nonholonomic_aperture_report", {}),
        NONHOLONOMIC_REPORT,
        "nonholonomic aperture report input",
    )
    assert_file_hash(
        inputs.get("nonholonomic_aperture_tables", {}),
        NONHOLONOMIC_TABLES,
        "nonholonomic aperture tables input",
    )
    assert_file_hash(
        inputs.get("coordinate_helper_script", {}),
        barycenter.DERIVE_SCRIPT,
        "coordinate helper script input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "eta6.ext_cone.manifest@1"
    ):
        raise AssertionError("eta6 exterior support manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 exterior support manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 exterior support manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 exterior support missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 exterior support index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 exterior support index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "eta6.ext_cone.verification@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_eta6_ext_cone()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
