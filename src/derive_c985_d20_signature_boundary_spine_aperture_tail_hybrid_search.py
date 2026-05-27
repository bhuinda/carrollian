from __future__ import annotations

import itertools
import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff import (
        OUT_DIR as ATOM_TRADEOFF_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_TABLES,
        GEODESIC_MIN_AFTER_NODE42,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_signature_boundary_spine_typed_corridors import (
        SYMBOLIC_ALPHABET_CSV,
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
    from derive_c985_d20_signature_boundary_spine_aperture_atom_selected_tradeoff import (
        OUT_DIR as ATOM_TRADEOFF_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_aperture_cycle_ranking import (
        APERTURE_NODE_ID,
        CELL_COMPLEX_EDGES,
        CELL_COMPLEX_TABLES,
        GEODESIC_MIN_AFTER_NODE42,
        REWRITE_COMPLEX_EDGES,
        REWRITE_COMPLEX_TABLES,
        SYMBOLIC_ASSOCIATIVITY_CSV,
        SYMBOLIC_ASSOCIATIVITY_TABLES,
        build_trace,
        edge_key,
        associativity_lookup,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_signature_boundary_spine_typed_corridors import (
        SYMBOLIC_ALPHABET_CSV,
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


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_tail_hybrid_search"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_TAIL_HYBRID_SEARCH_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

ATOM_TRADEOFF_REPORT = ATOM_TRADEOFF_DIR / "report.json"
ATOM_TRADEOFF_JSON = (
    ATOM_TRADEOFF_DIR / "signature_boundary_spine_aperture_atom_selected_tradeoff.json"
)
ATOM_TRADEOFF_CANDIDATES = (
    ATOM_TRADEOFF_DIR / "aperture_atom_selected_tradeoff_candidates.csv"
)
ATOM_TRADEOFF_TABLES = (
    ATOM_TRADEOFF_DIR / "signature_boundary_spine_aperture_atom_selected_tradeoff_tables.npz"
)
ATOM_TRADEOFF_CERTIFICATE = (
    ATOM_TRADEOFF_DIR
    / "signature_boundary_spine_aperture_atom_selected_tradeoff_certificate.json"
)

CELL_COMPLEX_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_signature_residual_cell_complex"
    / "report.json"
)
CELL_COMPLEX_CERTIFICATE = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_signature_residual_cell_complex"
    / "signature_residual_cell_complex_certificate.json"
)
REWRITE_COMPLEX_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_rewrite_complex_hyperbolicity"
    / "report.json"
)
REWRITE_COMPLEX_CERTIFICATE = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_rewrite_complex_hyperbolicity"
    / "rewrite_complex_certificate.json"
)
SYMBOLIC_ASSOCIATIVITY_REPORT = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_symbolic_associativity"
    / "report.json"
)
SYMBOLIC_ASSOCIATIVITY_CERTIFICATE = (
    D20_INVARIANTS
    / "proof_obligations"
    / "c985_d20_symbolic_associativity"
    / "symbolic_associativity_certificate.json"
)

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_tail_hybrid_search.py"
)

ORIGIN_CARRIER_ID = 12
X2_ATOM_ID = 7
X1_ATOM_ID = 4
X2_SYMBOL_ID = 2
X1_SYMBOL_ID = 1
SEARCH_LENGTHS = [5, 6]
BASELINE_TAIL_OVERHEAD = 3
BASELINE_TAIL_VALLEY = 37
BASELINE_TAIL_DELTA_TWICE = 1
BASELINE_TAIL_VARIATION = 127

