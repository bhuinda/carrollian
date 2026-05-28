from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
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
        SYMBOLIC_ALPHABET_CSV,
        TAIL_CARRIER_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search import (
        OUT_DIR as PARTIAL_SPLITTER_DIR,
        STATUS as PARTIAL_SPLITTER_STATUS,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        REWRITE_COMPLEX_EDGES,
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
        SYMBOLIC_ALPHABET_CSV,
        TAIL_CARRIER_COLUMNS,
        build_carrier_adjacency,
        carrier_paths,
        tail_slices,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search import (
        OUT_DIR as PARTIAL_SPLITTER_DIR,
        STATUS as PARTIAL_SPLITTER_STATUS,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_rewrite_node_lift import (
        REWRITE_COMPLEX_EDGES,
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
    "c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_TRIM_NEIGHBORHOOD_SEARCH_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

PARTIAL_SPLITTER_REPORT = PARTIAL_SPLITTER_DIR / "report.json"
PARTIAL_SPLITTER_JSON = (
    PARTIAL_SPLITTER_DIR
    / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search.json"
)
PARTIAL_SPLITTER_FRONTIER = (
    PARTIAL_SPLITTER_DIR / "aperture_closure_tail_partial_splitter_frontier.csv"
)
PARTIAL_SPLITTER_PROFILES = (
    PARTIAL_SPLITTER_DIR / "aperture_closure_tail_partial_splitter_profiles.csv"
)
PARTIAL_SPLITTER_TEMPLATES = (
    PARTIAL_SPLITTER_DIR / "aperture_closure_tail_partial_splitter_templates.csv"
)
PARTIAL_SPLITTER_OBSERVABLES = (
    PARTIAL_SPLITTER_DIR / "aperture_closure_tail_partial_splitter_observables.csv"
)
PARTIAL_SPLITTER_TABLES = (
    PARTIAL_SPLITTER_DIR
    / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_tables.npz"
)
PARTIAL_SPLITTER_CERTIFICATE = (
    PARTIAL_SPLITTER_DIR
    / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search.py"
)

SEED_WORDS = (
    (2, 1, 4, 3, 1, 5, 2, 5, 5, 2, 1, 4, 5),
    (2, 1, 4, 3, 1, 5, 5, 2, 1, 4, 5),
)
SYMBOL_ALPHABET = (1, 2, 3, 4, 5)
PREFIX_FIXED = (2, 1)
MIN_WORD_LENGTH = 8
MAX_WORD_LENGTH = 16
MAX_EDIT_RADIUS = 3
TARGET_DELTA_TWICE = 2
TARGET_VARIATION_STRICT_BOUND = 223
TARGET_CLOSED_PATH_COUNT = 24
TARGET_TEMPLATE_COUNT = 6

WORD_COLUMNS = [f"word_symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_WORD_LENGTH + 4)]

SHELL_COLUMNS = [
    "edit_radius",
    "word_count",
]

FRONTIER_COLUMNS = [
    "trim_candidate_id",
    "edit_radius",
    "word_length",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "closure_excess_abs_from_24",
    "normalized_tail_template_count",
    "template_excess_abs_from_6",
    "template_lift_count_min",
    "template_lift_count_max",
    "four_lift_template_count",
    "all_four_lift_flag",
    "exact24_flag",
    "six_template_flag",
    "exact24_six_template_flag",
    "exact24_six_all_four_flag",
    "all_four_ge24_flag",
    "best_all_four_ge24_flag",
    "best_six_template_gap_flag",
    "tail_entry_3_path_count",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
    "has_chord_31_28_flag",
    "has_chord_50_34_flag",
]

PROFILE_COLUMNS = [
    "profile_id",
    "trim_candidate_id",
    "profile_code",
    "edit_radius",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "normalized_tail_template_count",
    "template_lift_count_min",
    "template_lift_count_max",
    "four_lift_template_count",
    "tail_entry_3_path_count",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "neighborhood_total_word_count": 0,
    "radius0_word_count": 1,
    "radius1_word_count": 2,
    "radius2_word_count": 3,
    "radius3_word_count": 4,
    "trace_valid_word_count": 5,
    "metric_repair_candidate_count": 6,
    "closed_positive_candidate_count": 7,
    "exact24_count": 8,
    "six_template_count": 9,
    "exact24_six_template_count": 10,
    "exact24_six_all_four_count": 11,
    "all_four_ge24_count": 12,
    "best_all_four_ge24_count": 13,
    "best_all_four_ge24_closure_excess": 14,
    "best_all_four_ge24_template_count": 15,
    "best_six_template_count": 16,
    "best_six_template_closure_excess": 17,
    "best_six_template_min_variation": 18,
    "best_six_template_template_lift_min": 19,
    "best_six_template_template_lift_max": 20,
}

PROFILE_CODES = {
    "exact24": 0,
    "best_all_four_ge24": 1,
    "best_six_template_gap": 2,
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


def one_edit_neighbors(word: tuple[int, ...]):
    for index, symbol in enumerate(word):
        for replacement in SYMBOL_ALPHABET:
            if replacement != symbol:
                yield word[:index] + (replacement,) + word[index + 1 :]
    for index in range(len(word)):
        yield word[:index] + word[index + 1 :]
    for index in range(len(word) + 1):
        for symbol in SYMBOL_ALPHABET:
            yield word[:index] + (symbol,) + word[index:]


def build_neighborhood() -> tuple[dict[tuple[int, ...], int], list[dict[str, int]]]:
    radius_by_word = {word: 0 for word in SEED_WORDS}
    frontier = set(SEED_WORDS)
    shell_rows = [{"edit_radius": 0, "word_count": len(SEED_WORDS)}]
    for radius in range(1, MAX_EDIT_RADIUS + 1):
        next_frontier = set()
        for word in frontier:
            for neighbor in one_edit_neighbors(word):
                if (
                    MIN_WORD_LENGTH <= len(neighbor) <= MAX_WORD_LENGTH
                    and neighbor[: len(PREFIX_FIXED)] == PREFIX_FIXED
                    and neighbor not in radius_by_word
                ):
                    radius_by_word[neighbor] = radius
                    next_frontier.add(neighbor)
        shell_rows.append({"edit_radius": radius, "word_count": len(next_frontier)})
        frontier = next_frontier
    return radius_by_word, shell_rows


def endpoint_counts(
    templates: Counter[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
) -> Counter[int]:
    counts: Counter[int] = Counter()
    for template, path_count in templates.items():
        counts[int(template[0][0])] += int(path_count)
    return counts


def build_scan_rows() -> tuple[list[dict[str, Any]], list[dict[str, int]], dict[str, int]]:
    radius_by_word, shell_rows = build_neighborhood()
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
    rows: list[dict[str, Any]] = []
    for word, edit_radius in sorted(
        radius_by_word.items(),
        key=lambda item: (len(item[0]), item[0]),
    ):
        try:
            _raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
        except Exception:
            continue
        stats["trace_valid_word_count"] += 1
        variation = int(metrics["trace_signature_total_variation"])
        delta_twice = int(metrics["metric_gromov_delta_twice"])
        if delta_twice != TARGET_DELTA_TWICE or variation >= TARGET_VARIATION_STRICT_BOUND:
            continue
        trace = tuple(int(value) for value in trace_nodes)
        has_31_28 = contains_undirected_edge(trace, 31, 28)
        has_50_34 = contains_undirected_edge(trace, 50, 34)
        if not (has_31_28 or has_50_34):
            continue
        stats["metric_repair_candidate_count"] += 1
        states = carrier_paths(word, carrier_adjacency)
        closed_states = first_return_closed(states)
        if not closed_states:
            continue
        tail_start = max(0, len(word) - 5)
        templates = Counter(tail_slices(state, tail_start) for state in closed_states)
        lift_counts = sorted(int(value) for value in templates.values())
        endpoints = endpoint_counts(templates)
        rows.append(
            {
                "edit_radius": edit_radius,
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
                "all_four_lift_flag": int(all(value == 4 for value in lift_counts)),
                "tail_entry_3_path_count": endpoints[3],
                "tail_entry_9_path_count": endpoints[9],
                "tail_entry_10_path_count": endpoints[10],
                "tail_entry_11_path_count": endpoints[11],
                "tail_entry_13_path_count": endpoints[13],
                "has_chord_31_28_flag": int(has_31_28),
                "has_chord_50_34_flag": int(has_50_34),
                "lift_counts": tuple(lift_counts),
            }
        )
    return rows, shell_rows, dict(stats)


def build_payloads() -> dict[str, Any]:
    partial_report = load_json(PARTIAL_SPLITTER_REPORT)
    partial_json = load_json(PARTIAL_SPLITTER_JSON)
    partial_certificate = load_json(PARTIAL_SPLITTER_CERTIFICATE)
    partial_frontier = read_int_dict_csv(PARTIAL_SPLITTER_FRONTIER)
    seed_ids = [
        row["partial_candidate_id"]
        for row in partial_frontier
        if row["best_oversplitter_flag"] == 1
    ]

    scan_rows_raw, shell_rows, stats = build_scan_rows()
    exact24_raw = [
        row
        for row in scan_rows_raw
        if row["first_return_closed_path_count"] == TARGET_CLOSED_PATH_COUNT
    ]
    six_template_raw = [
        row
        for row in scan_rows_raw
        if row["normalized_tail_template_count"] == TARGET_TEMPLATE_COUNT
    ]
    exact24_six_raw = [
        row
        for row in exact24_raw
        if row["normalized_tail_template_count"] == TARGET_TEMPLATE_COUNT
    ]
    all_four_ge24_raw = [
        row
        for row in scan_rows_raw
        if row["all_four_lift_flag"] == 1
        and row["first_return_closed_path_count"] >= TARGET_CLOSED_PATH_COUNT
    ]
    best_all_four_closure_excess = min(
        abs(row["first_return_closed_path_count"] - TARGET_CLOSED_PATH_COUNT)
        for row in all_four_ge24_raw
    )
    best_all_four_template_count = min(
        row["normalized_tail_template_count"]
        for row in all_four_ge24_raw
        if abs(row["first_return_closed_path_count"] - TARGET_CLOSED_PATH_COUNT)
        == best_all_four_closure_excess
    )
    best_all_four_ge24_raw = [
        row
        for row in all_four_ge24_raw
        if abs(row["first_return_closed_path_count"] - TARGET_CLOSED_PATH_COUNT)
        == best_all_four_closure_excess
        and row["normalized_tail_template_count"] == best_all_four_template_count
    ]
    best_six_closure_excess = min(
        abs(row["first_return_closed_path_count"] - TARGET_CLOSED_PATH_COUNT)
        for row in six_template_raw
    )
    best_six_template_raw = [
        row
        for row in six_template_raw
        if abs(row["first_return_closed_path_count"] - TARGET_CLOSED_PATH_COUNT)
        == best_six_closure_excess
    ]

    best_all_four_words = {row["word"] for row in best_all_four_ge24_raw}
    best_six_words = {row["word"] for row in best_six_template_raw}
    frontier_rows = []
    for candidate_id, row in enumerate(
        sorted(
            scan_rows_raw,
            key=lambda value: (
                value["trace_signature_total_variation"],
                value["edit_radius"],
                len(value["word"]),
                value["word"],
            ),
        )
    ):
        exact24 = row["first_return_closed_path_count"] == TARGET_CLOSED_PATH_COUNT
        six_template = row["normalized_tail_template_count"] == TARGET_TEMPLATE_COUNT
        all_four = row["all_four_lift_flag"] == 1
        frontier_rows.append(
            {
                "trim_candidate_id": candidate_id,
                "edit_radius": row["edit_radius"],
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
                        padded(row["trace"], len(TRACE_NODE_COLUMNS)),
                    )
                },
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
                "template_excess_abs_from_6": abs(
                    row["normalized_tail_template_count"] - TARGET_TEMPLATE_COUNT
                ),
                "template_lift_count_min": row["template_lift_count_min"],
                "template_lift_count_max": row["template_lift_count_max"],
                "four_lift_template_count": row["four_lift_template_count"],
                "all_four_lift_flag": int(all_four),
                "exact24_flag": int(exact24),
                "six_template_flag": int(six_template),
                "exact24_six_template_flag": int(exact24 and six_template),
                "exact24_six_all_four_flag": int(exact24 and six_template and all_four),
                "all_four_ge24_flag": int(
                    all_four
                    and row["first_return_closed_path_count"]
                    >= TARGET_CLOSED_PATH_COUNT
                ),
                "best_all_four_ge24_flag": int(row["word"] in best_all_four_words),
                "best_six_template_gap_flag": int(row["word"] in best_six_words),
                "tail_entry_3_path_count": row["tail_entry_3_path_count"],
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "tail_entry_13_path_count": row["tail_entry_13_path_count"],
                "has_chord_31_28_flag": row["has_chord_31_28_flag"],
                "has_chord_50_34_flag": row["has_chord_50_34_flag"],
            }
        )

    frontier_by_word = {
        tuple(row[column] for column in WORD_COLUMNS if row[column] != -1): row
        for row in frontier_rows
    }
    profile_source_rows = []
    for row in exact24_raw:
        profile_source_rows.append(("exact24", frontier_by_word[row["word"]]))
    for row in best_all_four_ge24_raw:
        profile_source_rows.append(("best_all_four_ge24", frontier_by_word[row["word"]]))
    for row in best_six_template_raw:
        profile_source_rows.append(("best_six_template_gap", frontier_by_word[row["word"]]))
    seen_profile_keys = set()
    profile_rows = []
    for code_name, row in profile_source_rows:
        key = (code_name, row["trim_candidate_id"])
        if key in seen_profile_keys:
            continue
        seen_profile_keys.add(key)
        profile_rows.append(
            {
                "profile_id": len(profile_rows),
                "trim_candidate_id": row["trim_candidate_id"],
                "profile_code": PROFILE_CODES[code_name],
                "edit_radius": row["edit_radius"],
                "trace_signature_total_variation": row[
                    "trace_signature_total_variation"
                ],
                "first_return_closed_path_count": row[
                    "first_return_closed_path_count"
                ],
                "normalized_tail_template_count": row[
                    "normalized_tail_template_count"
                ],
                "template_lift_count_min": row["template_lift_count_min"],
                "template_lift_count_max": row["template_lift_count_max"],
                "four_lift_template_count": row["four_lift_template_count"],
                "tail_entry_3_path_count": row["tail_entry_3_path_count"],
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "tail_entry_13_path_count": row["tail_entry_13_path_count"],
            }
        )

    shell_table = table_from_rows(SHELL_COLUMNS, shell_rows)
    frontier_table = table_from_rows(FRONTIER_COLUMNS, frontier_rows)
    profile_table = table_from_rows(PROFILE_COLUMNS, profile_rows)

    shell_counts = {row["edit_radius"]: row["word_count"] for row in shell_rows}
    observable_values = {
        "neighborhood_total_word_count": sum(shell_counts.values()),
        "radius0_word_count": shell_counts[0],
        "radius1_word_count": shell_counts[1],
        "radius2_word_count": shell_counts[2],
        "radius3_word_count": shell_counts[3],
        "trace_valid_word_count": stats["trace_valid_word_count"],
        "metric_repair_candidate_count": stats["metric_repair_candidate_count"],
        "closed_positive_candidate_count": len(frontier_rows),
        "exact24_count": len(exact24_raw),
        "six_template_count": len(six_template_raw),
        "exact24_six_template_count": len(exact24_six_raw),
        "exact24_six_all_four_count": sum(
            row["exact24_six_all_four_flag"] for row in frontier_rows
        ),
        "all_four_ge24_count": len(all_four_ge24_raw),
        "best_all_four_ge24_count": len(best_all_four_ge24_raw),
        "best_all_four_ge24_closure_excess": best_all_four_closure_excess,
        "best_all_four_ge24_template_count": best_all_four_template_count,
        "best_six_template_count": len(best_six_template_raw),
        "best_six_template_closure_excess": best_six_closure_excess,
        "best_six_template_min_variation": min(
            row["trace_signature_total_variation"] for row in best_six_template_raw
        ),
        "best_six_template_template_lift_min": min(
            row["template_lift_count_min"] for row in best_six_template_raw
        ),
        "best_six_template_template_lift_max": max(
            row["template_lift_count_max"] for row in best_six_template_raw
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
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "partial_splitter_report_certified": partial_report.get("status")
        == PARTIAL_SPLITTER_STATUS,
        "partial_splitter_certificate_certified": partial_certificate.get("status")
        == PARTIAL_SPLITTER_STATUS,
        "partial_splitter_schema_available": partial_json.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_closure_tail_partial_splitter_search@1",
        "partial_splitter_declares_seed_oversplitters": seed_ids == [19, 20],
        "radius_shell_counts_are_expected": [
            row["word_count"] for row in shell_rows
        ]
        == [2, 185, 7712, 195967],
        "neighborhood_total_word_count_is_203866": observable_values[
            "neighborhood_total_word_count"
        ]
        == 203_866,
        "trace_valid_word_count_is_139238": stats["trace_valid_word_count"]
        == 139_238,
        "metric_repair_candidate_count_is_10792": stats[
            "metric_repair_candidate_count"
        ]
        == 10_792,
        "closed_positive_candidate_count_is_219": len(frontier_rows) == 219,
        "no_exact24_six_template_trim_exists": len(exact24_six_raw) == 0,
        "no_exact24_six_all_four_trim_exists": observable_values[
            "exact24_six_all_four_count"
        ]
        == 0,
        "exact24_rows_exist_but_never_have_six_templates": len(exact24_raw) == 14
        and all(
            row["normalized_tail_template_count"] != TARGET_TEMPLATE_COUNT
            for row in exact24_raw
        ),
        "six_template_rows_exist_but_never_have_24_closures": len(six_template_raw)
        == 37
        and all(
            row["first_return_closed_path_count"] != TARGET_CLOSED_PATH_COUNT
            for row in six_template_raw
        ),
        "best_all_four_ge24_rows_are_28_by_7": len(best_all_four_ge24_raw) == 8
        and all(
            row["first_return_closed_path_count"] == 28
            and row["normalized_tail_template_count"] == 7
            for row in best_all_four_ge24_raw
        ),
        "best_six_template_gap_is_32_closures": best_six_closure_excess == 8
        and all(
            row["first_return_closed_path_count"] == 32
            for row in best_six_template_raw
            if row["trace_signature_total_variation"] == 215
        ),
        "shell_table_shape_matches_codebook": tuple(shell_table.shape)
        == (4, len(SHELL_COLUMNS)),
        "frontier_table_shape_matches_codebook": tuple(frontier_table.shape)
        == (219, len(FRONTIER_COLUMNS)),
        "profile_table_shape_matches_codebook": profile_table.shape[1]
        == len(PROFILE_COLUMNS),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "seed_partial_candidate_ids": seed_ids,
        "seed_words": [list(word) for word in SEED_WORDS],
        "neighborhood_shell_counts": [row["word_count"] for row in shell_rows],
        "closed_positive_candidate_count": len(frontier_rows),
        "exact24_count": len(exact24_raw),
        "six_template_count": len(six_template_raw),
        "exact24_six_template_count": len(exact24_six_raw),
        "exact24_six_all_four_count": observable_values[
            "exact24_six_all_four_count"
        ],
        "best_all_four_ge24_profiles": [
            {
                "variation": row["trace_signature_total_variation"],
                "edit_radius": row["edit_radius"],
                "word": list(row["word"]),
                "closed_paths": row["first_return_closed_path_count"],
                "template_count": row["normalized_tail_template_count"],
            }
            for row in best_all_four_ge24_raw
        ],
        "best_six_template_closure_excess": best_six_closure_excess,
        "shell_table_sha256": sha_array(shell_table),
        "frontier_table_sha256": sha_array(frontier_table),
        "profile_table_sha256": sha_array(profile_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    trim = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search@1",
        "object": "d20",
        "comparison_rule": {
            "parent": PARTIAL_SPLITTER_REPORT.relative_to(ROOT).as_posix(),
            "seed_oversplitters": [list(word) for word in SEED_WORDS],
            "edit_radius": MAX_EDIT_RADIUS,
            "filters": [
                "word starts with x2,x1",
                "8 <= word_length <= 16",
                "metric_gromov_delta_twice = 2",
                "trace_signature_total_variation < 223",
                "trace contains repair chord 31--28 or 50--34",
                "first_return_closed_path_count > 0",
            ],
            "target": [
                "first_return_closed_path_count = 24",
                "normalized_tail_template_count = 6",
                "all retained templates have four lifts",
            ],
        },
        "summary": {
            "neighborhood_total_word_count": observable_values[
                "neighborhood_total_word_count"
            ],
            "closed_positive_candidate_count": len(frontier_rows),
            "exact24_six_all_four_count": observable_values[
                "exact24_six_all_four_count"
            ],
            "best_all_four_ge24_count": len(best_all_four_ge24_raw),
            "best_all_four_ge24_closure_excess": best_all_four_closure_excess,
            "best_six_template_closure_excess": best_six_closure_excess,
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_TRIM_NEIGHBORHOOD_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "radius-three local edits around the two certified oversplitters contain 203866 prefix-valid words",
            "after delta2, sub-223, repair-chord, and closed-positive filters, 219 candidates remain",
            "none has the requested exact 24 closures, six templates, and all-four lift profile",
            "the best all-four rows are still 28-closure seven-template oversplitters, while the closest six-template rows have at least 32 closures",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The local trim attempt fails through edit radius three around the "
            "two certified 28-closure oversplitters. The search covers 203,866 "
            "prefix-valid local words, keeps 10,792 sub-223 delta2 repair-chord "
            "candidates, and finds 219 closed-positive candidates. Fourteen "
            "rows have exactly 24 closures, but none has six templates. "
            "Thirty-seven rows have six templates, but none has exactly 24 "
            "closures. No row satisfies the exact 24 / six-template / all-four "
            "trim target. The nearest all-four rows remain 28-closure "
            "seven-template oversplitters; the nearest six-template rows have "
            "32 closures."
        ),
        "stage_protocol": {
            "draft": "seed the neighborhood with the two certified 28-closure oversplitters",
            "witness": "enumerate all prefix-valid words through edit radius three and evaluate delta, repair chords, closures, and tail-template lifts",
            "coherence": "compare exact-24 rows, six-template rows, and all-four ge24 rows against the trim target",
            "closure": "certify that no radius-three local trim reaches exact 24 closures, six templates, and all-four lifts below variation 223",
            "emit": "emit shell counts, frontier rows, profile rows, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "partial_splitter_report": input_entry(
                PARTIAL_SPLITTER_REPORT,
                {
                    "status": partial_report.get("status"),
                    "certificate_sha256": partial_report.get("certificate_sha256"),
                },
            ),
            "partial_splitter_json": input_entry(PARTIAL_SPLITTER_JSON),
            "partial_splitter_frontier": input_entry(PARTIAL_SPLITTER_FRONTIER),
            "partial_splitter_profiles": input_entry(PARTIAL_SPLITTER_PROFILES),
            "partial_splitter_templates": input_entry(PARTIAL_SPLITTER_TEMPLATES),
            "partial_splitter_observables": input_entry(PARTIAL_SPLITTER_OBSERVABLES),
            "partial_splitter_tables": input_entry(PARTIAL_SPLITTER_TABLES),
            "partial_splitter_certificate": input_entry(PARTIAL_SPLITTER_CERTIFICATE),
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
            "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search.json"
            ),
            "aperture_closure_tail_trim_neighborhood_shells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_trim_neighborhood_shells.csv"
            ),
            "aperture_closure_tail_trim_neighborhood_frontier_csv": relpath(
                OUT_DIR / "aperture_closure_tail_trim_neighborhood_frontier.csv"
            ),
            "aperture_closure_tail_trim_neighborhood_profiles_csv": relpath(
                OUT_DIR / "aperture_closure_tail_trim_neighborhood_profiles.csv"
            ),
            "aperture_closure_tail_trim_neighborhood_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_trim_neighborhood_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "the radius-three local trim neighborhood around the two certified oversplitters",
                "that no sub-223 delta2 closed-positive row in that neighborhood has exact 24 closures, six templates, and all-four lifts",
                "that exact-24 rows and six-template rows occur separately but do not coincide",
                "that the nearest all-four rows remain 28-closure seven-template oversplitters",
            ],
            "does_not_certify_because_not_required": [
                "edit radius four or higher",
                "words not beginning with x2,x1",
                "variation 223 or higher",
                "global optimality outside the declared trim neighborhood",
            ],
        },
        "next_highest_yield_item": (
            "Leave local trimming and change the aperture: search radius-one "
            "edits of the selected six-template lift and the 28-closure "
            "oversplitters together, allowing variation up to 223, to identify "
            "the first move that trades endpoint-13 excess for endpoint-11 "
            "closure without losing delta2."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified partial-splitter artifacts",
            "build the radius-three local edit neighborhood around the two oversplitters",
            "check exact-24 rows, six-template rows, and all-four ge24 rows",
            "check no exact 24 / six-template / all-four trim target exists",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search": trim,
        "aperture_closure_tail_trim_neighborhood_shells_csv": csv_text(
            SHELL_COLUMNS,
            shell_rows,
        ),
        "aperture_closure_tail_trim_neighborhood_frontier_csv": csv_text(
            FRONTIER_COLUMNS,
            frontier_rows,
        ),
        "aperture_closure_tail_trim_neighborhood_profiles_csv": csv_text(
            PROFILE_COLUMNS,
            profile_rows,
        ),
        "aperture_closure_tail_trim_neighborhood_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "shell_table": shell_table,
        "frontier_table": frontier_table,
        "profile_table": profile_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate": certificate,
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
        / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search"
        ],
    )
    (OUT_DIR / "aperture_closure_tail_trim_neighborhood_shells.csv").write_text(
        payloads["aperture_closure_tail_trim_neighborhood_shells_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_trim_neighborhood_frontier.csv").write_text(
        payloads["aperture_closure_tail_trim_neighborhood_frontier_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_trim_neighborhood_profiles.csv").write_text(
        payloads["aperture_closure_tail_trim_neighborhood_profiles_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_trim_neighborhood_observables.csv").write_text(
        payloads["aperture_closure_tail_trim_neighborhood_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_tables.npz",
        shell_table=payloads["shell_table"],
        frontier_table=payloads["frontier_table"],
        profile_table=payloads["profile_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate"
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
