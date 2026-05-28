from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift import (
        DERIVE_SCRIPT,
        DINI_REPORT,
        DINI_TABLES,
        H4_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        TRANSFER_CENTERS,
        TRANSFER_REPORT,
        TRANSFER_TABLES,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift import (
        DERIVE_SCRIPT,
        DINI_REPORT,
        DINI_TABLES,
        H4_COLUMNS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        STATUS,
        THEOREM_ID,
        TRANSFER_CENTERS,
        TRANSFER_REPORT,
        TRANSFER_TABLES,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    h4_precursor = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_certificate.json"
    )
    coordinates_csv = (OUT_DIR / "eta6_h4_precursor_coordinates.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "eta6_h4_precursor_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if h4_precursor != expected["h4_precursor"]:
        raise AssertionError("eta6 H4 precursor JSON is not reproducible")
    if coordinates_csv != expected["coordinates_csv"]:
        raise AssertionError("eta6 H4 precursor coordinates CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 H4 precursor observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 H4 precursor certificate is not reproducible")

    for name in ["h4_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 H4 precursor table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift@1"
    ):
        raise AssertionError("eta6 H4 precursor report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 H4 precursor report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 H4 precursor all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 H4 precursor checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 H4 precursor report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 H4 precursor report hash is not reproducible")

    h4_table = np.asarray(tables["h4_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(h4_table.shape) != (5, len(H4_COLUMNS)):
        raise AssertionError("eta6 H4 precursor coordinate table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("eta6 H4 precursor observable table shape mismatch")

    h4_rows = table_rows(h4_table, H4_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if [row["h_conductance_x1e12"] for row in h4_rows] != [
        4_329_004_000,
        3_649_635_000,
        2_645_503_000,
        2_615_519_000,
        2_610_966_000,
    ]:
        raise AssertionError("eta6 H4 precursor height chain mismatch")
    if [row["r_holonomy_x1e12"] for row in h4_rows] != [
        1_000_000_000_000,
        1_000_000_000_000,
        1_000_000_000_000,
        1_000_000_000_000,
        1_000_000_000_000,
    ]:
        raise AssertionError("eta6 H4 precursor residual chain mismatch")
    if [row["poincare_available_flag"] for row in h4_rows] != [1, 0, 0, 0, 0]:
        raise AssertionError("eta6 H4 precursor Poincare availability mismatch")
    if any(row["inside_unit_disk_flag"] != 1 for row in h4_rows):
        raise AssertionError("eta6 H4 precursor coordinate outside unit disk")
    if any(row["h4_metric_certified_flag"] for row in h4_rows):
        raise AssertionError("eta6 H4 precursor unexpectedly certifies H4 metric")

    required_observables = {
        "coordinate_count": 5,
        "poincare_available_count": 1,
        "symbolic_precursor_count": 4,
        "inside_unit_disk_count": 5,
        "h4_metric_certified_count": 0,
        "r_fixed_nonzero_count": 5,
        "h_strict_descent_flag": 1,
        "base_x_x1e12": 67_572_661_820,
        "base_y_x1e12": 4_522_140_858,
        "base_radius_x1e12": 67_723_810_000,
        "final_h_conductance_x1e12": 2_610_966_000,
        "base_to_final_h_drop_x1e12": 1_718_038_000,
        "symbolic_chart_max_radius_x1e12": 397_707_725_008,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 H4 precursor observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("dini_report", {}), DINI_REPORT, "Dini report input")
    assert_file_hash(inputs.get("dini_tables", {}), DINI_TABLES, "Dini tables input")
    assert_file_hash(
        inputs.get("second_window_transfer_report", {}),
        TRANSFER_REPORT,
        "second-window transfer report input",
    )
    assert_file_hash(
        inputs.get("second_window_transfer_centers", {}),
        TRANSFER_CENTERS,
        "second-window transfer centers input",
    )
    assert_file_hash(
        inputs.get("second_window_transfer_tables", {}),
        TRANSFER_TABLES,
        "second-window transfer tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift_manifest@1"
    ):
        raise AssertionError("eta6 H4 precursor manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 H4 precursor manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 H4 precursor manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 H4 precursor missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 H4 precursor index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 H4 precursor index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_h4_precursor_lift()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
