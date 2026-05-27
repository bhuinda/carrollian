from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search import (
        OUT_DIR as BOUNDED_BACKTRACK_DIR,
        STATUS as BOUNDED_BACKTRACK_STATUS,
        WALK_CANDIDATE_COLUMNS,
    )
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
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure import (
        CLOSED_PATH_COLUMNS as TAIL_CLOSED_PATH_COLUMNS,
        CLOSURE_SUFFIX_COLUMNS as TAIL_CLOSURE_SUFFIX_COLUMNS,
        OUT_DIR as TAIL_CLOSURE_DIR,
        REPAIR_COLUMNS as TAIL_REPAIR_COLUMNS,
        REPAIR_WORD_COLUMNS as TAIL_REPAIR_WORD_COLUMNS,
        STATUS as TAIL_CLOSURE_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        ORIGIN_CARRIER_ID,
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
        WALK_CANDIDATE_COLUMNS,
    )
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
    from derive_c985_d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure import (
        CLOSED_PATH_COLUMNS as TAIL_CLOSED_PATH_COLUMNS,
        CLOSURE_SUFFIX_COLUMNS as TAIL_CLOSURE_SUFFIX_COLUMNS,
        OUT_DIR as TAIL_CLOSURE_DIR,
        REPAIR_COLUMNS as TAIL_REPAIR_COLUMNS,
        REPAIR_WORD_COLUMNS as TAIL_REPAIR_WORD_COLUMNS,
        STATUS as TAIL_CLOSURE_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        ORIGIN_CARRIER_ID,
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
    "c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_CLOSED_REPAIR_CYCLE_RANKING_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TAIL_CLOSURE_REPORT = TAIL_CLOSURE_DIR / "report.json"
TAIL_CLOSURE_JSON = (
    TAIL_CLOSURE_DIR
    / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure.json"
)
TAIL_CLOSURE_REPAIRS = (
    TAIL_CLOSURE_DIR / "aperture_overhead2_post_aperture_tail_repairs.csv"
)
TAIL_CLOSURE_CLOSED_PATHS = (
    TAIL_CLOSURE_DIR / "aperture_overhead2_post_aperture_tail_closed_paths.csv"
)
TAIL_CLOSURE_TABLES = (
    TAIL_CLOSURE_DIR
    / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_tables.npz"
)
TAIL_CLOSURE_CERTIFICATE = (
    TAIL_CLOSURE_DIR
    / "signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure_certificate.json"
)

BOUNDED_BACKTRACK_REPORT = BOUNDED_BACKTRACK_DIR / "report.json"
BOUNDED_BACKTRACK_JSON = (
    BOUNDED_BACKTRACK_DIR / "signature_boundary_spine_aperture_bounded_backtrack_search.json"
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
    / "derive_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking.py"
)

MAX_SYMBOL_LENGTH = 7
MAX_TRACE_NODES = 8
BASELINE_SCORE = (
    BASELINE_TAIL_OVERHEAD,
    BASELINE_TAIL_VALLEY,
    BASELINE_TAIL_DELTA_TWICE,
    BASELINE_TAIL_VARIATION,
)

SYMBOL_COLUMNS = [f"symbol_{index}_id" for index in range(MAX_SYMBOL_LENGTH)]
TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_TRACE_NODES)]

REPAIR_CLASS_COLUMNS = [
    "repair_id",
    "target_word_id",
    "path_symbol_length",
    *SYMBOL_COLUMNS,
    "closed_path_count",
    "bounded_word_match_count",
    "exact_bounded_match_count",
    "outside_bounded_path_count",
    "simple_outside_count",
    "intermediate_origin_outside_count",
    "unexplained_outside_count",
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "trace_edge_count",
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "baseline_score_alias_flag",
    "nonbaseline_overhead3_class_flag",
    "score_better_candidate_count",
    "score_class_candidate_count",
    "score_rank_min",
    "score_rank_max",
    "best_exact_bounded_rank",
    "worst_exact_bounded_rank",
    "exact_bounded_candidate_min_id",
    "exact_bounded_candidate_max_id",
]

