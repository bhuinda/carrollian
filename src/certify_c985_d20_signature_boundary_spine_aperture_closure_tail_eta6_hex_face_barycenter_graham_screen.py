from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        EXTREMA_COLUMNS,
        GRAHAM_AREA_X1E12,
        GRAHAM_TOLERANCE_X1E12,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REGULAR_AREA_X1E12,
        SCREEN_CODES,
        STATUS,
        THEOREM_ID,
        TRUNCATED_SKELETON_REPORT,
        TRUNCATED_SKELETON_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        skeleton,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen import (
        CENTER_COLUMNS,
        DERIVE_SCRIPT,
        EXTREMA_COLUMNS,
        GRAHAM_AREA_X1E12,
        GRAHAM_TOLERANCE_X1E12,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        REGULAR_AREA_X1E12,
        SCREEN_CODES,
        STATUS,
        THEOREM_ID,
        TRUNCATED_SKELETON_REPORT,
        TRUNCATED_SKELETON_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        skeleton,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    screen = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_certificate.json"
    )
    centers_csv = (OUT_DIR / "eta6_hex_face_barycenter_centers.csv").read_text(
        encoding="utf-8"
    )
    extrema_csv = (OUT_DIR / "eta6_hex_face_barycenter_extrema.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "eta6_hex_face_barycenter_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_tables.npz",
        allow_pickle=False,
    )
    index = load_json(skeleton.INDEX_PATH)

    if screen != expected["screen"]:
        raise AssertionError("eta6 hex-face barycenter screen JSON mismatch")
    if centers_csv != expected["centers_csv"]:
        raise AssertionError("eta6 hex-face barycenter centers CSV mismatch")
    if extrema_csv != expected["extrema_csv"]:
        raise AssertionError("eta6 hex-face barycenter extrema CSV mismatch")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 hex-face barycenter observables CSV mismatch")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 hex-face barycenter certificate mismatch")

    for name in ["center_table", "extrema_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 hex-face barycenter table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen@1"
    ):
        raise AssertionError("eta6 hex-face barycenter report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 hex-face barycenter report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 hex-face barycenter all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 hex-face barycenter checks mismatch")
    if skeleton.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 hex-face barycenter report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 hex-face barycenter report hash mismatch")

    center_table = np.asarray(tables["center_table"], dtype=np.int64)
    extrema_table = np.asarray(tables["extrema_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    expected_shapes = {
        "center": (20, len(CENTER_COLUMNS)),
        "extrema": (4, len(EXTREMA_COLUMNS)),
        "observable": (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }
    actual_shapes = {
        "center": tuple(center_table.shape),
        "extrema": tuple(extrema_table.shape),
        "observable": tuple(observable_table.shape),
    }
    if actual_shapes != expected_shapes:
        raise AssertionError(f"eta6 hex-face barycenter table shapes: {actual_shapes}")

    center_rows = table_rows(center_table, CENTER_COLUMNS)
    extrema_rows = table_rows(extrema_table, EXTREMA_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if sorted(row["face_source_id"] for row in center_rows) != list(range(20)):
        raise AssertionError("eta6 hex-face barycenter source id coverage mismatch")

    extrema_by_code = {row["screen_code"]: row for row in extrema_rows}
    closest_all = extrema_by_code[SCREEN_CODES["closest_all"]]
    max_all = extrema_by_code[SCREEN_CODES["max_all"]]
    closest_connected = extrema_by_code[SCREEN_CODES["closest_connected"]]
    max_connected = extrema_by_code[SCREEN_CODES["max_connected"]]

    if (
        tuple(closest_all[f"face_{index}"] for index in range(6)),
        tuple(closest_all[f"ordered_{index}"] for index in range(6)),
        closest_all["area_x1e12"],
        closest_all["area_over_regular_ratio_x1e12"],
        closest_all["area_over_graham_ratio_x1e12"],
        closest_all["graham_error_x1e12"],
        closest_all["connected_flag"],
    ) != (
        (0, 1, 2, 9, 12, 13),
        (13, 0, 1, 9, 2, 12),
        654_459_905_217,
        1_007_607_021_837,
        969_597_522_325,
        20_521_094_783,
        0,
    ):
        raise AssertionError("eta6 hex-face barycenter closest-all row mismatch")

    if (
        tuple(max_all[f"face_{index}"] for index in range(6)),
        max_all["area_x1e12"],
        max_all["connected_flag"],
    ) != ((8, 9, 12, 15, 16, 19), 654_459_905_217, 0):
        raise AssertionError("eta6 hex-face barycenter max-all row mismatch")

    if (
        tuple(closest_connected[f"face_{index}"] for index in range(6)),
        tuple(closest_connected[f"ordered_{index}"] for index in range(6)),
        closest_connected["area_x1e12"],
        closest_connected["area_over_regular_ratio_x1e12"],
        closest_connected["area_over_graham_ratio_x1e12"],
        closest_connected["graham_error_x1e12"],
        closest_connected["connected_flag"],
    ) != (
        (0, 1, 4, 7, 11, 14),
        (0, 11, 7, 1, 14, 4),
        404_508_497_187,
        622_781_623_304,
        599_288_716_552,
        270_472_502_813,
        1,
    ):
        raise AssertionError("eta6 hex-face barycenter closest-connected row mismatch")

    if (
        tuple(max_connected[f"face_{index}"] for index in range(6)),
        max_connected["area_x1e12"],
        max_connected["connected_flag"],
    ) != ((10, 11, 13, 17, 18, 19), 404_508_497_187, 1):
        raise AssertionError("eta6 hex-face barycenter max-connected row mismatch")

    required_observables = {
        "hex_face_center_count": 20,
        "candidate_count_all": 38_760,
        "candidate_count_connected": 690,
        "simple_public_six_cycle_count": 0,
        "graham_tolerance_x1e12": GRAHAM_TOLERANCE_X1E12,
        "graham_area_x1e12": GRAHAM_AREA_X1E12,
        "regular_area_x1e12": REGULAR_AREA_X1E12,
        "within_graham_tolerance_all_count": 0,
        "within_graham_tolerance_connected_count": 0,
        "closest_all_area_x1e12": 654_459_905_217,
        "closest_all_graham_error_x1e12": 20_521_094_783,
        "closest_all_connected_flag": 0,
        "closest_connected_area_x1e12": 404_508_497_187,
        "closest_connected_graham_error_x1e12": 270_472_502_813,
        "max_all_area_x1e12": 654_459_905_217,
        "max_connected_area_x1e12": 404_508_497_187,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(
                f"eta6 hex-face barycenter observable {key} mismatch"
            )

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("truncated_skeleton_report", {}),
        TRUNCATED_SKELETON_REPORT,
        "truncated skeleton report input",
    )
    assert_file_hash(
        inputs.get("truncated_skeleton_tables", {}),
        TRUNCATED_SKELETON_TABLES,
        "truncated skeleton tables input",
    )
    assert_file_hash(
        inputs.get("hcycle_edge_table", {}),
        skeleton.HCYCLE_EDGE_TABLE,
        "H-cycle edge table input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen_manifest@1"
    ):
        raise AssertionError("eta6 hex-face barycenter manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 hex-face barycenter manifest report hash mismatch")
    if skeleton.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 hex-face barycenter manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 hex-face barycenter missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 hex-face barycenter index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 hex-face barycenter index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_hex_face_barycenter_graham_screen()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
