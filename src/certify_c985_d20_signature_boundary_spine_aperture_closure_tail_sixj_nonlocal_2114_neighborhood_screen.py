from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        NONLOCAL_SCREEN_CERTIFICATE,
        NONLOCAL_SCREEN_REPORT,
        NONLOCAL_SCREEN_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARTNER_COLUMNS,
        STATUS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen import (
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        NONLOCAL_SCREEN_CERTIFICATE,
        NONLOCAL_SCREEN_REPORT,
        NONLOCAL_SCREEN_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PARTNER_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    neighborhood = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_certificate.json"
    )
    partner_csv = (OUT_DIR / "sixj_nonlocal_2114_neighborhood_partners.csv").read_text(
        encoding="utf-8"
    )
    intervention_csv = (
        OUT_DIR / "sixj_nonlocal_2114_neighborhood_interventions.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "sixj_nonlocal_2114_neighborhood_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if neighborhood != expected["neighborhood_screen"]:
        raise AssertionError("2114 neighborhood JSON is not reproducible")
    if partner_csv != expected["partner_csv"]:
        raise AssertionError("2114 partner CSV is not reproducible")
    if intervention_csv != expected["intervention_csv"]:
        raise AssertionError("2114 intervention CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("2114 observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("2114 certificate is not reproducible")

    for name in ["partner_table", "intervention_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"2114 table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen@1"
    ):
        raise AssertionError("2114 report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("2114 neighborhood screen is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("2114 all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("2114 checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("2114 report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("2114 report hash is not reproducible")

    partner_table = np.asarray(tables["partner_table"], dtype=np.int64)
    intervention_table = np.asarray(tables["intervention_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(partner_table.shape) != (27, len(PARTNER_COLUMNS)):
        raise AssertionError("2114 partner table shape mismatch")
    if tuple(intervention_table.shape) != (28, len(INTERVENTION_COLUMNS)):
        raise AssertionError("2114 intervention table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("2114 observable table shape mismatch")

    partner_rows = table_rows(partner_table, PARTNER_COLUMNS)
    intervention_rows = table_rows(intervention_table, INTERVENTION_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    near_codes = [row["block_code"] for row in partner_rows if row["partner_kind"] == 1]
    local_codes = [row["block_code"] for row in partner_rows if row["partner_kind"] == 2]
    if near_codes != [1145, 5211, 1143, 1144, 1211, 1452, 5521, 1431, 4521, 1445, 1521, 4121, 2521, 5221]:
        raise AssertionError("2114 two-hop nonlocal partner order mismatch")
    if local_codes != [1451, 4512, 4552, 5125, 1255, 5255, 1252, 2145, 5252, 4511, 4551, 5115, 5511]:
        raise AssertionError("2114 local partner order mismatch")
    if any(row["support_changed_flag"] for row in intervention_rows):
        raise AssertionError("2114 support-changing row found")
    if not all(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        for row in intervention_rows
    ):
        raise AssertionError("2114 old cut support mismatch")

    selected = [row for row in intervention_rows if row["selected_best_flag"] == 1]
    if len(selected) != 1:
        raise AssertionError("2114 selected best row count mismatch")
    best = selected[0]
    if (
        best["block_code_a"],
        best["block_code_b"],
        best["state_count"],
        best["edge_count"],
        best["cut_edge_count"],
        best["old_cut_edge_still_cut_count"],
        best["lambda_2_x1e12"],
        best["cut_conductance_x1e12"],
        best["conductance_reduction_x1e12"],
    ) != (2_114, 5_255, 952, 3_058, 6, 6, 1_969_615_000, 2_615_519_000, 1_713_485_000):
        raise AssertionError("2114 selected best witness mismatch")

    required_observables = {
        "closed_metric_word_count": 984,
        "base_state_count": 860,
        "base_edge_count": 2_571,
        "base_cut_edge_count": 6,
        "base_cut_conductance_x1e12": 4_329_004_000,
        "target_block_code": 2_114,
        "target_word_count": 123,
        "near_nonlocal_partner_count": 14,
        "local_partner_count": 13,
        "intervention_count": 28,
        "support_changing_intervention_count": 0,
        "best_block_code_a": 2_114,
        "best_block_code_b": 5_255,
        "best_state_count": 952,
        "best_edge_count": 3_058,
        "best_cut_edge_count": 6,
        "best_old_cut_edge_still_cut_count": 6,
        "best_lambda_2_x1e12": 1_969_615_000,
        "best_cut_conductance_x1e12": 2_615_519_000,
        "best_conductance_reduction_x1e12": 1_713_485_000,
        "max_cut_edge_count": 13,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"2114 observable {key} mismatch")

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
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen_manifest@1"
    ):
        raise AssertionError("2114 manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("2114 manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("2114 manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("2114 missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("2114 index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("2114 index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_2114_neighborhood_screen()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
