from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLOSED_PATH_COLUMNS,
        CLOSURE_OUTLIER_CERTIFICATE,
        CLOSURE_OUTLIER_JSON,
        CLOSURE_OUTLIER_REPORT,
        CLOSURE_OUTLIER_SELECTED_BRANCHES,
        CLOSURE_OUTLIER_TABLES,
        DERIVE_SCRIPT,
        ENDPOINT_COLUMNS,
        FINAL_PRE_ORIGIN_CARRIER_ID,
        FIXED_TAIL_ATOMS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_OUTLIER_ID,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        TAIL_ENTRY_CARRIERS,
        TAIL_START_SYMBOL_INDEX,
        TAIL_TEMPLATE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WITNESS_IDS,
        WITNESS_SUMMARY_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        CLOSED_PATH_COLUMNS,
        CLOSURE_OUTLIER_CERTIFICATE,
        CLOSURE_OUTLIER_JSON,
        CLOSURE_OUTLIER_REPORT,
        CLOSURE_OUTLIER_SELECTED_BRANCHES,
        CLOSURE_OUTLIER_TABLES,
        DERIVE_SCRIPT,
        ENDPOINT_COLUMNS,
        FINAL_PRE_ORIGIN_CARRIER_ID,
        FIXED_TAIL_ATOMS,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_OUTLIER_ID,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        TAIL_ENTRY_CARRIERS,
        TAIL_START_SYMBOL_INDEX,
        TAIL_TEMPLATE_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        WITNESS_IDS,
        WITNESS_SUMMARY_COLUMNS,
        build_payloads,
        self_hash,
    )


