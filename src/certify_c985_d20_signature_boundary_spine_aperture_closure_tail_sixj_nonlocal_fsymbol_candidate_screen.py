from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen import (
        ASSOCIATOR_REPORT,
        CANDIDATE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PENTAGON_REPORT,
        STATUS,
        TETRAHEDRAL_CLOSURE_CERTIFICATE,
        TETRAHEDRAL_CLOSURE_REPORT,
        TETRAHEDRAL_CLOSURE_TABLES,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen import (
        ASSOCIATOR_REPORT,
        CANDIDATE_COLUMNS,
        DERIVE_SCRIPT,
        INDEX_PATH,
        INTERVENTION_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PENTAGON_REPORT,
        STATUS,
        TETRAHEDRAL_CLOSURE_CERTIFICATE,
        TETRAHEDRAL_CLOSURE_REPORT,
        TETRAHEDRAL_CLOSURE_TABLES,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    screen = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_certificate.json"
    )
    candidate_csv = (OUT_DIR / "sixj_nonlocal_fsymbol_candidates.csv").read_text(
        encoding="utf-8"
    )
    intervention_csv = (
        OUT_DIR / "sixj_nonlocal_fsymbol_screen_interventions.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "sixj_nonlocal_fsymbol_screen_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if screen != expected["nonlocal_screen"]:
        raise AssertionError("sixj nonlocal screen JSON is not reproducible")
    if candidate_csv != expected["candidate_csv"]:
        raise AssertionError("sixj nonlocal candidate CSV is not reproducible")
    if intervention_csv != expected["intervention_csv"]:
        raise AssertionError("sixj nonlocal intervention CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("sixj nonlocal observable CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("sixj nonlocal certificate is not reproducible")

    for name in ["candidate_table", "intervention_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"sixj nonlocal table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen@1"
    ):
        raise AssertionError("sixj nonlocal report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("sixj nonlocal screen is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("sixj nonlocal all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("sixj nonlocal checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("sixj nonlocal report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("sixj nonlocal report hash is not reproducible")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    intervention_table = np.asarray(tables["intervention_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(candidate_table.shape) != (171, len(CANDIDATE_COLUMNS)):
        raise AssertionError("sixj nonlocal candidate table shape mismatch")
    if tuple(intervention_table.shape) != (21, len(INTERVENTION_COLUMNS)):
        raise AssertionError("sixj nonlocal intervention table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("sixj nonlocal observable table shape mismatch")

    candidate_rows = table_rows(candidate_table, CANDIDATE_COLUMNS)
    intervention_rows = table_rows(intervention_table, INTERVENTION_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    selected_codes = [
        row["block_code"] for row in candidate_rows if row["selected_screen_flag"] == 1
    ]
    if selected_codes != [1452, 4521, 2114, 1145, 5214, 5521]:
        raise AssertionError("sixj nonlocal selected candidate order mismatch")
    if any(row["local_touch_flag"] or row["base_promoted_flag"] for row in candidate_rows):
        raise AssertionError("sixj nonlocal candidate table leaked local blocks")
    if any(row["support_changed_flag"] for row in intervention_rows):
        raise AssertionError("sixj nonlocal support-changing row found")
    if not all(
        row["old_cut_edge_still_cut_count"] == 6
        and row["old_cut_edge_same_side_count"] == 0
        for row in intervention_rows
    ):
        raise AssertionError("sixj nonlocal old cut support mismatch")

    selected = [row for row in intervention_rows if row["selected_best_flag"] == 1]
    if len(selected) != 1:
        raise AssertionError("sixj nonlocal selected best count mismatch")
    best = selected[0]
    if (
        best["intervention_size"],
        best["block_code_a"],
        best["block_code_b"],
        best["state_count"],
        best["edge_count"],
        best["cut_edge_count"],
        best["old_cut_edge_still_cut_count"],
        best["lambda_2_x1e12"],
        best["cut_conductance_x1e12"],
        best["conductance_reduction_x1e12"],
    ) != (1, 2114, -1, 945, 3_045, 6, 6, 1_972_362_000, 2_645_503_000, 1_683_501_000):
        raise AssertionError("sixj nonlocal selected best witness mismatch")

    required_observables = {
        "closed_metric_word_count": 984,
        "base_state_count": 860,
        "base_edge_count": 2_571,
        "base_cut_edge_count": 6,
        "base_cut_conductance_x1e12": 4_329_004_000,
        "local_touch_block_count": 15,
        "nonlocal_block_count": 171,
        "screen_block_count": 6,
        "screen_intervention_count": 21,
        "support_changing_intervention_count": 0,
        "best_intervention_size": 1,
        "best_block_code_a": 2_114,
        "best_block_code_b": -1,
        "best_state_count": 945,
        "best_edge_count": 3_045,
        "best_cut_edge_count": 6,
        "best_old_cut_edge_still_cut_count": 6,
        "best_lambda_2_x1e12": 1_972_362_000,
        "best_cut_conductance_x1e12": 2_645_503_000,
        "best_conductance_reduction_x1e12": 1_683_501_000,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"sixj nonlocal observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("tetrahedral_closure_report", {}),
        TETRAHEDRAL_CLOSURE_REPORT,
        "tetrahedral closure report input",
    )
    assert_file_hash(
        inputs.get("tetrahedral_closure_certificate", {}),
        TETRAHEDRAL_CLOSURE_CERTIFICATE,
        "tetrahedral closure certificate input",
    )
    assert_file_hash(
        inputs.get("tetrahedral_closure_tables", {}),
        TETRAHEDRAL_CLOSURE_TABLES,
        "tetrahedral closure tables input",
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
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen_manifest@1"
    ):
        raise AssertionError("sixj nonlocal manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj nonlocal manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("sixj nonlocal manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("sixj nonlocal missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("sixj nonlocal index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("sixj nonlocal index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_sixj_nonlocal_fsymbol_candidate_screen()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
