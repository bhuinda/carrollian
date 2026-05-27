from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
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
        OUT_DIR as OVERHEAD2_CARRIER_DIR,
        STATUS as OVERHEAD2_CARRIER_STATUS,
        advance_states,
        build_carrier_adjacency,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        ORIGIN_CARRIER_ID,
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
        OUT_DIR as OVERHEAD2_CARRIER_DIR,
        STATUS as OVERHEAD2_CARRIER_STATUS,
        advance_states,
        build_carrier_adjacency,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        ORIGIN_CARRIER_ID,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_EDIT_REPAIR_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

OVERHEAD2_CARRIER_REPORT = OVERHEAD2_CARRIER_DIR / "report.json"
OVERHEAD2_CARRIER_JSON = (
    OVERHEAD2_CARRIER_DIR
    / "signature_boundary_spine_aperture_overhead2_carrier_realizability.json"
)
OVERHEAD2_CARRIER_TABLES = (
    OVERHEAD2_CARRIER_DIR
    / "signature_boundary_spine_aperture_overhead2_carrier_realizability_tables.npz"
)
OVERHEAD2_CARRIER_CERTIFICATE = (
    OVERHEAD2_CARRIER_DIR
    / "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair.py"
)

MAX_EDIT_DISTANCE = 2
MAX_WORD_LENGTH = 5 + MAX_EDIT_DISTANCE
WEAK_CRITERION = 0
STRONG_CRITERION = 1

