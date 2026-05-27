from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_gate_automaton import (
        AUTOMATON_TRANSITION_COLUMNS,
        BRANCH_WORD_COLUMNS,
        GATE_AUTOMATON_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_JSON,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRIGRAM_WINDOW_COLUMNS,
        TYPED_CORRIDOR_BRANCH_CSV,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGE_CSV,
        TYPED_CORRIDOR_JSON,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        STATUS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_gate_automaton import (
        AUTOMATON_TRANSITION_COLUMNS,
        BRANCH_WORD_COLUMNS,
        GATE_AUTOMATON_OBSERVABLE_COLUMNS,
        OBSERVABLE_CODES,
        OUT_DIR,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_JSON,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        THEOREM_ID,
        TRIGRAM_WINDOW_COLUMNS,
        TYPED_CORRIDOR_BRANCH_CSV,
        TYPED_CORRIDOR_CERTIFICATE,
        TYPED_CORRIDOR_EDGE_CSV,
        TYPED_CORRIDOR_JSON,
        TYPED_CORRIDOR_REPORT,
        TYPED_CORRIDOR_TABLES,
        STATUS,
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


def validate_c985_d20_signature_boundary_spine_gate_automaton() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    automaton = load_json(OUT_DIR / "signature_boundary_spine_gate_automaton.json")
    certificate = load_json(
        OUT_DIR / "signature_boundary_spine_gate_automaton_certificate.json"
    )
    transition_csv = (OUT_DIR / "gate_automaton_transitions.csv").read_text(
        encoding="utf-8"
    )
    branch_word_csv = (OUT_DIR / "gate_branch_words.csv").read_text(
        encoding="utf-8"
    )
    trigram_csv = (OUT_DIR / "gate_trigram_windows.csv").read_text(
        encoding="utf-8"
    )
    observable_csv = (OUT_DIR / "gate_automaton_observables.csv").read_text(
        encoding="utf-8"
    )
    tables = np.load(
        OUT_DIR / "signature_boundary_spine_gate_automaton_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if automaton != expected["signature_boundary_spine_gate_automaton"]:
        raise AssertionError("boundary spine gate automaton JSON is not reproducible")
    if transition_csv != expected["gate_automaton_transitions_csv"]:
        raise AssertionError("gate automaton transition CSV is not reproducible")
    if branch_word_csv != expected["gate_branch_words_csv"]:
        raise AssertionError("gate branch word CSV is not reproducible")
    if trigram_csv != expected["gate_trigram_windows_csv"]:
        raise AssertionError("gate trigram CSV is not reproducible")
    if observable_csv != expected["gate_automaton_observables_csv"]:
        raise AssertionError("gate automaton observable CSV is not reproducible")
    if certificate != expected["signature_boundary_spine_gate_automaton_certificate"]:
        raise AssertionError("gate automaton certificate is not reproducible")

    table_names = [
        "gate_automaton_transition_table",
        "gate_branch_word_table",
        "gate_trigram_window_table",
        "gate_automaton_observable_table",
    ]
    for name in table_names:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"gate automaton table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_gate_automaton@1":
        raise AssertionError("C985 d20 boundary spine gate automaton report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 boundary spine gate automaton is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 boundary spine gate automaton all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 boundary spine gate automaton checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine gate automaton report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 boundary spine gate automaton report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "typed_corridor_report_certified",
        "symbolic_associativity_report_certified",
        "typed_corridor_schema_available",
        "symbolic_associativity_schema_available",
        "typed_corridor_tables_available",
        "symbolic_associativity_tables_available",
        "gate_sequence_matches_typed_corridors",
        "accepting_states_match_branch_prefixes",
        "transition_count_is_16",
        "source_to_branch_prefix_is_14",
        "post_branch_tail_count_is_2",
        "branch_word_lengths_match_expected",
        "source_to_branch_windows_match_expected",
        "all_source_to_branch_trigrams_are_associativity_certified",
        "source_to_branch_unique_trigram_count_is_11",
        "source_to_branch_canonical_triples_match_expected",
        "source_to_branch_sector_coverage_histogram_matches_expected",
        "source_to_branch_signature_range_matches_expected",
        "observed_max_below_global_associativity_max",
        "full_sector_windows_use_canonical_triple_32",
        "source_to_branch_gate_symbols_omit_x2_x4",
        "transition_table_shape_is_16_by_16",
        "branch_word_table_shape_is_6_by_14",
        "trigram_table_shape_is_12_by_20",
        "observable_table_shape_matches_codebook",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 boundary spine gate automaton missing true checks: {missing}")

    witness = report.get("witness", {})
    expected_gate_sequence = [5, 5, 0, 0, 1, 3, 1, 5, 3, 5, 5, 3, 5, 3, 1, 0]
    expected_windows = [
        [5, 5, 0],
        [5, 0, 0],
        [0, 0, 1],
        [0, 1, 3],
        [1, 3, 1],
        [3, 1, 5],
        [1, 5, 3],
        [5, 3, 5],
        [3, 5, 5],
        [5, 5, 3],
        [5, 3, 5],
        [3, 5, 3],
    ]
    if witness.get("gate_symbol_sequence") != expected_gate_sequence:
        raise AssertionError("gate automaton sequence mismatch")
    if witness.get("accepting_state_ids") != [1, 3, 5, 8, 12, 14]:
        raise AssertionError("gate automaton accepting states mismatch")
    if witness.get("source_to_branch_trigram_windows") != expected_windows:
        raise AssertionError("gate automaton trigram windows mismatch")
    if witness.get("source_to_branch_unique_trigram_count") != 11:
        raise AssertionError("gate automaton unique trigram count mismatch")
    if witness.get("source_to_branch_canonical_triple_ids") != [1, 5, 8, 20, 23, 32, 48, 51]:
        raise AssertionError("gate automaton canonical triple ids mismatch")
    if witness.get("source_to_branch_sector_coverage_histogram") != [
        {"value": 3, "count": 0},
        {"value": 4, "count": 1},
        {"value": 5, "count": 9},
        {"value": 6, "count": 2},
    ]:
        raise AssertionError("gate automaton sector histogram mismatch")
    if witness.get("full_sector_trigram_windows") != [[3, 1, 5], [1, 5, 3]]:
        raise AssertionError("gate automaton full-sector windows mismatch")
    if witness.get("source_to_branch_signature_union_range") != {
        "min": 90,
        "max": 175,
        "global_symbolic_associativity_max": 185,
        "gap_to_global_max": 10,
    }:
        raise AssertionError("gate automaton signature range mismatch")
    if witness.get("missing_gate_symbol_ids") != [2, 4]:
        raise AssertionError("gate automaton missing gate symbols mismatch")

    transition_table = np.asarray(tables["gate_automaton_transition_table"], dtype=np.int64)
    branch_table = np.asarray(tables["gate_branch_word_table"], dtype=np.int64)
    trigram_table = np.asarray(tables["gate_trigram_window_table"], dtype=np.int64)
    observable_table = np.asarray(tables["gate_automaton_observable_table"], dtype=np.int64)

    if transition_table.shape != (16, len(AUTOMATON_TRANSITION_COLUMNS)):
        raise AssertionError("gate automaton transition table shape mismatch")
    if branch_table.shape != (6, len(BRANCH_WORD_COLUMNS)):
        raise AssertionError("gate automaton branch table shape mismatch")
    if trigram_table.shape != (12, len(TRIGRAM_WINDOW_COLUMNS)):
        raise AssertionError("gate automaton trigram table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(GATE_AUTOMATON_OBSERVABLE_COLUMNS)):
        raise AssertionError("gate automaton observable table shape mismatch")
    if transition_table[:, 5].tolist() != expected_gate_sequence:
        raise AssertionError("gate automaton transition table sequence mismatch")
    if branch_table[:, 3].tolist() != [1, 3, 5, 8, 12, 14]:
        raise AssertionError("gate branch word lengths mismatch")
    if trigram_table[:, 6].tolist() != [210, 180, 1, 9, 55, 119, 69, 203, 143, 213, 203, 141]:
        raise AssertionError("gate trigram triple ids mismatch")
    if trigram_table[:, 11].tolist() != [1] * 12:
        raise AssertionError("gate trigram left/right match flags mismatch")
    if trigram_table[:, 12].tolist() != [1] * 12:
        raise AssertionError("gate trigram direct sorted flags mismatch")
    if observable_table[:, 1].tolist() != [
        code for _, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]:
        raise AssertionError("gate automaton observable code order mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("typed_corridor_report", {}),
        TYPED_CORRIDOR_REPORT,
        "typed corridor report input",
    )
    assert_file_hash(inputs.get("typed_corridors", {}), TYPED_CORRIDOR_JSON, "typed corridor JSON input")
    assert_file_hash(
        inputs.get("typed_corridor_edges", {}),
        TYPED_CORRIDOR_EDGE_CSV,
        "typed corridor edge input",
    )
    assert_file_hash(
        inputs.get("typed_corridor_branches", {}),
        TYPED_CORRIDOR_BRANCH_CSV,
        "typed corridor branch input",
    )
    assert_file_hash(
        inputs.get("typed_corridor_tables", {}),
        TYPED_CORRIDOR_TABLES,
        "typed corridor tables input",
    )
    assert_file_hash(
        inputs.get("typed_corridor_certificate", {}),
        TYPED_CORRIDOR_CERTIFICATE,
        "typed corridor certificate input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity_report", {}),
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        "symbolic associativity report input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity", {}),
        SYMBOLIC_ASSOCIATIVITY_JSON,
        "symbolic associativity JSON input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity_csv", {}),
        SYMBOLIC_ASSOCIATIVITY_CSV,
        "symbolic associativity CSV input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity_tables", {}),
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        "symbolic associativity tables input",
    )
    assert_file_hash(
        inputs.get("symbolic_associativity_certificate", {}),
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        "symbolic associativity certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_gate_automaton_manifest@1":
        raise AssertionError("C985 d20 boundary spine gate automaton manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine gate automaton manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 boundary spine gate automaton manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 boundary spine gate automaton missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 boundary spine gate automaton index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 boundary spine gate automaton index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_gate_automaton@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "accepting_state_ids": witness.get("accepting_state_ids"),
        "source_to_branch_unique_trigram_count": witness.get(
            "source_to_branch_unique_trigram_count"
        ),
        "source_to_branch_canonical_triple_ids": witness.get(
            "source_to_branch_canonical_triple_ids"
        ),
        "source_to_branch_signature_union_range": witness.get(
            "source_to_branch_signature_union_range"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_gate_automaton()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
