from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability import (
        build_carrier_adjacency,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        selected_prefix_consumed,
        target_match_indices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        padded,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        OUT_DIR as WEAK_PROMOTION_DIR,
        STATUS as WEAK_PROMOTION_STATUS,
        carrier_paths,
        first_return_closed,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        SYMBOLIC_ALPHABET_CSV,
        shared_atoms,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        associativity_lookup,
        build_trace,
        edge_key,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability import (
        build_carrier_adjacency,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        selected_prefix_consumed,
        target_match_indices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        padded,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        OUT_DIR as WEAK_PROMOTION_DIR,
        STATUS as WEAK_PROMOTION_STATUS,
        carrier_paths,
        first_return_closed,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        SYMBOLIC_ALPHABET_CSV,
        shared_atoms,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD3_PRE_NODE44_STRONGIFICATION_GAP_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

WEAK_PROMOTION_REPORT = WEAK_PROMOTION_DIR / "report.json"
WEAK_PROMOTION_JSON = (
    WEAK_PROMOTION_DIR
    / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit.json"
)
WEAK_PROMOTION_REPAIRS = (
    WEAK_PROMOTION_DIR / "aperture_overhead3_weak_promotion_repairs.csv"
)
WEAK_PROMOTION_TABLES = (
    WEAK_PROMOTION_DIR
    / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_tables.npz"
)
WEAK_PROMOTION_CERTIFICATE = (
    WEAK_PROMOTION_DIR
    / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap.py"
)

MAX_PREFIX_SYMBOL_LENGTH = 7
MAX_SUFFIX_SYMBOL_LENGTH = 4
MAX_STRONG_WORD_LENGTH = 10
MAX_TRACE_NODES = 12
MAX_EDIT_COST = 3
FIXED_TAIL_PREFIX_LENGTH = 2
TARGET_WORD_ID = 0
CARRIER_IDS = list(range(14))

PREFIX_SYMBOL_COLUMNS = [
    f"prefix_symbol_{index}_id" for index in range(MAX_PREFIX_SYMBOL_LENGTH)
]
SUFFIX_SYMBOL_COLUMNS = [
    f"promotion_suffix_symbol_{index}_id" for index in range(MAX_SUFFIX_SYMBOL_LENGTH)
]
BASE_WORD_SYMBOL_COLUMNS = [
    f"base_word_symbol_{index}_id" for index in range(MAX_STRONG_WORD_LENGTH)
]
STRONG_WORD_SYMBOL_COLUMNS = [
    f"strong_word_symbol_{index}_id" for index in range(MAX_STRONG_WORD_LENGTH)
]
TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_TRACE_NODES)]
SUBSTITUTION_COLUMNS = [
    "substitution_0_position",
    "substitution_0_from_symbol_id",
    "substitution_0_to_symbol_id",
    "substitution_1_position",
    "substitution_1_from_symbol_id",
    "substitution_1_to_symbol_id",
    "substitution_2_position",
    "substitution_2_from_symbol_id",
    "substitution_2_to_symbol_id",
]
INSERTION_COLUMNS = [
    "insertion_0_slot",
    "insertion_0_symbol_id",
    "insertion_1_slot",
    "insertion_1_symbol_id",
    "insertion_2_slot",
    "insertion_2_symbol_id",
]
ENDPOINT_HISTOGRAM_COLUMNS = [
    f"prefix_endpoint_carrier_{carrier_id}_count" for carrier_id in CARRIER_IDS
]

PREFIX_CLASS_COLUMNS = [
    "prefix_class_id",
    "source_trace_class_id",
    "member_candidate_count",
    "member_candidate_id_0",
    "member_candidate_id_1",
    "member_candidate_id_2",
    "member_candidate_id_3",
    "member_candidate_id_4",
    "member_candidate_id_5",
    "member_candidate_id_6",
    "prefix_length",
    *PREFIX_SYMBOL_COLUMNS,
    "promotion_suffix_length",
    *SUFFIX_SYMBOL_COLUMNS,
    "base_word_length",
    *BASE_WORD_SYMBOL_COLUMNS,
    "prefix_carrier_path_count",
    "prefix_endpoint_distinct_count",
    *ENDPOINT_HISTOGRAM_COLUMNS,
    "promoted_closed_path_count",
    "fixed_tail_substitution_space_count",
    "fixed_tail_substitution_strong_closed_hit_count",
    "unfixed_tail_substitution_space_count",
    "unfixed_tail_substitution_strong_closed_hit_count",
    "minimal_mixed_edit_cost",
    "minimal_strongification_word_count",
    "best_strongification_witness_id",
]

