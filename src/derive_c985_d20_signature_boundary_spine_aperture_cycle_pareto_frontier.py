from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        CANDIDATE_COLUMNS as RANKING_CANDIDATE_COLUMNS,
        OUT_DIR as RANKING_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_x2_clean_detour_choice import (
        OUT_DIR as CLEAN_DETOUR_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        DETOUR_EDGE_COLUMNS,
        OUT_DIR as X2_DETOUR_DIR,
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
        CANDIDATE_COLUMNS as RANKING_CANDIDATE_COLUMNS,
        OUT_DIR as RANKING_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        OUT_DIR as TYPED_CORRIDOR_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_x2_clean_detour_choice import (
        OUT_DIR as CLEAN_DETOUR_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_x2_detour_fan import (
        DETOUR_EDGE_COLUMNS,
        OUT_DIR as X2_DETOUR_DIR,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_FRONTIER_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

RANKING_REPORT = RANKING_DIR / "report.json"
RANKING_JSON = RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking.json"
RANKING_CANDIDATES = RANKING_DIR / "aperture_cycle_ranked_candidates.csv"
RANKING_OBSERVABLES = RANKING_DIR / "aperture_cycle_ranking_observables.csv"
RANKING_TABLES = RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking_tables.npz"
RANKING_CERTIFICATE = (
    RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking_certificate.json"
)

X2_DETOUR_REPORT = X2_DETOUR_DIR / "report.json"
X2_DETOUR_EDGES = X2_DETOUR_DIR / "x2_detour_edges.csv"
X2_DETOUR_RETURNS = X2_DETOUR_DIR / "x2_detour_return_paths.csv"
X2_DETOUR_TABLES = X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_tables.npz"
X2_DETOUR_CERTIFICATE = (
    X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_certificate.json"
)

CLEAN_DETOUR_REPORT = CLEAN_DETOUR_DIR / "report.json"
CLEAN_DETOUR_JSON = CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice.json"
CLEAN_DETOUR_CHOICES = CLEAN_DETOUR_DIR / "x2_clean_detour_return_choices.csv"
CLEAN_DETOUR_TABLES = (
    CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice_tables.npz"
)
CLEAN_DETOUR_CERTIFICATE = (
    CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice_certificate.json"
)

TYPED_CORRIDOR_REPORT = TYPED_CORRIDOR_DIR / "report.json"
TYPED_CORRIDOR_EDGES = TYPED_CORRIDOR_DIR / "corridor_edge_symbols.csv"
TYPED_CORRIDOR_TABLES = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_tables.npz"
)
TYPED_CORRIDOR_CERTIFICATE = (
    TYPED_CORRIDOR_DIR / "signature_boundary_spine_typed_corridors_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier.py"
)

SELECTED_CANDIDATE_ID = 6
PARETO_CANDIDATE_IDS = [0, 1, 2, 3, 4, 5, 6]
DOMINATED_CANDIDATE_IDS = [7, 8, 9]
GEODESIC_MIXED_CANDIDATE_IDS = [0, 1, 2, 3, 4, 5]

PARETO_CANDIDATE_COLUMNS = [
    "candidate_id",
    "rank_order",
    "cell_edge_0_id",
    "cell_edge_1_id",
    "cell_edge_2_id",
    "cell_edge_3_id",
    "symbol_0_id",
    "symbol_1_id",
    "symbol_2_id",
    "symbol_3_id",
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "clean_single_x2_first_contact_flag",
    "mixed_x2_x5_first_contact_flag",
    "x1_tail_preserving_flag",
    "x0_tail_flag",
    "typed_tail_abandonment_flag",
    "typed_boundary_cost",
    "geodesic_optimal_flag",
    "typed_optimal_flag",
    "pareto_frontier_flag",
    "dominated_flag",
    "pareto_class_code",
]

PARETO_CLASS_COLUMNS = [
    "pareto_class_code",
    "representative_candidate_id",
    "candidate_count",
    "pareto_frontier_class_flag",
    "geodesic_optimal_flag",
    "clean_single_x2_first_contact_flag",
    "mixed_x2_x5_first_contact_flag",
    "x1_tail_preserving_flag",
    "x0_tail_flag",
    "typed_boundary_cost",
    "min_rank_order",
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
    "candidate_count": 0,
    "pareto_candidate_count": 1,
    "pareto_class_count": 2,
    "dominated_candidate_count": 3,
    "geodesic_optimal_mixed_count": 4,
    "typed_optimal_clean_x1_count": 5,
    "mixed_x2_x5_required_for_zero_overhead_flag": 6,
    "x1_tail_abandoned_for_zero_overhead_flag": 7,
    "selected_candidate_id": 8,
    "selected_typed_boundary_cost": 9,
    "selected_trace_detour_overhead": 10,
    "selected_signature_valley_depth": 11,
    "min_trace_detour_overhead": 12,
    "min_typed_boundary_cost": 13,
}

CLASS_NAMES = {
    0: "geodesic_mixed_x5_tail",
    1: "clean_x1_tail",
    2: "mixed_x1_tail",
    3: "clean_x0_tail",
    4: "mixed_x0_tail",
}

PARETO_METRIC_COLUMNS = [
    "trace_detour_overhead",
    "typed_boundary_cost",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
]


def dominates(left: dict[str, int], right: dict[str, int]) -> bool:
    left_values = [int(left[column]) for column in PARETO_METRIC_COLUMNS]
    right_values = [int(right[column]) for column in PARETO_METRIC_COLUMNS]
    return all(a <= b for a, b in zip(left_values, right_values)) and any(
        a < b for a, b in zip(left_values, right_values)
    )


def classify_candidate(row: dict[str, int]) -> int:
    clean = int(row["clean_single_x2_first_contact_flag"])
    mixed = int(row["mixed_x2_x5_first_contact_flag"])
    x1_tail = int(row["x1_tail_preserving_flag"])
    x0_tail = int(row["x0_tail_flag"])
    geodesic = int(row["geodesic_optimal_flag"])
    if geodesic and mixed and not x1_tail and not x0_tail:
        return 0
    if clean and x1_tail:
        return 1
    if mixed and x1_tail:
        return 2
    if clean and x0_tail:
        return 3
    if mixed and x0_tail:
        return 4
    raise AssertionError(f"unclassified Pareto candidate {row['candidate_id']}")


def build_candidate_rows(
    ranking_rows: list[dict[str, int]],
    detour_edges_by_cell: dict[int, dict[str, int]],
) -> list[dict[str, int]]:
    raw_rows: list[dict[str, int]] = []
    for ranking_row in ranking_rows:
        first_edge_id = int(ranking_row["cell_edge_0_id"])
        detour_edge = detour_edges_by_cell[first_edge_id]
        clean_first = int(detour_edge["single_x2_flag"])
        mixed_first = int(detour_edge["mixed_x2_x5_flag"])
        x1_tail = int(ranking_row["x1_tail_preserving_flag"])
        typed_abandonment = int(x1_tail == 0)
        typed_cost = mixed_first + typed_abandonment
        row = {
            "candidate_id": int(ranking_row["candidate_id"]),
            "rank_order": int(ranking_row["rank_order"]),
            "cell_edge_0_id": first_edge_id,
            "cell_edge_1_id": int(ranking_row["cell_edge_1_id"]),
            "cell_edge_2_id": int(ranking_row["cell_edge_2_id"]),
            "cell_edge_3_id": int(ranking_row["cell_edge_3_id"]),
            "symbol_0_id": int(ranking_row["symbol_0_id"]),
            "symbol_1_id": int(ranking_row["symbol_1_id"]),
            "symbol_2_id": int(ranking_row["symbol_2_id"]),
            "symbol_3_id": int(ranking_row["symbol_3_id"]),
            "trace_detour_overhead": int(ranking_row["trace_detour_overhead"]),
            "signature_valley_depth": int(ranking_row["signature_valley_depth"]),
            "metric_gromov_delta_twice": int(ranking_row["metric_gromov_delta_twice"]),
            "trace_signature_total_variation": int(
                ranking_row["trace_signature_total_variation"]
            ),
            "clean_single_x2_first_contact_flag": clean_first,
            "mixed_x2_x5_first_contact_flag": mixed_first,
            "x1_tail_preserving_flag": x1_tail,
            "x0_tail_flag": int(ranking_row["x0_tail_flag"]),
            "typed_tail_abandonment_flag": typed_abandonment,
            "typed_boundary_cost": typed_cost,
            "geodesic_optimal_flag": int(ranking_row["geodesic_equivalent_flag"]),
            "typed_optimal_flag": 0,
            "pareto_frontier_flag": 0,
            "dominated_flag": 0,
            "pareto_class_code": -1,
        }
        raw_rows.append(row)

    min_typed_cost = min(int(row["typed_boundary_cost"]) for row in raw_rows)
    for row in raw_rows:
        row["typed_optimal_flag"] = int(int(row["typed_boundary_cost"]) == min_typed_cost)
        row["dominated_flag"] = int(
            any(
                dominates(other, row)
                for other in raw_rows
                if int(other["candidate_id"]) != int(row["candidate_id"])
            )
        )
        row["pareto_frontier_flag"] = int(row["dominated_flag"] == 0)
        row["pareto_class_code"] = classify_candidate(row)
    return raw_rows


def build_class_rows(candidate_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    class_rows: list[dict[str, int]] = []
    for class_code in sorted(CLASS_NAMES):
        members = [
            row
            for row in candidate_rows
            if int(row["pareto_class_code"]) == int(class_code)
        ]
        if not members:
            continue
        representative = min(members, key=lambda row: int(row["rank_order"]))
        class_rows.append(
            {
                "pareto_class_code": class_code,
                "representative_candidate_id": int(representative["candidate_id"]),
                "candidate_count": len(members),
                "pareto_frontier_class_flag": int(
                    any(int(row["pareto_frontier_flag"]) == 1 for row in members)
                ),
                "geodesic_optimal_flag": int(
                    any(int(row["geodesic_optimal_flag"]) == 1 for row in members)
                ),
                "clean_single_x2_first_contact_flag": int(
                    any(
                        int(row["clean_single_x2_first_contact_flag"]) == 1
                        for row in members
                    )
                ),
                "mixed_x2_x5_first_contact_flag": int(
                    any(int(row["mixed_x2_x5_first_contact_flag"]) == 1 for row in members)
                ),
                "x1_tail_preserving_flag": int(
                    any(int(row["x1_tail_preserving_flag"]) == 1 for row in members)
                ),
                "x0_tail_flag": int(any(int(row["x0_tail_flag"]) == 1 for row in members)),
                "typed_boundary_cost": min(
                    int(row["typed_boundary_cost"]) for row in members
                ),
                "min_rank_order": min(int(row["rank_order"]) for row in members),
                "min_trace_detour_overhead": min(
                    int(row["trace_detour_overhead"]) for row in members
                ),
                "min_signature_valley_depth": min(
                    int(row["signature_valley_depth"]) for row in members
                ),
                "min_metric_gromov_delta_twice": min(
                    int(row["metric_gromov_delta_twice"]) for row in members
                ),
                "min_trace_signature_total_variation": min(
                    int(row["trace_signature_total_variation"]) for row in members
                ),
            }
        )
    return class_rows


def build_payloads() -> dict[str, Any]:
    ranking_report = load_json(RANKING_REPORT)
    ranking = load_json(RANKING_JSON)
    ranking_certificate = load_json(RANKING_CERTIFICATE)
    x2_detour_report = load_json(X2_DETOUR_REPORT)
    x2_detour_certificate = load_json(X2_DETOUR_CERTIFICATE)
    clean_detour_report = load_json(CLEAN_DETOUR_REPORT)
    clean_detour = load_json(CLEAN_DETOUR_JSON)
    clean_detour_certificate = load_json(CLEAN_DETOUR_CERTIFICATE)
    typed_corridor_report = load_json(TYPED_CORRIDOR_REPORT)
    typed_corridor_certificate = load_json(TYPED_CORRIDOR_CERTIFICATE)

    ranking_tables = np.load(RANKING_TABLES, allow_pickle=False)
    x2_detour_tables = np.load(X2_DETOUR_TABLES, allow_pickle=False)
    clean_detour_tables = np.load(CLEAN_DETOUR_TABLES, allow_pickle=False)
    typed_corridor_tables = np.load(TYPED_CORRIDOR_TABLES, allow_pickle=False)
    ranking_candidate_table = np.asarray(
        ranking_tables["candidate_table"], dtype=np.int64
    )
    x2_detour_edge_table = np.asarray(x2_detour_tables["edge_table"], dtype=np.int64)
    clean_choice_table = np.asarray(
        clean_detour_tables["return_choice_table"], dtype=np.int64
    )
    typed_corridor_edge_table = np.asarray(
        typed_corridor_tables["corridor_edge_table"], dtype=np.int64
    )

    ranking_rows = read_int_csv(RANKING_CANDIDATES)
    detour_edge_rows = read_int_csv(X2_DETOUR_EDGES)
    detour_return_rows = read_int_csv(X2_DETOUR_RETURNS)
    clean_choice_rows = read_int_csv(CLEAN_DETOUR_CHOICES)
    typed_corridor_rows = read_int_csv(TYPED_CORRIDOR_EDGES)

    detour_edges_by_cell = {
        int(row["cell_edge_id"]): row for row in detour_edge_rows
    }
    candidate_rows = build_candidate_rows(ranking_rows, detour_edges_by_cell)
    class_rows = build_class_rows(candidate_rows)

    selected_row = next(
        row for row in candidate_rows if int(row["candidate_id"]) == SELECTED_CANDIDATE_ID
    )
    pareto_rows = [
        row for row in candidate_rows if int(row["pareto_frontier_flag"]) == 1
    ]
    dominated_rows = [row for row in candidate_rows if int(row["dominated_flag"]) == 1]
    geodesic_rows = [
        row
        for row in candidate_rows
        if int(row["trace_detour_overhead"]) == 0
    ]
    typed_optimal_clean_x1_rows = [
        row
        for row in candidate_rows
        if int(row["typed_boundary_cost"]) == 0
        and int(row["clean_single_x2_first_contact_flag"]) == 1
        and int(row["x1_tail_preserving_flag"]) == 1
    ]
    pareto_class_count = len(
        {
            int(row["pareto_class_code"])
            for row in candidate_rows
            if int(row["pareto_frontier_flag"]) == 1
        }
    )

    observable_values = {
        "candidate_count": len(candidate_rows),
        "pareto_candidate_count": len(pareto_rows),
        "pareto_class_count": pareto_class_count,
        "dominated_candidate_count": len(dominated_rows),
        "geodesic_optimal_mixed_count": len(GEODESIC_MIXED_CANDIDATE_IDS),
        "typed_optimal_clean_x1_count": len(typed_optimal_clean_x1_rows),
        "mixed_x2_x5_required_for_zero_overhead_flag": int(
            all(int(row["mixed_x2_x5_first_contact_flag"]) == 1 for row in geodesic_rows)
        ),
        "x1_tail_abandoned_for_zero_overhead_flag": int(
            all(int(row["typed_tail_abandonment_flag"]) == 1 for row in geodesic_rows)
        ),
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_typed_boundary_cost": int(selected_row["typed_boundary_cost"]),
        "selected_trace_detour_overhead": int(selected_row["trace_detour_overhead"]),
        "selected_signature_valley_depth": int(selected_row["signature_valley_depth"]),
        "min_trace_detour_overhead": min(
            int(row["trace_detour_overhead"]) for row in candidate_rows
        ),
        "min_typed_boundary_cost": min(
            int(row["typed_boundary_cost"]) for row in candidate_rows
        ),
    }
    observable_rows = [
        {
            "observable_id": observable_id,
            "observable_code": code,
            "value_x1e12": int(observable_values[name]),
            "aux_id": -1,
        }
        for name, code in sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
        for observable_id in [code]
    ]

    candidate_table = table_from_rows(PARETO_CANDIDATE_COLUMNS, candidate_rows)
    class_table = table_from_rows(PARETO_CLASS_COLUMNS, class_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    pareto_candidate_ids = [int(row["candidate_id"]) for row in pareto_rows]
    dominated_candidate_ids = [int(row["candidate_id"]) for row in dominated_rows]
    geodesic_mixed_rows = [
        row
        for row in candidate_rows
        if int(row["candidate_id"]) in GEODESIC_MIXED_CANDIDATE_IDS
    ]
    class_by_code = {int(row["pareto_class_code"]): row for row in class_rows}
    selected_clean_choice = next(
        row
        for row in clean_choice_rows
        if int(row["least_disturbance_flag"]) == 1
    )
    x1_tail_corridor = next(
        row
        for row in typed_corridor_rows
        if int(row["boundary_spine_rank"]) == 5
        and int(row["negative_carrier_mask_class_id"]) == 8
        and int(row["shared_symbol_id"]) == 1
    )
    x0_tail_corridor = next(
        row
        for row in typed_corridor_rows
        if int(row["boundary_spine_rank"]) == 3
        and int(row["negative_carrier_mask_class_id"]) == 7
        and int(row["shared_symbol_id"]) == 0
    )

    checks = {
        "ranking_report_certified": ranking_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_CERTIFIED",
        "ranking_certificate_certified": ranking_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_CERTIFIED",
        "x2_detour_report_certified": x2_detour_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "x2_detour_certificate_certified": x2_detour_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "clean_detour_report_certified": clean_detour_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_CERTIFIED",
        "clean_detour_certificate_certified": clean_detour_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_CERTIFIED",
        "typed_corridor_report_certified": typed_corridor_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "typed_corridor_certificate_certified": typed_corridor_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_TYPED_CORRIDORS_CERTIFIED",
        "ranking_schema_available": ranking.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_cycle_ranking@1",
        "clean_detour_schema_available": clean_detour.get("schema")
        == "c985.d20_signature_boundary_spine_x2_clean_detour_choice@1",
        "ranking_candidate_table_shape_is_10_by_34": tuple(
            ranking_candidate_table.shape
        )
        == (10, len(RANKING_CANDIDATE_COLUMNS)),
        "x2_detour_edge_table_shape_is_13_by_15": tuple(x2_detour_edge_table.shape)
        == (13, len(DETOUR_EDGE_COLUMNS)),
        "clean_choice_table_shape_is_2_choices": tuple(clean_choice_table.shape)[0] == 2,
        "typed_corridor_table_has_16_edges": tuple(typed_corridor_edge_table.shape)[0]
        == 16,
        "candidate_count_is_10": len(candidate_rows) == 10,
        "first_contact_flags_match_expected": [
            (
                int(row["candidate_id"]),
                int(row["cell_edge_0_id"]),
                int(row["clean_single_x2_first_contact_flag"]),
                int(row["mixed_x2_x5_first_contact_flag"]),
            )
            for row in candidate_rows
        ]
        == [
            (0, 39, 0, 1),
            (1, 39, 0, 1),
            (2, 39, 0, 1),
            (3, 41, 0, 1),
            (4, 41, 0, 1),
            (5, 41, 0, 1),
            (6, 14, 1, 0),
            (7, 41, 0, 1),
            (8, 14, 1, 0),
            (9, 41, 0, 1),
        ],
        "zero_overhead_requires_mixed_first_contact": all(
            int(row["mixed_x2_x5_first_contact_flag"]) == 1 for row in geodesic_rows
        ),
        "zero_overhead_abandons_x1_tail": all(
            int(row["x1_tail_preserving_flag"]) == 0 for row in geodesic_rows
        ),
        "geodesic_mixed_candidate_ids_match": [
            int(row["candidate_id"]) for row in geodesic_mixed_rows
        ]
        == GEODESIC_MIXED_CANDIDATE_IDS,
        "typed_cost_zero_is_unique_selected_candidate": [
            int(row["candidate_id"])
            for row in candidate_rows
            if int(row["typed_boundary_cost"]) == 0
        ]
        == [SELECTED_CANDIDATE_ID],
        "selected_candidate_is_clean_x1_tail": int(
            selected_row["clean_single_x2_first_contact_flag"]
        )
        == 1
        and int(selected_row["mixed_x2_x5_first_contact_flag"]) == 0
        and int(selected_row["x1_tail_preserving_flag"]) == 1
        and int(selected_row["typed_boundary_cost"]) == 0,
        "selected_candidate_matches_prior_clean_choice": [
            int(selected_row[f"cell_edge_{index}_id"]) for index in range(2)
        ]
        == [
            int(selected_clean_choice["x2_cell_edge_id"]),
            int(selected_clean_choice["return_cell_edge_id"]),
        ],
        "typed_tail_witnesses_exist": int(x1_tail_corridor["shared_symbol_id"]) == 1
        and int(x0_tail_corridor["shared_symbol_id"]) == 0,
        "pareto_candidate_ids_match": pareto_candidate_ids == PARETO_CANDIDATE_IDS,
        "dominated_candidate_ids_match": dominated_candidate_ids
        == DOMINATED_CANDIDATE_IDS,
        "candidate_7_dominated_by_selected_candidate": dominates(
            selected_row, next(row for row in candidate_rows if int(row["candidate_id"]) == 7)
        ),
        "candidate_8_dominated_by_selected_candidate": dominates(
            selected_row, next(row for row in candidate_rows if int(row["candidate_id"]) == 8)
        ),
        "candidate_9_is_dominated": int(
            next(row for row in candidate_rows if int(row["candidate_id"]) == 9)[
                "dominated_flag"
            ]
        )
        == 1,
        "pareto_class_count_is_2": pareto_class_count == 2,
        "class_table_has_5_rows": len(class_rows) == 5,
        "geodesic_class_has_6_candidates_and_typed_cost_2": int(
            class_by_code[0]["candidate_count"]
        )
        == 6
        and int(class_by_code[0]["typed_boundary_cost"]) == 2
        and int(class_by_code[0]["min_trace_detour_overhead"]) == 0,
        "clean_x1_class_is_selected_and_typed_cost_0": int(
            class_by_code[1]["representative_candidate_id"]
        )
        == SELECTED_CANDIDATE_ID
        and int(class_by_code[1]["typed_boundary_cost"]) == 0
        and int(class_by_code[1]["min_trace_detour_overhead"]) == 3,
        "candidate_table_shape_is_10_by_25": tuple(candidate_table.shape)
        == (10, len(PARETO_CANDIDATE_COLUMNS)),
        "class_table_shape_is_5_by_15": tuple(class_table.shape)
        == (5, len(PARETO_CLASS_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "candidate_count": len(candidate_rows),
        "pareto_candidate_ids": pareto_candidate_ids,
        "dominated_candidate_ids": dominated_candidate_ids,
        "pareto_classes": [
            {
                "class_code": int(row["pareto_class_code"]),
                "class_name": CLASS_NAMES[int(row["pareto_class_code"])],
                "representative_candidate_id": int(row["representative_candidate_id"]),
                "candidate_count": int(row["candidate_count"]),
                "pareto_frontier_class": bool(row["pareto_frontier_class_flag"]),
                "typed_boundary_cost": int(row["typed_boundary_cost"]),
                "trace_detour_overhead": int(row["min_trace_detour_overhead"]),
                "signature_valley_depth": int(row["min_signature_valley_depth"]),
                "metric_gromov_delta": float(
                    int(row["min_metric_gromov_delta_twice"]) / 2.0
                ),
                "trace_signature_total_variation": int(
                    row["min_trace_signature_total_variation"]
                ),
            }
            for row in class_rows
        ],
        "selected_candidate": {
            "candidate_id": int(selected_row["candidate_id"]),
            "edge_cycle": [
                int(selected_row[f"cell_edge_{index}_id"]) for index in range(4)
            ],
            "symbol_cycle": [
                int(selected_row[f"symbol_{index}_id"]) for index in range(4)
            ],
            "typed_boundary_cost": int(selected_row["typed_boundary_cost"]),
            "trace_detour_overhead": int(selected_row["trace_detour_overhead"]),
            "signature_valley_depth": int(selected_row["signature_valley_depth"]),
            "metric_gromov_delta": float(
                int(selected_row["metric_gromov_delta_twice"]) / 2.0
            ),
        },
        "candidate_table_sha256": sha_array(candidate_table),
        "class_table_sha256": sha_array(class_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    pareto_frontier = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_pareto_frontier@1",
        "object": "d20",
        "cost_model": {
            "geometry_cost_vector": [
                "trace_detour_overhead",
                "signature_valley_depth",
                "metric_gromov_delta_twice",
                "trace_signature_total_variation",
            ],
            "typed_boundary_cost": (
                "mixed_x2_x5_first_contact_flag + "
                "typed_tail_abandonment_flag"
            ),
            "dominance_rule": (
                "a candidate dominates another when it is no worse in "
                "trace overhead, typed-boundary cost, valley depth, Gromov "
                "delta twice, and signature variation, and strictly better "
                "in at least one"
            ),
        },
        "class_names": {str(key): value for key, value in CLASS_NAMES.items()},
        "pareto_candidate_ids": pareto_candidate_ids,
        "dominated_candidate_ids": dominated_candidate_ids,
        "summary": {
            "pareto_class_count": pareto_class_count,
            "geodesic_optimal_mixed_candidate_count": len(
                GEODESIC_MIXED_CANDIDATE_IDS
            ),
            "typed_optimal_clean_x1_candidate_id": SELECTED_CANDIDATE_ID,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_pareto_frontier_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_FRONTIER_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the six zero-overhead cycles are geodesic-optimal but require mixed x2/x5 first contact and abandon the certified x1 tail",
            "the selected x2,x1,x4,x5 cycle is the unique typed-cost-zero candidate and remains Pareto-optimal despite overhead 3",
            "candidate 7 is typed-dominated by the selected clean x1 cycle, while the x0-tail family is also dominated",
            "the finite comparable class has exactly two Pareto frontier classes: geodesic-mixed and clean-x1 typed-tail preserving",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_pareto_frontier@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The comparable aperture-cycle family has a two-class Pareto "
            "frontier: zero-overhead mixed x2/x5 cycles minimize geometry but "
            "pay typed-boundary cost 2, while the selected clean x1-tail cycle "
            "minimizes typed-boundary cost at 0 and pays overhead 3."
        ),
        "stage_protocol": {
            "draft": "lift ranked aperture cycles into a two-axis geometry/typing cost model",
            "witness": "materialize clean versus mixed first-contact flags, x1-tail preservation, and typed costs",
            "coherence": "compute finite nondomination under trace overhead, typed cost, valley depth, delta, and variation",
            "closure": "certify the Pareto frontier within the existing 10-cycle comparable class only",
            "emit": "emit Pareto JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "ranking_report": input_entry(
                RANKING_REPORT,
                {
                    "status": ranking_report.get("status"),
                    "certificate_sha256": ranking_report.get("certificate_sha256"),
                },
            ),
            "ranking_json": input_entry(RANKING_JSON),
            "ranking_candidates": input_entry(RANKING_CANDIDATES),
            "ranking_observables": input_entry(RANKING_OBSERVABLES),
            "ranking_tables": input_entry(RANKING_TABLES),
            "ranking_certificate": input_entry(RANKING_CERTIFICATE),
            "x2_detour_report": input_entry(
                X2_DETOUR_REPORT,
                {
                    "status": x2_detour_report.get("status"),
                    "certificate_sha256": x2_detour_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "x2_detour_edges": input_entry(X2_DETOUR_EDGES),
            "x2_detour_returns": input_entry(X2_DETOUR_RETURNS),
            "x2_detour_tables": input_entry(X2_DETOUR_TABLES),
            "x2_detour_certificate": input_entry(X2_DETOUR_CERTIFICATE),
            "clean_detour_report": input_entry(
                CLEAN_DETOUR_REPORT,
                {
                    "status": clean_detour_report.get("status"),
                    "certificate_sha256": clean_detour_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "clean_detour_json": input_entry(CLEAN_DETOUR_JSON),
            "clean_detour_choices": input_entry(CLEAN_DETOUR_CHOICES),
            "clean_detour_tables": input_entry(CLEAN_DETOUR_TABLES),
            "clean_detour_certificate": input_entry(CLEAN_DETOUR_CERTIFICATE),
            "typed_corridor_report": input_entry(
                TYPED_CORRIDOR_REPORT,
                {
                    "status": typed_corridor_report.get("status"),
                    "certificate_sha256": typed_corridor_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "typed_corridor_edges": input_entry(TYPED_CORRIDOR_EDGES),
            "typed_corridor_tables": input_entry(TYPED_CORRIDOR_TABLES),
            "typed_corridor_certificate": input_entry(TYPED_CORRIDOR_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_cycle_pareto_frontier": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier.json"
            ),
            "aperture_cycle_pareto_candidates_csv": relpath(
                OUT_DIR / "aperture_cycle_pareto_candidates.csv"
            ),
            "aperture_cycle_pareto_classes_csv": relpath(
                OUT_DIR / "aperture_cycle_pareto_classes.csv"
            ),
            "aperture_cycle_pareto_observables_csv": relpath(
                OUT_DIR / "aperture_cycle_pareto_observables.csv"
            ),
            "signature_boundary_spine_aperture_cycle_pareto_frontier_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_cycle_pareto_frontier_tables.npz"
            ),
            "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "typed-boundary costs for the 10 already ranked x2-rooted aperture cycles",
                "which zero-overhead cycles require mixed x2/x5 first contacts",
                "which cycles preserve or abandon the certified x1 tail",
                "the finite Pareto frontier under the stated geometry/typed cost vector",
            ],
            "does_not_certify_because_not_required": [
                "optimality among carrier cycles longer than four edges",
                "disambiguation of mixed x2/x5 contacts into atom-level x2-only data",
                "new aperture routes outside the ranked comparable class",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Drill into the zero-overhead mixed cycles at atom level: certify "
            "whether mixed x2/x5 first contacts on edges 39 and 41 can be "
            "resolved to pure x2 witnesses, or prove that the ambiguity is "
            "intrinsic to this carrier-mask quotient."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_pareto_frontier_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified ranking, x2-detour, clean-detour, and typed-corridor artifacts",
            "annotate each ranked candidate with clean or mixed first x2 contact",
            "compute typed-tail abandonment and typed-boundary cost",
            "compute finite Pareto nondomination over geometry and typed-boundary costs",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_cycle_pareto_frontier": pareto_frontier,
        "aperture_cycle_pareto_candidates_csv": csv_text(
            PARETO_CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_cycle_pareto_classes_csv": csv_text(
            PARETO_CLASS_COLUMNS,
            class_rows,
        ),
        "aperture_cycle_pareto_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "class_table": class_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier.json",
        payloads["signature_boundary_spine_aperture_cycle_pareto_frontier"],
    )
    (OUT_DIR / "aperture_cycle_pareto_candidates.csv").write_text(
        payloads["aperture_cycle_pareto_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cycle_pareto_classes.csv").write_text(
        payloads["aperture_cycle_pareto_classes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_cycle_pareto_observables.csv").write_text(
        payloads["aperture_cycle_pareto_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier_tables.npz",
        candidate_table=payloads["candidate_table"],
        class_table=payloads["class_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate"
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
                "pareto_candidate_ids": witness["pareto_candidate_ids"],
                "dominated_candidate_ids": witness["dominated_candidate_ids"],
                "selected_candidate": witness["selected_candidate"],
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
