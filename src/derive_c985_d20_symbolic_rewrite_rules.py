from __future__ import annotations

import itertools
import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_hyperbolic_boundary_graph import (
        atom_signature_sets,
        signature_class_ids,
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
    from derive_c985_d20_hyperbolic_boundary_graph import (
        atom_signature_sets,
        signature_class_ids,
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


THEOREM_ID = "c985_d20_symbolic_rewrite_rules"
STATUS = "C985_D20_SYMBOLIC_REWRITE_RULES_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

NORMAL_WORD_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_normal_form_words"
ATLAS_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_boundary_invariant_atlas"
GEOMETRY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_tensor_geometry_invariants"

NORMAL_WORD_REPORT = NORMAL_WORD_DIR / "report.json"
NORMAL_WORDS_JSON = NORMAL_WORD_DIR / "normal_form_words.json"
NORMAL_WORD_TABLES = NORMAL_WORD_DIR / "normal_form_word_tables.npz"
NORMAL_WORD_CERTIFICATE = NORMAL_WORD_DIR / "normal_form_words_certificate.json"
ATLAS_REPORT = ATLAS_DIR / "report.json"
ATLAS_JSON = ATLAS_DIR / "d20_boundary_invariant_atlas.json"
GEOMETRY_REPORT = GEOMETRY_DIR / "report.json"
RELATION_GEOMETRY_SIGNATURES = GEOMETRY_DIR / "relation_geometry_signatures.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_symbolic_rewrite_rules.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_symbolic_rewrite_rules.py"

SYMBOL_NAMES = ["x0", "x1", "x2", "x3", "x4", "x5"]

ALPHABET_COLUMNS = [
    "symbol_id",
    "atom_id",
    "sector_mask",
    "missing_sector_mask",
    "sector_count",
    "signature_class_count",
    "tensor_path_support",
    "tensor_path_coefficient_mass",
    "normal_word_count",
]

RULE_COLUMNS = [
    "rule_id",
    "left_symbol_id",
    "right_symbol_id",
    "left_atom_id",
    "right_atom_id",
    "canonical_left_symbol_id",
    "canonical_right_symbol_id",
    "canonical_left_atom_id",
    "canonical_right_atom_id",
    "canonical_pair_id",
    "is_swap_rule",
    "source_sector_union_mask",
    "canonical_sector_union_mask",
    "sector_coverage_count",
    "sector_overlap_count",
    "missing_sector_count",
    "signature_union_count",
    "signature_intersection_count",
    "signature_symmetric_difference_count",
    "tensor_path_support_sum",
    "tensor_path_coefficient_mass_sum",
    "word_concatenation_count",
]

CONCAT_COLUMNS = [
    "concat_id",
    "left_word_id",
    "right_word_id",
    "left_symbol_id",
    "right_symbol_id",
    "rule_id",
    "canonical_pair_id",
    "canonical_left_symbol_id",
    "canonical_right_symbol_id",
    "sector_coverage_count",
    "signature_union_count",
    "tensor_path_support_sum",
    "tensor_path_coefficient_mass_sum",
]


def csv_text(headers: list[str], rows: list[dict[str, Any]]) -> str:
    out = [",".join(headers)]
    for row in rows:
        out.append(",".join(str(row[column]) for column in headers))
    return "\n".join(out) + "\n"


def histogram(values: list[int]) -> list[dict[str, int]]:
    counts: dict[int, int] = {}
    for value in values:
        counts[int(value)] = counts.get(int(value), 0) + 1
    return [
        {"value": int(value), "count": int(count)}
        for value, count in sorted(counts.items())
    ]


def atom_label(atlas: dict[str, Any], atom_id: int) -> str:
    return "{" + ",".join(atlas["atom_rows"][atom_id]["h6_triple"]) + "}"


def sector_mask(labels: list[str]) -> int:
    mask = 0
    for label in labels:
        mask |= 1 << OBJECT_LABELS.index(label)
    return int(mask)


def mask_labels(mask: int) -> list[str]:
    return [
        label
        for index, label in enumerate(OBJECT_LABELS)
        if int(mask) & (1 << index)
    ]


def int_list_sha256(values: list[int] | set[int]) -> str:
    return sha_array(np.asarray(sorted(int(value) for value in values), dtype=np.int64))


def build_alphabet(
    atlas: dict[str, Any],
    normal_words: dict[str, Any],
    signature_sets: list[set[int]],
    signature_class_total: int,
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    word_rows = normal_words["normal_form_words"]
    atom_rows = normal_words["unique_cycle_atoms"]
    atom_to_word_ids: dict[int, list[int]] = {}
    for row in word_rows:
        atom_to_word_ids.setdefault(int(row["atom_id"]), []).append(int(row["word_id"]))

    alphabet_rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    membership_rows: list[np.ndarray] = []
    for symbol_id, row in enumerate(sorted(atom_rows, key=lambda item: int(item["atom_id"]))):
        atom_id = int(row["atom_id"])
        atom = atlas["atom_rows"][atom_id]
        signatures = sorted(signature_sets[atom_id])
        mask = sector_mask(atom["h6_triple"])
        missing_mask = ((1 << len(OBJECT_LABELS)) - 1) ^ mask
        membership = np.zeros(signature_class_total, dtype=np.int8)
        membership[np.asarray(signatures, dtype=np.int64)] = 1
        alphabet_row = {
            "symbol_id": symbol_id,
            "symbol": SYMBOL_NAMES[symbol_id],
            "atom_id": atom_id,
            "atom_label": atom_label(atlas, atom_id),
            "sector_path": "|".join(atom["h6_triple"]),
            "sector_mask": int(mask),
            "covered_sectors": mask_labels(mask),
            "missing_sector_mask": int(missing_mask),
            "missing_sectors": mask_labels(missing_mask),
            "sector_count": int(mask.bit_count()),
            "signature_class_count": len(signatures),
            "signature_class_ids": signatures,
            "signature_class_sha256": int_list_sha256(signatures),
            "tensor_path_support": int(row["tensor_path_support_from_cubes"]),
            "tensor_path_coefficient_mass": int(row["tensor_path_coefficient_mass_from_cubes"]),
            "normal_word_count": len(atom_to_word_ids[atom_id]),
            "normal_word_ids": sorted(atom_to_word_ids[atom_id]),
        }
        alphabet_rows.append(alphabet_row)
        table_rows.append([int(alphabet_row[column]) for column in ALPHABET_COLUMNS])
        membership_rows.append(membership)

    return (
        alphabet_rows,
        np.asarray(table_rows, dtype=np.int64),
        np.vstack(membership_rows).astype(np.int8),
    )


def build_rewrite_rules(
    alphabet_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[tuple[int, int], dict[str, Any]]]:
    canonical_pair_ids: dict[tuple[int, int], int] = {}
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    lookup: dict[tuple[int, int], dict[str, Any]] = {}
    full_mask = (1 << len(OBJECT_LABELS)) - 1

    for left, right in itertools.product(alphabet_rows, repeat=2):
        left_id = int(left["symbol_id"])
        right_id = int(right["symbol_id"])
        canonical_symbol_ids = tuple(sorted((left_id, right_id)))
        if canonical_symbol_ids not in canonical_pair_ids:
            canonical_pair_ids[canonical_symbol_ids] = len(canonical_pair_ids)
        canonical_left = alphabet_rows[canonical_symbol_ids[0]]
        canonical_right = alphabet_rows[canonical_symbol_ids[1]]

        left_signatures = set(left["signature_class_ids"])
        right_signatures = set(right["signature_class_ids"])
        signature_union = left_signatures | right_signatures
        signature_intersection = left_signatures & right_signatures
        source_union_mask = int(left["sector_mask"]) | int(right["sector_mask"])
        canonical_union_mask = int(canonical_left["sector_mask"]) | int(canonical_right["sector_mask"])
        overlap_mask = int(left["sector_mask"]) & int(right["sector_mask"])
        support_sum = int(left["tensor_path_support"]) + int(right["tensor_path_support"])
        mass_sum = int(left["tensor_path_coefficient_mass"]) + int(
            right["tensor_path_coefficient_mass"]
        )
        row = {
            "rule_id": len(rows),
            "lhs": f"{left['symbol']} {right['symbol']}",
            "rhs": f"{canonical_left['symbol']} {canonical_right['symbol']}",
            "left_symbol_id": left_id,
            "right_symbol_id": right_id,
            "left_atom_id": int(left["atom_id"]),
            "right_atom_id": int(right["atom_id"]),
            "canonical_left_symbol_id": int(canonical_left["symbol_id"]),
            "canonical_right_symbol_id": int(canonical_right["symbol_id"]),
            "canonical_left_atom_id": int(canonical_left["atom_id"]),
            "canonical_right_atom_id": int(canonical_right["atom_id"]),
            "canonical_pair_id": canonical_pair_ids[canonical_symbol_ids],
            "is_swap_rule": int((left_id, right_id) != canonical_symbol_ids),
            "source_sector_union_mask": source_union_mask,
            "canonical_sector_union_mask": canonical_union_mask,
            "sector_coverage_count": int(source_union_mask.bit_count()),
            "covered_sectors": mask_labels(source_union_mask),
            "sector_overlap_count": int(overlap_mask.bit_count()),
            "missing_sector_count": int((full_mask ^ source_union_mask).bit_count()),
            "signature_union_count": len(signature_union),
            "signature_intersection_count": len(signature_intersection),
            "signature_symmetric_difference_count": len(signature_union - signature_intersection),
            "signature_union_sha256": int_list_sha256(signature_union),
            "tensor_path_support_sum": support_sum,
            "tensor_path_coefficient_mass_sum": mass_sum,
            "word_concatenation_count": int(left["normal_word_count"]) * int(right["normal_word_count"]),
            "preservation_checks": {
                "sector_union_preserved": source_union_mask == canonical_union_mask,
                "signature_union_preserved": int_list_sha256(signature_union)
                == int_list_sha256(
                    set(canonical_left["signature_class_ids"])
                    | set(canonical_right["signature_class_ids"])
                ),
                "tensor_support_sum_preserved": support_sum
                == int(canonical_left["tensor_path_support"]) + int(canonical_right["tensor_path_support"]),
                "tensor_mass_sum_preserved": mass_sum
                == int(canonical_left["tensor_path_coefficient_mass"])
                + int(canonical_right["tensor_path_coefficient_mass"]),
            },
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in RULE_COLUMNS])
        lookup[(left_id, right_id)] = row

    return rows, np.asarray(table_rows, dtype=np.int64), lookup


def build_word_concatenations(
    normal_words: dict[str, Any],
    atom_to_symbol: dict[int, int],
    rule_lookup: dict[tuple[int, int], dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray]:
    rows: list[dict[str, Any]] = []
    table_rows: list[list[int]] = []
    word_rows = normal_words["normal_form_words"]
    for left, right in itertools.product(word_rows, repeat=2):
        left_word_id = int(left["word_id"])
        right_word_id = int(right["word_id"])
        left_symbol_id = atom_to_symbol[int(left["atom_id"])]
        right_symbol_id = atom_to_symbol[int(right["atom_id"])]
        rule = rule_lookup[(left_symbol_id, right_symbol_id)]
        support_sum = int(left["tensor_path_support"]) + int(right["tensor_path_support"])
        mass_sum = int(left["tensor_path_coefficient_mass"]) + int(
            right["tensor_path_coefficient_mass"]
        )
        row = {
            "concat_id": len(rows),
            "left_word_id": left_word_id,
            "right_word_id": right_word_id,
            "left_symbol_id": left_symbol_id,
            "right_symbol_id": right_symbol_id,
            "rule_id": int(rule["rule_id"]),
            "canonical_pair_id": int(rule["canonical_pair_id"]),
            "canonical_left_symbol_id": int(rule["canonical_left_symbol_id"]),
            "canonical_right_symbol_id": int(rule["canonical_right_symbol_id"]),
            "sector_coverage_count": int(rule["sector_coverage_count"]),
            "signature_union_count": int(rule["signature_union_count"]),
            "tensor_path_support_sum": support_sum,
            "tensor_path_coefficient_mass_sum": mass_sum,
        }
        rows.append(row)
        table_rows.append([int(row[column]) for column in CONCAT_COLUMNS])
    return rows, np.asarray(table_rows, dtype=np.int64)


def build_payloads() -> dict[str, Any]:
    normal_report = load_json(NORMAL_WORD_REPORT)
    normal_words = load_json(NORMAL_WORDS_JSON)
    normal_certificate = load_json(NORMAL_WORD_CERTIFICATE)
    atlas_report = load_json(ATLAS_REPORT)
    atlas = load_json(ATLAS_JSON)
    geometry_report = load_json(GEOMETRY_REPORT)
    normal_tables = np.load(NORMAL_WORD_TABLES, allow_pickle=False)
    normal_word_table = np.asarray(normal_tables["normal_form_word_table"], dtype=np.int64)
    normal_atom_table = np.asarray(normal_tables["normal_form_atom_table"], dtype=np.int64)
    relation_npz = np.load(RELATION_GEOMETRY_SIGNATURES, allow_pickle=False)
    relation_records = np.asarray(relation_npz["relation_records"], dtype=np.int64)
    class_ids = signature_class_ids(relation_records)
    signature_class_total = int(len(np.unique(class_ids)))
    signature_sets = atom_signature_sets(atlas, relation_records, class_ids)

    alphabet_rows, alphabet_table, membership_matrix = build_alphabet(
        atlas,
        normal_words,
        signature_sets,
        signature_class_total,
    )
    rule_rows, rule_table, rule_lookup = build_rewrite_rules(alphabet_rows)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"])
        for row in alphabet_rows
    }
    concat_rows, concat_table = build_word_concatenations(
        normal_words,
        atom_to_symbol,
        rule_lookup,
    )

    full_mask = (1 << len(OBJECT_LABELS)) - 1
    alphabet_sector_union_mask = 0
    alphabet_signature_union: set[int] = set()
    for row in alphabet_rows:
        alphabet_sector_union_mask |= int(row["sector_mask"])
        alphabet_signature_union.update(int(x) for x in row["signature_class_ids"])

    rule_pair_histogram: dict[tuple[int, int], int] = {}
    for row in concat_rows:
        pair = (int(row["left_symbol_id"]), int(row["right_symbol_id"]))
        rule_pair_histogram[pair] = rule_pair_histogram.get(pair, 0) + 1

    max_signature_union = max(int(row["signature_union_count"]) for row in rule_rows)
    max_signature_rule_atom_pairs = [
        [int(row["left_atom_id"]), int(row["right_atom_id"])]
        for row in rule_rows
        if int(row["signature_union_count"]) == max_signature_union
    ]
    full_sector_rule_count = sum(
        1 for row in rule_rows if int(row["source_sector_union_mask"]) == full_mask
    )
    full_sector_concat_count = sum(
        1 for row in concat_rows if int(row["sector_coverage_count"]) == len(OBJECT_LABELS)
    )
    canonical_pair_count = len(set(int(row["canonical_pair_id"]) for row in rule_rows))

    symbolic_alphabet = {
        "schema": "c985.d20_symbolic_alphabet_rewrites@1",
        "object": "d20",
        "source_normal_form_words_certificate": normal_report.get("certificate_sha256"),
        "source_tensor_geometry_certificate": geometry_report.get("certificate_sha256"),
        "alphabet_rule": {
            "letters": "six symbols x0..x5, one for each certified normal-form cycle atom",
            "binary_rewrite": "ordered letter pairs normalize to lexicographically sorted atom-symbol pairs",
            "preserved_data": [
                "H6 sector union",
                "relation-signature union",
                "tensor path support sum with multiplicity",
                "tensor path coefficient mass sum with multiplicity",
            ],
        },
        "h6_sector_order": OBJECT_LABELS,
        "alphabet": alphabet_rows,
        "binary_rewrite_rules": rule_rows,
        "summary": {
            "alphabet_symbol_count": len(alphabet_rows),
            "covered_h6_sectors": mask_labels(alphabet_sector_union_mask),
            "alphabet_signature_union_count": len(alphabet_signature_union),
            "signature_class_total": signature_class_total,
            "binary_rewrite_rule_count": len(rule_rows),
            "canonical_binary_pair_count": canonical_pair_count,
            "nontrivial_swap_rule_count": sum(int(row["is_swap_rule"]) for row in rule_rows),
            "word_concatenation_rewrite_count": len(concat_rows),
            "full_sector_binary_rule_count": full_sector_rule_count,
            "full_sector_word_concatenation_count": full_sector_concat_count,
            "binary_rule_sector_coverage_histogram": histogram(
                [int(row["sector_coverage_count"]) for row in rule_rows]
            ),
            "binary_rule_sector_overlap_histogram": histogram(
                [int(row["sector_overlap_count"]) for row in rule_rows]
            ),
            "binary_rule_signature_union_count_min": min(
                int(row["signature_union_count"]) for row in rule_rows
            ),
            "binary_rule_signature_union_count_max": max_signature_union,
            "max_signature_union_rule_atom_pairs": max_signature_rule_atom_pairs,
        },
    }

    word_concatenation_rewrites = {
        "schema": "c985.d20_word_concatenation_rewrites@1",
        "object": "d20",
        "word_source": "the 36 certified d20 normal-form words",
        "rewrite_target": "six-symbol alphabet binary normal forms",
        "word_concatenation_rewrites": concat_rows,
        "summary": symbolic_alphabet["summary"],
    }

    checks = {
        "normal_form_words_report_certified": normal_report.get("status")
        == "C985_D20_NORMAL_FORM_WORDS_CERTIFIED",
        "normal_form_words_certificate_certified": normal_certificate.get("status")
        == "C985_D20_NORMAL_FORM_WORDS_CERTIFIED",
        "boundary_atlas_report_certified": atlas_report.get("status")
        == "C985_D20_BOUNDARY_INVARIANT_ATLAS_CERTIFIED",
        "tensor_geometry_report_certified": geometry_report.get("status")
        == "C985_TENSOR_GEOMETRY_INVARIANTS_CERTIFIED",
        "normal_word_table_shape_is_36_by_13": tuple(normal_word_table.shape) == (36, 13),
        "normal_atom_table_shape_is_6_by_8": tuple(normal_atom_table.shape) == (6, 8),
        "alphabet_symbol_count_is_6": len(alphabet_rows) == 6,
        "alphabet_symbols_have_six_normal_words_each": all(
            int(row["normal_word_count"]) == 6 for row in alphabet_rows
        ),
        "alphabet_signature_membership_shape_is_6_by_233": tuple(membership_matrix.shape) == (6, 233),
        "alphabet_covers_all_six_h6_sectors": alphabet_sector_union_mask == full_mask,
        "alphabet_signature_union_count_is_221": len(alphabet_signature_union) == 221,
        "binary_rewrite_rule_count_is_36": len(rule_rows) == 36,
        "canonical_binary_pair_count_is_21": canonical_pair_count == 21,
        "nontrivial_swap_rule_count_is_15": sum(int(row["is_swap_rule"]) for row in rule_rows) == 15,
        "word_concatenation_rewrite_count_is_1296": len(concat_rows) == 1296,
        "each_symbol_pair_has_36_word_concatenations": sorted(rule_pair_histogram.values()) == [36] * 36,
        "binary_sector_coverage_histogram_is_6_three_10_four_18_five_2_six": histogram(
            [int(row["sector_coverage_count"]) for row in rule_rows]
        )
        == [
            {"value": 3, "count": 6},
            {"value": 4, "count": 10},
            {"value": 5, "count": 18},
            {"value": 6, "count": 2},
        ],
        "binary_sector_overlap_histogram_is_2_zero_18_one_10_two_6_three": histogram(
            [int(row["sector_overlap_count"]) for row in rule_rows]
        )
        == [
            {"value": 0, "count": 2},
            {"value": 1, "count": 18},
            {"value": 2, "count": 10},
            {"value": 3, "count": 6},
        ],
        "full_sector_binary_rule_count_is_2": full_sector_rule_count == 2,
        "full_sector_word_concatenation_count_is_72": full_sector_concat_count == 72,
        "binary_rule_signature_union_count_max_is_155": max_signature_union == 155,
        "max_signature_union_rules_are_atoms_7_and_12": max_signature_rule_atom_pairs
        == [[7, 12], [12, 7]],
        "all_rewrite_rules_preserve_sector_union": all(
            row["preservation_checks"]["sector_union_preserved"] for row in rule_rows
        ),
        "all_rewrite_rules_preserve_signature_union": all(
            row["preservation_checks"]["signature_union_preserved"] for row in rule_rows
        ),
        "all_rewrite_rules_preserve_tensor_support_sum": all(
            row["preservation_checks"]["tensor_support_sum_preserved"] for row in rule_rows
        ),
        "all_rewrite_rules_preserve_tensor_mass_sum": all(
            row["preservation_checks"]["tensor_mass_sum_preserved"] for row in rule_rows
        ),
        "word_concatenations_map_to_existing_rules": all(
            (int(row["left_symbol_id"]), int(row["right_symbol_id"])) in rule_lookup
            for row in concat_rows
        ),
        "word_concatenation_signature_counts_match_rules": all(
            int(row["signature_union_count"])
            == int(rule_lookup[(int(row["left_symbol_id"]), int(row["right_symbol_id"]))]["signature_union_count"])
            for row in concat_rows
        ),
        "word_concatenation_tensor_support_sums_match_rules": all(
            int(row["tensor_path_support_sum"])
            == int(rule_lookup[(int(row["left_symbol_id"]), int(row["right_symbol_id"]))]["tensor_path_support_sum"])
            for row in concat_rows
        ),
        "word_concatenation_tensor_mass_sums_match_rules": all(
            int(row["tensor_path_coefficient_mass_sum"])
            == int(
                rule_lookup[(int(row["left_symbol_id"]), int(row["right_symbol_id"]))][
                    "tensor_path_coefficient_mass_sum"
                ]
            )
            for row in concat_rows
        ),
    }

    witness = {
        "alphabet_symbol_count": len(alphabet_rows),
        "alphabet_atom_ids": [int(row["atom_id"]) for row in alphabet_rows],
        "covered_h6_sectors": mask_labels(alphabet_sector_union_mask),
        "signature_class_total": signature_class_total,
        "alphabet_signature_union_count": len(alphabet_signature_union),
        "binary_rewrite_rule_count": len(rule_rows),
        "canonical_binary_pair_count": canonical_pair_count,
        "nontrivial_swap_rule_count": sum(int(row["is_swap_rule"]) for row in rule_rows),
        "word_concatenation_rewrite_count": len(concat_rows),
        "full_sector_binary_rule_count": full_sector_rule_count,
        "full_sector_word_concatenation_count": full_sector_concat_count,
        "binary_rule_sector_coverage_histogram": symbolic_alphabet["summary"][
            "binary_rule_sector_coverage_histogram"
        ],
        "binary_rule_sector_overlap_histogram": symbolic_alphabet["summary"][
            "binary_rule_sector_overlap_histogram"
        ],
        "binary_rule_signature_union_count_min": symbolic_alphabet["summary"][
            "binary_rule_signature_union_count_min"
        ],
        "binary_rule_signature_union_count_max": max_signature_union,
        "max_signature_union_rule_atom_pairs": max_signature_rule_atom_pairs,
        "alphabet_table_sha256": sha_array(alphabet_table),
        "alphabet_signature_membership_sha256": sha_array(membership_matrix),
        "rewrite_rule_table_sha256": sha_array(rule_table),
        "word_concatenation_rewrite_table_sha256": sha_array(concat_table),
        "normal_word_table_sha256": sha_array(normal_word_table),
        "normal_atom_table_sha256": sha_array(normal_atom_table),
    }

    certificate = {
        "schema": "c985.d20_symbolic_rewrite_rules_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_SYMBOLIC_REWRITE_RULES_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the six normal-form atoms define a symbolic alphabet x0..x5",
            "all 36 ordered binary letter concatenations normalize to 21 canonical atom pairs",
            "the normalizer preserves H6 sector unions and relation-signature unions",
            "the normalizer preserves tensor support and coefficient mass with word multiplicity",
            "all 1,296 ordered normal-form word concatenations map through the six-letter rewrite table",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_symbolic_rewrite_rules@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The six certified d20 normal-form atoms form a symbolic alphabet whose "
            "binary concatenations admit a deterministic rewrite normalizer that "
            "preserves H6 sector coverage, relation-signature unions, and "
            "tensor-sector support/mass with multiplicity."
        ),
        "stage_protocol": {
            "draft": "use the certified normal-form word atoms as six alphabet letters",
            "witness": "materialize all binary letter rules and all 36x36 word concatenation rewrites",
            "coherence": "check canonicalization preserves sector masks, signature unions, and tensor support/mass sums",
            "closure": "certify a d20 symbolic rewrite readout without asserting a new categorical product",
            "emit": "emit alphabet/rewrite JSON, CSV, NPZ tables, certificate, report, and next deepening target",
        },
        "inputs": {
            "normal_form_words_report": input_entry(
                NORMAL_WORD_REPORT,
                {
                    "status": normal_report.get("status"),
                    "certificate_sha256": normal_report.get("certificate_sha256"),
                },
            ),
            "normal_form_words": input_entry(NORMAL_WORDS_JSON),
            "normal_form_word_tables": input_entry(NORMAL_WORD_TABLES),
            "normal_form_words_certificate": input_entry(NORMAL_WORD_CERTIFICATE),
            "boundary_atlas_report": input_entry(
                ATLAS_REPORT,
                {
                    "status": atlas_report.get("status"),
                    "certificate_sha256": atlas_report.get("certificate_sha256"),
                },
            ),
            "boundary_atlas": input_entry(ATLAS_JSON),
            "tensor_geometry_report": input_entry(
                GEOMETRY_REPORT,
                {
                    "status": geometry_report.get("status"),
                    "certificate_sha256": geometry_report.get("certificate_sha256"),
                },
            ),
            "relation_geometry_signatures": input_entry(RELATION_GEOMETRY_SIGNATURES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "symbolic_alphabet": relpath(OUT_DIR / "symbolic_alphabet.json"),
            "symbolic_alphabet_csv": relpath(OUT_DIR / "symbolic_alphabet.csv"),
            "rewrite_rules_csv": relpath(OUT_DIR / "rewrite_rules.csv"),
            "word_concatenation_rewrites": relpath(OUT_DIR / "word_concatenation_rewrites.json"),
            "word_concatenation_rewrites_csv": relpath(OUT_DIR / "word_concatenation_rewrites.csv"),
            "symbolic_rewrite_tables": relpath(OUT_DIR / "symbolic_rewrite_tables.npz"),
            "symbolic_rewrite_certificate": relpath(OUT_DIR / "symbolic_rewrite_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "six-symbol alphabet from the certified normal-form atoms",
                "36 binary letter rewrite rules and 21 canonical unordered atom-pair normal forms",
                "1,296 normal-form word concatenation rewrites through the six-symbol table",
                "sector-mask, relation-signature, tensor-support, and tensor-mass preservation under canonicalization",
            ],
            "does_not_certify_because_not_required": [
                "a new monoidal product on C985 objects",
                "a confluent rewrite system for arbitrary-length symbolic words",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Extend the binary rewrite normalizer to length-three symbolic words, "
            "then compare associativity of the rewrite normal forms with the "
            "certified pentagon chain normal form."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_symbolic_rewrite_rules_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load the certified d20 normal-form words and tensor geometry signature records",
            "construct one alphabet symbol for each certified normal-form cycle atom",
            "materialize every ordered binary symbol rewrite and every ordered word-pair rewrite",
            "recompute sector masks, signature unions, support sums, and mass sums",
            "check rewrite preservation and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "symbolic_alphabet": symbolic_alphabet,
        "symbolic_alphabet_csv": csv_text(ALPHABET_COLUMNS, alphabet_rows),
        "rewrite_rules_csv": csv_text(RULE_COLUMNS, rule_rows),
        "word_concatenation_rewrites": word_concatenation_rewrites,
        "word_concatenation_rewrites_csv": csv_text(CONCAT_COLUMNS, concat_rows),
        "alphabet_table": alphabet_table,
        "alphabet_signature_membership": membership_matrix,
        "rewrite_rule_table": rule_table,
        "word_concatenation_rewrite_table": concat_table,
        "symbolic_rewrite_certificate": certificate,
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
    write_json(OUT_DIR / "symbolic_alphabet.json", payloads["symbolic_alphabet"])
    (OUT_DIR / "symbolic_alphabet.csv").write_text(
        payloads["symbolic_alphabet_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "rewrite_rules.csv").write_text(
        payloads["rewrite_rules_csv"],
        encoding="utf-8",
    )
    write_json(OUT_DIR / "word_concatenation_rewrites.json", payloads["word_concatenation_rewrites"])
    (OUT_DIR / "word_concatenation_rewrites.csv").write_text(
        payloads["word_concatenation_rewrites_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "symbolic_rewrite_tables.npz",
        alphabet_table=payloads["alphabet_table"],
        alphabet_signature_membership=payloads["alphabet_signature_membership"],
        rewrite_rule_table=payloads["rewrite_rule_table"],
        word_concatenation_rewrite_table=payloads["word_concatenation_rewrite_table"],
    )
    write_json(OUT_DIR / "symbolic_rewrite_certificate.json", payloads["symbolic_rewrite_certificate"])
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
                "alphabet_symbol_count": witness["alphabet_symbol_count"],
                "binary_rewrite_rule_count": witness["binary_rewrite_rule_count"],
                "word_concatenation_rewrite_count": witness["word_concatenation_rewrite_count"],
                "alphabet_signature_union_count": witness["alphabet_signature_union_count"],
                "full_sector_binary_rule_count": witness["full_sector_binary_rule_count"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