SEARCH_COST_COLUMNS = [
    "prefix_class_id",
    "edit_cost",
    "unique_candidate_word_count",
    "strong_closed_hit_count",
]

STRONGIFICATION_WITNESS_COLUMNS = [
    "strongification_witness_id",
    "prefix_class_id",
    "edit_cost",
    "substitution_count",
    "insertion_count",
    *SUBSTITUTION_COLUMNS,
    *INSERTION_COLUMNS,
    "strong_word_length",
    *STRONG_WORD_SYMBOL_COLUMNS,
    "target_last_symbol_rank",
    "first_node44_consumed_symbol_count",
    "closed_path_count",
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "best_score_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "prefix_class_count": 0,
    "nonstrong_member_count": 1,
    "class0_member_count": 2,
    "class1_member_count": 3,
    "class0_prefix_path_count": 4,
    "class1_prefix_path_count": 5,
    "fixed_tail_substitution_hit_count": 6,
    "unfixed_tail_substitution_hit_count": 7,
    "cost_below_three_hit_count": 8,
    "class0_minimal_mixed_edit_cost": 9,
    "class1_minimal_mixed_edit_cost": 10,
    "class0_minimal_witness_count": 11,
    "class1_minimal_witness_count": 12,
    "rank104_best_overhead_advantage": 13,
    "rank104_best_variation_advantage": 14,
    "minimal_witness_count": 15,
}


