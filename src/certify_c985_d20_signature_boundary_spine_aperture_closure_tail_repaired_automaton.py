from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        AUTOMATON_OBSERVABLE_CODES,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NATIVE_CLASS_COLUMNS,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        POINCARE_COLUMNS,
        RECURRENT_CLASS_COLUMNS,
        SKIP_WINDOW_CERTIFICATE,
        SKIP_WINDOW_CELLS,
        SKIP_WINDOW_COMPONENTS,
        SKIP_WINDOW_REPORT,
        SKIP_WINDOW_TABLES,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton import (
        AUTOMATON_OBSERVABLE_CODES,
        DERIVE_SCRIPT,
        INDEX_PATH,
        NATIVE_CLASS_COLUMNS,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        POINCARE_COLUMNS,
        RECURRENT_CLASS_COLUMNS,
        SKIP_WINDOW_CERTIFICATE,
        SKIP_WINDOW_CELLS,
        SKIP_WINDOW_COMPONENTS,
        SKIP_WINDOW_REPORT,
        SKIP_WINDOW_TABLES,
        SPECTRAL_CUT_COLUMNS,
        STATE_COLUMNS,
        STATUS,
        THEOREM_ID,
        TRANSITION_COLUMNS,
        VALIDATOR_SCRIPT,
        build_payloads,
        self_hash,
    )


EXPECTED_REPAIRED_CLASS_SIZES = [
    787,
    15,
    11,
    6,
    4,
    2,
    2,
    2,
    2,
    2,
    2,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
]
EXPECTED_NATIVE_CLASS_SIZES = [347, 185, 15, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1]


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


