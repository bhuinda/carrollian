from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        OUT_DIR as CYCLE_RANKING_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
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
        OUT_DIR as CYCLE_RANKING_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_cycle_pareto"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CYCLE_RANKING_REPORT = CYCLE_RANKING_DIR / "report.json"
CYCLE_RANKING_JSON = (
    CYCLE_RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking.json"
)
CYCLE_RANKING_CANDIDATES = CYCLE_RANKING_DIR / "aperture_cycle_ranked_candidates.csv"
CYCLE_RANKING_TABLES = (
    CYCLE_RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking_tables.npz"
)
CYCLE_RANKING_CERTIFICATE = (
    CYCLE_RANKING_DIR / "signature_boundary_spine_aperture_cycle_ranking_certificate.json"
)

X2_DETOUR_REPORT = X2_DETOUR_DIR / "report.json"
X2_DETOUR_EDGES = X2_DETOUR_DIR / "x2_detour_edges.csv"
X2_DETOUR_TABLES = X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_tables.npz"
X2_DETOUR_CERTIFICATE = X2_DETOUR_DIR / "signature_boundary_spine_x2_detour_fan_certificate.json"

CLEAN_DETOUR_REPORT = CLEAN_DETOUR_DIR / "report.json"
CLEAN_DETOUR_JSON = (
    CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice.json"
)
CLEAN_DETOUR_TABLES = (
    CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice_tables.npz"
)
CLEAN_DETOUR_CERTIFICATE = (
    CLEAN_DETOUR_DIR / "signature_boundary_spine_x2_clean_detour_choice_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_cycle_pareto.py"
)

SELECTED_CYCLE_EDGE_IDS = [14, 11, 33, 43]
SELECTED_CYCLE_SYMBOLS = [2, 1, 4, 5]
GEODESIC_MIXED_CLASS = 0
CLEAN_X1_CLASS = 1
MIXED_X1_CLASS = 2
CLEAN_X0_CLASS = 3
MIXED_X0_CLASS = 4

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
    "geodesic_equivalent_flag",
    "clean_single_x2_first_contact_flag",
    "mixed_x2_x5_first_contact_flag",
    "x1_tail_preserving_flag",
    "x1_tail_abandonment_flag",
    "x0_tail_flag",
    "typed_boundary_cost",
    "pareto_class_code",
    "pareto_frontier_flag",
    "dominated_flag",
    "selected_tail_cycle_flag",
]

PARETO_CLASS_COLUMNS = [
    "pareto_class_code",
    "representative_candidate_id",
    "candidate_count",
    "pareto_frontier_flag",
    "geodesic_equivalent_flag",
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
    "geodesic_mixed_candidate_count": 3,
    "geodesic_mixed_pareto_count": 4,
    "clean_x1_candidate_count": 5,
    "clean_x1_pareto_count": 6,
    "dominated_candidate_count": 7,
    "mixed_x1_dominated_count": 8,
    "x0_tail_dominated_count": 9,
    "min_typed_boundary_cost": 10,
    "min_trace_detour_overhead": 11,
    "selected_tail_cycle_pareto_flag": 12,
    "selected_tail_cycle_typed_cost": 13,
}


def pareto_vector(row: dict[str, int]) -> tuple[int, int, int, int, int]:
    return (
        int(row["trace_detour_overhead"]),
        int(row["typed_boundary_cost"]),
        int(row["signature_valley_depth"]),
        int(row["metric_gromov_delta_twice"]),
        int(row["trace_signature_total_variation"]),
    )


def dominates(left: dict[str, int], right: dict[str, int]) -> bool:
    left_vector = pareto_vector(left)
    right_vector = pareto_vector(right)
    return all(a <= b for a, b in zip(left_vector, right_vector)) and any(
        a < b for a, b in zip(left_vector, right_vector)
    )