PATH_MATCH_COLUMNS = [
    "closed_path_id",
    "repair_id",
    "target_word_id",
    "path_symbol_length",
    *SYMBOL_COLUMNS,
    "simple_closed_walk_flag",
    "no_intermediate_origin_flag",
    "repeated_interior_carrier_count",
    "bounded_scope_eligible_flag",
    "exact_bounded_match_flag",
    "bounded_candidate_id",
    "bounded_rank_order",
    "bounded_trace_detour_overhead",
    "bounded_signature_valley_depth",
    "bounded_metric_gromov_delta_twice",
    "bounded_trace_signature_total_variation",
    "outside_reason_code",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "repair_class_count": 0,
    "closed_path_count": 1,
    "exact_bounded_match_count": 2,
    "target0_exact_bounded_match_count": 3,
    "target1_exact_bounded_match_count": 4,
    "target0_outside_bounded_path_count": 5,
    "target1_outside_bounded_path_count": 6,
    "simple_outside_path_count": 7,
    "intermediate_origin_outside_path_count": 8,
    "unexplained_outside_path_count": 9,
    "target0_baseline_score_alias_flag": 10,
    "target1_nonbaseline_overhead3_class_flag": 11,
    "target0_score_class_candidate_count": 12,
    "target1_score_class_candidate_count": 13,
    "target1_score_better_candidate_count": 14,
    "bounded_scope_eligible_path_count": 15,
    "bounded_scope_eligible_unmatched_count": 16,
}

EXACT_MATCH_REASON = 0
SIMPLE_OUTSIDE_REASON = 1
INTERMEDIATE_ORIGIN_OUTSIDE_REASON = 2
UNEXPLAINED_OUTSIDE_REASON = 3


def read_csv_ints(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def padded(values: tuple[int, ...] | list[int], size: int) -> list[int]:
    return [*values, *([-1] * (size - len(values)))]


def values_from_columns(row: dict[str, int], columns: list[str]) -> tuple[int, ...]:
    return tuple(int(row[column]) for column in columns if int(row[column]) >= 0)


def bounded_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"selected_symbol_{index}_id"])
        for index in range(int(row["walk_length"]))
    )


def bounded_edges(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"cell_edge_{index}_id"])
        for index in range(int(row["walk_length"]))
    )


def bounded_atoms(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"selected_atom_{index}_id"])
        for index in range(int(row["walk_length"]))
    )


def closed_edges(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"cell_edge_{index}_id"])
        for index in range(int(row["path_symbol_length"]))
    )


def closed_atoms(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"selected_atom_{index}_id"])
        for index in range(int(row["path_symbol_length"]))
    )


def closed_carriers(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        int(row[f"carrier_{index}_id"])
        for index in range(int(row["path_symbol_length"]) + 1)
    )


def repair_symbol_word(row: dict[str, int]) -> tuple[int, ...]:
    repair_word = values_from_columns(row, TAIL_REPAIR_WORD_COLUMNS)
    closure_suffix = values_from_columns(row, TAIL_CLOSURE_SUFFIX_COLUMNS)
    return (*repair_word, *closure_suffix)


def is_simple_closed_walk(carriers: tuple[int, ...]) -> bool:
    return carriers[0] == carriers[-1] and len(set(carriers[:-1])) == len(carriers[:-1])


def repeated_interior_carrier_count(carriers: tuple[int, ...]) -> int:
    interior = carriers[1:-1]
    return len(interior) - len(set(interior))


def no_intermediate_origin(carriers: tuple[int, ...]) -> bool:
    return ORIGIN_CARRIER_ID not in carriers[1:-1]


def bounded_score(row: dict[str, int]) -> tuple[int, int, int, int]:
    return (
        int(row["trace_detour_overhead"]),
        int(row["signature_valley_depth"]),
        int(row["metric_gromov_delta_twice"]),
        int(row["trace_signature_total_variation"]),
    )


def outside_reason(
    exact_match: bool,
    simple: bool,
    first_return: bool,
) -> int:
    if exact_match:
        return EXACT_MATCH_REASON
    if simple:
        return SIMPLE_OUTSIDE_REASON
    if not first_return:
        return INTERMEDIATE_ORIGIN_OUTSIDE_REASON
    return UNEXPLAINED_OUTSIDE_REASON


