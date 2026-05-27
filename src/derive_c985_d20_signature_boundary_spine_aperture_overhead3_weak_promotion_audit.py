from __future__ import annotations

import csv
import itertools
import json
from collections import Counter
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
        advance_states,
        build_carrier_adjacency,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_edit_repair import (
        CANDIDATE_COLUMNS as EDIT_REPAIR_COLUMNS,
        MAX_WORD_LENGTH as EDIT_MAX_WORD_LENGTH,
        OUT_DIR as EDIT_REPAIR_DIR,
        STATUS as EDIT_REPAIR_STATUS,
        row_word as edit_repair_word,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        TRACE_CLASS_COLUMNS,
        TRACE_NODE_COLUMNS,
        OUT_DIR as TRACE_QUOTIENT_DIR,
        STATUS as TRACE_QUOTIENT_STATUS,
        bounded_word,
        padded,
        read_csv_ints,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit import (
        OUT_DIR as RANK104_DIR,
        STATUS as RANK104_STATUS,
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
        CANDIDATE_COLUMNS as EDIT_REPAIR_COLUMNS,
        MAX_WORD_LENGTH as EDIT_MAX_WORD_LENGTH,
        OUT_DIR as EDIT_REPAIR_DIR,
        STATUS as EDIT_REPAIR_STATUS,
        row_word as edit_repair_word,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        BOUNDED_BACKTRACK_CANDIDATES,
        BOUNDED_BACKTRACK_TABLES,
        TRACE_CLASS_COLUMNS,
        TRACE_NODE_COLUMNS,
        OUT_DIR as TRACE_QUOTIENT_DIR,
        STATUS as TRACE_QUOTIENT_STATUS,
        bounded_word,
        padded,
        read_csv_ints,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_rank104_branch_audit import (
        OUT_DIR as RANK104_DIR,
        STATUS as RANK104_STATUS,
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
    "c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD3_WEAK_PROMOTION_AUDIT_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TRACE_QUOTIENT_REPORT = TRACE_QUOTIENT_DIR / "report.json"
TRACE_QUOTIENT_JSON = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient.json"
)
TRACE_QUOTIENT_CLASSES = TRACE_QUOTIENT_DIR / "aperture_overhead3_trace_classes.csv"
TRACE_QUOTIENT_TABLES = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_tables.npz"
)
TRACE_QUOTIENT_CERTIFICATE = (
    TRACE_QUOTIENT_DIR
    / "signature_boundary_spine_aperture_overhead3_trace_class_quotient_certificate.json"
)

RANK104_REPORT = RANK104_DIR / "report.json"
RANK104_CERTIFICATE = (
    RANK104_DIR / "signature_boundary_spine_aperture_rank104_branch_audit_certificate.json"
)

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
    / "derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit.py"
)

MAX_WORD_LENGTH = EDIT_MAX_WORD_LENGTH
MAX_PROMOTION_SUFFIX_LENGTH = 4
TARGET_TRACE_OVERHEAD = 3

