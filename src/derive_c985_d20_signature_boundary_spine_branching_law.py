from __future__ import annotations

import json
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_poincare_path import (
        OUT_DIR as SPINE_PATH_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        OUT_DIR as ROUTING_PREFIX_DIR,
        bitset,
        popcount,
        read_int_csv,
        scaled_ratio,
        table_from_rows,
    )
    from .derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
    )
    from .derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        REGION_NEGATIVE,
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
    from derive_c985_d20_signature_boundary_spine_poincare_path import (
        OUT_DIR as SPINE_PATH_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        OUT_DIR as ROUTING_PREFIX_DIR,
        bitset,
        popcount,
        read_int_csv,
        scaled_ratio,
        table_from_rows,
    )
    from derive_c985_d20_signature_geodesic_residual_chart import (
        OUT_DIR as RESIDUAL_CHART_DIR,
    )
    from derive_c985_d20_signature_residual_cell_complex import (
        EDGE_CENTRAL_NEGATIVE,
        EDGE_HIGH_NEGATIVE,
        REGION_NEGATIVE,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_branching_law"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_BRANCHING_LAW_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

SPINE_PATH_REPORT = SPINE_PATH_DIR / "report.json"
SPINE_PATH_EDGES = SPINE_PATH_DIR / "boundary_spine_poincare_edges.csv"
SPINE_PATH_TABLES = SPINE_PATH_DIR / "signature_boundary_spine_poincare_path_tables.npz"
SPINE_PATH_CERTIFICATE = (
    SPINE_PATH_DIR / "signature_boundary_spine_poincare_path_certificate.json"
)

ROUTING_PREFIX_REPORT = ROUTING_PREFIX_DIR / "report.json"
ROUTING_PREFIX_JSON = ROUTING_PREFIX_DIR / "signature_boundary_spine_routing_prefix.json"
ROUTING_PREFIX_SUMMARY = ROUTING_PREFIX_DIR / "routing_prefix_summary.csv"
ROUTING_PREFIX_TABLES = (
    ROUTING_PREFIX_DIR / "signature_boundary_spine_routing_prefix_tables.npz"
)
ROUTING_PREFIX_CERTIFICATE = (
    ROUTING_PREFIX_DIR / "signature_boundary_spine_routing_prefix_certificate.json"
)

RESIDUAL_CHART_REPORT = RESIDUAL_CHART_DIR / "report.json"
RESIDUAL_CHART_JSON = RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart.json"
RESIDUAL_CHART_CARRIER_CSV = RESIDUAL_CHART_DIR / "carrier_residual_chart.csv"
RESIDUAL_CHART_TABLES = RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_tables.npz"
RESIDUAL_CHART_CERTIFICATE = (
    RESIDUAL_CHART_DIR / "signature_geodesic_residual_chart_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT / "src" / "derive_c985_d20_signature_boundary_spine_branching_law.py"
)
VALIDATOR_SCRIPT = (
    ROOT / "src" / "certify_c985_d20_signature_boundary_spine_branching_law.py"
)

PROBABILITY_SCALE = 1_000_000_000_000
PHASE_PRE_FLIP = -1
PHASE_AT_FLIP = 0
PHASE_POST_FLIP = 1
PREVIOUS_OBSTRUCTION_MASKS = [4, 7, 8]

BRANCH_ORDER_COLUMNS = [
    "branch_order_rank",
    "negative_carrier_mask_class_id",
    "first_prefix_length",
    "first_boundary_mask_edge_id",
    "first_positive_carrier_mask_class_id",
    "first_boundary_partition_code",
    "first_phase_code",
    "previous_obstruction_flag",
    "negative_region_flag",
    "boundary_active_negative_flag",
    "carrier_atom_mask",
    "signature_class_count",
    "stationary_mass_x1e12",
    "axis_coordinate_x1e12",
    "signed_residual_coordinate_x1e12",
    "residual_gate_margin_x1e12",
    "cumulative_flux_at_entry_x1e12",
    "cumulative_entropy_at_entry_x1e12",
    "total_edge_count_for_carrier",
    "total_flux_for_carrier_x1e12",
    "total_entropy_for_carrier_x1e12",
]

PHASE_SUMMARY_COLUMNS = [
    "phase_code",
    "edge_count",
    "new_negative_carrier_count",
    "new_negative_carrier_bitset",
    "touched_negative_carrier_count",
    "touched_negative_carrier_bitset",
    "new_obstruction_carrier_count",
    "new_obstruction_carrier_bitset",
    "touched_obstruction_carrier_count",
    "touched_obstruction_carrier_bitset",
    "central_negative_edge_count",
    "high_negative_edge_count",
    "phase_flux_x1e12",
    "phase_flux_fraction_x1e12",
    "phase_entropy_x1e12",
    "phase_entropy_fraction_x1e12",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "residual_flip_prefix_length": 0,
    "negative_branch_count": 1,
    "boundary_active_negative_count": 2,
    "full_negative_region_count": 3,
    "inactive_negative_region_count": 4,
    "pre_flip_new_negative_count": 5,
    "at_flip_new_negative_count": 6,
    "post_flip_new_negative_count": 7,
    "pre_flip_obstruction_count": 8,
    "at_flip_obstruction_count": 9,
    "post_flip_obstruction_count": 10,
    "flip_new_negative_mask_id": 11,
    "flip_new_obstruction_flag": 12,
    "delayed_obstruction_mask_id": 13,
    "all_boundary_active_negative_reached_prefix": 14,
    "first_high_negative_prefix": 15,
    "all_boundary_active_before_high_flag": 16,
    "branch_completion_before_high_prefix_gap": 17,
    "obstruction_branch_order_signature": 18,
    "negative_branch_order_signature": 19,
    "inactive_negative_region_bitset": 20,
}


def phase_for_prefix(prefix_length: int, flip_prefix: int) -> int:
    if int(prefix_length) < int(flip_prefix):
        return PHASE_PRE_FLIP
    if int(prefix_length) == int(flip_prefix):
        return PHASE_AT_FLIP
    return PHASE_POST_FLIP


def decode_bitset(value: int) -> list[int]:
    return [index for index in range(64) if int(value) & (1 << index)]


def build_payloads() -> dict[str, Any]:
    spine_report = load_json(SPINE_PATH_REPORT)
    routing_report = load_json(ROUTING_PREFIX_REPORT)
    routing_prefix = load_json(ROUTING_PREFIX_JSON)
    residual_report = load_json(RESIDUAL_CHART_REPORT)
    residual_chart = load_json(RESIDUAL_CHART_JSON)

    spine_tables = np.load(SPINE_PATH_TABLES, allow_pickle=False)
    routing_tables = np.load(ROUTING_PREFIX_TABLES, allow_pickle=False)
    residual_tables = np.load(RESIDUAL_CHART_TABLES, allow_pickle=False)

    edge_rows = read_int_csv(SPINE_PATH_EDGES)
    summary_rows = read_int_csv(ROUTING_PREFIX_SUMMARY)
    carrier_rows = {
        int(row["carrier_mask_class_id"]): row
        for row in read_int_csv(RESIDUAL_CHART_CARRIER_CSV)
    }

    flip_prefix = int(
        routing_report["witness"]["edge_cloud_crossing_prefix"]["prefix_length"]
    )
    total_flux = sum(int(row["undirected_stationary_flux_x1e12"]) for row in edge_rows)
    total_entropy = sum(
        int(row["total_entropy_contribution_x1e12"]) for row in edge_rows
    )

    cumulative_by_prefix = {
        int(row["prefix_length"]): {
            "flux": int(row["cumulative_flux_x1e12"]),
            "entropy": int(row["cumulative_entropy_x1e12"]),
        }
        for row in summary_rows
    }
    total_by_negative: dict[int, dict[str, int]] = {}
    for row in edge_rows:
        mask_id = int(row["negative_carrier_mask_class_id"])
        totals = total_by_negative.setdefault(
            mask_id,
            {
                "edge_count": 0,
                "flux": 0,
                "entropy": 0,
            },
        )
        totals["edge_count"] += 1
        totals["flux"] += int(row["undirected_stationary_flux_x1e12"])
        totals["entropy"] += int(row["total_entropy_contribution_x1e12"])

    negative_region_bitset = bitset(
        {
            int(row["carrier_mask_class_id"])
            for row in carrier_rows.values()
            if int(row["elbow_region_code"]) == REGION_NEGATIVE
        }
    )
    boundary_active_negative_bitset = bitset(
        {int(row["negative_carrier_mask_class_id"]) for row in edge_rows}
    )
    inactive_negative_bitset = negative_region_bitset & ~boundary_active_negative_bitset
    obstruction_bitset = bitset(PREVIOUS_OBSTRUCTION_MASKS)

    seen: set[int] = set()
    branch_rows: list[dict[str, int]] = []
    for row in edge_rows:
        mask_id = int(row["negative_carrier_mask_class_id"])
        if mask_id in seen:
            continue
        seen.add(mask_id)
        prefix_length = int(row["boundary_spine_rank"])
        phase_code = phase_for_prefix(prefix_length, flip_prefix)
        carrier = carrier_rows[mask_id]
        totals = total_by_negative[mask_id]
        branch_rows.append(
            {
                "branch_order_rank": len(branch_rows) + 1,
                "negative_carrier_mask_class_id": mask_id,
                "first_prefix_length": prefix_length,
                "first_boundary_mask_edge_id": int(row["boundary_mask_edge_id"]),
                "first_positive_carrier_mask_class_id": int(
                    row["positive_carrier_mask_class_id"]
                ),
                "first_boundary_partition_code": int(row["boundary_partition_code"]),
                "first_phase_code": phase_code,
                "previous_obstruction_flag": int(
                    mask_id in PREVIOUS_OBSTRUCTION_MASKS
                ),
                "negative_region_flag": int(
                    bool(negative_region_bitset & (1 << mask_id))
                ),
                "boundary_active_negative_flag": int(
                    bool(boundary_active_negative_bitset & (1 << mask_id))
                ),
                "carrier_atom_mask": int(carrier["carrier_atom_mask"]),
                "signature_class_count": int(carrier["signature_class_count"]),
                "stationary_mass_x1e12": int(carrier["stationary_mass_x1e12"]),
                "axis_coordinate_x1e12": int(carrier["axis_coordinate_x1e12"]),
                "signed_residual_coordinate_x1e12": int(
                    carrier["signed_residual_coordinate_x1e12"]
                ),
                "residual_gate_margin_x1e12": int(
                    carrier["residual_gate_margin_x1e12"]
                ),
                "cumulative_flux_at_entry_x1e12": cumulative_by_prefix[
                    prefix_length
                ]["flux"],
                "cumulative_entropy_at_entry_x1e12": cumulative_by_prefix[
                    prefix_length
                ]["entropy"],
                "total_edge_count_for_carrier": totals["edge_count"],
                "total_flux_for_carrier_x1e12": totals["flux"],
                "total_entropy_for_carrier_x1e12": totals["entropy"],
            }
        )

    phase_rows: list[dict[str, int]] = []
    for phase_code in (PHASE_PRE_FLIP, PHASE_AT_FLIP, PHASE_POST_FLIP):
        phase_edge_rows = [
            row
            for row in edge_rows
            if phase_for_prefix(int(row["boundary_spine_rank"]), flip_prefix)
            == phase_code
        ]
        new_negative = {
            int(row["negative_carrier_mask_class_id"])
            for row in branch_rows
            if int(row["first_phase_code"]) == phase_code
        }
        touched_negative = {
            int(row["negative_carrier_mask_class_id"]) for row in phase_edge_rows
        }
        new_obstruction = new_negative & set(PREVIOUS_OBSTRUCTION_MASKS)
        touched_obstruction = touched_negative & set(PREVIOUS_OBSTRUCTION_MASKS)
        phase_flux = sum(
            int(row["undirected_stationary_flux_x1e12"]) for row in phase_edge_rows
        )
        phase_entropy = sum(
            int(row["total_entropy_contribution_x1e12"]) for row in phase_edge_rows
        )
        phase_rows.append(
            {
                "phase_code": phase_code,
                "edge_count": len(phase_edge_rows),
                "new_negative_carrier_count": len(new_negative),
                "new_negative_carrier_bitset": bitset(new_negative),
                "touched_negative_carrier_count": len(touched_negative),
                "touched_negative_carrier_bitset": bitset(touched_negative),
                "new_obstruction_carrier_count": len(new_obstruction),
                "new_obstruction_carrier_bitset": bitset(new_obstruction),
                "touched_obstruction_carrier_count": len(touched_obstruction),
                "touched_obstruction_carrier_bitset": bitset(touched_obstruction),
                "central_negative_edge_count": sum(
                    1
                    for row in phase_edge_rows
                    if int(row["boundary_partition_code"]) == EDGE_CENTRAL_NEGATIVE
                ),
                "high_negative_edge_count": sum(
                    1
                    for row in phase_edge_rows
                    if int(row["boundary_partition_code"]) == EDGE_HIGH_NEGATIVE
                ),
                "phase_flux_x1e12": phase_flux,
                "phase_flux_fraction_x1e12": scaled_ratio(phase_flux, total_flux),
                "phase_entropy_x1e12": phase_entropy,
                "phase_entropy_fraction_x1e12": scaled_ratio(
                    phase_entropy,
                    total_entropy,
                ),
            }
        )

    first_high_negative_prefix = min(
        int(row["boundary_spine_rank"])
        for row in edge_rows
        if int(row["boundary_partition_code"]) == EDGE_HIGH_NEGATIVE
    )
    all_negative_reached_prefix = max(
        int(row["first_prefix_length"]) for row in branch_rows
    )
    flip_new_masks = [
        int(row["negative_carrier_mask_class_id"])
        for row in branch_rows
        if int(row["first_phase_code"]) == PHASE_AT_FLIP
    ]
    delayed_obstruction = [
        int(row["negative_carrier_mask_class_id"])
        for row in branch_rows
        if int(row["previous_obstruction_flag"]) == 1
        and int(row["first_phase_code"]) == PHASE_POST_FLIP
    ]
    obstruction_branch_order = [
        int(row["negative_carrier_mask_class_id"])
        for row in branch_rows
        if int(row["previous_obstruction_flag"]) == 1
    ]
    negative_branch_order = [
        int(row["negative_carrier_mask_class_id"]) for row in branch_rows
    ]
    obstruction_order_signature = sum(
        (index + 1) * mask_id for index, mask_id in enumerate(obstruction_branch_order)
    )
    negative_order_signature = sum(
        (index + 1) * mask_id for index, mask_id in enumerate(negative_branch_order)
    )

    observable_values = {
        "residual_flip_prefix_length": flip_prefix,
        "negative_branch_count": len(branch_rows),
        "boundary_active_negative_count": popcount(boundary_active_negative_bitset),
        "full_negative_region_count": popcount(negative_region_bitset),
        "inactive_negative_region_count": popcount(inactive_negative_bitset),
        "pre_flip_new_negative_count": next(
            row for row in phase_rows if int(row["phase_code"]) == PHASE_PRE_FLIP
        )["new_negative_carrier_count"],
        "at_flip_new_negative_count": next(
            row for row in phase_rows if int(row["phase_code"]) == PHASE_AT_FLIP
        )["new_negative_carrier_count"],
        "post_flip_new_negative_count": next(
            row for row in phase_rows if int(row["phase_code"]) == PHASE_POST_FLIP
        )["new_negative_carrier_count"],
        "pre_flip_obstruction_count": next(
            row for row in phase_rows if int(row["phase_code"]) == PHASE_PRE_FLIP
        )["new_obstruction_carrier_count"],
        "at_flip_obstruction_count": next(
            row for row in phase_rows if int(row["phase_code"]) == PHASE_AT_FLIP
        )["new_obstruction_carrier_count"],
        "post_flip_obstruction_count": next(
            row for row in phase_rows if int(row["phase_code"]) == PHASE_POST_FLIP
        )["new_obstruction_carrier_count"],
        "flip_new_negative_mask_id": flip_new_masks[0],
        "flip_new_obstruction_flag": int(flip_new_masks[0] in PREVIOUS_OBSTRUCTION_MASKS),
        "delayed_obstruction_mask_id": delayed_obstruction[0],
        "all_boundary_active_negative_reached_prefix": all_negative_reached_prefix,
        "first_high_negative_prefix": first_high_negative_prefix,
        "all_boundary_active_before_high_flag": int(
            all_negative_reached_prefix < first_high_negative_prefix
        ),
        "branch_completion_before_high_prefix_gap": int(
            first_high_negative_prefix - all_negative_reached_prefix
        ),
        "obstruction_branch_order_signature": obstruction_order_signature,
        "negative_branch_order_signature": negative_order_signature,
        "inactive_negative_region_bitset": inactive_negative_bitset,
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

    branch_table = table_from_rows(BRANCH_ORDER_COLUMNS, branch_rows)
    phase_table = table_from_rows(PHASE_SUMMARY_COLUMNS, phase_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "spine_path_report_certified": spine_report.get("all_checks_pass") is True,
        "routing_prefix_report_certified": routing_report.get("all_checks_pass")
        is True,
        "residual_chart_report_certified": residual_report.get("all_checks_pass")
        is True,
        "spine_path_certificate_available": SPINE_PATH_CERTIFICATE.exists(),
        "routing_prefix_certificate_available": ROUTING_PREFIX_CERTIFICATE.exists(),
        "residual_chart_certificate_available": RESIDUAL_CHART_CERTIFICATE.exists(),
        "routing_prefix_schema_available": routing_prefix.get("schema")
        == "c985.d20_signature_boundary_spine_routing_prefix@1",
        "residual_chart_schema_available": residual_chart.get("schema")
        == "c985.d20_signature_geodesic_residual_chart@1",
        "spine_path_tables_available": "spine_poincare_edge_table"
        in spine_tables.files,
        "routing_prefix_tables_available": "routing_prefix_summary_table"
        in routing_tables.files,
        "residual_chart_tables_available": "carrier_residual_chart_table"
        in residual_tables.files,
        "branch_order_matches_expected": negative_branch_order
        == [13, 7, 8, 9, 6, 4],
        "branch_first_prefixes_match_expected": [
            int(row["first_prefix_length"]) for row in branch_rows
        ]
        == [1, 3, 5, 8, 12, 14],
        "phase_new_bitsets_match_expected": [
            int(row["new_negative_carrier_bitset"]) for row in phase_rows
        ]
        == [8576, 512, 80],
        "phase_edge_counts_match_expected": [
            int(row["edge_count"]) for row in phase_rows
        ]
        == [7, 1, 8],
        "obstruction_branch_order_matches_expected": obstruction_branch_order
        == [7, 8, 4],
        "obstruction_phase_counts_match_expected": (
            observable_values["pre_flip_obstruction_count"],
            observable_values["at_flip_obstruction_count"],
            observable_values["post_flip_obstruction_count"],
        )
        == (2, 0, 1),
        "flip_new_mask_is_non_obstruction_9": (
            observable_values["flip_new_negative_mask_id"],
            observable_values["flip_new_obstruction_flag"],
        )
        == (9, 0),
        "delayed_obstruction_is_mask_4": observable_values[
            "delayed_obstruction_mask_id"
        ]
        == 4,
        "all_boundary_active_negative_reached_before_high_contact": (
            observable_values["all_boundary_active_negative_reached_prefix"],
            observable_values["first_high_negative_prefix"],
            observable_values["all_boundary_active_before_high_flag"],
        )
        == (14, 15, 1),
        "inactive_negative_region_is_mask_5": inactive_negative_bitset == 32,
        "branch_table_shape_is_6_by_21": tuple(branch_table.shape)
        == (6, len(BRANCH_ORDER_COLUMNS)),
        "phase_table_shape_is_3_by_16": tuple(phase_table.shape)
        == (3, len(PHASE_SUMMARY_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "residual_flip_prefix_length": flip_prefix,
        "negative_branch_order": negative_branch_order,
        "negative_branch_first_prefixes": [
            int(row["first_prefix_length"]) for row in branch_rows
        ],
        "negative_branch_first_edge_ids": [
            int(row["first_boundary_mask_edge_id"]) for row in branch_rows
        ],
        "pre_flip_new_negative_mask_ids": decode_bitset(phase_rows[0]["new_negative_carrier_bitset"]),
        "at_flip_new_negative_mask_ids": decode_bitset(phase_rows[1]["new_negative_carrier_bitset"]),
        "post_flip_new_negative_mask_ids": decode_bitset(phase_rows[2]["new_negative_carrier_bitset"]),
        "previous_obstruction_mask_class_ids": PREVIOUS_OBSTRUCTION_MASKS,
        "obstruction_branch_order": obstruction_branch_order,
        "obstruction_branch_first_prefixes": [
            int(row["first_prefix_length"])
            for row in branch_rows
            if int(row["previous_obstruction_flag"]) == 1
        ],
        "pre_flip_obstruction_mask_ids": decode_bitset(
            phase_rows[0]["new_obstruction_carrier_bitset"]
        ),
        "at_flip_obstruction_mask_ids": decode_bitset(
            phase_rows[1]["new_obstruction_carrier_bitset"]
        ),
        "post_flip_obstruction_mask_ids": decode_bitset(
            phase_rows[2]["new_obstruction_carrier_bitset"]
        ),
        "flip_new_negative_mask_id": observable_values["flip_new_negative_mask_id"],
        "delayed_obstruction_mask_id": observable_values[
            "delayed_obstruction_mask_id"
        ],
        "all_boundary_active_negative_reached_prefix": all_negative_reached_prefix,
        "first_high_negative_prefix": first_high_negative_prefix,
        "boundary_active_negative_mask_ids": decode_bitset(
            boundary_active_negative_bitset
        ),
        "inactive_negative_region_mask_ids": decode_bitset(inactive_negative_bitset),
        "phase_flux_entropy": {
            "pre_flip": {
                "edge_count": int(phase_rows[0]["edge_count"]),
                "flux_fraction_x1e12": int(
                    phase_rows[0]["phase_flux_fraction_x1e12"]
                ),
                "entropy_fraction_x1e12": int(
                    phase_rows[0]["phase_entropy_fraction_x1e12"]
                ),
            },
            "at_flip": {
                "edge_count": int(phase_rows[1]["edge_count"]),
                "flux_fraction_x1e12": int(
                    phase_rows[1]["phase_flux_fraction_x1e12"]
                ),
                "entropy_fraction_x1e12": int(
                    phase_rows[1]["phase_entropy_fraction_x1e12"]
                ),
            },
            "post_flip": {
                "edge_count": int(phase_rows[2]["edge_count"]),
                "flux_fraction_x1e12": int(
                    phase_rows[2]["phase_flux_fraction_x1e12"]
                ),
                "entropy_fraction_x1e12": int(
                    phase_rows[2]["phase_entropy_fraction_x1e12"]
                ),
            },
        },
        "negative_branch_order_table_sha256": sha_array(branch_table),
        "branch_phase_summary_table_sha256": sha_array(phase_table),
        "branch_observable_table_sha256": sha_array(observable_table),
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_branching_law_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_BRANCHING_LAW_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the negative branch first-arrival order is 13, 7, 8, 9, 6, 4",
            "the prefix-8 residual flip introduces carrier mask 9, not one of the old obstruction masks",
            "the old obstruction masks enter in branch order 7, 8, 4",
            "masks 7 and 8 enter before the residual flip, while mask 4 is the delayed post-flip obstruction",
            "all boundary-active negative masks are reached at prefix 14, one step before the first high-negative contact",
        ],
    }

    branch_law = {
        "schema": "c985.d20_signature_boundary_spine_branching_law@1",
        "object": "d20",
        "routing_rule": {
            "source": "certified entropy-ordered Poincare conductance-spine routing prefix",
            "branch_order": "first occurrence of each negative carrier mask along the ranked boundary spine",
            "phase_rule": "pre-flip if first prefix is below 8, at-flip if it is 8, post-flip if above 8",
            "comparison": "intersect first-arrival phases with previous one-dimensional obstruction masks 4, 7, and 8",
        },
        "residual_flip_prefix_length": flip_prefix,
        "negative_branch_order": witness["negative_branch_order"],
        "obstruction_branch_order": witness["obstruction_branch_order"],
        "pre_flip_new_negative_mask_ids": witness["pre_flip_new_negative_mask_ids"],
        "at_flip_new_negative_mask_ids": witness["at_flip_new_negative_mask_ids"],
        "post_flip_new_negative_mask_ids": witness["post_flip_new_negative_mask_ids"],
        "delayed_obstruction_mask_id": witness["delayed_obstruction_mask_id"],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_branching_law@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The prefix-8 residual flip induces a finite branch law on negative "
            "carrier masks: 13, 7, and 8 enter before the flip, 9 enters at the "
            "flip, and 6 then 4 enter after it, so the old one-dimensional "
            "obstruction masks split as early 7,8 and delayed 4."
        ),
        "stage_protocol": {
            "draft": "read the entropy spine as a first-arrival order on negative carrier masks",
            "witness": "materialize branch-order and phase-summary tables around the prefix-8 residual flip",
            "coherence": "compare the first-arrival phases with the previous one-dimensional obstruction masks",
            "closure": "certify a finite branch law without claiming an alternative ordering or continuum flow",
            "emit": "emit branch-law JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "spine_path_report": input_entry(
                SPINE_PATH_REPORT,
                {
                    "status": spine_report.get("status"),
                    "certificate_sha256": spine_report.get("certificate_sha256"),
                },
            ),
            "spine_path_edges": input_entry(SPINE_PATH_EDGES),
            "spine_path_tables": input_entry(SPINE_PATH_TABLES),
            "spine_path_certificate": input_entry(SPINE_PATH_CERTIFICATE),
            "routing_prefix_report": input_entry(
                ROUTING_PREFIX_REPORT,
                {
                    "status": routing_report.get("status"),
                    "certificate_sha256": routing_report.get("certificate_sha256"),
                },
            ),
            "routing_prefix": input_entry(ROUTING_PREFIX_JSON),
            "routing_prefix_summary": input_entry(ROUTING_PREFIX_SUMMARY),
            "routing_prefix_tables": input_entry(ROUTING_PREFIX_TABLES),
            "routing_prefix_certificate": input_entry(ROUTING_PREFIX_CERTIFICATE),
            "residual_chart_report": input_entry(
                RESIDUAL_CHART_REPORT,
                {
                    "status": residual_report.get("status"),
                    "certificate_sha256": residual_report.get("certificate_sha256"),
                },
            ),
            "residual_chart": input_entry(RESIDUAL_CHART_JSON),
            "residual_chart_carriers": input_entry(RESIDUAL_CHART_CARRIER_CSV),
            "residual_chart_tables": input_entry(RESIDUAL_CHART_TABLES),
            "residual_chart_certificate": input_entry(RESIDUAL_CHART_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_branching_law": relpath(
                OUT_DIR / "signature_boundary_spine_branching_law.json"
            ),
            "negative_branch_order_csv": relpath(
                OUT_DIR / "negative_branch_order.csv"
            ),
            "branch_phase_summary_csv": relpath(
                OUT_DIR / "branch_phase_summary.csv"
            ),
            "branch_observables_csv": relpath(OUT_DIR / "branch_observables.csv"),
            "signature_boundary_spine_branching_law_tables": relpath(
                OUT_DIR / "signature_boundary_spine_branching_law_tables.npz"
            ),
            "signature_boundary_spine_branching_law_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_branching_law_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "first-arrival order of boundary-active negative carrier masks along the entropy spine",
                "pre-flip, at-flip, and post-flip carrier phases around the prefix-8 residual crossing",
                "the branch-order placement of the previous obstruction masks 4, 7, and 8",
                "that all boundary-active negative masks enter before the first high-negative boundary contact",
            ],
            "does_not_certify_because_not_required": [
                "that this branch order is invariant under alternative spine rankings",
                "a stochastic branching process, continuum geodesic flow, or mixing-time estimate",
                "higher-eigenmode branch laws",
                "new associator, pentagon, pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Promote the branch law into a typed corridor certificate: for each "
            "new negative carrier branch, certify the positive carrier masks and "
            "active atoms that deliver it, then compare that corridor grammar with "
            "the six-symbol rewrite alphabet."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_branching_law_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified Poincare-spine, routing-prefix, and residual-chart artifacts",
            "extract first arrivals of every boundary-active negative carrier mask",
            "phase first arrivals against the prefix-8 residual flip",
            "compare branch phases with the previous one-dimensional obstruction masks",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_branching_law": branch_law,
        "negative_branch_order_csv": csv_text(BRANCH_ORDER_COLUMNS, branch_rows),
        "branch_phase_summary_csv": csv_text(PHASE_SUMMARY_COLUMNS, phase_rows),
        "branch_observables_csv": csv_text(OBSERVABLE_COLUMNS, observable_rows),
        "negative_branch_order_table": branch_table,
        "branch_phase_summary_table": phase_table,
        "branch_observable_table": observable_table,
        "signature_boundary_spine_branching_law_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_branching_law.json",
        payloads["signature_boundary_spine_branching_law"],
    )
    (OUT_DIR / "negative_branch_order.csv").write_text(
        payloads["negative_branch_order_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "branch_phase_summary.csv").write_text(
        payloads["branch_phase_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "branch_observables.csv").write_text(
        payloads["branch_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_branching_law_tables.npz",
        negative_branch_order_table=payloads["negative_branch_order_table"],
        branch_phase_summary_table=payloads["branch_phase_summary_table"],
        branch_observable_table=payloads["branch_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_branching_law_certificate.json",
        payloads["signature_boundary_spine_branching_law_certificate"],
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
                "negative_branch_order": witness["negative_branch_order"],
                "negative_branch_first_prefixes": witness[
                    "negative_branch_first_prefixes"
                ],
                "obstruction_branch_order": witness["obstruction_branch_order"],
                "pre_flip_new_negative_mask_ids": witness[
                    "pre_flip_new_negative_mask_ids"
                ],
                "at_flip_new_negative_mask_ids": witness[
                    "at_flip_new_negative_mask_ids"
                ],
                "post_flip_new_negative_mask_ids": witness[
                    "post_flip_new_negative_mask_ids"
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
