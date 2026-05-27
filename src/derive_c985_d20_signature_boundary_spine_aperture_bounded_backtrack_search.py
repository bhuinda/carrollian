from __future__ import annotations

import itertools
import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        ORIGIN_CARRIER_ID,
        OUT_DIR as TAIL_HYBRID_DIR,
        STATUS as TAIL_HYBRID_STATUS,
        X1_ATOM_ID,
        X1_SYMBOL_ID,
        X2_ATOM_ID,
        X2_SYMBOL_ID,
        shared_atoms,
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
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search import (
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_VARIATION,
        CELL_COMPLEX_CERTIFICATE,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_REPORT,
        CELL_COMPLEX_TABLES,
        REWRITE_COMPLEX_CERTIFICATE,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_REPORT,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ALPHABET_CSV,
        SYMBOLIC_ASSOCIATIVITY_CERTIFICATE,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_REPORT,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        ORIGIN_CARRIER_ID,
        OUT_DIR as TAIL_HYBRID_DIR,
        STATUS as TAIL_HYBRID_STATUS,
        X1_ATOM_ID,
        X1_SYMBOL_ID,
        X2_ATOM_ID,
        X2_SYMBOL_ID,
        shared_atoms,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_BOUNDED_BACKTRACK_SEARCH_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

TAIL_HYBRID_REPORT = TAIL_HYBRID_DIR / "report.json"
TAIL_HYBRID_JSON = (
    TAIL_HYBRID_DIR / "signature_boundary_spine_aperture_tail_hybrid_search.json"
)
TAIL_HYBRID_CANDIDATES = TAIL_HYBRID_DIR / "aperture_tail_hybrid_candidates.csv"
TAIL_HYBRID_TABLES = (
    TAIL_HYBRID_DIR / "signature_boundary_spine_aperture_tail_hybrid_search_tables.npz"
)
TAIL_HYBRID_CERTIFICATE = (
    TAIL_HYBRID_DIR
    / "signature_boundary_spine_aperture_tail_hybrid_search_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_bounded_backtrack_search.py"
)

SEARCH_LENGTHS = [5, 6, 7]
TRACE_BOUNDARY_NODE_ID = 48
STRICT_APERTURE_NODE_ID = 42
TAIL_VALLEY_NODE_ID = 27

WALK_CANDIDATE_COLUMNS = [
    "walk_candidate_id",
    "rank_order",
    "walk_length",
    "carrier_0_id",
    "carrier_1_id",
    "carrier_2_id",
    "carrier_3_id",
    "carrier_4_id",
    "carrier_5_id",
    "carrier_6_id",
    "carrier_7_id",
    "cell_edge_0_id",
    "cell_edge_1_id",
    "cell_edge_2_id",
    "cell_edge_3_id",
    "cell_edge_4_id",
    "cell_edge_5_id",
    "cell_edge_6_id",
    "selected_atom_0_id",
    "selected_atom_1_id",
    "selected_atom_2_id",
    "selected_atom_3_id",
    "selected_atom_4_id",
    "selected_atom_5_id",
    "selected_atom_6_id",
    "selected_symbol_0_id",
    "selected_symbol_1_id",
    "selected_symbol_2_id",
    "selected_symbol_3_id",
    "selected_symbol_4_id",
    "selected_symbol_5_id",
    "selected_symbol_6_id",
    "cycle_window_node_0_id",
    "cycle_window_node_1_id",
    "cycle_window_node_2_id",
    "cycle_window_node_3_id",
    "cycle_window_node_4_id",
    "cycle_window_node_5_id",
    "cycle_window_node_6_id",
    "repeated_interior_carrier_count",
    "immediate_backtrack_count",
    "trace_node_count",
    "trace_edge_count",
    "trace_detour_overhead",
    "trace_signature_total_variation",
    "signature_valley_depth",
    "trace_min_signature_after_node42",
    "metric_gromov_delta_twice",
    "metric_diameter",
    "metric_radius",
    "first_node44_trace_rank",
    "node44_realization_flag",
    "first_selected_x2_flag",
    "immediate_x1_tail_flag",
    "nonsimple_walk_flag",
    "no_intermediate_origin_flag",
    "improves_tail_overhead_flag",
    "contains_node27_after_node42_flag",
    "matches_baseline_tail_score_flag",
    "best_backtrack_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "rooted_closed_5_walk_count": 0,
    "rooted_closed_6_walk_count": 1,
    "rooted_closed_7_walk_count": 2,
    "simple_5_walk_count": 3,
    "simple_6_walk_count": 4,
    "simple_7_walk_count": 5,
    "nonsimple_5_walk_count": 6,
    "nonsimple_6_walk_count": 7,
    "nonsimple_7_walk_count": 8,
    "first_x2_5_walk_count": 9,
    "first_x2_6_walk_count": 10,
    "first_x2_7_walk_count": 11,
    "first_x2_x1_tail_5_walk_count": 12,
    "first_x2_x1_tail_6_walk_count": 13,
    "first_x2_x1_tail_7_walk_count": 14,
    "node44_5_candidate_count": 15,
    "node44_6_candidate_count": 16,
    "node44_7_candidate_count": 17,
    "node44_candidate_count": 18,
    "best_trace_overhead": 19,
    "improvement_candidate_count": 20,
    "baseline_matching_candidate_count": 21,
    "best_backtrack_candidate_count": 22,
    "best_backtrack_5_candidate_count": 23,
    "best_backtrack_6_candidate_count": 24,
    "best_backtrack_7_candidate_count": 25,
    "immediate_backtrack_candidate_count": 26,
    "best_immediate_backtrack_candidate_count": 27,
    "node27_forced_candidate_count": 28,
    "distinct_symbol_word_count": 29,
    "distinct_trace_node_count": 30,
}


def padded(values: list[int], size: int) -> list[int]:
    return [*values, *([-1] * (size - len(values)))]


def rooted_closed_walks(
    adjacency: dict[int, list[int]],
    edge_count: int,
) -> list[list[int]]:
    walks: list[list[int]] = []

    def rec(path: list[int]) -> None:
        if len(path) == edge_count:
            if ORIGIN_CARRIER_ID in adjacency.get(path[-1], []):
                walks.append([*path, ORIGIN_CARRIER_ID])
            return
        for neighbor in adjacency.get(path[-1], []):
            if neighbor == ORIGIN_CARRIER_ID:
                continue
            rec([*path, neighbor])

    rec([ORIGIN_CARRIER_ID])
    return walks


def is_simple_closed_walk(carriers: list[int]) -> bool:
    return carriers[0] == carriers[-1] and len(set(carriers[:-1])) == len(carriers[:-1])


def repeated_interior_carrier_count(carriers: list[int]) -> int:
    interior = carriers[1:-1]
    return len(interior) - len(set(interior))


def immediate_backtrack_count(carriers: list[int]) -> int:
    return sum(1 for index in range(len(carriers) - 2) if carriers[index] == carriers[index + 2])


def no_intermediate_origin(carriers: list[int]) -> bool:
    return ORIGIN_CARRIER_ID not in carriers[1:-1]


def build_payloads() -> dict[str, Any]:
    tail_report = load_json(TAIL_HYBRID_REPORT)
    tail_search = load_json(TAIL_HYBRID_JSON)
    tail_certificate = load_json(TAIL_HYBRID_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    tail_tables = np.load(TAIL_HYBRID_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    tail_candidate_table = np.asarray(tail_tables["candidate_table"], dtype=np.int64)
    cell_edge_table = np.asarray(cell_tables["carrier_region_edge_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"],
        dtype=np.int64,
    )

    cell_edges = read_int_csv(CELL_COMPLEX_EDGES)
    rewrite_edges = read_int_csv(REWRITE_COMPLEX_EDGES)
    associativity_rows = read_int_csv(SYMBOLIC_ASSOCIATIVITY_CSV)
    alphabet_rows = read_int_csv(SYMBOLIC_ALPHABET_CSV)

    atom_to_symbol = {
        int(row["atom_id"]): int(row["symbol_id"]) for row in alphabet_rows
    }
    assoc_by_word = associativity_lookup(associativity_rows)
    rewrite_edge_by_pair = {
        edge_key(int(row["source_node_id"]), int(row["target_node_id"])): row
        for row in rewrite_edges
    }
    edge_by_pair = {
        edge_key(
            int(row["source_carrier_mask_class_id"]),
            int(row["target_carrier_mask_class_id"]),
        ): row
        for row in cell_edges
    }
    adjacency: dict[int, list[int]] = {}
    for row in cell_edges:
        source = int(row["source_carrier_mask_class_id"])
        target = int(row["target_carrier_mask_class_id"])
        adjacency.setdefault(source, []).append(target)
        adjacency.setdefault(target, []).append(source)
    adjacency = {key: sorted(set(values)) for key, values in adjacency.items()}

    rooted_closed_counts: dict[int, int] = {}
    simple_counts: dict[int, int] = {}
    nonsimple_counts: dict[int, int] = {}
    prefilter_counts: Counter[tuple[int, str]] = Counter()
    payloads: list[dict[str, Any]] = []

    for length in SEARCH_LENGTHS:
        walks = rooted_closed_walks(adjacency, length)
        rooted_closed_counts[length] = len(walks)
        simple_counts[length] = sum(int(is_simple_closed_walk(walk)) for walk in walks)
        nonsimple_counts[length] = len(walks) - simple_counts[length]
        for carriers in walks:
            if is_simple_closed_walk(carriers):
                continue
            edge_rows = [
                edge_by_pair[edge_key(source, target)]
                for source, target in zip(carriers, carriers[1:])
            ]
            edge_ids = [int(row["cell_edge_id"]) for row in edge_rows]
            atom_options = [shared_atoms(row) for row in edge_rows]
            if X2_ATOM_ID not in atom_options[0]:
                continue
            prefilter_counts[(length, "first_x2")] += 1
            if X1_ATOM_ID not in atom_options[1]:
                continue
            prefilter_counts[(length, "first_x2_x1_tail")] += 1
            atom_options[0] = [X2_ATOM_ID]
            atom_options[1] = [X1_ATOM_ID]
            for atoms in itertools.product(*atom_options):
                symbols = tuple(atom_to_symbol[atom_id] for atom_id in atoms)
                if symbols[0] != X2_SYMBOL_ID or symbols[1] != X1_SYMBOL_ID:
                    continue
                cycle_windows = [
                    assoc_by_word[tuple(symbols[index:] + symbols[:index])[:3]]
                    for index in range(len(symbols))
                ]
                cycle_window_nodes = [
                    int(row["canonical_triple_id"]) for row in cycle_windows
                ]
                if APERTURE_NODE_ID not in cycle_window_nodes:
                    continue
                raw_windows, trace_nodes, trace_signatures, metrics = build_trace(
                    symbols,
                    assoc_by_word,
                    rewrite_edge_by_pair,
                )
                payloads.append(
                    {
                        "walk_length": length,
                        "carriers": carriers,
                        "edge_ids": edge_ids,
                        "atoms": list(atoms),
                        "symbols": list(symbols),
                        "cycle_window_nodes": cycle_window_nodes,
                        "trace_nodes": trace_nodes,
                        "trace_signatures": trace_signatures,
                        "metrics": metrics,
                        "raw_windows": raw_windows,
                        "repeated_interior_carrier_count": repeated_interior_carrier_count(carriers),
                        "immediate_backtrack_count": immediate_backtrack_count(carriers),
                    }
                )

    payloads = sorted(
        payloads,
        key=lambda row: (
            int(row["metrics"]["trace_detour_overhead"]),
            int(row["metrics"]["signature_valley_depth"]),
            int(row["metrics"]["metric_gromov_delta_twice"]),
            int(row["metrics"]["trace_signature_total_variation"]),
            int(row["walk_length"]),
            row["edge_ids"],
            row["atoms"],
        ),
    )
    best_score = None
    baseline_score = (
        BASELINE_TAIL_OVERHEAD,
        BASELINE_TAIL_VALLEY,
        BASELINE_TAIL_DELTA_TWICE,
        BASELINE_TAIL_VARIATION,
    )
    candidate_rows: list[dict[str, int]] = []
    for rank_order, payload in enumerate(payloads, start=1):
        metrics = payload["metrics"]
        score = (
            int(metrics["trace_detour_overhead"]),
            int(metrics["signature_valley_depth"]),
            int(metrics["metric_gromov_delta_twice"]),
            int(metrics["trace_signature_total_variation"]),
        )
        if best_score is None:
            best_score = score
        carriers = padded(payload["carriers"], 8)
        edge_ids = padded(payload["edge_ids"], 7)
        atoms = padded(payload["atoms"], 7)
        symbols = padded(payload["symbols"], 7)
        cycle_nodes = padded(payload["cycle_window_nodes"], 7)
        trace_nodes = payload["trace_nodes"]
        row = {
            "walk_candidate_id": len(candidate_rows),
            "rank_order": rank_order,
            "walk_length": int(payload["walk_length"]),
            "carrier_0_id": carriers[0],
            "carrier_1_id": carriers[1],
            "carrier_2_id": carriers[2],
            "carrier_3_id": carriers[3],
            "carrier_4_id": carriers[4],
            "carrier_5_id": carriers[5],
            "carrier_6_id": carriers[6],
            "carrier_7_id": carriers[7],
            "cell_edge_0_id": edge_ids[0],
            "cell_edge_1_id": edge_ids[1],
            "cell_edge_2_id": edge_ids[2],
            "cell_edge_3_id": edge_ids[3],
            "cell_edge_4_id": edge_ids[4],
            "cell_edge_5_id": edge_ids[5],
            "cell_edge_6_id": edge_ids[6],
            "selected_atom_0_id": atoms[0],
            "selected_atom_1_id": atoms[1],
            "selected_atom_2_id": atoms[2],
            "selected_atom_3_id": atoms[3],
            "selected_atom_4_id": atoms[4],
            "selected_atom_5_id": atoms[5],
            "selected_atom_6_id": atoms[6],
            "selected_symbol_0_id": symbols[0],
            "selected_symbol_1_id": symbols[1],
            "selected_symbol_2_id": symbols[2],
            "selected_symbol_3_id": symbols[3],
            "selected_symbol_4_id": symbols[4],
            "selected_symbol_5_id": symbols[5],
            "selected_symbol_6_id": symbols[6],
            "cycle_window_node_0_id": cycle_nodes[0],
            "cycle_window_node_1_id": cycle_nodes[1],
            "cycle_window_node_2_id": cycle_nodes[2],
            "cycle_window_node_3_id": cycle_nodes[3],
            "cycle_window_node_4_id": cycle_nodes[4],
            "cycle_window_node_5_id": cycle_nodes[5],
            "cycle_window_node_6_id": cycle_nodes[6],
            "repeated_interior_carrier_count": int(
                payload["repeated_interior_carrier_count"]
            ),
            "immediate_backtrack_count": int(payload["immediate_backtrack_count"]),
            "trace_node_count": len(trace_nodes),
            "trace_edge_count": int(metrics["trace_edge_count"]),
            "trace_detour_overhead": int(metrics["trace_detour_overhead"]),
            "trace_signature_total_variation": int(
                metrics["trace_signature_total_variation"]
            ),
            "signature_valley_depth": int(metrics["signature_valley_depth"]),
            "trace_min_signature_after_node42": int(
                metrics["trace_min_signature_after_node42"]
            ),
            "metric_gromov_delta_twice": int(metrics["metric_gromov_delta_twice"]),
            "metric_diameter": int(metrics["metric_diameter"]),
            "metric_radius": int(metrics["metric_radius"]),
            "first_node44_trace_rank": int(metrics["first_node44_trace_rank"]),
            "node44_realization_flag": int(
                APERTURE_NODE_ID in payload["cycle_window_nodes"]
            ),
            "first_selected_x2_flag": int(symbols[0] == X2_SYMBOL_ID),
            "immediate_x1_tail_flag": int(symbols[1] == X1_SYMBOL_ID),
            "nonsimple_walk_flag": int(not is_simple_closed_walk(payload["carriers"])),
            "no_intermediate_origin_flag": int(no_intermediate_origin(payload["carriers"])),
            "improves_tail_overhead_flag": int(
                int(metrics["trace_detour_overhead"]) < BASELINE_TAIL_OVERHEAD
            ),
            "contains_node27_after_node42_flag": int(
                len(trace_nodes) >= 3
                and trace_nodes[0] == TRACE_BOUNDARY_NODE_ID
                and trace_nodes[1] == STRICT_APERTURE_NODE_ID
                and trace_nodes[2] == TAIL_VALLEY_NODE_ID
            ),
            "matches_baseline_tail_score_flag": int(score == baseline_score),
            "best_backtrack_flag": int(score == best_score),
        }
        candidate_rows.append(row)

    candidate_table = table_from_rows(WALK_CANDIDATE_COLUMNS, candidate_rows)
    length_counts = Counter(int(row["walk_length"]) for row in candidate_rows)
    overhead_histogram = Counter(
        int(row["trace_detour_overhead"]) for row in candidate_rows
    )
    best_rows = [row for row in candidate_rows if int(row["best_backtrack_flag"]) == 1]
    observable_values = {
        "rooted_closed_5_walk_count": rooted_closed_counts[5],
        "rooted_closed_6_walk_count": rooted_closed_counts[6],
        "rooted_closed_7_walk_count": rooted_closed_counts[7],
        "simple_5_walk_count": simple_counts[5],
        "simple_6_walk_count": simple_counts[6],
        "simple_7_walk_count": simple_counts[7],
        "nonsimple_5_walk_count": nonsimple_counts[5],
        "nonsimple_6_walk_count": nonsimple_counts[6],
        "nonsimple_7_walk_count": nonsimple_counts[7],
        "first_x2_5_walk_count": prefilter_counts[(5, "first_x2")],
        "first_x2_6_walk_count": prefilter_counts[(6, "first_x2")],
        "first_x2_7_walk_count": prefilter_counts[(7, "first_x2")],
        "first_x2_x1_tail_5_walk_count": prefilter_counts[
            (5, "first_x2_x1_tail")
        ],
        "first_x2_x1_tail_6_walk_count": prefilter_counts[
            (6, "first_x2_x1_tail")
        ],
        "first_x2_x1_tail_7_walk_count": prefilter_counts[
            (7, "first_x2_x1_tail")
        ],
        "node44_5_candidate_count": length_counts[5],
        "node44_6_candidate_count": length_counts[6],
        "node44_7_candidate_count": length_counts[7],
        "node44_candidate_count": len(candidate_rows),
        "best_trace_overhead": min(
            int(row["trace_detour_overhead"]) for row in candidate_rows
        ),
        "improvement_candidate_count": sum(
            int(row["improves_tail_overhead_flag"]) for row in candidate_rows
        ),
        "baseline_matching_candidate_count": sum(
            int(row["matches_baseline_tail_score_flag"]) for row in candidate_rows
        ),
        "best_backtrack_candidate_count": len(best_rows),
        "best_backtrack_5_candidate_count": sum(
            int(row["walk_length"] == 5) for row in best_rows
        ),
        "best_backtrack_6_candidate_count": sum(
            int(row["walk_length"] == 6) for row in best_rows
        ),
        "best_backtrack_7_candidate_count": sum(
            int(row["walk_length"] == 7) for row in best_rows
        ),
        "immediate_backtrack_candidate_count": sum(
            int(row["immediate_backtrack_count"] > 0) for row in candidate_rows
        ),
        "best_immediate_backtrack_candidate_count": sum(
            int(row["immediate_backtrack_count"] > 0) for row in best_rows
        ),
        "node27_forced_candidate_count": sum(
            int(row["contains_node27_after_node42_flag"]) for row in candidate_rows
        ),
        "distinct_symbol_word_count": len(
            {
                tuple(
                    int(row[f"selected_symbol_{index}_id"])
                    for index in range(int(row["walk_length"]))
                )
                for row in candidate_rows
            }
        ),
        "distinct_trace_node_count": len(
            {tuple(payload["trace_nodes"]) for payload in payloads}
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

    backtrack_histogram = Counter(
        int(row["immediate_backtrack_count"]) for row in candidate_rows
    )
    repeated_histogram = Counter(
        int(row["repeated_interior_carrier_count"]) for row in candidate_rows
    )
    best_backtrack_histogram = Counter(
        int(row["immediate_backtrack_count"]) for row in best_rows
    )
    best_repeated_histogram = Counter(
        int(row["repeated_interior_carrier_count"]) for row in best_rows
    )
    checks = {
        "tail_hybrid_report_certified": tail_report.get("status")
        == TAIL_HYBRID_STATUS,
        "tail_hybrid_certificate_certified": tail_certificate.get("status")
        == TAIL_HYBRID_STATUS,
        "tail_hybrid_schema_available": tail_search.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_tail_hybrid_search@1",
        "tail_hybrid_candidate_table_shape_is_127_by_50": tuple(
            tail_candidate_table.shape
        )
        == (127, 50),
        "cell_complex_report_certified": cell_report.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "cell_complex_certificate_certified": cell_certificate.get("status")
        == "C985_D20_SIGNATURE_RESIDUAL_CELL_COMPLEX_CERTIFIED",
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "symbolic_associativity_report_certified": associativity_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "symbolic_associativity_certificate_certified": associativity_certificate.get(
            "status"
        )
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "rooted_closed_walk_counts_match": rooted_closed_counts
        == {5: 1680, 6: 10004, 7: 59548},
        "simple_walk_counts_match": simple_counts == {5: 938, 6: 3326, 7: 9980},
        "nonsimple_walk_counts_match": nonsimple_counts
        == {5: 742, 6: 6678, 7: 49568},
        "prefilter_counts_match": prefilter_counts[(5, "first_x2")] == 304
        and prefilter_counts[(6, "first_x2")] == 2666
        and prefilter_counts[(7, "first_x2")] == 19640
        and prefilter_counts[(5, "first_x2_x1_tail")] == 87
        and prefilter_counts[(6, "first_x2_x1_tail")] == 789
        and prefilter_counts[(7, "first_x2_x1_tail")] == 5749,
        "node44_candidate_counts_match": length_counts[5] == 1
        and length_counts[6] == 77
        and length_counts[7] == 1209
        and len(candidate_rows) == 1287,
        "all_candidates_are_nonsimple_first_return_walks": all(
            int(row["nonsimple_walk_flag"]) == 1
            and int(row["no_intermediate_origin_flag"]) == 1
            for row in candidate_rows
        ),
        "all_candidates_select_x2_then_x1": all(
            int(row["first_selected_x2_flag"]) == 1
            and int(row["immediate_x1_tail_flag"]) == 1
            for row in candidate_rows
        ),
        "all_candidates_realize_node44": all(
            int(row["node44_realization_flag"]) == 1 for row in candidate_rows
        ),
        "all_candidates_force_node27_after_node42": observable_values[
            "node27_forced_candidate_count"
        ]
        == len(candidate_rows),
        "no_candidate_improves_tail_overhead": observable_values[
            "improvement_candidate_count"
        ]
        == 0,
        "best_trace_overhead_equals_baseline_3": observable_values[
            "best_trace_overhead"
        ]
        == BASELINE_TAIL_OVERHEAD,
        "best_backtrack_score_matches_tail_baseline": best_score
        == baseline_score,
        "best_backtrack_count_is_103": len(best_rows) == 103,
        "best_backtrack_length_split_is_1_8_94": observable_values[
            "best_backtrack_5_candidate_count"
        ]
        == 1
        and observable_values["best_backtrack_6_candidate_count"] == 8
        and observable_values["best_backtrack_7_candidate_count"] == 94,
        "backtrack_candidates_do_not_improve": all(
            int(row["trace_detour_overhead"]) >= BASELINE_TAIL_OVERHEAD
            for row in candidate_rows
            if int(row["immediate_backtrack_count"]) > 0
        ),
        "overhead_histogram_matches": dict(overhead_histogram)
        == {3: 240, 4: 157, 5: 604, 6: 286},
        "immediate_backtrack_histogram_matches": dict(backtrack_histogram)
        == {0: 406, 1: 736, 2: 145},
        "repeated_interior_histogram_matches": dict(repeated_histogram)
        == {1: 993, 2: 290, 3: 4},
        "candidate_table_shape_is_1287_by_codebook": tuple(candidate_table.shape)
        == (1287, len(WALK_CANDIDATE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "search_lengths": SEARCH_LENGTHS,
        "rooted_closed_walk_counts": {
            str(length): rooted_closed_counts[length] for length in SEARCH_LENGTHS
        },
        "simple_walk_counts": {
            str(length): simple_counts[length] for length in SEARCH_LENGTHS
        },
        "nonsimple_walk_counts": {
            str(length): nonsimple_counts[length] for length in SEARCH_LENGTHS
        },
        "node44_candidate_count": len(candidate_rows),
        "candidate_count_by_length": {
            str(length): length_counts[length] for length in SEARCH_LENGTHS
        },
        "overhead_histogram": {
            str(key): overhead_histogram[key] for key in sorted(overhead_histogram)
        },
        "immediate_backtrack_histogram": {
            str(key): backtrack_histogram[key] for key in sorted(backtrack_histogram)
        },
        "repeated_interior_carrier_histogram": {
            str(key): repeated_histogram[key] for key in sorted(repeated_histogram)
        },
        "best_backtrack_count": len(best_rows),
        "best_backtrack_count_by_length": {
            "5": observable_values["best_backtrack_5_candidate_count"],
            "6": observable_values["best_backtrack_6_candidate_count"],
            "7": observable_values["best_backtrack_7_candidate_count"],
        },
        "best_immediate_backtrack_histogram": {
            str(key): best_backtrack_histogram[key]
            for key in sorted(best_backtrack_histogram)
        },
        "best_repeated_interior_carrier_histogram": {
            str(key): best_repeated_histogram[key]
            for key in sorted(best_repeated_histogram)
        },
        "best_backtrack_score": {
            "trace_detour_overhead": BASELINE_TAIL_OVERHEAD,
            "signature_valley_depth": BASELINE_TAIL_VALLEY,
            "metric_gromov_delta": float(BASELINE_TAIL_DELTA_TWICE / 2.0),
            "trace_signature_total_variation": BASELINE_TAIL_VARIATION,
        },
        "forced_trace_prefix": [
            TRACE_BOUNDARY_NODE_ID,
            STRICT_APERTURE_NODE_ID,
            TAIL_VALLEY_NODE_ID,
        ],
        "best_trace_node_sequence": [
            TRACE_BOUNDARY_NODE_ID,
            STRICT_APERTURE_NODE_ID,
            TAIL_VALLEY_NODE_ID,
            28,
            34,
            APERTURE_NODE_ID,
        ],
        "best_backtrack_edge_cycles_prefix": [
            [
                int(row[f"cell_edge_{index}_id"])
                for index in range(int(row["walk_length"]))
            ]
            for row in best_rows[:12]
        ],
        "candidate_table_sha256": sha_array(candidate_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    bounded_search = {
        "schema": "c985.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1",
        "object": "d20",
        "search_rule": {
            "carrier_scope": "rooted first-return closed carrier walks of length 5, 6, and 7 from carrier 12",
            "simplicity": "exclude simple cycles and retain only walks with repeated interior carriers",
            "atom_selector": "first selected atom is x2 atom 7 and second selected atom is x1 atom 4",
            "aperture_filter": "at least one cyclic selected-symbol window realizes node 44",
            "metric": "same anchored rewrite trace metric as the aperture-cycle ranking",
        },
        "summary": {
            "node44_candidate_count": len(candidate_rows),
            "best_trace_overhead": observable_values["best_trace_overhead"],
            "improvement_candidate_count": observable_values[
                "improvement_candidate_count"
            ],
            "best_backtrack_candidate_count": len(best_rows),
            "node27_forced_candidate_count": observable_values[
                "node27_forced_candidate_count"
            ],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_bounded_backtrack_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_BOUNDED_BACKTRACK_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "there are 1287 non-simple first-return closed-walk candidates of length 5, 6, or 7 with first x2, immediate x1 tail, and node44 realization",
            "allowing repeated interior carriers and immediate backtracks does not reduce the x1-tail trace overhead below 3",
            "every surviving candidate begins the anchored trace 48 -> 42 -> 27, so the node27 valley is forced in this finite bounded-walk window",
            "the 103 best candidates match the existing x1-tail baseline score overhead 3, valley 37, delta 0.5, variation 127",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_bounded_backtrack_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "In rooted first-return non-simple closed carrier walks of length "
            "5, 6, and 7 with first x2 and immediate x1-tail preservation, "
            "no node44 candidate reduces trace detour below 3; all surviving "
            "traces pass through node27 immediately after node42."
        ),
        "stage_protocol": {
            "draft": "enumerate rooted first-return closed walks with repeated interior carriers",
            "witness": "materialize selected atom words, node44 hits, backtrack counts, repeated-carrier counts, and anchored traces",
            "coherence": "rank by the established trace overhead, valley depth, Gromov delta, and variation metric",
            "closure": "certify no lower-overhead x1-tail candidate and forced node27 valley in the bounded non-simple window",
            "emit": "emit bounded-walk JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "tail_hybrid_report": input_entry(
                TAIL_HYBRID_REPORT,
                {
                    "status": tail_report.get("status"),
                    "certificate_sha256": tail_report.get("certificate_sha256"),
                },
            ),
            "tail_hybrid_json": input_entry(TAIL_HYBRID_JSON),
            "tail_hybrid_candidates": input_entry(TAIL_HYBRID_CANDIDATES),
            "tail_hybrid_tables": input_entry(TAIL_HYBRID_TABLES),
            "tail_hybrid_certificate": input_entry(TAIL_HYBRID_CERTIFICATE),
            "cell_complex_report": input_entry(
                CELL_COMPLEX_REPORT,
                {
                    "status": cell_report.get("status"),
                    "certificate_sha256": cell_report.get("certificate_sha256"),
                },
            ),
            "cell_complex_edges": input_entry(CELL_COMPLEX_EDGES),
            "cell_complex_tables": input_entry(CELL_COMPLEX_TABLES),
            "cell_complex_certificate": input_entry(CELL_COMPLEX_CERTIFICATE),
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGES),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "symbolic_associativity_report": input_entry(
                SYMBOLIC_ASSOCIATIVITY_REPORT,
                {
                    "status": associativity_report.get("status"),
                    "certificate_sha256": associativity_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "symbolic_associativity_csv": input_entry(SYMBOLIC_ASSOCIATIVITY_CSV),
            "symbolic_associativity_tables": input_entry(
                SYMBOLIC_ASSOCIATIVITY_TABLES
            ),
            "symbolic_associativity_certificate": input_entry(
                SYMBOLIC_ASSOCIATIVITY_CERTIFICATE
            ),
            "symbolic_alphabet": input_entry(SYMBOLIC_ALPHABET_CSV),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_bounded_backtrack_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_bounded_backtrack_search.json"
            ),
            "aperture_bounded_backtrack_candidates_csv": relpath(
                OUT_DIR / "aperture_bounded_backtrack_candidates.csv"
            ),
            "aperture_bounded_backtrack_observables_csv": relpath(
                OUT_DIR / "aperture_bounded_backtrack_observables.csv"
            ),
            "signature_boundary_spine_aperture_bounded_backtrack_search_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_bounded_backtrack_search_tables.npz"
            ),
            "signature_boundary_spine_aperture_bounded_backtrack_search_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_bounded_backtrack_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all rooted first-return closed carrier walks of length 5, 6, and 7 from carrier 12",
                "the non-simple repeated-interior-carrier subfamily of those walks",
                "the atom-selected first x2 and immediate x1-tail filter",
                "node44 realization and anchored rewrite trace metrics for all surviving candidates",
                "no trace-overhead improvement below 3 and forced trace prefix 48 -> 42 -> 27 in this finite bounded-walk window",
            ],
            "does_not_certify_because_not_required": [
                "walks longer than seven carrier edges",
                "walks that revisit carrier 12 before the final closure",
                "simple length-seven cycles outside the repeated-carrier backtrack scope",
                "tail preservation not represented by immediate selected x1 after selected x2",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Move from carrier walks to symbol-state automata: quotient the "
            "bounded-walk search by anchored trace nodes and selected-symbol "
            "suffixes, then compute the minimal forbidden transition that "
            "would skip node27 while preserving first x2 and immediate x1."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_bounded_backtrack_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified tail-hybrid, cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "enumerate rooted first-return closed walks of length 5, 6, and 7 from carrier 12",
            "retain only non-simple repeated-interior-carrier walks",
            "filter to first selected atom x2, immediate selected atom x1, and node44 realization",
            "rank each surviving anchored rewrite trace against the x1-tail baseline and check forced node27 valley",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_bounded_backtrack_search": bounded_search,
        "aperture_bounded_backtrack_candidates_csv": csv_text(
            WALK_CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_bounded_backtrack_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_bounded_backtrack_search_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_bounded_backtrack_search.json",
        payloads["signature_boundary_spine_aperture_bounded_backtrack_search"],
    )
    (OUT_DIR / "aperture_bounded_backtrack_candidates.csv").write_text(
        payloads["aperture_bounded_backtrack_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_bounded_backtrack_observables.csv").write_text(
        payloads["aperture_bounded_backtrack_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_bounded_backtrack_search_tables.npz",
        candidate_table=payloads["candidate_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR
        / "signature_boundary_spine_aperture_bounded_backtrack_search_certificate.json",
        payloads[
            "signature_boundary_spine_aperture_bounded_backtrack_search_certificate"
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
                "node44_candidate_count": witness["node44_candidate_count"],
                "overhead_histogram": witness["overhead_histogram"],
                "best_backtrack_count": witness["best_backtrack_count"],
                "forced_trace_prefix": witness["forced_trace_prefix"],
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
