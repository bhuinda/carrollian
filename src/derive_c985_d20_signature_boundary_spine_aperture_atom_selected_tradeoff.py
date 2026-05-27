from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement import (
        OUT_DIR as ATOM_SELECTOR_DIR,
        SELECTOR_CANDIDATE_COLUMNS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier import (
        OUT_DIR as PARETO_DIR,
        PARETO_CANDIDATE_COLUMNS,
        dominates,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms import (
        CANDIDATE_RESOLUTION_COLUMNS as MIXED_CANDIDATE_COLUMNS,
        OUT_DIR as MIXED_CONTACT_DIR,
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
    from derive_c985_d20_signature_boundary_spine_aperture_atom_selector_refinement import (
        OUT_DIR as ATOM_SELECTOR_DIR,
        SELECTOR_CANDIDATE_COLUMNS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_pareto_frontier import (
        OUT_DIR as PARETO_DIR,
        PARETO_CANDIDATE_COLUMNS,
        dominates,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_mixed_contact_atoms import (
        CANDIDATE_RESOLUTION_COLUMNS as MIXED_CANDIDATE_COLUMNS,
        OUT_DIR as MIXED_CONTACT_DIR,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTED_TRADEOFF_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

ATOM_SELECTOR_REPORT = ATOM_SELECTOR_DIR / "report.json"
ATOM_SELECTOR_JSON = (
    ATOM_SELECTOR_DIR / "signature_boundary_spine_aperture_atom_selector_refinement.json"
)
ATOM_SELECTOR_CANDIDATES = ATOM_SELECTOR_DIR / "aperture_atom_selector_candidates.csv"
ATOM_SELECTOR_STEPS = ATOM_SELECTOR_DIR / "aperture_atom_selector_steps.csv"
ATOM_SELECTOR_TABLES = (
    ATOM_SELECTOR_DIR
    / "signature_boundary_spine_aperture_atom_selector_refinement_tables.npz"
)
ATOM_SELECTOR_CERTIFICATE = (
    ATOM_SELECTOR_DIR
    / "signature_boundary_spine_aperture_atom_selector_refinement_certificate.json"
)

MIXED_CONTACT_REPORT = MIXED_CONTACT_DIR / "report.json"
MIXED_CONTACT_CANDIDATES = MIXED_CONTACT_DIR / "aperture_candidate_atom_resolution.csv"
MIXED_CONTACT_EDGES = MIXED_CONTACT_DIR / "aperture_first_contact_edge_resolution.csv"
MIXED_CONTACT_TABLES = (
    MIXED_CONTACT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_tables.npz"
)
MIXED_CONTACT_CERTIFICATE = (
    MIXED_CONTACT_DIR / "signature_boundary_spine_aperture_mixed_contact_atoms_certificate.json"
)

PARETO_REPORT = PARETO_DIR / "report.json"
PARETO_JSON = PARETO_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier.json"
PARETO_CANDIDATES = PARETO_DIR / "aperture_cycle_pareto_candidates.csv"
PARETO_CLASSES = PARETO_DIR / "aperture_cycle_pareto_classes.csv"
PARETO_TABLES = PARETO_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier_tables.npz"
PARETO_CERTIFICATE = (
    PARETO_DIR / "signature_boundary_spine_aperture_cycle_pareto_frontier_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff.py"
)

X2_ATOM_ID = 7
ZERO_OVERHEAD_CANDIDATE_IDS = [0, 1, 2, 3, 4, 5]
SELECTED_CLEAN_X1_CANDIDATE_ID = 6
MIXED_X1_CANDIDATE_ID = 7
ATOM_SELECTED_FRONTIER_IDS = [0, 1, 2, 3, 4, 5, 6, 7]
ATOM_SELECTED_DOMINATED_IDS = [8, 9]

TRADEOFF_METRIC_COLUMNS = [
    "trace_detour_overhead",
    "atom_selected_tail_cost",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
]

TRADEOFF_CANDIDATE_COLUMNS = [
    "candidate_id",
    "rank_order",
    "cell_edge_0_id",
    "trace_detour_overhead",
    "signature_valley_depth",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "x1_tail_preserving_flag",
    "x0_tail_flag",
    "typed_tail_abandonment_flag",
    "old_typed_boundary_cost",
    "carrier_mask_pure_x2_first_contact_flag",
    "carrier_mask_mixed_x2_x5_first_contact_flag",
    "atom_level_x2_witness_flag",
    "selected_first_contact_atom_id",
    "selected_first_contact_symbol_id",
    "selected_first_contact_x5_leakage_flag",
    "unselected_x5_first_contact_cowitness_flag",
    "first_contact_selector_required_flag",
    "full_atom_selector_certified_flag",
    "atom_selected_tail_cost",
    "atom_cost_reduction",
    "geodesic_optimal_flag",
    "atom_selected_pareto_frontier_flag",
    "atom_selected_dominated_flag",
    "atom_selected_class_code",
]

TRADEOFF_CLASS_COLUMNS = [
    "atom_selected_class_code",
    "representative_candidate_id",
    "candidate_count",
    "frontier_class_flag",
    "geodesic_optimal_flag",
    "x1_tail_preserving_flag",
    "x0_tail_flag",
    "atom_selected_tail_cost",
    "min_trace_detour_overhead",
    "min_signature_valley_depth",
    "min_metric_gromov_delta_twice",
    "min_trace_signature_total_variation",
    "selector_required_count",
    "clean_carrier_first_contact_count",
    "selected_first_contact_x5_leakage_count",
    "full_atom_selector_certified_count",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "candidate_count": 0,
    "frontier_candidate_count": 1,
    "frontier_class_count": 2,
    "dominated_candidate_count": 3,
    "selected_first_contact_x5_leakage_count": 4,
    "zero_overhead_atom_tail_cost": 5,
    "clean_x1_atom_tail_cost": 6,
    "zero_overhead_atom_cost_zero_count": 7,
    "geodesic_frontier_candidate_count": 8,
    "x1_tail_frontier_candidate_count": 9,
    "atom_cost_reduction_positive_count": 10,
    "frontier_expanded_by_candidate_7_flag": 11,
    "x1_tail_obstruction_survives_flag": 12,
    "selected_leakage_collapses_mixed_penalty_flag": 13,
}

CLASS_NAMES = {
    0: "atom_selected_geodesic_tail_abandoned",
    1: "atom_selected_x1_tail",
    2: "atom_selected_x0_tail",
}


def tradeoff_dominates(left: dict[str, int], right: dict[str, int]) -> bool:
    left_values = [int(left[column]) for column in TRADEOFF_METRIC_COLUMNS]
    right_values = [int(right[column]) for column in TRADEOFF_METRIC_COLUMNS]
    return all(a <= b for a, b in zip(left_values, right_values)) and any(
        a < b for a, b in zip(left_values, right_values)
    )


def class_code(row: dict[str, int]) -> int:
    if int(row["geodesic_optimal_flag"]) == 1:
        return 0
    if int(row["x1_tail_preserving_flag"]) == 1:
        return 1
    if int(row["x0_tail_flag"]) == 1:
        return 2
    raise AssertionError(f"unclassified candidate {row['candidate_id']}")


def build_candidate_rows(
    pareto_rows: list[dict[str, int]],
    mixed_rows_by_id: dict[int, dict[str, int]],
    selector_rows_by_id: dict[int, dict[str, int]],
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for pareto_row in pareto_rows:
        candidate_id = int(pareto_row["candidate_id"])
        mixed_row = mixed_rows_by_id[candidate_id]
        selector_row = selector_rows_by_id.get(candidate_id)
        selected_atom_id = (
            int(selector_row["selected_atom_0_id"])
            if selector_row is not None
            else X2_ATOM_ID
        )
        selected_symbol_id = (
            int(selector_row["selected_symbol_0_id"])
            if selector_row is not None
            else 2
        )
        selected_leakage = (
            int(selector_row["first_contact_selected_x5_leakage_flag"])
            if selector_row is not None
            else 0
        )
        unselected_x5 = (
            int(selector_row["first_contact_x5_cowitness_flag"])
            if selector_row is not None
            else int(mixed_row["atom_x5_cowitness_flag"])
        )
        selector_required = (
            int(selector_row["atom_selector_required_flag"])
            if selector_row is not None
            else int(mixed_row["requires_atom_selector_flag"])
        )
        typed_tail_abandonment = int(pareto_row["typed_tail_abandonment_flag"])
        atom_tail_cost = typed_tail_abandonment + selected_leakage
        old_cost = int(pareto_row["typed_boundary_cost"])
        row = {
            "candidate_id": candidate_id,
            "rank_order": int(pareto_row["rank_order"]),
            "cell_edge_0_id": int(pareto_row["cell_edge_0_id"]),
            "trace_detour_overhead": int(pareto_row["trace_detour_overhead"]),
            "signature_valley_depth": int(pareto_row["signature_valley_depth"]),
            "metric_gromov_delta_twice": int(pareto_row["metric_gromov_delta_twice"]),
            "trace_signature_total_variation": int(
                pareto_row["trace_signature_total_variation"]
            ),
            "x1_tail_preserving_flag": int(pareto_row["x1_tail_preserving_flag"]),
            "x0_tail_flag": int(pareto_row["x0_tail_flag"]),
            "typed_tail_abandonment_flag": typed_tail_abandonment,
            "old_typed_boundary_cost": old_cost,
            "carrier_mask_pure_x2_first_contact_flag": int(
                pareto_row["clean_single_x2_first_contact_flag"]
            ),
            "carrier_mask_mixed_x2_x5_first_contact_flag": int(
                pareto_row["mixed_x2_x5_first_contact_flag"]
            ),
            "atom_level_x2_witness_flag": int(mixed_row["atom_level_x2_witness_flag"]),
            "selected_first_contact_atom_id": selected_atom_id,
            "selected_first_contact_symbol_id": selected_symbol_id,
            "selected_first_contact_x5_leakage_flag": selected_leakage,
            "unselected_x5_first_contact_cowitness_flag": unselected_x5,
            "first_contact_selector_required_flag": selector_required,
            "full_atom_selector_certified_flag": int(selector_row is not None),
            "atom_selected_tail_cost": atom_tail_cost,
            "atom_cost_reduction": old_cost - atom_tail_cost,
            "geodesic_optimal_flag": int(pareto_row["geodesic_optimal_flag"]),
            "atom_selected_pareto_frontier_flag": 0,
            "atom_selected_dominated_flag": 0,
            "atom_selected_class_code": -1,
        }
        rows.append(row)

    for row in rows:
        row["atom_selected_dominated_flag"] = int(
            any(
                tradeoff_dominates(other, row)
                for other in rows
                if int(other["candidate_id"]) != int(row["candidate_id"])
            )
        )
        row["atom_selected_pareto_frontier_flag"] = int(
            int(row["atom_selected_dominated_flag"]) == 0
        )
        row["atom_selected_class_code"] = class_code(row)
    return rows


def build_class_rows(candidate_rows: list[dict[str, int]]) -> list[dict[str, int]]:
    class_rows: list[dict[str, int]] = []
    for code in sorted(CLASS_NAMES):
        members = [
            row for row in candidate_rows if int(row["atom_selected_class_code"]) == code
        ]
        if not members:
            continue
        representative = min(members, key=lambda row: int(row["rank_order"]))
        class_rows.append(
            {
                "atom_selected_class_code": code,
                "representative_candidate_id": int(representative["candidate_id"]),
                "candidate_count": len(members),
                "frontier_class_flag": int(
                    any(
                        int(row["atom_selected_pareto_frontier_flag"]) == 1
                        for row in members
                    )
                ),
                "geodesic_optimal_flag": int(
                    any(int(row["geodesic_optimal_flag"]) == 1 for row in members)
                ),
                "x1_tail_preserving_flag": int(
                    any(int(row["x1_tail_preserving_flag"]) == 1 for row in members)
                ),
                "x0_tail_flag": int(any(int(row["x0_tail_flag"]) == 1 for row in members)),
                "atom_selected_tail_cost": min(
                    int(row["atom_selected_tail_cost"]) for row in members
                ),
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
                "selector_required_count": sum(
                    int(row["first_contact_selector_required_flag"]) for row in members
                ),
                "clean_carrier_first_contact_count": sum(
                    int(row["carrier_mask_pure_x2_first_contact_flag"])
                    for row in members
                ),
                "selected_first_contact_x5_leakage_count": sum(
                    int(row["selected_first_contact_x5_leakage_flag"])
                    for row in members
                ),
                "full_atom_selector_certified_count": sum(
                    int(row["full_atom_selector_certified_flag"]) for row in members
                ),
            }
        )
    return class_rows


def build_payloads() -> dict[str, Any]:
    atom_selector_report = load_json(ATOM_SELECTOR_REPORT)
    atom_selector = load_json(ATOM_SELECTOR_JSON)
    atom_selector_certificate = load_json(ATOM_SELECTOR_CERTIFICATE)
    mixed_report = load_json(MIXED_CONTACT_REPORT)
    mixed_certificate = load_json(MIXED_CONTACT_CERTIFICATE)
    pareto_report = load_json(PARETO_REPORT)
    pareto = load_json(PARETO_JSON)
    pareto_certificate = load_json(PARETO_CERTIFICATE)

    atom_selector_tables = np.load(ATOM_SELECTOR_TABLES, allow_pickle=False)
    mixed_tables = np.load(MIXED_CONTACT_TABLES, allow_pickle=False)
    pareto_tables = np.load(PARETO_TABLES, allow_pickle=False)
    atom_selector_candidate_table = np.asarray(
        atom_selector_tables["selector_candidate_table"],
        dtype=np.int64,
    )
    mixed_candidate_table = np.asarray(
        mixed_tables["candidate_resolution_table"],
        dtype=np.int64,
    )
    pareto_candidate_table = np.asarray(
        pareto_tables["candidate_table"],
        dtype=np.int64,
    )

    atom_selector_rows = read_int_csv(ATOM_SELECTOR_CANDIDATES)
    mixed_rows = read_int_csv(MIXED_CONTACT_CANDIDATES)
    pareto_rows = read_int_csv(PARETO_CANDIDATES)
    mixed_rows_by_id = {int(row["candidate_id"]): row for row in mixed_rows}
    selector_rows_by_id = {
        int(row["candidate_id"]): row for row in atom_selector_rows
    }

    candidate_rows = build_candidate_rows(
        pareto_rows,
        mixed_rows_by_id,
        selector_rows_by_id,
    )
    class_rows = build_class_rows(candidate_rows)
    frontier_rows = [
        row
        for row in candidate_rows
        if int(row["atom_selected_pareto_frontier_flag"]) == 1
    ]
    dominated_rows = [
        row for row in candidate_rows if int(row["atom_selected_dominated_flag"]) == 1
    ]
    zero_overhead_rows = [
        row for row in candidate_rows if int(row["geodesic_optimal_flag"]) == 1
    ]
    x1_frontier_rows = [
        row
        for row in frontier_rows
        if int(row["x1_tail_preserving_flag"]) == 1
    ]
    candidate_table = table_from_rows(TRADEOFF_CANDIDATE_COLUMNS, candidate_rows)
    class_table = table_from_rows(TRADEOFF_CLASS_COLUMNS, class_rows)

    observable_values = {
        "candidate_count": len(candidate_rows),
        "frontier_candidate_count": len(frontier_rows),
        "frontier_class_count": len(
            {
                int(row["atom_selected_class_code"])
                for row in frontier_rows
            }
        ),
        "dominated_candidate_count": len(dominated_rows),
        "selected_first_contact_x5_leakage_count": sum(
            int(row["selected_first_contact_x5_leakage_flag"])
            for row in candidate_rows
        ),
        "zero_overhead_atom_tail_cost": min(
            int(row["atom_selected_tail_cost"]) for row in zero_overhead_rows
        ),
        "clean_x1_atom_tail_cost": int(
            next(
                row
                for row in candidate_rows
                if int(row["candidate_id"]) == SELECTED_CLEAN_X1_CANDIDATE_ID
            )["atom_selected_tail_cost"]
        ),
        "zero_overhead_atom_cost_zero_count": len(
            [
                row
                for row in zero_overhead_rows
                if int(row["atom_selected_tail_cost"]) == 0
            ]
        ),
        "geodesic_frontier_candidate_count": len(
            [row for row in frontier_rows if int(row["geodesic_optimal_flag"]) == 1]
        ),
        "x1_tail_frontier_candidate_count": len(x1_frontier_rows),
        "atom_cost_reduction_positive_count": len(
            [row for row in candidate_rows if int(row["atom_cost_reduction"]) > 0]
        ),
        "frontier_expanded_by_candidate_7_flag": int(
            any(
                int(row["candidate_id"]) == MIXED_X1_CANDIDATE_ID
                for row in frontier_rows
            )
        ),
        "x1_tail_obstruction_survives_flag": int(
            all(int(row["atom_selected_tail_cost"]) > 0 for row in zero_overhead_rows)
        ),
        "selected_leakage_collapses_mixed_penalty_flag": int(
            all(
                int(row["selected_first_contact_x5_leakage_flag"]) == 0
                for row in candidate_rows
            )
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

    frontier_ids = [int(row["candidate_id"]) for row in frontier_rows]
    dominated_ids = [int(row["candidate_id"]) for row in dominated_rows]
    class_by_code = {int(row["atom_selected_class_code"]): row for row in class_rows}
    selected_clean_row = next(
        row
        for row in candidate_rows
        if int(row["candidate_id"]) == SELECTED_CLEAN_X1_CANDIDATE_ID
    )
    mixed_x1_row = next(
        row for row in candidate_rows if int(row["candidate_id"]) == MIXED_X1_CANDIDATE_ID
    )
    x0_rows = [
        row for row in candidate_rows if int(row["x0_tail_flag"]) == 1
    ]

    checks = {
        "atom_selector_report_certified": atom_selector_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTOR_REFINEMENT_CERTIFIED",
        "atom_selector_certificate_certified": atom_selector_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTOR_REFINEMENT_CERTIFIED",
        "mixed_contact_report_certified": mixed_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_MIXED_CONTACT_ATOMS_CERTIFIED",
        "mixed_contact_certificate_certified": mixed_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_MIXED_CONTACT_ATOMS_CERTIFIED",
        "pareto_report_certified": pareto_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_FRONTIER_CERTIFIED",
        "pareto_certificate_certified": pareto_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CYCLE_PARETO_FRONTIER_CERTIFIED",
        "atom_selector_schema_available": atom_selector.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_atom_selector_refinement@1",
        "pareto_schema_available": pareto.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_cycle_pareto_frontier@1",
        "atom_selector_candidate_table_shape_is_6_by_37": tuple(
            atom_selector_candidate_table.shape
        )
        == (6, len(SELECTOR_CANDIDATE_COLUMNS)),
        "mixed_candidate_table_shape_is_10_by_16": tuple(mixed_candidate_table.shape)
        == (10, len(MIXED_CANDIDATE_COLUMNS)),
        "pareto_candidate_table_shape_is_10_by_25": tuple(pareto_candidate_table.shape)
        == (10, len(PARETO_CANDIDATE_COLUMNS)),
        "all_candidates_select_x2_first_atom": all(
            int(row["selected_first_contact_atom_id"]) == X2_ATOM_ID
            and int(row["selected_first_contact_symbol_id"]) == 2
            for row in candidate_rows
        ),
        "selected_first_contact_leakage_is_zero": observable_values[
            "selected_first_contact_x5_leakage_count"
        ]
        == 0,
        "zero_overhead_cost_drops_from_2_to_1": [
            (
                int(row["old_typed_boundary_cost"]),
                int(row["atom_selected_tail_cost"]),
            )
            for row in zero_overhead_rows
        ]
        == [(2, 1)] * 6,
        "zero_overhead_cost_zero_count_is_0": observable_values[
            "zero_overhead_atom_cost_zero_count"
        ]
        == 0,
        "clean_x1_candidate_cost_is_0": int(
            selected_clean_row["atom_selected_tail_cost"]
        )
        == 0,
        "mixed_x1_candidate_7_enters_frontier": int(
            mixed_x1_row["atom_selected_pareto_frontier_flag"]
        )
        == 1
        and int(mixed_x1_row["atom_selected_tail_cost"]) == 0,
        "frontier_candidate_ids_are_0_through_7": frontier_ids
        == ATOM_SELECTED_FRONTIER_IDS,
        "dominated_candidate_ids_are_8_and_9": dominated_ids
        == ATOM_SELECTED_DOMINATED_IDS,
        "frontier_class_count_is_2": observable_values["frontier_class_count"] == 2,
        "x1_tail_obstruction_survives": observable_values[
            "x1_tail_obstruction_survives_flag"
        ]
        == 1,
        "geodesic_class_has_cost_1_and_zero_overhead": int(
            class_by_code[0]["atom_selected_tail_cost"]
        )
        == 1
        and int(class_by_code[0]["min_trace_detour_overhead"]) == 0,
        "x1_tail_class_has_cost_0_and_overhead_3": int(
            class_by_code[1]["atom_selected_tail_cost"]
        )
        == 0
        and int(class_by_code[1]["min_trace_detour_overhead"]) == 3,
        "x0_tail_class_is_dominated": int(class_by_code[2]["frontier_class_flag"]) == 0,
        "x0_tail_candidates_are_dominated": all(
            int(row["atom_selected_dominated_flag"]) == 1 for row in x0_rows
        ),
        "candidate_table_shape_is_10_by_26": tuple(candidate_table.shape)
        == (10, len(TRADEOFF_CANDIDATE_COLUMNS)),
        "class_table_shape_is_3_by_16": tuple(class_table.shape)
        == (3, len(TRADEOFF_CLASS_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "frontier_candidate_ids": frontier_ids,
        "dominated_candidate_ids": dominated_ids,
        "frontier_classes": [
            {
                "class_code": int(row["atom_selected_class_code"]),
                "class_name": CLASS_NAMES[int(row["atom_selected_class_code"])],
                "representative_candidate_id": int(row["representative_candidate_id"]),
                "candidate_count": int(row["candidate_count"]),
                "frontier_class": bool(row["frontier_class_flag"]),
                "atom_selected_tail_cost": int(row["atom_selected_tail_cost"]),
                "trace_detour_overhead": int(row["min_trace_detour_overhead"]),
                "signature_valley_depth": int(row["min_signature_valley_depth"]),
                "metric_gromov_delta": float(
                    int(row["min_metric_gromov_delta_twice"]) / 2.0
                ),
                "trace_signature_total_variation": int(
                    row["min_trace_signature_total_variation"]
                ),
                "selector_required_count": int(row["selector_required_count"]),
                "clean_carrier_first_contact_count": int(
                    row["clean_carrier_first_contact_count"]
                ),
            }
            for row in class_rows
        ],
        "cost_rule": (
            "atom_selected_tail_cost = selected_first_contact_x5_leakage_flag "
            "+ typed_tail_abandonment_flag"
        ),
        "zero_overhead_cost_transition": {
            "old_typed_boundary_cost": 2,
            "atom_selected_tail_cost": 1,
            "reason": "selected first-contact x5 leakage is zero, but x1 tail is still abandoned",
        },
        "x1_tail_class": {
            "candidate_ids": [
                int(row["candidate_id"])
                for row in candidate_rows
                if int(row["x1_tail_preserving_flag"]) == 1
            ],
            "atom_selected_tail_cost": 0,
            "trace_detour_overhead": 3,
            "signature_valley_depth": 37,
        },
        "candidate_table_sha256": sha_array(candidate_table),
        "class_table_sha256": sha_array(class_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    tradeoff = {
        "schema": "c985.d20_signature_boundary_spine_aperture_atom_selected_tradeoff@1",
        "object": "d20",
        "cost_model": {
            "old_boundary_cost": "mixed carrier-mask first contact + x1-tail abandonment",
            "atom_selected_cost": (
                "selected first-contact x5 leakage + x1-tail abandonment"
            ),
            "dominance_rule": (
                "lower is better for trace overhead, atom-selected tail cost, "
                "signature valley depth, Gromov delta twice, and signature variation"
            ),
        },
        "class_names": {str(key): value for key, value in CLASS_NAMES.items()},
        "frontier_candidate_ids": frontier_ids,
        "dominated_candidate_ids": dominated_ids,
        "summary": {
            "frontier_class_count": observable_values["frontier_class_count"],
            "x1_tail_obstruction_survives": True,
            "selected_leakage_collapses_mixed_penalty": True,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_atom_selected_tradeoff_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTED_TRADEOFF_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "atom selection removes the selected first-contact x5 leakage penalty from every ranked candidate",
            "the zero-overhead class drops from typed cost 2 to atom-selected tail cost 1",
            "the zero-overhead class still abandons the certified x1 tail, so it does not collapse onto the cost-zero x1-tail class",
            "candidate 7 joins the cost-zero x1-tail frontier at atom level, while x0-tail candidates 8 and 9 remain dominated",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selected_tradeoff@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "After charging only selected first-contact x5 leakage, the "
            "mixed-contact penalty collapses but the x1-tail obstruction "
            "survives. The atom-selected frontier has a zero-overhead class "
            "with tail cost 1 and an x1-tail class with tail cost 0 and "
            "overhead 3."
        ),
        "stage_protocol": {
            "draft": "replace carrier-mask mixed-contact cost by selected first-contact leakage cost",
            "witness": "materialize atom-selected costs for all ranked aperture candidates",
            "coherence": "compute Pareto nondomination under geometry plus atom-selected tail cost",
            "closure": "certify that first-contact ambiguity collapses but x1-tail preservation remains a separate obstruction",
            "emit": "emit atom-selected tradeoff JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "atom_selector_report": input_entry(
                ATOM_SELECTOR_REPORT,
                {
                    "status": atom_selector_report.get("status"),
                    "certificate_sha256": atom_selector_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "atom_selector_json": input_entry(ATOM_SELECTOR_JSON),
            "atom_selector_candidates": input_entry(ATOM_SELECTOR_CANDIDATES),
            "atom_selector_steps": input_entry(ATOM_SELECTOR_STEPS),
            "atom_selector_tables": input_entry(ATOM_SELECTOR_TABLES),
            "atom_selector_certificate": input_entry(ATOM_SELECTOR_CERTIFICATE),
            "mixed_contact_report": input_entry(
                MIXED_CONTACT_REPORT,
                {
                    "status": mixed_report.get("status"),
                    "certificate_sha256": mixed_report.get("certificate_sha256"),
                },
            ),
            "mixed_contact_candidates": input_entry(MIXED_CONTACT_CANDIDATES),
            "mixed_contact_edges": input_entry(MIXED_CONTACT_EDGES),
            "mixed_contact_tables": input_entry(MIXED_CONTACT_TABLES),
            "mixed_contact_certificate": input_entry(MIXED_CONTACT_CERTIFICATE),
            "pareto_report": input_entry(
                PARETO_REPORT,
                {
                    "status": pareto_report.get("status"),
                    "certificate_sha256": pareto_report.get("certificate_sha256"),
                },
            ),
            "pareto_json": input_entry(PARETO_JSON),
            "pareto_candidates": input_entry(PARETO_CANDIDATES),
            "pareto_classes": input_entry(PARETO_CLASSES),
            "pareto_tables": input_entry(PARETO_TABLES),
            "pareto_certificate": input_entry(PARETO_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_atom_selected_tradeoff": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_atom_selected_tradeoff.json"
            ),
            "aperture_atom_selected_tradeoff_candidates_csv": relpath(
                OUT_DIR / "aperture_atom_selected_tradeoff_candidates.csv"
            ),
            "aperture_atom_selected_tradeoff_classes_csv": relpath(
                OUT_DIR / "aperture_atom_selected_tradeoff_classes.csv"
            ),
            "aperture_atom_selected_tradeoff_observables_csv": relpath(
                OUT_DIR / "aperture_atom_selected_tradeoff_observables.csv"
            ),
            "signature_boundary_spine_aperture_atom_selected_tradeoff_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_atom_selected_tradeoff_tables.npz"
            ),
            "signature_boundary_spine_aperture_atom_selected_tradeoff_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_atom_selected_tradeoff_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the atom-selected tradeoff cost for all 10 ranked aperture candidates",
                "that selected first-contact x5 leakage is zero for the comparable class",
                "that the zero-overhead class remains tail-cost one because it abandons the x1 tail",
                "the atom-selected Pareto frontier and dominated x0-tail candidates",
            ],
            "does_not_certify_because_not_required": [
                "a carrier-mask pure x2 replacement for mixed edges 39 or 41",
                "a full atom selector for every non-geodesic candidate beyond first contact",
                "that x1-tail preservation can coexist with zero overhead in this comparable class",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Search for the missing hybrid: an atom-selected cycle that keeps "
            "the x1 tail while reducing the three-step carrier detour. Enumerate "
            "five- and six-edge atom-selected cycles rooted at carrier 12, with "
            "first selected atom x2 and explicit x1-tail preservation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_atom_selected_tradeoff_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified atom-selector, mixed-contact, and Pareto artifacts",
            "replace carrier-mask mixed-contact cost by selected first-contact leakage cost",
            "compute atom-selected tail cost for each ranked aperture candidate",
            "recompute finite Pareto nondomination under geometry and atom-selected tail cost",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_atom_selected_tradeoff": tradeoff,
        "aperture_atom_selected_tradeoff_candidates_csv": csv_text(
            TRADEOFF_CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_atom_selected_tradeoff_classes_csv": csv_text(
            TRADEOFF_CLASS_COLUMNS,
            class_rows,
        ),
        "aperture_atom_selected_tradeoff_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "class_table": class_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_atom_selected_tradeoff_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_atom_selected_tradeoff.json",
        payloads["signature_boundary_spine_aperture_atom_selected_tradeoff"],
    )
    (OUT_DIR / "aperture_atom_selected_tradeoff_candidates.csv").write_text(
        payloads["aperture_atom_selected_tradeoff_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_atom_selected_tradeoff_classes.csv").write_text(
        payloads["aperture_atom_selected_tradeoff_classes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_atom_selected_tradeoff_observables.csv").write_text(
        payloads["aperture_atom_selected_tradeoff_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_atom_selected_tradeoff_tables.npz",
        candidate_table=payloads["candidate_table"],
        class_table=payloads["class_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_atom_selected_tradeoff_certificate.json",
        payloads["signature_boundary_spine_aperture_atom_selected_tradeoff_certificate"],
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
                "frontier_candidate_ids": witness["frontier_candidate_ids"],
                "dominated_candidate_ids": witness["dominated_candidate_ids"],
                "zero_overhead_cost_transition": witness[
                    "zero_overhead_cost_transition"
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
