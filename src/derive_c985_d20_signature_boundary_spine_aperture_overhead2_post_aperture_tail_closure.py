from __future__ import annotations

import itertools
import json
from collections import Counter
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
        advance_states,
        build_carrier_adjacency,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        CANDIDATE_COLUMNS as EDIT_CANDIDATE_COLUMNS,
        OUT_DIR as EDIT_REPAIR_DIR,
        STATUS as EDIT_REPAIR_STATUS,
        MAX_WORD_LENGTH as EDIT_MAX_WORD_LENGTH,
        row_word as edit_row_word,
        selected_prefix_consumed,
        target_match_indices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
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
        advance_states,
        build_carrier_adjacency,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        CANDIDATE_COLUMNS as EDIT_CANDIDATE_COLUMNS,
        OUT_DIR as EDIT_REPAIR_DIR,
        STATUS as EDIT_REPAIR_STATUS,
        MAX_WORD_LENGTH as EDIT_MAX_WORD_LENGTH,
        row_word as edit_row_word,
        selected_prefix_consumed,
        target_match_indices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
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


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_POST_APERTURE_TAIL_CLOSURE_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

EDIT_REPAIR_REPORT = EDIT_REPAIR_DIR / "report.json"
EDIT_REPAIR_JSON = (
    EDIT_REPAIR_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair.json"
)
EDIT_REPAIR_CANDIDATES = EDIT_REPAIR_DIR / "aperture_overhead2_edit_repair_candidates.csv"
EDIT_REPAIR_TABLES = (
    EDIT_REPAIR_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair_tables.npz"
)
EDIT_REPAIR_CERTIFICATE = (
    EDIT_REPAIR_DIR / "signature_boundary_spine_aperture_overhead2_edit_repair_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure.py"
)

MAX_CLOSURE_EXTENSION = 2
MAX_REPAIR_WORD_LENGTH = EDIT_MAX_WORD_LENGTH + 1
MAX_PATH_SYMBOL_LENGTH = EDIT_MAX_WORD_LENGTH + MAX_CLOSURE_EXTENSION

REPAIR_WORD_COLUMNS = [f"symbol_{index}_id" for index in range(MAX_REPAIR_WORD_LENGTH)]
CLOSURE_SUFFIX_COLUMNS = [
    f"closure_suffix_symbol_{index}_id" for index in range(MAX_CLOSURE_EXTENSION)
]
PATH_CARRIER_COLUMNS = [
    f"carrier_{index}_id" for index in range(MAX_PATH_SYMBOL_LENGTH + 1)
]
PATH_EDGE_COLUMNS = [f"cell_edge_{index}_id" for index in range(MAX_PATH_SYMBOL_LENGTH)]
PATH_ATOM_COLUMNS = [
    f"selected_atom_{index}_id" for index in range(MAX_PATH_SYMBOL_LENGTH)
]

REPAIR_COLUMNS = [
    "repair_id",
    "edit_candidate_id",
    "target_word_id",
    "repair_word_length",
    *REPAIR_WORD_COLUMNS,
    "first_node44_raw_rank",
    "first_node44_consumed_symbol_count",
    "post_aperture_tail_length",
    "post_aperture_tail_symbol_0_id",
    "target_last_symbol_rank",
    "target_consumed_before_node44_flag",
    "target_consumed_after_node44_flag",
    "first_node44_prefix_path_count",
    "first_node44_prefix_closed_path_count",
    "full_repair_path_count",
    "full_repair_closed_path_count",
    "distinct_full_end_carrier_count",
    "minimal_extra_closure_length",
    "minimal_closure_suffix_count",
    *CLOSURE_SUFFIX_COLUMNS,
    "closure_extended_path_count",
    "closure_closed_path_count",
    "early_hit_nonclosing_flag",
    "post_aperture_tail_closes_cycle_flag",
    "needs_extra_closure_after_node44_flag",
]

