from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_symbolic_rewrite_rules import (
        ALPHABET_COLUMNS,
        ATLAS_JSON,
        ATLAS_REPORT,
        CONCAT_COLUMNS,
        GEOMETRY_REPORT,
        INDEX_PATH,
        NORMAL_WORD_CERTIFICATE,
        NORMAL_WORD_REPORT,
        NORMAL_WORD_TABLES,
        NORMAL_WORDS_JSON,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        RULE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_symbolic_rewrite_rules import (
        ALPHABET_COLUMNS,
        ATLAS_JSON,
        ATLAS_REPORT,
        CONCAT_COLUMNS,
        GEOMETRY_REPORT,
        INDEX_PATH,
        NORMAL_WORD_CERTIFICATE,
        NORMAL_WORD_REPORT,
        NORMAL_WORD_TABLES,
        NORMAL_WORDS_JSON,
        OUT_DIR,
        RELATION_GEOMETRY_SIGNATURES,
        RULE_COLUMNS,
        STATUS,
        THEOREM_ID,
        build_payloads,
        self_hash,
    )


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


def validate_c985_d20_symbolic_rewrite_rules() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    symbolic_alphabet = load_json(OUT_DIR / "symbolic_alphabet.json")
    word_rewrites = load_json(OUT_DIR / "word_concatenation_rewrites.json")
    certificate = load_json(OUT_DIR / "symbolic_rewrite_certificate.json")
    alphabet_csv = (OUT_DIR / "symbolic_alphabet.csv").read_text(encoding="utf-8")
    rules_csv = (OUT_DIR / "rewrite_rules.csv").read_text(encoding="utf-8")
    concat_csv = (OUT_DIR / "word_concatenation_rewrites.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "symbolic_rewrite_tables.npz", allow_pickle=False)
    alphabet_table = np.asarray(tables["alphabet_table"], dtype=np.int64)
    membership = np.asarray(tables["alphabet_signature_membership"], dtype=np.int8)
    rule_table = np.asarray(tables["rewrite_rule_table"], dtype=np.int64)
    concat_table = np.asarray(tables["word_concatenation_rewrite_table"], dtype=np.int64)
    index = load_json(INDEX_PATH)

    if symbolic_alphabet != expected["symbolic_alphabet"]:
        raise AssertionError("d20 symbolic alphabet JSON is not reproducible")
    if word_rewrites != expected["word_concatenation_rewrites"]:
        raise AssertionError("d20 word concatenation rewrite JSON is not reproducible")
    if alphabet_csv != expected["symbolic_alphabet_csv"]:
        raise AssertionError("d20 symbolic alphabet CSV is not reproducible")
    if rules_csv != expected["rewrite_rules_csv"]:
        raise AssertionError("d20 symbolic rewrite rules CSV is not reproducible")
    if concat_csv != expected["word_concatenation_rewrites_csv"]:
        raise AssertionError("d20 word concatenation rewrite CSV is not reproducible")
    if not np.array_equal(alphabet_table, expected["alphabet_table"]):
        raise AssertionError("d20 symbolic alphabet table is not reproducible")
    if not np.array_equal(membership, expected["alphabet_signature_membership"]):
        raise AssertionError("d20 symbolic alphabet signature membership is not reproducible")
    if not np.array_equal(rule_table, expected["rewrite_rule_table"]):
        raise AssertionError("d20 symbolic rewrite rule table is not reproducible")
    if not np.array_equal(concat_table, expected["word_concatenation_rewrite_table"]):
        raise AssertionError("d20 word concatenation rewrite table is not reproducible")
    if certificate != expected["symbolic_rewrite_certificate"]:
        raise AssertionError("d20 symbolic rewrite certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_symbolic_rewrite_rules@1":
        raise AssertionError("C985 d20 symbolic rewrite report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 symbolic rewrite rules are not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 symbolic rewrite all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 symbolic rewrite checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbolic rewrite report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 symbolic rewrite report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "normal_form_words_report_certified",
        "normal_form_words_certificate_certified",
        "boundary_atlas_report_certified",
        "tensor_geometry_report_certified",
        "normal_word_table_shape_is_36_by_13",
        "normal_atom_table_shape_is_6_by_8",
        "alphabet_symbol_count_is_6",
        "alphabet_symbols_have_six_normal_words_each",
        "alphabet_signature_membership_shape_is_6_by_233",
        "alphabet_covers_all_six_h6_sectors",
        "alphabet_signature_union_count_is_221",
        "binary_rewrite_rule_count_is_36",
        "canonical_binary_pair_count_is_21",
        "nontrivial_swap_rule_count_is_15",
        "word_concatenation_rewrite_count_is_1296",
        "each_symbol_pair_has_36_word_concatenations",
        "binary_sector_coverage_histogram_is_6_three_10_four_18_five_2_six",
        "binary_sector_overlap_histogram_is_2_zero_18_one_10_two_6_three",
        "full_sector_binary_rule_count_is_2",
        "full_sector_word_concatenation_count_is_72",
        "binary_rule_signature_union_count_max_is_155",
        "max_signature_union_rules_are_atoms_7_and_12",
        "all_rewrite_rules_preserve_sector_union",
        "all_rewrite_rules_preserve_signature_union",
        "all_rewrite_rules_preserve_tensor_support_sum",
        "all_rewrite_rules_preserve_tensor_mass_sum",
        "word_concatenations_map_to_existing_rules",
        "word_concatenation_signature_counts_match_rules",
        "word_concatenation_tensor_support_sums_match_rules",
        "word_concatenation_tensor_mass_sums_match_rules",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 symbolic rewrite missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("alphabet_symbol_count") != 6:
        raise AssertionError("symbolic alphabet count mismatch")
    if witness.get("alphabet_atom_ids") != [1, 4, 7, 11, 12, 19]:
        raise AssertionError("symbolic alphabet atom ids mismatch")
    if witness.get("covered_h6_sectors") != ["B-", "B+", "V-", "V+", "S-", "S+"]:
        raise AssertionError("symbolic alphabet H6 sector coverage mismatch")
    if witness.get("signature_class_total") != 233:
        raise AssertionError("symbolic rewrite signature class total mismatch")
    if witness.get("alphabet_signature_union_count") != 221:
        raise AssertionError("symbolic alphabet signature union count mismatch")
    if witness.get("binary_rewrite_rule_count") != 36:
        raise AssertionError("symbolic binary rewrite rule count mismatch")
    if witness.get("canonical_binary_pair_count") != 21:
        raise AssertionError("symbolic canonical pair count mismatch")
    if witness.get("nontrivial_swap_rule_count") != 15:
        raise AssertionError("symbolic swap rule count mismatch")
    if witness.get("word_concatenation_rewrite_count") != 1296:
        raise AssertionError("symbolic word concatenation count mismatch")
    if witness.get("full_sector_binary_rule_count") != 2:
        raise AssertionError("symbolic full-sector binary count mismatch")
    if witness.get("full_sector_word_concatenation_count") != 72:
        raise AssertionError("symbolic full-sector word concatenation count mismatch")
    if witness.get("binary_rule_signature_union_count_max") != 155:
        raise AssertionError("symbolic max signature union count mismatch")
    if witness.get("max_signature_union_rule_atom_pairs") != [[7, 12], [12, 7]]:
        raise AssertionError("symbolic max signature atom pairs mismatch")

    if alphabet_table.shape != (6, len(ALPHABET_COLUMNS)):
        raise AssertionError("symbolic alphabet table shape mismatch")
    if membership.shape != (6, 233):
        raise AssertionError("symbolic alphabet membership shape mismatch")
    if rule_table.shape != (36, len(RULE_COLUMNS)):
        raise AssertionError("symbolic rewrite rule table shape mismatch")
    if concat_table.shape != (1296, len(CONCAT_COLUMNS)):
        raise AssertionError("symbolic word concatenation table shape mismatch")
    if int(np.count_nonzero(rule_table[:, 11] != rule_table[:, 12])) != 0:
        raise AssertionError("symbolic rewrite sector union changed under canonicalization")
    if int(np.count_nonzero(rule_table[:, 10])) != 15:
        raise AssertionError("symbolic rewrite swap-rule column mismatch")
    if sorted(int(x) for x in np.bincount(concat_table[:, 5], minlength=36)) != [36] * 36:
        raise AssertionError("symbolic word concatenations do not cover each rule 36 times")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("normal_form_words_report", {}),
        NORMAL_WORD_REPORT,
        "normal-form words report input",
    )
    assert_file_hash(inputs.get("normal_form_words", {}), NORMAL_WORDS_JSON, "normal-form words input")
    assert_file_hash(
        inputs.get("normal_form_word_tables", {}),
        NORMAL_WORD_TABLES,
        "normal-form word tables input",
    )
    assert_file_hash(
        inputs.get("normal_form_words_certificate", {}),
        NORMAL_WORD_CERTIFICATE,
        "normal-form words certificate input",
    )
    assert_file_hash(inputs.get("boundary_atlas_report", {}), ATLAS_REPORT, "boundary atlas report input")
    assert_file_hash(inputs.get("boundary_atlas", {}), ATLAS_JSON, "boundary atlas input")
    assert_file_hash(
        inputs.get("tensor_geometry_report", {}),
        GEOMETRY_REPORT,
        "tensor geometry report input",
    )
    assert_file_hash(
        inputs.get("relation_geometry_signatures", {}),
        RELATION_GEOMETRY_SIGNATURES,
        "relation signatures input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_symbolic_rewrite_rules_manifest@1":
        raise AssertionError("C985 d20 symbolic rewrite manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbolic rewrite manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 symbolic rewrite manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 symbolic rewrite rules missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbolic rewrite index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 symbolic rewrite index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_symbolic_rewrite_rules@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "alphabet_atom_ids": witness.get("alphabet_atom_ids"),
        "alphabet_signature_union_count": witness.get("alphabet_signature_union_count"),
        "binary_rewrite_rule_count": witness.get("binary_rewrite_rule_count"),
        "canonical_binary_pair_count": witness.get("canonical_binary_pair_count"),
        "word_concatenation_rewrite_count": witness.get("word_concatenation_rewrite_count"),
        "full_sector_binary_rule_count": witness.get("full_sector_binary_rule_count"),
        "full_sector_word_concatenation_count": witness.get("full_sector_word_concatenation_count"),
        "binary_rule_signature_union_count_max": witness.get("binary_rule_signature_union_count_max"),
        "max_signature_union_rule_atom_pairs": witness.get("max_signature_union_rule_atom_pairs"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_symbolic_rewrite_rules()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
