from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        BRIDGE_COLUMNS,
        CLOSURE_OUTLIER_CERTIFICATE,
        CLOSURE_OUTLIER_REPORT,
        CLOSURE_OUTLIER_SELECTED_BRANCHES,
        DELTA_WITNESS_COLUMNS,
        DERIVE_SCRIPT,
        ENDPOINT_SPLIT_CERTIFICATE,
        ENDPOINT_SPLIT_CLOSED_PATHS,
        ENDPOINT_SPLIT_JSON,
        ENDPOINT_SPLIT_REPORT,
        ENDPOINT_SPLIT_TABLES,
        ENDPOINT_SPLIT_TEMPLATES,
        FIXED_TAIL_ATOMS,
        INDEX_PATH,
        NODE45_WINDOW,
        NODE54_WINDOW,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_OUTLIER_ID,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SHARED_REWRITE_TAIL,
        SHARED_TAIL_WORD,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        TEMPLATE_COLUMNS,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        TRACE_SIGNATURE_COLUMNS,
        VALIDATOR_SCRIPT,
        WITNESS_IDS,
        WITNESS_METRIC_COLUMNS,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        BRIDGE_COLUMNS,
        CLOSURE_OUTLIER_CERTIFICATE,
        CLOSURE_OUTLIER_REPORT,
        CLOSURE_OUTLIER_SELECTED_BRANCHES,
        DELTA_WITNESS_COLUMNS,
        DERIVE_SCRIPT,
        ENDPOINT_SPLIT_CERTIFICATE,
        ENDPOINT_SPLIT_CLOSED_PATHS,
        ENDPOINT_SPLIT_JSON,
        ENDPOINT_SPLIT_REPORT,
        ENDPOINT_SPLIT_TABLES,
        ENDPOINT_SPLIT_TEMPLATES,
        FIXED_TAIL_ATOMS,
        INDEX_PATH,
        NODE45_WINDOW,
        NODE54_WINDOW,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANK104_OUTLIER_ID,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_NODES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SHARED_REWRITE_TAIL,
        SHARED_TAIL_WORD,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        TEMPLATE_COLUMNS,
        THEOREM_ID,
        TRACE_NODE_COLUMNS,
        TRACE_SIGNATURE_COLUMNS,
        VALIDATOR_SCRIPT,
        WITNESS_IDS,
        WITNESS_METRIC_COLUMNS,
        build_payloads,
        self_hash,
    )


EXPECTED_BRIDGE_ROWS = [
    (9, 0, 27, 28, 146, 169, 23, 0, 0),
    (9, 1, 28, 34, 169, 177, 8, 0, 0),
    (9, 2, 34, 54, 177, 134, 43, 0, 1),
    (23, 0, 27, 31, 146, 151, 5, 1, 0),
    (23, 1, 31, 50, 151, 146, 5, 1, 0),
    (23, 2, 50, 54, 146, 134, 12, 1, 1),
]
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
EXPECTED_OBSERVABLES = {
    "baseline_delta_twice": 2,
    "rank104_delta_twice": 4,
    "rank104_delta_penalty_over_baseline": 2,
    "baseline_variation": 213,
    "rank104_variation": 161,
    "rank104_variation_advantage": 52,
    "common_tail_template_count": 6,
    "template_specific_delta_driver_count": 0,
    "uniform_template_lift_count": 6,
    "baseline_bridge_variation": 74,
    "rank104_bridge_variation": 22,
    "bridge_variation_advantage": 52,
    "common_prefix_variation": 88,
    "shared_tail_variation": 51,
    "rank104_best_delta_witness_count": 21,
    "rank104_high_delta_prefix_tail_witness_count": 18,
}


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


def trace_from_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in TRACE_NODE_COLUMNS[: row["trace_node_count"]])


