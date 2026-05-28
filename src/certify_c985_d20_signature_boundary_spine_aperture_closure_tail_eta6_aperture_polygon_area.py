from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area import (
        DERIVE_SCRIPT,
        GRAHAM_REPORT,
        GRAHAM_TABLES,
        INDEX_PATH,
        METRIC_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        POINT_COLUMNS,
        PROMOTION_REPORT,
        PROMOTION_TABLES,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area import (
        DERIVE_SCRIPT,
        GRAHAM_REPORT,
        GRAHAM_TABLES,
        INDEX_PATH,
        METRIC_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        POINT_COLUMNS,
        PROMOTION_REPORT,
        PROMOTION_TABLES,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    aperture_polygon = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_certificate.json"
    )
    midpoints_csv = (OUT_DIR / "eta6_aperture_polygon_midpoints.csv").read_text(
        encoding="utf-8"
    )
    metrics_csv = (OUT_DIR / "eta6_aperture_polygon_metrics.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "eta6_aperture_polygon_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if aperture_polygon != expected["aperture_polygon"]:
        raise AssertionError("eta6 aperture polygon JSON is not reproducible")
    if midpoints_csv != expected["midpoints_csv"]:
        raise AssertionError("eta6 aperture polygon midpoint CSV is not reproducible")
    if metrics_csv != expected["metrics_csv"]:
        raise AssertionError("eta6 aperture polygon metric CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 aperture polygon observable CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 aperture polygon certificate is not reproducible")

    for name in ["point_table", "metric_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 aperture polygon table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area@1"
    ):
        raise AssertionError("eta6 aperture polygon report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 aperture polygon report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 aperture polygon all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 aperture polygon checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 aperture polygon report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 aperture polygon report hash is not reproducible")

    point_table = np.asarray(tables["point_table"], dtype=np.int64)
    metric_table = np.asarray(tables["metric_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(point_table.shape) != (6, len(POINT_COLUMNS)):
        raise AssertionError("eta6 aperture polygon point table shape mismatch")
    if tuple(metric_table.shape) != (1, len(METRIC_COLUMNS)):
        raise AssertionError("eta6 aperture polygon metric table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("eta6 aperture polygon observable table shape mismatch")

    point_rows = table_rows(point_table, POINT_COLUMNS)
    metric = table_rows(metric_table, METRIC_COLUMNS)[0]
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if [row["cut_edge_id"] for row in point_rows] != [
        2504,
        2516,
        2530,
        2537,
        2541,
        2545,
    ]:
        raise AssertionError("eta6 aperture polygon cut-edge ids mismatch")
    if sorted(
        point_rows,
        key=lambda row: row["polygon_order"],
    ) != [
        point_rows[1],
        point_rows[3],
        point_rows[2],
        point_rows[5],
        point_rows[0],
        point_rows[4],
    ]:
        raise AssertionError("eta6 aperture polygon cyclic order mismatch")
    if [row["cut_edge_id"] for row in point_rows if row["convex_hull_flag"] == 1] != [
        2504,
        2530,
        2541,
    ]:
        raise AssertionError("eta6 aperture polygon hull edge ids mismatch")
    required_metric = {
        "cut_edge_count": 6,
        "unique_midpoint_count": 6,
        "convex_hull_vertex_count": 3,
        "diameter_sq_x1e12": 10_540_354_657,
        "polygon_area_x1e12": 1_742_768_258,
        "diameter_normalized_area_x1e12": 165_342_468_540,
        "regular_area_x1e12": 649_519_000_000,
        "graham_area_x1e12": 674_981_000_000,
        "area_over_regular_ratio_x1e12": 254_561_403_962,
        "area_over_graham_ratio_x1e12": 244_958_700_378,
        "regular_area_abs_error_x1e12": 484_176_531_460,
        "graham_area_abs_error_x1e12": 509_638_531_460,
        "convex_hexagon_flag": 0,
        "graham_area_match_flag": 0,
        "area_certificate_available_flag": 1,
        "truncated_icosahedral_skeleton_certified_flag": 0,
    }
    for key, value in required_metric.items():
        if metric[key] != value:
            raise AssertionError(f"eta6 aperture polygon metric {key} mismatch")
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 aperture polygon observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("graham_throat_report", {}),
        GRAHAM_REPORT,
        "Graham throat report input",
    )
    assert_file_hash(
        inputs.get("graham_throat_tables", {}),
        GRAHAM_TABLES,
        "Graham throat tables input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_report", {}),
        PROMOTION_REPORT,
        "second-window promotion report input",
    )
    assert_file_hash(
        inputs.get("second_window_promotion_tables", {}),
        PROMOTION_TABLES,
        "second-window promotion tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area_manifest@1"
    ):
        raise AssertionError("eta6 aperture polygon manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 aperture polygon manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("eta6 aperture polygon manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 aperture polygon missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 aperture polygon index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 aperture polygon index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_aperture_polygon_area()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