def validate_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    automaton = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_repaired_automaton.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate.json"
    )
    states_csv = (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_states.csv"
    ).read_text(encoding="utf-8")
    transitions_csv = (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_transitions.csv"
    ).read_text(encoding="utf-8")
    recurrent_classes_csv = (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_recurrent_classes.csv"
    ).read_text(encoding="utf-8")
    native_classes_csv = (
        OUT_DIR
        / "aperture_closure_tail_repaired_automaton_native_recurrent_classes.csv"
    ).read_text(encoding="utf-8")
    spectral_cut_csv = (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_spectral_cut.csv"
    ).read_text(encoding="utf-8")
    poincare_csv = (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_poincare.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_closure_tail_repaired_automaton_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_repaired_automaton_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        automaton
        != expected[
            "signature_boundary_spine_aperture_closure_tail_repaired_automaton"
        ]
    ):
        raise AssertionError("repaired automaton JSON is not reproducible")
    if states_csv != expected["repaired_automaton_states_csv"]:
        raise AssertionError("repaired automaton states CSV is not reproducible")
    if transitions_csv != expected["repaired_automaton_transitions_csv"]:
        raise AssertionError("repaired automaton transitions CSV is not reproducible")
    if recurrent_classes_csv != expected["repaired_automaton_recurrent_classes_csv"]:
        raise AssertionError("repaired recurrent classes CSV is not reproducible")
    if (
        native_classes_csv
        != expected["repaired_automaton_native_recurrent_classes_csv"]
    ):
        raise AssertionError("native recurrent classes CSV is not reproducible")
    if spectral_cut_csv != expected["repaired_automaton_spectral_cut_csv"]:
        raise AssertionError("repaired automaton spectral cut CSV is not reproducible")
    if poincare_csv != expected["repaired_automaton_poincare_csv"]:
        raise AssertionError("repaired automaton Poincare CSV is not reproducible")
    if observables_csv != expected["repaired_automaton_observables_csv"]:
        raise AssertionError("repaired automaton observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_closure_tail_repaired_automaton_certificate"
        ]
    ):
        raise AssertionError("repaired automaton certificate is not reproducible")

    for name in [
        "state_table",
        "transition_table",
        "recurrent_class_table",
        "native_recurrent_class_table",
        "spectral_cut_table",
        "poincare_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"repaired automaton table {name} is not reproducible")

    if (
        report.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton@1"
    ):
        raise AssertionError("repaired automaton report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("repaired automaton layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("repaired automaton all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("repaired automaton checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("repaired automaton report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("repaired automaton report is not reproducible")

    state_table = np.asarray(tables["state_table"], dtype=np.int64)
    transition_table = np.asarray(tables["transition_table"], dtype=np.int64)
    recurrent_class_table = np.asarray(tables["recurrent_class_table"], dtype=np.int64)
    native_class_table = np.asarray(
        tables["native_recurrent_class_table"],
        dtype=np.int64,
    )
    spectral_cut_table = np.asarray(tables["spectral_cut_table"], dtype=np.int64)
    poincare_table = np.asarray(tables["poincare_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if state_table.shape != (846, len(STATE_COLUMNS)):
        raise AssertionError("repaired automaton state table shape mismatch")
    if transition_table.shape != (5_098, len(TRANSITION_COLUMNS)):
        raise AssertionError("repaired automaton transition table shape mismatch")
    if recurrent_class_table.shape != (22, len(RECURRENT_CLASS_COLUMNS)):
        raise AssertionError("repaired recurrent class table shape mismatch")
    if native_class_table.shape != (13, len(NATIVE_CLASS_COLUMNS)):
        raise AssertionError("native recurrent class table shape mismatch")
    if spectral_cut_table.shape != (1, len(SPECTRAL_CUT_COLUMNS)):
        raise AssertionError("repaired spectral cut table shape mismatch")
    if poincare_table.shape != (787, len(POINCARE_COLUMNS)):
        raise AssertionError("repaired Poincare table shape mismatch")
    if observable_table.shape != (
        len(AUTOMATON_OBSERVABLE_CODES),
        len(OBSERVABLE_COLUMNS),
    ):
        raise AssertionError("repaired observable table shape mismatch")

    state_rows = table_rows(state_table, STATE_COLUMNS)
    transition_rows = table_rows(transition_table, TRANSITION_COLUMNS)
    recurrent_rows = table_rows(recurrent_class_table, RECURRENT_CLASS_COLUMNS)
    native_rows = table_rows(native_class_table, NATIVE_CLASS_COLUMNS)
    spectral = table_rows(spectral_cut_table, SPECTRAL_CUT_COLUMNS)[0]
    observables = {
        row["observable_code"]: row["value_x1e12"]
        for row in table_rows(observable_table, OBSERVABLE_COLUMNS)
    }

    if [row["state_count"] for row in recurrent_rows] != EXPECTED_REPAIRED_CLASS_SIZES:
        raise AssertionError("repaired recurrent class sizes mismatch")
    if [row["state_count"] for row in native_rows] != EXPECTED_NATIVE_CLASS_SIZES:
        raise AssertionError("native recurrent class sizes mismatch")
    if sum(row["derived_only_flag"] for row in state_rows) != 284:
        raise AssertionError("derived-only state count mismatch")
    if sum(row["native_repair_flag"] for row in state_rows) != 562:
        raise AssertionError("native state count mismatch")
    if sum(row["boundary_path_edge_flag"] for row in transition_rows) != 4:
        raise AssertionError("directed boundary-path transition count mismatch")
    if sum(row["spectral_cut_edge_flag"] for row in transition_rows) != 12:
        raise AssertionError("directed spectral-cut transition count mismatch")
    if (
        spectral["cut_edge_count"],
        spectral["derived_cut_edge_count"],
        spectral["positive_state_count"],
        spectral["negative_state_count"],
        spectral["left_side_code"],
        spectral["gate_side_code"],
        spectral["right_side_code"],
    ) != (6, 6, 593, 194, 1, 1, 1):
        raise AssertionError("spectral cut witness mismatch")
    if spectral["lambda_2_x1e12"] <= 0:
        raise AssertionError("spectral lambda_2 is not positive")
    if spectral["lambda_3_x1e12"] <= spectral["lambda_2_x1e12"]:
        raise AssertionError("spectral lambda_3 does not exceed lambda_2")

    required_observables = {
        "state_count": 846,
        "undirected_edge_count": 2_549,
        "directed_transition_count": 5_098,
        "native_state_count": 562,
        "derived_only_state_count": 284,
        "native_recurrent_class_count": 13,
        "repaired_recurrent_class_count": 22,
        "merged_recurrent_class_size": 787,
        "native_transition_edge_count": 1_694,
        "derived_transition_edge_count": 855,
        "derived_only_transition_edge_count": 766,
        "boundary_path_edge_count": 2,
        "left_right_same_native_recurrent_class": 0,
        "left_right_same_repaired_recurrent_class": 1,
        "gate_in_merged_recurrent_class": 1,
        "spectral_cut_edge_count": 6,
        "spectral_cut_derived_edge_count": 6,
        "spectral_positive_state_count": 593,
        "spectral_negative_state_count": 194,
        "poincare_point_count": 787,
    }
    for key, value in required_observables.items():
        code = AUTOMATON_OBSERVABLE_CODES[key]
        if observables.get(code) != value * 10**12:
            raise AssertionError(f"observable {key} mismatch")

    witness = report.get("witness", {})
    if witness.get("native_recurrent_class_sizes") != EXPECTED_NATIVE_CLASS_SIZES:
        raise AssertionError("native class witness mismatch")
    if witness.get("repaired_recurrent_class_sizes") != EXPECTED_REPAIRED_CLASS_SIZES:
        raise AssertionError("repaired class witness mismatch")
    if witness.get("spectral_cut", {}).get("derived_cut_edge_count") != 6:
        raise AssertionError("spectral witness mismatch")
    if witness.get("poincare_geometry", {}).get("point_count") != 787:
        raise AssertionError("Poincare witness mismatch")
    if certificate.get("status") != STATUS:
        raise AssertionError("repaired automaton certificate status mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("skip_window_report", {}),
        SKIP_WINDOW_REPORT,
        "skip-window report input",
    )
    assert_file_hash(
        inputs.get("skip_window_certificate", {}),
        SKIP_WINDOW_CERTIFICATE,
        "skip-window certificate input",
    )
    assert_file_hash(
        inputs.get("skip_window_cells", {}),
        SKIP_WINDOW_CELLS,
        "skip-window cells input",
    )
    assert_file_hash(
        inputs.get("skip_window_components", {}),
        SKIP_WINDOW_COMPONENTS,
        "skip-window components input",
    )
    assert_file_hash(
        inputs.get("skip_window_tables", {}),
        SKIP_WINDOW_TABLES,
        "skip-window tables input",
    )
    assert_file_hash(inputs.get("derive_script", {}), DERIVE_SCRIPT, "derive script input")
    assert_file_hash(inputs.get("validator", {}), VALIDATOR_SCRIPT, "validator input")

    if (
        manifest.get("schema")
        != "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton_manifest@1"
    ):
        raise AssertionError("repaired automaton manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("repaired automaton manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("repaired automaton manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("repaired automaton missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("repaired automaton index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("repaired automaton index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "witness": witness,
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_closure_tail_repaired_automaton()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