def signatures_from_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[column] for column in TRACE_SIGNATURE_COLUMNS[: row["trace_node_count"]]
    )


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    rewrite_lift = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_rewrite_node_lift.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_rewrite_node_lift_certificate.json"
    )
    witness_csv = (
        OUT_DIR / "aperture_closure_tail_rewrite_witness_metrics.csv"
    ).read_text(encoding="utf-8")
    bridge_csv = (OUT_DIR / "aperture_closure_tail_rewrite_bridges.csv").read_text(
        encoding="utf-8"
    )
    template_csv = (OUT_DIR / "aperture_closure_tail_rewrite_templates.csv").read_text(
        encoding="utf-8"
    )
    delta_csv = (
        OUT_DIR / "aperture_closure_tail_rewrite_delta_witnesses.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_rewrite_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_rewrite_node_lift_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        rewrite_lift
        != expected["signature_boundary_spine_aperture_closure_tail_rewrite_node_lift"]
    ):
        raise AssertionError("closure-tail rewrite lift JSON is not reproducible")
    if witness_csv != expected["aperture_closure_tail_rewrite_witness_metrics_csv"]:
        raise AssertionError("closure-tail rewrite witness CSV is not reproducible")
    if bridge_csv != expected["aperture_closure_tail_rewrite_bridges_csv"]:
        raise AssertionError("closure-tail rewrite bridge CSV is not reproducible")
    if template_csv != expected["aperture_closure_tail_rewrite_templates_csv"]:
        raise AssertionError("closure-tail rewrite template CSV is not reproducible")
    if delta_csv != expected["aperture_closure_tail_rewrite_delta_witnesses_csv"]:
        raise AssertionError("closure-tail rewrite delta CSV is not reproducible")
    if observables_csv != expected["aperture_closure_tail_rewrite_observables_csv"]:
        raise AssertionError("closure-tail rewrite observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_rewrite_node_lift_certificate"
        ]
    ):
        raise AssertionError("closure-tail rewrite certificate is not reproducible")

    for name in [
        "witness_table",
        "bridge_table",
        "template_table",
        "delta_witness_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"closure-tail rewrite table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift@1":
        raise AssertionError("closure-tail rewrite report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("closure-tail rewrite layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("closure-tail rewrite all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("closure-tail rewrite checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure-tail rewrite report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("closure-tail rewrite report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"closure-tail rewrite missing true checks: {missing}")

    witness_table = np.asarray(tables["witness_table"], dtype=np.int64)
    bridge_table = np.asarray(tables["bridge_table"], dtype=np.int64)
    template_table = np.asarray(tables["template_table"], dtype=np.int64)
    delta_witness_table = np.asarray(tables["delta_witness_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if witness_table.shape != (2, len(WITNESS_METRIC_COLUMNS)):
        raise AssertionError("closure-tail rewrite witness table shape mismatch")
    if bridge_table.shape != (6, len(BRIDGE_COLUMNS)):
        raise AssertionError("closure-tail rewrite bridge table shape mismatch")
    if template_table.shape != (6, len(TEMPLATE_COLUMNS)):
        raise AssertionError("closure-tail rewrite template table shape mismatch")
    if delta_witness_table.shape != (26, len(DELTA_WITNESS_COLUMNS)):
        raise AssertionError("closure-tail rewrite delta table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("closure-tail rewrite observable table shape mismatch")

    witness_rows = table_rows(witness_table, WITNESS_METRIC_COLUMNS)
    bridge_rows = table_rows(bridge_table, BRIDGE_COLUMNS)
    template_rows = table_rows(template_table, TEMPLATE_COLUMNS)
    delta_rows = table_rows(delta_witness_table, DELTA_WITNESS_COLUMNS)
    observable_rows = table_rows(observable_table, OBSERVABLE_COLUMNS)

    if [row["witness_id"] for row in witness_rows] != list(WITNESS_IDS):
        raise AssertionError("closure-tail rewrite witness ids mismatch")
    if [trace_from_row(row) for row in witness_rows] != [
        (48, 42, 27, 28, 34, 54, 45, 29, 28, 34, 44),
        (48, 42, 27, 31, 50, 54, 45, 29, 28, 34, 44),
    ]:
        raise AssertionError("closure-tail rewrite witness traces mismatch")
    if [signatures_from_row(row) for row in witness_rows] != [
        (132, 183, 146, 169, 177, 134, 148, 169, 169, 177, 185),
        (132, 183, 146, 151, 146, 134, 148, 169, 169, 177, 185),
    ]:
        raise AssertionError("closure-tail rewrite signatures mismatch")
    if [row["metric_gromov_delta_twice"] for row in witness_rows] != [2, 4]:
        raise AssertionError("closure-tail rewrite delta mismatch")
    if [row["trace_signature_total_variation"] for row in witness_rows] != [213, 161]:
        raise AssertionError("closure-tail rewrite variation mismatch")
    if [row["closed_path_count"] for row in witness_rows] != [12, 24]:
        raise AssertionError("closure-tail rewrite closed path mismatch")
    if [row["template_lift_count"] for row in witness_rows] != [2, 4]:
        raise AssertionError("closure-tail rewrite lift count mismatch")
    if [row["common_prefix_variation"] for row in witness_rows] != [88, 88]:
        raise AssertionError("closure-tail rewrite common prefix mismatch")
    if [row["bridge_variation"] for row in witness_rows] != [74, 22]:
        raise AssertionError("closure-tail rewrite bridge variation mismatch")
    if [row["shared_tail_variation"] for row in witness_rows] != [51, 51]:
        raise AssertionError("closure-tail rewrite shared tail mismatch")
    if [
        row["bridge_variation_advantage_over_baseline"] for row in witness_rows
    ] != [0, 52]:
        raise AssertionError("closure-tail rewrite bridge advantage mismatch")
    if [row["rank104_delta_penalty_over_baseline"] for row in witness_rows] != [0, 2]:
        raise AssertionError("closure-tail rewrite delta penalty mismatch")
    if [row["best_delta_witness_count"] for row in witness_rows] != [5, 21]:
        raise AssertionError("closure-tail rewrite best delta count mismatch")
    if [
        row["best_delta_witness_with_prefix_and_tail_node_count"]
        for row in witness_rows
    ] != [0, 18]:
        raise AssertionError("closure-tail rewrite prefix-tail count mismatch")
    if [row["template_specific_delta_driver_count"] for row in witness_rows] != [0, 0]:
        raise AssertionError("closure-tail rewrite template driver count mismatch")
    if [row["uniform_template_lift_flag"] for row in witness_rows] != [1, 1]:
        raise AssertionError("closure-tail rewrite uniform lift flags mismatch")

    if [row_tuple(row, BRIDGE_COLUMNS) for row in bridge_rows] != EXPECTED_BRIDGE_ROWS:
        raise AssertionError("closure-tail rewrite bridge rows mismatch")
    if [
        row_tuple(row, TAIL_CARRIER_COLUMNS) for row in template_rows
    ] != EXPECTED_TEMPLATE_CARRIERS:
        raise AssertionError("closure-tail rewrite template carriers mismatch")
    if [
        row_tuple(row, TAIL_EDGE_COLUMNS) for row in template_rows
    ] != EXPECTED_TEMPLATE_EDGES:
        raise AssertionError("closure-tail rewrite template edges mismatch")
    if any(
        row_tuple(row, TAIL_ATOM_COLUMNS) != FIXED_TAIL_ATOMS
        for row in template_rows
    ):
        raise AssertionError("closure-tail rewrite atom tail mismatch")
    if [
        (row["baseline_outlier_path_count"], row["rank104_outlier_path_count"])
        for row in template_rows
    ] != [(2, 4)] * 6:
        raise AssertionError("closure-tail rewrite template lift counts mismatch")
    if any(row["rank104_extra_path_count"] != 2 for row in template_rows):
        raise AssertionError("closure-tail rewrite template extra count mismatch")
    if any(
        row["rank104_to_baseline_multiplier_x1e6"] != 2_000_000
        for row in template_rows
    ):
        raise AssertionError("closure-tail rewrite template multiplier mismatch")
    if any(
        (
            row["node54_window_left_symbol_id"],
            row["node54_window_middle_symbol_id"],
            row["node54_window_right_symbol_id"],
        )
        != NODE54_WINDOW
        for row in template_rows
    ):
        raise AssertionError("closure-tail rewrite node54 window mismatch")
    if any(
        (
            row["node45_window_left_symbol_id"],
            row["node45_window_middle_symbol_id"],
            row["node45_window_right_symbol_id"],
        )
        != NODE45_WINDOW
        for row in template_rows
    ):
        raise AssertionError("closure-tail rewrite node45 window mismatch")
    if any(row["template_specific_delta_driver_flag"] != 0 for row in template_rows):
        raise AssertionError("closure-tail rewrite specific driver flag mismatch")
    if any(row["uniform_prefix_lift_driver_flag"] != 1 for row in template_rows):
        raise AssertionError("closure-tail rewrite uniform driver flag mismatch")

    delta_counts = Counter(row["witness_id"] for row in delta_rows)
    if delta_counts != {9: 5, 23: 21}:
        raise AssertionError("closure-tail rewrite delta witness counts mismatch")
    max_delta_by_witness = {
        witness_id: max(
            row["metric_gromov_delta_twice"]
            for row in delta_rows
            if row["witness_id"] == witness_id
        )
        for witness_id in delta_counts
    }
    if max_delta_by_witness != {9: 2, 23: 4}:
        raise AssertionError("closure-tail rewrite delta maxima mismatch")
    if sum(
        row["prefix_tail_interaction_flag"]
        for row in delta_rows
        if row["witness_id"] == RANK104_OUTLIER_ID
    ) != 18:
        raise AssertionError("closure-tail rewrite rank104 prefix-tail flags mismatch")
    if sum(
        row["contains_prefix_driver_node_flag"]
        for row in delta_rows
        if row["witness_id"] == 9
    ) != 0:
        raise AssertionError("closure-tail rewrite baseline prefix flags mismatch")
    if any(
        row["contains_shared_tail_node_flag"] != 1 for row in delta_rows
    ):
        raise AssertionError("closure-tail rewrite delta shared-tail flags mismatch")

    observables = {
        row["observable_code"]: row["value_x1e12"] // 10**12
        for row in observable_rows
    }
    expected_observables = {
        OBSERVABLE_CODES[key]: value for key, value in EXPECTED_OBSERVABLES.items()
    }
    if observables != expected_observables:
        raise AssertionError("closure-tail rewrite observables mismatch")

    witness = report.get("witness", {})
    if witness.get("baseline_outlier", {}).get("bridge") != [27, 28, 34, 54]:
        raise AssertionError("closure-tail rewrite baseline bridge mismatch")
    if witness.get("rank104_outlier", {}).get("bridge") != [27, 31, 50, 54]:
        raise AssertionError("closure-tail rewrite rank104 bridge mismatch")
    if witness.get("shared_rewrite_tail") != list(SHARED_REWRITE_TAIL):
        raise AssertionError("closure-tail rewrite shared tail mismatch")
    if witness.get("shared_symbol_tail") != list(SHARED_TAIL_WORD):
        raise AssertionError("closure-tail rewrite symbol tail mismatch")
    if witness.get("template_specific_delta_driver_count") != 0:
        raise AssertionError("closure-tail rewrite witness driver count mismatch")
    if rewrite_lift.get("summary", {}).get("rank104_delta_penalty") != 2:
        raise AssertionError("closure-tail rewrite summary delta penalty mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("closure-tail rewrite certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("endpoint_split_report", {}), ENDPOINT_SPLIT_REPORT, "endpoint split report input")
    assert_file_hash(inputs.get("endpoint_split_json", {}), ENDPOINT_SPLIT_JSON, "endpoint split JSON input")
    assert_file_hash(inputs.get("endpoint_split_templates", {}), ENDPOINT_SPLIT_TEMPLATES, "endpoint split templates input")
    assert_file_hash(inputs.get("endpoint_split_closed_paths", {}), ENDPOINT_SPLIT_CLOSED_PATHS, "endpoint split closed paths input")
    assert_file_hash(inputs.get("endpoint_split_tables", {}), ENDPOINT_SPLIT_TABLES, "endpoint split tables input")
    assert_file_hash(inputs.get("endpoint_split_certificate", {}), ENDPOINT_SPLIT_CERTIFICATE, "endpoint split certificate input")
    assert_file_hash(inputs.get("closure_outlier_report", {}), CLOSURE_OUTLIER_REPORT, "closure outlier report input")
    assert_file_hash(inputs.get("closure_outlier_selected_branches", {}), CLOSURE_OUTLIER_SELECTED_BRANCHES, "closure outlier selected branches input")
    assert_file_hash(inputs.get("closure_outlier_certificate", {}), CLOSURE_OUTLIER_CERTIFICATE, "closure outlier certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_nodes", {}), REWRITE_COMPLEX_NODES, "rewrite complex nodes input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity tables input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift_manifest@1":
        raise AssertionError("closure-tail rewrite manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure-tail rewrite manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("closure-tail rewrite manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("closure-tail rewrite missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("closure-tail rewrite index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("closure-tail rewrite index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift@1",
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
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
