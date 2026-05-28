from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen import (
        ASSOCIATOR_REPORT,
        DERIVE_SCRIPT,
        HYPEREDGE_COLUMNS,
        INDEX_PATH,
        NONLOCAL_SCREEN_CERTIFICATE,
        NONLOCAL_SCREEN_JSON,
        NONLOCAL_SCREEN_REPORT,
        NONLOCAL_SCREEN_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PENTAGON_REPORT,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen import (
        ASSOCIATOR_REPORT,
        DERIVE_SCRIPT,
        HYPEREDGE_COLUMNS,
        INDEX_PATH,
        NONLOCAL_SCREEN_CERTIFICATE,
        NONLOCAL_SCREEN_JSON,
        NONLOCAL_SCREEN_REPORT,
        NONLOCAL_SCREEN_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PENTAGON_REPORT,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    hypergraph = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_certificate.json"
    )
    hyperedge_csv = (OUT_DIR / "sixj_borromean_hypergraph_hyperedges.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "sixj_borromean_hypergraph_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if hypergraph != expected["hypergraph"]:
        raise AssertionError("Borromean hypergraph JSON is not reproducible")
    if hyperedge_csv != expected["hyperedge_csv"]:
        raise AssertionError("Borromean hyperedge CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("Borromean observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("Borromean certificate is not reproducible")

    for name in ["hyperedge_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"Borromean table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen@1"
    ):
        raise AssertionError("Borromean report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("Borromean hypergraph screen is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("Borromean all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("Borromean checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("Borromean report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("Borromean report hash is not reproducible")

    hyperedge_table = np.asarray(tables["hyperedge_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(hyperedge_table.shape) != (20, len(HYPEREDGE_COLUMNS)):
        raise AssertionError("Borromean hyperedge table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("Borromean observable table shape mismatch")

    hyperedge_rows = table_rows(hyperedge_table, HYPEREDGE_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if not all(row["pairwise_shadow_inert_flag"] == 1 for row in hyperedge_rows):
        raise AssertionError("Borromean pairwise-inert shadow mismatch")
    if any(row["support_changed_flag"] for row in hyperedge_rows):
        raise AssertionError("Borromean support-changing hyperedge found")
    if any(row["borromean_opening_flag"] for row in hyperedge_rows):
        raise AssertionError("Borromean opening hyperedge found")
    if not all(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        for row in hyperedge_rows
    ):
        raise AssertionError("Borromean old cut support mismatch")
    if any(row["cut_conductance_x1e12"] < 4_329_004_000 for row in hyperedge_rows):
        raise AssertionError("Borromean conductance-improving hyperedge found")

    selected = [row for row in hyperedge_rows if row["selected_best_flag"] == 1]
    if len(selected) != 1:
        raise AssertionError("Borromean selected best row count mismatch")
    best = selected[0]
    if (
        best["hyperedge_id"],
        best["block_code_a"],
        best["block_code_b"],
        best["block_code_c"],
        best["state_count"],
        best["edge_count"],
        best["cut_edge_count"],
        best["old_cut_edge_still_cut_count"],
        best["lambda_2_x1e12"],
        best["cut_conductance_x1e12"],
        best["conductance_reduction_x1e12"],
    ) != (
        18,
        2_114,
        5_214,
        5_521,
        980,
        3_122,
        11,
        6,
        2_480_783_000,
        4_670_913_000,
        -341_909_000,
    ):
        raise AssertionError("Borromean selected best witness mismatch")

    required_observables = {
        "closed_metric_word_count": 984,
        "base_state_count": 860,
        "base_edge_count": 2_571,
        "base_cut_edge_count": 6,
        "base_cut_conductance_x1e12": 4_329_004_000,
        "selected_f_address_count": 6,
        "ordinary_repair_edge_count": 21,
        "ordinary_singleton_shadow_count": 6,
        "ordinary_pair_shadow_count": 15,
        "ordinary_shadow_support_changing_count": 0,
        "hyperedge_count": 20,
        "pairwise_inert_hyperedge_count": 20,
        "borromean_opening_hyperedge_count": 0,
        "support_changing_hyperedge_count": 0,
        "conductance_improving_hyperedge_count": 0,
        "best_block_code_a": 2_114,
        "best_block_code_b": 5_214,
        "best_block_code_c": 5_521,
        "best_state_count": 980,
        "best_edge_count": 3_122,
        "best_cut_edge_count": 11,
        "best_old_cut_edge_still_cut_count": 6,
        "best_lambda_2_x1e12": 2_480_783_000,
        "best_cut_conductance_x1e12": 4_670_913_000,
        "best_conductance_reduction_x1e12": -341_909_000,
        "max_cut_edge_count": 13,
        "min_old_cut_edge_still_cut_count": 6,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"Borromean observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("nonlocal_screen_report", {}),
        NONLOCAL_SCREEN_REPORT,
        "nonlocal screen report input",
    )
    assert_file_hash(
        inputs.get("nonlocal_screen_certificate", {}),
        NONLOCAL_SCREEN_CERTIFICATE,
        "nonlocal screen certificate input",
    )
    assert_file_hash(
        inputs.get("nonlocal_screen_tables", {}),
        NONLOCAL_SCREEN_TABLES,
        "nonlocal screen tables input",
    )
    assert_file_hash(
        inputs.get("nonlocal_screen_json", {}),
        NONLOCAL_SCREEN_JSON,
        "nonlocal screen JSON input",
    )
    assert_file_hash(
        inputs.get("associator_report", {}),
        ASSOCIATOR_REPORT,
        "associator report input",
    )
    assert_file_hash(
        inputs.get("pentagon_report", {}),
        PENTAGON_REPORT,
        "pentagon report input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen_manifest@1"
    ):
        raise AssertionError("Borromean manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Borromean manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("Borromean manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("Borromean screen missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("Borromean index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("Borromean index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_borromean_hypergraph_screen()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