SYMBOL_COLUMNS = [f"symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
PREFIX_SYMBOL_COLUMNS = [
    f"promotion_prefix_symbol_{index}_id" for index in range(MAX_WORD_LENGTH)
]
EXISTING_POST44_SYMBOL_COLUMNS = [
    f"existing_post_node44_symbol_{index}_id" for index in range(MAX_WORD_LENGTH)
]
PROMOTION_SUFFIX_COLUMNS = [
    f"minimal_promotion_suffix_symbol_{index}_id"
    for index in range(MAX_PROMOTION_SUFFIX_LENGTH)
]

PROMOTION_REPAIR_COLUMNS = [
    "promotion_repair_id",
    "edit_repair_candidate_id",
    "target_word_id",
    "edit_distance",
    "word_length",
    *SYMBOL_COLUMNS,
    "trace_class_id",
    "bounded_match_count",
    "bounded_rank_min",
    "bounded_rank_max",
    "pre_aperture_strong_flag",
    "target_consumed_before_node44_flag",
    "nonstrong_weak_flag",
    "nonminimal_weak_flag",
    "first_node44_consumed_symbol_count",
    "promotion_prefix_length",
    *PREFIX_SYMBOL_COLUMNS,
    "existing_post_node44_suffix_length",
    *EXISTING_POST44_SYMBOL_COLUMNS,
    "remaining_target_symbol_count_at_node44",
    "minimal_promotion_suffix_length",
    "minimal_promotion_suffix_count",
    *PROMOTION_SUFFIX_COLUMNS,
    "promotion_closed_path_count",
    "promotion_target_consumed_flag",
    "promotion_closes_to_origin_flag",
    "post_suffix_can_make_pre_aperture_strong_flag",
    "existing_post44_suffix_strictly_longer_than_min_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "selected_weak_bounded_repair_count": 0,
    "selected_nonstrong_repair_count": 1,
    "selected_strong_repair_count": 2,
    "nonminimal_nonstrong_repair_count": 3,
    "minimal_nonstrong_repair_count": 4,
    "nonstrong_x5_promotion_count": 5,
    "strong_x3_closure_promotion_count": 6,
    "post_suffix_strongification_count": 7,
    "class0_selected_count": 8,
    "class1_selected_count": 9,
    "class2_selected_count": 10,
    "bounded_match_total": 11,
    "nonstrong_bounded_match_total": 12,
    "existing_suffix_improvement_count": 13,
}


def edit_repair_rows(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def trace_from_class_row(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(int(row[column]) for column in TRACE_NODE_COLUMNS if row[column] >= 0)


def target_progress(symbols: tuple[int, ...], target: tuple[int, ...]) -> int:
    progress = 0
    for symbol_id in symbols:
        if progress < len(target) and symbol_id == target[progress]:
            progress += 1
    return progress


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


def first_return_closed(
    states: list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
) -> list[tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    return [
        state
        for state in states
        if state[1][-1] == ORIGIN_CARRIER_ID
        and ORIGIN_CARRIER_ID not in state[1][1:-1]
    ]


def minimal_promotion_suffixes(
    prefix: tuple[int, ...],
    target: tuple[int, ...],
    symbol_ids: list[int],
    adjacency: dict[int, list[tuple[int, dict[str, Any]]]],
) -> tuple[int, list[tuple[int, ...]], dict[tuple[int, ...], int]]:
    prefix_states = carrier_paths(prefix, adjacency)
    for suffix_length in range(MAX_PROMOTION_SUFFIX_LENGTH + 1):
        suffixes: list[tuple[int, ...]] = []
        closed_counts: dict[tuple[int, ...], int] = {}
        for suffix in itertools.product(symbol_ids, repeat=suffix_length):
            if target_progress((*prefix, *suffix), target) != len(target):
                continue
            closed = first_return_closed(extend_states(prefix_states, suffix, adjacency))
            if closed:
                suffixes.append(suffix)
                closed_counts[suffix] = len(closed)
        if suffixes:
            return suffix_length, sorted(suffixes), closed_counts
    return -1, [], {}


def bounded_rows_by_word_and_trace_class(
    bounded_rows: list[dict[str, int]],
    class_by_trace: dict[tuple[int, ...], dict[str, int]],
    assoc_by_word: dict[tuple[int, ...], dict[str, int]],
    rewrite_edge_by_pair: dict[tuple[int, int], dict[str, int]],
) -> dict[tuple[tuple[int, ...], int], list[dict[str, int]]]:
    rows_by_word_class: dict[tuple[tuple[int, ...], int], list[dict[str, int]]] = {}
    for row in bounded_rows:
        if int(row["trace_detour_overhead"]) != TARGET_TRACE_OVERHEAD:
            continue
        _raw, trace_nodes, _signatures, _metrics = build_trace(
            bounded_word(row),
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        trace = tuple(int(value) for value in trace_nodes)
        if trace not in class_by_trace:
            continue
        class_id = int(class_by_trace[trace]["trace_class_id"])
        rows_by_word_class.setdefault((bounded_word(row), class_id), []).append(row)
    return rows_by_word_class


def build_payloads() -> dict[str, Any]:
    trace_report = load_json(TRACE_QUOTIENT_REPORT)
    trace_quotient = load_json(TRACE_QUOTIENT_JSON)
    trace_certificate = load_json(TRACE_QUOTIENT_CERTIFICATE)
    rank104_report = load_json(RANK104_REPORT)
    rank104_certificate = load_json(RANK104_CERTIFICATE)
    edit_report = load_json(EDIT_REPAIR_REPORT)
    edit_repair = load_json(EDIT_REPAIR_JSON)
    edit_certificate = load_json(EDIT_REPAIR_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    trace_tables = np.load(TRACE_QUOTIENT_TABLES, allow_pickle=False)
    bounded_tables = np.load(BOUNDED_BACKTRACK_TABLES, allow_pickle=False)
    edit_tables = np.load(EDIT_REPAIR_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    trace_class_table = np.asarray(trace_tables["trace_class_table"], dtype=np.int64)
    bounded_candidate_table = np.asarray(
        bounded_tables["candidate_table"],
        dtype=np.int64,
    )
    edit_candidate_table = np.asarray(edit_tables["candidate_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    class_rows = read_csv_ints(TRACE_QUOTIENT_CLASSES)
    class_by_trace = {trace_from_class_row(row): row for row in class_rows}
    bounded_rows = read_csv_ints(BOUNDED_BACKTRACK_CANDIDATES)
    edit_rows = edit_repair_rows(EDIT_REPAIR_CANDIDATES)
    cell_edges = read_int_csv(CELL_COMPLEX_EDGES)
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    symbol_ids = sorted({int(row["symbol_id"]) for row in alphabet_rows})
    adjacency, _carriers = build_carrier_adjacency(cell_edges, atom_to_symbol)
    assoc_by_word = associativity_lookup(read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV))
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }
    bounded_by_word_class = bounded_rows_by_word_and_trace_class(
        bounded_rows,
        class_by_trace,
        assoc_by_word,
        rewrite_edge_by_pair,
    )

    weak_min_by_target = {
        target_id: min(
            row["edit_distance"]
            for row in edit_rows
            if row["target_word_id"] == target_id and row["weak_repair_flag"] == 1
        )
        for target_id in range(len(LOWER_OVERHEAD_TAIL_WORDS))
    }

    selected_rows: list[dict[str, Any]] = []
    for edit_row in edit_rows:
        if int(edit_row["weak_repair_flag"]) != 1:
            continue
        if int(edit_row["trace_detour_overhead"]) != TARGET_TRACE_OVERHEAD:
            continue
        word = edit_repair_word(edit_row)
        for (_match_word, class_id), matches in bounded_by_word_class.items():
            if _match_word == word:
                selected_rows.append(
                    {
                        "edit_row": edit_row,
                        "word": word,
                        "trace_class_id": class_id,
                        "bounded_matches": sorted(
                            matches,
                            key=lambda row: int(row["rank_order"]),
                        ),
                    }
                )

    selected_rows = sorted(
        selected_rows,
        key=lambda row: (
            int(row["trace_class_id"]),
            int(row["edit_row"]["target_word_id"]),
            int(row["edit_row"]["candidate_id"]),
        ),
    )

    promotion_rows = []
    for promotion_repair_id, selected in enumerate(selected_rows):
        edit_row = selected["edit_row"]
        word = selected["word"]
        target_word_id = int(edit_row["target_word_id"])
        target = tuple(int(value) for value in LOWER_OVERHEAD_TAIL_WORDS[target_word_id])
        consumed_count = int(edit_row["selected_prefix_consumed_at_node44"])
        prefix = word[:consumed_count]
        existing_post44 = word[consumed_count:]
        suffix_length, suffixes, closed_counts = minimal_promotion_suffixes(
            prefix,
            target,
            symbol_ids,
            adjacency,
        )
        best_suffix = suffixes[0] if suffixes else ()
        target_consumed = int(target_progress((*prefix, *best_suffix), target) == len(target))
        closed_count = int(closed_counts.get(best_suffix, 0))
        ranks = [int(row["rank_order"]) for row in selected["bounded_matches"]]
        strong = int(edit_row["strong_repair_flag"])
        nonstrong = int(edit_row["weak_repair_flag"] == 1 and strong == 0)
        nonminimal = int(
            int(edit_row["edit_distance"]) > weak_min_by_target[target_word_id]
        )
        existing_longer = int(
            nonstrong == 1 and len(existing_post44) > suffix_length >= 0
        )
        promotion_rows.append(
            {
                "promotion_repair_id": promotion_repair_id,
                "edit_repair_candidate_id": int(edit_row["candidate_id"]),
                "target_word_id": target_word_id,
                "edit_distance": int(edit_row["edit_distance"]),
                "word_length": len(word),
                **{
                    column: value
                    for column, value in zip(
                        SYMBOL_COLUMNS,
                        padded(word, MAX_WORD_LENGTH),
                    )
                },
                "trace_class_id": int(selected["trace_class_id"]),
                "bounded_match_count": len(selected["bounded_matches"]),
                "bounded_rank_min": min(ranks),
                "bounded_rank_max": max(ranks),
                "pre_aperture_strong_flag": strong,
                "target_consumed_before_node44_flag": int(
                    edit_row["target_consumed_before_node44_flag"]
                ),
                "nonstrong_weak_flag": nonstrong,
                "nonminimal_weak_flag": nonminimal,
                "first_node44_consumed_symbol_count": consumed_count,
                "promotion_prefix_length": len(prefix),
                **{
                    column: value
                    for column, value in zip(
                        PREFIX_SYMBOL_COLUMNS,
                        padded(prefix, MAX_WORD_LENGTH),
                    )
                },
                "existing_post_node44_suffix_length": len(existing_post44),
                **{
                    column: value
                    for column, value in zip(
                        EXISTING_POST44_SYMBOL_COLUMNS,
                        padded(existing_post44, MAX_WORD_LENGTH),
                    )
                },
                "remaining_target_symbol_count_at_node44": len(target)
                - target_progress(prefix, target),
                "minimal_promotion_suffix_length": suffix_length,
                "minimal_promotion_suffix_count": len(suffixes),
                **{
                    column: value
                    for column, value in zip(
                        PROMOTION_SUFFIX_COLUMNS,
                        padded(best_suffix, MAX_PROMOTION_SUFFIX_LENGTH),
                    )
                },
                "promotion_closed_path_count": closed_count,
                "promotion_target_consumed_flag": target_consumed,
                "promotion_closes_to_origin_flag": int(closed_count > 0),
                "post_suffix_can_make_pre_aperture_strong_flag": 0,
                "existing_post44_suffix_strictly_longer_than_min_flag": existing_longer,
            }
        )

    promotion_table = table_from_rows(PROMOTION_REPAIR_COLUMNS, promotion_rows)
    class_counts = Counter(row["trace_class_id"] for row in promotion_rows)
    observable_values = {
        "selected_weak_bounded_repair_count": len(promotion_rows),
        "selected_nonstrong_repair_count": sum(
            row["nonstrong_weak_flag"] for row in promotion_rows
        ),
        "selected_strong_repair_count": sum(
            row["pre_aperture_strong_flag"] for row in promotion_rows
        ),
        "nonminimal_nonstrong_repair_count": sum(
            row["nonstrong_weak_flag"] and row["nonminimal_weak_flag"]
            for row in promotion_rows
        ),
        "minimal_nonstrong_repair_count": sum(
            row["nonstrong_weak_flag"] and not row["nonminimal_weak_flag"]
            for row in promotion_rows
        ),
        "nonstrong_x5_promotion_count": sum(
            row["nonstrong_weak_flag"]
            and row["minimal_promotion_suffix_length"] == 1
            and row["minimal_promotion_suffix_symbol_0_id"] == 5
            for row in promotion_rows
        ),
        "strong_x3_closure_promotion_count": sum(
            row["pre_aperture_strong_flag"]
            and row["minimal_promotion_suffix_length"] == 1
            and row["minimal_promotion_suffix_symbol_0_id"] == 3
            for row in promotion_rows
        ),
        "post_suffix_strongification_count": sum(
            row["post_suffix_can_make_pre_aperture_strong_flag"]
            for row in promotion_rows
        ),
        "class0_selected_count": class_counts[0],
        "class1_selected_count": class_counts[1],
        "class2_selected_count": class_counts[2],
        "bounded_match_total": sum(
            row["bounded_match_count"] for row in promotion_rows
        ),
        "nonstrong_bounded_match_total": sum(
            row["bounded_match_count"]
            for row in promotion_rows
            if row["nonstrong_weak_flag"]
        ),
        "existing_suffix_improvement_count": sum(
            row["existing_post44_suffix_strictly_longer_than_min_flag"]
            for row in promotion_rows
        ),
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

    candidate_ids = [
        row["edit_repair_candidate_id"] for row in promotion_rows
    ]
    closure_counts_by_candidate = {
        str(row["edit_repair_candidate_id"]): row["promotion_closed_path_count"]
        for row in promotion_rows
    }
    promotion_suffix_by_candidate = {
        str(row["edit_repair_candidate_id"]): [
            value
            for value in [
                row[column] for column in PROMOTION_SUFFIX_COLUMNS
            ]
            if value >= 0
        ]
        for row in promotion_rows
    }
    checks = {
        "trace_quotient_report_certified": trace_report.get("status")
        == TRACE_QUOTIENT_STATUS,
        "trace_quotient_certificate_certified": trace_certificate.get("status")
        == TRACE_QUOTIENT_STATUS,
        "trace_quotient_schema_available": trace_quotient.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient@1",
        "rank104_report_certified": rank104_report.get("status") == RANK104_STATUS,
        "rank104_certificate_certified": rank104_certificate.get("status")
        == RANK104_STATUS,
        "edit_repair_report_certified": edit_report.get("status")
        == EDIT_REPAIR_STATUS,
        "edit_repair_certificate_certified": edit_certificate.get("status")
        == EDIT_REPAIR_STATUS,
        "edit_repair_schema_available": edit_repair.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead2_edit_repair@1",
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
        "trace_class_table_shape_is_7_by_codebook": tuple(trace_class_table.shape)
        == (7, len(TRACE_CLASS_COLUMNS)),
        "bounded_candidate_table_shape_is_1287": tuple(bounded_candidate_table.shape)[0]
        == 1287,
        "edit_candidate_table_shape_is_596_by_codebook": tuple(
            edit_candidate_table.shape
        )
        == (596, len(EDIT_REPAIR_COLUMNS)),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "promotion_table_shape_matches_codebook": tuple(promotion_table.shape)
        == (8, len(PROMOTION_REPAIR_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "selected_candidate_ids_match_expected": candidate_ids
        == [20, 263, 264, 265, 270, 273, 104, 544],
        "selected_trace_class_distribution_is_6_1_1": class_counts
        == Counter({0: 6, 1: 1, 2: 1}),
        "seven_selected_rows_are_nonstrong_target0": observable_values[
            "selected_nonstrong_repair_count"
        ]
        == 7
        and all(
            row["target_word_id"] == 0
            for row in promotion_rows
            if row["nonstrong_weak_flag"]
        ),
        "one_selected_row_is_strong_target1": observable_values[
            "selected_strong_repair_count"
        ]
        == 1
        and any(
            row["target_word_id"] == 1
            and row["pre_aperture_strong_flag"] == 1
            and row["edit_repair_candidate_id"] == 544
            for row in promotion_rows
        ),
        "six_nonstrong_rows_are_nonminimal": observable_values[
            "nonminimal_nonstrong_repair_count"
        ]
        == 6
        and observable_values["minimal_nonstrong_repair_count"] == 1,
        "all_nonstrong_promotions_are_single_x5": observable_values[
            "nonstrong_x5_promotion_count"
        ]
        == 7,
        "strong_target1_needs_x3_closure_return": observable_values[
            "strong_x3_closure_promotion_count"
        ]
        == 1,
        "post_node44_suffix_never_strongifies_first_hit": observable_values[
            "post_suffix_strongification_count"
        ]
        == 0,
        "all_promotions_consume_target_and_close": all(
            row["promotion_target_consumed_flag"] == 1
            and row["promotion_closes_to_origin_flag"] == 1
            for row in promotion_rows
        ),
        "closure_counts_match_expected": closure_counts_by_candidate
        == {
            "20": 4,
            "263": 4,
            "264": 4,
            "265": 4,
            "270": 4,
            "273": 4,
            "104": 8,
            "544": 3,
        },
        "bounded_match_totals_match_expected": observable_values[
            "bounded_match_total"
        ]
        == 49
        and observable_values["nonstrong_bounded_match_total"] == 46,
        "five_nonstrong_suffixes_have_redundant_post44_symbol": observable_values[
            "existing_suffix_improvement_count"
        ]
        == 5,
    }

    witness = {
        "selected_edit_repair_candidate_ids": candidate_ids,
        "trace_class_distribution": {
            str(class_id): class_counts[class_id] for class_id in sorted(class_counts)
        },
        "nonstrong_candidate_ids": [
            row["edit_repair_candidate_id"]
            for row in promotion_rows
            if row["nonstrong_weak_flag"]
        ],
        "strong_candidate_ids": [
            row["edit_repair_candidate_id"]
            for row in promotion_rows
            if row["pre_aperture_strong_flag"]
        ],
        "promotion_suffix_by_candidate": promotion_suffix_by_candidate,
        "promotion_closed_path_count_by_candidate": closure_counts_by_candidate,
        "bounded_rank_interval_by_candidate": {
            str(row["edit_repair_candidate_id"]): [
                row["bounded_rank_min"],
                row["bounded_rank_max"],
            ]
            for row in promotion_rows
        },
        "promotion_table_sha256": sha_array(promotion_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    audit = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit@1",
        "object": "d20",
        "audit_rule": {
            "source_scope": "weak edit-repair rows with trace overhead 3 and exact bounded first-return matches in the seven-class overhead-3 quotient",
            "promotion_scope": "suffixes appended from the first node44 carrier prefix, searched over the six selected-symbol alphabet through length four",
            "closure_rule": "target subsequence consumed and first-return carrier path closed at carrier 12",
            "strong_boundary": "post-node44 suffixes are not allowed to redefine whether the first node44 hit was pre-aperture strong",
        },
        "summary": {
            "selected_repair_count": observable_values[
                "selected_weak_bounded_repair_count"
            ],
            "nonstrong_target0_count": observable_values[
                "selected_nonstrong_repair_count"
            ],
            "already_strong_target1_count": observable_values[
                "selected_strong_repair_count"
            ],
            "nonstrong_minimal_promotion": "one post-node44 x5 for all seven nonstrong target0 rows",
            "strong_target1_promotion": "one post-node44 x3 return contact for carrier closure; target consumption was already complete",
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD3_WEAK_PROMOTION_AUDIT_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "eight weak edit-repair words with overhead 3 have exact bounded first-return matches in the seven trace classes",
            "seven are nonstrong target0 rows; six of those seven are nonminimal weak repairs beyond the one-insertion minimum",
            "all seven nonstrong target0 rows need exactly one post-node44 x5 to consume the remaining target symbol and close a first-return carrier path",
            "five nonminimal target0 rows already carry a longer post-node44 suffix than the minimal x5 promotion requires",
            "the target1 row is already pre-aperture strong at candidate 544 but still needs one post-node44 x3 return contact for first-return carrier closure",
            "no suffix appended after the first node44 hit can convert a nonstrong first hit into a strong first hit",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Across the seven bounded overhead-3 trace classes, the target-language "
            "weak repairs with closed bounded matches reduce to seven nonstrong "
            "target0 rows plus one already-strong target1 row. Every nonstrong "
            "target0 row has the same minimal post-node44 target-consumption "
            "closure: append x5. This promotes carrier closure after the first "
            "node44 hit, but it cannot retroactively make the first hit strong."
        ),
        "stage_protocol": {
            "draft": "select weak overhead-3 edit repairs that have exact bounded first-return matches in the seven trace classes",
            "witness": "materialize trace-class membership, bounded rank intervals, node44 prefixes, and minimal promotion suffixes",
            "coherence": "separate post-node44 target-consumption closure from pre-aperture strong repair status",
            "closure": "certify that all nonstrong selected rows close with one x5 and that suffixes cannot strongify an early hit",
            "emit": "emit weak-promotion audit JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "trace_quotient_report": input_entry(
                TRACE_QUOTIENT_REPORT,
                {
                    "status": trace_report.get("status"),
                    "certificate_sha256": trace_report.get("certificate_sha256"),
                },
            ),
            "trace_quotient_json": input_entry(TRACE_QUOTIENT_JSON),
            "trace_quotient_classes": input_entry(TRACE_QUOTIENT_CLASSES),
            "trace_quotient_tables": input_entry(TRACE_QUOTIENT_TABLES),
            "trace_quotient_certificate": input_entry(TRACE_QUOTIENT_CERTIFICATE),
            "rank104_report": input_entry(
                RANK104_REPORT,
                {
                    "status": rank104_report.get("status"),
                    "certificate_sha256": rank104_report.get("certificate_sha256"),
                },
            ),
            "rank104_certificate": input_entry(RANK104_CERTIFICATE),
            "bounded_backtrack_candidates": input_entry(BOUNDED_BACKTRACK_CANDIDATES),
            "bounded_backtrack_tables": input_entry(BOUNDED_BACKTRACK_TABLES),
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
            "signature_boundary_spine_aperture_overhead3_weak_promotion_audit": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit.json"
            ),
            "aperture_overhead3_weak_promotion_repairs_csv": relpath(
                OUT_DIR / "aperture_overhead3_weak_promotion_repairs.csv"
            ),
            "aperture_overhead3_weak_promotion_observables_csv": relpath(
                OUT_DIR / "aperture_overhead3_weak_promotion_observables.csv"
            ),
            "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_tables.npz"
            ),
            "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "which weak overhead-3 edit repairs have exact bounded first-return matches in the seven trace classes",
                "the minimal post-node44 suffix needed to consume the remaining target symbols and close from the first node44 carrier prefix",
                "that all selected nonstrong target0 rows share the one-symbol x5 promotion",
                "that candidate 544 is the only selected already-strong target1 row",
                "that post-node44 suffixes cannot change the pre-aperture strong/nonstrong classification of the first node44 hit",
            ],
            "does_not_certify_because_not_required": [
                "walks outside the already-certified bounded first-return search",
                "edit repairs with overhead other than 3",
                "repairs using deletion or substitution edits",
                "turning nonstrong first hits into strong first hits by changing pre-node44 symbols",
                "categorical center, braiding, pivotal, or spherical data",
            ],
        },
        "next_highest_yield_item": (
            "Collapse the seven nonstrong x5-promoted target0 rows by their "
            "pre-node44 trace branch and carrier-prefix endpoint histogram, then "
            "ask which pre-node44 symbol substitution is the least edit that "
            "turns the shared post-node44 x5 closure into a genuinely strong "
            "first-hit repair."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified overhead-3 quotient, rank-104 audit, edit-repair, carrier cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "select weak overhead-3 edit repairs with exact bounded first-return matches in the seven trace classes",
            "recompute node44 prefixes and minimal post-node44 target-consumption closure suffixes",
            "separate post-node44 closure promotion from pre-aperture strong repair status",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_overhead3_weak_promotion_audit": audit,
        "aperture_overhead3_weak_promotion_repairs_csv": csv_text(
            PROMOTION_REPAIR_COLUMNS,
            promotion_rows,
        ),
        "aperture_overhead3_weak_promotion_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "promotion_repair_table": promotion_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate": certificate,
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
        / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit.json",
        payloads["signature_boundary_spine_aperture_overhead3_weak_promotion_audit"],
    )
    (OUT_DIR / "aperture_overhead3_weak_promotion_repairs.csv").write_text(
        payloads["aperture_overhead3_weak_promotion_repairs_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead3_weak_promotion_observables.csv").write_text(
        payloads["aperture_overhead3_weak_promotion_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_tables.npz",
        promotion_repair_table=payloads["promotion_repair_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_overhead3_weak_promotion_audit_certificate"
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
                "selected_edit_repair_candidate_ids": witness[
                    "selected_edit_repair_candidate_ids"
                ],
                "promotion_suffix_by_candidate": witness[
                    "promotion_suffix_by_candidate"
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
