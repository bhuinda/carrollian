from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        FRONTIER_COLUMNS,
        NEXT_SYMBOL_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOL_STATE_CERTIFICATE,
        SYMBOL_STATE_FORBIDDEN,
        SYMBOL_STATE_JSON,
        SYMBOL_STATE_REPORT,
        SYMBOL_STATE_TABLES,
        THEOREM_ID,
        WORD_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        FRONTIER_COLUMNS,
        NEXT_SYMBOL_COLUMNS,
        OBSERVABLE_CODES,
        OBSERVABLE_COLUMNS,
        OUT_DIR,
        PREFIX_COLUMNS,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOL_STATE_CERTIFICATE,
        SYMBOL_STATE_FORBIDDEN,
        SYMBOL_STATE_JSON,
        SYMBOL_STATE_REPORT,
        SYMBOL_STATE_TABLES,
        THEOREM_ID,
        WORD_COLUMNS,
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


def validate_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    realizability = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_carrier_realizability.json"
    )
    certificate = load_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate.json"
    )
    words_csv = (OUT_DIR / "aperture_overhead2_carrier_words.csv").read_text(
        encoding="utf-8"
    )
    prefixes_csv = (OUT_DIR / "aperture_overhead2_carrier_prefixes.csv").read_text(
        encoding="utf-8"
    )
    frontier_csv = (
        OUT_DIR / "aperture_overhead2_carrier_frontier_paths.csv"
    ).read_text(encoding="utf-8")
    next_symbols_csv = (
        OUT_DIR / "aperture_overhead2_carrier_next_symbols.csv"
    ).read_text(encoding="utf-8")
    observables_csv = (
        OUT_DIR / "aperture_overhead2_carrier_observables.csv"
    ).read_text(encoding="utf-8")
    tables = np.load(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_carrier_realizability_tables.npz",
        allow_pickle=False,
    )
    index = load_json(INDEX_PATH)

    if (
        realizability
        != expected[
            "signature_boundary_spine_aperture_overhead2_carrier_realizability"
        ]
    ):
        raise AssertionError("overhead2 carrier realizability JSON is not reproducible")
    if words_csv != expected["aperture_overhead2_carrier_words_csv"]:
        raise AssertionError("overhead2 carrier words CSV is not reproducible")
    if prefixes_csv != expected["aperture_overhead2_carrier_prefixes_csv"]:
        raise AssertionError("overhead2 carrier prefixes CSV is not reproducible")
    if frontier_csv != expected["aperture_overhead2_carrier_frontier_paths_csv"]:
        raise AssertionError("overhead2 carrier frontier CSV is not reproducible")
    if next_symbols_csv != expected["aperture_overhead2_carrier_next_symbols_csv"]:
        raise AssertionError("overhead2 carrier next-symbol CSV is not reproducible")
    if observables_csv != expected["aperture_overhead2_carrier_observables_csv"]:
        raise AssertionError("overhead2 carrier observables CSV is not reproducible")
    if (
        certificate
        != expected[
            "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate"
        ]
    ):
        raise AssertionError("overhead2 carrier certificate is not reproducible")

    for name in [
        "word_table",
        "prefix_table",
        "frontier_table",
        "next_symbol_table",
        "observable_table",
    ]:
        if not np.array_equal(np.asarray(tables[name]), expected[name]):
            raise AssertionError(f"overhead2 carrier table {name} is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability@1":
        raise AssertionError("C985 d20 overhead2 carrier report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 overhead2 carrier layer is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 overhead2 carrier all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 overhead2 carrier checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead2 carrier report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 overhead2 carrier report is not reproducible")

    missing = sorted(
        key
        for key in expected["report"]["checks"]
        if report.get("checks", {}).get(key) is not True
    )
    if missing:
        raise AssertionError(f"C985 d20 overhead2 carrier missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("target_words") != [[2, 1, 4, 2, 5], [2, 1, 5, 2, 4]]:
        raise AssertionError("overhead2 carrier target words mismatch")
    if witness.get("rooted_full_realization_count") != 0:
        raise AssertionError("overhead2 carrier rooted count mismatch")
    if witness.get("global_full_realization_count") != 0:
        raise AssertionError("overhead2 carrier global count mismatch")
    if witness.get("first_missing_prefix_length_by_word") != {"0": 4, "1": 5}:
        raise AssertionError("overhead2 carrier missing-prefix witness mismatch")
    if witness.get("rooted_last_viable_prefix_count_by_word") != {"0": 8, "1": 8}:
        raise AssertionError("overhead2 carrier rooted frontier mismatch")
    if witness.get("global_last_viable_prefix_count_by_word") != {"0": 32, "1": 32}:
        raise AssertionError("overhead2 carrier global frontier mismatch")
    if witness.get("required_next_symbol_count_by_scope_word") != {
        "0:0": 0,
        "0:1": 0,
        "1:0": 0,
        "1:1": 0,
    }:
        raise AssertionError("overhead2 carrier required-next mismatch")

    word_table = np.asarray(tables["word_table"], dtype=np.int64)
    prefix_table = np.asarray(tables["prefix_table"], dtype=np.int64)
    frontier_table = np.asarray(tables["frontier_table"], dtype=np.int64)
    next_symbol_table = np.asarray(tables["next_symbol_table"], dtype=np.int64)
    observable_table = np.asarray(tables["observable_table"], dtype=np.int64)
    if word_table.shape != (2, len(WORD_COLUMNS)):
        raise AssertionError("overhead2 carrier word table shape mismatch")
    if prefix_table.shape != (20, len(PREFIX_COLUMNS)):
        raise AssertionError("overhead2 carrier prefix table shape mismatch")
    if frontier_table.shape != (80, len(FRONTIER_COLUMNS)):
        raise AssertionError("overhead2 carrier frontier table shape mismatch")
    if next_symbol_table.shape != (42, len(NEXT_SYMBOL_COLUMNS)):
        raise AssertionError("overhead2 carrier next-symbol table shape mismatch")
    if observable_table.shape != (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)):
        raise AssertionError("overhead2 carrier observable table shape mismatch")

    rooted_full_idx = WORD_COLUMNS.index("rooted_full_path_count")
    global_full_idx = WORD_COLUMNS.index("global_full_path_count")
    missing_root_idx = WORD_COLUMNS.index("rooted_first_missing_prefix_length")
    missing_global_idx = WORD_COLUMNS.index("global_first_missing_prefix_length")
    if word_table[:, rooted_full_idx].tolist() != [0, 0]:
        raise AssertionError("overhead2 carrier rooted full vector mismatch")
    if word_table[:, global_full_idx].tolist() != [0, 0]:
        raise AssertionError("overhead2 carrier global full vector mismatch")
    if word_table[:, missing_root_idx].tolist() != [4, 5]:
        raise AssertionError("overhead2 carrier rooted missing vector mismatch")
    if word_table[:, missing_global_idx].tolist() != [4, 5]:
        raise AssertionError("overhead2 carrier global missing vector mismatch")

    first_missing_idx = PREFIX_COLUMNS.index("first_missing_flag")
    path_count_idx = PREFIX_COLUMNS.index("path_count")
    required_symbol_idx = PREFIX_COLUMNS.index("required_symbol_id")
    missing_rows = prefix_table[prefix_table[:, first_missing_idx] == 1]
    if missing_rows.shape[0] != 4:
        raise AssertionError("overhead2 carrier missing row count mismatch")
    if missing_rows[:, path_count_idx].tolist() != [0, 0, 0, 0]:
        raise AssertionError("overhead2 carrier missing row path counts mismatch")
    if missing_rows[:, required_symbol_idx].tolist() != [2, 2, 4, 4]:
        raise AssertionError("overhead2 carrier missing required symbols mismatch")

    required_flag_idx = NEXT_SYMBOL_COLUMNS.index("required_symbol_flag")
    if int(np.sum(next_symbol_table[:, required_flag_idx])) != 0:
        raise AssertionError("overhead2 carrier required next-symbol unexpectedly present")

    inputs = report.get("inputs", {})
    assert_file_hash(inputs.get("symbol_state_report", {}), SYMBOL_STATE_REPORT, "symbol-state report input")
    assert_file_hash(inputs.get("symbol_state_json", {}), SYMBOL_STATE_JSON, "symbol-state JSON input")
    assert_file_hash(inputs.get("symbol_state_tables", {}), SYMBOL_STATE_TABLES, "symbol-state tables input")
    assert_file_hash(inputs.get("symbol_state_forbidden_transitions", {}), SYMBOL_STATE_FORBIDDEN, "symbol-state forbidden transitions input")
    assert_file_hash(inputs.get("symbol_state_certificate", {}), SYMBOL_STATE_CERTIFICATE, "symbol-state certificate input")
    assert_file_hash(inputs.get("cell_complex_report", {}), CELL_COMPLEX_REPORT, "cell complex report input")
    assert_file_hash(inputs.get("cell_complex_edges", {}), CELL_COMPLEX_EDGES, "cell complex edges input")
    assert_file_hash(inputs.get("cell_complex_tables", {}), CELL_COMPLEX_TABLES, "cell complex tables input")
    assert_file_hash(inputs.get("cell_complex_certificate", {}), CELL_COMPLEX_CERTIFICATE, "cell complex certificate input")
    assert_file_hash(inputs.get("rewrite_complex_report", {}), REWRITE_COMPLEX_REPORT, "rewrite complex report input")
    assert_file_hash(inputs.get("rewrite_complex_edges", {}), REWRITE_COMPLEX_EDGES, "rewrite complex edges input")
    assert_file_hash(inputs.get("rewrite_complex_tables", {}), REWRITE_COMPLEX_TABLES, "rewrite complex tables input")
    assert_file_hash(inputs.get("rewrite_complex_certificate", {}), REWRITE_COMPLEX_CERTIFICATE, "rewrite complex certificate input")
    assert_file_hash(inputs.get("symbolic_associativity_report", {}), SYMBOLIC_ASSOCIATIVITY_REPORT, "symbolic associativity report input")
    assert_file_hash(inputs.get("symbolic_associativity_csv", {}), SYMBOLIC_ASSOCIATIVITY_CSV, "symbolic associativity CSV input")
    assert_file_hash(inputs.get("symbolic_associativity_tables", {}), SYMBOLIC_ASSOCIATIVITY_TABLES, "symbolic associativity tables input")
    assert_file_hash(inputs.get("symbolic_associativity_certificate", {}), SYMBOLIC_ASSOCIATIVITY_CERTIFICATE, "symbolic associativity certificate input")
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_CSV, "symbolic alphabet input")

    if manifest.get("schema") != "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability_manifest@1":
        raise AssertionError("C985 d20 overhead2 carrier manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead2 carrier manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 overhead2 carrier manifest self hash mismatch")

    entry = next(
        (row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID),
        None,
    )
    if entry is None:
        raise AssertionError("C985 d20 overhead2 carrier missing from index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 overhead2 carrier index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 overhead2 carrier index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "target_words": witness.get("target_words"),
        "rooted_full_realization_count": witness.get(
            "rooted_full_realization_count"
        ),
        "global_full_realization_count": witness.get(
            "global_full_realization_count"
        ),
        "first_missing_prefix_length_by_word": witness.get(
            "first_missing_prefix_length_by_word"
        ),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
