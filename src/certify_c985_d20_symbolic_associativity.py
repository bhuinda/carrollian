from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .certify_io import ROOT, h_file, h_json
    from .derive_c985_d20_symbolic_associativity import (
        OUT_DIR,
        PENTAGON_CERTIFICATE,
        PENTAGON_NORMAL_FORM,
        PENTAGON_REPORT,
        REWRITE_REPORT,
        STATUS,
        SYMBOLIC_ALPHABET_JSON,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_TABLES,
        THEOREM_ID,
        TRIPLE_COLUMNS,
        build_payloads,
        self_hash,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from certify_io import ROOT, h_file, h_json
    from derive_c985_d20_symbolic_associativity import (
        OUT_DIR,
        PENTAGON_CERTIFICATE,
        PENTAGON_NORMAL_FORM,
        PENTAGON_REPORT,
        REWRITE_REPORT,
        STATUS,
        SYMBOLIC_ALPHABET_JSON,
        SYMBOLIC_REWRITE_CERTIFICATE,
        SYMBOLIC_REWRITE_TABLES,
        THEOREM_ID,
        TRIPLE_COLUMNS,
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


def validate_c985_d20_symbolic_associativity() -> dict[str, Any]:
    expected = build_payloads()

    report = load_json(OUT_DIR / "report.json")
    manifest = load_json(OUT_DIR / "manifest.json")
    symbolic_associativity = load_json(OUT_DIR / "symbolic_associativity.json")
    certificate = load_json(OUT_DIR / "symbolic_associativity_certificate.json")
    associativity_csv = (OUT_DIR / "symbolic_associativity.csv").read_text(encoding="utf-8")
    tables = np.load(OUT_DIR / "symbolic_associativity_tables.npz", allow_pickle=False)
    associativity_table = np.asarray(tables["symbolic_associativity_table"], dtype=np.int64)
    index = load_json(INDEX_PATH)

    if symbolic_associativity != expected["symbolic_associativity"]:
        raise AssertionError("d20 symbolic associativity JSON is not reproducible")
    if associativity_csv != expected["symbolic_associativity_csv"]:
        raise AssertionError("d20 symbolic associativity CSV is not reproducible")
    if not np.array_equal(associativity_table, expected["symbolic_associativity_table"]):
        raise AssertionError("d20 symbolic associativity table is not reproducible")
    if certificate != expected["symbolic_associativity_certificate"]:
        raise AssertionError("d20 symbolic associativity certificate is not reproducible")

    if report.get("schema") != "c985.proof_obligation.d20_symbolic_associativity@1":
        raise AssertionError("C985 d20 symbolic associativity report schema mismatch")
    if report.get("status") != STATUS:
        raise AssertionError("C985 d20 symbolic associativity is not certified")
    if report.get("all_checks_pass") is not True:
        raise AssertionError("C985 d20 symbolic associativity all_checks_pass is not true")
    if report.get("checks") != expected["report"]["checks"]:
        raise AssertionError("C985 d20 symbolic associativity checks mismatch")
    if self_hash(report, "certificate_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbolic associativity report self hash mismatch")
    if report.get("certificate_sha256") != expected["report"]["certificate_sha256"]:
        raise AssertionError("C985 d20 symbolic associativity report is not reproducible")

    checks = report.get("checks", {})
    required_true = {
        "symbolic_rewrite_report_certified",
        "symbolic_rewrite_certificate_certified",
        "pentagon_report_certified",
        "pentagon_certificate_certified",
        "alphabet_table_shape_is_6_by_9",
        "alphabet_signature_membership_shape_is_6_by_233",
        "binary_rewrite_table_shape_is_36_by_22",
        "word_concatenation_table_shape_is_1296_by_13",
        "symbolic_triple_count_is_216",
        "canonical_symbolic_triple_count_is_56",
        "noncanonical_symbolic_triple_count_is_160",
        "all_left_reductions_equal_right_reductions",
        "all_reductions_match_direct_sorted_normal_form",
        "each_symbolic_triple_has_216_normal_word_lifts",
        "normal_word_triple_count_is_46656",
        "full_sector_symbolic_triple_count_is_78",
        "full_sector_normal_word_triple_count_is_16848",
        "symbolic_triple_sector_coverage_histogram_is_6_three_30_four_102_five_78_six",
        "symbolic_triple_signature_union_count_max_is_185",
        "symbolic_triple_signature_union_count_min_is_53",
        "max_signature_union_triples_are_atoms_7_12_19_permutations",
        "min_signature_union_triple_is_atom_11_repeated",
        "left_and_right_paths_use_all_36_binary_rules",
        "left_and_right_paths_have_equal_swap_counts",
        "pentagon_top_and_bottom_normal_forms_match",
        "pentagon_normal_form_is_typed_length_four_chain",
        "pentagon_report_exact_chain_count_matches",
    }
    missing = sorted(key for key in required_true if checks.get(key) is not True)
    if missing:
        raise AssertionError(f"C985 d20 symbolic associativity missing true checks: {missing}")

    witness = report.get("witness", {})
    if witness.get("symbolic_triple_count") != 216:
        raise AssertionError("symbolic associativity triple count mismatch")
    if witness.get("canonical_symbolic_triple_count") != 56:
        raise AssertionError("symbolic associativity canonical triple count mismatch")
    if witness.get("noncanonical_symbolic_triple_count") != 160:
        raise AssertionError("symbolic associativity noncanonical triple count mismatch")
    if witness.get("total_normal_word_triple_count") != 46656:
        raise AssertionError("symbolic associativity normal-word triple count mismatch")
    if witness.get("full_sector_symbolic_triple_count") != 78:
        raise AssertionError("symbolic associativity full-sector triple count mismatch")
    if witness.get("full_sector_normal_word_triple_count") != 16848:
        raise AssertionError("symbolic associativity full-sector word triple count mismatch")
    if witness.get("left_path_swap_count") != 270 or witness.get("right_path_swap_count") != 270:
        raise AssertionError("symbolic associativity path swap count mismatch")
    if witness.get("symbolic_triple_signature_union_count_max") != 185:
        raise AssertionError("symbolic associativity max signature union mismatch")
    if witness.get("symbolic_triple_signature_union_count_min") != 53:
        raise AssertionError("symbolic associativity min signature union mismatch")
    if witness.get("max_signature_union_atom_triples") != [
        [7, 12, 19],
        [7, 19, 12],
        [12, 7, 19],
        [12, 19, 7],
        [19, 7, 12],
        [19, 12, 7],
    ]:
        raise AssertionError("symbolic associativity max signature atom triples mismatch")
    if witness.get("min_signature_union_atom_triples") != [[11, 11, 11]]:
        raise AssertionError("symbolic associativity min signature atom triple mismatch")
    if witness.get("symbolic_associativity_normal_form") != "sorted_length_three_symbol_word(x_i,x_j,x_k)":
        raise AssertionError("symbolic associativity normal form mismatch")
    if witness.get("pentagon_chain_normal_form") != "typed_length_four_chain(x0,x1,x2,x3,x4)":
        raise AssertionError("symbolic associativity pentagon normal form mismatch")

    if associativity_table.shape != (216, len(TRIPLE_COLUMNS)):
        raise AssertionError("symbolic associativity table shape mismatch")
    if int(np.count_nonzero(associativity_table[:, 16] != 1)) != 0:
        raise AssertionError("symbolic associativity has left/right reduction defects")
    if int(np.count_nonzero(associativity_table[:, 17] != 1)) != 0:
        raise AssertionError("symbolic associativity has direct sorted normal-form defects")
    if int(np.count_nonzero(associativity_table[:, 23] != 216)) != 0:
        raise AssertionError("symbolic associativity word multiplicity mismatch")

    inputs = report.get("inputs", {})
    assert_file_hash(
        inputs.get("symbolic_rewrite_report", {}),
        REWRITE_REPORT,
        "symbolic rewrite report input",
    )
    assert_file_hash(inputs.get("symbolic_alphabet", {}), SYMBOLIC_ALPHABET_JSON, "symbolic alphabet input")
    assert_file_hash(
        inputs.get("symbolic_rewrite_tables", {}),
        SYMBOLIC_REWRITE_TABLES,
        "symbolic rewrite tables input",
    )
    assert_file_hash(
        inputs.get("symbolic_rewrite_certificate", {}),
        SYMBOLIC_REWRITE_CERTIFICATE,
        "symbolic rewrite certificate input",
    )
    assert_file_hash(inputs.get("pentagon_report", {}), PENTAGON_REPORT, "pentagon report input")
    assert_file_hash(
        inputs.get("pentagon_normal_form", {}),
        PENTAGON_NORMAL_FORM,
        "pentagon normal form input",
    )
    assert_file_hash(
        inputs.get("pentagon_certificate", {}),
        PENTAGON_CERTIFICATE,
        "pentagon certificate input",
    )

    if manifest.get("schema") != "c985.proof_obligation.d20_symbolic_associativity_manifest@1":
        raise AssertionError("C985 d20 symbolic associativity manifest schema mismatch")
    if manifest.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbolic associativity manifest report hash mismatch")
    if self_hash(manifest, "manifest_sha256") != manifest.get("manifest_sha256"):
        raise AssertionError("C985 d20 symbolic associativity manifest self hash mismatch")

    entry = next((row for row in index.get("obligations", []) if row.get("id") == THEOREM_ID), None)
    if entry is None:
        raise AssertionError("C985 d20 symbolic associativity missing from proof obligation index")
    if entry.get("report_sha256") != report.get("certificate_sha256"):
        raise AssertionError("C985 d20 symbolic associativity index report hash mismatch")
    if entry.get("status") != report.get("status"):
        raise AssertionError("C985 d20 symbolic associativity index status mismatch")
    if h_json({key: value for key, value in index.items() if key != "registry_sha256"}) != index.get(
        "registry_sha256"
    ):
        raise AssertionError("proof obligation index self hash mismatch")

    return {
        "schema": "c985.verification.d20_symbolic_associativity@1",
        "status": "PASS",
        "verified_report": (OUT_DIR / "report.json").relative_to(ROOT).as_posix(),
        "certificate_sha256": report.get("certificate_sha256"),
        "symbolic_triple_count": witness.get("symbolic_triple_count"),
        "canonical_symbolic_triple_count": witness.get("canonical_symbolic_triple_count"),
        "total_normal_word_triple_count": witness.get("total_normal_word_triple_count"),
        "full_sector_symbolic_triple_count": witness.get("full_sector_symbolic_triple_count"),
        "symbolic_triple_signature_union_count_max": witness.get(
            "symbolic_triple_signature_union_count_max"
        ),
        "max_signature_union_atom_triples": witness.get("max_signature_union_atom_triples"),
        "symbolic_associativity_normal_form": witness.get("symbolic_associativity_normal_form"),
        "pentagon_chain_normal_form": witness.get("pentagon_chain_normal_form"),
        "closure_boundary": report.get("closure_boundary"),
        "next_highest_yield_item": report.get("next_highest_yield_item"),
    }


def main() -> None:
    result = validate_c985_d20_symbolic_associativity()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