EXPECTED_TEMPLATE_CARRIERS = [
    (9, 10, 3, 8, 13, 12),
    (9, 10, 11, 8, 13, 12),
    (9, 11, 3, 8, 13, 12),
    (10, 11, 3, 8, 13, 12),
    (11, 10, 3, 8, 13, 12),
    (11, 10, 11, 8, 13, 12),
]
EXPECTED_TEMPLATE_EDGES = [
    (34, 12, 11, 33, 43),
    (34, 38, 31, 33, 43),
    (35, 13, 11, 33, 43),
    (38, 13, 11, 33, 43),
    (38, 12, 11, 33, 43),
    (38, 38, 31, 33, 43),
]
EXPECTED_ENDPOINT_ROWS = [
    {
        "witness_id": 9,
        "tail_entry_carrier_id": 9,
        "normalized_tail_template_count": 3,
        "closed_path_count": 6,
        "path_count_per_template_min": 2,
        "path_count_per_template_max": 2,
    },
    {
        "witness_id": 9,
        "tail_entry_carrier_id": 10,
        "normalized_tail_template_count": 1,
        "closed_path_count": 2,
        "path_count_per_template_min": 2,
        "path_count_per_template_max": 2,
    },
    {
        "witness_id": 9,
        "tail_entry_carrier_id": 11,
        "normalized_tail_template_count": 2,
        "closed_path_count": 4,
        "path_count_per_template_min": 2,
        "path_count_per_template_max": 2,
    },
    {
        "witness_id": 23,
        "tail_entry_carrier_id": 9,
        "normalized_tail_template_count": 3,
        "closed_path_count": 12,
        "path_count_per_template_min": 4,
        "path_count_per_template_max": 4,
    },
    {
        "witness_id": 23,
        "tail_entry_carrier_id": 10,
        "normalized_tail_template_count": 1,
        "closed_path_count": 4,
        "path_count_per_template_min": 4,
        "path_count_per_template_max": 4,
    },
    {
        "witness_id": 23,
        "tail_entry_carrier_id": 11,
        "normalized_tail_template_count": 2,
        "closed_path_count": 8,
        "path_count_per_template_min": 4,
        "path_count_per_template_max": 4,
    },
]


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


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def row_tuple(row: dict[str, int], columns: list[str]) -> tuple[int, ...]:
    return tuple(row[column] for column in columns)


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    endpoint_split = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_closure_tail_endpoint_split.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate.json"
    )
    summary_csv = (OUT_DIR / "aperture_closure_tail_witness_summaries.csv").read_text(
        encoding="utf-8"
    )
    closed_csv = (OUT_DIR / "aperture_closure_tail_closed_paths.csv").read_text(
        encoding="utf-8"
    )
    template_csv = (OUT_DIR / "aperture_closure_tail_templates.csv").read_text(
        encoding="utf-8"
    )
    endpoint_csv = (OUT_DIR / "aperture_closure_tail_endpoint_counts.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "aperture_closure_tail_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_endpoint_split_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        endpoint_split
        != expected[
            "signature_boundary_spine_aperture_closure_tail_endpoint_split"
        ]
    ):
        raise AssertionError("closure-tail endpoint split JSON is not reproducible")
    if summary_csv != expected["aperture_closure_tail_witness_summaries_csv"]:
        raise AssertionError("closure-tail witness summary CSV is not reproducible")
    if closed_csv != expected["aperture_closure_tail_closed_paths_csv"]:
        raise AssertionError("closure-tail closed path CSV is not reproducible")
    if template_csv != expected["aperture_closure_tail_templates_csv"]:
        raise AssertionError("closure-tail template CSV is not reproducible")
    if endpoint_csv != expected["aperture_closure_tail_endpoint_counts_csv"]:
        raise AssertionError("closure-tail endpoint CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_observables_csv"]:
        raise AssertionError("closure-tail observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate"
        ]
    ):
        raise AssertionError("closure-tail certificate is not reproducible")

    for name in [
        "summary_table",
        "closed_path_table",
        "template_table",
        "endpoint_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"closure-tail table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split@1":
        raise AssertionError("closure-tail report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("closure-tail layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("closure-tail all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("closure-tail checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure-tail report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("closure-tail report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"closure-tail missing true checks: {missing}")

    summary_table = np.asarray(tables["summary_table"], dtype=np.int64)
    closed_path_table = np.asarray(tables["closed_path_table"], dtype=np.int64)
    template_table = np.asarray(tables["template_table"], dtype=np.int64)
    endpoint_table = np.asarray(tables["endpoint_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if summary_table.shape != (2, len(WITNESS_SUMMARY_COLUMNS)):
        raise AssertionError("closure-tail summary table shape mismatch")
    if closed_path_table.shape != (36, len(CLOSED_PATH_COLUMNS)):
        raise AssertionError("closure-tail closed path table shape mismatch")
    if template_table.shape != (6, len(TAIL_TEMPLATE_COLUMNS)):
        raise AssertionError("closure-tail template table shape mismatch")
    if endpoint_table.shape != (6, len(ENDPOINT_COLUMNS)):
        raise AssertionError("closure-tail endpoint table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("closure-tail observable table shape mismatch")

    summary_rows = table_rows(summary_table, WITNESS_SUMMARY_COLUMNS)
    closed_path_rows = table_rows(closed_path_table, CLOSED_PATH_COLUMNS)
    template_rows = table_rows(template_table, TAIL_TEMPLATE_COLUMNS)
    endpoint_rows = table_rows(endpoint_table, ENDPOINT_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)

    if [row["witness_id"] for row in summary_rows] != list(WITNESS_IDS):
        raise AssertionError("closure-tail witness ids mismatch")
    if [row["full_carrier_path_count"] for row in summary_rows] != [120, 240]:
        raise AssertionError("closure-tail full path counts mismatch")
    if [row["first_return_closed_path_count"] for row in summary_rows] != [12, 24]:
        raise AssertionError("closure-tail closed path counts mismatch")
    if [row["normalized_tail_template_count"] for row in summary_rows] != [6, 6]:
        raise AssertionError("closure-tail template counts mismatch")
    if [row["tail_entry_carrier_count"] for row in summary_rows] != [3, 3]:
        raise AssertionError("closure-tail endpoint counts mismatch")
    if [row["template_lift_count_min"] for row in summary_rows] != [2, 4]:
        raise AssertionError("closure-tail template lift minima mismatch")
    if [row["template_lift_count_max"] for row in summary_rows] != [2, 4]:
        raise AssertionError("closure-tail template lift maxima mismatch")
    if [row["fixed_tail_atom_sequence_flag"] for row in summary_rows] != [1, 1]:
        raise AssertionError("closure-tail fixed-tail flags mismatch")
    if [row["final_pre_origin_carrier_id"] for row in summary_rows] != [13, 13]:
        raise AssertionError("closure-tail final pre-origin carriers mismatch")
    if [row["intermediate_origin_hit_count"] for row in summary_rows] != [0, 0]:
        raise AssertionError("closure-tail intermediate origin hits mismatch")
    if [
        row["shared_tail_start_symbol_index"] for row in summary_rows
    ] != [TAIL_START_SYMBOL_INDEX[witness_id] for witness_id in WITNESS_IDS]:
        raise AssertionError("closure-tail shared tail start mismatch")
    if [
        (row["tail_entry_9_path_count"], row["tail_entry_10_path_count"], row["tail_entry_11_path_count"])
        for row in summary_rows
    ] != [(6, 2, 4), (12, 4, 8)]:
        raise AssertionError("closure-tail summary endpoint histogram mismatch")

    closed_counts = Counter(row["witness_id"] for row in closed_path_rows)
    if closed_counts != {9: 12, 23: 24}:
        raise AssertionError("closure-tail closed path witness counts mismatch")
    if any(row["first_return_closed_flag"] != 1 for row in closed_path_rows):
        raise AssertionError("closure-tail closed path first-return flag mismatch")
    if any(
        row["final_pre_origin_carrier_id"] != FINAL_PRE_ORIGIN_CARRIER_ID
        for row in closed_path_rows
    ):
        raise AssertionError("closure-tail final pre-origin path mismatch")
    if any(
        row_tuple(row, TAIL_ATOM_COLUMNS) != FIXED_TAIL_ATOMS
        for row in closed_path_rows
    ):
        raise AssertionError("closure-tail closed path atom tail mismatch")

    if [
        row_tuple(row, TAIL_CARRIER_COLUMNS) for row in template_rows
    ] != EXPECTED_TEMPLATE_CARRIERS:
        raise AssertionError("closure-tail template carriers mismatch")
    if [
        row_tuple(row, TAIL_EDGE_COLUMNS) for row in template_rows
    ] != EXPECTED_TEMPLATE_EDGES:
        raise AssertionError("closure-tail template edges mismatch")
    if any(
        row_tuple(row, TAIL_ATOM_COLUMNS) != FIXED_TAIL_ATOMS
        for row in template_rows
    ):
        raise AssertionError("closure-tail template atom tails mismatch")
    if [
        (row["baseline_outlier_path_count"], row["rank104_outlier_path_count"])
        for row in template_rows
    ] != [(2, 4)] * 6:
        raise AssertionError("closure-tail template lift counts mismatch")
    if any(
        row["rank104_to_baseline_multiplier_x1e6"] != 2_000_000
        for row in template_rows
    ):
        raise AssertionError("closure-tail template multiplier mismatch")
    if Counter(row["tail_entry_carrier_id"] for row in template_rows) != {
        9: 3,
        10: 1,
        11: 2,
    }:
        raise AssertionError("closure-tail template endpoint distribution mismatch")

    if endpoint_rows != EXPECTED_ENDPOINT_ROWS:
        raise AssertionError("closure-tail endpoint row mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES["baseline_closed_path_count"]: 12,
        OBSERVABLE_CODES["rank104_closed_path_count"]: 24,
        OBSERVABLE_CODES["closure_multiplier_x1e6"]: 2_000_000,
        OBSERVABLE_CODES["normalized_tail_template_count"]: 6,
        OBSERVABLE_CODES["baseline_template_lift_count"]: 2,
        OBSERVABLE_CODES["rank104_template_lift_count"]: 4,
        OBSERVABLE_CODES["tail_entry_carrier_count"]: len(TAIL_ENTRY_CARRIERS),
        OBSERVABLE_CODES["tail_entry_9_baseline_count"]: 6,
        OBSERVABLE_CODES["tail_entry_9_rank104_count"]: 12,
        OBSERVABLE_CODES["tail_entry_10_baseline_count"]: 2,
        OBSERVABLE_CODES["tail_entry_10_rank104_count"]: 4,
        OBSERVABLE_CODES["tail_entry_11_baseline_count"]: 4,
        OBSERVABLE_CODES["tail_entry_11_rank104_count"]: 8,
        OBSERVABLE_CODES["fixed_tail_atom_sequence_flag"]: 1,
        OBSERVABLE_CODES["final_pre_origin_carrier_id"]: 13,
        OBSERVABLE_CODES["intermediate_origin_hit_count"]: 0,
    }
    if observables != expected_observables:
        raise AssertionError("closure-tail observables mismatch")

    witness = report.get("witness", {})
    if witness.get("baseline_outlier", {}).get("witness_id") != 9:
        raise AssertionError("closure-tail baseline witness mismatch")
    if witness.get("rank104_outlier", {}).get("witness_id") != RANK104_OUTLIER_ID:
        raise AssertionError("closure-tail rank104 witness mismatch")
    if witness.get("fixed_tail_atom_sequence") != list(FIXED_TAIL_ATOMS):
        raise AssertionError("closure-tail witness atom sequence mismatch")
    if len(witness.get("normalized_tail_templates", [])) != 6:
        raise AssertionError("closure-tail witness template count mismatch")
    if endpoint_split.get("summary", {}).get("baseline_closed_path_count") != 12:
        raise AssertionError("closure-tail endpoint split baseline count mismatch")
    if endpoint_split.get("summary", {}).get("rank104_closed_path_count") != 24:
        raise AssertionError("closure-tail endpoint split rank104 count mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("closure-tail certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("closure_outlier_report", {}), CLOSURE_OUTLIER_REPORT, "closure outlier report input")
    assert_file_hash(inputs.get("closure_outlier_json", {}), CLOSURE_OUTLIER_JSON, "closure outlier JSON input")
    assert_file_hash(inputs.get("closure_outlier_selected_branches", {}), CLOSURE_OUTLIER_SELECTED_BRANCHES, "closure outlier selected branches input")
    assert_file_hash(inputs.get("closure_outlier_tables", {}), CLOSURE_OUTLIER_TABLES, "closure outlier tables input")
    assert_file_hash(inputs.get("closure_outlier_certificate", {}), CLOSURE_OUTLIER_CERTIFICATE, "closure outlier certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split_manifest@1":
        raise AssertionError("closure-tail manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure-tail manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("closure-tail manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("closure-tail missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure-tail index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("closure-tail index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_endpoint_split@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "baseline_outlier": witness.get("baseline_outlier"),
        "rank104_outlier": witness.get("rank104_outlier"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