def class_code(row: dict[str, int]) -> int:
    if int(row["geodesic_equivalent_flag"]) == 1:
        return GEODESIC_MIXED_CLASS
    if int(row["clean_single_x2_first_contact_flag"]) == 1 and int(
        row["x1_tail_preserving_flag"]
    ) == 1:
        return CLEAN_X1_CLASS
    if int(row["mixed_x2_x5_first_contact_flag"]) == 1 and int(
        row["x1_tail_preserving_flag"]
    ) == 1:
        return MIXED_X1_CLASS
    if int(row["clean_single_x2_first_contact_flag"]) == 1 and int(
        row["x0_tail_flag"]
    ) == 1:
        return CLEAN_X0_CLASS
    return MIXED_X0_CLASS


def build_payloads() -> dict[str, Any]:
    ranking_report = load_json(CYCLE_RANKING_REPORT)
    ranking = load_json(CYCLE_RANKING_JSON)
    ranking_certificate = load_json(CYCLE_RANKING_CERTIFICATE)
    detour_report = load_json(X2_DETOUR_REPORT)
    detour_certificate = load_json(X2_DETOUR_CERTIFICATE)
    clean_report = load_json(CLEAN_DETOUR_REPORT)
    clean_choice = load_json(CLEAN_DETOUR_JSON)
    clean_certificate = load_json(CLEAN_DETOUR_CERTIFICATE)

    ranking_tables = np.load(CYCLE_RANKING_TABLES, allow_pickle=False)
    detour_tables = np.load(X2_DETOUR_TABLES, allow_pickle=False)
    clean_tables = np.load(CLEAN_DETOUR_TABLES, allow_pickle=False)
    ranking_candidate_table = np.asarray(ranking_tables["candidate_table"], dtype=np.int64)
    detour_edge_table = np.asarray(detour_tables["edge_table"], dtype=np.int64)
    clean_choice_table = np.asarray(clean_tables["return_choice_table"], dtype=np.int64)

    ranking_rows = read_int_csv(CYCLE_RANKING_CANDIDATES)
    detour_edges = {
        int(row["cell_edge_id"]): row for row in read_int_csv(X2_DETOUR_EDGES)
    }

    pareto_rows: list[dict[str, int]] = []
    for row in ranking_rows:
        first_edge_id = int(row["cell_edge_0_id"])
        detour_edge = detour_edges[first_edge_id]
        clean_x2 = int(detour_edge["single_x2_flag"])
        mixed_x2_x5 = int(detour_edge["mixed_x2_x5_flag"])
        x1_tail = int(row["x1_tail_preserving_flag"])
        x1_abandonment = 1 - x1_tail
        pareto_row = {
            "candidate_id": int(row["candidate_id"]),
            "rank_order": int(row["rank_order"]),
            "cell_edge_0_id": first_edge_id,
            "cell_edge_1_id": int(row["cell_edge_1_id"]),
            "cell_edge_2_id": int(row["cell_edge_2_id"]),
            "cell_edge_3_id": int(row["cell_edge_3_id"]),
            "symbol_0_id": int(row["symbol_0_id"]),
            "symbol_1_id": int(row["symbol_1_id"]),
            "symbol_2_id": int(row["symbol_2_id"]),
            "symbol_3_id": int(row["symbol_3_id"]),
            "trace_detour_overhead": int(row["trace_detour_overhead"]),
            "signature_valley_depth": int(row["signature_valley_depth"]),
            "metric_gromov_delta_twice": int(row["metric_gromov_delta_twice"]),
            "trace_signature_total_variation": int(
                row["trace_signature_total_variation"]
            ),
            "geodesic_equivalent_flag": int(row["geodesic_equivalent_flag"]),
            "clean_single_x2_first_contact_flag": clean_x2,
            "mixed_x2_x5_first_contact_flag": mixed_x2_x5,
            "x1_tail_preserving_flag": x1_tail,
            "x1_tail_abandonment_flag": x1_abandonment,
            "x0_tail_flag": int(row["x0_tail_flag"]),
            "typed_boundary_cost": mixed_x2_x5 + x1_abandonment,
            "pareto_class_code": 0,
            "pareto_frontier_flag": 0,
            "dominated_flag": 0,
            "selected_tail_cycle_flag": int(row["selected_tail_cycle_flag"]),
        }
        pareto_row["pareto_class_code"] = class_code(pareto_row)
        pareto_rows.append(pareto_row)

    for row in pareto_rows:
        row["dominated_flag"] = int(
            any(
                other["candidate_id"] != row["candidate_id"]
                and dominates(other, row)
                for other in pareto_rows
            )
        )
        row["pareto_frontier_flag"] = 1 - int(row["dominated_flag"])

    class_groups: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in pareto_rows:
        class_groups[int(row["pareto_class_code"])].append(row)

    class_rows: list[dict[str, int]] = []
    for code in sorted(class_groups):
        rows = class_groups[code]
        representative = sorted(rows, key=lambda item: int(item["rank_order"]))[0]
        class_rows.append(
            {
                "pareto_class_code": code,
                "representative_candidate_id": int(representative["candidate_id"]),
                "candidate_count": len(rows),
                "pareto_frontier_flag": int(
                    any(int(row["pareto_frontier_flag"]) == 1 for row in rows)
                ),
                "geodesic_equivalent_flag": int(
                    any(int(row["geodesic_equivalent_flag"]) == 1 for row in rows)
                ),
                "clean_single_x2_first_contact_flag": int(
                    any(
                        int(row["clean_single_x2_first_contact_flag"]) == 1
                        for row in rows
                    )
                ),
                "mixed_x2_x5_first_contact_flag": int(
                    any(int(row["mixed_x2_x5_first_contact_flag"]) == 1 for row in rows)
                ),
                "x1_tail_preserving_flag": int(
                    any(int(row["x1_tail_preserving_flag"]) == 1 for row in rows)
                ),
                "x0_tail_flag": int(any(int(row["x0_tail_flag"]) == 1 for row in rows)),
                "typed_boundary_cost": min(
                    int(row["typed_boundary_cost"]) for row in rows
                ),
                "min_rank_order": min(int(row["rank_order"]) for row in rows),
                "min_trace_detour_overhead": min(
                    int(row["trace_detour_overhead"]) for row in rows
                ),
                "min_signature_valley_depth": min(
                    int(row["signature_valley_depth"]) for row in rows
                ),
                "min_metric_gromov_delta_twice": min(
                    int(row["metric_gromov_delta_twice"]) for row in rows
                ),
                "min_trace_signature_total_variation": min(
                    int(row["trace_signature_total_variation"]) for row in rows
                ),
            }
        )

    selected_rows = [
        row for row in pareto_rows if int(row["selected_tail_cycle_flag"]) == 1
    ]
    if len(selected_rows) != 1:
        raise AssertionError("selected tail cycle should be unique")
    selected = selected_rows[0]

    observable_values = {
        "candidate_count": len(pareto_rows),
        "pareto_candidate_count": sum(
            int(row["pareto_frontier_flag"]) for row in pareto_rows
        ),
        "pareto_class_count": sum(
            int(row["pareto_frontier_flag"]) for row in class_rows
        ),
        "geodesic_mixed_candidate_count": len(
            class_groups.get(GEODESIC_MIXED_CLASS, [])
        ),
        "geodesic_mixed_pareto_count": sum(
            int(row["pareto_frontier_flag"])
            for row in class_groups.get(GEODESIC_MIXED_CLASS, [])
        ),
        "clean_x1_candidate_count": len(class_groups.get(CLEAN_X1_CLASS, [])),
        "clean_x1_pareto_count": sum(
            int(row["pareto_frontier_flag"])
            for row in class_groups.get(CLEAN_X1_CLASS, [])
        ),
        "dominated_candidate_count": sum(int(row["dominated_flag"]) for row in pareto_rows),
        "mixed_x1_dominated_count": sum(
            int(row["dominated_flag"])
            for row in class_groups.get(MIXED_X1_CLASS, [])
        ),
        "x0_tail_dominated_count": sum(
            int(row["dominated_flag"])
            for row in [
                *class_groups.get(CLEAN_X0_CLASS, []),
                *class_groups.get(MIXED_X0_CLASS, []),
            ]
        ),
        "min_typed_boundary_cost": min(int(row["typed_boundary_cost"]) for row in pareto_rows),
        "min_trace_detour_overhead": min(
            int(row["trace_detour_overhead"]) for row in pareto_rows
        ),
        "selected_tail_cycle_pareto_flag": int(selected["pareto_frontier_flag"]),
        "selected_tail_cycle_typed_cost": int(selected["typed_boundary_cost"]),
    }
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": code,
            "value_x1e12": int(observable_values[name]),
            "aux_id": 0,
        }
        for index, (name, code) in enumerate(
            sorted(OBSERVABLE_CODES.items(), key=lambda item: item[1])
        )
    ]

    candidate_table = table_from_rows(PARETO_CANDIDATE_COLUMNS, pareto_rows)
    class_table = table_from_rows(PARETO_CLASS_COLUMNS, class_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "cycle_ranking_report_certified": ranking_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_CERTIFIED",
        "cycle_ranking_certificate_certified": ranking_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_RANKING_CERTIFIED",
        "x2_detour_report_certified": detour_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "x2_detour_certificate_certified": detour_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_DETOUR_FAN_CERTIFIED",
        "clean_detour_report_certified": clean_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_CERTIFIED",
        "clean_detour_certificate_certified": clean_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_X2_CLEAN_DETOUR_CHOICE_CERTIFIED",
        "cycle_ranking_schema_available": ranking.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_cycle_ranking@1",
        "clean_detour_schema_available": clean_choice.get("schema")
        == "c985.d20_signature_boundary_spine_x2_clean_detour_choice@1",
        "cycle_ranking_candidate_table_shape_is_10_by_34": tuple(
            ranking_candidate_table.shape
        )
        == (10, 34),
        "x2_detour_edge_table_shape_is_13_by_15": tuple(detour_edge_table.shape)
        == (13, len(DETOUR_EDGE_COLUMNS)),
        "clean_choice_table_shape_is_2_by_23": tuple(clean_choice_table.shape)
        == (2, 23),
        "all_first_edges_have_x2_contact_audit": all(
            int(row["cell_edge_0_id"]) in detour_edges for row in pareto_rows
        ),
        "candidate_count_is_10": len(pareto_rows) == 10,
        "pareto_candidate_count_is_7": observable_values["pareto_candidate_count"]
        == 7,
        "pareto_class_count_is_2": observable_values["pareto_class_count"] == 2,
        "geodesic_mixed_candidate_count_is_6": observable_values[
            "geodesic_mixed_candidate_count"
        ]
        == 6,
        "all_geodesic_cycles_are_mixed_x2_x5": all(
            int(row["mixed_x2_x5_first_contact_flag"]) == 1
            for row in class_groups[GEODESIC_MIXED_CLASS]
        ),
        "all_geodesic_cycles_abandon_x1_tail": all(
            int(row["x1_tail_abandonment_flag"]) == 1
            for row in class_groups[GEODESIC_MIXED_CLASS]
        ),
        "clean_x1_candidate_count_is_1": observable_values[
            "clean_x1_candidate_count"
        ]
        == 1,
        "clean_x1_candidate_is_selected": int(
            class_groups[CLEAN_X1_CLASS][0]["selected_tail_cycle_flag"]
        )
        == 1,
        "selected_tail_cycle_is_pareto": int(selected["pareto_frontier_flag"]) == 1,
        "selected_tail_cycle_typed_cost_is_zero": int(selected["typed_boundary_cost"])
        == 0,
        "selected_tail_cycle_edges_match_prior": [
            int(selected[f"cell_edge_{index}_id"]) for index in range(4)
        ]
        == SELECTED_CYCLE_EDGE_IDS,
        "selected_tail_cycle_symbols_match_prior": [
            int(selected[f"symbol_{index}_id"]) for index in range(4)
        ]
        == SELECTED_CYCLE_SYMBOLS,
        "dominated_candidate_count_is_3": observable_values[
            "dominated_candidate_count"
        ]
        == 3,
        "mixed_x1_candidate_is_dominated": observable_values[
            "mixed_x1_dominated_count"
        ]
        == 1,
        "x0_tail_candidates_are_dominated": observable_values[
            "x0_tail_dominated_count"
        ]
        == 2,
        "pareto_class_codes_are_expected": [int(row["pareto_class_code"]) for row in class_rows]
        == [0, 1, 2, 3, 4],
        "candidate_table_shape_is_10_by_25": tuple(candidate_table.shape)
        == (10, len(PARETO_CANDIDATE_COLUMNS)),
        "class_table_shape_is_5_by_15": tuple(class_table.shape)
        == (5, len(PARETO_CLASS_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    frontier_rows = [
        row for row in pareto_rows if int(row["pareto_frontier_flag"]) == 1
    ]
    witness = {
        "pareto_frontier_candidate_ids": [
            int(row["candidate_id"]) for row in frontier_rows
        ],
        "pareto_frontier_class_codes": [
            int(row["pareto_class_code"])
            for row in class_rows
            if int(row["pareto_frontier_flag"]) == 1
        ],
        "geodesic_mixed_candidate_ids": [
            int(row["candidate_id"]) for row in class_groups[GEODESIC_MIXED_CLASS]
        ],
        "clean_x1_candidate_id": int(class_groups[CLEAN_X1_CLASS][0]["candidate_id"]),
        "selected_tail_cycle_id": int(selected["candidate_id"]),
        "selected_tail_cycle_typed_boundary_cost": int(selected["typed_boundary_cost"]),
        "selected_tail_cycle_vector": list(pareto_vector(selected)),
        "geodesic_mixed_vector": list(pareto_vector(class_groups[GEODESIC_MIXED_CLASS][0])),
        "dominated_candidate_ids": [
            int(row["candidate_id"]) for row in pareto_rows if int(row["dominated_flag"]) == 1
        ],
        "ranking_dimensions": [
            "trace_detour_overhead",
            "typed_boundary_cost",
            "signature_valley_depth",
            "metric_gromov_delta_twice",
            "trace_signature_total_variation",
        ],
        "candidate_table_sha256": sha_array(candidate_table),
        "class_table_sha256": sha_array(class_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    pareto = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_pareto@1",
        "object": "d20",
        "pareto_rule": {
            "geometric_cost": "trace overhead, signature valley depth, Gromov delta, and signature variation",
            "typed_boundary_cost": "mixed x2/x5 first contact plus abandoning the certified x1 tail",
            "frontier": "nondominated candidates under geometry and typed-boundary cost",
        },
        "candidate_audit": pareto_rows,
        "pareto_classes": class_rows,
        "summary": {
            "candidate_count": len(pareto_rows),
            "pareto_candidate_count": observable_values["pareto_candidate_count"],
            "pareto_class_count": observable_values["pareto_class_count"],
            "selected_tail_cycle_typed_boundary_cost": int(
                selected["typed_boundary_cost"]
            ),
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_cycle_pareto_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "all six zero-overhead cycles require a mixed x2/x5 first contact and abandon the certified x1 tail",
            "the selected clean x2,x1 cycle is the unique typed-cost-zero candidate and remains Pareto-optimal",
            "three candidates are dominated: the mixed x1 cycle and the two x0-tail cycles",
            "the finite frontier has two classes: geodesic-optimal mixed cycles and typed-tail-optimal clean x1 cycle",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_pareto@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The comparable aperture-cycle family has a two-class Pareto "
            "frontier: six geodesic-optimal cycles with mixed x2/x5 first "
            "contacts and abandoned x1 tail, and one typed-tail-optimal clean "
            "x2,x1 cycle with overhead 3."
        ),
        "stage_protocol": {
            "draft": "audit ranked cycles for mixed first x2 contacts and x1-tail preservation",
            "witness": "materialize per-candidate typed cost, dominance, and class summaries",
            "coherence": "compute the nondominated frontier over geometry and typed-boundary costs",
            "closure": "certify the finite Pareto frontier without claiming longer-cycle optimality",
            "emit": "emit aperture-cycle Pareto JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "cycle_ranking_report": input_entry(
                CYCLE_RANKING_REPORT,
                {
                    "status": ranking_report.get("status"),
                    "certificate_sha256": ranking_report.get("certificate_sha256"),
                },
            ),
            "cycle_ranking": input_entry(CYCLE_RANKING_JSON),
            "cycle_ranking_candidates": input_entry(CYCLE_RANKING_CANDIDATES),
            "cycle_ranking_tables": input_entry(CYCLE_RANKING_TABLES),
            "cycle_ranking_certificate": input_entry(CYCLE_RANKING_CERTIFICATE),
            "x2_detour_report": input_entry(
                X2_DETOUR_REPORT,
                {
                    "status": detour_report.get("status"),
                    "certificate_sha256": detour_report.get("certificate_sha256"),
                },
            ),
            "x2_detour_edges": input_entry(X2_DETOUR_EDGES),
            "x2_detour_tables": input_entry(X2_DETOUR_TABLES),
            "x2_detour_certificate": input_entry(X2_DETOUR_CERTIFICATE),
            "clean_detour_report": input_entry(
                CLEAN_DETOUR_REPORT,
                {
                    "status": clean_report.get("status"),
                    "certificate_sha256": clean_report.get("certificate_sha256"),
                },
            ),
            "clean_detour": input_entry(CLEAN_DETOUR_JSON),
            "clean_detour_tables": input_entry(CLEAN_DETOUR_TABLES),
            "clean_detour_certificate": input_entry(CLEAN_DETOUR_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_cycle_pareto": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto.json"
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
            "signature_boundary_spine_aperture_cycle_pareto_tables": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_tables.npz"
            ),
            "signature_boundary_spine_aperture_cycle_pareto_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "mixed x2/x5 first-contact cost for every comparable cycle",
                "x1-tail abandonment cost for every comparable cycle",
                "the nondominated Pareto frontier under geometry and typed-boundary costs",
                "that geodesic optimality and clean x1-tail preservation are incompatible within this finite class",
            ],
            "does_not_certify_because_not_required": [
                "cycles longer than four carrier edges",
                "alternate typed-cost functions not based on mixed contact and x1-tail preservation",
                "global optimality outside the certified comparable cycle class",
                "new categorical F-symbols, braiding, pivotality, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Search the next shell of five-edge origin-returning cycles to see "
            "whether any cycle achieves both clean x2,x1-tail preservation and "
            "lower aperture overhead than 3, or certify the radius-5 obstruction."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_cycle_pareto_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified aperture-cycle ranking, x2-detour, and clean-detour artifacts",
            "audit first x2 contact as clean single x2 or mixed x2/x5",
            "score each candidate by mixed-contact and x1-tail abandonment cost",
            "compute nondominated frontier against trace overhead, valley depth, delta, and signature variation",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_cycle_pareto": pareto,
        "aperture_cycle_pareto_candidates_csv": csv_text(
            PARETO_CANDIDATE_COLUMNS,
            pareto_rows,
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
        "signature_boundary_spine_aperture_cycle_pareto_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto.json",
        payloads["signature_boundary_spine_aperture_cycle_pareto"],
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
        OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_tables.npz",
        candidate_table=payloads["candidate_table"],
        class_table=payloads["class_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_cycle_pareto_certificate.json",
        payloads["signature_boundary_spine_aperture_cycle_pareto_certificate"],
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
                "pareto_frontier_candidate_ids": witness[
                    "pareto_frontier_candidate_ids"
                ],
                "pareto_frontier_class_codes": witness["pareto_frontier_class_codes"],
                "selected_tail_cycle_vector": witness["selected_tail_cycle_vector"],
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