def promotion_rows(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def row_values(
    row: dict[str, int],
    prefix: str,
    size: int,
) -> tuple[int, ...]:
    return tuple(
        int(row[f"{prefix}_{index}_id"])
        for index in range(size)
        if int(row[f"{prefix}_{index}_id"]) >= 0
    )


def target0() -> tuple[int, ...]:
    return tuple(int(value) for value in LOWER_OVERHEAD_TAIL_WORDS[TARGET_WORD_ID])


def endpoint_histogram(
    prefix: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> Counter[int]:
    return Counter(state[1][-1] for state in carrier_paths(prefix, adjacency))


def evaluate_strong_closed_word(
    word: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
    assoc_by_word: dict[tuple[int, ...], dict[str, int]],
    rewrite_edge_by_pair: dict[tuple[int, int], dict[str, int]],
) -> dict[str, Any] | None:
    closed = first_return_closed(carrier_paths(word, adjacency))
    if not closed:
        return None
    try:
        raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
            word,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        consumed_count, _raw_rank = selected_prefix_consumed(raw_windows, len(word))
    except AssertionError:
        return None
    target_indices = target_match_indices(word, target0())
    if not target_indices or consumed_count < 0 or target_indices[-1] >= consumed_count:
        return None
    return {
        "word": word,
        "target_indices": tuple(target_indices),
        "consumed_count": consumed_count,
        "closed_path_count": len(closed),
        "trace_nodes": tuple(int(value) for value in trace_nodes),
        "metrics": {key: int(value) for key, value in metrics.items()},
    }


def substitution_hit_count(
    prefix: tuple[int, ...],
    suffix: tuple[int, ...],
    fixed_prefix_length: int,
    symbol_ids: list[int],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
    assoc_by_word: dict[tuple[int, ...], dict[str, int]],
    rewrite_edge_by_pair: dict[tuple[int, int], dict[str, int]],
) -> tuple[int, int]:
    variable_count = len(prefix) - fixed_prefix_length
    hit_count = 0
    for replacements in itertools.product(symbol_ids, repeat=variable_count):
        candidate_prefix = (*prefix[:fixed_prefix_length], *replacements)
        if evaluate_strong_closed_word(
            (*candidate_prefix, *suffix),
            adjacency,
            assoc_by_word,
            rewrite_edge_by_pair,
        ):
            hit_count += 1
    return len(symbol_ids) ** variable_count, hit_count


def unique_mixed_words_at_cost(
    prefix: tuple[int, ...],
    suffix: tuple[int, ...],
    edit_cost: int,
    symbol_ids: list[int],
) -> dict[tuple[int, ...], tuple[int, int, tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    positions = list(range(FIXED_TAIL_PREFIX_LENGTH, len(prefix)))
    slots = range(FIXED_TAIL_PREFIX_LENGTH, len(prefix) + 1)
    words: dict[
        tuple[int, ...],
        tuple[int, int, tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    ] = {}
    for substitution_count in range(edit_cost + 1):
        insertion_count = edit_cost - substitution_count
        for substitution_positions in itertools.combinations(
            positions,
            substitution_count,
        ):
            for substitution_symbols in itertools.product(
                symbol_ids,
                repeat=substitution_count,
            ):
                if any(
                    prefix[position] == symbol_id
                    for position, symbol_id in zip(
                        substitution_positions,
                        substitution_symbols,
                    )
                ):
                    continue
                mutated_prefix = list(prefix)
                for position, symbol_id in zip(
                    substitution_positions,
                    substitution_symbols,
                ):
                    mutated_prefix[position] = symbol_id
                for insertion_slots in itertools.combinations_with_replacement(
                    slots,
                    insertion_count,
                ):
                    for insertion_symbols in itertools.product(
                        symbol_ids,
                        repeat=insertion_count,
                    ):
                        buckets: dict[int, list[int]] = defaultdict(list)
                        for slot, symbol_id in zip(insertion_slots, insertion_symbols):
                            buckets[slot].append(symbol_id)
                        word: list[int] = []
                        for index in range(len(mutated_prefix) + 1):
                            word.extend(buckets.get(index, []))
                            if index < len(mutated_prefix):
                                word.append(mutated_prefix[index])
                        candidate_word = (*word, *suffix)
                        operation = (
                            substitution_count,
                            insertion_count,
                            tuple(int(value) for value in substitution_positions),
                            tuple(int(value) for value in substitution_symbols),
                            tuple(int(value) for value in insertion_slots),
                            tuple(int(value) for value in insertion_symbols),
                        )
                        if candidate_word not in words or operation < words[candidate_word]:
                            words[candidate_word] = operation
    return words


def operation_substitution_values(
    prefix: tuple[int, ...],
    positions: tuple[int, ...],
    symbols: tuple[int, ...],
) -> list[int]:
    values: list[int] = []
    for position, symbol_id in zip(positions, symbols):
        values.extend([position, prefix[position], symbol_id])
    return padded(values, len(SUBSTITUTION_COLUMNS))


def operation_insertion_values(
    slots: tuple[int, ...],
    symbols: tuple[int, ...],
) -> list[int]:
    values: list[int] = []
    for slot, symbol_id in zip(slots, symbols):
        values.extend([slot, symbol_id])
    return padded(values, len(INSERTION_COLUMNS))


def score_key(row: dict[str, int]) -> tuple[int, int, int, int, int, tuple[int, ...], int]:
    word = tuple(
        row[column]
        for column in STRONG_WORD_SYMBOL_COLUMNS[: row["strong_word_length"]]
    )
    return (
        row["trace_detour_overhead"],
        row["signature_valley_depth"],
        row["metric_gromov_delta_twice"],
        row["trace_signature_total_variation"],
        row["strong_word_length"],
        word,
        -row["closed_path_count"],
    )


def build_payloads() -> dict[str, Any]:
    weak_report = load_json(WEAK_PROMOTION_REPORT)
    weak_json = load_json(WEAK_PROMOTION_JSON)
    weak_certificate = load_json(WEAK_PROMOTION_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    weak_tables = np.load(WEAK_PROMOTION_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    weak_promotion_table = np.asarray(
        weak_tables["promotion_repair_table"],
        dtype=np.int64,
    )
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    symbol_ids = sorted({int(row["symbol_id"]) for row in alphabet_rows})
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    adjacency, _carriers = build_carrier_adjacency(
        read_int_csv(CELL_COMPLEX_EDGES),
        atom_to_symbol,
    )
    assoc_by_word = associativity_lookup(read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV))
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }

    nonstrong_rows = [
        row
        for row in promotion_rows(WEAK_PROMOTION_REPAIRS)
        if row["nonstrong_weak_flag"] == 1
    ]
    grouped: dict[
        tuple[int, tuple[int, ...], tuple[int, ...], tuple[tuple[int, int], ...]],
        list[dict[str, int]],
    ] = defaultdict(list)
    for row in nonstrong_rows:
        prefix = row_values(row, "promotion_prefix_symbol", MAX_PREFIX_SYMBOL_LENGTH)
        suffix = row_values(
            row,
            "minimal_promotion_suffix_symbol",
            MAX_SUFFIX_SYMBOL_LENGTH,
        )
        histogram = endpoint_histogram(prefix, adjacency)
        key = (
            row["trace_class_id"],
            prefix,
            suffix,
            tuple(sorted((int(key), int(value)) for key, value in histogram.items())),
        )
        grouped[key].append(row)

    prefix_class_rows = []
    search_rows = []
    witness_rows = []
    witness_rows_by_class: dict[int, list[dict[str, int]]] = {}

    for prefix_class_id, (key, members) in enumerate(
        sorted(grouped.items(), key=lambda item: item[0][0])
    ):
        trace_class_id, prefix, suffix, histogram_items = key
        histogram = Counter(dict(histogram_items))
        base_word = (*prefix, *suffix)
        member_ids = sorted(row["edit_repair_candidate_id"] for row in members)
        fixed_space, fixed_hits = substitution_hit_count(
            prefix,
            suffix,
            FIXED_TAIL_PREFIX_LENGTH,
            symbol_ids,
            adjacency,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        unfixed_space, unfixed_hits = substitution_hit_count(
            prefix,
            suffix,
            0,
            symbol_ids,
            adjacency,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        minimal_cost = -1
        minimal_hits: list[dict[str, int]] = []
        for edit_cost in range(MAX_EDIT_COST + 1):
            candidate_words = unique_mixed_words_at_cost(
                prefix,
                suffix,
                edit_cost,
                symbol_ids,
            )
            hit_rows = []
            for word, operation in sorted(candidate_words.items()):
                evaluation = evaluate_strong_closed_word(
                    word,
                    adjacency,
                    assoc_by_word,
                    rewrite_edge_by_pair,
                )
                if evaluation is None:
                    continue
                (
                    substitution_count,
                    insertion_count,
                    substitution_positions,
                    substitution_symbols,
                    insertion_slots,
                    insertion_symbols,
                ) = operation
                metrics = evaluation["metrics"]
                row = {
                    "strongification_witness_id": len(witness_rows) + len(hit_rows),
                    "prefix_class_id": prefix_class_id,
                    "edit_cost": edit_cost,
                    "substitution_count": substitution_count,
                    "insertion_count": insertion_count,
                    **{
                        column: value
                        for column, value in zip(
                            SUBSTITUTION_COLUMNS,
                            operation_substitution_values(
                                prefix,
                                substitution_positions,
                                substitution_symbols,
                            ),
                        )
                    },
                    **{
                        column: value
                        for column, value in zip(
                            INSERTION_COLUMNS,
                            operation_insertion_values(
                                insertion_slots,
                                insertion_symbols,
                            ),
                        )
                    },
                    "strong_word_length": len(word),
                    **{
                        column: value
                        for column, value in zip(
                            STRONG_WORD_SYMBOL_COLUMNS,
                            padded(word, MAX_STRONG_WORD_LENGTH),
                        )
                    },
                    "target_last_symbol_rank": evaluation["target_indices"][-1],
                    "first_node44_consumed_symbol_count": evaluation[
                        "consumed_count"
                    ],
                    "closed_path_count": evaluation["closed_path_count"],
                    "trace_node_count": len(evaluation["trace_nodes"]),
                    **{
                        column: value
                        for column, value in zip(
                            TRACE_NODE_COLUMNS,
                            padded(evaluation["trace_nodes"], MAX_TRACE_NODES),
                        )
                    },
                    "trace_detour_overhead": metrics["trace_detour_overhead"],
                    "signature_valley_depth": metrics["signature_valley_depth"],
                    "metric_gromov_delta_twice": metrics["metric_gromov_delta_twice"],
                    "trace_signature_total_variation": metrics[
                        "trace_signature_total_variation"
                    ],
                    "best_score_flag": 0,
                }
                hit_rows.append(row)
            search_rows.append(
                {
                    "prefix_class_id": prefix_class_id,
                    "edit_cost": edit_cost,
                    "unique_candidate_word_count": len(candidate_words),
                    "strong_closed_hit_count": len(hit_rows),
                }
            )
            if hit_rows and minimal_cost == -1:
                minimal_cost = edit_cost
                minimal_hits = hit_rows
        if minimal_cost < 0:
            raise AssertionError(f"no strongification found for prefix class {prefix_class_id}")
        best_row = sorted(minimal_hits, key=score_key)[0]
        for row in minimal_hits:
            row["best_score_flag"] = int(row is best_row)
            row["strongification_witness_id"] = len(witness_rows)
            witness_rows.append(row)
        witness_rows_by_class[prefix_class_id] = minimal_hits
        best_witness_id = next(
            row["strongification_witness_id"]
            for row in witness_rows
            if row["prefix_class_id"] == prefix_class_id and row["best_score_flag"] == 1
        )
        prefix_class_rows.append(
            {
                "prefix_class_id": prefix_class_id,
                "source_trace_class_id": trace_class_id,
                "member_candidate_count": len(member_ids),
                **{
                    f"member_candidate_id_{index}": value
                    for index, value in enumerate(padded(member_ids, 7))
                },
                "prefix_length": len(prefix),
                **{
                    column: value
                    for column, value in zip(
                        PREFIX_SYMBOL_COLUMNS,
                        padded(prefix, MAX_PREFIX_SYMBOL_LENGTH),
                    )
                },
                "promotion_suffix_length": len(suffix),
                **{
                    column: value
                    for column, value in zip(
                        SUFFIX_SYMBOL_COLUMNS,
                        padded(suffix, MAX_SUFFIX_SYMBOL_LENGTH),
                    )
                },
                "base_word_length": len(base_word),
                **{
                    column: value
                    for column, value in zip(
                        BASE_WORD_SYMBOL_COLUMNS,
                        padded(base_word, MAX_STRONG_WORD_LENGTH),
                    )
                },
                "prefix_carrier_path_count": sum(histogram.values()),
                "prefix_endpoint_distinct_count": len(histogram),
                **{
                    column: histogram[carrier_id]
                    for column, carrier_id in zip(
                        ENDPOINT_HISTOGRAM_COLUMNS,
                        CARRIER_IDS,
                    )
                },
                "promoted_closed_path_count": int(members[0]["promotion_closed_path_count"]),
                "fixed_tail_substitution_space_count": fixed_space,
                "fixed_tail_substitution_strong_closed_hit_count": fixed_hits,
                "unfixed_tail_substitution_space_count": unfixed_space,
                "unfixed_tail_substitution_strong_closed_hit_count": unfixed_hits,
                "minimal_mixed_edit_cost": minimal_cost,
                "minimal_strongification_word_count": len(minimal_hits),
                "best_strongification_witness_id": best_witness_id,
            }
        )

    prefix_class_table = table_from_rows(PREFIX_CLASS_COLUMNS, prefix_class_rows)
    search_table = table_from_rows(SEARCH_COST_COLUMNS, search_rows)
    witness_table = table_from_rows(STRONGIFICATION_WITNESS_COLUMNS, witness_rows)
    class0 = prefix_class_rows[0]
    class1 = prefix_class_rows[1]
    best_by_class = {
        row["prefix_class_id"]: row
        for row in witness_rows
        if row["best_score_flag"] == 1
    }
    observable_values = {
        "prefix_class_count": len(prefix_class_rows),
        "nonstrong_member_count": len(nonstrong_rows),
        "class0_member_count": class0["member_candidate_count"],
        "class1_member_count": class1["member_candidate_count"],
        "class0_prefix_path_count": class0["prefix_carrier_path_count"],
        "class1_prefix_path_count": class1["prefix_carrier_path_count"],
        "fixed_tail_substitution_hit_count": sum(
            row["fixed_tail_substitution_strong_closed_hit_count"]
            for row in prefix_class_rows
        ),
        "unfixed_tail_substitution_hit_count": sum(
            row["unfixed_tail_substitution_strong_closed_hit_count"]
            for row in prefix_class_rows
        ),
        "cost_below_three_hit_count": sum(
            row["strong_closed_hit_count"]
            for row in search_rows
            if row["edit_cost"] < 3
        ),
        "class0_minimal_mixed_edit_cost": class0["minimal_mixed_edit_cost"],
        "class1_minimal_mixed_edit_cost": class1["minimal_mixed_edit_cost"],
        "class0_minimal_witness_count": class0[
            "minimal_strongification_word_count"
        ],
        "class1_minimal_witness_count": class1[
            "minimal_strongification_word_count"
        ],
        "rank104_best_overhead_advantage": best_by_class[0]["trace_detour_overhead"]
        - best_by_class[1]["trace_detour_overhead"],
        "rank104_best_variation_advantage": best_by_class[0][
            "trace_signature_total_variation"
        ]
        - best_by_class[1]["trace_signature_total_variation"],
        "minimal_witness_count": len(witness_rows),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    best_words = {
        str(class_id): [
            row[column]
            for column in STRONG_WORD_SYMBOL_COLUMNS[: row["strong_word_length"]]
        ]
        for class_id, row in sorted(best_by_class.items())
    }
    checks = {
        "weak_promotion_report_certified": weak_report.get("status")
        == WEAK_PROMOTION_STATUS,
        "weak_promotion_certificate_certified": weak_certificate.get("status")
        == WEAK_PROMOTION_STATUS,
        "weak_promotion_schema_available": weak_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit@1",
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "symbolic_associativity_report_certified": associativity_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "symbolic_associativity_certificate_certified": associativity_certificate.get(
            "status"
        )
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "weak_promotion_table_shape_is_8": tuple(weak_promotion_table.shape)[0] == 8,
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "prefix_class_table_shape_matches_codebook": tuple(prefix_class_table.shape)
        == (2, len(PREFIX_CLASS_COLUMNS)),
        "search_table_shape_matches_codebook": tuple(search_table.shape)
        == (8, len(SEARCH_COST_COLUMNS)),
        "witness_table_shape_matches_codebook": tuple(witness_table.shape)
        == (24, len(STRONGIFICATION_WITNESS_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "prefix_classes_collapse_6_and_1_members": [
            row["member_candidate_count"] for row in prefix_class_rows
        ]
        == [6, 1],
        "prefix_endpoint_histograms_match_expected": [
            [
                row[column]
                for column in ENDPOINT_HISTOGRAM_COLUMNS
                if row[column] > 0
            ]
            for row in prefix_class_rows
        ]
        == [[6, 6, 4, 4, 4], [12, 12, 8, 8, 8]],
        "rank104_endpoint_histogram_is_double_class0": all(
            class1[column] == 2 * class0[column]
            for column in ENDPOINT_HISTOGRAM_COLUMNS
        ),
        "no_fixed_tail_or_unfixed_substitution_strongifies": observable_values[
            "fixed_tail_substitution_hit_count"
        ]
        == 0
        and observable_values["unfixed_tail_substitution_hit_count"] == 0,
        "no_mixed_edit_below_three_strongifies": observable_values[
            "cost_below_three_hit_count"
        ]
        == 0,
        "minimal_mixed_edit_costs_are_three": [
            row["minimal_mixed_edit_cost"] for row in prefix_class_rows
        ]
        == [3, 3],
        "minimal_witness_counts_are_10_and_14": [
            row["minimal_strongification_word_count"] for row in prefix_class_rows
        ]
        == [10, 14],
        "best_strongification_words_match_expected": best_words
        == {
            "0": [2, 1, 4, 5, 1, 2, 0, 4, 5],
            "1": [2, 1, 3, 4, 1, 5, 2, 1, 4, 5],
        },
        "rank104_best_strongification_has_lower_score": (
            best_by_class[1]["trace_detour_overhead"],
            best_by_class[1]["signature_valley_depth"],
            best_by_class[1]["metric_gromov_delta_twice"],
            best_by_class[1]["trace_signature_total_variation"],
        )
        == (6, 37, 1, 143)
        and (
            best_by_class[0]["trace_detour_overhead"],
            best_by_class[0]["signature_valley_depth"],
            best_by_class[0]["metric_gromov_delta_twice"],
            best_by_class[0]["trace_signature_total_variation"],
        )
        == (7, 45, 3, 205),
    }

    witness = {
        "prefix_classes": {
            str(row["prefix_class_id"]): {
                "source_trace_class_id": row["source_trace_class_id"],
                "member_candidate_ids": [
                    row[f"member_candidate_id_{index}"]
                    for index in range(7)
                    if row[f"member_candidate_id_{index}"] >= 0
                ],
                "prefix": [
                    row[column]
                    for column in PREFIX_SYMBOL_COLUMNS[: row["prefix_length"]]
                ],
                "promotion_suffix": [
                    row[column]
                    for column in SUFFIX_SYMBOL_COLUMNS[
                        : row["promotion_suffix_length"]
                    ]
                ],
                "endpoint_histogram": {
                    str(carrier_id): row[column]
                    for column, carrier_id in zip(
                        ENDPOINT_HISTOGRAM_COLUMNS,
                        CARRIER_IDS,
                    )
                    if row[column] > 0
                },
                "minimal_mixed_edit_cost": row["minimal_mixed_edit_cost"],
                "minimal_strongification_word_count": row[
                    "minimal_strongification_word_count"
                ],
            }
            for row in prefix_class_rows
        },
        "best_strongification_words": best_words,
        "best_strongification_scores": {
            str(class_id): [
                row["trace_detour_overhead"],
                row["signature_valley_depth"],
                row["metric_gromov_delta_twice"],
                row["trace_signature_total_variation"],
            ]
            for class_id, row in sorted(best_by_class.items())
        },
        "search_hit_counts": {
            f"{row['prefix_class_id']}:{row['edit_cost']}": row[
                "strong_closed_hit_count"
            ]
            for row in search_rows
        },
        "prefix_class_table_sha256": sha_array(prefix_class_table),
        "search_table_sha256": sha_array(search_table),
        "witness_table_sha256": sha_array(witness_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    strongification = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap@1",
        "object": "d20",
        "audit_rule": {
            "source_scope": "the seven nonstrong target0 rows from the weak-promotion audit",
            "collapse_key": "trace class, pre-node44 selected-symbol prefix, promoted suffix, and rooted carrier-prefix endpoint histogram",
            "substitution_scope": "all fixed-length pre-node44 symbol substitutions, both preserving and not preserving the initial x2,x1 tail prefix, with the promoted x5 suffix fixed",
            "mixed_edit_scope": "substitutions after the fixed x2,x1 tail prefix plus insertions before the promoted x5 suffix, with cost substitution_count + insertion_count and cost searched through three",
        },
        "summary": {
            "prefix_class_count": len(prefix_class_rows),
            "substitution_strongification_count": 0,
            "minimal_mixed_edit_cost_by_prefix_class": {
                str(row["prefix_class_id"]): row["minimal_mixed_edit_cost"]
                for row in prefix_class_rows
            },
            "best_strongification_words": best_words,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD3_PRE_NODE44_STRONGIFICATION_GAP_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the seven nonstrong x5-promoted target0 rows collapse to two pre-node44 prefix classes",
            "the baseline trace prefix class contains six rows and has endpoint histogram 2:6,3:6,10:4,11:4,12:4",
            "the rank-104 prefix class contains one row and doubles that endpoint histogram",
            "no fixed-length pre-node44 symbol substitution with the promoted x5 suffix fixed yields a strong first-hit closed repair",
            "the first strong first-hit closed repairs appear only at mixed edit cost three",
            "the rank-104 prefix class has the better best strongification score: overhead 6, valley 37, delta_twice 1, variation 143",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The seven nonstrong target0 rows from the weak-promotion layer "
            "collapse to two pre-node44 carrier-prefix geometries. Pure "
            "pre-node44 substitution cannot make either geometry a genuinely "
            "strong first-hit closed repair while the promoted x5 suffix is "
            "held fixed. The least successful fixed-tail edit in the certified "
            "mixed substitution/insertion scope has cost three; the rank-104 "
            "prefix class is the better strongification gateway."
        ),
        "stage_protocol": {
            "draft": "collapse nonstrong x5-promoted target0 rows by trace class, prefix, suffix, and endpoint histogram",
            "witness": "materialize endpoint histograms, substitution exhaustion counts, and minimal mixed-edit strongification witnesses",
            "coherence": "separate impossible fixed-length substitution from possible cost-three pre-node44 expansion",
            "closure": "certify the two prefix classes, zero substitution hits, cost-three minimum, and rank-104 best strongification advantage",
            "emit": "emit strongification-gap JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "weak_promotion_report": input_entry(
                WEAK_PROMOTION_REPORT,
                {
                    "status": weak_report.get("status"),
                    "certificate_sha256": weak_report.get("certificate_sha256"),
                },
            ),
            "weak_promotion_json": input_entry(WEAK_PROMOTION_JSON),
            "weak_promotion_repairs": input_entry(WEAK_PROMOTION_REPAIRS),
            "weak_promotion_tables": input_entry(WEAK_PROMOTION_TABLES),
            "weak_promotion_certificate": input_entry(WEAK_PROMOTION_CERTIFICATE),
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_report.get("status"),
                    "certificate_sha256": cell_report.get("certificate_sha256"),
                },
            ),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "symbolic_associativity_report": input_entry(
                SYMBOLIC_ASSOCIATIVITY_REPORT,
                {
                    "status": associativity_report.get("status"),
                    "certificate_sha256": associativity_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "symbolic_associativity_csv": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "symbolic_associativity_tables": input_entry(
                SYMBOLIC_ASSOCIATIVITY_TABLES
            ),
            "symbolic_associativity_certificate": input_entry(
                SYMBOLIC_ASSOCIATIVITY_CERTIFICATE
            ),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap.json"
            ),
            "aperture_overhead3_strongification_prefix_classes_csv": relpath(
                OUT_DIR / "aperture_overhead3_strongification_prefix_classes.csv"
            ),
            "aperture_overhead3_strongification_search_costs_csv": relpath(
                OUT_DIR / "aperture_overhead3_strongification_search_costs.csv"
            ),
            "aperture_overhead3_strongification_witnesses_csv": relpath(
                OUT_DIR / "aperture_overhead3_strongification_witnesses.csv"
            ),
            "aperture_overhead3_strongification_observables_csv": relpath(
                OUT_DIR / "aperture_overhead3_strongification_observables.csv"
            ),
            "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_tables.npz"
            ),
            "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the two prefix-endpoint classes of the seven nonstrong x5-promoted target0 rows",
                "exhaustion of fixed-length pre-node44 substitution spaces with the x5 suffix fixed",
                "the minimal mixed substitution/insertion edit cost through cost three",
                "all minimal cost-three strongification witness words in the fixed-tail mixed-edit scope",
                "the better best strongification score of the rank-104 prefix class",
            ],
            "does_not_certify_because_not_required": [
                "deletions or movement of the fixed final x5 promotion suffix",
                "edits before the initial x2,x1 tail prefix in the mixed-edit search",
                "strongification outside the residual carrier graph",
                "costs above three after a cost-three witness has been found",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Follow the rank-104 best strongification word "
            "x2,x1,x3,x4,x1,x5,x2,x1,x4,x5 as a new trace branch and compare "
            "its geodesic shortcuts against the original target1 branch."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified weak-promotion, carrier cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "collapse nonstrong promoted target0 rows by prefix endpoint histogram",
            "exhaust fixed-length substitution spaces with the x5 suffix fixed",
            "search mixed substitution/insertion edits through cost three and materialize all minimal witnesses",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap": strongification,
        "aperture_overhead3_strongification_prefix_classes_csv": csv_text(
            PREFIX_CLASS_COLUMNS,
            prefix_class_rows,
        ),
        "aperture_overhead3_strongification_search_costs_csv": csv_text(
            SEARCH_COST_COLUMNS,
            search_rows,
        ),
        "aperture_overhead3_strongification_witnesses_csv": csv_text(
            STRONGIFICATION_WITNESS_COLUMNS,
            witness_rows,
        ),
        "aperture_overhead3_strongification_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "prefix_class_table": prefix_class_table,
        "search_table": search_table,
        "strongification_witness_table": witness_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate": certificate,
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
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap.json",
        payloads[
            "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap"
        ],
    )
    (OUT_DIR / "aperture_overhead3_strongification_prefix_classes.csv").write_text(
        payloads["aperture_overhead3_strongification_prefix_classes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_strongification_search_costs.csv").write_text(
        payloads["aperture_overhead3_strongification_search_costs_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_strongification_witnesses.csv").write_text(
        payloads["aperture_overhead3_strongification_witnesses_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_strongification_observables.csv").write_text(
        payloads["aperture_overhead3_strongification_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_tables.npz",
        prefix_class_table=payloads["prefix_class_table"],
        search_table=payloads["search_table"],
        strongification_witness_table=payloads["strongification_witness_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap_certificate"
        ],
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
                "prefix_classes": witness["prefix_classes"],
                "best_strongification_words": witness[
                    "best_strongification_words"
                ],
                "next_highest_yield_item": payloads["report"][
                    "next_highest_yield_item"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
