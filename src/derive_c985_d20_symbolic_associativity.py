from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_symbolic_rewrite_rules import (
        SYMBOL_NAMES,
        csv_text,
        histogram,
        int_list_sha256,
        mask_labels,
    )
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_symbolic_rewrite_rules import (
        SYMBOL_NAMES,
        csv_text,
        histogram,
        int_list_sha256,
        mask_labels,
    )
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_symbolic_associativity"
STATUS = "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

REWRITE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_symbolic_rewrite_rules"
PENTAGON_DIR = D20_INVARIANTS / "proof_obligations" / "c985_pentagon_chain_normal_form"

REWRITE_REPORT = REWRITE_DIR / "report.json"
SYMBOLIC_ALPHABET_JSON = REWRITE_DIR / "symbolic_alphabet.json"
SYMBOLIC_REWRITE_TABLES = REWRITE_DIR / "symbolic_rewrite_tables.npz"
SYMBOLIC_REWRITE_CERTIFICATE = REWRITE_DIR / "symbolic_rewrite_certificate.json"
PENTAGON_REPORT = PENTAGON_DIR / "report.json"
PENTAGON_NORMAL_FORM = PENTAGON_DIR / "pentagon_normal_form.json"
PENTAGON_CERTIFICATE = PENTAGON_DIR / "pentagon_certificate.json"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_symbolic_associativity.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_symbolic_associativity.py"

TRIPLE_COLUMNS = [
    "triple_id",
    "left_symbol_id",
    "middle_symbol_id",
    "right_symbol_id",
    "left_atom_id",
    "middle_atom_id",
    "right_atom_id",
    "canonical_first_symbol_id",
    "canonical_second_symbol_id",
    "canonical_third_symbol_id",
    "left_path_first_rule_id",
    "left_path_second_rule_id",
    "left_path_third_rule_id",
    "right_path_first_rule_id",
    "right_path_second_rule_id",
    "right_path_third_rule_id",
    "left_final_matches_right_final",
    "matches_direct_sorted_normal_form",
    "sector_union_mask",
    "sector_coverage_count",
    "signature_union_count",
    "tensor_path_support_sum",
    "tensor_path_coefficient_mass_sum",
    "word_triple_multiplicity",
    "left_path_swap_count",
    "right_path_swap_count",
    "canonical_triple_id",
]


