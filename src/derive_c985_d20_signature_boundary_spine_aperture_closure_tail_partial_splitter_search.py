from __future__ import annotations

import csv
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        PREFIX_FIXED,
        PRE_TAIL_LENGTH_MAX,
        PRE_TAIL_LENGTH_MIN,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SHARED_TAIL_WORD,
        SYMBOL_ALPHABET,
        contains_undirected_edge,
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
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction import (
        OUT_DIR as LOWER_LIFT_DIR,
        STATUS as LOWER_LIFT_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        REWRITE_COMPLEX_EDGES,
        SHARED_REWRITE_TAIL,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        associativity_lookup,
        build_trace,
        csv_text,
        edge_key,
        read_int_csv,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        PREFIX_FIXED,
        PRE_TAIL_LENGTH_MAX,
        PRE_TAIL_LENGTH_MIN,
        SELECTED_SIX_TEMPLATE_TRACE,
        SELECTED_SIX_TEMPLATE_WORD,
        SHARED_TAIL_WORD,
        SYMBOL_ALPHABET,
        contains_undirected_edge,
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
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction import (
        OUT_DIR as LOWER_LIFT_DIR,
        STATUS as LOWER_LIFT_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        REWRITE_COMPLEX_EDGES,
        SHARED_REWRITE_TAIL,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        associativity_lookup,
        build_trace,
        csv_text,
        edge_key,
        read_int_csv,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_PARTIAL_SPLITTER_SEARCH_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

LOWER_LIFT_REPORT = LOWER_LIFT_DIR / "report.json"
LOWER_LIFT_JSON = (
    LOWER_LIFT_DIR
    / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction.json"
)
LOWER_LIFT_PROFILES = (
    LOWER_LIFT_DIR / "aperture_closure_tail_lower_variation_profiles.csv"
)
LOWER_LIFT_TEMPLATES = (
    LOWER_LIFT_DIR / "aperture_closure_tail_lower_variation_templates.csv"
)
LOWER_LIFT_EDGES = (
    LOWER_LIFT_DIR / "aperture_closure_tail_lower_variation_lift_edges.csv"
)
LOWER_LIFT_OBSERVABLES = (
    LOWER_LIFT_DIR / "aperture_closure_tail_lower_variation_observables.csv"
)
LOWER_LIFT_TABLES = (
    LOWER_LIFT_DIR
    / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_tables.npz"
)
LOWER_LIFT_CERTIFICATE = (
    LOWER_LIFT_DIR
    / "signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search.py"
)

TARGET_DELTA_TWICE = 2
TARGET_CLOSED_PATH_COUNT = 24
SELECTED_SIX_TEMPLATE_VARIATION = 223
MAX_WORD_LENGTH = 13
MAX_TRACE_NODES = 16
WORD_COLUMNS = [f"word_symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_TRACE_NODES)]

FRONTIER_COLUMNS = [
    "partial_candidate_id",
    "word_length",
    "pre_tail_symbol_count",
    "trace_node_count",
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "closure_excess_abs_from_24",
    "normalized_tail_template_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "four_lift_template_count",
    "any_four_lift_flag",
    "all_four_lift_flag",
    "exact_24_flag",
    "exact_24_any_four_lift_flag",
    "all_four_ge24_flag",
    "best_oversplitter_flag",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
    "has_chord_31_28_flag",
    "has_chord_50_34_flag",
    "rank104_prefix_27_31_50_flag",
    "shared_rewrite_tail_suffix_flag",
]

PROFILE_KIND_CODES = {
    "lower_exact_collapsed": 0,
    "sub223_all_four_oversplitter": 1,
    "selected_six_template_lift": 2,
}

PROFILE_COLUMNS = [
    "profile_id",
    "profile_kind_code",
    "partial_candidate_id",
    "word_length",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "four_lift_template_count",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
]

TEMPLATE_COLUMNS = [
    "partial_candidate_id",
    "normalized_tail_template_id",
    "tail_entry_carrier_id",
    "splice_path_count",
    "rank104_template_match_flag",
    *TAIL_CARRIER_COLUMNS,
    *TAIL_EDGE_COLUMNS,
    *TAIL_ATOM_COLUMNS,
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "sub223_delta2_closed_positive_count": 0,
    "sub223_exact24_count": 1,
    "sub223_exact24_any_four_lift_count": 2,
    "sub223_exact24_partial_splitter_count": 3,
    "sub223_any_four_lift_count": 4,
    "sub223_all_four_lift_count": 5,
    "sub223_all_four_ge24_count": 6,
    "best_oversplitter_count": 7,
    "best_oversplitter_min_variation": 8,
    "best_oversplitter_max_variation": 9,
    "best_oversplitter_closed_path_count": 10,
    "best_oversplitter_template_count": 11,
    "best_oversplitter_closure_excess": 12,
    "best_oversplitter_endpoint_9_count": 13,
    "best_oversplitter_endpoint_10_count": 14,
    "best_oversplitter_endpoint_11_count": 15,
    "best_oversplitter_endpoint_13_count": 16,
    "selected_six_template_variation": 17,
    "selected_six_template_closed_paths": 18,
    "selected_six_template_template_count": 19,
    "selected_gap_over_best_oversplitter_min": 20,
    "selected_gap_over_best_oversplitter_max": 21,
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


def padded(values: tuple[int, ...], length: int) -> tuple[int, ...]:
    return values + tuple(-1 for _ in range(length - len(values)))


def endpoint_counts(
    templates: Counter[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
) -> Counter[int]:
    counts: Counter[int] = Counter()
    for template, path_count in templates.items():
        counts[int(template[0][0])] += int(path_count)
    return counts


def build_rank104_template_set() -> set[tuple[int, ...]]:
    rows = read_int_dict_csv(LOWER_LIFT_TEMPLATES)
    return {
        tuple(row[column] for column in TAIL_CARRIER_COLUMNS)
        for row in rows
        if row["splice_witness_id"] == 2
    }


def scan_candidates() -> list[dict[str, Any]]:
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)
    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    carrier_adjacency, _carriers = build_carrier_adjacency(
        read_int_csv(CELL_COMPLEX_EDGES),
        atom_to_symbol,
    )
    assoc_by_word = associativity_lookup(read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV))
    rewrite_edge_by_pair = {
        edge_key(row["source_node_id"], row["target_node_id"]): row
        for row in read_int_csv(REWRITE_COMPLEX_EDGES)
    }

    rows: list[dict[str, Any]] = []
    for pre_tail_length in range(PRE_TAIL_LENGTH_MIN, PRE_TAIL_LENGTH_MAX + 1):
        for prefix in product(SYMBOL_ALPHABET, repeat=pre_tail_length):
            if prefix[: len(PREFIX_FIXED)] != PREFIX_FIXED:
                continue
            word = tuple(int(value) for value in prefix) + SHARED_TAIL_WORD
            _raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
            variation = int(metrics["trace_signature_total_variation"])
            delta_twice = int(metrics["metric_gromov_delta_twice"])
            if delta_twice != TARGET_DELTA_TWICE or variation >= SELECTED_SIX_TEMPLATE_VARIATION:
                continue
            trace = tuple(int(value) for value in trace_nodes)
            has_31_28 = contains_undirected_edge(trace, 31, 28)
            has_50_34 = contains_undirected_edge(trace, 50, 34)
            if not (has_31_28 or has_50_34):
                continue
            states = carrier_paths(word, carrier_adjacency)
            closed_states = first_return_closed(states)
            if not closed_states:
                continue
            tail_start = len(word) - len(SHARED_TAIL_WORD)
            templates = Counter(tail_slices(state, tail_start) for state in closed_states)
            lift_counts = sorted(int(value) for value in templates.values())
            endpoints = endpoint_counts(templates)
            rows.append(
                {
                    "word": word,
                    "trace": trace,
                    "metric_gromov_delta_twice": delta_twice,
                    "trace_signature_total_variation": variation,
                    "first_return_closed_path_count": len(closed_states),
                    "normalized_tail_template_count": len(templates),
                    "template_lift_count_min": min(lift_counts),
                    "template_lift_count_max": max(lift_counts),
                    "four_lift_template_count": sum(
                        int(value == 4) for value in lift_counts
                    ),
                    "any_four_lift_flag": int(4 in lift_counts),
                    "all_four_lift_flag": int(all(value == 4 for value in lift_counts)),
                    "tail_entry_9_path_count": endpoints[9],
                    "tail_entry_10_path_count": endpoints[10],
                    "tail_entry_11_path_count": endpoints[11],
                    "tail_entry_13_path_count": endpoints[13],
                    "has_chord_31_28_flag": int(has_31_28),
                    "has_chord_50_34_flag": int(has_50_34),
                    "rank104_prefix_27_31_50_flag": int(
                        trace[:5] == (48, 42, 27, 31, 50)
                    ),
                    "shared_rewrite_tail_suffix_flag": int(
                        trace[-len(SHARED_REWRITE_TAIL) :] == SHARED_REWRITE_TAIL
                    ),
                    "templates": templates,
                }
            )
    rows.sort(
        key=lambda row: (
            row["trace_signature_total_variation"],
            len(row["word"]),
            row["word"],
        )
    )
    return rows


def build_payloads() -> dict[str, Any]:
    lower_report = load_json(LOWER_LIFT_REPORT)
    lower_json = load_json(LOWER_LIFT_JSON)
    lower_certificate = load_json(LOWER_LIFT_CERTIFICATE)
    lower_profiles = read_int_dict_csv(LOWER_LIFT_PROFILES)
    rank104_template_set = build_rank104_template_set()
    scanned_rows = scan_candidates()

    all_four_ge24_indices = [
        index
        for index, row in enumerate(scanned_rows)
        if row["all_four_lift_flag"] == 1
        and row["first_return_closed_path_count"] >= TARGET_CLOSED_PATH_COUNT
    ]
    best_oversplitter_indices = list(all_four_ge24_indices)
    frontier_rows = []
    for candidate_id, row in enumerate(scanned_rows):
        exact_24 = row["first_return_closed_path_count"] == TARGET_CLOSED_PATH_COUNT
        frontier_rows.append(
            {
                "partial_candidate_id": candidate_id,
                "word_length": len(row["word"]),
                "pre_tail_symbol_count": len(row["word"]) - len(SHARED_TAIL_WORD),
                "trace_node_count": len(row["trace"]),
                "metric_gromov_delta_twice": row["metric_gromov_delta_twice"],
                "trace_signature_total_variation": row[
                    "trace_signature_total_variation"
                ],
                "first_return_closed_path_count": row[
                    "first_return_closed_path_count"
                ],
                "closure_excess_abs_from_24": abs(
                    row["first_return_closed_path_count"] - TARGET_CLOSED_PATH_COUNT
                ),
                "normalized_tail_template_count": row[
                    "normalized_tail_template_count"
                ],
                "template_lift_count_min": row["template_lift_count_min"],
                "template_lift_count_max": row["template_lift_count_max"],
                "four_lift_template_count": row["four_lift_template_count"],
                "any_four_lift_flag": row["any_four_lift_flag"],
                "all_four_lift_flag": row["all_four_lift_flag"],
                "exact_24_flag": int(exact_24),
                "exact_24_any_four_lift_flag": int(
                    exact_24 and row["any_four_lift_flag"] == 1
                ),
                "all_four_ge24_flag": int(candidate_id in all_four_ge24_indices),
                "best_oversplitter_flag": int(candidate_id in best_oversplitter_indices),
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "tail_entry_13_path_count": row["tail_entry_13_path_count"],
                "has_chord_31_28_flag": row["has_chord_31_28_flag"],
                "has_chord_50_34_flag": row["has_chord_50_34_flag"],
                "rank104_prefix_27_31_50_flag": row[
                    "rank104_prefix_27_31_50_flag"
                ],
                "shared_rewrite_tail_suffix_flag": row[
                    "shared_rewrite_tail_suffix_flag"
                ],
            }
        )

    lower_profile_by_variation = {
        row["trace_signature_total_variation"]: row for row in lower_profiles
    }
    selected_profile = next(
        row for row in lower_profiles if row["selected_six_template_lift_flag"] == 1
    )

    profile_specs: list[tuple[int, str, int | None, dict[str, Any]]] = [
        (0, "lower_exact_collapsed", 10, scanned_rows[10]),
        (1, "lower_exact_collapsed", 12, scanned_rows[12]),
        (2, "sub223_all_four_oversplitter", 19, scanned_rows[19]),
        (3, "sub223_all_four_oversplitter", 20, scanned_rows[20]),
    ]
    selected_profile_row = {
        "word": SELECTED_SIX_TEMPLATE_WORD,
        "trace": SELECTED_SIX_TEMPLATE_TRACE,
        "metric_gromov_delta_twice": TARGET_DELTA_TWICE,
        "trace_signature_total_variation": selected_profile[
            "trace_signature_total_variation"
        ],
        "first_return_closed_path_count": selected_profile[
            "first_return_closed_path_count"
        ],
        "normalized_tail_template_count": selected_profile[
            "normalized_tail_template_count"
        ],
        "four_lift_template_count": selected_profile[
            "normalized_tail_template_count"
        ],
        "tail_entry_9_path_count": selected_profile["tail_entry_9_path_count"],
        "tail_entry_10_path_count": selected_profile["tail_entry_10_path_count"],
        "tail_entry_11_path_count": selected_profile["tail_entry_11_path_count"],
        "tail_entry_13_path_count": selected_profile["tail_entry_13_path_count"],
    }
    profile_specs.append((4, "selected_six_template_lift", -1, selected_profile_row))

    profile_rows = []
    for profile_id, kind, candidate_id, row in profile_specs:
        profile_rows.append(
            {
                "profile_id": profile_id,
                "profile_kind_code": PROFILE_KIND_CODES[kind],
                "partial_candidate_id": int(candidate_id)
                if candidate_id is not None
                else -1,
                "word_length": len(row["word"]),
                **{
                    column: value
                    for column, value in zip(
                        WORD_COLUMNS,
                        padded(row["word"], MAX_WORD_LENGTH),
                    )
                },
                "trace_node_count": len(row["trace"]),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(row["trace"], MAX_TRACE_NODES),
                    )
                },
                "metric_gromov_delta_twice": row["metric_gromov_delta_twice"],
                "trace_signature_total_variation": row[
                    "trace_signature_total_variation"
                ],
                "first_return_closed_path_count": row[
                    "first_return_closed_path_count"
                ],
                "normalized_tail_template_count": row[
                    "normalized_tail_template_count"
                ],
                "four_lift_template_count": row["four_lift_template_count"],
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "tail_entry_13_path_count": row["tail_entry_13_path_count"],
            }
        )

    template_rows = []
    for candidate_id in best_oversplitter_indices:
        templates = scanned_rows[candidate_id]["templates"]
        for template_id, (template, count) in enumerate(
            sorted(templates.items(), key=lambda item: item[0][0])
        ):
            carriers, edge_ids, atom_ids = template
            template_rows.append(
                {
                    "partial_candidate_id": candidate_id,
                    "normalized_tail_template_id": template_id,
                    "tail_entry_carrier_id": int(carriers[0]),
                    "splice_path_count": int(count),
                    "rank104_template_match_flag": int(
                        tuple(carriers) in rank104_template_set
                    ),
                    **{
                        column: value
                        for column, value in zip(TAIL_CARRIER_COLUMNS, carriers)
                    },
                    **{column: value for column, value in zip(TAIL_EDGE_COLUMNS, edge_ids)},
                    **{column: value for column, value in zip(TAIL_ATOM_COLUMNS, atom_ids)},
                }
            )

    exact24_rows = [
        row for row in frontier_rows if row["exact_24_flag"] == 1
    ]
    best_oversplitter_rows = [
        frontier_rows[index] for index in best_oversplitter_indices
    ]
    observable_values = {
        "sub223_delta2_closed_positive_count": len(frontier_rows),
        "sub223_exact24_count": len(exact24_rows),
        "sub223_exact24_any_four_lift_count": sum(
            row["exact_24_any_four_lift_flag"] for row in exact24_rows
        ),
        "sub223_exact24_partial_splitter_count": sum(
            row["exact_24_any_four_lift_flag"] and row["normalized_tail_template_count"] > 3
            for row in exact24_rows
        ),
        "sub223_any_four_lift_count": sum(
            row["any_four_lift_flag"] for row in frontier_rows
        ),
        "sub223_all_four_lift_count": sum(
            row["all_four_lift_flag"] for row in frontier_rows
        ),
        "sub223_all_four_ge24_count": len(best_oversplitter_rows),
        "best_oversplitter_count": len(best_oversplitter_rows),
        "best_oversplitter_min_variation": min(
            row["trace_signature_total_variation"] for row in best_oversplitter_rows
        ),
        "best_oversplitter_max_variation": max(
            row["trace_signature_total_variation"] for row in best_oversplitter_rows
        ),
        "best_oversplitter_closed_path_count": min(
            row["first_return_closed_path_count"] for row in best_oversplitter_rows
        ),
        "best_oversplitter_template_count": min(
            row["normalized_tail_template_count"] for row in best_oversplitter_rows
        ),
        "best_oversplitter_closure_excess": min(
            row["closure_excess_abs_from_24"] for row in best_oversplitter_rows
        ),
        "best_oversplitter_endpoint_9_count": best_oversplitter_rows[0][
            "tail_entry_9_path_count"
        ],
        "best_oversplitter_endpoint_10_count": best_oversplitter_rows[0][
            "tail_entry_10_path_count"
        ],
        "best_oversplitter_endpoint_11_count": best_oversplitter_rows[0][
            "tail_entry_11_path_count"
        ],
        "best_oversplitter_endpoint_13_count": best_oversplitter_rows[0][
            "tail_entry_13_path_count"
        ],
        "selected_six_template_variation": selected_profile[
            "trace_signature_total_variation"
        ],
        "selected_six_template_closed_paths": selected_profile[
            "first_return_closed_path_count"
        ],
        "selected_six_template_template_count": selected_profile[
            "normalized_tail_template_count"
        ],
        "selected_gap_over_best_oversplitter_min": selected_profile[
            "trace_signature_total_variation"
        ]
        - max(row["trace_signature_total_variation"] for row in best_oversplitter_rows),
        "selected_gap_over_best_oversplitter_max": selected_profile[
            "trace_signature_total_variation"
        ]
        - min(row["trace_signature_total_variation"] for row in best_oversplitter_rows),
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

    frontier_table = table_from_rows(FRONTIER_COLUMNS, frontier_rows)
    profile_table = table_from_rows(PROFILE_COLUMNS, profile_rows)
    template_table = table_from_rows(TEMPLATE_COLUMNS, template_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "lower_lift_report_certified": lower_report.get("status") == LOWER_LIFT_STATUS,
        "lower_lift_certificate_certified": lower_certificate.get("status")
        == LOWER_LIFT_STATUS,
        "lower_lift_schema_available": lower_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_closure_tail_lower_variation_lift_obstruction@1",
        "sub223_delta2_closed_positive_count_is_22": len(frontier_rows) == 22,
        "sub223_exact24_rows_are_collapsed_witnesses_0_1": [
            (
                row["trace_signature_total_variation"],
                row["normalized_tail_template_count"],
                row["template_lift_count_min"],
                row["template_lift_count_max"],
                row["four_lift_template_count"],
            )
            for row in exact24_rows
        ]
        == [(197, 2, 12, 12, 0), (199, 3, 8, 8, 0)],
        "no_sub223_exact24_partial_splitter_exists": observable_values[
            "sub223_exact24_partial_splitter_count"
        ]
        == 0,
        "sub223_all_four_ge24_rows_are_two_28_path_oversplitters": [
            (
                row["partial_candidate_id"],
                row["trace_signature_total_variation"],
                row["first_return_closed_path_count"],
                row["normalized_tail_template_count"],
                row["four_lift_template_count"],
            )
            for row in best_oversplitter_rows
        ]
        == [(19, 217, 28, 7, 7), (20, 219, 28, 7, 7)],
        "best_oversplitters_have_same_endpoint_distribution": all(
            (
                row["tail_entry_9_path_count"],
                row["tail_entry_10_path_count"],
                row["tail_entry_11_path_count"],
                row["tail_entry_13_path_count"],
            )
            == (12, 4, 0, 12)
            for row in best_oversplitter_rows
        ),
        "best_oversplitter_templates_have_fixed_tail_and_four_lifts": all(
            row["splice_path_count"] == 4
            and tuple(row[column] for column in TAIL_ATOM_COLUMNS) == FIXED_TAIL_ATOMS
            for row in template_rows
        ),
        "best_oversplitter_templates_are_four_rank104_plus_three_endpoint13": [
            sum(
                row["rank104_template_match_flag"]
                for row in template_rows
                if row["partial_candidate_id"] == candidate_id
            )
            for candidate_id in best_oversplitter_indices
        ]
        == [4, 4]
        and [
            sum(
                row["tail_entry_carrier_id"] == 13
                for row in template_rows
                if row["partial_candidate_id"] == candidate_id
            )
            for candidate_id in best_oversplitter_indices
        ]
        == [3, 3],
        "selected_profile_is_24_path_six_template_lift": (
            selected_profile["trace_signature_total_variation"],
            selected_profile["first_return_closed_path_count"],
            selected_profile["normalized_tail_template_count"],
        )
        == (223, 24, 6),
        "frontier_table_shape_matches_codebook": tuple(frontier_table.shape)
        == (22, len(FRONTIER_COLUMNS)),
        "profile_table_shape_matches_codebook": tuple(profile_table.shape)
        == (5, len(PROFILE_COLUMNS)),
        "template_table_shape_matches_codebook": tuple(template_table.shape)
        == (14, len(TEMPLATE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "sub223_delta2_closed_positive_count": len(frontier_rows),
        "sub223_exact24_candidate_ids": [
            row["partial_candidate_id"] for row in exact24_rows
        ],
        "sub223_exact24_partial_splitter_count": observable_values[
            "sub223_exact24_partial_splitter_count"
        ],
        "best_oversplitter_candidate_ids": [
            row["partial_candidate_id"] for row in best_oversplitter_rows
        ],
        "best_oversplitter_words": [
            list(scanned_rows[row["partial_candidate_id"]]["word"])
            for row in best_oversplitter_rows
        ],
        "best_oversplitter_traces": [
            list(scanned_rows[row["partial_candidate_id"]]["trace"])
            for row in best_oversplitter_rows
        ],
        "best_oversplitter_variations": [
            row["trace_signature_total_variation"] for row in best_oversplitter_rows
        ],
        "best_oversplitter_endpoint_distribution": {
            "9": best_oversplitter_rows[0]["tail_entry_9_path_count"],
            "10": best_oversplitter_rows[0]["tail_entry_10_path_count"],
            "11": best_oversplitter_rows[0]["tail_entry_11_path_count"],
            "13": best_oversplitter_rows[0]["tail_entry_13_path_count"],
        },
        "selected_six_template_word": list(SELECTED_SIX_TEMPLATE_WORD),
        "selected_six_template_trace": list(SELECTED_SIX_TEMPLATE_TRACE),
        "frontier_table_sha256": sha_array(frontier_table),
        "profile_table_sha256": sha_array(profile_table),
        "template_table_sha256": sha_array(template_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    splitter = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search@1",
        "object": "d20",
        "comparison_rule": {
            "parent": LOWER_LIFT_REPORT.relative_to(ROOT).as_posix(),
            "bounded_search_space": "fixed prefix x2,x1; pre-tail lengths 5..8; fixed tail x5,x2,x1,x4,x5",
            "filters": [
                "metric_gromov_delta_twice = 2",
                "trace_signature_total_variation < 223",
                "trace contains repair chord 31--28 or 50--34",
                "first_return_closed_path_count > 0",
            ],
        },
        "summary": {
            "sub223_delta2_closed_positive_count": len(frontier_rows),
            "sub223_exact24_partial_splitter_count": observable_values[
                "sub223_exact24_partial_splitter_count"
            ],
            "best_oversplitter_candidate_ids": witness[
                "best_oversplitter_candidate_ids"
            ],
            "best_oversplitter_closed_path_count": observable_values[
                "best_oversplitter_closed_path_count"
            ],
            "best_oversplitter_template_count": observable_values[
                "best_oversplitter_template_count"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_PARTIAL_SPLITTER_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "below variation 223, the bounded delta2 repair-chord search has 22 closed-positive rows",
            "the only exact 24-closure rows below 223 are the already certified collapsed witnesses 0 and 1, and neither has a four-lift template",
            "the closest all-four-lift rows with at least 24 closures are two 28-closure seven-template oversplitters at variations 217 and 219",
            "therefore the next obstruction is not absence of four-lift splitting, but trimming one excess endpoint-13 template while preserving delta2 below 223",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "In the same bounded carrier-splice search space, there is no "
            "sub-223 exact 24-closure partial splitter. The exact 24-closure "
            "rows below 223 remain only the collapsed witnesses at variations "
            "197 and 199, and neither has any four-lift template. However, "
            "four-lift splitting appears just below the six-template lift as "
            "two seven-template oversplitters: candidate 19 at variation 217 "
            "and candidate 20 at variation 219. Both have 28 first-return "
            "closures, all seven templates at four lifts, endpoint distribution "
            "12/4/0/12 over carriers 9/10/11/13, and delta_twice 2."
        ),
        "stage_protocol": {
            "draft": "scan the parent bounded pre-tail space below the selected six-template variation",
            "witness": "materialize all closed-positive delta2 repair-chord rows and the all-four-lift oversplitter templates",
            "coherence": "compare exact 24 rows, any-four rows, all-four rows, and selected lift profile",
            "closure": "certify no exact 24-closure partial splitter below 223 and isolate the two 28-closure oversplitters",
            "emit": "emit frontier, profiles, oversplitter templates, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "lower_lift_report": input_entry(
                LOWER_LIFT_REPORT,
                {
                    "status": lower_report.get("status"),
                    "certificate_sha256": lower_report.get("certificate_sha256"),
                },
            ),
            "lower_lift_json": input_entry(LOWER_LIFT_JSON),
            "lower_lift_profiles": input_entry(LOWER_LIFT_PROFILES),
            "lower_lift_templates": input_entry(LOWER_LIFT_TEMPLATES),
            "lower_lift_edges": input_entry(LOWER_LIFT_EDGES),
            "lower_lift_observables": input_entry(LOWER_LIFT_OBSERVABLES),
            "lower_lift_tables": input_entry(LOWER_LIFT_TABLES),
            "lower_lift_certificate": input_entry(LOWER_LIFT_CERTIFICATE),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "symbolic_associativity": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_partial_splitter_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search.json"
            ),
            "aperture_closure_tail_partial_splitter_frontier_csv": relpath(
                OUT_DIR / "aperture_closure_tail_partial_splitter_frontier.csv"
            ),
            "aperture_closure_tail_partial_splitter_profiles_csv": relpath(
                OUT_DIR / "aperture_closure_tail_partial_splitter_profiles.csv"
            ),
            "aperture_closure_tail_partial_splitter_templates_csv": relpath(
                OUT_DIR / "aperture_closure_tail_partial_splitter_templates.csv"
            ),
            "aperture_closure_tail_partial_splitter_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_partial_splitter_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the sub-223 delta2 closed-positive repair-chord frontier in the declared bounded search",
                "that no exact 24-closure partial splitter exists below variation 223 in that frontier",
                "that candidates 19 and 20 are the only all-four-lift rows with at least 24 closures below 223",
                "that those rows are 28-closure seven-template oversplitters with three endpoint-13 templates",
            ],
            "does_not_certify_because_not_required": [
                "searches at variation 223 or above",
                "global optimality outside the parent bounded pre-tail search",
                "whether one endpoint-13 template can be trimmed or redirected while preserving delta2",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Trim the two 28-closure oversplitters: try to delete or redirect one "
            "endpoint-13 four-lift template into the endpoint-11 pair so the row "
            "has exactly 24 closures, six templates, variation below 223, and "
            "delta_twice 2."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified lower-variation lift-obstruction artifacts",
            "scan the bounded sub-223 delta2 repair-chord frontier",
            "check exact 24-closure rows for four-lift partial splitting",
            "check all-four-lift ge24 oversplitters and their template profiles",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_partial_splitter_search": splitter,
        "aperture_closure_tail_partial_splitter_frontier_csv": csv_text(
            FRONTIER_COLUMNS,
            frontier_rows,
        ),
        "aperture_closure_tail_partial_splitter_profiles_csv": csv_text(
            PROFILE_COLUMNS,
            profile_rows,
        ),
        "aperture_closure_tail_partial_splitter_templates_csv": csv_text(
            TEMPLATE_COLUMNS,
            template_rows,
        ),
        "aperture_closure_tail_partial_splitter_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "frontier_table": frontier_table,
        "profile_table": profile_table,
        "template_table": template_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search.json",
        payloads["signature_boundary_spine_aperture_closure_tail_partial_splitter_search"],
    )
    (OUT_DIR / "aperture_closure_tail_partial_splitter_frontier.csv").write_text(
        payloads["aperture_closure_tail_partial_splitter_frontier_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_partial_splitter_profiles.csv").write_text(
        payloads["aperture_closure_tail_partial_splitter_profiles_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_partial_splitter_templates.csv").write_text(
        payloads["aperture_closure_tail_partial_splitter_templates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_partial_splitter_observables.csv").write_text(
        payloads["aperture_closure_tail_partial_splitter_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_tables.npz",
        frontier_table=payloads["frontier_table"],
        profile_table=payloads["profile_table"],
        template_table=payloads["template_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate"
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