HYBRID_CANDIDATE_COLUMNS = [
    "hybrid_candidate_id",
    "rank_order",
    "cycle_length",
    "carrier_0_id",
    "carrier_1_id",
    "carrier_2_id",
    "carrier_3_id",
    "carrier_4_id",
    "carrier_5_id",
    "carrier_6_id",
    "cell_edge_0_id",
    "cell_edge_1_id",
    "cell_edge_2_id",
    "cell_edge_3_id",
    "cell_edge_4_id",
    "cell_edge_5_id",
    "selected_atom_0_id",
    "selected_atom_1_id",
    "selected_atom_2_id",
    "selected_atom_3_id",
    "selected_atom_4_id",
    "selected_atom_5_id",
    "selected_symbol_0_id",
    "selected_symbol_1_id",
    "selected_symbol_2_id",
    "selected_symbol_3_id",
    "selected_symbol_4_id",
    "selected_symbol_5_id",
    "cycle_window_node_0_id",
    "cycle_window_node_1_id",
    "cycle_window_node_2_id",
    "cycle_window_node_3_id",
    "cycle_window_node_4_id",
    "cycle_window_node_5_id",
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
    "improves_tail_overhead_flag",
    "matches_baseline_tail_score_flag",
    "best_hybrid_flag",
]

OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "rooted_simple_5_cycle_count": 0,
    "rooted_simple_6_cycle_count": 1,
    "first_x2_5_cycle_count": 2,
    "first_x2_6_cycle_count": 3,
    "first_x2_x1_tail_5_cycle_count": 4,
    "first_x2_x1_tail_6_cycle_count": 5,
    "node44_hybrid_5_candidate_count": 6,
    "node44_hybrid_6_candidate_count": 7,
    "node44_hybrid_candidate_count": 8,
    "best_trace_overhead": 9,
    "improvement_candidate_count": 10,
    "baseline_matching_candidate_count": 11,
    "best_hybrid_candidate_count": 12,
    "best_hybrid_5_candidate_count": 13,
    "best_hybrid_6_candidate_count": 14,
    "max_trace_overhead": 15,
    "distinct_symbol_word_count": 16,
    "distinct_trace_node_count": 17,
}


def bit_ids(mask: int) -> list[int]:
    return [index for index in range(64) if int(mask) & (1 << index)]


def shared_atoms(edge: dict[str, int]) -> list[int]:
    return bit_ids(
        int(edge["source_carrier_atom_mask"]) & int(edge["target_carrier_atom_mask"])
    )


def rooted_simple_cycles(
    adjacency: dict[int, list[int]],
    edge_count: int,
) -> list[list[int]]:
    cycles: list[list[int]] = []

    def rec(path: list[int]) -> None:
        if len(path) == edge_count:
            if ORIGIN_CARRIER_ID in adjacency.get(path[-1], []):
                cycles.append([*path, ORIGIN_CARRIER_ID])
            return
        for neighbor in sorted(adjacency.get(path[-1], [])):
            if neighbor == ORIGIN_CARRIER_ID or neighbor in path:
                continue
            rec([*path, neighbor])

    rec([ORIGIN_CARRIER_ID])
    return cycles


def padded(values: list[int], size: int) -> list[int]:
    return [*values, *([-1] * (size - len(values)))]


