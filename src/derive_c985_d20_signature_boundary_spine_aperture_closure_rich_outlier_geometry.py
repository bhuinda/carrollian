from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking import (
        BRANCH_PROFILE_COLUMNS,
        OUT_DIR as COST3_RANKING_DIR,
        RANKING_COLUMNS,
        SCORE_COLUMNS,
        STATUS as COST3_RANKING_STATUS,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        csv_text,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        common_prefix_suffix,
        levenshtein,
        trace_edges,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking import (
        BRANCH_PROFILE_COLUMNS,
        OUT_DIR as COST3_RANKING_DIR,
        RANKING_COLUMNS,
        SCORE_COLUMNS,
        STATUS as COST3_RANKING_STATUS,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        csv_text,
        input_entry,
        load_json,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_trace_class_quotient import (
        common_prefix_suffix,
        levenshtein,
        trace_edges,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_RICH_OUTLIER_GEOMETRY_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

COST3_RANKING_REPORT = COST3_RANKING_DIR / "report.json"
COST3_RANKING_JSON = (
    COST3_RANKING_DIR
    / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking.json"
)
COST3_RANKING_BRANCH_PROFILES = (
    COST3_RANKING_DIR / "aperture_cost3_strongification_branch_profiles.csv"
)
COST3_RANKING_RANKINGS = (
    COST3_RANKING_DIR / "aperture_cost3_strongification_rankings.csv"
)
COST3_RANKING_TABLES = (
    COST3_RANKING_DIR
    / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_tables.npz"
)
COST3_RANKING_CERTIFICATE = (
    COST3_RANKING_DIR
    / "signature_boundary_spine_aperture_cost3_strongification_geometry_ranking_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry.py"
)

REFERENCE_WITNESS_ID = 17
CLOSURE_OUTLIER_IDS = (9, 23)
SELECTED_WITNESS_IDS = (REFERENCE_WITNESS_ID, *CLOSURE_OUTLIER_IDS)
SHARED_CLOSURE_TAIL = (54, 45, 29, 28, 34, 44)
MAX_DIVERGENT_NODES = 4

DIVERGENT_SOURCE_COLUMNS = [
    f"reference_divergent_node_{index}_id" for index in range(MAX_DIVERGENT_NODES)
]
DIVERGENT_OUTLIER_COLUMNS = [
    f"outlier_divergent_node_{index}_id" for index in range(MAX_DIVERGENT_NODES)
]
TAIL_NODE_COLUMNS = [
    f"shared_closure_tail_node_{index}_id" for index in range(len(SHARED_CLOSURE_TAIL))
]

SELECTED_BRANCH_COLUMNS = [
    "selection_order",
    "witness_id",
    "role_code",
    "prefix_class_id",
    "global_rank",
    "prefix_class_rank",
    "word_length",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    *SCORE_COLUMNS,
    "closed_path_count",
    "score_pareto_flag",
    "closure_augmented_pareto_flag",
    "shared_closure_tail_flag",
    "shared_closure_tail_start_index",
    "shared_closure_tail_node_count",
]

REFERENCE_COMPARISON_COLUMNS = [
    "comparison_id",
    "reference_witness_id",
    "outlier_witness_id",
    "outlier_prefix_class_id",
    "outlier_global_rank",
    "reference_closed_path_count",
    "outlier_closed_path_count",
    "outlier_closed_path_gain",
    "reference_trace_detour_overhead",
    "outlier_trace_detour_overhead",
    "outlier_overhead_penalty",
    "reference_signature_valley_depth",
    "outlier_signature_valley_depth",
    "outlier_valley_penalty",
    "reference_metric_gromov_delta_twice",
    "outlier_metric_gromov_delta_twice",
    "outlier_delta_penalty",
    "reference_trace_signature_total_variation",
    "outlier_trace_signature_total_variation",
    "outlier_variation_penalty",
    "closure_gain_per_overhead_x1e6",
    "closure_gain_per_variation_x1e6",
    "common_prefix_node_count",
    "common_suffix_node_count",
    "reference_divergent_node_count",
    "outlier_divergent_node_count",
    "trace_node_edit_distance",
    "trace_edge_edit_distance",
    "outlier_shared_closure_tail_flag",
    "outlier_shared_closure_tail_start_index",
    *DIVERGENT_SOURCE_COLUMNS,
    *DIVERGENT_OUTLIER_COLUMNS,
]

OUTLIER_PAIR_COLUMNS = [
    "pair_id",
    "baseline_class_outlier_witness_id",
    "rank104_class_outlier_witness_id",
    "common_prefix_node_count",
    "common_suffix_node_count",
    "baseline_divergent_node_count",
    "rank104_divergent_node_count",
    "trace_node_edit_distance",
    "trace_edge_edit_distance",
    "rank104_outlier_closed_path_gain",
    "rank104_outlier_variation_advantage",
    "rank104_outlier_delta_penalty",
    "shared_closure_tail_node_count",
    *TAIL_NODE_COLUMNS,
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "selected_branch_count": 0,
    "closure_outlier_count": 1,
    "shared_closure_tail_node_count": 2,
    "reference_witness_id": 3,
    "baseline_outlier_witness_id": 4,
    "rank104_outlier_witness_id": 5,
    "baseline_outlier_closed_gain": 6,
    "rank104_outlier_closed_gain": 7,
    "common_outlier_overhead_penalty": 8,
    "common_outlier_valley_penalty": 9,
    "rank104_outlier_extra_closed_gain_over_baseline": 10,
    "rank104_outlier_variation_advantage_over_baseline": 11,
    "rank104_outlier_delta_penalty_over_baseline": 12,
    "outlier_pair_common_suffix_node_count": 13,
    "reference_score_pareto_flag": 14,
    "outlier_score_pareto_count": 15,
    "outlier_closure_augmented_pareto_count": 16,
}


def table_rows(table: np.ndarray, columns: list[str]) -> list[dict[str, int]]:
    return [
        {column: int(values[index]) for index, column in enumerate(columns)}
        for values in table
    ]


def row_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS[: row["word_length"]])


def row_trace(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in TRACE_NODE_COLUMNS[: row["trace_node_count"]])


def score(row: dict[str, int]) -> tuple[int, int, int, int]:
    return tuple(row[column] for column in SCORE_COLUMNS)  # type: ignore[return-value]


def padded(values: tuple[int, ...], length: int) -> tuple[int, ...]:
    return values + tuple(-1 for _ in range(length - len(values)))


def tail_start(trace: tuple[int, ...], tail: tuple[int, ...]) -> int:
    for index in range(len(trace) - len(tail) + 1):
        if trace[index : index + len(tail)] == tail:
            return index
    return -1


def selected_row(
    selection_order: int,
    ranking: dict[str, int],
) -> dict[str, int]:
    trace = row_trace(ranking)
    shared_tail_start = tail_start(trace, SHARED_CLOSURE_TAIL)
    return {
        "selection_order": selection_order,
        "witness_id": ranking["strongification_witness_id"],
        "role_code": 0
        if ranking["strongification_witness_id"] == REFERENCE_WITNESS_ID
        else 1,
        "prefix_class_id": ranking["prefix_class_id"],
        "global_rank": ranking["global_rank"],
        "prefix_class_rank": ranking["prefix_class_rank"],
        "word_length": ranking["word_length"],
        **{column: ranking[column] for column in WORD_COLUMNS},
        "trace_node_count": ranking["trace_node_count"],
        **{column: ranking[column] for column in TRACE_NODE_COLUMNS},
        **{column: ranking[column] for column in SCORE_COLUMNS},
        "closed_path_count": ranking["closed_path_count"],
        "score_pareto_flag": ranking["score_pareto_flag"],
        "closure_augmented_pareto_flag": ranking["closure_augmented_pareto_flag"],
        "shared_closure_tail_flag": int(shared_tail_start >= 0),
        "shared_closure_tail_start_index": shared_tail_start,
        "shared_closure_tail_node_count": len(SHARED_CLOSURE_TAIL)
        if shared_tail_start >= 0
        else 0,
    }


def ratio_x1e6(numerator: int, denominator: int) -> int:
    if denominator == 0:
        return -1
    return numerator * 10**6 // denominator


def reference_comparison_row(
    comparison_id: int,
    reference: dict[str, int],
    outlier: dict[str, int],
) -> dict[str, int]:
    reference_trace = row_trace(reference)
    outlier_trace = row_trace(outlier)
    prefix, suffix, reference_divergent, outlier_divergent = common_prefix_suffix(
        reference_trace,
        outlier_trace,
    )
    closed_gain = outlier["closed_path_count"] - reference["closed_path_count"]
    overhead_penalty = (
        outlier["trace_detour_overhead"] - reference["trace_detour_overhead"]
    )
    variation_penalty = (
        outlier["trace_signature_total_variation"]
        - reference["trace_signature_total_variation"]
    )
    shared_tail_start = tail_start(outlier_trace, SHARED_CLOSURE_TAIL)
    return {
        "comparison_id": comparison_id,
        "reference_witness_id": reference["witness_id"],
        "outlier_witness_id": outlier["witness_id"],
        "outlier_prefix_class_id": outlier["prefix_class_id"],
        "outlier_global_rank": outlier["global_rank"],
        "reference_closed_path_count": reference["closed_path_count"],
        "outlier_closed_path_count": outlier["closed_path_count"],
        "outlier_closed_path_gain": closed_gain,
        "reference_trace_detour_overhead": reference["trace_detour_overhead"],
        "outlier_trace_detour_overhead": outlier["trace_detour_overhead"],
        "outlier_overhead_penalty": overhead_penalty,
        "reference_signature_valley_depth": reference["signature_valley_depth"],
        "outlier_signature_valley_depth": outlier["signature_valley_depth"],
        "outlier_valley_penalty": outlier["signature_valley_depth"]
        - reference["signature_valley_depth"],
        "reference_metric_gromov_delta_twice": reference[
            "metric_gromov_delta_twice"
        ],
        "outlier_metric_gromov_delta_twice": outlier[
            "metric_gromov_delta_twice"
        ],
        "outlier_delta_penalty": outlier["metric_gromov_delta_twice"]
        - reference["metric_gromov_delta_twice"],
        "reference_trace_signature_total_variation": reference[
            "trace_signature_total_variation"
        ],
        "outlier_trace_signature_total_variation": outlier[
            "trace_signature_total_variation"
        ],
        "outlier_variation_penalty": variation_penalty,
        "closure_gain_per_overhead_x1e6": ratio_x1e6(
            closed_gain,
            overhead_penalty,
        ),
        "closure_gain_per_variation_x1e6": ratio_x1e6(
            closed_gain,
            variation_penalty,
        ),
        "common_prefix_node_count": prefix,
        "common_suffix_node_count": suffix,
        "reference_divergent_node_count": len(reference_divergent),
        "outlier_divergent_node_count": len(outlier_divergent),
        "trace_node_edit_distance": levenshtein(reference_trace, outlier_trace),
        "trace_edge_edit_distance": levenshtein(
            trace_edges(reference_trace),
            trace_edges(outlier_trace),
        ),
        "outlier_shared_closure_tail_flag": int(shared_tail_start >= 0),
        "outlier_shared_closure_tail_start_index": shared_tail_start,
        **{
            column: value
            for column, value in zip(
                DIVERGENT_SOURCE_COLUMNS,
                padded(reference_divergent, MAX_DIVERGENT_NODES),
            )
        },
        **{
            column: value
            for column, value in zip(
                DIVERGENT_OUTLIER_COLUMNS,
                padded(outlier_divergent, MAX_DIVERGENT_NODES),
            )
        },
    }


def outlier_pair_row(
    baseline_outlier: dict[str, int],
    rank104_outlier: dict[str, int],
) -> dict[str, int]:
    baseline_trace = row_trace(baseline_outlier)
    rank104_trace = row_trace(rank104_outlier)
    prefix, suffix, baseline_divergent, rank104_divergent = common_prefix_suffix(
        baseline_trace,
        rank104_trace,
    )
    return {
        "pair_id": 0,
        "baseline_class_outlier_witness_id": baseline_outlier["witness_id"],
        "rank104_class_outlier_witness_id": rank104_outlier["witness_id"],
        "common_prefix_node_count": prefix,
        "common_suffix_node_count": suffix,
        "baseline_divergent_node_count": len(baseline_divergent),
        "rank104_divergent_node_count": len(rank104_divergent),
        "trace_node_edit_distance": levenshtein(baseline_trace, rank104_trace),
        "trace_edge_edit_distance": levenshtein(
            trace_edges(baseline_trace),
            trace_edges(rank104_trace),
        ),
        "rank104_outlier_closed_path_gain": rank104_outlier["closed_path_count"]
        - baseline_outlier["closed_path_count"],
        "rank104_outlier_variation_advantage": baseline_outlier[
            "trace_signature_total_variation"
        ]
        - rank104_outlier["trace_signature_total_variation"],
        "rank104_outlier_delta_penalty": rank104_outlier[
            "metric_gromov_delta_twice"
        ]
        - baseline_outlier["metric_gromov_delta_twice"],
        "shared_closure_tail_node_count": len(SHARED_CLOSURE_TAIL),
        **{
            column: value
            for column, value in zip(TAIL_NODE_COLUMNS, SHARED_CLOSURE_TAIL)
        },
    }


def build_payloads() -> dict[str, Any]:
    cost3_report = load_json(COST3_RANKING_REPORT)
    cost3_json = load_json(COST3_RANKING_JSON)
    cost3_certificate = load_json(COST3_RANKING_CERTIFICATE)
    cost3_tables = np.load(COST3_RANKING_TABLES, allow_pickle=False)
    branch_profile_table = np.asarray(
        cost3_tables["branch_profile_table"],
        dtype=np.int64,
    )
    ranking_table = np.asarray(cost3_tables["ranking_table"], dtype=np.int64)
    branch_profiles = table_rows(branch_profile_table, BRANCH_PROFILE_COLUMNS)
    rankings = table_rows(ranking_table, RANKING_COLUMNS)
    profile_by_id = {row["branch_id"]: row for row in branch_profiles}
    ranking_by_id = {row["strongification_witness_id"]: row for row in rankings}

    selected_rows = [
        selected_row(index, ranking_by_id[witness_id])
        for index, witness_id in enumerate(SELECTED_WITNESS_IDS)
    ]
    reference = selected_rows[0]
    outliers = selected_rows[1:]
    comparison_rows = [
        reference_comparison_row(index, reference, outlier)
        for index, outlier in enumerate(outliers)
    ]
    pair_rows = [outlier_pair_row(outliers[0], outliers[1])]
    observable_values = {
        "selected_branch_count": len(selected_rows),
        "closure_outlier_count": len(outliers),
        "shared_closure_tail_node_count": len(SHARED_CLOSURE_TAIL),
        "reference_witness_id": REFERENCE_WITNESS_ID,
        "baseline_outlier_witness_id": CLOSURE_OUTLIER_IDS[0],
        "rank104_outlier_witness_id": CLOSURE_OUTLIER_IDS[1],
        "baseline_outlier_closed_gain": comparison_rows[0][
            "outlier_closed_path_gain"
        ],
        "rank104_outlier_closed_gain": comparison_rows[1][
            "outlier_closed_path_gain"
        ],
        "common_outlier_overhead_penalty": comparison_rows[0][
            "outlier_overhead_penalty"
        ],
        "common_outlier_valley_penalty": comparison_rows[0][
            "outlier_valley_penalty"
        ],
        "rank104_outlier_extra_closed_gain_over_baseline": pair_rows[0][
            "rank104_outlier_closed_path_gain"
        ],
        "rank104_outlier_variation_advantage_over_baseline": pair_rows[0][
            "rank104_outlier_variation_advantage"
        ],
        "rank104_outlier_delta_penalty_over_baseline": pair_rows[0][
            "rank104_outlier_delta_penalty"
        ],
        "outlier_pair_common_suffix_node_count": pair_rows[0][
            "common_suffix_node_count"
        ],
        "reference_score_pareto_flag": reference["score_pareto_flag"],
        "outlier_score_pareto_count": sum(
            row["score_pareto_flag"] for row in outliers
        ),
        "outlier_closure_augmented_pareto_count": sum(
            row["closure_augmented_pareto_flag"] for row in outliers
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

    selected_table = table_from_rows(SELECTED_BRANCH_COLUMNS, selected_rows)
    comparison_table = table_from_rows(
        REFERENCE_COMPARISON_COLUMNS,
        comparison_rows,
    )
    pair_table = table_from_rows(OUTLIER_PAIR_COLUMNS, pair_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "cost3_ranking_report_certified": cost3_report.get("status")
        == COST3_RANKING_STATUS,
        "cost3_ranking_certificate_certified": cost3_certificate.get("status")
        == COST3_RANKING_STATUS,
        "cost3_ranking_schema_available": cost3_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_cost3_strongification_geometry_ranking@1",
        "cost3_tables_have_24_profiles_and_rankings": tuple(branch_profile_table.shape)
        == (24, len(BRANCH_PROFILE_COLUMNS))
        and tuple(ranking_table.shape) == (24, len(RANKING_COLUMNS)),
        "selected_table_shape_matches_codebook": tuple(selected_table.shape)
        == (3, len(SELECTED_BRANCH_COLUMNS)),
        "comparison_table_shape_matches_codebook": tuple(comparison_table.shape)
        == (2, len(REFERENCE_COMPARISON_COLUMNS)),
        "pair_table_shape_matches_codebook": tuple(pair_table.shape)
        == (1, len(OUTLIER_PAIR_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
        "selected_witnesses_match_expected_frontier": [
            row["witness_id"] for row in selected_rows
        ]
        == [17, 9, 23],
        "reference_is_score_pareto_and_all_are_closure_augmented_pareto": reference[
            "score_pareto_flag"
        ]
        == 1
        and all(row["closure_augmented_pareto_flag"] == 1 for row in selected_rows)
        and sum(row["score_pareto_flag"] for row in outliers) == 0,
        "outliers_share_tail_54_45_29_28_34_44": all(
            row["shared_closure_tail_flag"] == 1
            and row["shared_closure_tail_node_count"] == len(SHARED_CLOSURE_TAIL)
            for row in outliers
        ),
        "reference_lacks_shared_closure_tail": reference[
            "shared_closure_tail_flag"
        ]
        == 0,
        "outliers_pay_common_overhead_and_valley_penalty": all(
            row["outlier_overhead_penalty"] == 2
            and row["outlier_valley_penalty"] == 12
            for row in comparison_rows
        ),
        "outlier_closure_gains_are_four_and_sixteen": [
            row["outlier_closed_path_gain"] for row in comparison_rows
        ]
        == [4, 16],
        "rank104_outlier_is_closure_efficient_but_delta_worse": pair_rows[0][
            "rank104_outlier_closed_path_gain"
        ]
        == 12
        and pair_rows[0]["rank104_outlier_variation_advantage"] == 52
        and pair_rows[0]["rank104_outlier_delta_penalty"] == 2,
        "outlier_pair_common_suffix_is_shared_tail": pair_rows[0][
            "common_suffix_node_count"
        ]
        == len(SHARED_CLOSURE_TAIL)
        and all(
            pair_rows[0][column] == value
            for column, value in zip(TAIL_NODE_COLUMNS, SHARED_CLOSURE_TAIL)
        ),
        "profile_scores_match_selected_rankings": all(
            score(profile_by_id[row["witness_id"]]) == score(row)
            and profile_by_id[row["witness_id"]]["closed_path_count"]
            == row["closed_path_count"]
            and row_trace(profile_by_id[row["witness_id"]]) == row_trace(row)
            for row in selected_rows
        ),
    }

    witness = {
        "reference": {
            "witness_id": reference["witness_id"],
            "word": list(row_word(reference)),
            "trace": list(row_trace(reference)),
            "score": list(score(reference)),
            "closed_path_count": reference["closed_path_count"],
        },
        "closure_outliers": [
            {
                "witness_id": row["witness_id"],
                "prefix_class_id": row["prefix_class_id"],
                "global_rank": row["global_rank"],
                "word": list(row_word(row)),
                "trace": list(row_trace(row)),
                "score": list(score(row)),
                "closed_path_count": row["closed_path_count"],
                "shared_closure_tail_start_index": row[
                    "shared_closure_tail_start_index"
                ],
            }
            for row in outliers
        ],
        "reference_comparisons": comparison_rows,
        "outlier_pair_comparison": pair_rows[0],
        "selected_table_sha256": sha_array(selected_table),
        "comparison_table_sha256": sha_array(comparison_table),
        "pair_table_sha256": sha_array(pair_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    geometry = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry@1",
        "object": "d20",
        "comparison_rule": {
            "reference": "witness 17, the unique score-only Pareto point",
            "outliers": "witnesses 9 and 23, the extra closure-augmented Pareto branches",
            "shared_tail": list(SHARED_CLOSURE_TAIL),
            "score_coordinates": SCORE_COLUMNS,
        },
        "summary": {
            "reference_witness_id": REFERENCE_WITNESS_ID,
            "closure_outlier_witness_ids": list(CLOSURE_OUTLIER_IDS),
            "shared_closure_tail": list(SHARED_CLOSURE_TAIL),
            "reference_score": list(score(reference)),
            "outlier_scores": {
                str(row["witness_id"]): list(score(row)) for row in outliers
            },
            "outlier_closed_path_gains": {
                str(row["outlier_witness_id"]): row["outlier_closed_path_gain"]
                for row in comparison_rows
            },
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_RICH_OUTLIER_GEOMETRY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "witnesses 9 and 23 are the two closure-augmented Pareto outliers outside the unique score-Pareto witness 17",
            "both outliers share the closure-rich terminal trace tail 54->45->29->28->34->44",
            "both outliers pay the same +2 overhead and +12 valley-depth penalty relative to witness 17",
            "witness 23 buys the larger closure gain, 24 paths instead of 12, with 52 less variation than witness 9 but delta_twice two units worse",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The two closure-augmented outliers survive because they both enter "
            "a shared terminal closure tail 54->45->29->28->34->44 that is "
            "absent from the score-optimal witness 17. This tail raises closure "
            "multiplicity, but it is geometrically expensive: both outliers pay "
            "+2 trace overhead and +12 valley depth relative to witness 17. "
            "Witness 23 is the stronger closure branch, gaining 16 closed paths "
            "over witness 17 and 12 over witness 9, while carrying 52 less "
            "variation than witness 9 but delta_twice two units worse."
        ),
        "stage_protocol": {
            "draft": "take the closure-augmented frontier outliers from the cost-three ranking certificate",
            "witness": "materialize witnesses 17, 9, and 23 with traces, scores, closure counts, and shared-tail flags",
            "coherence": "compare each outlier against witness17 and compare the outlier pair against their shared closure tail",
            "closure": "certify the closure multiplicity versus geometric optimality tradeoff",
            "emit": "emit selected-branch, comparison, pair, observable, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "cost3_ranking_report": input_entry(
                COST3_RANKING_REPORT,
                {
                    "status": cost3_report.get("status"),
                    "certificate_sha256": cost3_report.get("certificate_sha256"),
                },
            ),
            "cost3_ranking_json": input_entry(COST3_RANKING_JSON),
            "cost3_ranking_branch_profiles": input_entry(
                COST3_RANKING_BRANCH_PROFILES
            ),
            "cost3_ranking_rankings": input_entry(COST3_RANKING_RANKINGS),
            "cost3_ranking_tables": input_entry(COST3_RANKING_TABLES),
            "cost3_ranking_certificate": input_entry(COST3_RANKING_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_rich_outlier_geometry": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_rich_outlier_geometry.json"
            ),
            "aperture_closure_outlier_selected_branches_csv": relpath(
                OUT_DIR / "aperture_closure_outlier_selected_branches.csv"
            ),
            "aperture_closure_outlier_reference_comparisons_csv": relpath(
                OUT_DIR / "aperture_closure_outlier_reference_comparisons.csv"
            ),
            "aperture_closure_outlier_pair_comparison_csv": relpath(
                OUT_DIR / "aperture_closure_outlier_pair_comparison.csv"
            ),
            "aperture_closure_outlier_observables_csv": relpath(
                OUT_DIR / "aperture_closure_outlier_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_rich_outlier_geometry_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the selected frontier branches 17, 9, and 23",
                "the reference-to-outlier trace divergence, score penalties, and closure gains",
                "the shared outlier terminal tail 54->45->29->28->34->44",
                "the statement that closure-rich multiplicity is bought by worse geometry relative to witness17",
                "the witness23 versus witness9 tradeoff inside the closure-rich pair",
            ],
            "does_not_certify_because_not_required": [
                "closure path enumeration beyond counts certified by the cost-three ranking layer",
                "new ranking objectives beyond the declared score and closure comparisons",
                "edit costs above three",
                "deletions or movement of the final promoted x5 suffix",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Open the shared closure tail 54->45->29->28->34->44 at the carrier-path "
            "level: enumerate which carrier endpoints create the 12/24 closure "
            "multiplicity split between witnesses 9 and 23."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_rich_outlier_geometry_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified cost-three strongification geometry ranking artifacts",
            "select witnesses 17, 9, and 23 from the certified ranking table",
            "compare closure-rich outlier traces and scores against witness17",
            "compare the outlier pair and verify the shared terminal closure tail",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_rich_outlier_geometry": geometry,
        "aperture_closure_outlier_selected_branches_csv": csv_text(
            SELECTED_BRANCH_COLUMNS,
            selected_rows,
        ),
        "aperture_closure_outlier_reference_comparisons_csv": csv_text(
            REFERENCE_COMPARISON_COLUMNS,
            comparison_rows,
        ),
        "aperture_closure_outlier_pair_comparison_csv": csv_text(
            OUTLIER_PAIR_COLUMNS,
            pair_rows,
        ),
        "aperture_closure_outlier_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "selected_branch_table": selected_table,
        "comparison_table": comparison_table,
        "pair_table": pair_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_rich_outlier_geometry.json",
        payloads["signature_boundary_spine_aperture_closure_rich_outlier_geometry"],
    )
    (OUT_DIR / "aperture_closure_outlier_selected_branches.csv").write_text(
        payloads["aperture_closure_outlier_selected_branches_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_outlier_reference_comparisons.csv"
    ).write_text(
        payloads["aperture_closure_outlier_reference_comparisons_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_outlier_pair_comparison.csv").write_text(
        payloads["aperture_closure_outlier_pair_comparison_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_outlier_observables.csv").write_text(
        payloads["aperture_closure_outlier_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_tables.npz",
        selected_branch_table=payloads["selected_branch_table"],
        comparison_table=payloads["comparison_table"],
        pair_table=payloads["pair_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_rich_outlier_geometry_certificate"
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
                "reference": witness["reference"],
                "closure_outliers": witness["closure_outliers"],
                "outlier_pair_comparison": witness["outlier_pair_comparison"],
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