def build_payloads() -> dict[str, Any]:
    tail_report = load_json(TAIL_CLOSURE_REPORT)
    tail_closure = load_json(TAIL_CLOSURE_JSON)
    tail_certificate = load_json(TAIL_CLOSURE_CERTIFICATE)
    bounded_report = load_json(BOUNDED_BACKTRACK_REPORT)
    bounded_search = load_json(BOUNDED_BACKTRACK_JSON)
    bounded_certificate = load_json(BOUNDED_BACKTRACK_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    tail_tables = np.load(TAIL_CLOSURE_TABLES, allow_pickle=False)
    bounded_tables = np.load(BOUNDED_BACKTRACK_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    tail_repair_table = np.asarray(tail_tables["repair_table"], dtype=np.int64)
    tail_closed_path_table = np.asarray(tail_tables["closed_path_table"], dtype=np.int64)
    bounded_candidate_table = np.asarray(
        bounded_tables["candidate_table"],
        dtype=np.int64,
    )
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    repair_rows = read_csv_ints(TAIL_CLOSURE_REPAIRS)
    closed_rows = read_csv_ints(TAIL_CLOSURE_CLOSED_PATHS)
    bounded_rows = read_csv_ints(BOUNDED_BACKTRACK_CANDIDATES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    assoc_by_word = associativity_lookup(associativity_rows)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }

    bounded_by_word: dict[tuple[int, ...], list[dict[str, int]]] = defaultdict(list)
    bounded_by_edges_atoms: dict[tuple[tuple[int, ...], tuple[int, ...]], dict[str, int]] = {}
    score_histogram: Counter[tuple[int, int, int, int]] = Counter()
    for row in bounded_rows:
        bounded_by_word[bounded_word(row)].append(row)
        bounded_by_edges_atoms[(bounded_edges(row), bounded_atoms(row))] = row
        score_histogram[bounded_score(row)] += 1

    repair_word_by_id = {
        int(row["repair_id"]): repair_symbol_word(row) for row in repair_rows
    }
    target_by_repair = {
        int(row["repair_id"]): int(row["target_word_id"]) for row in repair_rows
    }
    path_rows = []
    class_accumulators: dict[int, dict[str, Any]] = {}

    for closed in closed_rows:
        repair_id = int(closed["repair_id"])
        target_word_id = int(closed["target_word_id"])
        symbol_word = repair_word_by_id[repair_id]
        carriers = closed_carriers(closed)
        simple = is_simple_closed_walk(carriers)
        first_return = no_intermediate_origin(carriers)
        repeated_count = repeated_interior_carrier_count(carriers)
        exact = bounded_by_edges_atoms.get((closed_edges(closed), closed_atoms(closed)))
        exact_match = exact is not None
        reason = outside_reason(exact_match, simple, first_return)
        class_accumulators.setdefault(
            repair_id,
            {
                "target_word_id": target_word_id,
                "symbol_word": symbol_word,
                "path_count": 0,
                "exact_matches": [],
                "outside_reasons": Counter(),
            },
        )
        class_accumulators[repair_id]["path_count"] += 1
        if exact is not None:
            class_accumulators[repair_id]["exact_matches"].append(exact)
        else:
            class_accumulators[repair_id]["outside_reasons"][reason] += 1
        path_rows.append(
            {
                "closed_path_id": int(closed["closed_path_id"]),
                "repair_id": repair_id,
                "target_word_id": target_word_id,
                "path_symbol_length": len(symbol_word),
                **{
                    column: value
                    for column, value in zip(
                        SYMBOL_COLUMNS,
                        padded(symbol_word, MAX_SYMBOL_LENGTH),
                    )
                },
                "simple_closed_walk_flag": int(simple),
                "no_intermediate_origin_flag": int(first_return),
                "repeated_interior_carrier_count": repeated_count,
                "bounded_scope_eligible_flag": int((not simple) and first_return),
                "exact_bounded_match_flag": int(exact_match),
                "bounded_candidate_id": int(exact["walk_candidate_id"]) if exact else -1,
                "bounded_rank_order": int(exact["rank_order"]) if exact else -1,
                "bounded_trace_detour_overhead": int(exact["trace_detour_overhead"])
                if exact
                else -1,
                "bounded_signature_valley_depth": int(exact["signature_valley_depth"])
                if exact
                else -1,
                "bounded_metric_gromov_delta_twice": int(
                    exact["metric_gromov_delta_twice"]
                )
                if exact
                else -1,
                "bounded_trace_signature_total_variation": int(
                    exact["trace_signature_total_variation"]
                )
                if exact
                else -1,
                "outside_reason_code": reason,
            }
        )

    class_rows = []
    for repair_id in sorted(class_accumulators):
        accumulator = class_accumulators[repair_id]
        symbol_word = accumulator["symbol_word"]
        raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
            symbol_word,
            assoc_by_word,
            rewrite_edge_by_pair,
        )
        score = (
            int(metrics["trace_detour_overhead"]),
            int(metrics["signature_valley_depth"]),
            int(metrics["metric_gromov_delta_twice"]),
            int(metrics["trace_signature_total_variation"]),
        )
        exact_matches = sorted(accumulator["exact_matches"], key=lambda row: row["rank_order"])
        exact_ranks = [int(row["rank_order"]) for row in exact_matches]
        exact_ids = [int(row["walk_candidate_id"]) for row in exact_matches]
        word_matches = bounded_by_word[symbol_word]
        better_count = sum(
            count for other_score, count in score_histogram.items() if other_score < score
        )
        class_count = int(score_histogram[score])
        outside_reasons = accumulator["outside_reasons"]
        class_rows.append(
            {
                "repair_id": repair_id,
                "target_word_id": int(accumulator["target_word_id"]),
                "path_symbol_length": len(symbol_word),
                **{
                    column: value
                    for column, value in zip(
                        SYMBOL_COLUMNS,
                        padded(symbol_word, MAX_SYMBOL_LENGTH),
                    )
                },
                "closed_path_count": int(accumulator["path_count"]),
                "bounded_word_match_count": len(word_matches),
                "exact_bounded_match_count": len(exact_matches),
                "outside_bounded_path_count": int(accumulator["path_count"])
                - len(exact_matches),
                "simple_outside_count": int(outside_reasons[SIMPLE_OUTSIDE_REASON]),
                "intermediate_origin_outside_count": int(
                    outside_reasons[INTERMEDIATE_ORIGIN_OUTSIDE_REASON]
                ),
                "unexplained_outside_count": int(
                    outside_reasons[UNEXPLAINED_OUTSIDE_REASON]
                ),
                "trace_node_count": len(trace_nodes),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(trace_nodes, MAX_TRACE_NODES),
                    )
                },
                "trace_edge_count": int(metrics["trace_edge_count"]),
                "trace_detour_overhead": score[0],
                "signature_valley_depth": score[1],
                "metric_gromov_delta_twice": score[2],
                "trace_signature_total_variation": score[3],
                "baseline_score_alias_flag": int(score == BASELINE_SCORE),
                "nonbaseline_overhead3_class_flag": int(
                    score[0] == BASELINE_TAIL_OVERHEAD and score != BASELINE_SCORE
                ),
                "score_better_candidate_count": better_count,
                "score_class_candidate_count": class_count,
                "score_rank_min": better_count + 1,
                "score_rank_max": better_count + class_count,
                "best_exact_bounded_rank": min(exact_ranks) if exact_ranks else -1,
                "worst_exact_bounded_rank": max(exact_ranks) if exact_ranks else -1,
                "exact_bounded_candidate_min_id": min(exact_ids) if exact_ids else -1,
                "exact_bounded_candidate_max_id": max(exact_ids) if exact_ids else -1,
            }
        )

    class_by_target = {row["target_word_id"]: row for row in class_rows}
    path_table = table_from_rows(PATH_MATCH_COLUMNS, path_rows)
    repair_class_table = table_from_rows(REPAIR_CLASS_COLUMNS, class_rows)
    observable_values = {
        "repair_class_count": len(class_rows),
        "closed_path_count": len(path_rows),
        "exact_bounded_match_count": sum(
            row["exact_bounded_match_count"] for row in class_rows
        ),
        "target0_exact_bounded_match_count": class_by_target[0][
            "exact_bounded_match_count"
        ],
        "target1_exact_bounded_match_count": class_by_target[1][
            "exact_bounded_match_count"
        ],
        "target0_outside_bounded_path_count": class_by_target[0][
            "outside_bounded_path_count"
        ],
        "target1_outside_bounded_path_count": class_by_target[1][
            "outside_bounded_path_count"
        ],
        "simple_outside_path_count": sum(
            row["simple_outside_count"] for row in class_rows
        ),
        "intermediate_origin_outside_path_count": sum(
            row["intermediate_origin_outside_count"] for row in class_rows
        ),
        "unexplained_outside_path_count": sum(
            row["unexplained_outside_count"] for row in class_rows
        ),
        "target0_baseline_score_alias_flag": class_by_target[0][
            "baseline_score_alias_flag"
        ],
        "target1_nonbaseline_overhead3_class_flag": class_by_target[1][
            "nonbaseline_overhead3_class_flag"
        ],
        "target0_score_class_candidate_count": class_by_target[0][
            "score_class_candidate_count"
        ],
        "target1_score_class_candidate_count": class_by_target[1][
            "score_class_candidate_count"
        ],
        "target1_score_better_candidate_count": class_by_target[1][
            "score_better_candidate_count"
        ],
        "bounded_scope_eligible_path_count": sum(
            row["bounded_scope_eligible_flag"] for row in path_rows
        ),
        "bounded_scope_eligible_unmatched_count": sum(
            1
            for row in path_rows
            if row["bounded_scope_eligible_flag"] == 1
            and row["exact_bounded_match_flag"] == 0
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
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "tail_closure_report_certified": tail_report.get("status")
        == TAIL_CLOSURE_STATUS,
        "tail_closure_certificate_certified": tail_certificate.get("status")
        == TAIL_CLOSURE_STATUS,
        "tail_closure_schema_available": tail_closure.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead2_post_aperture_tail_closure@1",
        "bounded_backtrack_report_certified": bounded_report.get("status")
        == BOUNDED_BACKTRACK_STATUS,
        "bounded_backtrack_certificate_certified": bounded_certificate.get("status")
        == BOUNDED_BACKTRACK_STATUS,
        "bounded_backtrack_schema_available": bounded_search.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1",
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
        "tail_repair_table_shape_is_2_by_codebook": tuple(tail_repair_table.shape)
        == (2, len(TAIL_REPAIR_COLUMNS)),
        "tail_closed_path_table_shape_is_20_by_codebook": tuple(
            tail_closed_path_table.shape
        )
        == (20, len(TAIL_CLOSED_PATH_COLUMNS)),
        "bounded_candidate_table_shape_is_1287_by_codebook": tuple(
            bounded_candidate_table.shape
        )
        == (1287, len(WALK_CANDIDATE_COLUMNS)),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "repair_class_table_shape_is_2_by_codebook": tuple(repair_class_table.shape)
        == (2, len(REPAIR_CLASS_COLUMNS)),
        "path_match_table_shape_is_20_by_codebook": tuple(path_table.shape)
        == (20, len(PATH_MATCH_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "exact_bounded_match_split_is_2_and_3": [
            observable_values["target0_exact_bounded_match_count"],
            observable_values["target1_exact_bounded_match_count"],
        ]
        == [2, 3],
        "outside_bounded_split_is_6_and_9": [
            observable_values["target0_outside_bounded_path_count"],
            observable_values["target1_outside_bounded_path_count"],
        ]
        == [6, 9],
        "outside_reasons_are_only_simple_or_intermediate_origin": observable_values[
            "simple_outside_path_count"
        ]
        == 2
        and observable_values["intermediate_origin_outside_path_count"] == 13
        and observable_values["unexplained_outside_path_count"] == 0,
        "all_bounded_scope_eligible_paths_match_exactly": observable_values[
            "bounded_scope_eligible_path_count"
        ]
        == 5
        and observable_values["bounded_scope_eligible_unmatched_count"] == 0,
        "target0_is_baseline_score_alias": class_by_target[0][
            "baseline_score_alias_flag"
        ]
        == 1
        and class_by_target[0]["score_better_candidate_count"] == 0
        and class_by_target[0]["score_class_candidate_count"] == 103,
        "target0_exact_bounded_ranks_are_5_to_9": class_by_target[0][
            "best_exact_bounded_rank"
        ]
        == 5
        and class_by_target[0]["worst_exact_bounded_rank"] == 9,
        "target0_trace_matches_baseline_trace": [
            class_by_target[0][column]
            for column in TRACE_NODE_COLUMNS
            if class_by_target[0][column] >= 0
        ]
        == [48, 42, 27, 28, 34, 44],
        "target1_is_nonbaseline_overhead3_class": class_by_target[1][
            "nonbaseline_overhead3_class_flag"
        ]
        == 1
        and class_by_target[1]["baseline_score_alias_flag"] == 0,
        "target1_exact_bounded_ranks_are_122_to_124": class_by_target[1][
            "best_exact_bounded_rank"
        ]
        == 122
        and class_by_target[1]["worst_exact_bounded_rank"] == 124,
        "target1_score_class_is_three_with_121_better": class_by_target[1][
            "score_class_candidate_count"
        ]
        == 3
        and class_by_target[1]["score_better_candidate_count"] == 121,
        "target1_trace_is_distinct_overhead3_branch": [
            class_by_target[1][column]
            for column in TRACE_NODE_COLUMNS
            if class_by_target[1][column] >= 0
        ]
        == [48, 42, 27, 29, 45, 44],
    }

    witness = {
        "repair_classes": {
            str(row["target_word_id"]): {
                "repair_id": row["repair_id"],
                "symbol_word": [
                    value for value in [row[column] for column in SYMBOL_COLUMNS] if value >= 0
                ],
                "closed_path_count": row["closed_path_count"],
                "exact_bounded_match_count": row["exact_bounded_match_count"],
                "outside_bounded_path_count": row["outside_bounded_path_count"],
                "simple_outside_count": row["simple_outside_count"],
                "intermediate_origin_outside_count": row[
                    "intermediate_origin_outside_count"
                ],
                "trace_nodes": [
                    value
                    for value in [row[column] for column in TRACE_NODE_COLUMNS]
                    if value >= 0
                ],
                "score": {
                    "trace_detour_overhead": row["trace_detour_overhead"],
                    "signature_valley_depth": row["signature_valley_depth"],
                    "metric_gromov_delta_twice": row["metric_gromov_delta_twice"],
                    "trace_signature_total_variation": row[
                        "trace_signature_total_variation"
                    ],
                },
                "baseline_score_alias": bool(row["baseline_score_alias_flag"]),
                "nonbaseline_overhead3_class": bool(
                    row["nonbaseline_overhead3_class_flag"]
                ),
                "score_rank_interval": [
                    row["score_rank_min"],
                    row["score_rank_max"],
                ],
                "exact_bounded_rank_interval": [
                    row["best_exact_bounded_rank"],
                    row["worst_exact_bounded_rank"],
                ],
            }
            for row in class_rows
        },
        "outside_reason_counts": {
            "simple": observable_values["simple_outside_path_count"],
            "intermediate_origin": observable_values[
                "intermediate_origin_outside_path_count"
            ],
            "unexplained": observable_values["unexplained_outside_path_count"],
        },
        "repair_class_table_sha256": sha_array(repair_class_table),
        "path_match_table_sha256": sha_array(path_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    ranking = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking@1",
        "object": "d20",
        "search_rule": {
            "source": "closed paths certified by the post-aperture tail-closure layer",
            "comparison_space": "the 1,287 bounded non-simple first-return candidates",
            "exact_match": "same ordered cell-edge sequence and same selected atom sequence",
            "rank_metric": "bounded-search trace score (overhead, valley depth, delta_twice, total variation)",
        },
        "summary": {
            "target0": witness["repair_classes"]["0"],
            "target1": witness["repair_classes"]["1"],
            "outside_reason_counts": witness["outside_reason_counts"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_OVERHEAD2_CLOSED_REPAIR_CYCLE_RANKING_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "target0's closed repair class has 8 closed carrier paths; 2 are exact bounded-candidate aliases and they sit in the baseline score class",
            "target0's remaining 6 closed paths are outside the bounded non-simple first-return scope because 2 are simple and 4 revisit the origin before final closure",
            "target1's x3-return class has 12 closed carrier paths; 3 are exact bounded candidates ranked 122..124 with score (3,37,1,169)",
            "target1 is an overhead-3 carrier class but not a baseline-score alias: 121 bounded candidates rank ahead of it and its trace branch is 48->42->27->29->45->44",
            "every closed repair path that satisfies the bounded non-simple first-return scope has an exact bounded candidate match",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Closed one-contact repairs split into a baseline alias and a new "
            "overhead-3 branch. The target0 x5 post-tail class aliases the "
            "baseline trace score when it lies inside the bounded first-return "
            "scope; the target1 x3-return class is present in the bounded "
            "search but forms a distinct nonbaseline overhead-3 trace class."
        ),
        "stage_protocol": {
            "draft": "match closed repaired paths against bounded first-return candidates by exact edge and selected-atom sequence",
            "witness": "materialize per-path match status, outside-scope reasons, trace scores, and score-rank intervals",
            "coherence": "separate baseline-score aliases from nonbaseline overhead-3 trace classes",
            "closure": "certify exact bounded matches and bounded-scope exclusions for all 20 closed repair paths",
            "emit": "emit closed-repair ranking JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "tail_closure_report": input_entry(
                TAIL_CLOSURE_REPORT,
                {
                    "status": tail_report.get("status"),
                    "certificate_sha256": tail_report.get("certificate_sha256"),
                },
            ),
            "tail_closure_json": input_entry(TAIL_CLOSURE_JSON),
            "tail_closure_repairs": input_entry(TAIL_CLOSURE_REPAIRS),
            "tail_closure_closed_paths": input_entry(TAIL_CLOSURE_CLOSED_PATHS),
            "tail_closure_tables": input_entry(TAIL_CLOSURE_TABLES),
            "tail_closure_certificate": input_entry(TAIL_CLOSURE_CERTIFICATE),
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
            "bounded_backtrack_candidates": input_entry(BOUNDED_BACKTRACK_CANDIDATES),
            "bounded_backtrack_tables": input_entry(BOUNDED_BACKTRACK_TABLES),
            "bounded_backtrack_certificate": input_entry(BOUNDED_BACKTRACK_CERTIFICATE),
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
            "symbolic_associativity_tables": input_entry(SYMBOLIC_ASSOCIATIVITY_TABLES),
            "symbolic_associativity_certificate": input_entry(
                SYMBOLIC_ASSOCIATIVITY_CERTIFICATE
            ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking.json"
            ),
            "aperture_overhead2_closed_repair_classes_csv": relpath(
                OUT_DIR / "aperture_overhead2_closed_repair_classes.csv"
            ),
            "aperture_overhead2_closed_repair_path_matches_csv": relpath(
                OUT_DIR / "aperture_overhead2_closed_repair_path_matches.csv"
            ),
            "aperture_overhead2_closed_repair_observables_csv": relpath(
                OUT_DIR / "aperture_overhead2_closed_repair_observables.csv"
            ),
            "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_tables.npz"
            ),
            "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "exact edge-and-atom matches between closed repaired paths and bounded first-return candidates",
                "bounded-score ranking intervals for the two closed repair classes",
                "that target0's bounded-scope matches are baseline-score aliases",
                "that target1's bounded-scope matches form a nonbaseline overhead-3 trace class",
                "that all nonmatched closed repair paths are outside bounded scope because of simplicity or intermediate origin revisit",
            ],
            "does_not_certify_because_not_required": [
                "bounded candidates outside the two closed repair symbol classes",
                "closed repair paths using non-minimal edit repairs",
                "walks longer than the already-certified tail-closure witnesses",
                "changing the residual carrier-mask cell complex or symbolic canonicalization",
            ],
        },
        "next_highest_yield_item": (
            "Build the overhead-3 trace-class quotient: collapse the baseline "
            "alias class, isolate the target1 branch 48->42->27->29->45->44, "
            "and compute the minimal transition edit between the two classes."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified post-aperture tail closure and bounded backtrack artifacts",
            "match every closed repair path against bounded candidates by exact edge and selected-atom sequence",
            "classify nonmatches by bounded-scope exclusion reason",
            "compute bounded-score class rank intervals and trace classes for the two repairs",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking": ranking,
        "aperture_overhead2_closed_repair_classes_csv": csv_text(
            REPAIR_CLASS_COLUMNS,
            class_rows,
        ),
        "aperture_overhead2_closed_repair_path_matches_csv": csv_text(
            PATH_MATCH_COLUMNS,
            path_rows,
        ),
        "aperture_overhead2_closed_repair_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "repair_class_table": repair_class_table,
        "path_match_table": path_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate": certificate,
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
        / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking.json",
        payloads[
            "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking"
        ],
    )
    (OUT_DIR / "aperture_overhead2_closed_repair_classes.csv").write_text(
        payloads["aperture_overhead2_closed_repair_classes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_closed_repair_path_matches.csv").write_text(
        payloads["aperture_overhead2_closed_repair_path_matches_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_overhead2_closed_repair_observables.csv").write_text(
        payloads["aperture_overhead2_closed_repair_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_tables.npz",
        repair_class_table=payloads["repair_class_table"],
        path_match_table=payloads["path_match_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_overhead2_closed_repair_cycle_ranking_certificate"
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
                "repair_classes": witness["repair_classes"],
                "outside_reason_counts": witness["outside_reason_counts"],
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
