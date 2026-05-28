from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_sixj_conductance import (
        AGGREGATE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SOURCE_DEFS,
        SOURCE_SUMMARY_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_sixj_conductance import (
        AGGREGATE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        SOURCE_DEFS,
        SOURCE_SUMMARY_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    preservation = load_json(
        OUT_DIR
        / "sixj_conductance.json"
    )
    certificate = load_json(
        OUT_DIR
        / "sixj_conductance_certificate.json"
    )
    aggregate_csv = (
        OUT_DIR / "sixj_conductance_decreasing_aperture_preservation_rows.csv"
    ).read_text(encoding="utf-8")
    source_summary_csv = (
        OUT_DIR
        / "sixj_conductance_decreasing_aperture_preservation_source_summary.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR
        / "sixj_conductance_decreasing_aperture_preservation_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "sixj_conductance_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if preservation != expected["preservation"]:
        raise AssertionError("conductance-preservation JSON is not reproducible")
    if aggregate_csv != expected["aggregate_csv"]:
        raise AssertionError("conductance-preservation aggregate CSV is not reproducible")
    if source_summary_csv != expected["source_summary_csv"]:
        raise AssertionError(
            "conductance-preservation source summary CSV is not reproducible"
        )
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("conductance-preservation observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("conductance-preservation certificate is not reproducible")

    for name in ["aggregate_table", "source_summary_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"conductance-preservation table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation@1"
    ):
        raise AssertionError("conductance-preservation report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("conductance-preservation report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("conductance-preservation all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("conductance-preservation checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("conductance-preservation report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("conductance-preservation report hash is not reproducible")

    aggregate_table = np.asarray(tables["aggregate_table"], dtype=np.int64)
    source_summary_table = np.asarray(tables["source_summary_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(aggregate_table.shape) != (606, len(AGGREGATE_COLUMNS)):
        raise AssertionError("conductance-preservation aggregate table shape mismatch")
    if tuple(source_summary_table.shape) != (7, len(SOURCE_SUMMARY_COLUMNS)):
        raise AssertionError("conductance-preservation source summary shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("conductance-preservation observable table shape mismatch")

    aggregate_rows = table_rows(aggregate_table, AGGREGATE_COLUMNS)
    source_rows = table_rows(source_summary_table, SOURCE_SUMMARY_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if any(row["support_changed_flag"] for row in aggregate_rows):
        raise AssertionError("conductance-preservation support-changing row found")
    if any(row["aperture_preserved_flag"] != 1 for row in aggregate_rows):
        raise AssertionError("conductance-preservation aperture-preserved flag mismatch")
    decreasing_rows = [
        row for row in aggregate_rows if row["conductance_decreasing_flag"] == 1
    ]
    if len(decreasing_rows) != 153:
        raise AssertionError("conductance-preservation decreasing row count mismatch")
    if not all(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        and row["support_changed_flag"] == 0
        for row in decreasing_rows
    ):
        raise AssertionError("conductance-preservation decreasing aperture mismatch")

    expected_source_rows = {
        0: (45, 16, 0),
        1: (84, 25, 0),
        2: (382, 63, 0),
        3: (21, 3, 0),
        4: (28, 24, 0),
        5: (26, 22, 0),
        6: (20, 0, 0),
    }
    for row in source_rows:
        expected_counts = expected_source_rows.get(row["source_code"])
        if expected_counts is None:
            raise AssertionError("conductance-preservation unexpected source code")
        if (
            row["row_count"],
            row["conductance_decreasing_count"],
            row["support_changing_count"],
        ) != expected_counts:
            raise AssertionError("conductance-preservation source count mismatch")

    selected = min(
        decreasing_rows,
        key=lambda row: (
            row["cut_conductance_x1e12"],
            -row["lambda_2_x1e12"],
            row["source_code"],
            row["source_row_id"],
        ),
    )
    if (
        selected["source_code"],
        selected["source_row_id"],
        selected["intervention_size"],
        selected["block_code_0"],
        selected["block_code_1"],
        selected["block_code_2"],
        selected["state_count"],
        selected["edge_count"],
        selected["cut_edge_count"],
        selected["old_cut_edge_still_cut_count"],
        selected["lambda_2_x1e12"],
        selected["cut_conductance_x1e12"],
        selected["conductance_reduction_x1e12"],
    ) != (
        5,
        10,
        3,
        2_114,
        5_255,
        1_521,
        957,
        3_063,
        6,
        6,
        1_967_643_000,
        2_610_966_000,
        1_718_038_000,
    ):
        raise AssertionError("conductance-preservation best decreasing witness mismatch")

    required_observables = {
        "source_count": 7,
        "aggregate_row_count": 606,
        "conductance_decreasing_row_count": 153,
        "nonconductance_decreasing_row_count": 453,
        "support_changing_row_count": 0,
        "conductance_decreasing_support_changing_count": 0,
        "all_rows_aperture_preserved_count": 606,
        "min_decreasing_old_cut_edge_still_cut_count": 6,
        "max_decreasing_old_cut_edge_same_side_count": 0,
        "best_source_code": 5,
        "best_source_row_id": 10,
        "best_intervention_size": 3,
        "best_block_code_0": 2_114,
        "best_block_code_1": 5_255,
        "best_block_code_2": 1_521,
        "best_state_count": 957,
        "best_edge_count": 3_063,
        "best_cut_edge_count": 6,
        "best_old_cut_edge_still_cut_count": 6,
        "best_lambda_2_x1e12": 1_967_643_000,
        "best_cut_conductance_x1e12": 2_610_966_000,
        "best_conductance_reduction_x1e12": 1_718_038_000,
        "borromean_hyperedge_count": 20,
        "borromean_conductance_decreasing_count": 0,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"conductance-preservation observable {key} mismatch")

    inputs = report.get("inputs", {})
    for source in SOURCE_DEFS:
        entry = inputs.get(source["name"], {})
        assert_file_hash(
            entry.get("report", {}),
            source["report"],
            f"{source['name']} report input",
        )
        assert_file_hash(
            entry.get("tables", {}),
            source["tables"],
            f"{source['name']} tables input",
        )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation_manifest@1"
    ):
        raise AssertionError("conductance-preservation manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("conductance-preservation manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("conductance-preservation manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("conductance-preservation missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("conductance-preservation index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("conductance-preservation index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_conductance_decreasing_aperture_preservation()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
