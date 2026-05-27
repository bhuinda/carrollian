from __future__ import annotations

import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        OUT_DIR as BOUNDED_BACKTRACK_DIR,
        STATUS as BOUNDED_BACKTRACK_STATUS,
        STRICT_APERTURE_NODE_ID,
        TAIL_VALLEY_NODE_ID,
        TRACE_BOUNDARY_NODE_ID,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        GEODESIC_MIN_AFTER_NODE42,
        PREFIX_SYMBOLS,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        X1_SYMBOL_ID,
        X2_SYMBOL_ID,
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
    from derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        OUT_DIR as BOUNDED_BACKTRACK_DIR,
        STATUS as BOUNDED_BACKTRACK_STATUS,
        STRICT_APERTURE_NODE_ID,
        TAIL_VALLEY_NODE_ID,
        TRACE_BOUNDARY_NODE_ID,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        GEODESIC_MIN_AFTER_NODE42,
        PREFIX_SYMBOLS,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        X1_SYMBOL_ID,
        X2_SYMBOL_ID,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_SYMBOL_STATE_OBSTRUCTION_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

BOUNDED_BACKTRACK_REPORT = BOUNDED_BACKTRACK_DIR / "report.json"
BOUNDED_BACKTRACK_JSON = (
    BOUNDED_BACKTRACK_DIR
    / "signature_boundary_spine_aperture_bounded_backtrack_search.json"
)
BOUNDED_BACKTRACK_CANDIDATES = (
    BOUNDED_BACKTRACK_DIR / "aperture_bounded_backtrack_candidates.csv"
)
BOUNDED_BACKTRACK_TABLES = (
    BOUNDED_BACKTRACK_DIR
    / "signature_boundary_spine_aperture_bounded_backtrack_search_tables.npz"
)
BOUNDED_BACKTRACK_CERTIFICATE = (
    BOUNDED_BACKTRACK_DIR
    / "signature_boundary_spine_aperture_bounded_backtrack_search_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_symbol_state_obstruction.py"
)

POST_X2_STATE = (STRICT_APERTURE_NODE_ID, PREFIX_SYMBOLS[1], X2_SYMBOL_ID)
TAIL_STATE = (TAIL_VALLEY_NODE_ID, X2_SYMBOL_ID, X1_SYMBOL_ID)
LOWER_OVERHEAD_TAIL_WORDS = [
    (2, 1, 4, 2, 5),
    (2, 1, 5, 2, 4),
]

STATE_COLUMNS = [
    "state_id",
    "trace_node_id",
    "suffix_left_symbol_id",
    "suffix_right_symbol_id",
    "visit_count",
    "distinct_candidate_count",
    "start_state_flag",
    "post_x2_state_flag",
    "node27_state_flag",
    "node44_state_flag",
]

TRANSITION_COLUMNS = [
    "transition_id",
    "source_state_id",
    "target_state_id",
    "source_trace_node_id",
    "source_suffix_left_symbol_id",
    "source_suffix_right_symbol_id",
    "label_symbol_id",
    "raw_target_node_id",
    "target_trace_node_id",
    "target_suffix_left_symbol_id",
    "target_suffix_right_symbol_id",
    "duplicate_trace_flag",
    "node27_transition_flag",
    "node44_transition_flag",
    "observed_transition_count",
    "distinct_candidate_count",
]

POST_X2_OUTGOING_COLUMNS = [
    "outgoing_id",
    "label_symbol_id",
    "target_suffix_left_symbol_id",
    "target_suffix_right_symbol_id",
    "raw_target_node_id",
    "target_trace_node_id",
    "signature_union_count",
    "sector_coverage_count",
    "preserves_immediate_x1_flag",
    "avoids_node27_flag",
    "keeps_geodesic_floor_flag",
    "canonical_node44_flag",
    "observed_bounded_transition_count",
    "ambient_edge_from_42_exists_flag",
    "signature_valley_depth",
]

COMPLETION_COLUMNS = [
    "completion_id",
    "completion_class_code",
    "completion_length_after_x2",
    "symbol_0_id",
    "symbol_1_id",
    "symbol_2_id",
    "symbol_3_id",
    "raw_node_0_id",
    "raw_node_1_id",
    "raw_node_2_id",
    "raw_node_3_id",
    "trace_edge_count",
    "trace_detour_overhead",
    "trace_min_signature_after_node42",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "preserves_x1_tail_flag",
    "skips_node27_flag",
    "bounded_exact_word_count",
    "bounded_prefix_word_count",
]

