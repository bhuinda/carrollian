from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        MIXED_CONTACT_CANDIDATES,
        MIXED_CONTACT_CERTIFICATE,
        MIXED_CONTACT_EDGES,
        MIXED_CONTACT_JSON,
        MIXED_CONTACT_REPORT,
        MIXED_CONTACT_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANKING_CANDIDATES,
        RANKING_CERTIFICATE,
        RANKING_JSON,
        RANKING_REPORT,
        RANKING_TABLES,
        SELECTED_ATOM_WORD,
        SELECTED_SYMBOL_WORD,
        SELECTOR_CANDIDATE_COLUMNS,
        SELECTOR_STEP_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_REPORT,
        SYMBOLIC_REWRITE_TABLES,
        THEOREM_ID,
        X2_ATOM_ID,
        X5_ATOM_ID,
        ZERO_OVERHEAD_CANDIDATE_IDS,
        ZERO_OVERHEAD_WINDOW_NODES,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        MIXED_CONTACT_CANDIDATES,
        MIXED_CONTACT_CERTIFICATE,
        MIXED_CONTACT_EDGES,
        MIXED_CONTACT_JSON,
        MIXED_CONTACT_REPORT,
        MIXED_CONTACT_TABLES,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        RANKING_CANDIDATES,
        RANKING_CERTIFICATE,
        RANKING_JSON,
        RANKING_REPORT,
        RANKING_TABLES,
        SELECTED_ATOM_WORD,
        SELECTED_SYMBOL_WORD,
        SELECTOR_CANDIDATE_COLUMNS,
        SELECTOR_STEP_COLUMNS,
        STATUS,
        SYMBOLIC_ALPHABET,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_REPORT,
        SYMBOLIC_REWRITE_TABLES,
        THEOREM_ID,
        X2_ATOM_ID,
        X5_ATOM_ID,
        ZERO_OVERHEAD_CANDIDATE_IDS,
        ZERO_OVERHEAD_WINDOW_NODES,
        build_payloads,
        self_hash,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH


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