CLOSED_PATH_COLUMNS = [
    "closed_path_id",
    "repair_id",
    "target_word_id",
    "closure_suffix_length",
    *CLOSURE_SUFFIX_COLUMNS,
    "path_symbol_length",
    *PATH_CARRIER_COLUMNS,
    *PATH_EDGE_COLUMNS,
    *PATH_ATOM_COLUMNS,
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "one_contact_weak_repair_count": 0,
    "early_node44_repair_count": 1,
    "strong_trace_one_contact_repair_count": 2,
    "full_word_closed_repair_count": 3,
    "extra_closure_required_repair_count": 4,
    "early_hit_nonclosing_repair_count": 5,
    "target0_post_aperture_tail_length": 6,
    "target1_post_aperture_tail_length": 7,
    "target0_full_closed_path_count": 8,
    "target1_full_closed_path_count": 9,
    "target0_min_extra_closure_length": 10,
    "target1_min_extra_closure_length": 11,
    "target1_best_closure_suffix_symbol": 12,
    "closed_path_row_count": 13,
}


def padded(values: tuple[int, ...] | list[int], size: int) -> list[int]:
    return [*values, *([-1] * (size - len(values)))]


def candidate_row_from_table(values: np.ndarray) -> dict[str, int]:
    return {
        column: int(values[index])
        for index, column in enumerate(EDIT_CANDIDATE_COLUMNS)
    }


def carrier_paths(
    word: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    states = [(ORIGIN_CARRIER_ID, (ORIGIN_CARRIER_ID,), (), ())]
    for symbol_id in word:
        states = advance_states(states, symbol_id, adjacency)
        if not states:
            break
    return states


def extend_states(
    states: list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
    suffix: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    next_states = states
    for symbol_id in suffix:
        next_states = advance_states(next_states, symbol_id, adjacency)
        if not next_states:
            break
    return next_states


def minimal_closure_suffixes(
    full_states: list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> tuple[int, list[tuple[int, ...]], dict[tuple[int, ...], list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]]]:
    for suffix_length in range(MAX_CLOSURE_EXTENSION + 1):
        suffixes: list[tuple[int, ...]] = []
        closed_by_suffix = {}
        for suffix in itertools.product(range(6), repeat=suffix_length):
            extended = extend_states(full_states, suffix, adjacency)
            closed = [
                state
                for state in extended
                if state[1][-1] == ORIGIN_CARRIER_ID
            ]
            if closed:
                suffixes.append(suffix)
                closed_by_suffix[suffix] = closed
        if suffixes:
            return suffix_length, sorted(suffixes), closed_by_suffix
    return -1, [], {}


def closed_path_row(
    row_id: int,
    repair_id: int,
    target_word_id: int,
    suffix: tuple[int, ...],
    state: tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]],
) -> dict[str, int]:
    _start, carriers, edge_ids, atom_ids = state
    return {
        "closed_path_id": row_id,
        "repair_id": repair_id,
        "target_word_id": target_word_id,
        "closure_suffix_length": len(suffix),
        **{
            column: value
            for column, value in zip(
                CLOSURE_SUFFIX_COLUMNS,
                padded(suffix, MAX_CLOSURE_EXTENSION),
            )
        },
        "path_symbol_length": len(edge_ids),
        **{
            column: value
            for column, value in zip(
                PATH_CARRIER_COLUMNS,
                padded(carriers, MAX_PATH_SYMBOL_LENGTH + 1),
            )
        },
        **{
            column: value
            for column, value in zip(
                PATH_EDGE_COLUMNS,
                padded(edge_ids, MAX_PATH_SYMBOL_LENGTH),
            )
        },
        **{
            column: value
            for column, value in zip(
                PATH_ATOM_COLUMNS,
                padded(atom_ids, MAX_PATH_SYMBOL_LENGTH),
            )
        },
    }


