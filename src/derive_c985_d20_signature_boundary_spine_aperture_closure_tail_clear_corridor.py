from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        OUT_DIR as CARRIER_SPLICE_DIR,
        SELECTED_SIX_TEMPLATE_WORD,
        STATUS as CARRIER_SPLICE_STATUS,
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
    from .derive_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search import (
        OUT_DIR as TRIM_NEIGHBORHOOD_DIR,
        SEED_WORDS,
        STATUS as TRIM_NEIGHBORHOOD_STATUS,
        one_edit_neighbors,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from .derive_c985_typed_simple_object_registry import INDEX_PATH
    from .paths import D20_INVARIANTS, ROOT
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_carrier_splice_realization import (
        OUT_DIR as CARRIER_SPLICE_DIR,
        SELECTED_SIX_TEMPLATE_WORD,
        STATUS as CARRIER_SPLICE_STATUS,
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
    from derive_c985_d20_signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search import (
        OUT_DIR as TRIM_NEIGHBORHOOD_DIR,
        SEED_WORDS,
        STATUS as TRIM_NEIGHBORHOOD_STATUS,
        one_edit_neighbors,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_overhead3_weak_promotion_audit import (
        first_return_closed,
    )
    from derive_c985_typed_simple_object_registry import INDEX_PATH
    from paths import D20_INVARIANTS, ROOT


THEOREM_ID = (
    "c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor"
)
STATUS = (
    "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CLEAR_CORRIDOR_CERTIFIED"
)
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

CARRIER_SPLICE_REPORT = CARRIER_SPLICE_DIR / "report.json"
CARRIER_SPLICE_CERTIFICATE = (
    CARRIER_SPLICE_DIR
    / "signature_boundary_spine_aperture_closure_tail_carrier_splice_realization_certificate.json"
)
PARTIAL_SPLITTER_REPORT = PARTIAL_SPLITTER_DIR / "report.json"
PARTIAL_SPLITTER_CERTIFICATE = (
    PARTIAL_SPLITTER_DIR
    / "signature_boundary_spine_aperture_closure_tail_partial_splitter_search_certificate.json"
)
TRIM_NEIGHBORHOOD_REPORT = TRIM_NEIGHBORHOOD_DIR / "report.json"
TRIM_NEIGHBORHOOD_CERTIFICATE = (
    TRIM_NEIGHBORHOOD_DIR
    / "signature_boundary_spine_aperture_closure_tail_trim_neighborhood_search_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_closure_tail_clear_corridor.py"
)

ANCHOR_SELECTED = 0
ANCHOR_OVERSPLITTER_217 = 1
ANCHOR_OVERSPLITTER_219 = 2
ANCHOR_WORDS = (
    SELECTED_SIX_TEMPLATE_WORD,
    SEED_WORDS[0],
    SEED_WORDS[1],
)

MIN_WORD_LENGTH = 8
MAX_WORD_LENGTH = 16
MAX_TRACE_NODES = 20
PREFIX_FIXED = (2, 1)
MAX_ANCHOR_EDIT_RADIUS = 1
TARGET_DELTA_TWICE = 2
TARGET_VARIATION_INCLUSIVE_BOUND = 223
TARGET_CLOSED_PATH_COUNT = 24
TARGET_TEMPLATE_COUNT = 6
TARGET_ENDPOINT_11_PATH_COUNT = 8

WORD_COLUMNS = [f"word_symbol_{index}_id" for index in range(MAX_WORD_LENGTH)]
TRACE_NODE_COLUMNS = [f"trace_node_{index}_id" for index in range(MAX_TRACE_NODES)]

CELL_COLUMNS = [
    "corridor_cell_id",
    "component_id",
    "nearest_anchor_edit_radius",
    "selected_anchor_edit_radius",
    "oversplitter217_anchor_edit_radius",
    "oversplitter219_anchor_edit_radius",
    "word_length",
    *WORD_COLUMNS,
    "trace_node_count",
    *TRACE_NODE_COLUMNS,
    "metric_gromov_delta_twice",
    "trace_signature_total_variation",
    "first_return_closed_path_count",
    "closure_excess_signed_from_24",
    "closure_excess_abs_from_24",
    "normalized_tail_template_count",
    "template_excess_signed_from_6",
    "template_excess_abs_from_6",
    "template_lift_count_min",
    "template_lift_count_max",
    "four_lift_template_count",
    "non_four_template_count",
    "all_four_lift_flag",
    "tail_entry_9_path_count",
    "tail_entry_10_path_count",
    "tail_entry_11_path_count",
    "tail_entry_13_path_count",
    "endpoint13_free_flag",
    "endpoint11_gap_abs_from_8",
    "angel_local_mass",
    "has_chord_31_28_flag",
    "has_chord_50_34_flag",
    "clear_flag",
    "underclosed_endpoint13_free_all_four_flag",
    "exact24_six_all_four_flag",
    "anchor_selected_flag",
    "anchor_oversplitter_flag",
]

EDGE_COLUMNS = [
    "corridor_edge_id",
    "source_cell_id",
    "target_cell_id",
    "source_component_id",
    "target_component_id",
    "edit_kind_code",
    "source_word_length",
    "target_word_length",
    "source_angel_local_mass",
    "target_angel_local_mass",
    "endpoint13_mass_delta_signed",
    "closure_count_delta_signed",
    "template_count_delta_signed",
]

COMPONENT_COLUMNS = [
    "component_id",
    "component_kind_code",
    "cell_count",
    "edge_count",
    "selected_anchor_flag",
    "oversplitter_anchor_count",
    "target_cell_count",
    "clear_cell_count",
    "underclosed_endpoint13_free_all_four_count",
    "endpoint13_heavy_cell_count",
    "min_variation",
    "min_angel_local_mass",
    "max_endpoint13_path_count",
    "min_endpoint13_path_count",
    "selected_to_oversplitter_bridge_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "anchor_word_count": 0,
    "radius1_total_word_count": 1,
    "trace_valid_word_count": 2,
    "delta2_variation_le223_word_count": 3,
    "repair_chord_admissible_word_count": 4,
    "closed_positive_cell_count": 5,
    "corridor_edge_count": 6,
    "connected_component_count": 7,
    "selected_component_cell_count": 8,
    "oversplitter_component_cell_count": 9,
    "target_cell_count": 10,
    "clear_cell_count": 11,
    "selected_component_clear_count": 12,
    "oversplitter_component_clear_count": 13,
    "underclosed_endpoint13_free_all_four_count": 14,
    "selected_to_oversplitter_path_exists": 15,
    "non_anchor_exact24_six_all_four_count": 16,
    "best_clear_nontarget_variation": 17,
    "best_clear_nontarget_closed_paths": 18,
    "best_clear_nontarget_template_count": 19,
    "oversplitter_underclosed_clearing_min_variation": 20,
    "oversplitter_underclosed_clearing_closed_paths": 21,
    "oversplitter_underclosed_clearing_template_count": 22,
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{path} is not a JSON object")
    return payload


def padded(values: tuple[int, ...], length: int) -> tuple[int, ...]:
    return values + tuple(-1 for _ in range(length - len(values)))


def read_int_dict_csv(path: Path) -> list[dict[str, int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def edit_kind_code(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    if len(left) == len(right):
        return 0
    return 1


def anchor_radiuses(word: tuple[int, ...]) -> tuple[int, int, int]:
    radius_values = []
    for anchor in ANCHOR_WORDS:
        if word == anchor:
            radius_values.append(0)
        elif word in one_edit_neighbors(anchor):
            radius_values.append(1)
        else:
            radius_values.append(2)
    return tuple(radius_values)


def endpoint_counts(
    templates: Counter[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]],
) -> Counter[int]:
    counts: Counter[int] = Counter()
    for template, path_count in templates.items():
        counts[int(template[0][0])] += int(path_count)
    return counts


def radius_one_words() -> set[tuple[int, ...]]:
    words = set(ANCHOR_WORDS)
    for anchor in ANCHOR_WORDS:
        for neighbor in one_edit_neighbors(anchor):
            if (
                MIN_WORD_LENGTH <= len(neighbor) <= MAX_WORD_LENGTH
                and neighbor[: len(PREFIX_FIXED)] == PREFIX_FIXED
            ):
                words.add(neighbor)
    return words


def build_raw_cells() -> tuple[list[dict[str, Any]], dict[str, int]]:
    candidate_words = radius_one_words()
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
    stats["anchor_word_count"] = len(ANCHOR_WORDS)
    stats["radius1_total_word_count"] = len(candidate_words)
    raw_cells: list[dict[str, Any]] = []
    for word in sorted(candidate_words, key=lambda value: (len(value), value)):
        try:
            _raw_windows, trace_nodes, _trace_signatures, metrics = build_trace(
                word,
                assoc_by_word,
                rewrite_edge_by_pair,
            )
        except Exception:
            stats["trace_failure_count"] += 1
            continue
        stats["trace_valid_word_count"] += 1
        variation = int(metrics["trace_signature_total_variation"])
        delta_twice = int(metrics["metric_gromov_delta_twice"])
        if (
            delta_twice != TARGET_DELTA_TWICE
            or variation > TARGET_VARIATION_INCLUSIVE_BOUND
        ):
            continue
        stats["delta2_variation_le223_word_count"] += 1
        trace = tuple(int(value) for value in trace_nodes)
        has_31_28 = contains_undirected_edge(trace, 31, 28)
        has_50_34 = contains_undirected_edge(trace, 50, 34)
        if not (has_31_28 or has_50_34):
            stats["no_repair_chord_word_count"] += 1
            continue
        stats["repair_chord_admissible_word_count"] += 1
        states = carrier_paths(word, carrier_adjacency)
        closed_states = first_return_closed(states)
        if not closed_states:
            stats["no_closed_path_word_count"] += 1
            continue
        tail_start = max(0, len(word) - 5)
        templates = Counter(tail_slices(state, tail_start) for state in closed_states)
        lift_counts = sorted(int(value) for value in templates.values())
        endpoints = endpoint_counts(templates)
        radius_values = anchor_radiuses(word)
        template_count = len(templates)
        four_lift_count = sum(int(value == 4) for value in lift_counts)
        non_four_count = template_count - four_lift_count
        closure_abs = abs(len(closed_states) - TARGET_CLOSED_PATH_COUNT)
        template_abs = abs(template_count - TARGET_TEMPLATE_COUNT)
        endpoint11_gap = abs(endpoints[11] - TARGET_ENDPOINT_11_PATH_COUNT)
        angel_local_mass = (
            closure_abs
            + template_abs
            + endpoints[13]
            + endpoint11_gap
            + non_four_count
        )
        raw_cells.append(
            {
                "word": word,
                "trace": trace,
                "nearest_anchor_edit_radius": min(radius_values),
                "selected_anchor_edit_radius": radius_values[ANCHOR_SELECTED],
                "oversplitter217_anchor_edit_radius": radius_values[
                    ANCHOR_OVERSPLITTER_217
                ],
                "oversplitter219_anchor_edit_radius": radius_values[
                    ANCHOR_OVERSPLITTER_219
                ],
                "metric_gromov_delta_twice": delta_twice,
                "trace_signature_total_variation": variation,
                "first_return_closed_path_count": len(closed_states),
                "normalized_tail_template_count": template_count,
                "template_lift_count_min": min(lift_counts),
                "template_lift_count_max": max(lift_counts),
                "four_lift_template_count": four_lift_count,
                "non_four_template_count": non_four_count,
                "all_four_lift_flag": int(all(value == 4 for value in lift_counts)),
                "tail_entry_9_path_count": endpoints[9],
                "tail_entry_10_path_count": endpoints[10],
                "tail_entry_11_path_count": endpoints[11],
                "tail_entry_13_path_count": endpoints[13],
                "endpoint11_gap_abs_from_8": endpoint11_gap,
                "angel_local_mass": angel_local_mass,
                "has_chord_31_28_flag": int(has_31_28),
                "has_chord_50_34_flag": int(has_50_34),
            }
        )
    return raw_cells, dict(stats)


def assign_components(
    raw_cells: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, int]], list[set[int]]]:
    raw_cells = sorted(
        raw_cells,
        key=lambda row: (
            row["nearest_anchor_edit_radius"],
            row["trace_signature_total_variation"],
            len(row["word"]),
            row["word"],
        ),
    )
    for cell_id, row in enumerate(raw_cells):
        row["corridor_cell_id"] = cell_id

    id_by_word = {row["word"]: row["corridor_cell_id"] for row in raw_cells}
    adjacency: dict[int, set[int]] = {
        row["corridor_cell_id"]: set() for row in raw_cells
    }
    for row in raw_cells:
        source_id = row["corridor_cell_id"]
        for neighbor in one_edit_neighbors(row["word"]):
            target_id = id_by_word.get(neighbor)
            if target_id is not None and target_id != source_id:
                adjacency[source_id].add(target_id)
                adjacency[target_id].add(source_id)

    components: list[set[int]] = []
    seen: set[int] = set()
    for cell_id in sorted(adjacency):
        if cell_id in seen:
            continue
        stack = [cell_id]
        seen.add(cell_id)
        component: set[int] = set()
        while stack:
            current = stack.pop()
            component.add(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(component)

    def component_sort_key(component: set[int]) -> tuple[int, int, int]:
        words = {raw_cells[cell_id]["word"] for cell_id in component}
        if ANCHOR_WORDS[ANCHOR_SELECTED] in words:
            kind = 0
        elif any(word in words for word in ANCHOR_WORDS[1:]):
            kind = 1
        else:
            kind = 2
        min_variation = min(
            raw_cells[cell_id]["trace_signature_total_variation"]
            for cell_id in component
        )
        return (kind, min_variation, min(component))

    components = sorted(components, key=component_sort_key)
    component_id_by_cell: dict[int, int] = {}
    for component_id, component in enumerate(components):
        for cell_id in component:
            component_id_by_cell[cell_id] = component_id
    for row in raw_cells:
        row["component_id"] = component_id_by_cell[row["corridor_cell_id"]]

    edge_rows = []
    seen_edges = set()
    for row in raw_cells:
        source_id = row["corridor_cell_id"]
        for target_id in adjacency[source_id]:
            edge = tuple(sorted((source_id, target_id)))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            source = raw_cells[edge[0]]
            target = raw_cells[edge[1]]
            edge_rows.append(
                {
                    "corridor_edge_id": len(edge_rows),
                    "source_cell_id": edge[0],
                    "target_cell_id": edge[1],
                    "source_component_id": source["component_id"],
                    "target_component_id": target["component_id"],
                    "edit_kind_code": edit_kind_code(source["word"], target["word"]),
                    "source_word_length": len(source["word"]),
                    "target_word_length": len(target["word"]),
                    "source_angel_local_mass": source["angel_local_mass"],
                    "target_angel_local_mass": target["angel_local_mass"],
                    "endpoint13_mass_delta_signed": (
                        target["tail_entry_13_path_count"]
                        - source["tail_entry_13_path_count"]
                    ),
                    "closure_count_delta_signed": (
                        target["first_return_closed_path_count"]
                        - source["first_return_closed_path_count"]
                    ),
                    "template_count_delta_signed": (
                        target["normalized_tail_template_count"]
                        - source["normalized_tail_template_count"]
                    ),
                }
            )
    return raw_cells, edge_rows, components


def build_rows() -> dict[str, Any]:
    raw_cells, stats = build_raw_cells()
    raw_cells, edge_rows, components = assign_components(raw_cells)
    rows_by_id = {row["corridor_cell_id"]: row for row in raw_cells}

    cell_rows = []
    for row in raw_cells:
        closed_paths = row["first_return_closed_path_count"]
        template_count = row["normalized_tail_template_count"]
        exact_target = (
            closed_paths == TARGET_CLOSED_PATH_COUNT
            and template_count == TARGET_TEMPLATE_COUNT
            and row["all_four_lift_flag"] == 1
        )
        endpoint13_free = row["tail_entry_13_path_count"] == 0
        clear = (
            row["all_four_lift_flag"] == 1
            and endpoint13_free
            and closed_paths >= TARGET_CLOSED_PATH_COUNT
        )
        cell_rows.append(
            {
                "corridor_cell_id": row["corridor_cell_id"],
                "component_id": row["component_id"],
                "nearest_anchor_edit_radius": row["nearest_anchor_edit_radius"],
                "selected_anchor_edit_radius": row["selected_anchor_edit_radius"],
                "oversplitter217_anchor_edit_radius": row[
                    "oversplitter217_anchor_edit_radius"
                ],
                "oversplitter219_anchor_edit_radius": row[
                    "oversplitter219_anchor_edit_radius"
                ],
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
                "first_return_closed_path_count": closed_paths,
                "closure_excess_signed_from_24": closed_paths
                - TARGET_CLOSED_PATH_COUNT,
                "closure_excess_abs_from_24": abs(
                    closed_paths - TARGET_CLOSED_PATH_COUNT
                ),
                "normalized_tail_template_count": template_count,
                "template_excess_signed_from_6": template_count
                - TARGET_TEMPLATE_COUNT,
                "template_excess_abs_from_6": abs(
                    template_count - TARGET_TEMPLATE_COUNT
                ),
                "template_lift_count_min": row["template_lift_count_min"],
                "template_lift_count_max": row["template_lift_count_max"],
                "four_lift_template_count": row["four_lift_template_count"],
                "non_four_template_count": row["non_four_template_count"],
                "all_four_lift_flag": row["all_four_lift_flag"],
                "tail_entry_9_path_count": row["tail_entry_9_path_count"],
                "tail_entry_10_path_count": row["tail_entry_10_path_count"],
                "tail_entry_11_path_count": row["tail_entry_11_path_count"],
                "tail_entry_13_path_count": row["tail_entry_13_path_count"],
                "endpoint13_free_flag": int(endpoint13_free),
                "endpoint11_gap_abs_from_8": row["endpoint11_gap_abs_from_8"],
                "angel_local_mass": row["angel_local_mass"],
                "has_chord_31_28_flag": row["has_chord_31_28_flag"],
                "has_chord_50_34_flag": row["has_chord_50_34_flag"],
                "clear_flag": int(clear),
                "underclosed_endpoint13_free_all_four_flag": int(
                    row["all_four_lift_flag"] == 1
                    and endpoint13_free
                    and closed_paths < TARGET_CLOSED_PATH_COUNT
                ),
                "exact24_six_all_four_flag": int(exact_target and endpoint13_free),
                "anchor_selected_flag": int(row["word"] == ANCHOR_WORDS[0]),
                "anchor_oversplitter_flag": int(row["word"] in ANCHOR_WORDS[1:]),
            }
        )

    cell_by_id = {row["corridor_cell_id"]: row for row in cell_rows}
    component_rows = []
    for component_id, component in enumerate(components):
        cells = [cell_by_id[cell_id] for cell_id in sorted(component)]
        words = {rows_by_id[cell_id]["word"] for cell_id in component}
        selected_flag = int(ANCHOR_WORDS[ANCHOR_SELECTED] in words)
        oversplitter_count = sum(int(word in words) for word in ANCHOR_WORDS[1:])
        if selected_flag:
            kind = 0
        elif oversplitter_count:
            kind = 1
        else:
            kind = 2
        edge_count = sum(
            int(edge["source_component_id"] == component_id)
            for edge in edge_rows
        )
        component_rows.append(
            {
                "component_id": component_id,
                "component_kind_code": kind,
                "cell_count": len(cells),
                "edge_count": edge_count,
                "selected_anchor_flag": selected_flag,
                "oversplitter_anchor_count": oversplitter_count,
                "target_cell_count": sum(
                    row["exact24_six_all_four_flag"] for row in cells
                ),
                "clear_cell_count": sum(row["clear_flag"] for row in cells),
                "underclosed_endpoint13_free_all_four_count": sum(
                    row["underclosed_endpoint13_free_all_four_flag"] for row in cells
                ),
                "endpoint13_heavy_cell_count": sum(
                    int(row["tail_entry_13_path_count"] > 0) for row in cells
                ),
                "min_variation": min(
                    row["trace_signature_total_variation"] for row in cells
                ),
                "min_angel_local_mass": min(row["angel_local_mass"] for row in cells),
                "max_endpoint13_path_count": max(
                    row["tail_entry_13_path_count"] for row in cells
                ),
                "min_endpoint13_path_count": min(
                    row["tail_entry_13_path_count"] for row in cells
                ),
                "selected_to_oversplitter_bridge_flag": int(
                    selected_flag and oversplitter_count > 0
                ),
            }
        )

    return {
        "stats": stats,
        "cell_rows": cell_rows,
        "edge_rows": edge_rows,
        "component_rows": component_rows,
    }


def build_payloads() -> dict[str, Any]:
    carrier_report = load_json(CARRIER_SPLICE_REPORT)
    carrier_certificate = load_json(CARRIER_SPLICE_CERTIFICATE)
    partial_report = load_json(PARTIAL_SPLITTER_REPORT)
    partial_certificate = load_json(PARTIAL_SPLITTER_CERTIFICATE)
    trim_report = load_json(TRIM_NEIGHBORHOOD_REPORT)
    trim_certificate = load_json(TRIM_NEIGHBORHOOD_CERTIFICATE)

    rows = build_rows()
    stats = rows["stats"]
    cell_rows = rows["cell_rows"]
    edge_rows = rows["edge_rows"]
    component_rows = rows["component_rows"]

    selected_component = next(
        row for row in component_rows if row["selected_anchor_flag"] == 1
    )
    oversplitter_component = next(
        row for row in component_rows if row["oversplitter_anchor_count"] == 2
    )
    clear_nontarget_rows = [
        row
        for row in cell_rows
        if row["clear_flag"] == 1 and row["exact24_six_all_four_flag"] == 0
    ]
    best_clear_nontarget = min(
        clear_nontarget_rows,
        key=lambda row: (
            row["trace_signature_total_variation"],
            row["angel_local_mass"],
            row["corridor_cell_id"],
        ),
    )
    oversplitter_underclosed = [
        row
        for row in cell_rows
        if row["component_id"] == oversplitter_component["component_id"]
        and row["underclosed_endpoint13_free_all_four_flag"] == 1
    ]
    best_oversplitter_underclosed = min(
        oversplitter_underclosed,
        key=lambda row: (
            row["trace_signature_total_variation"],
            row["angel_local_mass"],
            row["corridor_cell_id"],
        ),
    )
    non_anchor_targets = [
        row
        for row in cell_rows
        if row["exact24_six_all_four_flag"] == 1
        and row["anchor_selected_flag"] == 0
    ]

    observable_values = {
        "anchor_word_count": stats["anchor_word_count"],
        "radius1_total_word_count": stats["radius1_total_word_count"],
        "trace_valid_word_count": stats["trace_valid_word_count"],
        "delta2_variation_le223_word_count": stats[
            "delta2_variation_le223_word_count"
        ],
        "repair_chord_admissible_word_count": stats[
            "repair_chord_admissible_word_count"
        ],
        "closed_positive_cell_count": len(cell_rows),
        "corridor_edge_count": len(edge_rows),
        "connected_component_count": len(component_rows),
        "selected_component_cell_count": selected_component["cell_count"],
        "oversplitter_component_cell_count": oversplitter_component["cell_count"],
        "target_cell_count": sum(
            row["exact24_six_all_four_flag"] for row in cell_rows
        ),
        "clear_cell_count": sum(row["clear_flag"] for row in cell_rows),
        "selected_component_clear_count": selected_component["clear_cell_count"],
        "oversplitter_component_clear_count": oversplitter_component[
            "clear_cell_count"
        ],
        "underclosed_endpoint13_free_all_four_count": sum(
            row["underclosed_endpoint13_free_all_four_flag"] for row in cell_rows
        ),
        "selected_to_oversplitter_path_exists": int(
            selected_component["component_id"] == oversplitter_component["component_id"]
        ),
        "non_anchor_exact24_six_all_four_count": len(non_anchor_targets),
        "best_clear_nontarget_variation": best_clear_nontarget[
            "trace_signature_total_variation"
        ],
        "best_clear_nontarget_closed_paths": best_clear_nontarget[
            "first_return_closed_path_count"
        ],
        "best_clear_nontarget_template_count": best_clear_nontarget[
            "normalized_tail_template_count"
        ],
        "oversplitter_underclosed_clearing_min_variation": best_oversplitter_underclosed[
            "trace_signature_total_variation"
        ],
        "oversplitter_underclosed_clearing_closed_paths": best_oversplitter_underclosed[
            "first_return_closed_path_count"
        ],
        "oversplitter_underclosed_clearing_template_count": best_oversplitter_underclosed[
            "normalized_tail_template_count"
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

    cell_table = table_from_rows(CELL_COLUMNS, cell_rows)
    edge_table = table_from_rows(EDGE_COLUMNS, edge_rows)
    component_table = table_from_rows(COMPONENT_COLUMNS, component_rows)
    observable_table = table_from_rows(OBSERVABLE_COLUMNS, observable_rows)

    checks = {
        "carrier_splice_report_certified": carrier_report.get("status")
        == CARRIER_SPLICE_STATUS,
        "carrier_splice_certificate_certified": carrier_certificate.get("status")
        == CARRIER_SPLICE_STATUS,
        "partial_splitter_report_certified": partial_report.get("status")
        == PARTIAL_SPLITTER_STATUS,
        "partial_splitter_certificate_certified": partial_certificate.get("status")
        == PARTIAL_SPLITTER_STATUS,
        "trim_neighborhood_report_certified": trim_report.get("status")
        == TRIM_NEIGHBORHOOD_STATUS,
        "trim_neighborhood_certificate_certified": trim_certificate.get("status")
        == TRIM_NEIGHBORHOOD_STATUS,
        "radius1_total_word_count_is_291": observable_values[
            "radius1_total_word_count"
        ]
        == 291,
        "trace_valid_word_count_is_246": observable_values["trace_valid_word_count"]
        == 246,
        "delta2_variation_le223_word_count_is_51": observable_values[
            "delta2_variation_le223_word_count"
        ]
        == 51,
        "repair_chord_admissible_word_count_is_45": observable_values[
            "repair_chord_admissible_word_count"
        ]
        == 45,
        "closed_positive_cell_count_is_25": len(cell_rows) == 25,
        "corridor_edge_count_is_40": len(edge_rows) == 40,
        "component_count_is_two": len(component_rows) == 2,
        "selected_and_oversplitters_are_separate_components": observable_values[
            "selected_to_oversplitter_path_exists"
        ]
        == 0,
        "selected_component_has_unique_target": selected_component[
            "target_cell_count"
        ]
        == 1
        and observable_values["target_cell_count"] == 1,
        "no_non_anchor_exact24_six_all_four_cell": len(non_anchor_targets) == 0,
        "selected_component_has_two_clear_cells": selected_component[
            "clear_cell_count"
        ]
        == 2,
        "oversplitter_component_has_no_clear_cell": oversplitter_component[
            "clear_cell_count"
        ]
        == 0,
        "oversplitter_component_has_underclosed_e13_free_cells": oversplitter_component[
            "underclosed_endpoint13_free_all_four_count"
        ]
        == 4,
        "best_clear_nontarget_is_137_36_9": (
            best_clear_nontarget["trace_signature_total_variation"],
            best_clear_nontarget["first_return_closed_path_count"],
            best_clear_nontarget["normalized_tail_template_count"],
        )
        == (137, 36, 9),
        "best_oversplitter_clearing_collapses_to_8_2": (
            best_oversplitter_underclosed["trace_signature_total_variation"],
            best_oversplitter_underclosed["first_return_closed_path_count"],
            best_oversplitter_underclosed["normalized_tail_template_count"],
        )
        == (175, 8, 2),
        "cell_table_shape_matches_codebook": tuple(cell_table.shape)
        == (25, len(CELL_COLUMNS)),
        "edge_table_shape_matches_codebook": tuple(edge_table.shape)
        == (40, len(EDGE_COLUMNS)),
        "component_table_shape_matches_codebook": tuple(component_table.shape)
        == (2, len(COMPONENT_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    selected_target_row = next(
        row for row in cell_rows if row["exact24_six_all_four_flag"] == 1
    )
    witness = {
        "anchor_words": [list(word) for word in ANCHOR_WORDS],
        "radius1_total_word_count": observable_values["radius1_total_word_count"],
        "closed_positive_cell_count": len(cell_rows),
        "corridor_edge_count": len(edge_rows),
        "component_sizes": [row["cell_count"] for row in component_rows],
        "selected_component_id": selected_component["component_id"],
        "oversplitter_component_id": oversplitter_component["component_id"],
        "selected_target_cell": {
            "corridor_cell_id": selected_target_row["corridor_cell_id"],
            "variation": selected_target_row["trace_signature_total_variation"],
            "closed_paths": selected_target_row["first_return_closed_path_count"],
            "template_count": selected_target_row[
                "normalized_tail_template_count"
            ],
            "endpoint_distribution": {
                "9": selected_target_row["tail_entry_9_path_count"],
                "10": selected_target_row["tail_entry_10_path_count"],
                "11": selected_target_row["tail_entry_11_path_count"],
                "13": selected_target_row["tail_entry_13_path_count"],
            },
        },
        "best_clear_nontarget": {
            "corridor_cell_id": best_clear_nontarget["corridor_cell_id"],
            "variation": best_clear_nontarget["trace_signature_total_variation"],
            "closed_paths": best_clear_nontarget[
                "first_return_closed_path_count"
            ],
            "template_count": best_clear_nontarget[
                "normalized_tail_template_count"
            ],
            "word": [
                best_clear_nontarget[column]
                for column in WORD_COLUMNS
                if best_clear_nontarget[column] != -1
            ],
        },
        "best_oversplitter_endpoint13_clearing": {
            "corridor_cell_id": best_oversplitter_underclosed[
                "corridor_cell_id"
            ],
            "variation": best_oversplitter_underclosed[
                "trace_signature_total_variation"
            ],
            "closed_paths": best_oversplitter_underclosed[
                "first_return_closed_path_count"
            ],
            "template_count": best_oversplitter_underclosed[
                "normalized_tail_template_count"
            ],
        },
        "cell_table_sha256": sha_array(cell_table),
        "edge_table_sha256": sha_array(edge_table),
        "component_table_sha256": sha_array(component_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    corridor = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor@1",
        "object": "d20",
        "comparison_rule": {
            "parent": TRIM_NEIGHBORHOOD_REPORT.relative_to(ROOT).as_posix(),
            "anchor_words": {
                "selected_six_template_lift": list(ANCHOR_WORDS[0]),
                "oversplitter_variation_217": list(ANCHOR_WORDS[1]),
                "oversplitter_variation_219": list(ANCHOR_WORDS[2]),
            },
            "radius": MAX_ANCHOR_EDIT_RADIUS,
            "filters": [
                "word starts with x2,x1",
                "8 <= word_length <= 16",
                "metric_gromov_delta_twice = 2",
                "trace_signature_total_variation <= 223",
                "trace contains repair chord 31--28 or 50--34",
                "first_return_closed_path_count > 0",
            ],
            "clear_cell_definition": [
                "all retained templates have four lifts",
                "endpoint-13 path count is zero",
                "first_return_closed_path_count >= 24",
            ],
        },
        "summary": {
            "closed_positive_cell_count": len(cell_rows),
            "corridor_edge_count": len(edge_rows),
            "connected_component_count": len(component_rows),
            "target_cell_count": observable_values["target_cell_count"],
            "clear_cell_count": observable_values["clear_cell_count"],
            "selected_to_oversplitter_path_exists": observable_values[
                "selected_to_oversplitter_path_exists"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_CLOSURE_TAIL_CLEAR_CORRIDOR_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the radius-one aperture graph around the selected lift and two oversplitters has 25 closed-positive delta2 repair-chord cells",
            "those cells split into two admissible edit components: the selected component and the oversplitter component",
            "the selected component contains the unique exact 24-closure six-template all-four cell and one lower-variation clear overshoot at 36 closures and 9 templates",
            "the oversplitter component has no clear ge24 endpoint-13-free cell; clearing endpoint-13 there collapses to 8 closures and 2 templates",
            "therefore endpoint-13 mass is locally movable, but radius-one aperture edits trade it into closure/template mass rather than into the exact target",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The Angel-style radius-one aperture corridor around the selected "
            "six-template lift and the two 28-closure oversplitters has 25 "
            "closed-positive delta2 repair-chord cells under variation <= 223. "
            "The admissible edit graph has 40 edges and exactly two connected "
            "components: a selected-lift component with the unique exact "
            "24-closure, six-template, all-four cell, and an oversplitter "
            "component containing both 28-closure endpoint-13-heavy anchors. "
            "The selected component has a lower-variation endpoint-13-free "
            "clear overshoot at variation 137 with 36 closures and 9 templates. "
            "The oversplitter component has no endpoint-13-free all-four cell "
            "with at least 24 closures; its best endpoint-13-clearing neighbor "
            "collapses to 8 closures and 2 templates. Thus radius-one aperture "
            "edits can move endpoint-13 mass, but not into the exact 24/six "
            "target."
        ),
        "stage_protocol": {
            "draft": "seed the aperture corridor with the selected six-template lift and the two certified 28-closure oversplitters",
            "witness": "enumerate radius-one word edits and keep delta2, variation <= 223, repair-chord, closed-positive cells",
            "coherence": "build the one-edit cell graph and classify clear cells by endpoint-13 mass, all-four lifts, and closure count",
            "closure": "certify component separation and the absence of an oversplitter-side clear exact target at radius one",
            "emit": "emit corridor cells, edit edges, component summaries, observables, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "carrier_splice_report": input_entry(
                CARRIER_SPLICE_REPORT,
                {
                    "status": carrier_report.get("status"),
                    "certificate_sha256": carrier_report.get("certificate_sha256"),
                },
            ),
            "carrier_splice_certificate": input_entry(CARRIER_SPLICE_CERTIFICATE),
            "partial_splitter_report": input_entry(
                PARTIAL_SPLITTER_REPORT,
                {
                    "status": partial_report.get("status"),
                    "certificate_sha256": partial_report.get("certificate_sha256"),
                },
            ),
            "partial_splitter_certificate": input_entry(PARTIAL_SPLITTER_CERTIFICATE),
            "trim_neighborhood_report": input_entry(
                TRIM_NEIGHBORHOOD_REPORT,
                {
                    "status": trim_report.get("status"),
                    "certificate_sha256": trim_report.get("certificate_sha256"),
                },
            ),
            "trim_neighborhood_certificate": input_entry(TRIM_NEIGHBORHOOD_CERTIFICATE),
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
            "signature_boundary_spine_aperture_closure_tail_clear_corridor": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_clear_corridor.json"
            ),
            "aperture_closure_tail_clear_corridor_cells_csv": relpath(
                OUT_DIR / "aperture_closure_tail_clear_corridor_cells.csv"
            ),
            "aperture_closure_tail_clear_corridor_edges_csv": relpath(
                OUT_DIR / "aperture_closure_tail_clear_corridor_edges.csv"
            ),
            "aperture_closure_tail_clear_corridor_components_csv": relpath(
                OUT_DIR / "aperture_closure_tail_clear_corridor_components.csv"
            ),
            "aperture_closure_tail_clear_corridor_observables_csv": relpath(
                OUT_DIR / "aperture_closure_tail_clear_corridor_observables.csv"
            ),
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_clear_corridor_tables.npz"
            ),
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "radius-one edits around the selected six-template lift and the two certified oversplitters",
                "delta2, variation <= 223, repair-chord, closed-positive aperture cells in that radius-one graph",
                "component separation between the selected exact target and the oversplitter anchors",
                "that endpoint-13-clearing neighbors exist but do not preserve the exact 24/six all-four target",
            ],
            "does_not_certify_because_not_required": [
                "edit radius two or higher",
                "paths through cells that lose delta2, exceed variation 223, or drop repair-chord support",
                "a global no-go theorem outside the declared aperture corridor",
                "categorical pivotal, spherical, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Build the level-two clear-corridor search: expand from the two "
            "component boundaries through radius-two aperture edits, allow one "
            "tracked forbidden gate, and test whether endpoint-13 mass can be "
            "routed into endpoint-11 without closure/template blow-up."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_closure_tail_clear_corridor_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified carrier-splice, partial-splitter, and trim-neighborhood artifacts",
            "enumerate radius-one aperture words around the three anchors",
            "evaluate trace metrics, repair chords, first-return closures, and tail-template lifts",
            "build the admissible one-edit corridor graph and component summaries",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_closure_tail_clear_corridor": corridor,
        "aperture_closure_tail_clear_corridor_cells_csv": csv_text(
            CELL_COLUMNS,
            cell_rows,
        ),
        "aperture_closure_tail_clear_corridor_edges_csv": csv_text(
            EDGE_COLUMNS,
            edge_rows,
        ),
        "aperture_closure_tail_clear_corridor_components_csv": csv_text(
            COMPONENT_COLUMNS,
            component_rows,
        ),
        "aperture_closure_tail_clear_corridor_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "cell_table": cell_table,
        "edge_table": edge_table,
        "component_table": component_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_closure_tail_clear_corridor.json",
        payloads["signature_boundary_spine_aperture_closure_tail_clear_corridor"],
    )
    (OUT_DIR / "aperture_closure_tail_clear_corridor_cells.csv").write_text(
        payloads["aperture_closure_tail_clear_corridor_cells_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_clear_corridor_edges.csv").write_text(
        payloads["aperture_closure_tail_clear_corridor_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_clear_corridor_components.csv").write_text(
        payloads["aperture_closure_tail_clear_corridor_components_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_closure_tail_clear_corridor_observables.csv").write_text(
        payloads["aperture_closure_tail_clear_corridor_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_tables.npz",
        cell_table=payloads["cell_table"],
        edge_table=payloads["edge_table"],
        component_table=payloads["component_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_closure_tail_clear_corridor_certificate"
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