def validate_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    selector = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_atom_selector_refinement.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_atom_selector_refinement_certificate.json"
    )
    steps_csv = (OUT_DIR / "aperture_atom_selector_steps.csv").read_text(
        encoding="utf-8"
    )
    candidates_csv = (OUT_DIR / "aperture_atom_selector_candidates.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (OUT_DIR / "aperture_atom_selector_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_atom_selector_refinement_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if selector != expected["signature_boundary_spine_aperture_atom_selector_refinement"]:
        raise AssertionError("aperture atom selector JSON is not reproducible")
    if steps_csv != expected["aperture_atom_selector_steps_csv"]:
        raise AssertionError("aperture atom selector step CSV is not reproducible")
    if candidates_csv != expected["aperture_atom_selector_candidates_csv"]:
        raise AssertionError("aperture atom selector candidate CSV is not reproducible")
    if observables_csv != expected["aperture_atom_selector_observables_csv"]:
        raise AssertionError("aperture atom selector observable CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_atom_selector_refinement_certificate"
        ]
    ):
        raise AssertionError("aperture atom selector certificate is not reproducible")

    for name in ["selector_step_table", "selector_candidate_table", "observable_table"]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"aperture atom selector table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selector_refinement@1":
        raise AssertionError("C985 d20 aperture atom selector report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 aperture atom selector is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 aperture atom selector all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 aperture atom selector checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture atom selector report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 aperture atom selector report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 aperture atom selector missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("selector_candidate_ids") != ZERO_OVERHEAD_CANDIDATE_IDS:
        raise AssertionError("aperture atom selector candidate IDs mismatch")
    if witness.get("selected_atom_word") != SELECTED_ATOM_WORD:
        raise AssertionError("aperture atom selector atom word mismatch")
    if witness.get("selected_symbol_word") != SELECTED_SYMBOL_WORD:
        raise AssertionError("aperture atom selector symbol word mismatch")
    if witness.get("cycle_window_nodes") != ZERO_OVERHEAD_WINDOW_NODES:
        raise AssertionError("aperture atom selector cycle-window nodes mismatch")
    first_reading = witness.get("first_contact_reading", {})
    if first_reading.get("selected_atom_id") != X2_ATOM_ID:
        raise AssertionError("aperture atom selector first selected atom mismatch")
    if first_reading.get("unselected_cowitness_atom_id") != X5_ATOM_ID:
        raise AssertionError("aperture atom selector first x5 cowitness mismatch")
    if first_reading.get("selected_x5_leakage_count") != 0:
        raise AssertionError("aperture atom selector selected x5 leakage mismatch")
    if first_reading.get("forgetful_projection_remains_mixed") is not True:
        raise AssertionError("aperture atom selector forgetful projection mismatch")
    if witness.get("geodesic_metrics") != {
        "metric_gromov_delta": 0.0,
        "signature_valley_depth": 0,
        "trace_detour_overhead": 0,
        "trace_signature_total_variation": 53,
    }:
        raise AssertionError("aperture atom selector geodesic metrics mismatch")

    step_table = np.asarray(tables["selector_step_table"], dtype=np.int64)
    candidate_table = np.asarray(tables["selector_candidate_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if step_table.shape != (24, len(SELECTOR_STEP_COLUMNS)):
        raise AssertionError("aperture atom selector step table shape mismatch")
    if candidate_table.shape != (6, len(SELECTOR_CANDIDATE_COLUMNS)):
        raise AssertionError("aperture atom selector candidate table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("aperture atom selector observable table shape mismatch")

    selected_atom_columns = [
        SELECTOR_CANDIDATE_COLUMNS.index(f"selected_atom_{index}_id")
        for index in range(4)
    ]
    selected_symbol_columns = [
        SELECTOR_CANDIDATE_COLUMNS.index(f"selected_symbol_{index}_id")
        for index in range(4)
    ]
    if candidate_table[:, selected_atom_columns].tolist() != [
        SELECTED_ATOM_WORD
    ] * 6:
        raise AssertionError("aperture atom selector selected atom table mismatch")
    if candidate_table[:, selected_symbol_columns].tolist() != [
        SELECTED_SYMBOL_WORD
    ] * 6:
        raise AssertionError("aperture atom selector selected symbol table mismatch")
    if candidate_table[:, SELECTOR_CANDIDATE_COLUMNS.index("first_contact_selected_x5_leakage_flag")].tolist() != [0] * 6:
        raise AssertionError("aperture atom selector first x5 leakage vector mismatch")
    if candidate_table[:, SELECTOR_CANDIDATE_COLUMNS.index("first_contact_x5_cowitness_flag")].tolist() != [1] * 6:
        raise AssertionError("aperture atom selector first x5 cowitness vector mismatch")
    if candidate_table[:, SELECTOR_CANDIDATE_COLUMNS.index("geodesic_trace_preserved_flag")].tolist() != [1] * 6:
        raise AssertionError("aperture atom selector geodesic preservation vector mismatch")
    if candidate_table[:, SELECTOR_CANDIDATE_COLUMNS.index("forgetful_projection_mixed_flag")].tolist() != [1] * 6:
        raise AssertionError("aperture atom selector forgetful projection vector mismatch")

    step_atom_index = SELECTOR_STEP_COLUMNS.index("selected_atom_id")
    step_symbol_index = SELECTOR_STEP_COLUMNS.index("selected_symbol_id")
    selected_step_atoms = [
        step_table[row_start : row_start + 4, step_atom_index].tolist()
        for row_start in range(0, 24, 4)
    ]
    selected_step_symbols = [
        step_table[row_start : row_start + 4, step_symbol_index].tolist()
        for row_start in range(0, 24, 4)
    ]
    if selected_step_atoms != [SELECTED_ATOM_WORD] * 6:
        raise AssertionError("aperture atom selector step atom word mismatch")
    if selected_step_symbols != [SELECTED_SYMBOL_WORD] * 6:
        raise AssertionError("aperture atom selector step symbol word mismatch")
    if int(
        np.sum(
            step_table[
                :,
                SELECTOR_STEP_COLUMNS.index("selected_x5_first_contact_leakage_flag"),
            ]
        )
    ) != 0:
        raise AssertionError("aperture atom selector step x5 leakage sum mismatch")
    if int(
        np.sum(
            step_table[
                :,
                SELECTOR_STEP_COLUMNS.index("unselected_x5_first_contact_cowitness_flag"),
            ]
        )
    ) != 6:
        raise AssertionError("aperture atom selector unselected x5 cowitness sum mismatch")
    if int(
        np.sum(
            step_table[:, SELECTOR_STEP_COLUMNS.index("intended_x5_second_step_flag")]
        )
    ) != 6:
        raise AssertionError("aperture atom selector intended x5 sum mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("mixed_contact_report", {}), MIXED_CONTACT_REPORT, "mixed contact report input")
    assert_file_hash(inputs.get("mixed_contact_json", {}), MIXED_CONTACT_JSON, "mixed contact JSON input")
    assert_file_hash(inputs.get("mixed_contact_candidates", {}), MIXED_CONTACT_CANDIDATES, "mixed contact candidates input")
    assert_file_hash(inputs.get("mixed_contact_edges", {}), MIXED_CONTACT_EDGES, "mixed contact edges input")
    assert_file_hash(inputs.get("mixed_contact_tables", {}), MIXED_CONTACT_TABLES, "mixed contact tables input")
    assert_file_hash(inputs.get("mixed_contact_certificate", {}), MIXED_CONTACT_CERTIFICATE, "mixed contact certificate input")
    assert_file_hash(inputs.get("ranking_report", {}), RANKING_REPORT, "ranking report input")
    assert_file_hash(inputs.get("ranking_json", {}), RANKING_JSON, "ranking JSON input")
    assert_file_hash(inputs.get("ranking_candidates", {}), RANKING_CANDIDATES, "ranking candidates input")
    assert_file_hash(inputs.get("ranking_tables", {}), RANKING_TABLES, "ranking tables input")
    assert_file_hash(inputs.get("ranking_certificate", {}), RANKING_CERTIFICATE, "ranking certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("symbolic_rewrite_report", {}), SYMBOLIC_REWRITE_REPORT, "symbolic rewrite report input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET, "symbolic alphabet input")
    assert_file_hash(inputs.get("symbolic_rewrite_tables", {}), SYMBOLIC_REWRITE_TABLES, "symbolic rewrite tables input")
    assert_file_hash(inputs.get("symbolic_rewrite_certificate", {}), SYMBOLIC_REWRITE_CERTIFICATE, "symbolic rewrite certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selector_refinement_manifest@1":
        raise AssertionError("C985 d20 aperture atom selector manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture atom selector manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 aperture atom selector manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 aperture atom selector missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture atom selector index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 aperture atom selector index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_atom_selector_refinement@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "selector_candidate_ids": witness.get("selector_candidate_ids"),
        "selected_atom_word": witness.get("selected_atom_word"),
        "selected_symbol_word": witness.get("selected_symbol_word"),
        "first_contact_reading": witness.get("first_contact_reading"),
        "geodesic_metrics": witness.get("geodesic_metrics"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