def build_payloads() -> dict[str, Any]:
    atom_tradeoff_report = load_json(ATOM_TRADEOFF_REPORT)
    atom_tradeoff = load_json(ATOM_TRADEOFF_JSON)
    atom_tradeoff_certificate = load_json(ATOM_TRADEOFF_CERTIFICATE)
    cell_report = load_json(CELL_COMPLEX_REPORT)
    cell_certificate = load_json(CELL_COMPLEX_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)
    associativity_report = load_json(SYMBOLIC_ASSOCIATIVITY_REPORT)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)

    atom_tradeoff_tables = np.load(ATOM_TRADEOFF_TABLES, allow_pickle=False)
    cell_tables = np.load(CELL_COMPLEX_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    atom_tradeoff_candidate_table = np.asarray(
        atom_tradeoff_tables["candidate_table"],
        dtype=np.int64,
    )
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

    rooted_cycle_counts = {
        length: len(rooted_simple_cycles(adjacency, length))
        for length in SEARCH_LENGTHS
    }
    prefilter_counts: Counter[tuple[int, str]] = Counter()
    payloads: list[dict[str, Any]] = []

    for length in SEARCH_LENGTHS:
        for carriers in rooted_simple_cycles(adjacency, length):
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
                if not any(
                    int(row["canonical_triple_id"]) == APERTURE_NODE_ID
                    for row in cycle_windows
                ):
                    continue
                raw_windows, trace_nodes, trace_signatures, metrics = build_trace(
                    symbols,
                    assoc_by_word,
                    rewrite_edge_by_pair,
                )
                payloads.append(
                    {
                        "cycle_length": length,
                        "carriers": carriers,
                        "edge_ids": edge_ids,
                        "atoms": list(atoms),
                        "symbols": list(symbols),
                        "cycle_window_nodes": [
                            int(row["canonical_triple_id"]) for row in cycle_windows
                        ],
                        "trace_nodes": trace_nodes,
                        "trace_signatures": trace_signatures,
                        "metrics": metrics,
                        "raw_windows": raw_windows,
                    }
                )

    payloads = sorted(
        payloads,
        key=lambda row: (
            int(row["metrics"]["trace_detour_overhead"]),
            int(row["metrics"]["signature_valley_depth"]),
            int(row["metrics"]["metric_gromov_delta_twice"]),
            int(row["metrics"]["trace_signature_total_variation"]),
            int(row["cycle_length"]),
            row["edge_ids"],
            row["atoms"],
        ),
    )
    best_score = None
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
        carriers = padded(payload["carriers"], 7)
        edge_ids = padded(payload["edge_ids"], 6)
        atoms = padded(payload["atoms"], 6)
        symbols = padded(payload["symbols"], 6)
        cycle_nodes = padded(payload["cycle_window_nodes"], 6)
        row = {
            "hybrid_candidate_id": len(candidate_rows),
            "rank_order": rank_order,
            "cycle_length": int(payload["cycle_length"]),
            "carrier_0_id": carriers[0],
            "carrier_1_id": carriers[1],
            "carrier_2_id": carriers[2],
            "carrier_3_id": carriers[3],
            "carrier_4_id": carriers[4],
            "carrier_5_id": carriers[5],
            "carrier_6_id": carriers[6],
            "cell_edge_0_id": edge_ids[0],
            "cell_edge_1_id": edge_ids[1],
            "cell_edge_2_id": edge_ids[2],
            "cell_edge_3_id": edge_ids[3],
            "cell_edge_4_id": edge_ids[4],
            "cell_edge_5_id": edge_ids[5],
            "selected_atom_0_id": atoms[0],
            "selected_atom_1_id": atoms[1],
            "selected_atom_2_id": atoms[2],
            "selected_atom_3_id": atoms[3],
            "selected_atom_4_id": atoms[4],
            "selected_atom_5_id": atoms[5],
            "selected_symbol_0_id": symbols[0],
            "selected_symbol_1_id": symbols[1],
            "selected_symbol_2_id": symbols[2],
            "selected_symbol_3_id": symbols[3],
            "selected_symbol_4_id": symbols[4],
            "selected_symbol_5_id": symbols[5],
            "cycle_window_node_0_id": cycle_nodes[0],
            "cycle_window_node_1_id": cycle_nodes[1],
            "cycle_window_node_2_id": cycle_nodes[2],
            "cycle_window_node_3_id": cycle_nodes[3],
            "cycle_window_node_4_id": cycle_nodes[4],
            "cycle_window_node_5_id": cycle_nodes[5],
            "trace_node_count": len(payload["trace_nodes"]),
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
            "improves_tail_overhead_flag": int(
                int(metrics["trace_detour_overhead"]) < BASELINE_TAIL_OVERHEAD
            ),
            "matches_baseline_tail_score_flag": int(score == best_score),
            "best_hybrid_flag": int(score == best_score),
        }
        candidate_rows.append(row)

    candidate_table = table_from_rows(HYBRID_CANDIDATE_COLUMNS, candidate_rows)
    length_counts = Counter(int(row["cycle_length"]) for row in candidate_rows)
    best_rows = [row for row in candidate_rows if int(row["best_hybrid_flag"]) == 1]
    observable_values = {
        "rooted_simple_5_cycle_count": rooted_cycle_counts[5],
        "rooted_simple_6_cycle_count": rooted_cycle_counts[6],
        "first_x2_5_cycle_count": prefilter_counts[(5, "first_x2")],
        "first_x2_6_cycle_count": prefilter_counts[(6, "first_x2")],
        "first_x2_x1_tail_5_cycle_count": prefilter_counts[
            (5, "first_x2_x1_tail")
        ],
        "first_x2_x1_tail_6_cycle_count": prefilter_counts[
            (6, "first_x2_x1_tail")
        ],
        "node44_hybrid_5_candidate_count": length_counts[5],
        "node44_hybrid_6_candidate_count": length_counts[6],
        "node44_hybrid_candidate_count": len(candidate_rows),
        "best_trace_overhead": min(
            int(row["trace_detour_overhead"]) for row in candidate_rows
        ),
        "improvement_candidate_count": sum(
            int(row["improves_tail_overhead_flag"]) for row in candidate_rows
        ),
        "baseline_matching_candidate_count": sum(
            int(row["matches_baseline_tail_score_flag"]) for row in candidate_rows
        ),
        "best_hybrid_candidate_count": len(best_rows),
        "best_hybrid_5_candidate_count": sum(
            int(row["cycle_length"] == 5) for row in best_rows
        ),
        "best_hybrid_6_candidate_count": sum(
            int(row["cycle_length"] == 6) for row in best_rows
        ),
        "max_trace_overhead": max(
            int(row["trace_detour_overhead"]) for row in candidate_rows
        ),
        "distinct_symbol_word_count": len(
            {
                tuple(
                    int(row[f"selected_symbol_{index}_id"])
                    for index in range(int(row["cycle_length"]))
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

    overhead_histogram = Counter(
        int(row["trace_detour_overhead"]) for row in candidate_rows
    )
    valley_histogram = Counter(int(row["signature_valley_depth"]) for row in candidate_rows)
    checks = {
        "atom_tradeoff_report_certified": atom_tradeoff_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTED_TRADEOFF_CERTIFIED",
        "atom_tradeoff_certificate_certified": atom_tradeoff_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_ATOM_SELECTED_TRADEOFF_CERTIFIED",
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
        "atom_tradeoff_schema_available": atom_tradeoff.get("schema")
        == "c985.d20_signature_boundary_spine_aperture_atom_selected_tradeoff@1",
        "atom_tradeoff_candidate_table_shape_is_10_by_26": tuple(
            atom_tradeoff_candidate_table.shape
        )
        == (10, 26),
        "cell_complex_edge_table_shape_is_44_by_13": tuple(cell_edge_table.shape)
        == (44, 13),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "associativity_table_shape_is_216_by_27": tuple(associativity_table.shape)
        == (216, 27),
        "rooted_cycle_counts_match": rooted_cycle_counts == {5: 938, 6: 3326},
        "prefilter_counts_match": prefilter_counts[(5, "first_x2")] == 368
        and prefilter_counts[(6, "first_x2")] == 1310
        and prefilter_counts[(5, "first_x2_x1_tail")] == 98
        and prefilter_counts[(6, "first_x2_x1_tail")] == 319,
        "node44_candidate_counts_match": length_counts[5] == 19
        and length_counts[6] == 108
        and len(candidate_rows) == 127,
        "all_candidates_select_x2_then_x1": all(
            int(row["first_selected_x2_flag"]) == 1
            and int(row["immediate_x1_tail_flag"]) == 1
            for row in candidate_rows
        ),
        "all_candidates_realize_node44": all(
            int(row["node44_realization_flag"]) == 1 for row in candidate_rows
        ),
        "no_candidate_improves_tail_overhead": observable_values[
            "improvement_candidate_count"
        ]
        == 0,
        "best_trace_overhead_equals_baseline_3": observable_values[
            "best_trace_overhead"
        ]
        == BASELINE_TAIL_OVERHEAD,
        "best_hybrid_score_matches_tail_baseline": best_score
        == (
            BASELINE_TAIL_OVERHEAD,
            BASELINE_TAIL_VALLEY,
            BASELINE_TAIL_DELTA_TWICE,
            BASELINE_TAIL_VARIATION,
        ),
        "best_hybrid_count_is_11": len(best_rows) == 11,
        "best_hybrid_length_split_is_3_and_8": observable_values[
            "best_hybrid_5_candidate_count"
        ]
        == 3
        and observable_values["best_hybrid_6_candidate_count"] == 8,
        "overhead_histogram_matches": dict(overhead_histogram) == {3: 27, 4: 44, 5: 56},
        "minimum_valley_depth_is_37": min(valley_histogram) == 37,
        "candidate_table_shape_is_127_by_50": tuple(candidate_table.shape)
        == (127, len(HYBRID_CANDIDATE_COLUMNS)),
        "observable_table_shape_matches_codebook": tuple(observable_table.shape)
        == (len(OBSERVABLE_CODES), len(OBSERVABLE_COLUMNS)),
    }

    witness = {
        "search_lengths": SEARCH_LENGTHS,
        "rooted_simple_cycle_counts": {
            str(length): rooted_cycle_counts[length] for length in SEARCH_LENGTHS
        },
        "node44_hybrid_candidate_count": len(candidate_rows),
        "candidate_count_by_length": {
            str(length): length_counts[length] for length in SEARCH_LENGTHS
        },
        "overhead_histogram": {
            str(key): overhead_histogram[key] for key in sorted(overhead_histogram)
        },
        "best_hybrid_count": len(best_rows),
        "best_hybrid_count_by_length": {
            "5": observable_values["best_hybrid_5_candidate_count"],
            "6": observable_values["best_hybrid_6_candidate_count"],
        },
        "best_hybrid_score": {
            "trace_detour_overhead": BASELINE_TAIL_OVERHEAD,
            "signature_valley_depth": BASELINE_TAIL_VALLEY,
            "metric_gromov_delta": float(BASELINE_TAIL_DELTA_TWICE / 2.0),
            "trace_signature_total_variation": BASELINE_TAIL_VARIATION,
        },
        "best_hybrid_edge_cycles": [
            [
                int(row[f"cell_edge_{index}_id"])
                for index in range(int(row["cycle_length"]))
            ]
            for row in best_rows
        ],
        "candidate_table_sha256": sha_array(candidate_table),
        "observable_table_sha256": sha_array(observable_table),
    }

    hybrid_search = {
        "schema": "c985.d20_signature_boundary_spine_aperture_tail_hybrid_search@1",
        "object": "d20",
        "search_rule": {
            "carrier_scope": "rooted simple carrier cycles of length 5 and 6 from carrier 12",
            "atom_selector": "first selected atom is x2 atom 7 and second selected atom is x1 atom 4",
            "aperture_filter": "at least one cyclic selected-symbol window realizes node 44",
            "metric": "same anchored rewrite trace metric as the aperture-cycle ranking",
        },
        "summary": {
            "node44_hybrid_candidate_count": len(candidate_rows),
            "best_trace_overhead": observable_values["best_trace_overhead"],
            "improvement_candidate_count": observable_values[
                "improvement_candidate_count"
            ],
            "best_hybrid_candidate_count": len(best_rows),
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_tail_hybrid_search_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_TAIL_HYBRID_SEARCH_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "there are 127 five/six-edge atom-selected candidates rooted at carrier 12 with first x2, immediate x1 tail, and node44 realization",
            "none improves on the existing x1-tail trace overhead of 3",
            "27 candidates have overhead 3 and 11 match the full baseline score overhead 3, valley 37, delta 0.5, variation 127",
            "within this finite search window, adding one or two carrier edges does not produce a lower-overhead x1-tail hybrid",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_tail_hybrid_search@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "In rooted simple five- and six-edge atom-selected carrier cycles "
            "with first x2 and immediate x1-tail preservation, no node44 "
            "candidate reduces the trace detour below 3. The missing hybrid "
            "does not appear in this finite search window."
        ),
        "stage_protocol": {
            "draft": "enumerate rooted simple carrier cycles of length 5 and 6",
            "witness": "materialize selected atom words, selected symbol words, node44 hits, and anchored traces",
            "coherence": "rank by the established trace overhead, valley depth, Gromov delta, and variation metric",
            "closure": "certify no lower-overhead x1-tail hybrid in the declared finite search window",
            "emit": "emit hybrid-search JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "atom_tradeoff_report": input_entry(
                ATOM_TRADEOFF_REPORT,
                {
                    "status": atom_tradeoff_report.get("status"),
                    "certificate_sha256": atom_tradeoff_report.get(
                        "certificate_sha256"
                    ),
                },
            ),
            "atom_tradeoff_json": input_entry(ATOM_TRADEOFF_JSON),
            "atom_tradeoff_candidates": input_entry(ATOM_TRADEOFF_CANDIDATES),
            "atom_tradeoff_tables": input_entry(ATOM_TRADEOFF_TABLES),
            "atom_tradeoff_certificate": input_entry(ATOM_TRADEOFF_CERTIFICATE),
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
            "signature_boundary_spine_aperture_tail_hybrid_search": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_tail_hybrid_search.json"
            ),
            "aperture_tail_hybrid_candidates_csv": relpath(
                OUT_DIR / "aperture_tail_hybrid_candidates.csv"
            ),
            "aperture_tail_hybrid_observables_csv": relpath(
                OUT_DIR / "aperture_tail_hybrid_observables.csv"
            ),
            "signature_boundary_spine_aperture_tail_hybrid_search_tables": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_tail_hybrid_search_tables.npz"
            ),
            "signature_boundary_spine_aperture_tail_hybrid_search_certificate": relpath(
                OUT_DIR
                / "signature_boundary_spine_aperture_tail_hybrid_search_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all rooted simple five- and six-edge carrier cycles from carrier 12 in the residual cell complex",
                "the atom-selected first x2 and immediate x1-tail filter",
                "node44 realization and anchored rewrite trace metrics for all surviving candidates",
                "no trace-overhead improvement below 3 in this finite search window",
            ],
            "does_not_certify_because_not_required": [
                "cycles longer than six carrier edges",
                "non-simple carrier cycles with repeated interior carriers",
                "tail preservation not represented by immediate selected x1 after selected x2",
                "new categorical F-symbols, pivotality, braiding, or center data",
            ],
        },
        "next_highest_yield_item": (
            "Relax the simplicity constraint while bounding repeated carriers: "
            "enumerate short atom-selected walks that keep first x2 and immediate "
            "x1, then test whether a controlled backtrack can lower the trace "
            "detour or prove the node27 valley is unavoidable for x1-tail "
            "preservation."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_tail_hybrid_search_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified atom-tradeoff, cell-complex, rewrite-complex, and symbolic-associativity artifacts",
            "enumerate rooted simple five- and six-edge carrier cycles from carrier 12",
            "filter to first selected atom x2, immediate selected atom x1, and node44 realization",
            "rank each surviving anchored rewrite trace against the x1-tail baseline",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_tail_hybrid_search": hybrid_search,
        "aperture_tail_hybrid_candidates_csv": csv_text(
            HYBRID_CANDIDATE_COLUMNS,
            candidate_rows,
        ),
        "aperture_tail_hybrid_observables_csv": csv_text(
            OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "candidate_table": candidate_table,
        "observable_table": observable_table,
        "signature_boundary_spine_aperture_tail_hybrid_search_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_tail_hybrid_search.json",
        payloads["signature_boundary_spine_aperture_tail_hybrid_search"],
    )
    (OUT_DIR / "aperture_tail_hybrid_candidates.csv").write_text(
        payloads["aperture_tail_hybrid_candidates_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_tail_hybrid_observables.csv").write_text(
        payloads["aperture_tail_hybrid_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_tail_hybrid_search_tables.npz",
        candidate_table=payloads["candidate_table"],
        observable_table=payloads["observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_tail_hybrid_search_certificate.json",
        payloads["signature_boundary_spine_aperture_tail_hybrid_search_certificate"],
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
                "node44_hybrid_candidate_count": witness[
                    "node44_hybrid_candidate_count"
                ],
                "overhead_histogram": witness["overhead_histogram"],
                "best_hybrid_count": witness["best_hybrid_count"],
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