FORBIDDEN_COLUMNS = [
    "forbidden_id",
    "word_symbol_0_id",
    "word_symbol_1_id",
    "word_symbol_2_id",
    "word_symbol_3_id",
    "word_symbol_4_id",
    "first_missing_transition_rank",
    "source_trace_node_id",
    "source_suffix_left_symbol_id",
    "source_suffix_right_symbol_id",
    "label_symbol_id",
    "raw_target_node_id",
    "target_trace_node_id",
    "target_suffix_left_symbol_id",
    "target_suffix_right_symbol_id",
    "duplicate_trace_flag",
    "source_state_observed_count",
    "observed_transition_count",
    "bounded_exact_word_count",
    "bounded_prefix_word_count",
    "trace_detour_overhead",
    "signature_valley_depth",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "bounded_candidate_count": 0,
    "state_count": 1,
    "observed_transition_count": 2,
    "trace_sequence_count": 3,
    "selected_symbol_word_count": 4,
    "post_x2_observed_transition_count": 5,
    "x1_skip_transition_count": 6,
    "ambient_42_to_44_edge_exists": 7,
    "ambient_42_to_44_target_added_symbol": 8,
    "no_tail_min_completion_length_after_x2": 9,
    "no_tail_min_completion_count": 10,
    "x1_tail_min_completion_length_after_x2": 11,
    "x1_tail_min_completion_count": 12,
    "x1_tail_symbolic_overhead2_count": 13,
    "carrier_realized_symbolic_overhead2_count": 14,
    "minimal_forbidden_transition_count": 15,
}


def read_candidate_rows(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def candidate_symbols(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"selected_symbol_{index}_id"])
        for index in range(int(row["walk_length"]))
    )


def transition_key(
    source_node: int,
    suffix: tuple[int, int],
    label: int,
    assoc_by_word: dict[tuple[int, int, int], dict[str, int]],
) -> tuple[int, int, int, int, int, int, int, int, int]:
    assoc = assoc_by_word[(suffix[0], suffix[1], label)]
    raw_target = int(assoc["canonical_triple_id"])
    duplicate = int(source_node == raw_target)
    target_node = source_node if duplicate else raw_target
    target_suffix = (suffix[1], label)
    return (
        source_node,
        suffix[0],
        suffix[1],
        label,
        raw_target,
        target_node,
        target_suffix[0],
        target_suffix[1],
        duplicate,
    )


