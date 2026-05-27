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
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
        OUT_DIR as SYMBOL_STATE_DIR,
        STATUS as SYMBOL_STATE_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_OVERHEAD,
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
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction import (
        LOWER_OVERHEAD_TAIL_WORDS,
        OUT_DIR as SYMBOL_STATE_DIR,
        STATUS as SYMBOL_STATE_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_OVERHEAD,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_CARRIER_REALIZABILITY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SYMBOL_STATE_REPORT = SYMBOL_STATE_DIR / "report.json"
SYMBOL_STATE_JSON = (
    SYMBOL_STATE_DIR / "signature_boundary_spine_aperture_symbol_state_obstruction.json"
)
SYMBOL_STATE_TABLES = (
    SYMBOL_STATE_DIR
    / "signature_boundary_spine_aperture_symbol_state_obstruction_tables.npz"
)
SYMBOL_STATE_CERTIFICATE = (
    SYMBOL_STATE_DIR
    / "signature_boundary_spine_aperture_symbol_state_obstruction_certificate.json"
)
SYMBOL_STATE_FORBIDDEN = (
    SYMBOL_STATE_DIR / "aperture_symbol_state_forbidden_transitions.csv"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_overhead2_carrier_realizability.py"
)

ROOTED_SCOPE = 0
GLOBAL_SCOPE = 1
MAX_WORD_LENGTH = 5

WORD_COLUMNS = [
    "word_id",
    "symbol_0_id",
    "symbol_1_id",
    "symbol_2_id",
    "symbol_3_id",
    "symbol_4_id",
    "trace_detour_overhead",
    "signature_valley_depth",
    "rooted_full_path_count",
    "global_full_path_count",
    "rooted_first_missing_prefix_length",
    "global_first_missing_prefix_length",
    "rooted_last_viable_prefix_count",
    "global_last_viable_prefix_count",
]

PREFIX_COLUMNS = [
    "scope_code",
    "word_id",
    "prefix_length",
    "required_symbol_id",
    "path_count",
    "distinct_start_carrier_count",
    "distinct_end_carrier_count",
    "first_missing_flag",
    "full_word_flag",
]

FRONTIER_COLUMNS = [
    "scope_code",
    "word_id",
    "frontier_path_id",
    "prefix_length",
    "start_carrier_id",
    "end_carrier_id",
    "carrier_0_id",
    "carrier_1_id",
    "carrier_2_id",
    "carrier_3_id",
    "carrier_4_id",
    "carrier_5_id",
    "cell_edge_0_id",
    "cell_edge_1_id",
    "cell_edge_2_id",
    "cell_edge_3_id",
    "cell_edge_4_id",
    "selected_atom_0_id",
    "selected_atom_1_id",
    "selected_atom_2_id",
    "selected_atom_3_id",
    "selected_atom_4_id",
]

NEXT_SYMBOL_COLUMNS = [
    "scope_code",
    "word_id",
    "prefix_length",
    "frontier_carrier_id",
    "available_symbol_id",
    "outgoing_choice_count",
    "required_symbol_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "target_word_count": 0,
    "rooted_full_realization_count": 1,
    "global_full_realization_count": 2,
    "word0_rooted_last_viable_prefix_count": 3,
    "word0_global_last_viable_prefix_count": 4,
    "word1_rooted_last_viable_prefix_count": 5,
    "word1_global_last_viable_prefix_count": 6,
    "word0_first_missing_prefix_length": 7,
    "word1_first_missing_prefix_length": 8,
    "word0_rooted_required_next_count": 9,
    "word0_global_required_next_count": 10,
    "word1_rooted_required_next_count": 11,
    "word1_global_required_next_count": 12,
    "frontier_path_row_count": 13,
    "next_symbol_row_count": 14,
}


def padded(values: tuple[int, ...], size: int) -> list[int]:
    return [*values, *([-1] * (size - len(values)))]


def build_carrier_adjacency(
    cell_edges: list[dict[str, int]],
    atom_to_symbol: dict[int, int],
) -> tuple[dict[int, list[tuple[int, dict[str, Any]]]], list[int]]:
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    carriers: set[int] = set()
    for row in cell_edges:
        source = int(row["source_carrier_mask_class_id"])
        target = int(row["target_carrier_mask_class_id"])
        carriers.update([source, target])
        atoms_by_symbol: dict[int, list[int]] = defaultdict(list)
        for atom_id in shared_atoms(row):
            atoms_by_symbol[atom_to_symbol[atom_id]].append(atom_id)
        edge = {
            "edge_id": int(row["cell_edge_id"]),
            "source": source,
            "target": target,
            "atoms_by_symbol": {
                symbol: sorted(atom_ids)
                for symbol, atom_ids in atoms_by_symbol.items()
            },
        }
        adjacency[source].append((target, edge))
        adjacency[target].append((source, edge))
    return (
        {
            carrier: sorted(values, key=lambda item: (item[0], item[1]["edge_id"]))
            for carrier, values in adjacency.items()
        },
        sorted(carriers),
    )


def advance_states(
    states: list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
    symbol_id: int,
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    next_states = []
    for start, carriers, edge_ids, atom_ids in states:
        current = carriers[-1]
        for neighbor, edge in adjacency[current]:
            atoms = edge["atoms_by_symbol"].get(symbol_id, [])
            for atom_id in atoms:
                next_states.append(
                    (
                        start,
                        (*carriers, neighbor),
                        (*edge_ids, int(edge["edge_id"])),
                        (*atom_ids, atom_id),
                    )
                )
    return next_states


def next_symbol_counts(
    states: list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> dict[int, Counter[int]]:
    by_carrier: dict[int, Counter[int]] = defaultdict(Counter)
    for _start, carriers, _edge_ids, _atom_ids in states:
        current = carriers[-1]
        for _neighbor, edge in adjacency[current]:
            for symbol_id, atom_ids in edge["atoms_by_symbol"].items():
                by_carrier[current][symbol_id] += len(atom_ids)
    return {carrier: Counter(counter) for carrier, counter in by_carrier.items()}


def enumerate_prefixes(
    starts: list[int],
    word: tuple[int, ...],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> tuple[list[list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]], int]:
    states = [(start, (start,), (), ()) for start in starts]
    prefix_states = []
    first_missing = -1
    for prefix_length, symbol_id in enumerate(word, start=1):
        states = advance_states(states, symbol_id, adjacency)
        prefix_states.append(states)
        if first_missing == -1 and not states:
            first_missing = prefix_length
    return prefix_states, first_missing


def prefix_row(
    scope_code: int,
    word_id: int,
    prefix_length: int,
    required_symbol_id: int,
    states: list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
    first_missing: int,
    word_length: int,
) -> dict[str, int]:
    return {
        "scope_code": scope_code,
        "word_id": word_id,
        "prefix_length": prefix_length,
        "required_symbol_id": required_symbol_id,
        "path_count": len(states),
        "distinct_start_carrier_count": len({state[0] for state in states}),
        "distinct_end_carrier_count": len({state[1][-1] for state in states}),
        "first_missing_flag": int(prefix_length == first_missing),
        "full_word_flag": int(prefix_length == word_length and len(states) > 0),
    }


def frontier_rows(
    scope_code: int,
    word_id: int,
    prefix_length: int,
    states: list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
) -> list[dict[str, int]]:
    rows = []
    for state in states:
        start, carriers, edge_ids, atom_ids = state
        carrier_ids = padded(carriers, MAX_WORD_LENGTH + 1)
        edge_values = padded(edge_ids, MAX_WORD_LENGTH)
        atom_values = padded(atom_ids, MAX_WORD_LENGTH)
        rows.append(
            {
                "scope_code": scope_code,
                "word_id": word_id,
                "frontier_path_id": len(rows),
                "prefix_length": prefix_length,
                "start_carrier_id": start,
                "end_carrier_id": carriers[-1],
                "carrier_0_id": carrier_ids[0],
                "carrier_1_id": carrier_ids[1],
                "carrier_2_id": carrier_ids[2],
                "carrier_3_id": carrier_ids[3],
                "carrier_4_id": carrier_ids[4],
                "carrier_5_id": carrier_ids[5],
                "cell_edge_0_id": edge_values[0],
                "cell_edge_1_id": edge_values[1],
                "cell_edge_2_id": edge_values[2],
                "cell_edge_3_id": edge_values[3],
                "cell_edge_4_id": edge_values[4],
                "selected_atom_0_id": atom_values[0],
                "selected_atom_1_id": atom_values[1],
                "selected_atom_2_id": atom_values[2],
                "selected_atom_3_id": atom_values[3],
                "selected_atom_4_id": atom_values[4],
            }
        )
    return rows


def build_payloads() -> dict[str, Any]:
    symbol_state_report = load_json(SYMBOL_STATE_REPORT)
    symbol_state = load_json(SYMBOL_STATE_JSON)
    symbol_state_certificate = load_json(SYMBOL_STATE_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    symbol_state_tables = np.load(SYMBOL_STATE_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    forbidden_table = np.asarray(symbol_state_tables["forbidden_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    cell_edges = read_int_csv(CELL_COMPLEX_EDGES)
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    adjacency, carriers = build_carrier_adjacency(cell_edges, atom_to_symbol)
    assoc_by_word = associativity_lookup(associativity_rows)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }

    word_rows = []
    prefix_rows = []
    all_frontier_rows = []
    next_symbol_rows = []
    first_missing_by_word: dict[int, int] = {}
    rooted_frontier_count_by_word: dict[int, int] = {}
    global_frontier_count_by_word: dict[int, int] = {}
    required_next_counts: dict[tuple[int, int], int] = {}
    full_counts: dict[tuple[int, int], int] = {}

    for word_id, word in enumerate(LOWER_OVERHEAD_TAIL_WORDS):
        raw_windows, _trace_nodes, _trace_signatures, metrics = build_trace(
            word,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        per_scope: dict[int, dict[str, Any]] = {}
        for scope_code, starts in [
            (ROOTED_SCOPE, [ORIGIN_CARRIER_ID]),
            (GLOBAL_SCOPE, carriers),
        ]:
            prefix_states, first_missing = enumerate_prefixes(starts, word, adjacency)
            per_scope[scope_code] = {
                "prefix_states": prefix_states,
                "first_missing": first_missing,
            }
            first_missing_by_word[word_id] = first_missing
            for prefix_length, states in enumerate(prefix_states, start=1):
                prefix_rows.append(
                    prefix_row(
                        scope_code,
                        word_id,
                        prefix_length,
                        word[prefix_length - 1],
                        states,
                        first_missing,
                        len(word),
                    )
                )
            frontier_prefix = first_missing - 1
            frontier_states = prefix_states[frontier_prefix - 1]
            frontier = frontier_rows(scope_code, word_id, frontier_prefix, frontier_states)
            all_frontier_rows.extend(frontier)
            next_counts = next_symbol_counts(frontier_states, adjacency)
            required_symbol = word[first_missing - 1]
            required_total = 0
            for carrier_id in sorted(next_counts):
                for symbol_id in sorted(next_counts[carrier_id]):
                    count = int(next_counts[carrier_id][symbol_id])
                    required_total += count if symbol_id == required_symbol else 0
                    next_symbol_rows.append(
                        {
                            "scope_code": scope_code,
                            "word_id": word_id,
                            "prefix_length": frontier_prefix,
                            "frontier_carrier_id": carrier_id,
                            "available_symbol_id": symbol_id,
                            "outgoing_choice_count": count,
                            "required_symbol_flag": int(symbol_id == required_symbol),
                        }
                    )
            required_next_counts[(scope_code, word_id)] = required_total
            full_counts[(scope_code, word_id)] = len(prefix_states[-1])
            if scope_code == ROOTED_SCOPE:
                rooted_frontier_count_by_word[word_id] = len(frontier_states)
            else:
                global_frontier_count_by_word[word_id] = len(frontier_states)

        word_rows.append(
            {
                "word_id": word_id,
                "symbol_0_id": word[0],
                "symbol_1_id": word[1],
                "symbol_2_id": word[2],
                "symbol_3_id": word[3],
                "symbol_4_id": word[4],
                "trace_detour_overhead": int(metrics["trace_detour_overhead"]),
                "signature_valley_depth": int(metrics["signature_valley_depth"]),
                "rooted_full_path_count": full_counts[(ROOTED_SCOPE, word_id)],
                "global_full_path_count": full_counts[(GLOBAL_SCOPE, word_id)],
                "rooted_first_missing_prefix_length": per_scope[ROOTED_SCOPE][
                    "first_missing"
                ],
                "global_first_missing_prefix_length": per_scope[GLOBAL_SCOPE][
                    "first_missing"
                ],
                "rooted_last_viable_prefix_count": rooted_frontier_count_by_word[word_id],
                "global_last_viable_prefix_count": global_frontier_count_by_word[word_id],
            }
        )

    word_table = table_from_rows(WORD_COLUMNS, word_rows)
    prefix_table = table_from_rows(PREFIX_COLUMNS, prefix_rows)
    frontier_table = table_from_rows(FRONTIER_COLUMNS, all_frontier_rows)
    next_symbol_table = table_from_rows(NEXT_SYMBOL_COLUMNS, next_symbol_rows)
    observable_values = {
        "target_word_count": len(LOWER_OVERHEAD_TAIL_WORDS),
        "rooted_full_realization_count": sum(
            full_counts[(ROOTED_SCOPE, word_id)]
            for word_id in range(len(LOWER_OVERHEAD_TAIL_WORDS))
        ),
        "global_full_realization_count": sum(
            full_counts[(GLOBAL_SCOPE, word_id)]
            for word_id in range(len(LOWER_OVERHEAD_TAIL_WORDS))
        ),
        "word0_rooted_last_viable_prefix_count": rooted_frontier_count_by_word[0],
        "word0_global_last_viable_prefix_count": global_frontier_count_by_word[0],
        "word1_rooted_last_viable_prefix_count": rooted_frontier_count_by_word[1],
        "word1_global_last_viable_prefix_count": global_frontier_count_by_word[1],
        "word0_first_missing_prefix_length": first_missing_by_word[0],
        "word1_first_missing_prefix_length": first_missing_by_word[1],
        "word0_rooted_required_next_count": required_next_counts[(ROOTED_SCOPE, 0)],
        "word0_global_required_next_count": required_next_counts[(GLOBAL_SCOPE, 0)],
        "word1_rooted_required_next_count": required_next_counts[(ROOTED_SCOPE, 1)],
        "word1_global_required_next_count": required_next_counts[(GLOBAL_SCOPE, 1)],
        "frontier_path_row_count": len(all_frontier_rows),
        "next_symbol_row_count": len(next_symbol_rows),
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
        "symbol_state_report_certified": symbol_state_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_SYMBOL_STATE_OBSTRUCTION_CERTIFIED",
        "symbol_state_certificate_certified": symbol_state_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_SYMBOL_STATE_OBSTRUCTION_CERTIFIED",
        "symbol_state_schema_available": symbol_state.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_symbol_state_obstruction@1",
        "symbol_state_forbidden_table_shape_is_2_by_22": tuple(forbidden_table.shape)
        == (2, 22),
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
        "target_words_match_symbol_state_witness": LOWER_OVERHEAD_TAIL_WORDS
        == [(2, 1, 4, 2, 5), (2, 1, 5, 2, 4)],
        "rooted_full_realization_count_is_zero": observable_values[
            "rooted_full_realization_count"
        ]
        == 0,
        "global_full_realization_count_is_zero": observable_values[
            "global_full_realization_count"
        ]
        == 0,
        "word0_dies_at_fourth_symbol_x2": first_missing_by_word[0] == 4
        and required_next_counts[(ROOTED_SCOPE, 0)] == 0
        and required_next_counts[(GLOBAL_SCOPE, 0)] == 0,
        "word1_dies_at_fifth_symbol_x4": first_missing_by_word[1] == 5
        and required_next_counts[(ROOTED_SCOPE, 1)] == 0
        and required_next_counts[(GLOBAL_SCOPE, 1)] == 0,
        "rooted_frontier_counts_are_8_and_8": rooted_frontier_count_by_word
        == {0: 8, 1: 8},
        "global_frontier_counts_are_32_and_32": global_frontier_count_by_word
        == {0: 32, 1: 32},
        "word_table_shape_is_2_by_codebook": tuple(word_table.shape)
        == (2, len(WORD_COLUMNS)),
        "prefix_table_shape_is_20_by_codebook": tuple(prefix_table.shape)
        == (20, len(PREFIX_COLUMNS)),
        "frontier_table_shape_is_80_by_codebook": tuple(frontier_table.shape)
        == (80, len(FRONTIER_COLUMNS)),
        "next_symbol_table_shape_is_42_by_codebook": tuple(next_symbol_table.shape)
        == (42, len(NEXT_SYMBOL_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "both_words_are_symbolic_overhead2": all(
            int(row["trace_detour_overhead"]) < BASELINE_TAIL_OVERHEAD
            for row in word_rows
        ),
    }

    witness = {
        "target_words": [list(word) for word in LOWER_OVERHEAD_TAIL_WORDS],
        "rooted_full_realization_count": observable_values[
            "rooted_full_realization_count"
        ],
        "global_full_realization_count": observable_values[
            "global_full_realization_count"
        ],
        "first_missing_prefix_length_by_word": {
            str(word_id): first_missing_by_word[word_id]
            for word_id in sorted(first_missing_by_word)
        },
        "rooted_last_viable_prefix_count_by_word": {
            str(word_id): rooted_frontier_count_by_word[word_id]
            for word_id in sorted(rooted_frontier_count_by_word)
        },
        "global_last_viable_prefix_count_by_word": {
            str(word_id): global_frontier_count_by_word[word_id]
            for word_id in sorted(global_frontier_count_by_word)
        },
        "required_next_symbol_count_by_scope_word": {
            f"{scope_code}:{word_id}": required_next_counts[(scope_code, word_id)]
            for scope_code, word_id in sorted(required_next_counts)
        },
        "word_table_sha256": sha_array(word_table),
        "prefix_table_sha256": sha_array(prefix_table),
        "frontier_table_sha256": sha_array(frontier_table),
        "next_symbol_table_sha256": sha_array(next_symbol_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    realizability = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability@1",
        "object": "d20",
        "search_rule": {
            "target_words": "the two abstract x1-tail overhead-2 symbolic completions from the symbol-state obstruction",
            "rooted_scope": "all open carrier paths starting at carrier 12 with the exact selected-symbol word",
            "global_scope": "all open carrier paths starting at any residual carrier with the exact selected-symbol word",
            "edge_rule": "a carrier edge realizes a symbol if its shared active atom set contains an atom with that symbol id",
        },
        "summary": {
            "rooted_full_realization_count": observable_values[
                "rooted_full_realization_count"
            ],
            "global_full_realization_count": observable_values[
                "global_full_realization_count"
            ],
            "word0_first_missing_prefix_length": first_missing_by_word[0],
            "word1_first_missing_prefix_length": first_missing_by_word[1],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_CARRIER_REALIZABILITY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "neither abstract x1-tail overhead-2 word is realized as a carrier path from carrier 12",
            "neither word is realized as an open carrier path starting from any carrier in the 14-node residual cell complex",
            "word x2,x1,x4,x2,x5 dies at the fourth selected symbol: after x2,x1,x4 no frontier carrier has an outgoing x2 contact",
            "word x2,x1,x5,x2,x4 dies at the fifth selected symbol: after x2,x1,x5,x2 no frontier carrier has an outgoing x4 contact",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The two abstract x1-tail overhead-2 words are not carrier-realizable "
            "in the residual cell complex, even as open paths from arbitrary "
            "carrier starts. Their absence is a carrier-contact obstruction, "
            "not only a bounded first-return artifact."
        ),
        "stage_protocol": {
            "draft": "enumerate exact symbol-labelled carrier paths for the two overhead-2 words from carrier 12 and from all carriers",
            "witness": "materialize prefix counts, last viable frontier paths, and available next-symbol counts",
            "coherence": "compare the required next symbol at each death frontier with all residual carrier contacts",
            "closure": "certify zero rooted and zero global carrier realizations for both symbolic overhead-2 words",
            "emit": "emit realizability JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "symbol_state_report": input_entry(
                SYMBOL_STATE_REPORT,
                {
                    "status": symbol_state_report.get("status"),
                    "certificate_sha256": symbol_state_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "symbol_state_json": input_entry(SYMBOL_STATE_JSON),
            "symbol_state_tables": input_entry(SYMBOL_STATE_TABLES),
            "symbol_state_forbidden_transitions": input_entry(SYMBOL_STATE_FORBIDDEN),
            "symbol_state_certificate": input_entry(SYMBOL_STATE_CERTIFICATE),
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
            "signature_boundary_spine_aperture_overhead2_carrier_realizability": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_carrier_realizability.json"
            ),
            "aperture_overhead2_carrier_words_csv": relpath(
                OUT_DIR / "aperture_overhead2_carrier_words.csv"
            ),
            "aperture_overhead2_carrier_prefixes_csv": relpath(
                OUT_DIR / "aperture_overhead2_carrier_prefixes.csv"
            ),
            "aperture_overhead2_carrier_frontier_paths_csv": relpath(
                OUT_DIR / "aperture_overhead2_carrier_frontier_paths.csv"
            ),
            "aperture_overhead2_carrier_next_symbols_csv": relpath(
                OUT_DIR / "aperture_overhead2_carrier_next_symbols.csv"
            ),
            "aperture_overhead2_carrier_observables_csv": relpath(
                OUT_DIR / "aperture_overhead2_carrier_observables.csv"
            ),
            "signature_boundary_spine_aperture_overhead2_carrier_realizability_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_carrier_realizability_tables.npz"
            ),
            "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all exact selected-symbol carrier paths for the two overhead-2 words starting at carrier 12",
                "all exact selected-symbol carrier paths for the two overhead-2 words starting at any residual carrier",
                "the first carrier-contact death frontier for each word",
                "that both symbolic overhead-2 words have zero carrier realization in the residual cell complex",
            ],
            "does_not_certify_because_not_required": [
                "approximate words that insert extra symbols inside the overhead-2 word",
                "changing the residual carrier-mask cell complex",
                "changing the symbolic associativity canonicalization",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Compute the minimal carrier-symbol edit distance from each "
            "unrealizable overhead-2 word to a realizable x1-tail word, then "
            "certify the least extra contact that repairs the dead frontier "
            "and compare its trace overhead against the existing overhead-3 "
            "tail class."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_carrier_realizability_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified symbol-state, residual cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "enumerate exact symbol-labelled carrier paths for both overhead-2 words from carrier 12",
            "enumerate exact symbol-labelled carrier paths for both overhead-2 words from every residual carrier",
            "materialize frontier paths and available next-symbol counts at the first missing contact",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_overhead2_carrier_realizability": realizability,
        "aperture_overhead2_carrier_words_csv": csv_text(WORD_COLUMNS, word_rows),
        "aperture_overhead2_carrier_prefixes_csv": csv_text(
            PREFIX_COLUMNS,
            prefix_rows,
        ),
        "aperture_overhead2_carrier_frontier_paths_csv": csv_text(
            FRONTIER_COLUMNS,
            all_frontier_rows,
        ),
        "aperture_overhead2_carrier_next_symbols_csv": csv_text(
            NEXT_SYMBOL_COLUMNS,
            next_symbol_rows,
        ),
        "aperture_overhead2_carrier_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "word_table": word_table,
        "prefix_table": prefix_table,
        "frontier_table": frontier_table,
        "next_symbol_table": next_symbol_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_overhead2_carrier_realizability.json",
        payloads["signature_boundary_spine_aperture_overhead2_carrier_realizability"],
    )
    (OUT_DIR / "aperture_overhead2_carrier_words.csv").write_text(
        payloads["aperture_overhead2_carrier_words_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_carrier_prefixes.csv").write_text(
        payloads["aperture_overhead2_carrier_prefixes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_carrier_frontier_paths.csv").write_text(
        payloads["aperture_overhead2_carrier_frontier_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_carrier_next_symbols.csv").write_text(
        payloads["aperture_overhead2_carrier_next_symbols_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_carrier_observables.csv").write_text(
        payloads["aperture_overhead2_carrier_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_carrier_realizability_tables.npz",
        word_table=payloads["word_table"],
        prefix_table=payloads["prefix_table"],
        frontier_table=payloads["frontier_table"],
        next_symbol_table=payloads["next_symbol_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_overhead2_carrier_realizability_certificate"
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
                "target_words": witness["target_words"],
                "rooted_full_realization_count": witness[
                    "rooted_full_realization_count"
                ],
                "global_full_realization_count": witness[
                    "global_full_realization_count"
                ],
                "first_missing_prefix_length_by_word": witness[
                    "first_missing_prefix_length_by_word"
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
