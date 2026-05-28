from __future__ import annotations

import csv
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        CELL_COMPLEX_EDGES,
        FIXED_TAIL_ATOMS,
        OUT_DIR as ENDPOINT_SPLIT_DIR,
        SHARED_TAIL_WORD,
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        tail_slices,
        write_json,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search import (
        OUT_DIR as PREFIX_CHORD_DIR,
        STATUS as PREFIX_CHORD_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        RANK104_OUTLIER_ID,
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
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_endpoint_split import (
        CELL_COMPLEX_EDGES,
        FIXED_TAIL_ATOMS,
        OUT_DIR as ENDPOINT_SPLIT_DIR,
        SHARED_TAIL_WORD,
        SYMBOLIC_ALPHABET_CSV,
        TAIL_ATOM_COLUMNS,
        TAIL_CARRIER_COLUMNS,
        TAIL_EDGE_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        input_entry,
        relpath,
        self_hash,
        sha_array,
        table_from_rows,
        tail_slices,
        write_json,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_prefix_chord_search import (
        OUT_DIR as PREFIX_CHORD_DIR,
        STATUS as PREFIX_CHORD_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        RANK104_OUTLIER_ID,
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
    "c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_REALIZATION_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

PREFIX_CHORD_REPORT = PREFIX_CHORD_DIR / "report.json"
PREFIX_CHORD_JSON = (
    PREFIX_CHORD_DIR
    / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search.json"
)
PREFIX_CHORD_CANDIDATES = (
    PREFIX_CHORD_DIR / "aperture_closure_tail_prefix_chord_candidates.csv"
)
PREFIX_CHORD_TABLES = (
    PREFIX_CHORD_DIR
    / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_tables.npz"
)
PREFIX_CHORD_CERTIFICATE = (
    PREFIX_CHORD_DIR
    / "signature_boundary_spine_aperture_closure_tail_prefix_chord_search_certificate.json"
)
ENDPOINT_SPLIT_REPORT = ENDPOINT_SPLIT_DIR / "report.json"
ENDPOINT_SPLIT_TEMPLATES = (
    ENDPOINT_SPLIT_DIR / "aperture_closure_tail_templates.csv"
)
ENDPOINT_SPLIT_CERTIFICATE = (
    ENDPOINT_SPLIT_DIR
    / "signature_boundary_spine_aperture_closure_tail_endpoint_split_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization.py"
)

PREFIX_FIXED = (2, 1)
PRE_TAIL_LENGTH_MIN = 5
PRE_TAIL_LENGTH_MAX = 8
SYMBOL_ALPHABET = (1, 2, 3, 4, 5)
TARGET_DELTA_TWICE = 2
TARGET_CLOSED_PATH_COUNT = 24
RANK104_WORD = (2, 1, 3, 4, 5, 5, 2, 1, 4, 5)
SELECTED_SIX_TEMPLATE_WORD = (
    2,
    1,
    3,
    4,
    5,
    1,
    4,
    5,
    5,
    2,
    1,
    4,
    5,
)
SELECTED_SPLICE_INSERTION = (1, 4, 5)
SELECTED_SIX_TEMPLATE_TRACE = (
    48,
    42,
    27,
    31,
    50,
    34,
    54,
    45,
    29,
    28,
    34,
    44,
)

MAX_WORD_LENGTH = 13
MAX_TRACE_NODES = 16
WORD_COLUMNS = [f"word_symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_TRACE_NODES)]

EXACT_WITNESS_COLUMNS = [
    "splice_witness_id",
    "word_length",
    "pre_tail_symbol_count",
    "inserted_symbol_count_over_rank104",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "full_carrier_path_count",
    "normalized_tail_template_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "fixed_tail_atom_sequence_flag",
    "has_chord_31_28_flag",
    "has_chord_50_34_flag",
    "rank104_prefix_27_31_50_flag",
    "shared_rewrite_tail_suffix_flag",
    "six_template_retention_flag",
    "selected_min_variation_flag",
    "selected_six_template_retention_flag",
]

SELECTED_TEMPLATE_COLUMNS = [
    "splice_witness_id",
    "normalized_tail_template_id",
    "tail_entry_carrier_id",
    "selected_splice_path_count",
    "rank104_original_path_count",
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
    "bounded_search_space_count": 0,
    "trace_valid_count": 1,
    "trace_contains_repair_chord_count": 2,
    "trace_contains_31_28_count": 3,
    "trace_contains_50_34_count": 4,
    "closed_positive_chord_count": 5,
    "exact_24_delta2_splice_count": 6,
    "exact_31_28_splice_count": 7,
    "exact_50_34_splice_count": 8,
    "exact_both_chords_splice_count": 9,
    "rank104_prefix_exact_count": 10,
    "shared_rewrite_tail_exact_count": 11,
    "six_template_retention_exact_count": 12,
    "selected_six_template_word_length": 13,
    "selected_six_template_variation": 14,
    "selected_six_template_full_path_count": 15,
    "selected_six_template_closed_path_count": 16,
    "selected_six_template_delta_twice": 17,
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


def padded(values: tuple[int, ...] | list[int], length: int) -> tuple[int, ...]:
    base = tuple(int(value) for value in values)
    return base + tuple(-1 for _ in range(length - len(base)))


def contains_undirected_edge(trace: tuple[int, ...], left: int, right: int) -> bool:
    edge = {int(left), int(right)}
    return any({source, target} == edge for source, target in zip(trace, trace[1:]))


def endpoint_counts(
    templates: Counter[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
) -> Counter[int]:
    counts: Counter[int] = Counter()
    for template, path_count in templates.items():
        counts[int(template[0][0])] += int(path_count)
    return counts


def build_payloads() -> dict[str, Any]:
    prefix_report = load_json(PREFIX_CHORD_REPORT)
    prefix_certificate = load_json(PREFIX_CHORD_CERTIFICATE)
    endpoint_report = load_json(ENDPOINT_SPLIT_REPORT)
    endpoint_certificate = load_json(ENDPOINT_SPLIT_CERTIFICATE)
    endpoint_templates = read_int_dict_csv(ENDPOINT_SPLIT_TEMPLATES)

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

    stats: Counter[str] = Counter()
    exact_rows_raw: list[dict[str, Any]] = []
    selected_templates_raw: list[
        tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], int]
    ] = []

    for pre_tail_length in range(PRE_TAIL_LENGTH_MIN, PRE_TAIL_LENGTH_MAX + 1):
        for prefix in product(SYMBOL_ALPHABET, repeat=pre_tail_length):
            if prefix[: len(PREFIX_FIXED)] != PREFIX_FIXED:
                continue
            stats["bounded_search_space_count"] += 1
            word = tuple(int(value) for value in prefix) + SHARED_TAIL_WORD
            raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
            stats["trace_valid_count"] += 1
            trace = tuple(int(value) for value in trace_nodes)
            has_31_28 = contains_undirected_edge(trace, 31, 28)
            has_50_34 = contains_undirected_edge(trace, 50, 34)
            if not (has_31_28 or has_50_34):
                continue
            stats["trace_contains_repair_chord_count"] += 1
            stats["trace_contains_31_28_count"] += int(has_31_28)
            stats["trace_contains_50_34_count"] += int(has_50_34)
            states = carrier_paths(word, carrier_adjacency)
            closed_states = first_return_closed(states)
            if closed_states:
                stats["closed_positive_chord_count"] += 1
            if (
                int(metrics["metric_gromov_delta_twice"]) != TARGET_DELTA_TWICE
                or len(closed_states) != TARGET_CLOSED_PATH_COUNT
            ):
                continue
            stats["exact_24_delta2_splice_count"] += 1
            stats["exact_31_28_splice_count"] += int(has_31_28)
            stats["exact_50_34_splice_count"] += int(has_50_34)
            stats["exact_both_chords_splice_count"] += int(has_31_28 and has_50_34)

            tail_start = len(word) - len(SHARED_TAIL_WORD)
            template_counts = Counter(
                tail_slices(state, tail_start) for state in closed_states
            )
            lift_counts = sorted(int(value) for value in template_counts.values())
            endpoints = endpoint_counts(template_counts)
            fixed_tail = all(
                tuple(template[2]) == FIXED_TAIL_ATOMS for template in template_counts
            )
            rank104_prefix = trace[:5] == (48, 42, 27, 31, 50)
            shared_tail_suffix = trace[-len(SHARED_REWRITE_TAIL) :] == SHARED_REWRITE_TAIL
            six_template_retention = (
                len(template_counts) == 6 and lift_counts == [4, 4, 4, 4, 4, 4]
            )
            stats["rank104_prefix_exact_count"] += int(rank104_prefix)
            stats["shared_rewrite_tail_exact_count"] += int(shared_tail_suffix)
            stats["six_template_retention_exact_count"] += int(six_template_retention)
            exact_rows_raw.append(
                {
                    "word": word,
                    "trace": trace,
                    "metrics": {key: int(value) for key, value in metrics.items()},
                    "full_carrier_path_count": len(states),
                    "first_return_closed_path_count": len(closed_states),
                    "normalized_tail_template_count": len(template_counts),
                    "template_lift_count_min": min(lift_counts),
                    "template_lift_count_max": max(lift_counts),
                    "tail_entry_9_path_count": endpoints[9],
                    "tail_entry_10_path_count": endpoints[10],
                    "tail_entry_11_path_count": endpoints[11],
                    "fixed_tail_atom_sequence_flag": int(fixed_tail),
                    "has_chord_31_28_flag": int(has_31_28),
                    "has_chord_50_34_flag": int(has_50_34),
                    "rank104_prefix_27_31_50_flag": int(rank104_prefix),
                    "shared_rewrite_tail_suffix_flag": int(shared_tail_suffix),
                    "six_template_retention_flag": int(six_template_retention),
                    "last_raw_window_rank": int(raw_windows[-1]["trace_window_rank"]),
                    "template_counts": template_counts,
                }
            )

    exact_rows_raw.sort(
        key=lambda row: (
            row["metrics"]["trace_signature_total_variation"],
            len(row["word"]),
            row["word"],
        )
    )
    selected_min_variation_word = exact_rows_raw[0]["word"]
    selected_six_row = next(
        row for row in exact_rows_raw if row["word"] == SELECTED_SIX_TEMPLATE_WORD
    )
    for template, count in sorted(
        selected_six_row["template_counts"].items(),
        key=lambda item: item[0][0],
    ):
        selected_templates_raw.append((*template, int(count)))

    exact_rows = []
    for witness_id, row in enumerate(exact_rows_raw):
        word = row["word"]
        trace = row["trace"]
        exact_rows.append(
            {
                "splice_witness_id": witness_id,
                "word_length": len(word),
                "pre_tail_symbol_count": len(word) - len(SHARED_TAIL_WORD),
                "inserted_symbol_count_over_rank104": len(word) - len(RANK104_WORD),
                **{
                    column: value
                    for column, value in zip(WORD_COLUMNS, padded(word, MAX_WORD_LENGTH))
                },
                "trace_node_count": len(trace),
                **{
                    column: value
                    for column, value in zip(
                        TRACE_NODE_COLUMNS,
                        padded(trace, MAX_TRACE_NODES),
                    )
                },
                "metric_gromov_delta_twice": row["metrics"][
                    "metric_gromov_delta_twice"
                ],
                "trace_signature_total_variation": row["metrics"][
                    "trace_signature_total_variation"
                ],
                "first_return_closed_path_count": row[
                    "first_return_closed_path_count"
                ],
                "full_carrier_path_count": row["full_carrier_path_count"],
                "normalized_tail_template_count": row[
                    "normalized_tail_template_count"
                ],
                "template_lift_count_min": row["template_lift_count_min"],
                "template_lift_count_max": row["template_lift_count_max"],
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "fixed_tail_atom_sequence_flag": row[
                    "fixed_tail_atom_sequence_flag"
                ],
                "has_chord_31_28_flag": row["has_chord_31_28_flag"],
                "has_chord_50_34_flag": row["has_chord_50_34_flag"],
                "rank104_prefix_27_31_50_flag": row[
                    "rank104_prefix_27_31_50_flag"
                ],
                "shared_rewrite_tail_suffix_flag": row[
                    "shared_rewrite_tail_suffix_flag"
                ],
                "six_template_retention_flag": row["six_template_retention_flag"],
                "selected_min_variation_flag": int(
                    word == selected_min_variation_word
                ),
                "selected_six_template_retention_flag": int(
                    word == SELECTED_SIX_TEMPLATE_WORD
                ),
            }
        )

    selected_witness_id = next(
        row["splice_witness_id"]
        for row in exact_rows
        if row["selected_six_template_retention_flag"] == 1
    )
    selected_template_rows = []
    endpoint_template_by_tail = {
        tuple(row[column] for column in TAIL_CARRIER_COLUMNS): row
        for row in endpoint_templates
    }
    for template_id, (carriers, edge_ids, atom_ids, count) in enumerate(
        selected_templates_raw
    ):
        parent = endpoint_template_by_tail[tuple(carriers)]
        selected_template_rows.append(
            {
                "splice_witness_id": selected_witness_id,
                "normalized_tail_template_id": template_id,
                "tail_entry_carrier_id": carriers[0],
                "selected_splice_path_count": count,
                "rank104_original_path_count": parent[
                    "rank104_outlier_path_count"
                ],
                **{
                    column: value
                    for column, value in zip(TAIL_CARRIER_COLUMNS, carriers)
                },
                **{column: value for column, value in zip(TAIL_EDGE_COLUMNS, edge_ids)},
                **{column: value for column, value in zip(TAIL_ATOM_COLUMNS, atom_ids)},
            }
        )

    observable_values = {
        key: stats[key]
        for key in [
            "bounded_search_space_count",
            "trace_valid_count",
            "trace_contains_repair_chord_count",
            "trace_contains_31_28_count",
            "trace_contains_50_34_count",
            "closed_positive_chord_count",
            "exact_24_delta2_splice_count",
            "exact_31_28_splice_count",
            "exact_50_34_splice_count",
            "exact_both_chords_splice_count",
            "rank104_prefix_exact_count",
            "shared_rewrite_tail_exact_count",
            "six_template_retention_exact_count",
        ]
    }
    observable_values.update(
        {
            "selected_six_template_word_length": len(SELECTED_SIX_TEMPLATE_WORD),
            "selected_six_template_variation": selected_six_row["metrics"][
                "trace_signature_total_variation"
            ],
            "selected_six_template_full_path_count": selected_six_row[
                "full_carrier_path_count"
            ],
            "selected_six_template_closed_path_count": selected_six_row[
                "first_return_closed_path_count"
            ],
            "selected_six_template_delta_twice": selected_six_row["metrics"][
                "metric_gromov_delta_twice"
            ],
        }
    )
    observable_rows = [
        {
            "observable_id": index,
            "observable_code": OBSERVABLE_CODES[key],
            "value_x1e12": int(value) * 10**12,
            "aux_id": -1,
        }
        for index, (key, value) in enumerate(observable_values.items())
    ]

    exact_table = table_from_rows(EXACT_WITNESS_COLUMNS, exact_rows)
    selected_template_table = table_from_rows(
        SELECTED_TEMPLATE_COLUMNS,
        selected_template_rows,
    )
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    selected_exact_row = exact_rows[selected_witness_id]
    checks = {
        "prefix_chord_report_certified": prefix_report.get("status")
        == PREFIX_CHORD_STATUS,
        "prefix_chord_certificate_certified": prefix_certificate.get("status")
        == PREFIX_CHORD_STATUS,
        "endpoint_split_report_certified": endpoint_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ENDPOINT_SPLIT_CERTIFIED",
        "endpoint_split_certificate_certified": endpoint_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_ENDPOINT_SPLIT_CERTIFIED",
        "bounded_search_space_is_19500": stats["bounded_search_space_count"]
        == 19_500,
        "all_bounded_words_have_valid_trace": stats["trace_valid_count"]
        == 19_500,
        "repair_chord_trace_count_is_1726": stats[
            "trace_contains_repair_chord_count"
        ]
        == 1_726,
        "closed_positive_chord_count_is_240": stats["closed_positive_chord_count"]
        == 240,
        "eleven_exact_24_path_delta2_splices_exist": len(exact_rows) == 11,
        "both_repair_chords_are_carrier_realizable": stats[
            "exact_31_28_splice_count"
        ]
        == 6
        and stats["exact_50_34_splice_count"] == 6,
        "one_exact_splice_contains_both_repair_chords": stats[
            "exact_both_chords_splice_count"
        ]
        == 1,
        "unique_exact_splice_retains_six_rank104_tail_templates": stats[
            "six_template_retention_exact_count"
        ]
        == 1
        and stats["shared_rewrite_tail_exact_count"] == 1,
        "selected_six_template_word_is_expected_splice": tuple(
            selected_exact_row[column] for column in WORD_COLUMNS[: len(SELECTED_SIX_TEMPLATE_WORD)]
        )
        == SELECTED_SIX_TEMPLATE_WORD,
        "selected_six_template_trace_is_expected": tuple(
            selected_exact_row[column]
            for column in TRACE_NODE_COLUMNS[: selected_exact_row["trace_node_count"]]
        )
        == SELECTED_SIX_TEMPLATE_TRACE,
        "selected_six_template_reaches_delta2_and_24_paths": selected_exact_row[
            "metric_gromov_delta_twice"
        ]
        == 2
        and selected_exact_row["first_return_closed_path_count"] == 24,
        "selected_six_template_preserves_rank104_tail_distribution": [
            row["selected_splice_path_count"] for row in selected_template_rows
        ]
        == [4, 4, 4, 4, 4, 4]
        and [
            row["rank104_original_path_count"] for row in selected_template_rows
        ]
        == [4, 4, 4, 4, 4, 4],
        "selected_six_template_endpoint_counts_are_12_4_8": (
            selected_exact_row["tail_entry_9_path_count"],
            selected_exact_row["tail_entry_10_path_count"],
            selected_exact_row["tail_entry_11_path_count"],
        )
        == (12, 4, 8),
        "all_exact_splices_use_fixed_tail_atoms": all(
            row["fixed_tail_atom_sequence_flag"] == 1 for row in exact_rows
        ),
        "exact_table_shape_matches_codebook": tuple(exact_table.shape)
        == (11, len(EXACT_WITNESS_COLUMNS)),
        "selected_template_table_shape_matches_codebook": tuple(
            selected_template_table.shape
        )
        == (6, len(SELECTED_TEMPLATE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "rank104_outlier_id": RANK104_OUTLIER_ID,
        "bounded_search_space_count": stats["bounded_search_space_count"],
        "exact_24_path_delta2_splice_count": len(exact_rows),
        "exact_31_28_splice_count": stats["exact_31_28_splice_count"],
        "exact_50_34_splice_count": stats["exact_50_34_splice_count"],
        "selected_six_template_splice_witness_id": selected_witness_id,
        "selected_six_template_word": list(SELECTED_SIX_TEMPLATE_WORD),
        "selected_six_template_inserted_symbols": list(SELECTED_SPLICE_INSERTION),
        "selected_six_template_trace": list(SELECTED_SIX_TEMPLATE_TRACE),
        "selected_six_template_delta_twice": 2,
        "selected_six_template_closed_path_count": 24,
        "selected_six_template_full_carrier_path_count": selected_exact_row[
            "full_carrier_path_count"
        ],
        "selected_six_template_variation": selected_exact_row[
            "trace_signature_total_variation"
        ],
        "selected_six_template_endpoint_counts": {
            "9": selected_exact_row["tail_entry_9_path_count"],
            "10": selected_exact_row["tail_entry_10_path_count"],
            "11": selected_exact_row["tail_entry_11_path_count"],
        },
        "exact_witness_table_sha256": sha_array(exact_table),
        "selected_template_table_sha256": sha_array(selected_template_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    splice_realization = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization@1",
        "object": "d20",
        "comparison_rule": {
            "rank104_outlier": RANK104_OUTLIER_ID,
            "source_rank104_word": list(RANK104_WORD),
            "shared_tail_word": list(SHARED_TAIL_WORD),
            "target_delta_twice": TARGET_DELTA_TWICE,
            "target_closed_path_count": TARGET_CLOSED_PATH_COUNT,
        },
        "summary": {
            "exact_24_path_delta2_splice_count": len(exact_rows),
            "selected_six_template_word": list(SELECTED_SIX_TEMPLATE_WORD),
            "selected_six_template_trace": list(SELECTED_SIX_TEMPLATE_TRACE),
            "selected_six_template_closed_path_count": 24,
            "selected_six_template_delta_twice": 2,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CARRIER_SPLICE_REALIZATION_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "both bridge-to-baseline repair chords are realized by actual carrier-word splices in the bounded search",
            "eleven bounded splices have 24 first-return closures and delta_twice 2",
            "the selected splice inserts x1,x4,x5 before the shared tail and realizes 50--34 as a carrier-preserving chord",
            "that selected splice uniquely preserves the six rank104 tail templates with four lifts each",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The metric repair is carrier-realizable. In the bounded splice "
            "search preserving the symbolic tail x5,x2,x1,x4,x5, there are "
            "11 actual carrier words with 24 first-return closures and "
            "delta_twice 2. The unique one that also preserves the six "
            "rank104 tail templates inserts x1,x4,x5 before the shared tail: "
            "x2,x1,x3,x4,x5,x1,x4,x5,x5,x2,x1,x4,x5. Its trace is "
            "48->42->27->31->50->34->54->45->29->28->34->44, so it realizes "
            "the 50--34 repair chord and then rejoins the shared rewrite tail."
        ),
        "stage_protocol": {
            "draft": "start from the certified prefix-chord search and demand an actual carrier word",
            "witness": "enumerate bounded pre-tail splices with fixed prefix 2,1 and fixed tail 5,2,1,4,5",
            "coherence": "recompute rewrite traces, carrier paths, first-return closures, and tail-template counts",
            "closure": "certify the exact splices with 24 closures and delta_twice 2, including the six-template-retaining splice",
            "emit": "emit exact splice witnesses, selected template counts, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "prefix_chord_report": input_entry(
                PREFIX_CHORD_REPORT,
                {
                    "status": prefix_report.get("status"),
                    "certificate_sha256": prefix_report.get("certificate_sha256"),
                },
            ),
            "prefix_chord_json": input_entry(PREFIX_CHORD_JSON),
            "prefix_chord_candidates": input_entry(PREFIX_CHORD_CANDIDATES),
            "prefix_chord_tables": input_entry(PREFIX_CHORD_TABLES),
            "prefix_chord_certificate": input_entry(PREFIX_CHORD_CERTIFICATE),
            "endpoint_split_report": input_entry(
                ENDPOINT_SPLIT_REPORT,
                {
                    "status": endpoint_report.get("status"),
                    "certificate_sha256": endpoint_report.get("certificate_sha256"),
                },
            ),
            "endpoint_split_templates": input_entry(ENDPOINT_SPLIT_TEMPLATES),
            "endpoint_split_certificate": input_entry(ENDPOINT_SPLIT_CERTIFICATE),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "symbolic_associativity_csv": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization.json"
            ),
            "aperture_closure_tail_carrier_splice_exact_witnesses_csv": relpath(
                OUT_DIR / "aperture_closure_tail_carrier_splice_exact_witnesses.csv"
            ),
            "aperture_closure_tail_carrier_splice_selected_templates_csv": relpath(
                OUT_DIR / "aperture_closure_tail_carrier_splice_selected_templates.csv"
            ),
            "aperture_closure_tail_carrier_splice_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_carrier_splice_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "bounded carrier-word realization of the 31--28 and 50--34 repair chords",
                "existence of 11 bounded splices with 24 first-return closures and delta_twice 2",
                "the selected x1,x4,x5 insertion that realizes 50--34 and rejoins the shared rewrite tail",
                "retention of the six rank104 tail templates and 12/4/8 endpoint counts for the selected splice",
            ],
            "does_not_certify_because_not_required": [
                "global optimality outside pre-tail lengths 5 through 8",
                "variation optimality under the six-template-retention constraint beyond the declared bounded search",
                "edit costs above three inserted pre-tail symbols",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Optimize the carrier-realized splice frontier: search whether any "
            "six-template-retaining 24-path splice with delta_twice 2 has "
            "lower signature variation than 223, or prove 223 is the bounded "
            "minimum under the same tail-retention constraints."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified prefix-chord and endpoint-split artifacts",
            "enumerate bounded carrier-word splices preserving the shared tail",
            "recompute rewrite traces and first-return carrier closures",
            "check the 11 exact 24-path delta2 splices and selected six-template splice",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization": splice_realization,
        "aperture_closure_tail_carrier_splice_exact_witnesses_csv": csv_text(
            EXACT_WITNESS_COLUMNS,
            exact_rows,
        ),
        "aperture_closure_tail_carrier_splice_selected_templates_csv": csv_text(
            SELECTED_TEMPLATE_COLUMNS,
            selected_template_rows,
        ),
        "aperture_closure_tail_carrier_splice_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "exact_witness_table": exact_table,
        "selected_template_table": selected_template_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_carrier_splice_exact_witnesses.csv").write_text(
        payloads["aperture_closure_tail_carrier_splice_exact_witnesses_csv"],
        encoding="utf-8",
    )
    (
        OUT_DIR / "aperture_closure_tail_carrier_splice_selected_templates.csv"
    ).write_text(
        payloads["aperture_closure_tail_carrier_splice_selected_templates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_carrier_splice_observables.csv").write_text(
        payloads["aperture_closure_tail_carrier_splice_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_tables.npz",
        exact_witness_table=payloads["exact_witness_table"],
        selected_template_table=payloads["selected_template_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate"
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
