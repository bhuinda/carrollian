from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_corridor_insertion import (
        APERTURE_FAN_CERTIFICATE,
        APERTURE_FAN_JSON,
        APERTURE_FAN_PATHS,
        APERTURE_FAN_REPORT,
        APERTURE_FAN_TABLES,
        CANDIDATE_COLUMNS,
        GATE_AUTOMATON_CERTIFICATE,
        GATE_AUTOMATON_JSON,
        GATE_AUTOMATON_REPORT,
        GATE_AUTOMATON_TABLES,
        GATE_AUTOMATON_TRANSITIONS,
        GATE_AUTOMATON_TRIGRAMS,
        INSERTED_WINDOW_COLUMNS,
        INSERTION_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SELECTED_SEQUENCE_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_corridor_insertion import (
        APERTURE_FAN_CERTIFICATE,
        APERTURE_FAN_JSON,
        APERTURE_FAN_PATHS,
        APERTURE_FAN_REPORT,
        APERTURE_FAN_TABLES,
        CANDIDATE_COLUMNS,
        GATE_AUTOMATON_CERTIFICATE,
        GATE_AUTOMATON_JSON,
        GATE_AUTOMATON_REPORT,
        GATE_AUTOMATON_TABLES,
        GATE_AUTOMATON_TRANSITIONS,
        GATE_AUTOMATON_TRIGRAMS,
        INSERTED_WINDOW_COLUMNS,
        INSERTION_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SELECTED_SEQUENCE_COLUMNS,
        STATUS,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGES,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
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


def validate_c985_d20_signature_boundary_spine_aperture_corridor_insertion() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    insertion = load_json(
        OUT_DIR / "signature_boundary_spine_aperture_corridor_insertion.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_corridor_insertion_certificate.json"
    )
    candidates_csv = (OUT_DIR / "aperture_corridor_insertion_candidates.csv").read_text(
        encoding="utf-8"
    )
    windows_csv = (OUT_DIR / "aperture_corridor_inserted_windows.csv").read_text(
        encoding="utf-8"
    )
    sequence_csv = (OUT_DIR / "aperture_corridor_selected_sequence.csv").read_text(
        encoding="utf-8"
    )
    observables_csv = (
        OUT_DIR / "aperture_corridor_insertion_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_aperture_corridor_insertion_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if insertion != expected["signature_boundary_spine_aperture_corridor_insertion"]:
        raise AssertionError("aperture corridor insertion JSON is not reproducible")
    if candidates_csv != expected["aperture_corridor_insertion_candidates_csv"]:
        raise AssertionError("aperture corridor insertion candidate CSV is not reproducible")
    if windows_csv != expected["aperture_corridor_inserted_windows_csv"]:
        raise AssertionError("aperture corridor inserted window CSV is not reproducible")
    if sequence_csv != expected["aperture_corridor_selected_sequence_csv"]:
        raise AssertionError("aperture corridor selected sequence CSV is not reproducible")
    if observables_csv != expected["aperture_corridor_insertion_observables_csv"]:
        raise AssertionError("aperture corridor insertion observable CSV is not reproducible")
    if certificate != expected[
        "signature_boundary_spine_aperture_corridor_insertion_certificate"
    ]:
        raise AssertionError("aperture corridor insertion certificate is not reproducible")

    table_names = [
        "candidate_table",
        "inserted_window_table",
        "selected_sequence_table",
        "observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"aperture corridor insertion table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_corridor_insertion@1":
        raise AssertionError("C985 d20 aperture corridor insertion report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 aperture corridor insertion is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 aperture corridor insertion all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 aperture corridor insertion checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture corridor insertion report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 aperture corridor insertion report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "aperture_fan_report_certified",
        "aperture_fan_certificate_certified",
        "gate_automaton_report_certified",
        "gate_automaton_certificate_certified",
        "typed_corridor_report_certified",
        "typed_corridor_certificate_certified",
        "symbolic_associativity_report_certified",
        "symbolic_associativity_certificate_certified",
        "aperture_fan_schema_available",
        "gate_automaton_schema_available",
        "gate_transition_table_shape_is_16_by_16",
        "gate_trigram_table_shape_is_12_by_20",
        "typed_corridor_table_shape_is_16_by_23",
        "symbolic_associativity_table_shape_is_216_by_27",
        "aperture_geodesic_path_table_shape_is_6_by_17",
        "strict_aperture_path_is_48_42_44",
        "source_to_branch_sequence_matches_gate_report",
        "source_to_branch_sequence_omits_x2",
        "zero_edit_cannot_introduce_x2",
        "candidate_count_is_15",
        "feasible_strict_candidate_count_is_8",
        "boundary_anchored_feasible_candidate_count_is_4",
        "selected_insertion_position_is_14",
        "selected_edit_preserves_typed_contact_subsequence",
        "selected_edit_preserves_all_six_branch_words",
        "selected_edit_preserves_all_twelve_original_windows",
        "selected_edit_has_one_inserted_window",
        "selected_edit_creates_one_strict_42_window",
        "selected_inserted_window_is_5_3_2",
        "selected_inserted_window_canonical_is_42",
        "selected_inserted_window_full_sector_signature_183",
        "selected_window_overlaps_boundary_window_by_two_contacts",
        "selected_edit_is_unique_branch_and_window_preserving_feasible_candidate",
        "selected_sequence_length_is_15",
        "selected_sequence_suffix_is_5_3_2",
        "selected_sequence_still_omits_x4",
        "candidate_table_shape_is_15_by_15",
        "inserted_window_table_shape_is_39_by_14",
        "selected_sequence_table_shape_is_15_by_6",
        "observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 aperture corridor insertion missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("strict_aperture_path") != [48, 42, 44]:
        raise AssertionError("aperture corridor insertion strict path mismatch")
    if witness.get("original_source_to_branch_sequence") != [
        5,
        5,
        0,
        0,
        1,
        3,
        1,
        5,
        3,
        5,
        5,
        3,
        5,
        3,
    ]:
        raise AssertionError("aperture corridor insertion source sequence mismatch")
    if witness.get("feasible_strict_candidate_ids") != [7, 8, 9, 10, 11, 12, 13, 14]:
        raise AssertionError("aperture corridor insertion feasible candidate ids mismatch")
    if witness.get("boundary_anchored_feasible_candidate_ids") != [11, 12, 13, 14]:
        raise AssertionError("aperture corridor insertion anchored candidate ids mismatch")
    if witness.get("selected_candidate_id") != 14:
        raise AssertionError("aperture corridor insertion selected candidate mismatch")
    if witness.get("selected_edited_sequence") != [
        5,
        5,
        0,
        0,
        1,
        3,
        1,
        5,
        3,
        5,
        5,
        3,
        5,
        3,
        2,
    ]:
        raise AssertionError("aperture corridor insertion edited sequence mismatch")
    if witness.get("selected_new_window") != {
        "boundary_window_overlap_count": 2,
        "canonical_triple_id": 42,
        "contact_ids": [13, 14, 0],
        "edited_window_id": 13,
        "ordered_symbols": [5, 3, 2],
        "sector_coverage_count": 6,
        "signature_union_count": 183,
    }:
        raise AssertionError("aperture corridor insertion selected window mismatch")
    if witness.get("selected_preservation", {}).get("accepting_branch_word_preserved_count") != 6:
        raise AssertionError("aperture corridor insertion branch preservation mismatch")
    if witness.get("selected_preservation", {}).get("original_trigram_window_preserved_count") != 12:
        raise AssertionError("aperture corridor insertion window preservation mismatch")
    if witness.get("selected_preservation", {}).get("missing_symbol_bitset_after_insert") != 16:
        raise AssertionError("aperture corridor insertion missing symbol bitset mismatch")

    candidate_table = np.asarray(tables["candidate_table"], dtype=np.int64)
    inserted_window_table = np.asarray(tables["inserted_window_table"], dtype=np.int64)
    selected_sequence_table = np.asarray(tables["selected_sequence_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)

    if candidate_table.shape != (15, len(CANDIDATE_COLUMNS)):
        raise AssertionError("aperture corridor insertion candidate table shape mismatch")
    if inserted_window_table.shape != (39, len(INSERTED_WINDOW_COLUMNS)):
        raise AssertionError("aperture corridor inserted window table shape mismatch")
    if selected_sequence_table.shape != (15, len(SELECTED_SEQUENCE_COLUMNS)):
        raise AssertionError("aperture corridor selected sequence table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(INSERTION_OBSERVABLE_COLUMNS)):
        raise AssertionError("aperture corridor observable table shape mismatch")
    if candidate_table[:, 14].tolist().count(1) != 1:
        raise AssertionError("aperture corridor selected candidate flag count mismatch")
    if candidate_table[14].tolist() != [14, 14, 2, 14, -1, 1, 6, 12, 1, 1, 1, 1, 183, 2, 1]:
        raise AssertionError("aperture corridor selected candidate row mismatch")
    if selected_sequence_table[:, 2].tolist() != [
        5,
        5,
        0,
        0,
        1,
        3,
        1,
        5,
        3,
        5,
        5,
        3,
        5,
        3,
        2,
    ]:
        raise AssertionError("aperture corridor selected sequence symbols mismatch")
    if selected_sequence_table[:, 3].tolist().count(1) != 1:
        raise AssertionError("aperture corridor inserted contact flag mismatch")
    if inserted_window_table[38].tolist() != [14, 13, 5, 3, 2, 13, 14, 0, 42, 6, 1, 183, 1, 2]:
        raise AssertionError("aperture corridor selected inserted window table mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("aperture_fan_report", {}), APERTURE_FAN_REPORT, "aperture fan report input")
    assert_file_hash(inputs.get("aperture_fan", {}), APERTURE_FAN_JSON, "aperture fan JSON input")
    assert_file_hash(inputs.get("aperture_fan_paths", {}), APERTURE_FAN_PATHS, "aperture fan path input")
    assert_file_hash(inputs.get("aperture_fan_tables", {}), APERTURE_FAN_TABLES, "aperture fan table input")
    assert_file_hash(inputs.get("aperture_fan_certificate", {}), APERTURE_FAN_CERTIFICATE, "aperture fan certificate input")
    assert_file_hash(inputs.get("gate_automaton_report", {}), GATE_AUTOMATON_REPORT, "gate automaton report input")
    assert_file_hash(inputs.get("gate_automaton", {}), GATE_AUTOMATON_JSON, "gate automaton JSON input")
    assert_file_hash(inputs.get("gate_automaton_transitions", {}), GATE_AUTOMATON_TRANSITIONS, "gate automaton transition input")
    assert_file_hash(inputs.get("gate_automaton_trigrams", {}), GATE_AUTOMATON_TRIGRAMS, "gate automaton trigram input")
    assert_file_hash(inputs.get("gate_automaton_tables", {}), GATE_AUTOMATON_TABLES, "gate automaton table input")
    assert_file_hash(inputs.get("gate_automaton_certificate", {}), GATE_AUTOMATON_CERTIFICATE, "gate automaton certificate input")
    assert_file_hash(inputs.get("typed_corridor_report", {}), TYPED_CORRIDOR_REPORT, "typed corridor report input")
    assert_file_hash(inputs.get("typed_corridor_edges", {}), TYPED_CORRIDOR_EDGES, "typed corridor edge input")
    assert_file_hash(inputs.get("typed_corridor_tables", {}), TYPED_CORRIDOR_TABLES, "typed corridor table input")
    assert_file_hash(inputs.get("typed_corridor_certificate", {}), TYPED_CORRIDOR_CERTIFICATE, "typed corridor certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity table input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_corridor_insertion_manifest@1":
        raise AssertionError("C985 d20 aperture corridor insertion manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture corridor insertion manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 aperture corridor insertion manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 aperture corridor insertion missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 aperture corridor insertion index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 aperture corridor insertion index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_corridor_insertion@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "selected_candidate_id": witness.get("selected_candidate_id"),
        "selected_new_window": witness.get("selected_new_window"),
        "selected_preservation": witness.get("selected_preservation"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_corridor_insertion()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