def build_payloads() -> dict[str, Any]:
    edit_report = load_json(EDIT_REPAIR_REPORT)
    edit_repair = load_json(EDIT_REPAIR_JSON)
    edit_certificate = load_json(EDIT_REPAIR_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    edit_tables = np.load(EDIT_REPAIR_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    edit_candidate_table = np.asarray(edit_tables["candidate_table"], dtype=np.int64)
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

    candidate_rows = [
        candidate_row_from_table(row)
        for row in edit_candidate_table
    ]
    one_contact_repairs = sorted(
        [
            row
            for row in candidate_rows
            if row["edit_distance"] == 1 and row["weak_repair_flag"] == 1
        ],
        key=lambda row: (row["target_word_id"], row["candidate_id"]),
    )

    repair_rows = []
    closed_path_rows = []
    closed_path_count_by_repair: dict[int, int] = {}
    end_histograms: dict[int, dict[str, int]] = {}

    for repair_id, candidate in enumerate(one_contact_repairs):
        target_word_id = candidate["target_word_id"]
        target = LOWER_OVERHEAD_TAIL_WORDS[target_word_id]
        word = edit_row_word(candidate)
        raw_windows, _trace_nodes, _trace_signatures, _metrics = build_trace(
            word,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        consumed_count, raw_rank = selected_prefix_consumed(raw_windows, len(word))
        target_indices = target_match_indices(word, target)
        prefix_states = carrier_paths(word[:consumed_count], adjacency)
        full_states = carrier_paths(word, adjacency)
        closed_full = [
            state
            for state in full_states
            if state[1][-1] == ORIGIN_CARRIER_ID
        ]
        suffix_length, closure_suffixes, closed_by_suffix = minimal_closure_suffixes(
            full_states,
            adjacency,
        )
        best_suffix = closure_suffixes[0] if closure_suffixes else ()
        best_extended = extend_states(full_states, best_suffix, adjacency)
        best_closed = closed_by_suffix.get(best_suffix, [])
        for state in best_closed:
            closed_path_rows.append(
                closed_path_row(
                    len(closed_path_rows),
                    repair_id,
                    target_word_id,
                    best_suffix,
                    state,
                )
            )
        closed_path_count_by_repair[repair_id] = len(best_closed)
        end_histograms[repair_id] = {
            str(carrier_id): count
            for carrier_id, count in sorted(
                Counter(state[1][-1] for state in full_states).items()
            )
        }
        target_last_rank = target_indices[-1]
        target_before_node44 = int(target_last_rank < consumed_count)
        post_tail = word[consumed_count:]
        repair_rows.append(
            {
                "repair_id": repair_id,
                "edit_candidate_id": candidate["candidate_id"],
                "target_word_id": target_word_id,
                "repair_word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        REPAIR_WORD_COLUMNS,
                        padded(word, MAX_REPAIR_WORD_LENGTH),
                    )
                },
                "first_node44_raw_rank": raw_rank,
                "first_node44_consumed_symbol_count": consumed_count,
                "post_aperture_tail_length": len(post_tail),
                "post_aperture_tail_symbol_0_id": post_tail[0] if post_tail else -1,
                "target_last_symbol_rank": target_last_rank,
                "target_consumed_before_node44_flag": target_before_node44,
                "target_consumed_after_node44_flag": int(not target_before_node44),
                "first_node44_prefix_path_count": len(prefix_states),
                "first_node44_prefix_closed_path_count": sum(
                    1 for state in prefix_states if state[1][-1] == ORIGIN_CARRIER_ID
                ),
                "full_repair_path_count": len(full_states),
                "full_repair_closed_path_count": len(closed_full),
                "distinct_full_end_carrier_count": len(
                    {state[1][-1] for state in full_states}
                ),
                "minimal_extra_closure_length": suffix_length,
                "minimal_closure_suffix_count": len(closure_suffixes),
                **{
                    column: value
                    for column, value in zip(
                        CLOSURE_SUFFIX_COLUMNS,
                        padded(best_suffix, MAX_CLOSURE_EXTENSION),
                    )
                },
                "closure_extended_path_count": len(best_extended),
                "closure_closed_path_count": len(best_closed),
                "early_hit_nonclosing_flag": int(
                    not target_before_node44 and len(best_closed) == 0
                ),
                "post_aperture_tail_closes_cycle_flag": int(
                    len(post_tail) > 0 and len(closed_full) > 0
                ),
                "needs_extra_closure_after_node44_flag": int(
                    len(closed_full) == 0 and suffix_length > 0
                ),
            }
        )

    repair_table = table_from_rows(REPAIR_COLUMNS, repair_rows)
    closed_path_table = table_from_rows(CLOSED_PATH_COLUMNS, closed_path_rows)
    repair_by_target = {
        row["target_word_id"]: row
        for row in repair_rows
    }
    observable_values = {
        "one_contact_weak_repair_count": len(repair_rows),
        "early_node44_repair_count": sum(
            row["target_consumed_after_node44_flag"] for row in repair_rows
        ),
        "strong_trace_one_contact_repair_count": sum(
            row["target_consumed_before_node44_flag"] for row in repair_rows
        ),
        "full_word_closed_repair_count": sum(
            1 for row in repair_rows if row["full_repair_closed_path_count"] > 0
        ),
        "extra_closure_required_repair_count": sum(
            row["needs_extra_closure_after_node44_flag"] for row in repair_rows
        ),
        "early_hit_nonclosing_repair_count": sum(
            row["early_hit_nonclosing_flag"] for row in repair_rows
        ),
        "target0_post_aperture_tail_length": repair_by_target[0][
            "post_aperture_tail_length"
        ],
        "target1_post_aperture_tail_length": repair_by_target[1][
            "post_aperture_tail_length"
        ],
        "target0_full_closed_path_count": repair_by_target[0][
            "full_repair_closed_path_count"
        ],
        "target1_full_closed_path_count": repair_by_target[1][
            "full_repair_closed_path_count"
        ],
        "target0_min_extra_closure_length": repair_by_target[0][
            "minimal_extra_closure_length"
        ],
        "target1_min_extra_closure_length": repair_by_target[1][
            "minimal_extra_closure_length"
        ],
        "target1_best_closure_suffix_symbol": repair_by_target[1][
            "closure_suffix_symbol_0_id"
        ],
        "closed_path_row_count": len(closed_path_rows),
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
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "edit_repair_report_certified": edit_report.get("status")
        == EDIT_REPAIR_STATUS,
        "edit_repair_certificate_certified": edit_certificate.get("status")
        == EDIT_REPAIR_STATUS,
        "edit_repair_schema_available": edit_repair.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead2_edit_repair@1",
        "edit_candidate_table_shape_is_596_by_35": tuple(edit_candidate_table.shape)
        == (596, len(EDIT_CANDIDATE_COLUMNS)),
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
        "repair_table_shape_is_2_by_codebook": tuple(repair_table.shape)
        == (2, len(REPAIR_COLUMNS)),
        "closed_path_table_shape_is_20_by_codebook": tuple(closed_path_table.shape)
        == (20, len(CLOSED_PATH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "one_contact_weak_repair_count_is_two": observable_values[
            "one_contact_weak_repair_count"
        ]
        == 2,
        "one_repair_hits_node44_before_target_consumption": observable_values[
            "early_node44_repair_count"
        ]
        == 1,
        "one_repair_consumes_target_at_node44": observable_values[
            "strong_trace_one_contact_repair_count"
        ]
        == 1,
        "target0_word_has_post_aperture_x5_tail": repair_by_target[0][
            "post_aperture_tail_length"
        ]
        == 1
        and repair_by_target[0]["post_aperture_tail_symbol_0_id"] == 5,
        "target0_post_tail_closes_eight_full_cycles": repair_by_target[0][
            "full_repair_closed_path_count"
        ]
        == 8
        and repair_by_target[0]["minimal_extra_closure_length"] == 0,
        "target1_word_has_no_post_aperture_tail": repair_by_target[1][
            "post_aperture_tail_length"
        ]
        == 0,
        "target1_needs_one_x3_closure_contact": repair_by_target[1][
            "full_repair_closed_path_count"
        ]
        == 0
        and repair_by_target[1]["minimal_extra_closure_length"] == 1
        and repair_by_target[1]["closure_suffix_symbol_0_id"] == 3,
        "target1_x3_closure_has_twelve_closed_paths": repair_by_target[1][
            "closure_closed_path_count"
        ]
        == 12,
        "no_early_hit_has_dead_post_aperture_tail": observable_values[
            "early_hit_nonclosing_repair_count"
        ]
        == 0,
        "closed_path_rows_split_8_and_12": closed_path_count_by_repair == {0: 8, 1: 12},
    }

    witness = {
        "one_contact_weak_repairs": {
            str(row["target_word_id"]): {
                "repair_word": [
                    value
                    for value in [row[column] for column in REPAIR_WORD_COLUMNS]
                    if value >= 0
                ],
                "first_node44_consumed_symbol_count": row[
                    "first_node44_consumed_symbol_count"
                ],
                "post_aperture_tail_length": row["post_aperture_tail_length"],
                "post_aperture_tail_symbol_0_id": row[
                    "post_aperture_tail_symbol_0_id"
                ],
                "full_repair_path_count": row["full_repair_path_count"],
                "full_repair_closed_path_count": row[
                    "full_repair_closed_path_count"
                ],
                "minimal_extra_closure_length": row[
                    "minimal_extra_closure_length"
                ],
                "best_closure_suffix": [
                    value
                    for value in [
                        row[column] for column in CLOSURE_SUFFIX_COLUMNS
                    ]
                    if value >= 0
                ],
                "closure_closed_path_count": row["closure_closed_path_count"],
                "full_end_carrier_histogram": end_histograms[row["repair_id"]],
            }
            for row in repair_rows
        },
        "closed_path_count_by_repair": {
            str(repair_id): count
            for repair_id, count in sorted(closed_path_count_by_repair.items())
        },
        "repair_table_sha256": sha_array(repair_table),
        "closed_path_table_sha256": sha_array(closed_path_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    tail_closure = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure@1",
        "object": "d20",
        "search_rule": {
            "source": "the two one-contact weak repairs certified by the overhead-2 edit-repair layer",
            "classification": "compare first node44 trace time, target consumption time, full-word carrier closure, and least extra post-target closure suffix",
            "closure_bound": f"extra closure suffixes of length 0..{MAX_CLOSURE_EXTENSION}",
        },
        "summary": {
            "target0": witness["one_contact_weak_repairs"]["0"],
            "target1": witness["one_contact_weak_repairs"]["1"],
            "early_hit_nonclosing_repair_count": observable_values[
                "early_hit_nonclosing_repair_count"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_POST_APERTURE_TAIL_CLOSURE_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "target0's one-contact repair reaches node44 before the final target x5, but that post-aperture x5 tail consumes the target and closes 8 carrier cycles",
            "target1's one-contact repair consumes the target at node44 but has zero closed full-word carrier paths",
            "target1 closes after one extra post-target x3 contact, producing 12 closed carrier paths",
            "there is no one-contact weak repair that is merely an early node44 hit with a dead post-aperture tail within the certified closure bound",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The one-contact weak repairs split into two carrier-tail types. "
            "The target0 repair is trace-weak because node44 appears before "
            "the final target symbol, but its post-aperture x5 tail completes "
            "the target and closes carrier cycles. The target1 repair is "
            "trace-strong but carrier-open until one extra x3 return contact."
        ),
        "stage_protocol": {
            "draft": "extract the one-contact weak repairs from the certified edit-repair table",
            "witness": "enumerate first-node44 prefixes, full repair paths, closed full paths, and least post-target closure suffixes",
            "coherence": "separate trace timing from carrier closure and record closed carrier-path witnesses",
            "closure": "certify the two post-aperture tail types and the absence of an early dead tail in the closure bound",
            "emit": "emit tail-closure JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "edit_repair_report": input_entry(
                EDIT_REPAIR_REPORT,
                {
                    "status": edit_report.get("status"),
                    "certificate_sha256": edit_report.get("certificate_sha256"),
                },
            ),
            "edit_repair_json": input_entry(EDIT_REPAIR_JSON),
            "edit_repair_candidates": input_entry(EDIT_REPAIR_CANDIDATES),
            "edit_repair_tables": input_entry(EDIT_REPAIR_TABLES),
            "edit_repair_certificate": input_entry(EDIT_REPAIR_CERTIFICATE),
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
            "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure.json"
            ),
            "aperture_overhead2_post_aperture_tail_repairs_csv": relpath(
                OUT_DIR / "aperture_overhead2_post_aperture_tail_repairs.csv"
            ),
            "aperture_overhead2_post_aperture_tail_closed_paths_csv": relpath(
                OUT_DIR / "aperture_overhead2_post_aperture_tail_closed_paths.csv"
            ),
            "aperture_overhead2_post_aperture_tail_observables_csv": relpath(
                OUT_DIR / "aperture_overhead2_post_aperture_tail_observables.csv"
            ),
            "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_tables.npz"
            ),
            "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the two one-contact weak repairs from the edit-repair layer",
                "the first node44 trace time versus target-consumption time for each repair",
                "all closed full-word carrier paths for target0's post-aperture x5 tail",
                "the least extra closure suffix for target1 through length two, namely x3",
                "all closed carrier paths for the selected minimal closure suffixes",
            ],
            "does_not_certify_because_not_required": [
                "non-minimal weak repairs at edit distance two",
                "closure suffixes longer than two selected symbols",
                "ranking closed repair cycles against all bounded backtrack candidates",
                "changing the residual carrier-mask cell complex or symbolic canonicalization",
            ],
        },
        "next_highest_yield_item": (
            "Rank the closed repaired cycles against the 1,287 bounded "
            "first-return candidates to decide whether the x5 post-tail and "
            "x3 return are new cycle classes or aliases of the existing "
            "overhead-3 baseline trace."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified edit-repair, residual cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "extract the two one-contact weak repairs and recompute first node44 trace timing",
            "enumerate full carrier paths, full closed carrier paths, and least post-target closure suffixes",
            "materialize closed carrier-path witnesses for the minimal closure suffixes",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure": tail_closure,
        "aperture_overhead2_post_aperture_tail_repairs_csv": csv_text(
            REPAIR_COLUMNS,
            repair_rows,
        ),
        "aperture_overhead2_post_aperture_tail_closed_paths_csv": csv_text(
            CLOSED_PATH_COLUMNS,
            closed_path_rows,
        ),
        "aperture_overhead2_post_aperture_tail_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "repair_table": repair_table,
        "closed_path_table": closed_path_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate": certificate,
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
        / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure.json",
        payloads[
            "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure"
        ],
    )
    (OUT_DIR / "aperture_overhead2_post_aperture_tail_repairs.csv").write_text(
        payloads["aperture_overhead2_post_aperture_tail_repairs_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_post_aperture_tail_closed_paths.csv").write_text(
        payloads["aperture_overhead2_post_aperture_tail_closed_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_post_aperture_tail_observables.csv").write_text(
        payloads["aperture_overhead2_post_aperture_tail_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_tables.npz",
        repair_table=payloads["repair_table"],
        closed_path_table=payloads["closed_path_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate"
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
                "one_contact_weak_repairs": witness["one_contact_weak_repairs"],
                "closed_path_count_by_repair": witness[
                    "closed_path_count_by_repair"
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
