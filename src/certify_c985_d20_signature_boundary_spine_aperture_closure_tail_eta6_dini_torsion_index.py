from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index import (
        BASE_REPORT,
        CHAIN_COLUMNS,
        CONDUCTANCE_REPORT,
        CONDUCTANCE_TABLES,
        DERIVE_SCRIPT,
        HOLONOMY_REPORT,
        HOLONOMY_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        STATUS,
        STEP_COLUMNS,
        THEOREM_ID,
        VALIDATOR_SCRIPT,
        build_payloads,
        pair,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index import (
        BASE_REPORT,
        CHAIN_COLUMNS,
        CONDUCTANCE_REPORT,
        CONDUCTANCE_TABLES,
        DERIVE_SCRIPT,
        HOLONOMY_REPORT,
        HOLONOMY_TABLES,
        INDEX_PATH,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        STATUS,
        STEP_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    dini = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_certificate.json"
    )
    chain_csv = (OUT_DIR / "eta6_dini_torsion_chain.csv").read_text(
        encoding="utf-8"
    )
    steps_csv = (OUT_DIR / "eta6_dini_torsion_steps.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "eta6_dini_torsion_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if dini != expected["dini"]:
        raise AssertionError("eta6 Dini torsion JSON is not reproducible")
    if chain_csv != expected["chain_csv"]:
        raise AssertionError("eta6 Dini torsion chain CSV is not reproducible")
    if steps_csv != expected["steps_csv"]:
        raise AssertionError("eta6 Dini torsion step CSV is not reproducible")
    if observables_csv != expected["observables_csv"]:
        raise AssertionError("eta6 Dini torsion observables CSV is not reproducible")
    if certificate != expected["certificate"]:
        raise AssertionError("eta6 Dini torsion certificate is not reproducible")

    for name in ["chain_table", "step_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"eta6 Dini torsion table {name} mismatch")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index@1"
    ):
        raise AssertionError("eta6 Dini torsion report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("eta6 Dini torsion report is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("eta6 Dini torsion all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("eta6 Dini torsion checks mismatch")
    if pair.parent.self_hash(report, "certificate_sha256") != report.get(
        "certificate_sha256"
    ):
        raise AssertionError("eta6 Dini torsion report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("eta6 Dini torsion report hash is not reproducible")

    chain_table = np.asarray(tables["chain_table"], dtype=np.int64)
    step_table = np.asarray(tables["step_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if tuple(chain_table.shape) != (5, len(CHAIN_COLUMNS)):
        raise AssertionError("eta6 Dini torsion chain table shape mismatch")
    if tuple(step_table.shape) != (4, len(STEP_COLUMNS)):
        raise AssertionError("eta6 Dini torsion step table shape mismatch")
    if tuple(observable_table.shape) != (
        len(OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("eta6 Dini torsion observable table shape mismatch")

    chain_rows = table_rows(chain_table, CHAIN_COLUMNS)
    step_rows = table_rows(step_table, STEP_COLUMNS)
    observables = {
        row["observable_code"]: row["value"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }
    if [row["cut_conductance_x1e12"] for row in chain_rows] != [
        4_329_004_000,
        3_649_635_000,
        2_645_503_000,
        2_615_519_000,
        2_610_966_000,
    ]:
        raise AssertionError("eta6 Dini torsion conductance chain mismatch")
    if [row["eta6_holonomy_pairing"] for row in chain_rows] != [1, 1, 1, 1, 1]:
        raise AssertionError("eta6 Dini torsion holonomy chain mismatch")
    if any(row["support_changed_flag"] for row in chain_rows):
        raise AssertionError("eta6 Dini torsion support changed along chain")
    if any(row["old_cut_edge_still_cut_count"] != 6 for row in chain_rows):
        raise AssertionError("eta6 Dini torsion old cut edge count mismatch")
    if [row["conductance_drop_x1e12"] for row in step_rows] != [
        679_369_000,
        1_004_132_000,
        29_984_000,
        4_553_000,
    ]:
        raise AssertionError("eta6 Dini torsion step drops mismatch")
    if any(row["holonomy_delta"] for row in step_rows):
        raise AssertionError("eta6 Dini torsion holonomy delta mismatch")

    required_observables = {
        "chain_stage_count": 5,
        "transition_count": 4,
        "base_cut_conductance_x1e12": 4_329_004_000,
        "local_cut_conductance_x1e12": 3_649_635_000,
        "final_cut_conductance_x1e12": 2_610_966_000,
        "base_to_final_drop_x1e12": 1_718_038_000,
        "local_to_final_drop_x1e12": 1_038_669_000,
        "all_stage_holonomy_pairing_count": 5,
        "holonomy_delta_total": 0,
        "support_changed_total": 0,
        "old_cut_edge_min": 6,
        "strict_conductance_descent_flag": 1,
        "positive_final_conductance_flag": 1,
        "dini_total_torsion_base_x1e12": 429_509_500,
        "dini_total_torsion_local_x1e12": 346_223_000,
        "largest_step_drop_x1e12": 1_004_132_000,
        "largest_step_code": 12,
        "smallest_positive_step_drop_x1e12": 4_553_000,
        "nonlocal_tail_drop_after_2114_x1e12": 34_537_000,
        "poincare_height_available_for_all_stages_flag": 0,
        "h4_lift_certified_flag": 0,
    }
    for key, value in required_observables.items():
        if observables.get(OBSERVABLE_CODES[key]) != value:
            raise AssertionError(f"eta6 Dini torsion observable {key} mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("second_window_base_report", {}),
        BASE_REPORT,
        "second-window base report input",
    )
    assert_file_hash(
        inputs.get("conductance_preservation_report", {}),
        CONDUCTANCE_REPORT,
        "conductance-preservation report input",
    )
    assert_file_hash(
        inputs.get("conductance_preservation_tables", {}),
        CONDUCTANCE_TABLES,
        "conductance-preservation tables input",
    )
    assert_file_hash(
        inputs.get("eta6_holonomy_report", {}),
        HOLONOMY_REPORT,
        "eta6 holonomy report input",
    )
    assert_file_hash(
        inputs.get("eta6_holonomy_tables", {}),
        HOLONOMY_TABLES,
        "eta6 holonomy tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index_manifest@1"
    ):
        raise AssertionError("eta6 Dini torsion manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 Dini torsion manifest report hash mismatch")
    if pair.parent.self_hash(manifest, "manifest_sha256") != manifest.get(
        "manifest_sha256"
    ):
        raise AssertionError("eta6 Dini torsion manifest self hash mismatch")
    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("eta6 Dini torsion missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("eta6 Dini torsion index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("eta6 Dini torsion index status mismatch")
    index_without_hash = {
        key: value for key, value in index.items() if key != "registry_sha256"
    }
    if h_json(index_without_hash) != index.get("registry_sha256"):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": report.get("witness"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = (
        validate_c985_d20_signature_boundary_spine_aperture_closure_tail_eta6_dini_torsion_index()
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