def build_observed_quotient(
    rows: list[dict[str, int]],
    assoc_by_word: dict[tuple[int, int, int], dict[str, int]],
    rewrite_edge_by_pair: dict[tuple[int, int], dict[str, int]],
) -> dict[str, Any]:
    state_order: list[tuple[int, int, int]] = []
    state_visits: Counter[tuple[int, int, int]] = Counter()
    state_candidates: defaultdict[tuple[int, int, int], set[int]] = defaultdict(set)
    transition_order: list[tuple[int, int, int, int, int, int, int, int, int]] = []
    transition_visits: Counter[
        tuple[int, int, int, int, int, int, int, int, int]
    ] = Counter()
    transition_candidates: defaultdict[
        tuple[int, int, int, int, int, int, int, int, int], set[int]
    ] = defaultdict(set)
    trace_sequences: Counter[tuple[int, ...]] = Counter()
    symbol_words: Counter[tuple[int, ...]] = Counter()

    def add_state(state: tuple[int, int, int], candidate_id: int) -> None:
        if state not in state_visits:
            state_order.append(state)
        state_visits[state] += 1
        state_candidates[state].add(candidate_id)

    def add_transition(
        key: tuple[int, int, int, int, int, int, int, int, int],
        candidate_id: int,
    ) -> None:
        if key not in transition_visits:
            transition_order.append(key)
        transition_visits[key] += 1
        transition_candidates[key].add(candidate_id)

    for row in rows:
        candidate_id = int(row["walk_candidate_id"])
        symbols = candidate_symbols(row)
        raw_windows, trace_nodes, _trace_signatures, _metrics = build_trace(
            symbols,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        trace_sequences[tuple(trace_nodes)] += 1
        symbol_words[symbols] += 1
        current_node = TRACE_BOUNDARY_NODE_ID
        suffix = (PREFIX_SYMBOLS[0], PREFIX_SYMBOLS[1])
        add_state((current_node, suffix[0], suffix[1]), candidate_id)
        for window in raw_windows:
            label = int(window["right_symbol_id"])
            key = transition_key(current_node, suffix, label, assoc_by_word)
            add_transition(key, candidate_id)
            current_node = key[5]
            suffix = (key[6], key[7])
            add_state((current_node, suffix[0], suffix[1]), candidate_id)
            if key[4] == APERTURE_NODE_ID:
                break

    state_ids = {state: index for index, state in enumerate(state_order)}
    state_rows = []
    for state in state_order:
        state_rows.append(
            {
                "state_id": state_ids[state],
                "trace_node_id": state[0],
                "suffix_left_symbol_id": state[1],
                "suffix_right_symbol_id": state[2],
                "visit_count": state_visits[state],
                "distinct_candidate_count": len(state_candidates[state]),
                "start_state_flag": int(
                    state
                    == (
                        TRACE_BOUNDARY_NODE_ID,
                        PREFIX_SYMBOLS[0],
                        PREFIX_SYMBOLS[1],
                    )
                ),
                "post_x2_state_flag": int(state == POST_X2_STATE),
                "node27_state_flag": int(state[0] == TAIL_VALLEY_NODE_ID),
                "node44_state_flag": int(state[0] == APERTURE_NODE_ID),
            }
        )
    transition_rows = []
    for transition in transition_order:
        source_state = (transition[0], transition[1], transition[2])
        target_state = (transition[5], transition[6], transition[7])
        transition_rows.append(
            {
                "transition_id": len(transition_rows),
                "source_state_id": state_ids[source_state],
                "target_state_id": state_ids[target_state],
                "source_trace_node_id": transition[0],
                "source_suffix_left_symbol_id": transition[1],
                "source_suffix_right_symbol_id": transition[2],
                "label_symbol_id": transition[3],
                "raw_target_node_id": transition[4],
                "target_trace_node_id": transition[5],
                "target_suffix_left_symbol_id": transition[6],
                "target_suffix_right_symbol_id": transition[7],
                "duplicate_trace_flag": transition[8],
                "node27_transition_flag": int(transition[4] == TAIL_VALLEY_NODE_ID),
                "node44_transition_flag": int(transition[4] == APERTURE_NODE_ID),
                "observed_transition_count": transition_visits[transition],
                "distinct_candidate_count": len(transition_candidates[transition]),
            }
        )
    return {
        "state_rows": state_rows,
        "transition_rows": transition_rows,
        "transition_visits": transition_visits,
        "state_visits": state_visits,
        "trace_sequences": trace_sequences,
        "symbol_words": symbol_words,
    }


def word_count(symbol_words: Counter[tuple[int, ...]], word: tuple[int, ...]) -> int:
    return int(symbol_words.get(word, 0))


def prefix_count(symbol_words: Counter[tuple[int, ...]], word: tuple[int, ...]) -> int:
    return sum(count for symbols, count in symbol_words.items() if symbols[: len(word)] == word)


def path_raw_nodes(
    source_node: int,
    suffix: tuple[int, int],
    labels: tuple[int, ...],
    assoc_by_word: dict[tuple[int, int, int], dict[str, int]],
) -> list[int]:
    current = source_node
    raw_nodes: list[int] = []
    for label in labels:
        key = transition_key(current, suffix, label, assoc_by_word)
        raw_nodes.append(key[4])
        current = key[5]
        suffix = (key[6], key[7])
    return raw_nodes


def build_payloads() -> dict[str, Any]:
    bounded_report = load_json(BOUNDED_BACKTRACK_REPORT)
    bounded_search = load_json(BOUNDED_BACKTRACK_JSON)
    bounded_certificate = load_json(BOUNDED_BACKTRACK_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    bounded_tables = np.load(BOUNDED_BACKTRACK_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    bounded_candidate_table = np.asarray(
        bounded_tables["candidate_table"],
        dtype=np.int64,
    )
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    candidate_rows = read_candidate_rows(BOUNDED_BACKTRACK_CANDIDATES)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    assoc_by_word = associativity_lookup(associativity_rows)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }
    quotient = build_observed_quotient(
        candidate_rows,
        assoc_by_word,
        rewrite_edge_by_pair,
    )
    state_rows = quotient["state_rows"]
    transition_rows = quotient["transition_rows"]
    transition_visits = quotient["transition_visits"]
    state_visits = quotient["state_visits"]
    trace_sequences = quotient["trace_sequences"]
    symbol_words = quotient["symbol_words"]
    state_table = table_from_rows(STATE_COLUMNS, state_rows)
    transition_table = table_from_rows(TRANSITION_COLUMNS, transition_rows)

    post_x2_outgoing_rows = []
    for label in range(6):
        key = transition_key(
            STRICT_APERTURE_NODE_ID,
            (PREFIX_SYMBOLS[1], X2_SYMBOL_ID),
            label,
            assoc_by_word,
        )
        assoc = assoc_by_word[(PREFIX_SYMBOLS[1], X2_SYMBOL_ID, label)]
        ambient_edge_exists = key[4] == STRICT_APERTURE_NODE_ID or edge_key(
            STRICT_APERTURE_NODE_ID,
            key[4],
        ) in rewrite_edge_by_pair
        post_x2_outgoing_rows.append(
            {
                "outgoing_id": label,
                "label_symbol_id": label,
                "target_suffix_left_symbol_id": key[6],
                "target_suffix_right_symbol_id": key[7],
                "raw_target_node_id": key[4],
                "target_trace_node_id": key[5],
                "signature_union_count": int(assoc["signature_union_count"]),
                "sector_coverage_count": int(assoc["sector_coverage_count"]),
                "preserves_immediate_x1_flag": int(label == X1_SYMBOL_ID),
                "avoids_node27_flag": int(key[4] != TAIL_VALLEY_NODE_ID),
                "keeps_geodesic_floor_flag": int(
                    int(assoc["signature_union_count"]) >= GEODESIC_MIN_AFTER_NODE42
                ),
                "canonical_node44_flag": int(key[4] == APERTURE_NODE_ID),
                "observed_bounded_transition_count": int(transition_visits[key]),
                "ambient_edge_from_42_exists_flag": int(ambient_edge_exists),
                "signature_valley_depth": max(
                    0,
                    GEODESIC_MIN_AFTER_NODE42 - int(assoc["signature_union_count"]),
                ),
            }
        )
    post_x2_outgoing_table = table_from_rows(
        POST_X2_OUTGOING_COLUMNS,
        post_x2_outgoing_rows,
    )

    no_tail_completions: list[tuple[int, ...]] = []
    for labels in itertools.product(range(6), repeat=2):
        if labels[0] == X1_SYMBOL_ID:
            continue
        raw_nodes = path_raw_nodes(
            STRICT_APERTURE_NODE_ID,
            (PREFIX_SYMBOLS[1], X2_SYMBOL_ID),
            labels,
            assoc_by_word,
        )
        if raw_nodes[-1] == APERTURE_NODE_ID:
            no_tail_completions.append(labels)
    x1_tail_completions: list[tuple[int, ...]] = []
    for labels in itertools.product(range(6), repeat=3):
        raw_nodes = path_raw_nodes(
            TAIL_VALLEY_NODE_ID,
            (X2_SYMBOL_ID, X1_SYMBOL_ID),
            labels,
            assoc_by_word,
        )
        if raw_nodes[-1] == APERTURE_NODE_ID:
            x1_tail_completions.append((X1_SYMBOL_ID, *labels))

    completion_rows = []
    for class_code, completions in [(0, no_tail_completions), (1, x1_tail_completions)]:
        for labels in completions:
            symbols = (X2_SYMBOL_ID, *labels)
            raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
                symbols,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
            raw_nodes = [
                int(window["canonical_triple_id"])
                for window in raw_windows[1 if class_code == 0 else 0 :]
            ]
            label_values = list(labels)
            completion_rows.append(
                {
                    "completion_id": len(completion_rows),
                    "completion_class_code": class_code,
                    "completion_length_after_x2": len(labels),
                    "symbol_0_id": label_values[0] if len(label_values) > 0 else -1,
                    "symbol_1_id": label_values[1] if len(label_values) > 1 else -1,
                    "symbol_2_id": label_values[2] if len(label_values) > 2 else -1,
                    "symbol_3_id": label_values[3] if len(label_values) > 3 else -1,
                    "raw_node_0_id": raw_nodes[0] if len(raw_nodes) > 0 else -1,
                    "raw_node_1_id": raw_nodes[1] if len(raw_nodes) > 1 else -1,
                    "raw_node_2_id": raw_nodes[2] if len(raw_nodes) > 2 else -1,
                    "raw_node_3_id": raw_nodes[3] if len(raw_nodes) > 3 else -1,
                    "trace_edge_count": int(metrics["trace_edge_count"]),
                    "trace_detour_overhead": int(metrics["trace_detour_overhead"]),
                    "trace_min_signature_after_node42": int(
                        metrics["trace_min_signature_after_node42"]
                    ),
                    "signature_valley_depth": int(metrics["signature_valley_depth"]),
                    "metric_gromov_delta_twice": int(
                        metrics["metric_gromov_delta_twice"]
                    ),
                    "preserves_x1_tail_flag": int(class_code == 1),
                    "skips_node27_flag": int(TAIL_VALLEY_NODE_ID not in trace_nodes),
                    "bounded_exact_word_count": word_count(symbol_words, symbols),
                    "bounded_prefix_word_count": prefix_count(symbol_words, symbols),
                }
            )
    completion_table = table_from_rows(COMPLETION_COLUMNS, completion_rows)

    forbidden_rows = []
    for word in LOWER_OVERHEAD_TAIL_WORDS:
        raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
            word,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        current_node = TRACE_BOUNDARY_NODE_ID
        suffix = (PREFIX_SYMBOLS[0], PREFIX_SYMBOLS[1])
        first_missing = None
        first_missing_key = None
        for rank, window in enumerate(raw_windows):
            label = int(window["right_symbol_id"])
            key = transition_key(current_node, suffix, label, assoc_by_word)
            if transition_visits[key] == 0 and first_missing is None:
                first_missing = rank
                first_missing_key = key
                break
            current_node = key[5]
            suffix = (key[6], key[7])
            if key[4] == APERTURE_NODE_ID:
                break
        if first_missing is None or first_missing_key is None:
            raise AssertionError(f"lower-overhead word unexpectedly observed: {word}")
        source_state = (
            first_missing_key[0],
            first_missing_key[1],
            first_missing_key[2],
        )
        forbidden_rows.append(
            {
                "forbidden_id": len(forbidden_rows),
                "word_symbol_0_id": word[0],
                "word_symbol_1_id": word[1],
                "word_symbol_2_id": word[2],
                "word_symbol_3_id": word[3],
                "word_symbol_4_id": word[4],
                "first_missing_transition_rank": first_missing,
                "source_trace_node_id": first_missing_key[0],
                "source_suffix_left_symbol_id": first_missing_key[1],
                "source_suffix_right_symbol_id": first_missing_key[2],
                "label_symbol_id": first_missing_key[3],
                "raw_target_node_id": first_missing_key[4],
                "target_trace_node_id": first_missing_key[5],
                "target_suffix_left_symbol_id": first_missing_key[6],
                "target_suffix_right_symbol_id": first_missing_key[7],
                "duplicate_trace_flag": first_missing_key[8],
                "source_state_observed_count": int(state_visits[source_state]),
                "observed_transition_count": int(transition_visits[first_missing_key]),
                "bounded_exact_word_count": word_count(symbol_words, word),
                "bounded_prefix_word_count": prefix_count(symbol_words, word),
                "trace_detour_overhead": int(metrics["trace_detour_overhead"]),
                "signature_valley_depth": int(metrics["signature_valley_depth"]),
            }
        )
    forbidden_table = table_from_rows(FORBIDDEN_COLUMNS, forbidden_rows)

    ambient_geodesic_edge = rewrite_edge_by_pair[
        edge_key(STRICT_APERTURE_NODE_ID, APERTURE_NODE_ID)
    ]
    x1_skip_transition_count = sum(
        int(row["preserves_immediate_x1_flag"] == 1 and row["avoids_node27_flag"] == 1)
        for row in post_x2_outgoing_rows
    )
    symbolic_overhead2_rows = [
        row
        for row in completion_rows
        if int(row["preserves_x1_tail_flag"]) == 1
        and int(row["trace_detour_overhead"]) < BASELINE_TAIL_OVERHEAD
    ]
    observable_values = {
        "bounded_candidate_count": len(candidate_rows),
        "state_count": len(state_rows),
        "observed_transition_count": len(transition_rows),
        "trace_sequence_count": len(trace_sequences),
        "selected_symbol_word_count": len(symbol_words),
        "post_x2_observed_transition_count": sum(
            int(row["observed_bounded_transition_count"] > 0)
            for row in post_x2_outgoing_rows
        ),
        "x1_skip_transition_count": x1_skip_transition_count,
        "ambient_42_to_44_edge_exists": int(
            edge_key(STRICT_APERTURE_NODE_ID, APERTURE_NODE_ID)
            in rewrite_edge_by_pair
        ),
        "ambient_42_to_44_target_added_symbol": int(
            ambient_geodesic_edge["target_added_symbol_id"]
        ),
        "no_tail_min_completion_length_after_x2": min(
            len(path) for path in no_tail_completions
        ),
        "no_tail_min_completion_count": len(no_tail_completions),
        "x1_tail_min_completion_length_after_x2": min(
            len(path) for path in x1_tail_completions
        ),
        "x1_tail_min_completion_count": len(x1_tail_completions),
        "x1_tail_symbolic_overhead2_count": len(symbolic_overhead2_rows),
        "carrier_realized_symbolic_overhead2_count": sum(
            int(row["bounded_prefix_word_count"]) for row in symbolic_overhead2_rows
        ),
        "minimal_forbidden_transition_count": len(forbidden_rows),
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
        "bounded_backtrack_report_certified": bounded_report.get("status")
        == BOUNDED_BACKTRACK_STATUS,
        "bounded_backtrack_certificate_certified": bounded_certificate.get("status")
        == BOUNDED_BACKTRACK_STATUS,
        "bounded_backtrack_schema_available": bounded_search.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1",
        "bounded_candidate_table_shape_is_1287_by_60": tuple(
            bounded_candidate_table.shape
        )
        == (1287, 60),
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
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "observed_state_count_is_89": len(state_rows) == 89,
        "observed_transition_count_is_169": len(transition_rows) == 169,
        "observed_trace_sequence_count_is_85": len(trace_sequences) == 85,
        "observed_symbol_word_count_is_126": len(symbol_words) == 126,
        "post_x2_source_has_only_x1_observed_in_bounded_search": [
            row["observed_bounded_transition_count"] for row in post_x2_outgoing_rows
        ]
        == [0, 1287, 0, 0, 0, 0],
        "x1_transition_forces_node27": post_x2_outgoing_rows[X1_SYMBOL_ID][
            "raw_target_node_id"
        ]
        == TAIL_VALLEY_NODE_ID,
        "no_x1_labeled_skip_transition_exists": x1_skip_transition_count == 0,
        "ambient_42_to_44_edge_exists_but_requires_x4_addition": observable_values[
            "ambient_42_to_44_edge_exists"
        ]
        == 1
        and observable_values["ambient_42_to_44_target_added_symbol"] == 4,
        "no_tail_symbolic_min_length_is_2_with_two_paths": observable_values[
            "no_tail_min_completion_length_after_x2"
        ]
        == 2
        and observable_values["no_tail_min_completion_count"] == 2,
        "x1_tail_symbolic_min_length_is_4_with_six_paths": observable_values[
            "x1_tail_min_completion_length_after_x2"
        ]
        == 4
        and observable_values["x1_tail_min_completion_count"] == 6,
        "symbolic_x1_tail_has_two_overhead2_paths": observable_values[
            "x1_tail_symbolic_overhead2_count"
        ]
        == 2,
        "carrier_bounded_search_realizes_no_symbolic_overhead2_path": observable_values[
            "carrier_realized_symbolic_overhead2_count"
        ]
        == 0,
        "minimal_forbidden_transition_count_is_2": len(forbidden_rows) == 2,
        "first_forbidden_transition_is_duplicate_node28_x2": forbidden_rows[0]
        == {
            "forbidden_id": 0,
            "word_symbol_0_id": 2,
            "word_symbol_1_id": 1,
            "word_symbol_2_id": 4,
            "word_symbol_3_id": 2,
            "word_symbol_4_id": 5,
            "first_missing_transition_rank": 3,
            "source_trace_node_id": 28,
            "source_suffix_left_symbol_id": 1,
            "source_suffix_right_symbol_id": 4,
            "label_symbol_id": 2,
            "raw_target_node_id": 28,
            "target_trace_node_id": 28,
            "target_suffix_left_symbol_id": 4,
            "target_suffix_right_symbol_id": 2,
            "duplicate_trace_flag": 1,
            "source_state_observed_count": 410,
            "observed_transition_count": 0,
            "bounded_exact_word_count": 0,
            "bounded_prefix_word_count": 0,
            "trace_detour_overhead": 2,
            "signature_valley_depth": BASELINE_TAIL_VALLEY,
        },
        "state_table_shape_is_89_by_codebook": tuple(state_table.shape)
        == (89, len(STATE_COLUMNS)),
        "transition_table_shape_is_169_by_codebook": tuple(transition_table.shape)
        == (169, len(TRANSITION_COLUMNS)),
        "post_x2_outgoing_table_shape_is_6_by_codebook": tuple(
            post_x2_outgoing_table.shape
        )
        == (6, len(POST_X2_OUTGOING_COLUMNS)),
        "completion_table_shape_is_8_by_codebook": tuple(completion_table.shape)
        == (8, len(COMPLETION_COLUMNS)),
        "forbidden_table_shape_is_2_by_codebook": tuple(forbidden_table.shape)
        == (2, len(FORBIDDEN_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "bounded_candidate_count": len(candidate_rows),
        "observed_state_count": len(state_rows),
        "observed_transition_count": len(transition_rows),
        "observed_trace_sequence_count": len(trace_sequences),
        "observed_symbol_word_count": len(symbol_words),
        "post_x2_outgoing": {
            str(row["label_symbol_id"]): {
                "raw_target_node_id": row["raw_target_node_id"],
                "signature_union_count": row["signature_union_count"],
                "observed_bounded_transition_count": row[
                    "observed_bounded_transition_count"
                ],
            }
            for row in post_x2_outgoing_rows
        },
        "node27_skip_possible_with_immediate_x1": False,
        "ambient_42_to_44_edge": {
            "exists": True,
            "target_added_symbol_id": observable_values[
                "ambient_42_to_44_target_added_symbol"
            ],
            "required_tail_symbol_id": X1_SYMBOL_ID,
        },
        "symbolic_x1_tail_overhead2_words": [
            list(word) for word in LOWER_OVERHEAD_TAIL_WORDS
        ],
        "minimal_forbidden_transitions": forbidden_rows,
        "state_table_sha256": sha_array(state_table),
        "transition_table_sha256": sha_array(transition_table),
        "post_x2_outgoing_table_sha256": sha_array(post_x2_outgoing_table),
        "completion_table_sha256": sha_array(completion_table),
        "forbidden_table_sha256": sha_array(forbidden_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    symbol_state_obstruction = {
        "schema": "c985.d20_signature_boundary_spine_aperture_symbol_state_obstruction@1",
        "object": "d20",
        "search_rule": {
            "quotient": "bounded carrier candidates quotiented by anchored trace node and selected-symbol suffix",
            "source_state": "post-x2 state (trace node 42, suffix x3,x2)",
            "tail_constraint": "the next selected symbol is x1",
            "obstruction": "the x1-labelled deterministic transition lands at node27; the ambient 42->44 geodesic edge requires adding x4, not x1",
        },
        "summary": {
            "observed_state_count": len(state_rows),
            "observed_transition_count": len(transition_rows),
            "node27_skip_possible_with_immediate_x1": False,
            "symbolic_x1_tail_overhead2_count": len(symbolic_overhead2_rows),
            "carrier_realized_symbolic_overhead2_count": observable_values[
                "carrier_realized_symbolic_overhead2_count"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_symbol_state_obstruction_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_SYMBOL_STATE_OBSTRUCTION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the bounded carrier quotient has 89 anchored symbol states and 169 observed transitions",
            "from the post-x2 state, the immediate x1 transition is the only bounded observed outgoing transition and it deterministically lands at node27",
            "the ambient geodesic edge 42 -> 44 exists, but its rewrite label adds x4 rather than the required x1 tail symbol",
            "the pure symbol automaton has two x1-tail overhead-2 completions, but the bounded carrier quotient realizes neither; the earliest missing move is the duplicate node28 transition labelled x2 after x2,x1,x4",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_symbol_state_obstruction@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The symbol-state quotient proves that immediate x1 after x2 "
            "cannot skip node27. A lower-overhead x1-tail symbolic completion "
            "exists only in the abstract symbol automaton, and its first "
            "needed duplicate-node transition is absent from the bounded "
            "carrier quotient."
        ),
        "stage_protocol": {
            "draft": "quotient bounded carrier candidates by anchored trace node and selected-symbol suffix",
            "witness": "materialize observed symbol-state transitions, post-x2 outgoing alternatives, minimal completions, and missing lower-overhead moves",
            "coherence": "compare deterministic symbolic transitions with the ambient rewrite edge 42->44 and bounded carrier realization counts",
            "closure": "certify node27 cannot be skipped by an immediate x1 transition and locate the first carrier-forbidden lower-overhead symbolic transition",
            "emit": "emit symbol-state JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "bounded_backtrack_report": input_entry(
                BOUNDED_BACKTRACK_REPORT,
                {
                    "status": bounded_report.get("status"),
                    "certificate_sha256": bounded_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "bounded_backtrack_json": input_entry(BOUNDED_BACKTRACK_JSON),
            "bounded_backtrack_candidates": input_entry(
                BOUNDED_BACKTRACK_CANDIDATES
            ),
            "bounded_backtrack_tables": input_entry(BOUNDED_BACKTRACK_TABLES),
            "bounded_backtrack_certificate": input_entry(
                BOUNDED_BACKTRACK_CERTIFICATE
            ),
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
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_symbol_state_obstruction": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_symbol_state_obstruction.json"
            ),
            "aperture_symbol_state_states_csv": relpath(
                OUT_DIR / "aperture_symbol_state_states.csv"
            ),
            "aperture_symbol_state_transitions_csv": relpath(
                OUT_DIR / "aperture_symbol_state_transitions.csv"
            ),
            "aperture_symbol_state_post_x2_outgoing_csv": relpath(
                OUT_DIR / "aperture_symbol_state_post_x2_outgoing.csv"
            ),
            "aperture_symbol_state_completions_csv": relpath(
                OUT_DIR / "aperture_symbol_state_completions.csv"
            ),
            "aperture_symbol_state_forbidden_transitions_csv": relpath(
                OUT_DIR / "aperture_symbol_state_forbidden_transitions.csv"
            ),
            "aperture_symbol_state_observables_csv": relpath(
                OUT_DIR / "aperture_symbol_state_observables.csv"
            ),
            "signature_boundary_spine_aperture_symbol_state_obstruction_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_symbol_state_obstruction_tables.npz"
            ),
            "signature_boundary_spine_aperture_symbol_state_obstruction_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_symbol_state_obstruction_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the anchored symbol-state quotient of the 1287 bounded carrier candidates",
                "the six deterministic post-x2 outgoing symbolic alternatives",
                "that immediate x1 after x2 deterministically enters node27",
                "that the ambient 42->44 geodesic edge requires x4 rather than x1",
                "that the two lower-overhead x1-tail symbolic completions are not realized by the bounded carrier quotient",
            ],
            "does_not_certify_because_not_required": [
                "carrier walks beyond the bounded length-seven search",
                "an unrestricted carrier realization search for the two symbolic overhead-2 words",
                "changing the symbolic associativity canonicalization",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Search carrier realizability for the two abstract overhead-2 "
            "tail words x2,x1,x4,x2,x5 and x2,x1,x5,x2,x4 without the "
            "bounded first-return restriction; certify whether the missing "
            "duplicate-node transition is impossible in the residual cell "
            "complex or merely longer-range."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_symbol_state_obstruction_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified bounded-backtrack, rewrite-complex, and symbolic-associativity artifacts",
            "rebuild the bounded carrier quotient by anchored trace node and selected-symbol suffix",
            "enumerate deterministic post-x2 outgoing symbolic alternatives and minimal node44 completions",
            "locate lower-overhead x1-tail symbolic paths and their first missing bounded-carrier transitions",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_symbol_state_obstruction": symbol_state_obstruction,
        "aperture_symbol_state_states_csv": csv_text(STATE_COLUMNS, state_rows),
        "aperture_symbol_state_transitions_csv": csv_text(
            TRANSITION_COLUMNS,
            transition_rows,
        ),
        "aperture_symbol_state_post_x2_outgoing_csv": csv_text(
            POST_X2_OUTGOING_COLUMNS,
            post_x2_outgoing_rows,
        ),
        "aperture_symbol_state_completions_csv": csv_text(
            COMPLETION_COLUMNS,
            completion_rows,
        ),
        "aperture_symbol_state_forbidden_transitions_csv": csv_text(
            FORBIDDEN_COLUMNS,
            forbidden_rows,
        ),
        "aperture_symbol_state_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "state_table": state_table,
        "transition_table": transition_table,
        "post_x2_outgoing_table": post_x2_outgoing_table,
        "completion_table": completion_table,
        "forbidden_table": forbidden_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_symbol_state_obstruction_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_symbol_state_obstruction.json",
        payloads["signature_boundary_spine_aperture_symbol_state_obstruction"],
    )
    (OUT_DIR / "aperture_symbol_state_states.csv").write_text(
        payloads["aperture_symbol_state_states_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_symbol_state_transitions.csv").write_text(
        payloads["aperture_symbol_state_transitions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_symbol_state_post_x2_outgoing.csv").write_text(
        payloads["aperture_symbol_state_post_x2_outgoing_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_symbol_state_completions.csv").write_text(
        payloads["aperture_symbol_state_completions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_symbol_state_forbidden_transitions.csv").write_text(
        payloads["aperture_symbol_state_forbidden_transitions_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_symbol_state_observables.csv").write_text(
        payloads["aperture_symbol_state_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_symbol_state_obstruction_tables.npz",
        state_table=payloads["state_table"],
        transition_table=payloads["transition_table"],
        post_x2_outgoing_table=payloads["post_x2_outgoing_table"],
        completion_table=payloads["completion_table"],
        forbidden_table=payloads["forbidden_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_symbol_state_obstruction_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_symbol_state_obstruction_certificate"
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
                "observed_state_count": witness["observed_state_count"],
                "observed_transition_count": witness["observed_transition_count"],
                "node27_skip_possible_with_immediate_x1": witness[
                    "node27_skip_possible_with_immediate_x1"
                ],
                "symbolic_x1_tail_overhead2_words": witness[
                    "symbolic_x1_tail_overhead2_words"
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
