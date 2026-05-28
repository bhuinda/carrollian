from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality import (
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_EXACT_WITNESSES,
        CARRIER_SPLICE_JSON,
        CARRIER_SPLICE_REPORT,
        CARRIER_SPLICE_SELECTED_TEMPLATES,
        CARRIER_SPLICE_TABLES,
        OUT_DIR as CARRIER_SPLICE_OPTIMALITY_DIR,
        STATUS as CARRIER_SPLICE_OPTIMALITY_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        EXACT_WITNESS_COLUMNS,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SHARED_TAIL_WORD,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        CELL_COMPLEX_EDGES,
        FIXED_TAIL_ATOMS,
        OUT_DIR as ENDPOINT_SPLIT_DIR,
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        csv_text,
        read_int_csv,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality import (
        CARRIER_SPLICE_CERTIFICATE,
        CARRIER_SPLICE_EXACT_WITNESSES,
        CARRIER_SPLICE_JSON,
        CARRIER_SPLICE_REPORT,
        CARRIER_SPLICE_SELECTED_TEMPLATES,
        CARRIER_SPLICE_TABLES,
        OUT_DIR as CARRIER_SPLICE_OPTIMALITY_DIR,
        STATUS as CARRIER_SPLICE_OPTIMALITY_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        EXACT_WITNESS_COLUMNS,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SHARED_TAIL_WORD,
        TRACE_NODE_COLUMNS,
        WORD_COLUMNS,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        CELL_COMPLEX_EDGES,
        FIXED_TAIL_ATOMS,
        OUT_DIR as ENDPOINT_SPLIT_DIR,
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        csv_text,
        read_int_csv,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_LOWER_VARIATION_LIFT_OBSTRUCTION_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CARRIER_SPLICE_OPTIMALITY_REPORT = CARRIER_SPLICE_OPTIMALITY_DIR / "report.json"
CARRIER_SPLICE_OPTIMALITY_JSON = (
    CARRIER_SPLICE_OPTIMALITY_DIR
    / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality.json"
)
CARRIER_SPLICE_OPTIMALITY_FRONTIER = (
    CARRIER_SPLICE_OPTIMALITY_DIR
    / "aperture_closure_tail_carrier_splice_frontier.csv"
)
CARRIER_SPLICE_OPTIMALITY_CLASSES = (
    CARRIER_SPLICE_OPTIMALITY_DIR
    / "aperture_closure_tail_carrier_splice_optimality_classes.csv"
)
CARRIER_SPLICE_OPTIMALITY_OBSERVABLES = (
    CARRIER_SPLICE_OPTIMALITY_DIR
    / "aperture_closure_tail_carrier_splice_optimality_observables.csv"
)
CARRIER_SPLICE_OPTIMALITY_TABLES = (
    CARRIER_SPLICE_OPTIMALITY_DIR
    / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_tables.npz"
)
CARRIER_SPLICE_OPTIMALITY_CERTIFICATE = (
    CARRIER_SPLICE_OPTIMALITY_DIR
    / "signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality_certificate.json"
)
ENDPOINT_SPLIT_TEMPLATES = ENDPOINT_SPLIT_DIR / "aperture_closure_tail_templates.csv"

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction.py"
)

LOWER_VARIATION_WITNESS_IDS = (0, 1)
SELECTED_SIX_TEMPLATE_WITNESS_ID = 2
SELECTED_SIX_TEMPLATE_VARIATION = 223
TARGET_DELTA_TWICE = 2
TARGET_CLOSED_PATH_COUNT = 24
PROFILE_WITNESS_IDS = (*LOWER_VARIATION_WITNESS_IDS, SELECTED_SIX_TEMPLATE_WITNESS_ID)

PROFILE_CLASS_CODES = {
    "lower_variation_collapsed_tail_repair": 0,
    "selected_six_template_lift": 1,
}

PROFILE_COLUMNS = [
    "splice_witness_id",
    "profile_class_code",
    "word_length",
    "pre_tail_symbol_count",
    "inserted_symbol_count_over_rank104",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "variation_gap_to_selected_six_template_lift",
    "first_return_closed_path_count",
    "full_carrier_path_count",
    "normalized_tail_template_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "rank104_template_match_count",
    "non_rank104_template_count",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
    "tail_entry_other_path_count",
    "fixed_tail_atom_sequence_flag",
    "six_template_retention_flag",
    "lower_than_selected_flag",
    "selected_six_template_lift_flag",
]

TEMPLATE_COLUMNS = [
    "splice_witness_id",
    "normalized_tail_template_id",
    "parent_rank104_template_id",
    "tail_entry_carrier_id",
    "splice_path_count",
    "rank104_original_path_count",
    "rank104_template_match_flag",
    *TAIL_CARRIER_COLUMNS,
    *TAIL_EDGE_COLUMNS,
    *TAIL_ATOM_COLUMNS,
]

LIFT_EDGE_COLUMNS = [
    "lift_edge_id",
    "from_witness_id",
    "to_witness_id",
    "from_variation",
    "to_variation",
    "variation_gap_to_six_template_lift",
    "from_delta_twice",
    "to_delta_twice",
    "delta_preserved_flag",
    "from_closed_path_count",
    "to_closed_path_count",
    "closed_path_preserved_flag",
    "from_template_count",
    "to_template_count",
    "template_count_gain",
    "from_template_lift_min",
    "to_template_lift_min",
    "template_lift_min_change",
    "from_rank104_template_match_count",
    "to_rank104_template_match_count",
    "rank104_template_match_gain",
    "endpoint_9_path_count_change",
    "endpoint_10_path_count_change",
    "endpoint_11_path_count_change",
    "endpoint_13_path_count_change",
    "six_template_retention_gain",
    "delta4_reintroduced_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "lower_variation_witness_count": 0,
    "lower_variation_min": 1,
    "lower_variation_max": 2,
    "lower_variation_template_count_min": 3,
    "lower_variation_template_count_max": 4,
    "lower_variation_endpoint11_only_count": 5,
    "lower_variation_endpoint13_only_count": 6,
    "selected_lift_witness_id": 7,
    "selected_lift_variation": 8,
    "selected_lift_template_count": 9,
    "selected_lift_delta_twice": 10,
    "selected_lift_closed_paths": 11,
    "min_variation_gap_to_six_template_lift": 12,
    "max_variation_gap_to_six_template_lift": 13,
    "lift_reintroduces_delta4_count": 14,
    "lower_variation_direct_six_template_lift_count": 15,
    "lower_variation_rank104_template_match_max": 16,
    "selected_lift_endpoint_9_count": 17,
    "selected_lift_endpoint_10_count": 18,
    "selected_lift_endpoint_11_count": 19,
    "selected_lift_endpoint_13_count": 20,
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def read_int_dict_csv(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def row_word(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in WORD_COLUMNS[: row["word_length"]])


def row_trace(row: dict[str, int]) -> tuple[int, ...]:
    return tuple(row[column] for column in TRACE_NODE_COLUMNS[: row["trace_node_count"]])


def endpoint_counts(
    templates: Counter[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
) -> Counter[int]:
    counts: Counter[int] = Counter()
    for template, path_count in templates.items():
        counts[int(template[0][0])] += int(path_count)
    return counts


def template_counts_for_word(
    word: tuple[int, ...],
    carrier_adjacency: dict[int, list[tuple[int, int]]],
) -> Counter[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    states = carrier_paths(word, carrier_adjacency)
    closed_states = first_return_closed(states)
    tail_start = len(word) - len(SHARED_TAIL_WORD)
    return Counter(tail_slices(state, tail_start) for state in closed_states)


def rank104_template_map() -> dict[tuple[int, ...], dict[str, int]]:
    rows = read_int_dict_csv(ENDPOINT_SPLIT_TEMPLATES)
    return {tuple(row[column] for column in TAIL_CARRIER_COLUMNS): row for row in rows}


def build_payloads() -> dict[str, Any]:
    carrier_splice_report = load_json(CARRIER_SPLICE_REPORT)
    carrier_splice_json = load_json(CARRIER_SPLICE_JSON)
    carrier_splice_certificate = load_json(CARRIER_SPLICE_CERTIFICATE)
    optimality_report = load_json(CARRIER_SPLICE_OPTIMALITY_REPORT)
    optimality_json = load_json(CARRIER_SPLICE_OPTIMALITY_JSON)
    optimality_certificate = load_json(CARRIER_SPLICE_OPTIMALITY_CERTIFICATE)
    exact_rows_parent = read_int_dict_csv(CARRIER_SPLICE_EXACT_WITNESSES)
    selected_templates_parent = read_int_dict_csv(CARRIER_SPLICE_SELECTED_TEMPLATES)

    exact_by_id = {row["splice_witness_id"]: row for row in exact_rows_parent}
    selected_row = exact_by_id[SELECTED_SIX_TEMPLATE_WITNESS_ID]
    lower_rows = [exact_by_id[witness_id] for witness_id in LOWER_VARIATION_WITNESS_IDS]

    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    carrier_adjacency, _carriers = build_carrier_adjacency(
        read_int_csv(CELL_COMPLEX_EDGES),
        atom_to_symbol,
    )

    parent_template_by_carriers = rank104_template_map()
    template_counts_by_witness = {
        witness_id: template_counts_for_word(row_word(exact_by_id[witness_id]), carrier_adjacency)
        for witness_id in PROFILE_WITNESS_IDS
    }

    profile_rows: list[dict[str, int]] = []
    template_rows: list[dict[str, int]] = []
    profile_by_id: dict[int, dict[str, int]] = {}
    for witness_id in PROFILE_WITNESS_IDS:
        row = exact_by_id[witness_id]
        templates = template_counts_by_witness[witness_id]
        endpoints = endpoint_counts(templates)
        lift_counts = sorted(int(value) for value in templates.values())
        rank104_match_count = sum(
            1 for template in templates if template[0] in parent_template_by_carriers
        )
        total_endpoint_count = sum(int(value) for value in endpoints.values())
        endpoint_other_count = total_endpoint_count - sum(
            endpoints[entry] for entry in (9, 10, 11, 13)
        )
        is_selected_lift = witness_id == SELECTED_SIX_TEMPLATE_WITNESS_ID
        profile = {
            "splice_witness_id": witness_id,
            "profile_class_code": PROFILE_CLASS_CODES[
                "selected_six_template_lift"
                if is_selected_lift
                else "lower_variation_collapsed_tail_repair"
            ],
            "word_length": row["word_length"],
            "pre_tail_symbol_count": row["pre_tail_symbol_count"],
            "inserted_symbol_count_over_rank104": row[
                "inserted_symbol_count_over_rank104"
            ],
            "metric_gromov_delta_twice": row["metric_gromov_delta_twice"],
            "trace_signature_total_variation": row[
                "trace_signature_total_variation"
            ],
            "variation_gap_to_selected_six_template_lift": SELECTED_SIX_TEMPLATE_VARIATION
            - row["trace_signature_total_variation"],
            "first_return_closed_path_count": row["first_return_closed_path_count"],
            "full_carrier_path_count": row["full_carrier_path_count"],
            "normalized_tail_template_count": len(templates),
            "template_lift_count_min": min(lift_counts),
            "template_lift_count_max": max(lift_counts),
            "rank104_template_match_count": rank104_match_count,
            "non_rank104_template_count": len(templates) - rank104_match_count,
            "tail_entry_9_path_count": endpoints[9],
            "tail_entry_10_path_count": endpoints[10],
            "tail_entry_11_path_count": endpoints[11],
            "tail_entry_13_path_count": endpoints[13],
            "tail_entry_other_path_count": endpoint_other_count,
            "fixed_tail_atom_sequence_flag": int(
                all(tuple(template[2]) == FIXED_TAIL_ATOMS for template in templates)
            ),
            "six_template_retention_flag": row["six_template_retention_flag"],
            "lower_than_selected_flag": int(
                row["trace_signature_total_variation"]
                < SELECTED_SIX_TEMPLATE_VARIATION
            ),
            "selected_six_template_lift_flag": int(is_selected_lift),
        }
        profile_rows.append(profile)
        profile_by_id[witness_id] = profile

        for template_id, (template, count) in enumerate(
            sorted(templates.items(), key=lambda item: item[0][0])
        ):
            carriers, edge_ids, atom_ids = template
            parent = parent_template_by_carriers.get(tuple(carriers))
            parent_template_id = (
                parent["normalized_tail_template_id"] if parent is not None else -1
            )
            rank104_original_path_count = (
                parent["rank104_outlier_path_count"] if parent is not None else 0
            )
            template_rows.append(
                {
                    "splice_witness_id": witness_id,
                    "normalized_tail_template_id": template_id,
                    "parent_rank104_template_id": parent_template_id,
                    "tail_entry_carrier_id": int(carriers[0]),
                    "splice_path_count": int(count),
                    "rank104_original_path_count": rank104_original_path_count,
                    "rank104_template_match_flag": int(parent is not None),
                    **{
                        column: value
                        for column, value in zip(TAIL_CARRIER_COLUMNS, carriers)
                    },
                    **{column: value for column, value in zip(TAIL_EDGE_COLUMNS, edge_ids)},
                    **{column: value for column, value in zip(TAIL_ATOM_COLUMNS, atom_ids)},
                }
            )

    selected_profile = profile_by_id[SELECTED_SIX_TEMPLATE_WITNESS_ID]
    lift_edge_rows = []
    for edge_id, witness_id in enumerate(LOWER_VARIATION_WITNESS_IDS):
        source = profile_by_id[witness_id]
        lift_edge_rows.append(
            {
                "lift_edge_id": edge_id,
                "from_witness_id": witness_id,
                "to_witness_id": SELECTED_SIX_TEMPLATE_WITNESS_ID,
                "from_variation": source["trace_signature_total_variation"],
                "to_variation": selected_profile["trace_signature_total_variation"],
                "variation_gap_to_six_template_lift": selected_profile[
                    "trace_signature_total_variation"
                ]
                - source["trace_signature_total_variation"],
                "from_delta_twice": source["metric_gromov_delta_twice"],
                "to_delta_twice": selected_profile["metric_gromov_delta_twice"],
                "delta_preserved_flag": int(
                    source["metric_gromov_delta_twice"]
                    == selected_profile["metric_gromov_delta_twice"]
                ),
                "from_closed_path_count": source["first_return_closed_path_count"],
                "to_closed_path_count": selected_profile[
                    "first_return_closed_path_count"
                ],
                "closed_path_preserved_flag": int(
                    source["first_return_closed_path_count"]
                    == selected_profile["first_return_closed_path_count"]
                ),
                "from_template_count": source["normalized_tail_template_count"],
                "to_template_count": selected_profile[
                    "normalized_tail_template_count"
                ],
                "template_count_gain": selected_profile[
                    "normalized_tail_template_count"
                ]
                - source["normalized_tail_template_count"],
                "from_template_lift_min": source["template_lift_count_min"],
                "to_template_lift_min": selected_profile["template_lift_count_min"],
                "template_lift_min_change": selected_profile[
                    "template_lift_count_min"
                ]
                - source["template_lift_count_min"],
                "from_rank104_template_match_count": source[
                    "rank104_template_match_count"
                ],
                "to_rank104_template_match_count": selected_profile[
                    "rank104_template_match_count"
                ],
                "rank104_template_match_gain": selected_profile[
                    "rank104_template_match_count"
                ]
                - source["rank104_template_match_count"],
                "endpoint_9_path_count_change": selected_profile[
                    "tail_entry_9_path_count"
                ]
                - source["tail_entry_9_path_count"],
                "endpoint_10_path_count_change": selected_profile[
                    "tail_entry_10_path_count"
                ]
                - source["tail_entry_10_path_count"],
                "endpoint_11_path_count_change": selected_profile[
                    "tail_entry_11_path_count"
                ]
                - source["tail_entry_11_path_count"],
                "endpoint_13_path_count_change": selected_profile[
                    "tail_entry_13_path_count"
                ]
                - source["tail_entry_13_path_count"],
                "six_template_retention_gain": selected_profile[
                    "six_template_retention_flag"
                ]
                - source["six_template_retention_flag"],
                "delta4_reintroduced_flag": int(
                    selected_profile["metric_gromov_delta_twice"] == 4
                ),
            }
        )

    lower_profiles = [profile_by_id[witness_id] for witness_id in LOWER_VARIATION_WITNESS_IDS]
    lift_gaps = [
        row["variation_gap_to_six_template_lift"] for row in lift_edge_rows
    ]
    observable_values = {
        "lower_variation_witness_count": len(lower_profiles),
        "lower_variation_min": min(
            row["trace_signature_total_variation"] for row in lower_profiles
        ),
        "lower_variation_max": max(
            row["trace_signature_total_variation"] for row in lower_profiles
        ),
        "lower_variation_template_count_min": min(
            row["normalized_tail_template_count"] for row in lower_profiles
        ),
        "lower_variation_template_count_max": max(
            row["normalized_tail_template_count"] for row in lower_profiles
        ),
        "lower_variation_endpoint11_only_count": sum(
            row["tail_entry_11_path_count"] == TARGET_CLOSED_PATH_COUNT
            and row["tail_entry_other_path_count"] == 0
            for row in lower_profiles
        ),
        "lower_variation_endpoint13_only_count": sum(
            row["tail_entry_13_path_count"] == TARGET_CLOSED_PATH_COUNT
            and row["tail_entry_other_path_count"] == 0
            for row in lower_profiles
        ),
        "selected_lift_witness_id": SELECTED_SIX_TEMPLATE_WITNESS_ID,
        "selected_lift_variation": selected_profile[
            "trace_signature_total_variation"
        ],
        "selected_lift_template_count": selected_profile[
            "normalized_tail_template_count"
        ],
        "selected_lift_delta_twice": selected_profile["metric_gromov_delta_twice"],
        "selected_lift_closed_paths": selected_profile[
            "first_return_closed_path_count"
        ],
        "min_variation_gap_to_six_template_lift": min(lift_gaps),
        "max_variation_gap_to_six_template_lift": max(lift_gaps),
        "lift_reintroduces_delta4_count": sum(
            row["delta4_reintroduced_flag"] for row in lift_edge_rows
        ),
        "lower_variation_direct_six_template_lift_count": sum(
            row["six_template_retention_flag"] for row in lower_profiles
        ),
        "lower_variation_rank104_template_match_max": max(
            row["rank104_template_match_count"] for row in lower_profiles
        ),
        "selected_lift_endpoint_9_count": selected_profile[
            "tail_entry_9_path_count"
        ],
        "selected_lift_endpoint_10_count": selected_profile[
            "tail_entry_10_path_count"
        ],
        "selected_lift_endpoint_11_count": selected_profile[
            "tail_entry_11_path_count"
        ],
        "selected_lift_endpoint_13_count": selected_profile[
            "tail_entry_13_path_count"
        ],
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

    profile_table = table_from_rows(PROFILE_COLUMNS, profile_rows)
    template_table = table_from_rows(TEMPLATE_COLUMNS, template_rows)
    lift_edge_table = table_from_rows(LIFT_EDGE_COLUMNS, lift_edge_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "carrier_splice_report_certified": carrier_splice_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_REALIZATION_CERTIFIED",
        "carrier_splice_certificate_certified": carrier_splice_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_REALIZATION_CERTIFIED",
        "carrier_splice_schema_available": carrier_splice_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization@1",
        "optimality_report_certified": optimality_report.get("status")
        == CARRIER_SPLICE_OPTIMALITY_STATUS,
        "optimality_certificate_certified": optimality_certificate.get("status")
        == CARRIER_SPLICE_OPTIMALITY_STATUS,
        "optimality_schema_available": optimality_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_optimality@1",
        "parent_frontier_declares_lower_variation_witnesses_0_1": [
            row["splice_witness_id"]
            for row in exact_rows_parent
            if row["trace_signature_total_variation"]
            < SELECTED_SIX_TEMPLATE_VARIATION
        ]
        == list(LOWER_VARIATION_WITNESS_IDS),
        "parent_frontier_declares_unique_six_template_lift_2": [
            row["splice_witness_id"]
            for row in exact_rows_parent
            if row["six_template_retention_flag"] == 1
        ]
        == [SELECTED_SIX_TEMPLATE_WITNESS_ID],
        "selected_word_and_trace_match_parent": row_word(selected_row)
        == SELECTED_SIX_TEMPLATE_WORD
        and row_trace(selected_row) == SELECTED_SIX_TEMPLATE_TRACE,
        "profiles_are_all_exact_24_path_delta2": all(
            row["first_return_closed_path_count"] == TARGET_CLOSED_PATH_COUNT
            and row["metric_gromov_delta_twice"] == TARGET_DELTA_TWICE
            for row in profile_rows
        ),
        "lower_profiles_are_collapsed_not_six_template": all(
            row["normalized_tail_template_count"] < 6
            and row["six_template_retention_flag"] == 0
            for row in lower_profiles
        ),
        "witness_0_collapses_into_two_endpoint_11_templates": profile_by_id[0][
            "normalized_tail_template_count"
        ]
        == 2
        and profile_by_id[0]["template_lift_count_min"] == 12
        and profile_by_id[0]["template_lift_count_max"] == 12
        and profile_by_id[0]["tail_entry_11_path_count"] == 24,
        "witness_1_collapses_into_three_endpoint_13_templates": profile_by_id[1][
            "normalized_tail_template_count"
        ]
        == 3
        and profile_by_id[1]["template_lift_count_min"] == 8
        and profile_by_id[1]["template_lift_count_max"] == 8
        and profile_by_id[1]["tail_entry_13_path_count"] == 24,
        "selected_lift_retains_six_templates_with_uniform_four_lifts": selected_profile[
            "normalized_tail_template_count"
        ]
        == 6
        and selected_profile["template_lift_count_min"] == 4
        and selected_profile["template_lift_count_max"] == 4
        and selected_profile["rank104_template_match_count"] == 6,
        "selected_lift_endpoint_distribution_is_12_4_8": (
            selected_profile["tail_entry_9_path_count"],
            selected_profile["tail_entry_10_path_count"],
            selected_profile["tail_entry_11_path_count"],
            selected_profile["tail_entry_13_path_count"],
        )
        == (12, 4, 8, 0),
        "six_template_lift_preserves_delta2_and_24_paths": all(
            row["delta_preserved_flag"] == 1
            and row["closed_path_preserved_flag"] == 1
            and row["delta4_reintroduced_flag"] == 0
            for row in lift_edge_rows
        ),
        "variation_gap_to_six_template_lift_is_26_and_24": lift_gaps
        == [26, 24],
        "selected_template_rows_match_parent_selected_template_rows": [
            (
                row["parent_rank104_template_id"],
                row["splice_path_count"],
                tuple(row[column] for column in TAIL_CARRIER_COLUMNS),
            )
            for row in template_rows
            if row["splice_witness_id"] == SELECTED_SIX_TEMPLATE_WITNESS_ID
        ]
        == [
            (
                row["normalized_tail_template_id"],
                row["selected_splice_path_count"],
                tuple(row[column] for column in TAIL_CARRIER_COLUMNS),
            )
            for row in selected_templates_parent
        ],
        "profile_table_shape_matches_codebook": tuple(profile_table.shape)
        == (3, len(PROFILE_COLUMNS)),
        "template_table_shape_matches_codebook": tuple(template_table.shape)
        == (11, len(TEMPLATE_COLUMNS)),
        "lift_edge_table_shape_matches_codebook": tuple(lift_edge_table.shape)
        == (2, len(LIFT_EDGE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "lower_variation_witness_ids": list(LOWER_VARIATION_WITNESS_IDS),
        "lower_variation_profiles": [
            {
                "splice_witness_id": row["splice_witness_id"],
                "variation": row["trace_signature_total_variation"],
                "template_count": row["normalized_tail_template_count"],
                "lift_count_min": row["template_lift_count_min"],
                "lift_count_max": row["template_lift_count_max"],
                "endpoint_11_count": row["tail_entry_11_path_count"],
                "endpoint_13_count": row["tail_entry_13_path_count"],
            }
            for row in lower_profiles
        ],
        "selected_six_template_lift_witness_id": SELECTED_SIX_TEMPLATE_WITNESS_ID,
        "selected_six_template_lift_word": list(SELECTED_SIX_TEMPLATE_WORD),
        "selected_six_template_lift_trace": list(SELECTED_SIX_TEMPLATE_TRACE),
        "selected_six_template_lift_variation": selected_profile[
            "trace_signature_total_variation"
        ],
        "selected_six_template_lift_endpoint_distribution": {
            "9": selected_profile["tail_entry_9_path_count"],
            "10": selected_profile["tail_entry_10_path_count"],
            "11": selected_profile["tail_entry_11_path_count"],
            "13": selected_profile["tail_entry_13_path_count"],
        },
        "lift_gap_from_witness_0": lift_edge_rows[0][
            "variation_gap_to_six_template_lift"
        ],
        "lift_gap_from_witness_1": lift_edge_rows[1][
            "variation_gap_to_six_template_lift"
        ],
        "profile_table_sha256": sha_array(profile_table),
        "template_table_sha256": sha_array(template_table),
        "lift_edge_table_sha256": sha_array(lift_edge_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    obstruction = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction@1",
        "object": "d20",
        "comparison_rule": {
            "parent": CARRIER_SPLICE_OPTIMALITY_REPORT.relative_to(ROOT).as_posix(),
            "lower_variation_frontier": list(LOWER_VARIATION_WITNESS_IDS),
            "six_template_lift": SELECTED_SIX_TEMPLATE_WITNESS_ID,
            "tested_invariants": [
                "metric_gromov_delta_twice",
                "first_return_closed_path_count",
                "normalized tail-template distribution",
                "tail-entry carrier distribution",
                "trace-signature total variation",
            ],
        },
        "summary": {
            "lower_variation_witness_count": len(lower_profiles),
            "selected_six_template_lift_witness_id": SELECTED_SIX_TEMPLATE_WITNESS_ID,
            "lift_reintroduces_delta4_count": observable_values[
                "lift_reintroduces_delta4_count"
            ],
            "min_variation_gap_to_six_template_lift": observable_values[
                "min_variation_gap_to_six_template_lift"
            ],
            "max_variation_gap_to_six_template_lift": observable_values[
                "max_variation_gap_to_six_template_lift"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_LOWER_VARIATION_LIFT_OBSTRUCTION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "witness 0 is an exact 24-path delta2 repair at variation 197, but its tail collapses to two endpoint-11 templates at 12 lifts each",
            "witness 1 is an exact 24-path delta2 repair at variation 199, but its tail collapses to three endpoint-13 templates at 8 lifts each",
            "the six-template lift is witness 2 at variation 223 and it preserves delta2 and 24 closures",
            "therefore the obstruction to lifting the lower-variation rows is variation cost, not hyperbolicity relapse",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The exact lower-variation carrier splices are collapsed-tail repairs. "
            "Witness 0 has variation 197 and witness 1 has variation 199, with "
            "24 first-return closures and delta_twice 2, but they compress the "
            "rank104 tail into two endpoint-11 templates or three endpoint-13 "
            "templates. The unique six-template lift is witness 2 at variation "
            "223. It keeps delta_twice 2 and 24 closures, so the lift obstruction "
            "is the +26/+24 variation price of restoring the six-template tail "
            "distribution rather than a relapse to delta_twice 4."
        ),
        "stage_protocol": {
            "draft": "reuse the certified carrier-splice frontier and isolate the two lower-variation exact rows",
            "witness": "recompute first-return tail templates for witnesses 0, 1, and selected lift 2",
            "coherence": "compare endpoint distributions, rank104 template matches, lift gaps, delta, and closure counts",
            "closure": "certify that six-template lifting preserves delta2 but costs variation 26 or 24",
            "emit": "emit lower-variation profiles, tail templates, lift edges, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "carrier_splice_report": input_entry(
                CARRIER_SPLICE_REPORT,
                {
                    "status": carrier_splice_report.get("status"),
                    "certificate_sha256": carrier_splice_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "carrier_splice_json": input_entry(CARRIER_SPLICE_JSON),
            "carrier_splice_exact_witnesses": input_entry(
                CARRIER_SPLICE_EXACT_WITNESSES
            ),
            "carrier_splice_selected_templates": input_entry(
                CARRIER_SPLICE_SELECTED_TEMPLATES
            ),
            "carrier_splice_tables": input_entry(CARRIER_SPLICE_TABLES),
            "carrier_splice_certificate": input_entry(CARRIER_SPLICE_CERTIFICATE),
            "carrier_splice_optimality_report": input_entry(
                CARRIER_SPLICE_OPTIMALITY_REPORT,
                {
                    "status": optimality_report.get("status"),
                    "certificate_sha256": optimality_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "carrier_splice_optimality_json": input_entry(
                CARRIER_SPLICE_OPTIMALITY_JSON
            ),
            "carrier_splice_optimality_frontier": input_entry(
                CARRIER_SPLICE_OPTIMALITY_FRONTIER
            ),
            "carrier_splice_optimality_classes": input_entry(
                CARRIER_SPLICE_OPTIMALITY_CLASSES
            ),
            "carrier_splice_optimality_observables": input_entry(
                CARRIER_SPLICE_OPTIMALITY_OBSERVABLES
            ),
            "carrier_splice_optimality_tables": input_entry(
                CARRIER_SPLICE_OPTIMALITY_TABLES
            ),
            "carrier_splice_optimality_certificate": input_entry(
                CARRIER_SPLICE_OPTIMALITY_CERTIFICATE
            ),
            "endpoint_split_templates": input_entry(ENDPOINT_SPLIT_TEMPLATES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction.json"
            ),
            "aperture_closure_tail_lower_variation_profiles_csv": relpath(
                OUT_DIR / "aperture_closure_tail_lower_variation_profiles.csv"
            ),
            "aperture_closure_tail_lower_variation_templates_csv": relpath(
                OUT_DIR / "aperture_closure_tail_lower_variation_templates.csv"
            ),
            "aperture_closure_tail_lower_variation_lift_edges_csv": relpath(
                OUT_DIR / "aperture_closure_tail_lower_variation_lift_edges.csv"
            ),
            "aperture_closure_tail_lower_variation_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_lower_variation_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the exact lower-variation witness 0 and 1 tail-template profiles",
                "that both lower-variation profiles are collapsed tails rather than six-template lifts",
                "that the selected six-template lift preserves delta2 and 24 first-return closures",
                "that the observed lift gaps from the lower rows are +26 and +24 variation",
            ],
            "does_not_certify_because_not_required": [
                "global optimality outside the parent bounded pre-tail search",
                "the existence or nonexistence of intermediate partial splitters below variation 223",
                "carrier splices outside the certified exact 24-path delta2 frontier",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Search for a partial template splitter between witnesses 0/1 and "
            "witness 2: split endpoint-11 or endpoint-13 collapsed templates into "
            "4-lift subtemplates while keeping variation below 223 and "
            "delta_twice 2."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified carrier-splice realization and optimality artifacts",
            "recompute closed tail templates for witnesses 0, 1, and 2",
            "check lower-variation collapsed-tail profiles",
            "check six-template lift delta and closure preservation",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction": obstruction,
        "aperture_closure_tail_lower_variation_profiles_csv": csv_text(
            PROFILE_COLUMNS,
            profile_rows,
        ),
        "aperture_closure_tail_lower_variation_templates_csv": csv_text(
            TEMPLATE_COLUMNS,
            template_rows,
        ),
        "aperture_closure_tail_lower_variation_lift_edges_csv": csv_text(
            LIFT_EDGE_COLUMNS,
            lift_edge_rows,
        ),
        "aperture_closure_tail_lower_variation_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "profile_table": profile_table,
        "template_table": template_table,
        "lift_edge_table": lift_edge_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_lower_variation_profiles.csv").write_text(
        payloads["aperture_closure_tail_lower_variation_profiles_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_lower_variation_templates.csv").write_text(
        payloads["aperture_closure_tail_lower_variation_templates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_lower_variation_lift_edges.csv").write_text(
        payloads["aperture_closure_tail_lower_variation_lift_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_lower_variation_observables.csv").write_text(
        payloads["aperture_closure_tail_lower_variation_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_tables.npz",
        profile_table=payloads["profile_table"],
        template_table=payloads["template_table"],
        lift_edge_table=payloads["lift_edge_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate"
        ],
    )
    write_json(OUT_DIR / "report.json", payloads["report"])
    write_json(OUT_DIR / "manifest.json", payloads["manifest"])
    update_index(payloads["report"])


def main() -> None:
    payloads = build_payloads()
    write_payloads(payloads)
    report = payloads["report"]
    print(
        json.dumps(
            {
                "status": report["status"],
                "all_checks_pass": report["all_checks_pass"],
                "report": relpath(OUT_DIR / "report.json"),
                "manifest": relpath(OUT_DIR / "manifest.json"),
                "certificate_sha256": report["certificate_sha256"],
                "witness": report["witness"],
                "next_highest_yield_item": report["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
