from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry import (
        BRANCH_PROFILE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OUT_DIR as RANK104_GEOMETRY_DIR,
        RANK104_BEST_STRONG_WORD,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SKIPPED_NODE_COLUMNS,
        STATUS as RANK104_GEOMETRY_STATUS,
        STRONGIFICATION_GAP_CERTIFICATE,
        STRONGIFICATION_GAP_JSON,
        STRONGIFICATION_GAP_REPORT,
        STRONGIFICATION_GAP_TABLES,
        STRONGIFICATION_GAP_WITNESSES,
        STRONGIFICATION_GAP_STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TRACE_NODE_COLUMNS,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        TRACE_QUOTIENT_STATUS,
        WORD_COLUMNS,
        associativity_lookup,
        branch_profile,
        build_carrier_adjacency,
        csv_text,
        edge_key,
        input_entry,
        load_json,
        read_int_csv,
        relpath,
        rewrite_adjacency,
        row_trace,
        self_hash,
        sha_array,
        table_from_rows,
        witness_rows,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_rank104_strongification_branch_geometry import (
        BRANCH_PROFILE_COLUMNS,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        OUT_DIR as RANK104_GEOMETRY_DIR,
        RANK104_BEST_STRONG_WORD,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SKIPPED_NODE_COLUMNS,
        STATUS as RANK104_GEOMETRY_STATUS,
        STRONGIFICATION_GAP_CERTIFICATE,
        STRONGIFICATION_GAP_JSON,
        STRONGIFICATION_GAP_REPORT,
        STRONGIFICATION_GAP_TABLES,
        STRONGIFICATION_GAP_WITNESSES,
        STRONGIFICATION_GAP_STATUS,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        TRACE_NODE_COLUMNS,
        TRACE_QUOTIENT_CERTIFICATE,
        TRACE_QUOTIENT_CLASSES,
        TRACE_QUOTIENT_REPORT,
        TRACE_QUOTIENT_TABLES,
        TRACE_QUOTIENT_STATUS,
        WORD_COLUMNS,
        associativity_lookup,
        branch_profile,
        build_carrier_adjacency,
        csv_text,
        edge_key,
        input_entry,
        load_json,
        read_int_csv,
        relpath,
        rewrite_adjacency,
        row_trace,
        self_hash,
        sha_array,
        table_from_rows,
        witness_rows,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT
    from derive_c985_typed_simple_object_registry import INDEX_PATH


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_COST3_STRONGIFICATION_GEOMETRY_RANKING_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

RANK104_GEOMETRY_REPORT = RANK104_GEOMETRY_DIR / "report.json"
RANK104_GEOMETRY_JSON = (
    RANK104_GEOMETRY_DIR
    / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry.json"
)
RANK104_GEOMETRY_TABLES = (
    RANK104_GEOMETRY_DIR
    / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_tables.npz"
)
RANK104_GEOMETRY_CERTIFICATE = (
    RANK104_GEOMETRY_DIR
    / "signature_boundary_spine_aperture_rank104_strongification_branch_geometry_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking.py"
)

SCORE_COLUMNS = [
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
]

RANKING_COLUMNS = [
    "global_rank",
    "prefix_class_rank",
    "strongification_witness_id",
    "prefix_class_id",
    "edit_cost",
    "substitution_count",
    "insertion_count",
    "word_length",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    *SCORE_COLUMNS,
    "closed_path_count",
    "target_last_symbol_rank",
    "first_node44_consumed_symbol_count",
    "score_dominator_count",
    "score_pareto_flag",
    "closure_augmented_dominator_count",
    "closure_augmented_pareto_flag",
    "source_best_score_flag",
    "global_lexicographic_best_flag",
    "prefix_class_best_flag",
]

CLASS_SUMMARY_COLUMNS = [
    "prefix_class_id",
    "witness_count",
    "lexicographic_best_witness_id",
    "lexicographic_best_global_rank",
    "best_trace_detour_overhead",
    "best_signature_valley_depth",
    "best_metric_gromov_delta_twice",
    "best_trace_signature_total_variation",
    "best_closed_path_count",
    "score_pareto_count",
    "closure_augmented_pareto_count",
    "max_closed_path_count",
    "max_closed_path_best_witness_id",
    "min_trace_detour_overhead",
    "min_signature_valley_depth",
    "min_metric_gromov_delta_twice",
    "min_trace_signature_total_variation",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "cost3_witness_count": 0,
    "prefix_class_count": 1,
    "score_pareto_count": 2,
    "closure_augmented_pareto_count": 3,
    "rank104_witness_id": 4,
    "rank104_global_rank": 5,
    "rank104_score_pareto_flag": 6,
    "rank104_closure_augmented_pareto_flag": 7,
    "class0_best_witness_id": 8,
    "class1_best_witness_id": 9,
    "class0_best_global_rank": 10,
    "class1_best_global_rank": 11,
    "closure_augmented_extra_pareto_count": 12,
    "max_closed_path_count": 13,
    "max_closed_path_best_witness_id": 14,
    "rank104_unique_score_pareto_flag": 15,
    "rank104_global_not_merely_class_flag": 16,
}


def witness_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(
        row[f"strong_word_symbol_{index}_id"]
        for index in range(row["strong_word_length"])
    )


def witness_trace(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[f"trace_node_{index}_id"] for index in range(row["trace_node_count"]))


def profile_score(row: dict[str, int]) -> tuple[int, int, int, int]:
    return tuple(row[column] for column in SCORE_COLUMNS)  # type: ignore[return-value]


def score_dominates(source: dict[str, int], target: dict[str, int]) -> bool:
    source_score = profile_score(source)
    target_score = profile_score(target)
    return all(a <= b for a, b in zip(source_score, target_score)) and any(
        a < b for a, b in zip(source_score, target_score)
    )


def closure_augmented_dominates(source: dict[str, int], target: dict[str, int]) -> bool:
    source_score = profile_score(source)
    target_score = profile_score(target)
    score_no_worse = all(a <= b for a, b in zip(source_score, target_score))
    closure_no_worse = source["closed_path_count"] >= target["closed_path_count"]
    strictly_better = any(a < b for a, b in zip(source_score, target_score)) or (
        source["closed_path_count"] > target["closed_path_count"]
    )
    return score_no_worse and closure_no_worse and strictly_better


def pad_tuple(values: tuple[int, ...], size: int) -> tuple[int, ...]:
    return values + tuple(-1 for _ in range(size - len(values)))


def ranking_row(
    witness: dict[str, int],
    profile: dict[str, int],
    global_rank: int,
    class_rank: int,
    score_dominator_count: int,
    closure_dominator_count: int,
) -> dict[str, int]:
    word = witness_word(witness)
    trace = row_trace(profile)
    return {
        "global_rank": global_rank,
        "prefix_class_rank": class_rank,
        "strongification_witness_id": witness["strongification_witness_id"],
        "prefix_class_id": witness["prefix_class_id"],
        "edit_cost": witness["edit_cost"],
        "substitution_count": witness["substitution_count"],
        "insertion_count": witness["insertion_count"],
        "word_length": len(word),
        **{column: value for column, value in zip(WORD_COLUMNS, pad_tuple(word, len(WORD_COLUMNS)))},
        "trace_node_count": len(trace),
        **{
            column: value
            for column, value in zip(TRACE_NODE_COLUMNS, pad_tuple(trace, len(TRACE_NODE_COLUMNS)))
        },
        **{column: profile[column] for column in SCORE_COLUMNS},
        "closed_path_count": profile["closed_path_count"],
        "target_last_symbol_rank": profile["target_last_symbol_rank"],
        "first_node44_consumed_symbol_count": profile[
            "first_node44_consumed_symbol_count"
        ],
        "score_dominator_count": score_dominator_count,
        "score_pareto_flag": int(score_dominator_count == 0),
        "closure_augmented_dominator_count": closure_dominator_count,
        "closure_augmented_pareto_flag": int(closure_dominator_count == 0),
        "source_best_score_flag": witness["best_score_flag"],
        "global_lexicographic_best_flag": int(global_rank == 1),
        "prefix_class_best_flag": int(class_rank == 1),
    }


def class_summary_rows(ranking_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    rows = []
    for class_id in sorted({row["prefix_class_id"] for row in ranking_rows}):
        members = [row for row in ranking_rows if row["prefix_class_id"] == class_id]
        best = min(members, key=lambda row: row["global_rank"])
        max_closed = max(row["closed_path_count"] for row in members)
        max_closed_best = min(
            (row for row in members if row["closed_path_count"] == max_closed),
            key=lambda row: (
                row["trace_detour_overhead"],
                row["signature_valley_depth"],
                row["metric_gromov_delta_twice"],
                row["trace_signature_total_variation"],
                row["strongification_witness_id"],
            ),
        )
        rows.append(
            {
                "prefix_class_id": class_id,
                "witness_count": len(members),
                "lexicographic_best_witness_id": best["strongification_witness_id"],
                "lexicographic_best_global_rank": best["global_rank"],
                "best_trace_detour_overhead": best["trace_detour_overhead"],
                "best_signature_valley_depth": best["signature_valley_depth"],
                "best_metric_gromov_delta_twice": best["metric_gromov_delta_twice"],
                "best_trace_signature_total_variation": best[
                    "trace_signature_total_variation"
                ],
                "best_closed_path_count": best["closed_path_count"],
                "score_pareto_count": sum(row["score_pareto_flag"] for row in members),
                "closure_augmented_pareto_count": sum(
                    row["closure_augmented_pareto_flag"] for row in members
                ),
                "max_closed_path_count": max_closed,
                "max_closed_path_best_witness_id": max_closed_best[
                    "strongification_witness_id"
                ],
                "min_trace_detour_overhead": min(
                    row["trace_detour_overhead"] for row in members
                ),
                "min_signature_valley_depth": min(
                    row["signature_valley_depth"] for row in members
                ),
                "min_metric_gromov_delta_twice": min(
                    row["metric_gromov_delta_twice"] for row in members
                ),
                "min_trace_signature_total_variation": min(
                    row["trace_signature_total_variation"] for row in members
                ),
            }
        )
    return rows


def build_payloads() -> dict[str, Any]:
    gap_report = load_json(STRONGIFICATION_GAP_REPORT)
    gap_json = load_json(STRONGIFICATION_GAP_JSON)
    gap_certificate = load_json(STRONGIFICATION_GAP_CERTIFICATE)
    rank104_report = load_json(RANK104_GEOMETRY_REPORT)
    rank104_certificate = load_json(RANK104_GEOMETRY_CERTIFICATE)
    trace_report = load_json(TRACE_QUOTIENT_REPORT)
    trace_certificate = load_json(TRACE_QUOTIENT_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    adjacency, _carriers = build_carrier_adjacency(
        read_int_csv(CELL_COMPLEX_EDGES),
        atom_to_symbol,
    )
    assoc_by_word = associativity_lookup(read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV))
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }
    rewrite_graph = rewrite_adjacency(rewrite_edges)

    gap_witnesses = witness_rows(STRONGIFICATION_GAP_WITNESSES)
    witness_by_id = {row["strongification_witness_id"]: row for row in gap_witnesses}
    branch_rows = [
        branch_profile(
            witness["strongification_witness_id"],
            witness["prefix_class_id"],
            0,
            witness_word(witness),
            adjacency,
            assoc_by_word,
            rewrite_edge_by_pair,
            rewrite_graph,
        )
        for witness in gap_witnesses
    ]
    profile_by_id = {row["branch_id"]: row for row in branch_rows}

    global_order = sorted(
        gap_witnesses,
        key=lambda witness: (
            *profile_score(profile_by_id[witness["strongification_witness_id"]]),
            witness["strongification_witness_id"],
        ),
    )
    global_rank = {
        witness["strongification_witness_id"]: index + 1
        for index, witness in enumerate(global_order)
    }
    class_rank: dict[int, int] = {}
    for class_id in sorted({row["prefix_class_id"] for row in gap_witnesses}):
        class_order = [
            witness for witness in global_order if witness["prefix_class_id"] == class_id
        ]
        class_rank.update(
            {
                witness["strongification_witness_id"]: index + 1
                for index, witness in enumerate(class_order)
            }
        )

    ranking_rows = []
    for witness in gap_witnesses:
        witness_id = witness["strongification_witness_id"]
        profile = profile_by_id[witness_id]
        score_dominator_count = sum(
            score_dominates(other, profile)
            for other_id, other in profile_by_id.items()
            if other_id != witness_id
        )
        closure_dominator_count = sum(
            closure_augmented_dominates(other, profile)
            for other_id, other in profile_by_id.items()
            if other_id != witness_id
        )
        ranking_rows.append(
            ranking_row(
                witness,
                profile,
                global_rank[witness_id],
                class_rank[witness_id],
                score_dominator_count,
                closure_dominator_count,
            )
        )
    ranking_rows = sorted(ranking_rows, key=lambda row: row["global_rank"])
    class_rows = class_summary_rows(ranking_rows)

    score_pareto_ids = [
        row["strongification_witness_id"]
        for row in ranking_rows
        if row["score_pareto_flag"] == 1
    ]
    closure_pareto_ids = [
        row["strongification_witness_id"]
        for row in ranking_rows
        if row["closure_augmented_pareto_flag"] == 1
    ]
    rank104_row = next(
        row
        for row in ranking_rows
        if witness_word(witness_by_id[row["strongification_witness_id"]])
        == RANK104_BEST_STRONG_WORD
    )
    max_closed = max(row["closed_path_count"] for row in ranking_rows)
    max_closed_best = min(
        (row for row in ranking_rows if row["closed_path_count"] == max_closed),
        key=lambda row: row["global_rank"],
    )

    observable_values = {
        "cost3_witness_count": len(gap_witnesses),
        "prefix_class_count": len(class_rows),
        "score_pareto_count": len(score_pareto_ids),
        "closure_augmented_pareto_count": len(closure_pareto_ids),
        "rank104_witness_id": rank104_row["strongification_witness_id"],
        "rank104_global_rank": rank104_row["global_rank"],
        "rank104_score_pareto_flag": rank104_row["score_pareto_flag"],
        "rank104_closure_augmented_pareto_flag": rank104_row[
            "closure_augmented_pareto_flag"
        ],
        "class0_best_witness_id": class_rows[0]["lexicographic_best_witness_id"],
        "class1_best_witness_id": class_rows[1]["lexicographic_best_witness_id"],
        "class0_best_global_rank": class_rows[0]["lexicographic_best_global_rank"],
        "class1_best_global_rank": class_rows[1]["lexicographic_best_global_rank"],
        "closure_augmented_extra_pareto_count": len(
            set(closure_pareto_ids) - set(score_pareto_ids)
        ),
        "max_closed_path_count": max_closed,
        "max_closed_path_best_witness_id": max_closed_best[
            "strongification_witness_id"
        ],
        "rank104_unique_score_pareto_flag": int(score_pareto_ids == [17]),
        "rank104_global_not_merely_class_flag": int(
            rank104_row["global_rank"] == 1
            and class_rows[1]["lexicographic_best_witness_id"]
            == rank104_row["strongification_witness_id"]
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

    branch_table = table_from_rows(BRANCH_PROFILE_COLUMNS, branch_rows)
    ranking_table = table_from_rows(RANKING_COLUMNS, ranking_rows)
    class_summary_table = table_from_rows(CLASS_SUMMARY_COLUMNS, class_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    source_metric_checks = []
    for witness in gap_witnesses:
        profile = profile_by_id[witness["strongification_witness_id"]]
        source_metric_checks.append(
            witness_trace(witness) == row_trace(profile)
            and witness["closed_path_count"] == profile["closed_path_count"]
            and all(witness[column] == profile[column] for column in SCORE_COLUMNS)
            and witness["target_last_symbol_rank"]
            == profile["target_last_symbol_rank"]
            and witness["first_node44_consumed_symbol_count"]
            == profile["first_node44_consumed_symbol_count"]
        )

    checks = {
        "strongification_gap_report_certified": gap_report.get("status")
        == STRONGIFICATION_GAP_STATUS,
        "strongification_gap_certificate_certified": gap_certificate.get("status")
        == STRONGIFICATION_GAP_STATUS,
        "strongification_gap_schema_available": gap_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_overhead3_pre_node44_strongification_gap@1",
        "rank104_geometry_report_certified": rank104_report.get("status")
        == RANK104_GEOMETRY_STATUS,
        "rank104_geometry_certificate_certified": rank104_certificate.get("status")
        == RANK104_GEOMETRY_STATUS,
        "trace_quotient_report_certified": trace_report.get("status")
        == TRACE_QUOTIENT_STATUS,
        "trace_quotient_certificate_certified": trace_certificate.get("status")
        == TRACE_QUOTIENT_STATUS,
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
        "cost3_witness_count_is_24": len(gap_witnesses) == 24,
        "all_witnesses_are_cost_three": all(
            witness["edit_cost"] == 3 for witness in gap_witnesses
        ),
        "all_recomputed_profiles_match_gap_metrics": all(source_metric_checks),
        "branch_table_shape_matches_codebook": tuple(branch_table.shape)
        == (24, len(BRANCH_PROFILE_COLUMNS)),
        "ranking_table_shape_matches_codebook": tuple(ranking_table.shape)
        == (24, len(RANKING_COLUMNS)),
        "class_summary_table_shape_matches_codebook": tuple(class_summary_table.shape)
        == (2, len(CLASS_SUMMARY_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "global_lexicographic_best_is_rank104_witness_17": rank104_row[
            "strongification_witness_id"
        ]
        == 17
        and rank104_row["global_rank"] == 1
        and profile_score(profile_by_id[17]) == (6, 37, 1, 143),
        "score_pareto_frontier_is_unique_rank104": score_pareto_ids == [17],
        "closure_augmented_frontier_keeps_rank104_and_high_closure_outliers": closure_pareto_ids
        == [17, 9, 23],
        "prefix_class_best_witnesses_are_6_and_17": [
            row["lexicographic_best_witness_id"] for row in class_rows
        ]
        == [6, 17],
        "rank104_is_global_not_merely_class_best": observable_values[
            "rank104_global_not_merely_class_flag"
        ]
        == 1,
        "max_closed_path_count_is_24_with_best_witness_23": max_closed == 24
        and max_closed_best["strongification_witness_id"] == 23,
    }

    witness = {
        "global_best": {
            "witness_id": rank104_row["strongification_witness_id"],
            "prefix_class_id": rank104_row["prefix_class_id"],
            "word": list(RANK104_BEST_STRONG_WORD),
            "trace": list(row_trace(profile_by_id[17])),
            "score": list(profile_score(profile_by_id[17])),
            "closed_path_count": rank104_row["closed_path_count"],
        },
        "score_pareto_witness_ids": score_pareto_ids,
        "closure_augmented_pareto_witness_ids": closure_pareto_ids,
        "prefix_class_best_witness_ids": {
            str(row["prefix_class_id"]): row["lexicographic_best_witness_id"]
            for row in class_rows
        },
        "closure_augmented_extra_pareto_witness_ids": sorted(
            set(closure_pareto_ids) - set(score_pareto_ids)
        ),
        "max_closed_path_count": max_closed,
        "max_closed_path_witness_ids": [
            row["strongification_witness_id"]
            for row in ranking_rows
            if row["closed_path_count"] == max_closed
        ],
        "branch_profile_table_sha256": sha_array(branch_table),
        "ranking_table_sha256": sha_array(ranking_table),
        "class_summary_table_sha256": sha_array(class_summary_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    geometry_ranking = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking@1",
        "object": "d20",
        "ranking_rule": {
            "score_order": SCORE_COLUMNS,
            "score_frontier": "minimize the four branch-geometry score coordinates",
            "closure_augmented_frontier": "minimize the same four coordinates while maximizing first-return closed carrier path count",
        },
        "summary": {
            "cost3_witness_count": len(gap_witnesses),
            "global_best_witness_id": rank104_row["strongification_witness_id"],
            "global_best_score": list(profile_score(profile_by_id[17])),
            "score_pareto_witness_ids": score_pareto_ids,
            "closure_augmented_pareto_witness_ids": closure_pareto_ids,
            "rank104_is_unique_score_pareto": score_pareto_ids == [17],
            "rank104_is_closure_augmented_pareto": 17 in closure_pareto_ids,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_COST3_STRONGIFICATION_GEOMETRY_RANKING_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "all 24 cost-three strongification witnesses were rescored by the same branch-geometry profile used for the rank-104 comparison",
            "witness 17, the rank-104 best word, is global rank 1 by the four-coordinate score (overhead, valley, delta_twice, variation)",
            "the score-only Pareto frontier is uniquely witness 17, so rank-104 is not merely a class-local representative",
            "if closure count is added as a maximized objective, witnesses 9 and 23 remain as closure-rich outliers beside witness 17",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "Across all 24 cost-three pre-node44 strongification witnesses, "
            "rank-104 witness 17 is the unique score-Pareto branch and the "
            "global lexicographic best by overhead, valley depth, delta_twice, "
            "and signature variation. It is therefore not just the best member "
            "of prefix class 1. When first-return closure count is promoted to "
            "a fifth objective to maximize, witnesses 9 and 23 survive as "
            "closure-rich outliers, but neither improves the four-coordinate "
            "geometry score."
        ),
        "stage_protocol": {
            "draft": "take the next target from the rank104 branch-geometry certificate",
            "witness": "recompute branch profiles for all 24 cost-three strongification witnesses",
            "coherence": "compare recomputed traces, scores, and closure counts against the gap witness table",
            "closure": "certify the score-only and closure-augmented Pareto frontiers",
            "emit": "emit all-witness branch profiles, rankings, class summaries, observables, certificate, report, and verifier command",
        },
        "inputs": {
            "strongification_gap_report": input_entry(
                STRONGIFICATION_GAP_REPORT,
                {
                    "status": gap_report.get("status"),
                    "certificate_sha256": gap_report.get("certificate_sha256"),
                },
            ),
            "strongification_gap_json": input_entry(STRONGIFICATION_GAP_JSON),
            "strongification_gap_witnesses": input_entry(
                STRONGIFICATION_GAP_WITNESSES
            ),
            "strongification_gap_tables": input_entry(STRONGIFICATION_GAP_TABLES),
            "strongification_gap_certificate": input_entry(
                STRONGIFICATION_GAP_CERTIFICATE
            ),
            "rank104_geometry_report": input_entry(
                RANK104_GEOMETRY_REPORT,
                {
                    "status": rank104_report.get("status"),
                    "certificate_sha256": rank104_report.get("certificate_sha256"),
                },
            ),
            "rank104_geometry_json": input_entry(RANK104_GEOMETRY_JSON),
            "rank104_geometry_tables": input_entry(RANK104_GEOMETRY_TABLES),
            "rank104_geometry_certificate": input_entry(
                RANK104_GEOMETRY_CERTIFICATE
            ),
            "trace_quotient_report": input_entry(
                TRACE_QUOTIENT_REPORT,
                {
                    "status": trace_report.get("status"),
                    "certificate_sha256": trace_report.get("certificate_sha256"),
                },
            ),
            "trace_quotient_classes": input_entry(TRACE_QUOTIENT_CLASSES),
            "trace_quotient_tables": input_entry(TRACE_QUOTIENT_TABLES),
            "trace_quotient_certificate": input_entry(TRACE_QUOTIENT_CERTIFICATE),
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
            "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking.json"
            ),
            "aperture_cost3_strongification_branch_profiles_csv": relpath(
                OUT_DIR / "aperture_cost3_strongification_branch_profiles.csv"
            ),
            "aperture_cost3_strongification_rankings_csv": relpath(
                OUT_DIR / "aperture_cost3_strongification_rankings.csv"
            ),
            "aperture_cost3_strongification_prefix_class_summaries_csv": relpath(
                OUT_DIR / "aperture_cost3_strongification_prefix_class_summaries.csv"
            ),
            "aperture_cost3_strongification_observables_csv": relpath(
                OUT_DIR / "aperture_cost3_strongification_observables.csv"
            ),
            "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_tables.npz"
            ),
            "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the all-24 cost-three strongification branch profile table",
                "global and prefix-class lexicographic rankings by branch-geometry score",
                "the score-only Pareto frontier",
                "the closure-augmented Pareto frontier with first-return closure count maximized",
                "the statement that rank104 witness17 is globally score-optimal, not merely prefix-class optimal",
            ],
            "does_not_certify_because_not_required": [
                "edit costs above three",
                "deletions or movement of the final promoted x5 suffix",
                "new carrier paths outside the residual graph",
                "ranking objectives outside the declared branch-geometry score and closure count",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Read the two closure-augmented outliers, witnesses 9 and 23, "
            "as closure-rich branches: compare their detour geometry against "
            "rank104 witness17 to separate closure multiplicity from geometric optimality."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified pre-node44 strongification gap and rank104 branch-geometry artifacts",
            "recompute branch profiles for all 24 cost-three witnesses using the same geometry function",
            "verify recomputed scores, traces, and closure counts against the gap witness table",
            "materialize global ranks, prefix-class ranks, score Pareto flags, and closure-augmented Pareto flags",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking": geometry_ranking,
        "aperture_cost3_strongification_branch_profiles_csv": csv_text(
            BRANCH_PROFILE_COLUMNS,
            branch_rows,
        ),
        "aperture_cost3_strongification_rankings_csv": csv_text(
            RANKING_COLUMNS,
            ranking_rows,
        ),
        "aperture_cost3_strongification_prefix_class_summaries_csv": csv_text(
            CLASS_SUMMARY_COLUMNS,
            class_rows,
        ),
        "aperture_cost3_strongification_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "branch_profile_table": branch_table,
        "ranking_table": ranking_table,
        "class_summary_table": class_summary_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate": certificate,
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
        / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking.json",
        payloads[
            "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking"
        ],
    )
    (OUT_DIR / "aperture_cost3_strongification_branch_profiles.csv").write_text(
        payloads["aperture_cost3_strongification_branch_profiles_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cost3_strongification_rankings.csv").write_text(
        payloads["aperture_cost3_strongification_rankings_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_cost3_strongification_prefix_class_summaries.csv"
    ).write_text(
        payloads["aperture_cost3_strongification_prefix_class_summaries_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cost3_strongification_observables.csv").write_text(
        payloads["aperture_cost3_strongification_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_tables.npz",
        branch_profile_table=payloads["branch_profile_table"],
        ranking_table=payloads["ranking_table"],
        class_summary_table=payloads["class_summary_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate"
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
                "global_best": witness["global_best"],
                "score_pareto_witness_ids": witness["score_pareto_witness_ids"],
                "closure_augmented_pareto_witness_ids": witness[
                    "closure_augmented_pareto_witness_ids"
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