def rule_lookup(rules: list[dict[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    return {
        (int(row["left_symbol_id"]), int(row["right_symbol_id"])): row
        for row in rules
    }


def apply_rule(
    rules: dict[tuple[int, int], dict[str, Any]],
    left: int,
    right: int,
) -> tuple[int, int, dict[str, Any]]:
    rule = rules[(int(left), int(right))]
    return (
        int(rule["canonical_left_symbol_id"]),
        int(rule["canonical_right_symbol_id"]),
        rule,
    )


def left_associated_reduction(
    rules: dict[tuple[int, int], dict[str, Any]],
    triple: tuple[int, int, int],
) -> tuple[tuple[int, int, int], list[dict[str, Any]], list[list[int]]]:
    a, b, c = triple
    p, q, first = apply_rule(rules, a, b)
    after_first = [p, q, c]
    r, s, second = apply_rule(rules, after_first[1], after_first[2])
    after_second = [after_first[0], r, s]
    t, u, third = apply_rule(rules, after_second[0], after_second[1])
    final = (t, u, after_second[2])
    return final, [first, second, third], [after_first, after_second, list(final)]


def right_associated_reduction(
    rules: dict[tuple[int, int], dict[str, Any]],
    triple: tuple[int, int, int],
) -> tuple[tuple[int, int, int], list[dict[str, Any]], list[list[int]]]:
    a, b, c = triple
    p, q, first = apply_rule(rules, b, c)
    after_first = [a, p, q]
    r, s, second = apply_rule(rules, after_first[0], after_first[1])
    after_second = [r, s, after_first[2]]
    t, u, third = apply_rule(rules, after_second[1], after_second[2])
    final = (after_second[0], t, u)
    return final, [first, second, third], [after_first, after_second, list(final)]


def build_symbolic_triples(
    alphabet_rows: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    rules_by_pair = rule_lookup(rules)
    canonical_ids: dict[tuple[int, int, int], int] = {}
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []

    for triple in itertools.product(range(len(alphabet_rows)), repeat=3):
        canonical = tuple(sorted(int(x) for x in triple))
        if canonical not in canonical_ids:
            canonical_ids[canonical] = len(canonical_ids)

        left_final, left_rules, left_intermediates = left_associated_reduction(rules_by_pair, triple)
        right_final, right_rules, right_intermediates = right_associated_reduction(rules_by_pair, triple)
        triple_rows = [alphabet_rows[index] for index in triple]
        sector_union_mask = 0
        signature_union: set[int] = set()
        support_sum = 0
        mass_sum = 0
        for row in triple_rows:
            sector_union_mask |= int(row["sector_mask"])
            signature_union.update(int(x) for x in row["signature_class_ids"])
            support_sum += int(row["tensor_path_support"])
            mass_sum += int(row["tensor_path_coefficient_mass"])

        left_swap_count = sum(int(rule["is_swap_rule"]) for rule in left_rules)
        right_swap_count = sum(int(rule["is_swap_rule"]) for rule in right_rules)
        normal_word_multiplicity = int(
            np.prod([int(row["normal_word_count"]) for row in triple_rows])
        )
        row = {
            "triple_id": len(rows),
            "source_word": " ".join(SYMBOL_NAMES[index] for index in triple),
            "left_symbol_id": int(triple[0]),
            "middle_symbol_id": int(triple[1]),
            "right_symbol_id": int(triple[2]),
            "left_atom_id": int(triple_rows[0]["atom_id"]),
            "middle_atom_id": int(triple_rows[1]["atom_id"]),
            "right_atom_id": int(triple_rows[2]["atom_id"]),
            "canonical_word": " ".join(SYMBOL_NAMES[index] for index in canonical),
            "canonical_first_symbol_id": int(canonical[0]),
            "canonical_second_symbol_id": int(canonical[1]),
            "canonical_third_symbol_id": int(canonical[2]),
            "canonical_atom_ids": [
                int(alphabet_rows[index]["atom_id"])
                for index in canonical
            ],
            "canonical_triple_id": canonical_ids[canonical],
            "left_path": {
                "sorting_network": "(01),(12),(01)",
                "rule_ids": [int(rule["rule_id"]) for rule in left_rules],
                "intermediate_words": left_intermediates,
                "final_symbol_ids": list(left_final),
            },
            "right_path": {
                "sorting_network": "(12),(01),(12)",
                "rule_ids": [int(rule["rule_id"]) for rule in right_rules],
                "intermediate_words": right_intermediates,
                "final_symbol_ids": list(right_final),
            },
            "left_path_first_rule_id": int(left_rules[0]["rule_id"]),
            "left_path_second_rule_id": int(left_rules[1]["rule_id"]),
            "left_path_third_rule_id": int(left_rules[2]["rule_id"]),
            "right_path_first_rule_id": int(right_rules[0]["rule_id"]),
            "right_path_second_rule_id": int(right_rules[1]["rule_id"]),
            "right_path_third_rule_id": int(right_rules[2]["rule_id"]),
            "left_final_matches_right_final": int(left_final == right_final),
            "matches_direct_sorted_normal_form": int(left_final == canonical and right_final == canonical),
            "sector_union_mask": int(sector_union_mask),
            "covered_sectors": mask_labels(sector_union_mask),
            "sector_coverage_count": int(sector_union_mask.bit_count()),
            "signature_union_count": len(signature_union),
            "signature_union_sha256": int_list_sha256(signature_union),
            "tensor_path_support_sum": support_sum,
            "tensor_path_coefficient_mass_sum": mass_sum,
            "word_triple_multiplicity": normal_word_multiplicity,
            "left_path_swap_count": left_swap_count,
            "right_path_swap_count": right_swap_count,
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in TRIPLE_COLUMNS])

    return rows, np.asarray(table_rows, dtype=np.int64)


def build_payloads() -> dict[str, Any]:
    rewrite_report = load_json(REWRITE_REPORT)
    symbolic_alphabet = load_json(SYMBOLIC_ALPHABET_JSON)
    rewrite_certificate = load_json(SYMBOLIC_REWRITE_CERTIFICATE)
    pentagon_report = load_json(PENTAGON_REPORT)
    pentagon_normal_form = load_json(PENTAGON_NORMAL_FORM)
    pentagon_certificate = load_json(PENTAGON_CERTIFICATE)
    rewrite_tables = np.load(SYMBOLIC_REWRITE_TABLES, allow_pickle=False)
    alphabet_table = np.asarray(rewrite_tables["alphabet_table"], dtype=np.int64)
    membership_matrix = np.asarray(rewrite_tables["alphabet_signature_membership"], dtype=np.int8)
    rule_table = np.asarray(rewrite_tables["rewrite_rule_table"], dtype=np.int64)
    concat_table = np.asarray(rewrite_tables["word_concatenation_rewrite_table"], dtype=np.int64)

    alphabet_rows = symbolic_alphabet["alphabet"]
    binary_rules = symbolic_alphabet["binary_rewrite_rules"]
    triple_rows, triple_table = build_symbolic_triples(alphabet_rows, binary_rules)

    canonical_triple_count = len(set(int(row["canonical_triple_id"]) for row in triple_rows))
    full_sector_count = sum(
        1 for row in triple_rows if int(row["sector_coverage_count"]) == len(OBJECT_LABELS)
    )
    total_word_triples = sum(int(row["word_triple_multiplicity"]) for row in triple_rows)
    full_sector_word_triples = sum(
        int(row["word_triple_multiplicity"])
        for row in triple_rows
        if int(row["sector_coverage_count"]) == len(OBJECT_LABELS)
    )
    max_signature_union = max(int(row["signature_union_count"]) for row in triple_rows)
    min_signature_union = min(int(row["signature_union_count"]) for row in triple_rows)
    max_signature_atom_triples = [
        [int(row["left_atom_id"]), int(row["middle_atom_id"]), int(row["right_atom_id"])]
        for row in triple_rows
        if int(row["signature_union_count"]) == max_signature_union
    ]
    min_signature_atom_triples = [
        [int(row["left_atom_id"]), int(row["middle_atom_id"]), int(row["right_atom_id"])]
        for row in triple_rows
        if int(row["signature_union_count"]) == min_signature_union
    ]
    left_rule_ids = set(int(row[column]) for row in triple_rows for column in (
        "left_path_first_rule_id",
        "left_path_second_rule_id",
        "left_path_third_rule_id",
    ))
    right_rule_ids = set(int(row[column]) for row in triple_rows for column in (
        "right_path_first_rule_id",
        "right_path_second_rule_id",
        "right_path_third_rule_id",
    ))

    symbolic_associativity = {
        "schema": "c985.d20_symbolic_associativity@1",
        "object": "d20",
        "source_symbolic_rewrite_certificate": rewrite_report.get("certificate_sha256"),
        "source_pentagon_certificate": pentagon_report.get("certificate_sha256"),
        "associativity_rule": {
            "left_path_sorting_network": "(01),(12),(01)",
            "right_path_sorting_network": "(12),(01),(12)",
            "normal_form": "sorted_length_three_symbol_word(x_i,x_j,x_k)",
            "pentagon_boundary_comparison": (
                "the symbolic diamond is checked against the certified C985 "
                "top/bottom chain normal form metadata"
            ),
        },
        "h6_sector_order": OBJECT_LABELS,
        "symbolic_triples": triple_rows,
        "summary": {
            "symbolic_triple_count": len(triple_rows),
            "canonical_symbolic_triple_count": canonical_triple_count,
            "noncanonical_symbolic_triple_count": len(triple_rows) - canonical_triple_count,
            "word_triple_multiplicity_per_symbolic_triple": 216,
            "total_normal_word_triple_count": total_word_triples,
            "full_sector_symbolic_triple_count": full_sector_count,
            "full_sector_normal_word_triple_count": full_sector_word_triples,
            "left_path_swap_count": sum(int(row["left_path_swap_count"]) for row in triple_rows),
            "right_path_swap_count": sum(int(row["right_path_swap_count"]) for row in triple_rows),
            "symbolic_triple_sector_coverage_histogram": histogram(
                [int(row["sector_coverage_count"]) for row in triple_rows]
            ),
            "symbolic_triple_signature_union_count_min": min_signature_union,
            "symbolic_triple_signature_union_count_max": max_signature_union,
            "max_signature_union_atom_triples": max_signature_atom_triples,
            "min_signature_union_atom_triples": min_signature_atom_triples,
            "pentagon_top_path_normal_form": pentagon_normal_form.get("top_path_normal_form"),
            "pentagon_bottom_path_normal_form": pentagon_normal_form.get("bottom_path_normal_form"),
        },
    }

    checks = {
        "symbolic_rewrite_report_certified": rewrite_report.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "symbolic_rewrite_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED",
        "pentagon_report_certified": pentagon_report.get("status")
        == "C985_PENTAGON_CHAIN_NORMAL_FORM_CERTIFIED",
        "pentagon_certificate_certified": pentagon_certificate.get("status")
        == "C985_PENTAGON_CHAIN_NORMAL_FORM_CERTIFIED",
        "alphabet_table_shape_is_6_by_9": tuple(alphabet_table.shape) == (6, 9),
        "alphabet_signature_membership_shape_is_6_by_233": tuple(membership_matrix.shape) == (6, 233),
        "binary_rewrite_table_shape_is_36_by_22": tuple(rule_table.shape) == (36, 22),
        "word_concatenation_table_shape_is_1296_by_13": tuple(concat_table.shape) == (1296, 13),
        "symbolic_triple_count_is_216": len(triple_rows) == 216,
        "canonical_symbolic_triple_count_is_56": canonical_triple_count == 56,
        "noncanonical_symbolic_triple_count_is_160": len(triple_rows) - canonical_triple_count == 160,
        "all_left_reductions_equal_right_reductions": all(
            int(row["left_final_matches_right_final"]) == 1 for row in triple_rows
        ),
        "all_reductions_match_direct_sorted_normal_form": all(
            int(row["matches_direct_sorted_normal_form"]) == 1 for row in triple_rows
        ),
        "each_symbolic_triple_has_216_normal_word_lifts": all(
            int(row["word_triple_multiplicity"]) == 216 for row in triple_rows
        ),
        "normal_word_triple_count_is_46656": total_word_triples == 46656,
        "full_sector_symbolic_triple_count_is_78": full_sector_count == 78,
        "full_sector_normal_word_triple_count_is_16848": full_sector_word_triples == 16848,
        "symbolic_triple_sector_coverage_histogram_is_6_three_30_four_102_five_78_six": histogram(
            [int(row["sector_coverage_count"]) for row in triple_rows]
        )
        == [
            {"value": 3, "count": 6},
            {"value": 4, "count": 30},
            {"value": 5, "count": 102},
            {"value": 6, "count": 78},
        ],
        "symbolic_triple_signature_union_count_max_is_185": max_signature_union == 185,
        "symbolic_triple_signature_union_count_min_is_53": min_signature_union == 53,
        "max_signature_union_triples_are_atoms_7_12_19_permutations": max_signature_atom_triples
        == [
            [7, 12, 19],
            [7, 19, 12],
            [12, 7, 19],
            [12, 19, 7],
            [19, 7, 12],
            [19, 12, 7],
        ],
        "min_signature_union_triple_is_atom_11_repeated": min_signature_atom_triples == [[11, 11, 11]],
        "left_and_right_paths_use_all_36_binary_rules": len(left_rule_ids) == 36 and len(right_rule_ids) == 36,
        "left_and_right_paths_have_equal_swap_counts": sum(int(row["left_path_swap_count"]) for row in triple_rows)
        == sum(int(row["right_path_swap_count"]) for row in triple_rows)
        == 270,
        "pentagon_top_and_bottom_normal_forms_match": pentagon_normal_form.get("top_path_normal_form")
        == pentagon_normal_form.get("bottom_path_normal_form"),
        "pentagon_normal_form_is_typed_length_four_chain": pentagon_normal_form.get("top_path_normal_form")
        == "typed_length_four_chain(x0,x1,x2,x3,x4)",
        "pentagon_report_exact_chain_count_matches": pentagon_report.get("witness", {})
        .get("address_counts", {})
        .get("exact_length_four_chain_count")
        == 16837352591360,
    }

    witness = {
        "symbolic_triple_count": len(triple_rows),
        "canonical_symbolic_triple_count": canonical_triple_count,
        "noncanonical_symbolic_triple_count": len(triple_rows) - canonical_triple_count,
        "word_triple_multiplicity_per_symbolic_triple": 216,
        "total_normal_word_triple_count": total_word_triples,
        "full_sector_symbolic_triple_count": full_sector_count,
        "full_sector_normal_word_triple_count": full_sector_word_triples,
        "left_path_swap_count": sum(int(row["left_path_swap_count"]) for row in triple_rows),
        "right_path_swap_count": sum(int(row["right_path_swap_count"]) for row in triple_rows),
        "left_path_distinct_binary_rule_count": len(left_rule_ids),
        "right_path_distinct_binary_rule_count": len(right_rule_ids),
        "symbolic_triple_sector_coverage_histogram": symbolic_associativity["summary"][
            "symbolic_triple_sector_coverage_histogram"
        ],
        "symbolic_triple_signature_union_count_min": min_signature_union,
        "symbolic_triple_signature_union_count_max": max_signature_union,
        "max_signature_union_atom_triples": max_signature_atom_triples,
        "min_signature_union_atom_triples": min_signature_atom_triples,
        "symbolic_associativity_normal_form": "sorted_length_three_symbol_word(x_i,x_j,x_k)",
        "pentagon_chain_normal_form": pentagon_normal_form.get("top_path_normal_form"),
        "pentagon_exact_length_four_chain_count": pentagon_report.get("witness", {})
        .get("address_counts", {})
        .get("exact_length_four_chain_count"),
        "triple_associativity_table_sha256": sha_array(triple_table),
        "rewrite_rule_table_sha256": sha_array(rule_table),
        "alphabet_table_sha256": sha_array(alphabet_table),
        "word_concatenation_rewrite_table_sha256": sha_array(concat_table),
    }

    certificate = {
        "schema": "c985.d20_symbolic_associativity_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_SYMBOLIC_ASSOCIATIVITY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "all 216 ordered length-three symbolic words reduce to sorted normal form by both binary-rewrite paths",
            "the two sorting-network paths use all 36 binary rewrite rules and have equal swap total",
            "the symbolic triples account for 46,656 lifted normal-form word triples by multiplicity",
            "sector coverage and relation-signature coverage are preserved by both reduction paths",
            "the symbolic associativity normal form is compared with the certified C985 pentagon chain normal form metadata",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_symbolic_associativity@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The certified six-symbol d20 rewrite alphabet has a length-three "
            "associativity diamond: both binary-rewrite reduction paths send every "
            "ordered symbolic triple to the same sorted normal form while preserving "
            "sector, signature, and tensor-mass readouts."
        ),
        "stage_protocol": {
            "draft": "use certified binary symbolic rewrites and certified C985 pentagon normal-form metadata",
            "witness": "materialize all 216 ordered symbolic triples and both three-step reduction paths",
            "coherence": "check left and right reductions agree, match direct sorted normal form, and preserve readout invariants",
            "closure": "certify symbolic associativity at the d20 readout level without asserting a new C985 monoidal product",
            "emit": "emit length-three associativity JSON/CSV/NPZ, certificate, report, and next hyperbolic target",
        },
        "inputs": {
            "symbolic_rewrite_report": input_entry(
                REWRITE_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_JSON),
            "symbolic_rewrite_tables": input_entry(SYMBOLIC_REWRITE_TABLES),
            "symbolic_rewrite_certificate": input_entry(SYMBOLIC_REWRITE_CERTIFICATE),
            "pentagon_report": input_entry(
                PENTAGON_REPORT,
                {
                    "status": pentagon_report.get("status"),
                    "certificate_sha256": pentagon_report.get("certificate_sha256"),
                },
            ),
            "pentagon_normal_form": input_entry(PENTAGON_NORMAL_FORM),
            "pentagon_certificate": input_entry(PENTAGON_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "symbolic_associativity": relpath(OUT_DIR / "symbolic_associativity.json"),
            "symbolic_associativity_csv": relpath(OUT_DIR / "symbolic_associativity.csv"),
            "symbolic_associativity_tables": relpath(OUT_DIR / "symbolic_associativity_tables.npz"),
            "symbolic_associativity_certificate": relpath(OUT_DIR / "symbolic_associativity_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "length-three symbolic associativity for the six d20 normal-form atoms",
                "left and right binary-rewrite reduction paths agree on all 216 ordered triples",
                "46,656 lifted normal-form word triples accounted for by certified multiplicity",
                "sector-mask, relation-signature, tensor-support, and tensor-mass invariance under triple normalization",
                "readout-level comparison with the certified C985 pentagon chain normal form",
            ],
            "does_not_certify_because_not_required": [
                "a new associator or pentagon proof for C985 beyond the existing certificate",
                "a confluent rewrite system for arbitrary-length symbolic words",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Use the length-three symbolic normal forms as 56 nodes of a "
            "higher-order rewrite complex, then measure its hyperbolicity and "
            "compare its geodesics with the certified d20 Poincare chart."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_symbolic_associativity_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified binary symbolic rewrite rules and pentagon normal-form metadata",
            "materialize every ordered length-three symbolic word",
            "reduce each triple through left and right binary sorting-network paths",
            "compare both reductions with direct sorted normal form",
            "check sector, signature, support, mass, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "symbolic_associativity": symbolic_associativity,
        "symbolic_associativity_csv": csv_text(TRIPLE_COLUMNS, triple_rows),
        "symbolic_associativity_table": triple_table,
        "symbolic_associativity_certificate": certificate,
        "report": report,
        "manifest": manifest,
    }


def update_index(report: dict[str, Any]) -> None:
    if INDEX_PATH.exists():
        index_payload = load_json(INDEX_PATH)
        obligations = [
            row
            for row in index_payload.get("obligations", [])
            if isinstance(row, dict) and row.get("id") != THEOREM_ID
        ]
        schema = index_payload.get("schema", "d20.proof_obligation_registry.source_drop")
    else:
        obligations = []
        schema = "d20.proof_obligation_registry.source_drop"
    obligations.append(
        {
            "id": THEOREM_ID,
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
            "report_sha256": report["certificate_sha256"],
            "status": report["status"],
        }
    )
    updated = {
        "schema": schema,
        "status": "D20_PROOF_OBLIGATION_REGISTRY_BUILT",
        "obligation_count": len(obligations),
        "obligations": sorted(obligations, key=lambda row: row["id"]),
    }
    updated["registry_sha256"] = self_hash(updated, "registry_sha256")
    write_json(INDEX_PATH, updated)


def write_payloads(payloads: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "symbolic_associativity.json", payloads["symbolic_associativity"])
    (OUT_DIR / "symbolic_associativity.csv").write_text(
        payloads["symbolic_associativity_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "symbolic_associativity_tables.npz",
        symbolic_associativity_table=payloads["symbolic_associativity_table"],
    )
    write_json(
        OUT_DIR / "symbolic_associativity_certificate.json",
        payloads["symbolic_associativity_certificate"],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    witness = payloads["report"]["witness"]
    print(
        json.dumps(
            {
                "status": payloads["report"]["status"],
                "all_checks_pass": payloads["report"]["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": payloads["report"]["certificate_sha256"],
                "symbolic_triple_count": witness["symbolic_triple_count"],
                "canonical_symbolic_triple_count": witness["canonical_symbolic_triple_count"],
                "total_normal_word_triple_count": witness["total_normal_word_triple_count"],
                "full_sector_symbolic_triple_count": witness["full_sector_symbolic_triple_count"],
                "symbolic_triple_signature_union_count_max": witness[
                    "symbolic_triple_signature_union_count_max"
                ],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