WORD_COLUMNS = [f"symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]

CANDIDATE_COLUMNS = [
    "candidate_id",
    "target_word_id",
    "edit_distance",
    "word_length",
    *WORD_COLUMNS,
    "canonical_insert_0_slot",
    "canonical_insert_0_symbol_id",
    "canonical_insert_1_slot",
    "canonical_insert_1_symbol_id",
    "rooted_carrier_path_count",
    "distinct_end_carrier_count",
    "trace_reaches_node44_flag",
    "first_node44_raw_rank",
    "selected_prefix_consumed_at_node44",
    "target_subsequence_flag",
    "target_consumed_before_node44_flag",
    "weak_repair_flag",
    "strong_repair_flag",
    "trace_edge_count",
    "trace_detour_overhead",
    "trace_min_signature_after_node42",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "metric_diameter",
    "metric_radius",
    "trace_signature_total_variation",
    "beats_baseline_overhead_flag",
    "ties_baseline_overhead_flag",
    "baseline_score_match_flag",
]

MINIMUM_COLUMNS = [
    "target_word_id",
    "criterion_code",
    "minimal_edit_distance",
    "minimal_repair_count",
    "best_candidate_id",
    "best_word_length",
    *WORD_COLUMNS,
    "best_rooted_carrier_path_count",
    "best_trace_detour_overhead",
    "best_trace_min_signature_after_node42",
    "best_signature_valley_depth",
    "best_metric_gromov_delta_twice",
    "best_trace_signature_total_variation",
    "best_target_consumed_before_node44_flag",
    "best_beats_baseline_overhead_flag",
    "best_ties_baseline_overhead_flag",
    "best_baseline_score_match_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "candidate_word_count": 0,
    "target0_candidate_word_count": 1,
    "target1_candidate_word_count": 2,
    "weak_repair_count": 3,
    "strong_repair_count": 4,
    "target0_weak_min_edit_distance": 5,
    "target1_weak_min_edit_distance": 6,
    "target0_strong_min_edit_distance": 7,
    "target1_strong_min_edit_distance": 8,
    "target0_weak_min_repair_count": 9,
    "target1_weak_min_repair_count": 10,
    "target0_strong_min_repair_count": 11,
    "target1_strong_min_repair_count": 12,
    "target0_weak_best_overhead": 13,
    "target1_weak_best_overhead": 14,
    "target0_strong_best_overhead": 15,
    "target1_strong_best_overhead": 16,
    "weak_repairs_beating_baseline_count": 17,
    "strong_repairs_beating_baseline_count": 18,
    "baseline_score_matching_repair_count": 19,
}


def padded(values: tuple[int, ...] | list[int], size: int) -> list[int]:
    return [*values, *([-1] * (size - len(values)))]


def generated_words(target: tuple[int, ...], edit_distance: int) -> list[tuple[int, ...]]:
    seen: set[tuple[int, ...]] = set()
    for positions in itertools.combinations_with_replacement(
        range(2, len(target) + 1),
        edit_distance,
    ):
        for inserted_symbols in itertools.product(range(6), repeat=edit_distance):
            buckets: dict[int, list[int]] = defaultdict(list)
            for position, symbol_id in zip(positions, inserted_symbols):
                buckets[position].append(symbol_id)
            word: list[int] = []
            for target_position in range(len(target) + 1):
                word.extend(buckets[target_position])
                if target_position < len(target):
                    word.append(target[target_position])
            if word[:2] == [target[0], target[1]]:
                seen.add(tuple(word))
    return sorted(seen)


def target_match_indices(word: tuple[int, ...], target: tuple[int, ...]) -> list[int]:
    indices: list[int] = []
    target_rank = 0
    for word_rank, symbol_id in enumerate(word):
        if target_rank < len(target) and symbol_id == target[target_rank]:
            indices.append(word_rank)
            target_rank += 1
            if target_rank == len(target):
                break
    return indices if len(indices) == len(target) else []


def canonical_insertions(
    word: tuple[int, ...],
    target: tuple[int, ...],
) -> list[tuple[int, int]]:
    target_indices = set(target_match_indices(word, target))
    target_rank_before = 0
    insertions: list[tuple[int, int]] = []
    for word_rank, symbol_id in enumerate(word):
        if word_rank in target_indices:
            target_rank_before += 1
        else:
            insertions.append((target_rank_before, symbol_id))
    return insertions


def rooted_carrier_paths(
    word: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    states = [(ORIGIN_CARRIER_ID, (ORIGIN_CARRIER_ID,), (), ())]
    for symbol_id in word:
        states = advance_states(states, symbol_id, adjacency)
        if not states:
            break
    return states


def selected_prefix_consumed(raw_windows: list[dict[str, int]], word_length: int) -> tuple[int, int]:
    for window in raw_windows:
        if int(window["first_node44_stop_flag"]) == 1:
            raw_rank = int(window["trace_window_rank"])
            return min(raw_rank + 1, word_length), raw_rank
    return -1, -1


def row_word(row: dict[str, int], prefix: str = "symbol") -> tuple[int, ...]:
    values = []
    for index in range(MAX_WORD_LENGTH):
        value = int(row[f"{prefix}_{index}_id"])
        if value >= 0:
            values.append(value)
    return tuple(values)


def score_key(row: dict[str, int]) -> tuple[int, int, int, int, int, tuple[int, ...], int]:
    return (
        int(row["trace_detour_overhead"]),
        int(row["signature_valley_depth"]),
        int(row["metric_gromov_delta_twice"]),
        int(row["trace_signature_total_variation"]),
        int(row["word_length"]),
        row_word(row),
        -int(row["rooted_carrier_path_count"]),
    )


def build_payloads() -> dict[str, Any]:
    overhead2_report = load_json(OVERHEAD2_CARRIER_REPORT)
    overhead2_carrier = load_json(OVERHEAD2_CARRIER_JSON)
    overhead2_certificate = load_json(OVERHEAD2_CARRIER_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    overhead2_tables = np.load(OVERHEAD2_CARRIER_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    overhead2_word_table = np.asarray(overhead2_tables["word_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    cell_edges = read_int_csv(CELL_COMPLEX_EDGES)
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    adjacency, _carriers = build_carrier_adjacency(cell_edges, atom_to_symbol)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    assoc_by_word = associativity_lookup(associativity_rows)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }

    candidate_rows = []
    for target_word_id, target in enumerate(LOWER_OVERHEAD_TAIL_WORDS):
        for edit_distance in range(MAX_EDIT_DISTANCE + 1):
            for word in generated_words(target, edit_distance):
                states = rooted_carrier_paths(word, adjacency)
                target_indices = target_match_indices(word, target)
                insertions = padded(canonical_insertions(word, target), MAX_EDIT_DISTANCE)
                consumed_count = -1
                raw_rank = -1
                trace_reaches = 0
                metrics = {
                    "trace_edge_count": -1,
                    "trace_detour_overhead": -1,
                    "trace_min_signature_after_node42": -1,
                    "signature_valley_depth": -1,
                    "metric_gromov_delta_twice": -1,
                    "metric_diameter": -1,
                    "metric_radius": -1,
                    "trace_signature_total_variation": -1,
                }
                try:
                    raw_windows, _trace_nodes, _trace_signatures, trace_metrics = build_trace(
                        word,
                        assoc_by_word,
                        rewrite_edge_by_pair,
                    )
                    consumed_count, raw_rank = selected_prefix_consumed(
                        raw_windows,
                        len(word),
                    )
                    trace_reaches = 1
                    for key in metrics:
                        metrics[key] = int(trace_metrics[key])
                except AssertionError:
                    pass

                target_subsequence = int(bool(target_indices))
                target_consumed = int(
                    bool(target_indices)
                    and consumed_count >= 0
                    and target_indices[-1] < consumed_count
                )
                weak_repair = int(len(states) > 0 and trace_reaches and target_subsequence)
                strong_repair = int(weak_repair and target_consumed)
                baseline_score_match = int(
                    metrics["trace_detour_overhead"] == BASELINE_TAIL_OVERHEAD
                    and metrics["signature_valley_depth"] == BASELINE_TAIL_VALLEY
                    and metrics["metric_gromov_delta_twice"]
                    == BASELINE_TAIL_DELTA_TWICE
                    and metrics["trace_signature_total_variation"]
                    == BASELINE_TAIL_VARIATION
                )
                candidate_rows.append(
                    {
                        "candidate_id": len(candidate_rows),
                        "target_word_id": target_word_id,
                        "edit_distance": edit_distance,
                        "word_length": len(word),
                        **{
                            f"symbol_{index}_id": value
                            for index, value in enumerate(
                                padded(word, MAX_WORD_LENGTH)
                            )
                        },
                        "canonical_insert_0_slot": insertions[0][0]
                        if insertions[0] != -1
                        else -1,
                        "canonical_insert_0_symbol_id": insertions[0][1]
                        if insertions[0] != -1
                        else -1,
                        "canonical_insert_1_slot": insertions[1][0]
                        if insertions[1] != -1
                        else -1,
                        "canonical_insert_1_symbol_id": insertions[1][1]
                        if insertions[1] != -1
                        else -1,
                        "rooted_carrier_path_count": len(states),
                        "distinct_end_carrier_count": len(
                            {state[1][-1] for state in states}
                        ),
                        "trace_reaches_node44_flag": trace_reaches,
                        "first_node44_raw_rank": raw_rank,
                        "selected_prefix_consumed_at_node44": consumed_count,
                        "target_subsequence_flag": target_subsequence,
                        "target_consumed_before_node44_flag": target_consumed,
                        "weak_repair_flag": weak_repair,
                        "strong_repair_flag": strong_repair,
                        **metrics,
                        "beats_baseline_overhead_flag": int(
                            weak_repair
                            and metrics["trace_detour_overhead"]
                            < BASELINE_TAIL_OVERHEAD
                        ),
                        "ties_baseline_overhead_flag": int(
                            weak_repair
                            and metrics["trace_detour_overhead"]
                            == BASELINE_TAIL_OVERHEAD
                        ),
                        "baseline_score_match_flag": baseline_score_match,
                    }
                )

    minimum_rows = []
    minima_by_target_criterion: dict[tuple[int, int], list[dict[str, int]]] = {}
    for target_word_id in range(len(LOWER_OVERHEAD_TAIL_WORDS)):
        for criterion_code, flag_name in [
            (WEAK_CRITERION, "weak_repair_flag"),
            (STRONG_CRITERION, "strong_repair_flag"),
        ]:
            repairs = [
                row
                for row in candidate_rows
                if row["target_word_id"] == target_word_id and row[flag_name] == 1
            ]
            min_edit = min(row["edit_distance"] for row in repairs)
            min_repairs = [
                row for row in repairs if row["edit_distance"] == min_edit
            ]
            minima_by_target_criterion[(target_word_id, criterion_code)] = min_repairs
            best = sorted(min_repairs, key=score_key)[0]
            minimum_rows.append(
                {
                    "target_word_id": target_word_id,
                    "criterion_code": criterion_code,
                    "minimal_edit_distance": min_edit,
                    "minimal_repair_count": len(min_repairs),
                    "best_candidate_id": best["candidate_id"],
                    "best_word_length": best["word_length"],
                    **{
                        column: best[column]
                        for column in WORD_COLUMNS
                    },
                    "best_rooted_carrier_path_count": best[
                        "rooted_carrier_path_count"
                    ],
                    "best_trace_detour_overhead": best["trace_detour_overhead"],
                    "best_trace_min_signature_after_node42": best[
                        "trace_min_signature_after_node42"
                    ],
                    "best_signature_valley_depth": best["signature_valley_depth"],
                    "best_metric_gromov_delta_twice": best[
                        "metric_gromov_delta_twice"
                    ],
                    "best_trace_signature_total_variation": best[
                        "trace_signature_total_variation"
                    ],
                    "best_target_consumed_before_node44_flag": best[
                        "target_consumed_before_node44_flag"
                    ],
                    "best_beats_baseline_overhead_flag": best[
                        "beats_baseline_overhead_flag"
                    ],
                    "best_ties_baseline_overhead_flag": best[
                        "ties_baseline_overhead_flag"
                    ],
                    "best_baseline_score_match_flag": best[
                        "baseline_score_match_flag"
                    ],
                }
            )

    minimum_lookup = {
        (row["target_word_id"], row["criterion_code"]): row
        for row in minimum_rows
    }
    observable_values = {
        "candidate_word_count": len(candidate_rows),
        "target0_candidate_word_count": sum(
            1 for row in candidate_rows if row["target_word_id"] == 0
        ),
        "target1_candidate_word_count": sum(
            1 for row in candidate_rows if row["target_word_id"] == 1
        ),
        "weak_repair_count": sum(row["weak_repair_flag"] for row in candidate_rows),
        "strong_repair_count": sum(row["strong_repair_flag"] for row in candidate_rows),
        "target0_weak_min_edit_distance": minimum_lookup[
            (0, WEAK_CRITERION)
        ]["minimal_edit_distance"],
        "target1_weak_min_edit_distance": minimum_lookup[
            (1, WEAK_CRITERION)
        ]["minimal_edit_distance"],
        "target0_strong_min_edit_distance": minimum_lookup[
            (0, STRONG_CRITERION)
        ]["minimal_edit_distance"],
        "target1_strong_min_edit_distance": minimum_lookup[
            (1, STRONG_CRITERION)
        ]["minimal_edit_distance"],
        "target0_weak_min_repair_count": minimum_lookup[
            (0, WEAK_CRITERION)
        ]["minimal_repair_count"],
        "target1_weak_min_repair_count": minimum_lookup[
            (1, WEAK_CRITERION)
        ]["minimal_repair_count"],
        "target0_strong_min_repair_count": minimum_lookup[
            (0, STRONG_CRITERION)
        ]["minimal_repair_count"],
        "target1_strong_min_repair_count": minimum_lookup[
            (1, STRONG_CRITERION)
        ]["minimal_repair_count"],
        "target0_weak_best_overhead": minimum_lookup[
            (0, WEAK_CRITERION)
        ]["best_trace_detour_overhead"],
        "target1_weak_best_overhead": minimum_lookup[
            (1, WEAK_CRITERION)
        ]["best_trace_detour_overhead"],
        "target0_strong_best_overhead": minimum_lookup[
            (0, STRONG_CRITERION)
        ]["best_trace_detour_overhead"],
        "target1_strong_best_overhead": minimum_lookup[
            (1, STRONG_CRITERION)
        ]["best_trace_detour_overhead"],
        "weak_repairs_beating_baseline_count": sum(
            row["beats_baseline_overhead_flag"]
            for row in candidate_rows
            if row["weak_repair_flag"] == 1
        ),
        "strong_repairs_beating_baseline_count": sum(
            row["beats_baseline_overhead_flag"]
            for row in candidate_rows
            if row["strong_repair_flag"] == 1
        ),
        "baseline_score_matching_repair_count": sum(
            row["baseline_score_match_flag"]
            for row in candidate_rows
            if row["weak_repair_flag"] == 1
        ),
    }
    observable_rows = [
        {
            "observable_id": code,
            "observable_code": code,
            "value_x1e12": int(observable_values[name]),
            "aux_id": -1,
        }
        for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
    ]

    candidate_table = table_from_rows(CANDIDATE_COLUMNS, candidate_rows)
    minimum_table = table_from_rows(MINIMUM_COLUMNS, minimum_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "overhead2_carrier_report_certified": overhead2_report.get("status")
        == OVERHEAD2_CARRIER_STATUS,
        "overhead2_carrier_certificate_certified": overhead2_certificate.get("status")
        == OVERHEAD2_CARRIER_STATUS,
        "overhead2_carrier_schema_available": overhead2_carrier.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability@1",
        "overhead2_word_table_shape_is_2_by_14": tuple(overhead2_word_table.shape)
        == (2, 14),
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
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "candidate_table_shape_is_596_by_codebook": tuple(candidate_table.shape)
        == (596, len(CANDIDATE_COLUMNS)),
        "minimum_table_shape_is_4_by_codebook": tuple(minimum_table.shape)
        == (4, len(MINIMUM_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "exact_overhead2_words_have_no_weak_repair": all(
            row["weak_repair_flag"] == 0
            for row in candidate_rows
            if row["edit_distance"] == 0
        ),
        "weak_min_edit_distances_are_one_and_one": [
            observable_values["target0_weak_min_edit_distance"],
            observable_values["target1_weak_min_edit_distance"],
        ]
        == [1, 1],
        "strong_min_edit_distances_are_two_and_one": [
            observable_values["target0_strong_min_edit_distance"],
            observable_values["target1_strong_min_edit_distance"],
        ]
        == [2, 1],
        "minimal_weak_repairs_are_unique": [
            observable_values["target0_weak_min_repair_count"],
            observable_values["target1_weak_min_repair_count"],
        ]
        == [1, 1],
        "minimal_strong_repairs_are_two_and_one": [
            observable_values["target0_strong_min_repair_count"],
            observable_values["target1_strong_min_repair_count"],
        ]
        == [2, 1],
        "no_repair_beats_baseline_overhead": observable_values[
            "weak_repairs_beating_baseline_count"
        ]
        == 0
        and observable_values["strong_repairs_beating_baseline_count"] == 0,
        "weak_best_overheads_match_baseline": [
            observable_values["target0_weak_best_overhead"],
            observable_values["target1_weak_best_overhead"],
        ]
        == [BASELINE_TAIL_OVERHEAD, BASELINE_TAIL_OVERHEAD],
        "target0_strong_best_overhead_is_five": observable_values[
            "target0_strong_best_overhead"
        ]
        == 5,
        "target1_strong_best_overhead_matches_baseline": observable_values[
            "target1_strong_best_overhead"
        ]
        == BASELINE_TAIL_OVERHEAD,
        "target0_weak_best_is_post_aperture_tail": minimum_lookup[
            (0, WEAK_CRITERION)
        ]["best_target_consumed_before_node44_flag"]
        == 0,
        "target1_weak_best_is_also_strong": minimum_lookup[
            (1, WEAK_CRITERION)
        ]["best_target_consumed_before_node44_flag"]
        == 1,
        "target0_weak_best_word_matches_expected": row_word(
            minimum_lookup[(0, WEAK_CRITERION)]
        )
        == (2, 1, 4, 5, 2, 5),
        "target1_weak_best_word_matches_expected": row_word(
            minimum_lookup[(1, WEAK_CRITERION)]
        )
        == (2, 1, 5, 2, 5, 4),
        "target0_strong_best_word_matches_expected": row_word(
            minimum_lookup[(0, STRONG_CRITERION)]
        )
        == (2, 1, 4, 3, 2, 5, 4),
        "repair_counts_within_bound_are_stable": observable_values[
            "weak_repair_count"
        ]
        == 37
        and observable_values["strong_repair_count"] == 19,
    }

    witness = {
        "target_words": [list(word) for word in LOWER_OVERHEAD_TAIL_WORDS],
        "search_bound": {
            "max_insertions": MAX_EDIT_DISTANCE,
            "candidate_word_count": len(candidate_rows),
            "allowed_insertions": "after the fixed x2,x1 tail prefix only",
        },
        "criteria": {
            "weak": "rooted carrier path for the full edited word and first node44 trace hit",
            "strong": "weak repair whose first node44 trace hit occurs after the original target word is fully consumed",
        },
        "minimum_repairs": {
            f"{row['target_word_id']}:{row['criterion_code']}": {
                "minimal_edit_distance": row["minimal_edit_distance"],
                "minimal_repair_count": row["minimal_repair_count"],
                "best_word": list(row_word(row)),
                "best_trace_detour_overhead": row["best_trace_detour_overhead"],
                "best_signature_valley_depth": row[
                    "best_signature_valley_depth"
                ],
                "best_target_consumed_before_node44": bool(
                    row["best_target_consumed_before_node44_flag"]
                ),
            }
            for row in minimum_rows
        },
        "weak_repairs_beating_baseline_count": observable_values[
            "weak_repairs_beating_baseline_count"
        ],
        "strong_repairs_beating_baseline_count": observable_values[
            "strong_repairs_beating_baseline_count"
        ],
        "candidate_table_sha256": sha_array(candidate_table),
        "minimum_table_sha256": sha_array(minimum_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    edit_repair = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_edit_repair@1",
        "object": "d20",
        "search_rule": {
            "target_words": "the two abstract x1-tail overhead-2 words",
            "edit_model": "insertion-only selected-symbol edit distance preserving the initial x2,x1 tail prefix",
            "rooted_scope": "carrier paths start at residual carrier 12",
            "weak_repair": witness["criteria"]["weak"],
            "strong_repair": witness["criteria"]["strong"],
        },
        "summary": {
            "weak_min_edit_distance_by_target": {
                "0": observable_values["target0_weak_min_edit_distance"],
                "1": observable_values["target1_weak_min_edit_distance"],
            },
            "strong_min_edit_distance_by_target": {
                "0": observable_values["target0_strong_min_edit_distance"],
                "1": observable_values["target1_strong_min_edit_distance"],
            },
            "no_repair_beats_existing_tail_overhead": True,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_edit_repair_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_EDIT_REPAIR_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "both abstract overhead-2 words are one inserted contact away from a rooted carrier-realizable node44 trace",
            "neither one-contact repair beats the existing overhead-3 x1-tail class; both tie its trace overhead",
            "for x2,x1,x4,x2,x5, the unique one-contact repair x2,x1,x4,x5,x2,x5 reaches node44 before the final target x5 is consumed",
            "requiring full target consumption before the first node44 hit raises x2,x1,x4,x2,x5 to two inserted contacts, with best repair x2,x1,x4,x3,x2,x5,x4 and overhead 5",
            "for x2,x1,x5,x2,x4, the one-contact repair x2,x1,x5,x2,x5,x4 is already strong and has overhead 3",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_edit_repair@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The carrier obstruction is repaired by insertion, not by a lower "
            "trace overhead. Each abstract overhead-2 word is one carrier "
            "contact away from a rooted node44 trace, but no repaired word "
            "within the certified edit bound improves on the existing "
            "overhead-3 x1-tail class."
        ),
        "stage_protocol": {
            "draft": "enumerate insertion-only x1-tail repairs through two inserted selected-symbol contacts",
            "witness": "materialize carrier path counts, first node44 trace metrics, and weak versus strong repair flags",
            "coherence": "compare minimal repairs with the existing overhead-3 tail baseline and expose the target0 post-aperture tail seam",
            "closure": "certify per-word minimal edit distances under weak and strong repair criteria through the two-contact bound",
            "emit": "emit edit-repair JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "overhead2_carrier_report": input_entry(
                OVERHEAD2_CARRIER_REPORT,
                {
                    "status": overhead2_report.get("status"),
                    "certificate_sha256": overhead2_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "overhead2_carrier_json": input_entry(OVERHEAD2_CARRIER_JSON),
            "overhead2_carrier_tables": input_entry(OVERHEAD2_CARRIER_TABLES),
            "overhead2_carrier_certificate": input_entry(
                OVERHEAD2_CARRIER_CERTIFICATE
            ),
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
            "signature_boundary_spine_aperture_overhead2_edit_repair": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair.json"
            ),
            "aperture_overhead2_edit_repair_candidates_csv": relpath(
                OUT_DIR / "aperture_overhead2_edit_repair_candidates.csv"
            ),
            "aperture_overhead2_edit_repair_minima_csv": relpath(
                OUT_DIR / "aperture_overhead2_edit_repair_minima.csv"
            ),
            "aperture_overhead2_edit_repair_observables_csv": relpath(
                OUT_DIR / "aperture_overhead2_edit_repair_observables.csv"
            ),
            "signature_boundary_spine_aperture_overhead2_edit_repair_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_edit_repair_tables.npz"
            ),
            "signature_boundary_spine_aperture_overhead2_edit_repair_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_edit_repair_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all insertion-only edited words through two inserted symbols, preserving the initial x2,x1 prefix",
                "rooted carrier realizability from carrier 12 for each edited word",
                "first node44 trace metrics for each edited word that reaches the aperture",
                "minimal weak and strong edit distances for the two overhead-2 target words through the two-contact bound",
                "that no repaired word in this bound improves below overhead 3",
            ],
            "does_not_certify_because_not_required": [
                "deletions, substitutions, or insertions before the x2,x1 tail prefix",
                "carrier repairs requiring more than two inserted contacts",
                "closed first-return cycle repair after the first node44 hit",
                "changing the residual carrier-mask cell complex or symbolic canonicalization",
            ],
        },
        "next_highest_yield_item": (
            "Classify the post-aperture tails of the one-contact weak repairs: "
            "separate repairs that merely hit node44 early from repairs that "
            "close a carrier cycle after consuming the whole target word."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_edit_repair_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified overhead-2 carrier obstruction, residual cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "enumerate insertion-only selected-symbol repairs through two inserted contacts",
            "compute rooted carrier path counts and first node44 trace metrics for every candidate word",
            "certify weak and strong per-word minimal edit distances and compare them with the overhead-3 tail baseline",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_overhead2_edit_repair": edit_repair,
        "aperture_overhead2_edit_repair_candidates_csv": csv_text(
            CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_overhead2_edit_repair_minima_csv": csv_text(
            MINIMUM_COLUMNS,
            minimum_rows,
        ),
        "aperture_overhead2_edit_repair_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "minimum_table": minimum_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_overhead2_edit_repair_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair.json",
        payloads["signature_boundary_spine_aperture_overhead2_edit_repair"],
    )
    (OUT_DIR / "aperture_overhead2_edit_repair_candidates.csv").write_text(
        payloads["aperture_overhead2_edit_repair_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_edit_repair_minima.csv").write_text(
        payloads["aperture_overhead2_edit_repair_minima_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_edit_repair_observables.csv").write_text(
        payloads["aperture_overhead2_edit_repair_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair_tables.npz",
        candidate_table=payloads["candidate_table"],
        minimum_table=payloads["minimum_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_edit_repair_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_overhead2_edit_repair_certificate"
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
                "minimum_repairs": witness["minimum_repairs"],
                "weak_repairs_beating_baseline_count": witness[
                    "weak_repairs_beating_baseline_count"
                ],
                "strong_repairs_beating_baseline_count": witness[
                    "strong_repairs_beating_baseline_count"
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
