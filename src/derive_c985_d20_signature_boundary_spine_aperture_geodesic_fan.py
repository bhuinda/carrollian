from __future__ import annotations

import json
from collections import Counter
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_rewrite_complex_hyperbolicity import (
        OUT_DIR as REWRITE_COMPLEX_DIR,
    )
    from .derive_c985_d20_signature_boundary_spine_language_graph import (
        OUT_DIR as LANGUAGE_GRAPH_DIR,
        gromov_delta_witness,
        shortest_paths,
    )
    from .derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        read_int_csv,
        table_from_rows,
    )
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
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
    from derive_c985_d20_rewrite_complex_hyperbolicity import (
        OUT_DIR as REWRITE_COMPLEX_DIR,
    )
    from derive_c985_d20_signature_boundary_spine_language_graph import (
        OUT_DIR as LANGUAGE_GRAPH_DIR,
        gromov_delta_witness,
        shortest_paths,
    )
    from derive_c985_d20_signature_boundary_spine_routing_prefix import (
        bitset,
        read_int_csv,
        table_from_rows,
    )
    from derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_signature_boundary_spine_aperture_geodesic_fan"
STATUS = "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_GEODESIC_FAN_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

LANGUAGE_GRAPH_REPORT = LANGUAGE_GRAPH_DIR / "report.json"
LANGUAGE_GRAPH_JSON = (
    LANGUAGE_GRAPH_DIR / "signature_boundary_spine_language_graph.json"
)
LANGUAGE_GRAPH_NODE_CSV = LANGUAGE_GRAPH_DIR / "language_graph_nodes.csv"
LANGUAGE_GRAPH_EDGE_CSV = LANGUAGE_GRAPH_DIR / "language_graph_edges.csv"
LANGUAGE_APERTURE_CSV = LANGUAGE_GRAPH_DIR / "language_aperture_distances.csv"
LANGUAGE_GRAPH_TABLES = (
    LANGUAGE_GRAPH_DIR / "signature_boundary_spine_language_graph_tables.npz"
)
LANGUAGE_GRAPH_CERTIFICATE = (
    LANGUAGE_GRAPH_DIR / "signature_boundary_spine_language_graph_certificate.json"
)

REWRITE_COMPLEX_REPORT = REWRITE_COMPLEX_DIR / "report.json"
REWRITE_COMPLEX_JSON = REWRITE_COMPLEX_DIR / "rewrite_complex.json"
REWRITE_COMPLEX_NODE_CSV = REWRITE_COMPLEX_DIR / "rewrite_complex_nodes.csv"
REWRITE_COMPLEX_EDGE_CSV = REWRITE_COMPLEX_DIR / "rewrite_complex_edges.csv"
REWRITE_COMPLEX_TABLES = REWRITE_COMPLEX_DIR / "rewrite_complex_tables.npz"
REWRITE_COMPLEX_CERTIFICATE = REWRITE_COMPLEX_DIR / "rewrite_complex_certificate.json"

DERIVE_SCRIPT = (
    ROOT
    / "src"
    / "derive_c985_d20_signature_boundary_spine_aperture_geodesic_fan.py"
)
VALIDATOR_SCRIPT = (
    ROOT
    / "src"
    / "certify_c985_d20_signature_boundary_spine_aperture_geodesic_fan.py"
)

BOUNDARY_ENDPOINT_IDS = [20, 48]
APERTURE_NODE_ID = 44
APERTURE_WORD = "x2 x4 x5"
MISSING_GATE_SYMBOLS = [2, 4]
OBSERVED_SIGNATURE_THRESHOLD = 175

ROLE_BOUNDARY = 0
ROLE_INTERMEDIATE = 1
ROLE_APERTURE = 2
EDGE_BOUNDARY_TO_INTERMEDIATE = 0
EDGE_INTERMEDIATE_TO_APERTURE = 1

FAN_NODE_COLUMNS = [
    "fan_node_rank",
    "rewrite_node_id",
    "fan_role_code",
    "boundary_endpoint_flag",
    "intermediate_flag",
    "aperture_flag",
    "canonical_symbol_bitset",
    "x2_count",
    "x4_count",
    "x2_x4_symbol_count",
    "sector_coverage_count",
    "full_sector_flag",
    "signature_union_count",
    "high_signature_flag",
    "fan_degree",
    "fan_distance_to_aperture",
    "ambient_distance_to_aperture",
]

FAN_EDGE_COLUMNS = [
    "fan_edge_id",
    "source_fan_node_rank",
    "target_fan_node_rank",
    "source_rewrite_node_id",
    "target_rewrite_node_id",
    "edge_role_code",
    "path_incidence_count",
    "ambient_rewrite_distance",
    "source_sector_coverage_count",
    "target_sector_coverage_count",
    "source_signature_union_count",
    "target_signature_union_count",
]

GEODESIC_PATH_COLUMNS = [
    "geodesic_path_id",
    "source_boundary_node_id",
    "intermediate_node_id",
    "aperture_node_id",
    "source_boundary_rank",
    "intermediate_fan_node_rank",
    "path_length",
    "first_restored_symbol_id",
    "second_restored_symbol_id",
    "restoration_order_code",
    "intermediate_sector_coverage_count",
    "intermediate_full_sector_flag",
    "intermediate_signature_union_count",
    "intermediate_high_signature_flag",
    "aperture_signature_union_count",
    "restored_segment_min_signature_union_count",
    "full_sector_and_high_signature_flag",
]

RESTORATION_SUMMARY_COLUMNS = [
    "boundary_node_id",
    "geodesic_path_count",
    "full_sector_path_count",
    "high_signature_path_count",
    "full_sector_and_high_signature_path_count",
    "x2_first_path_count",
    "x4_first_path_count",
    "min_intermediate_signature_union_count",
    "max_intermediate_signature_union_count",
    "strict_best_path_id",
]

FAN_OBSERVABLE_COLUMNS = [
    "observable_id",
    "observable_code",
    "value_x1e12",
    "aux_id",
]

OBSERVABLE_CODES = {
    "boundary_endpoint_count": 0,
    "aperture_node_id": 1,
    "geodesic_path_count": 2,
    "fan_node_count": 3,
    "fan_edge_count": 4,
    "fan_graph_diameter": 5,
    "fan_graph_radius": 6,
    "fan_gromov_delta_twice": 7,
    "full_sector_intermediate_path_count": 8,
    "high_signature_intermediate_path_count": 9,
    "full_sector_and_high_signature_path_count": 10,
    "x2_first_path_count": 11,
    "x4_first_path_count": 12,
    "observed_signature_threshold": 13,
    "aperture_signature_union_count": 14,
    "max_intermediate_signature_union_count": 15,
    "min_intermediate_signature_union_count": 16,
    "boundary_to_aperture_ambient_distance": 17,
    "max_endpoint_geodesic_path_count": 18,
    "min_endpoint_geodesic_path_count": 19,
}


def node_symbols(node: dict[str, Any]) -> list[int]:
    return [int(value) for value in node["canonical_symbol_ids"]]


def symbol_count(node: dict[str, Any], symbol_id: int) -> int:
    return node_symbols(node).count(int(symbol_id))


def restored_symbol(source: dict[str, Any], target: dict[str, Any]) -> int:
    source_counts = Counter(node_symbols(source))
    target_counts = Counter(node_symbols(target))
    added = [
        symbol_id
        for symbol_id in MISSING_GATE_SYMBOLS
        if target_counts[symbol_id] > source_counts[symbol_id]
    ]
    if len(added) != 1:
        raise AssertionError("rewrite edge does not restore exactly one missing symbol")
    return int(added[0])


def build_payloads() -> dict[str, Any]:
    language_report = load_json(LANGUAGE_GRAPH_REPORT)
    language_graph = load_json(LANGUAGE_GRAPH_JSON)
    language_certificate = load_json(LANGUAGE_GRAPH_CERTIFICATE)
    rewrite_report = load_json(REWRITE_COMPLEX_REPORT)
    rewrite_complex = load_json(REWRITE_COMPLEX_JSON)
    rewrite_certificate = load_json(REWRITE_COMPLEX_CERTIFICATE)

    language_tables = np.load(LANGUAGE_GRAPH_TABLES, allow_pickle=False)
    rewrite_tables = np.load(REWRITE_COMPLEX_TABLES, allow_pickle=False)
    language_node_table = np.asarray(
        language_tables["language_node_table"], dtype=np.int64
    )
    language_edge_table = np.asarray(
        language_tables["language_edge_table"], dtype=np.int64
    )
    language_aperture_table = np.asarray(
        language_tables["language_aperture_table"], dtype=np.int64
    )
    rewrite_node_table = np.asarray(rewrite_tables["node_table"], dtype=np.int64)
    rewrite_edge_table = np.asarray(rewrite_tables["edge_table"], dtype=np.int64)
    rewrite_adjacency = np.asarray(rewrite_tables["adjacency"], dtype=np.int8)
    rewrite_distances = np.asarray(rewrite_tables["graph_distances"], dtype=np.int64)

    node_by_id = {int(row["node_id"]): row for row in rewrite_complex["nodes"]}
    aperture_node = node_by_id[APERTURE_NODE_ID]
    aperture_signature = int(aperture_node["signature_union_count"])

    path_rows: list[dict[str, int]] = []
    path_node_triples: list[list[int]] = []
    for boundary_rank, endpoint_id in enumerate(BOUNDARY_ENDPOINT_IDS):
        middle_ids = [
            node_id
            for node_id in range(int(rewrite_adjacency.shape[0]))
            if int(rewrite_adjacency[endpoint_id, node_id]) == 1
            and int(rewrite_adjacency[node_id, APERTURE_NODE_ID]) == 1
            and int(rewrite_distances[endpoint_id, APERTURE_NODE_ID]) == 2
        ]
        for intermediate_id in middle_ids:
            source_node = node_by_id[endpoint_id]
            intermediate_node = node_by_id[intermediate_id]
            first_symbol = restored_symbol(source_node, intermediate_node)
            second_symbol = restored_symbol(intermediate_node, aperture_node)
            intermediate_signature = int(intermediate_node["signature_union_count"])
            intermediate_full_sector = int(
                int(intermediate_node["sector_coverage_count"]) == 6
            )
            intermediate_high_signature = int(
                intermediate_signature >= OBSERVED_SIGNATURE_THRESHOLD
            )
            path_id = len(path_rows)
            path_rows.append(
                {
                    "geodesic_path_id": path_id,
                    "source_boundary_node_id": endpoint_id,
                    "intermediate_node_id": int(intermediate_id),
                    "aperture_node_id": APERTURE_NODE_ID,
                    "source_boundary_rank": boundary_rank,
                    "intermediate_fan_node_rank": -1,
                    "path_length": int(rewrite_distances[endpoint_id, APERTURE_NODE_ID]),
                    "first_restored_symbol_id": first_symbol,
                    "second_restored_symbol_id": second_symbol,
                    "restoration_order_code": first_symbol * 6 + second_symbol,
                    "intermediate_sector_coverage_count": int(
                        intermediate_node["sector_coverage_count"]
                    ),
                    "intermediate_full_sector_flag": intermediate_full_sector,
                    "intermediate_signature_union_count": intermediate_signature,
                    "intermediate_high_signature_flag": intermediate_high_signature,
                    "aperture_signature_union_count": aperture_signature,
                    "restored_segment_min_signature_union_count": min(
                        intermediate_signature,
                        aperture_signature,
                    ),
                    "full_sector_and_high_signature_flag": int(
                        intermediate_full_sector and intermediate_high_signature
                    ),
                }
            )
            path_node_triples.append([endpoint_id, int(intermediate_id), APERTURE_NODE_ID])

    intermediate_ids = sorted({path[1] for path in path_node_triples})
    fan_node_ids = BOUNDARY_ENDPOINT_IDS + intermediate_ids + [APERTURE_NODE_ID]
    rank_by_node = {node_id: index for index, node_id in enumerate(fan_node_ids)}
    for row in path_rows:
        row["intermediate_fan_node_rank"] = rank_by_node[
            int(row["intermediate_node_id"])
        ]

    fan_adjacency = np.zeros((len(fan_node_ids), len(fan_node_ids)), dtype=np.int8)
    edge_incidence_counts: Counter[tuple[int, int]] = Counter()
    for source, intermediate, aperture in path_node_triples:
        edge_incidence_counts[tuple(sorted((source, intermediate)))] += 1
        edge_incidence_counts[tuple(sorted((intermediate, aperture)))] += 1
        source_rank = rank_by_node[source]
        intermediate_rank = rank_by_node[intermediate]
        aperture_rank = rank_by_node[aperture]
        fan_adjacency[source_rank, intermediate_rank] = 1
        fan_adjacency[intermediate_rank, source_rank] = 1
        fan_adjacency[intermediate_rank, aperture_rank] = 1
        fan_adjacency[aperture_rank, intermediate_rank] = 1

    fan_distances = shortest_paths(fan_adjacency)
    fan_delta = gromov_delta_witness(fan_distances)
    fan_degrees = np.asarray(fan_adjacency.sum(axis=1), dtype=np.int64)

    fan_node_rows: list[dict[str, int]] = []
    for rank, node_id in enumerate(fan_node_ids):
        node = node_by_id[node_id]
        symbols = node_symbols(node)
        role = (
            ROLE_BOUNDARY
            if node_id in BOUNDARY_ENDPOINT_IDS
            else ROLE_APERTURE
            if node_id == APERTURE_NODE_ID
            else ROLE_INTERMEDIATE
        )
        fan_node_rows.append(
            {
                "fan_node_rank": rank,
                "rewrite_node_id": node_id,
                "fan_role_code": role,
                "boundary_endpoint_flag": int(role == ROLE_BOUNDARY),
                "intermediate_flag": int(role == ROLE_INTERMEDIATE),
                "aperture_flag": int(role == ROLE_APERTURE),
                "canonical_symbol_bitset": bitset(symbols),
                "x2_count": symbol_count(node, 2),
                "x4_count": symbol_count(node, 4),
                "x2_x4_symbol_count": symbol_count(node, 2)
                + symbol_count(node, 4),
                "sector_coverage_count": int(node["sector_coverage_count"]),
                "full_sector_flag": int(int(node["sector_coverage_count"]) == 6),
                "signature_union_count": int(node["signature_union_count"]),
                "high_signature_flag": int(
                    int(node["signature_union_count"]) >= OBSERVED_SIGNATURE_THRESHOLD
                ),
                "fan_degree": int(fan_degrees[rank]),
                "fan_distance_to_aperture": int(
                    fan_distances[rank, rank_by_node[APERTURE_NODE_ID]]
                ),
                "ambient_distance_to_aperture": int(
                    rewrite_distances[node_id, APERTURE_NODE_ID]
                ),
            }
        )

    fan_edge_rows: list[dict[str, int]] = []
    for edge_id, (source, target) in enumerate(sorted(edge_incidence_counts)):
        source_rank = rank_by_node[source]
        target_rank = rank_by_node[target]
        if target == APERTURE_NODE_ID or source == APERTURE_NODE_ID:
            edge_role = EDGE_INTERMEDIATE_TO_APERTURE
        else:
            edge_role = EDGE_BOUNDARY_TO_INTERMEDIATE
        source_node = node_by_id[source]
        target_node = node_by_id[target]
        fan_edge_rows.append(
            {
                "fan_edge_id": edge_id,
                "source_fan_node_rank": source_rank,
                "target_fan_node_rank": target_rank,
                "source_rewrite_node_id": source,
                "target_rewrite_node_id": target,
                "edge_role_code": edge_role,
                "path_incidence_count": int(edge_incidence_counts[(source, target)]),
                "ambient_rewrite_distance": int(rewrite_distances[source, target]),
                "source_sector_coverage_count": int(
                    source_node["sector_coverage_count"]
                ),
                "target_sector_coverage_count": int(
                    target_node["sector_coverage_count"]
                ),
                "source_signature_union_count": int(
                    source_node["signature_union_count"]
                ),
                "target_signature_union_count": int(
                    target_node["signature_union_count"]
                ),
            }
        )

    summary_rows: list[dict[str, int]] = []
    for endpoint_id in BOUNDARY_ENDPOINT_IDS:
        endpoint_paths = [
            row for row in path_rows if int(row["source_boundary_node_id"]) == endpoint_id
        ]
        strict_path_ids = [
            int(row["geodesic_path_id"])
            for row in endpoint_paths
            if int(row["full_sector_and_high_signature_flag"]) == 1
        ]
        summary_rows.append(
            {
                "boundary_node_id": endpoint_id,
                "geodesic_path_count": len(endpoint_paths),
                "full_sector_path_count": sum(
                    int(row["intermediate_full_sector_flag"]) for row in endpoint_paths
                ),
                "high_signature_path_count": sum(
                    int(row["intermediate_high_signature_flag"])
                    for row in endpoint_paths
                ),
                "full_sector_and_high_signature_path_count": len(strict_path_ids),
                "x2_first_path_count": sum(
                    1
                    for row in endpoint_paths
                    if int(row["first_restored_symbol_id"]) == 2
                ),
                "x4_first_path_count": sum(
                    1
                    for row in endpoint_paths
                    if int(row["first_restored_symbol_id"]) == 4
                ),
                "min_intermediate_signature_union_count": min(
                    int(row["intermediate_signature_union_count"])
                    for row in endpoint_paths
                ),
                "max_intermediate_signature_union_count": max(
                    int(row["intermediate_signature_union_count"])
                    for row in endpoint_paths
                ),
                "strict_best_path_id": min(strict_path_ids) if strict_path_ids else -1,
            }
        )

    full_sector_path_count = sum(
        int(row["intermediate_full_sector_flag"]) for row in path_rows
    )
    high_signature_path_count = sum(
        int(row["intermediate_high_signature_flag"]) for row in path_rows
    )
    strict_path_count = sum(
        int(row["full_sector_and_high_signature_flag"]) for row in path_rows
    )
    x2_first_path_count = sum(
        1 for row in path_rows if int(row["first_restored_symbol_id"]) == 2
    )
    x4_first_path_count = sum(
        1 for row in path_rows if int(row["first_restored_symbol_id"]) == 4
    )
    intermediate_signatures = [
        int(row["intermediate_signature_union_count"]) for row in path_rows
    ]
    endpoint_path_counts = [int(row["geodesic_path_count"]) for row in summary_rows]
    boundary_distance_values = {
        int(rewrite_distances[endpoint, APERTURE_NODE_ID])
        for endpoint in BOUNDARY_ENDPOINT_IDS
    }

    observable_values = {
        "boundary_endpoint_count": len(BOUNDARY_ENDPOINT_IDS),
        "aperture_node_id": APERTURE_NODE_ID,
        "geodesic_path_count": len(path_rows),
        "fan_node_count": len(fan_node_ids),
        "fan_edge_count": len(fan_edge_rows),
        "fan_graph_diameter": int(np.max(fan_distances)),
        "fan_graph_radius": int(np.min(np.max(fan_distances, axis=1))),
        "fan_gromov_delta_twice": int(fan_delta["delta_twice"]),
        "full_sector_intermediate_path_count": full_sector_path_count,
        "high_signature_intermediate_path_count": high_signature_path_count,
        "full_sector_and_high_signature_path_count": strict_path_count,
        "x2_first_path_count": x2_first_path_count,
        "x4_first_path_count": x4_first_path_count,
        "observed_signature_threshold": OBSERVED_SIGNATURE_THRESHOLD,
        "aperture_signature_union_count": aperture_signature,
        "max_intermediate_signature_union_count": max(intermediate_signatures),
        "min_intermediate_signature_union_count": min(intermediate_signatures),
        "boundary_to_aperture_ambient_distance": min(boundary_distance_values),
        "max_endpoint_geodesic_path_count": max(endpoint_path_counts),
        "min_endpoint_geodesic_path_count": min(endpoint_path_counts),
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

    fan_node_table = table_from_rows(FAN_NODE_COLUMNS, fan_node_rows)
    fan_edge_table = table_from_rows(FAN_EDGE_COLUMNS, fan_edge_rows)
    geodesic_path_table = table_from_rows(GEODESIC_PATH_COLUMNS, path_rows)
    restoration_summary_table = table_from_rows(
        RESTORATION_SUMMARY_COLUMNS,
        summary_rows,
    )
    fan_observable_table = table_from_rows(FAN_OBSERVABLE_COLUMNS, observable_rows)

    expected_paths = [
        [20, 14, 44],
        [20, 19, 44],
        [20, 45, 44],
        [20, 54, 44],
        [48, 42, 44],
        [48, 50, 44],
    ]
    strict_paths = [
        path_node_triples[int(row["geodesic_path_id"])]
        for row in path_rows
        if int(row["full_sector_and_high_signature_flag"]) == 1
    ]

    checks = {
        "language_graph_report_certified": language_report.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_LANGUAGE_GRAPH_CERTIFIED",
        "language_graph_certificate_certified": language_certificate.get("status")
        == "C985_D20_SIGNATURE_BOUNDARY_SPINE_LANGUAGE_GRAPH_CERTIFIED",
        "rewrite_complex_report_certified": rewrite_report.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "rewrite_complex_certificate_certified": rewrite_certificate.get("status")
        == "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED",
        "language_graph_schema_available": language_graph.get("schema")
        == "c985.d20_signature_boundary_spine_language_graph@1",
        "rewrite_complex_schema_available": rewrite_complex.get("schema")
        == "c985.d20_rewrite_complex_hyperbolicity@1",
        "language_graph_tables_available": (
            "language_node_table" in language_tables.files
            and "language_aperture_table" in language_tables.files
        ),
        "rewrite_complex_tables_available": (
            "adjacency" in rewrite_tables.files
            and "graph_distances" in rewrite_tables.files
        ),
        "language_node_table_shape_is_8_by_14": tuple(language_node_table.shape)
        == (8, 14),
        "language_edge_table_shape_is_7_by_10": tuple(language_edge_table.shape)
        == (7, 10),
        "language_aperture_table_shape_is_8_by_9": tuple(language_aperture_table.shape)
        == (8, 9),
        "rewrite_node_table_shape_is_56_by_17": tuple(rewrite_node_table.shape)
        == (56, 17),
        "rewrite_edge_table_shape_is_315_by_13": tuple(rewrite_edge_table.shape)
        == (315, 13),
        "language_boundary_endpoints_match_expected": language_report["witness"][
            "language_boundary_endpoint_node_ids"
        ]
        == BOUNDARY_ENDPOINT_IDS,
        "language_aperture_node_matches_expected": language_report["witness"][
            "aperture_node"
        ]["node_id"]
        == APERTURE_NODE_ID,
        "aperture_word_is_x2_x4_x5": str(aperture_node["canonical_word"])
        == APERTURE_WORD,
        "boundary_endpoints_are_ambient_distance_2": sorted(boundary_distance_values)
        == [2],
        "geodesic_paths_match_expected": path_node_triples == expected_paths,
        "geodesic_path_count_is_6": len(path_rows) == 6,
        "fan_node_count_is_9": len(fan_node_rows) == 9,
        "fan_edge_count_is_12": len(fan_edge_rows) == 12,
        "all_geodesic_paths_have_length_2": all(
            int(row["path_length"]) == 2 for row in path_rows
        ),
        "all_fan_edges_are_rewrite_complex_edges": all(
            int(row["ambient_rewrite_distance"]) == 1 for row in fan_edge_rows
        ),
        "all_paths_restore_x2_and_x4_once": all(
            sorted(
                [
                    int(row["first_restored_symbol_id"]),
                    int(row["second_restored_symbol_id"]),
                ]
            )
            == MISSING_GATE_SYMBOLS
            for row in path_rows
        ),
        "x2_first_and_x4_first_paths_are_balanced": (
            x2_first_path_count,
            x4_first_path_count,
        )
        == (3, 3),
        "full_sector_intermediate_path_count_is_2": full_sector_path_count == 2,
        "high_signature_intermediate_path_count_is_1": high_signature_path_count == 1,
        "strict_full_sector_high_signature_path_count_is_1": strict_path_count == 1,
        "strict_path_is_48_42_44": strict_paths == [[48, 42, 44]],
        "intermediate_signature_range_is_134_183": (
            min(intermediate_signatures),
            max(intermediate_signatures),
        )
        == (134, 183),
        "fan_graph_connected": bool(np.all(fan_distances < 10**9)),
        "fan_graph_diameter_is_4": observable_values["fan_graph_diameter"] == 4,
        "fan_graph_radius_is_2": observable_values["fan_graph_radius"] == 2,
        "fan_gromov_delta_is_1": fan_delta["delta_twice"] == 2,
        "fan_delta_witness_nodes_match_expected": [
            fan_node_ids[index] for index in fan_delta["witness_language_ranks"]
        ]
        == [20, 48, 14, 19],
        "fan_degree_histogram_matches_expected": histogram(
            [int(value) for value in fan_degrees.tolist()]
        )
        == [
            {"value": 2, "count": 7},
            {"value": 4, "count": 1},
            {"value": 6, "count": 1},
        ],
        "fan_node_table_shape_is_9_by_17": tuple(fan_node_table.shape)
        == (9, len(FAN_NODE_COLUMNS)),
        "fan_edge_table_shape_is_12_by_12": tuple(fan_edge_table.shape)
        == (12, len(FAN_EDGE_COLUMNS)),
        "geodesic_path_table_shape_is_6_by_17": tuple(geodesic_path_table.shape)
        == (6, len(GEODESIC_PATH_COLUMNS)),
        "restoration_summary_table_shape_is_2_by_10": tuple(
            restoration_summary_table.shape
        )
        == (2, len(RESTORATION_SUMMARY_COLUMNS)),
        "fan_observable_table_shape_matches_codebook": tuple(
            fan_observable_table.shape
        )
        == (len(OBSERVABLE_CODES), len(FAN_OBSERVABLE_COLUMNS)),
    }

    witness = {
        "boundary_endpoint_node_ids": BOUNDARY_ENDPOINT_IDS,
        "aperture_node": {
            "node_id": APERTURE_NODE_ID,
            "canonical_word": str(aperture_node["canonical_word"]),
            "canonical_atom_ids": aperture_node["canonical_atom_ids"],
            "sector_coverage_count": int(aperture_node["sector_coverage_count"]),
            "signature_union_count": aperture_signature,
        },
        "geodesic_path_node_triples": path_node_triples,
        "geodesic_path_count": len(path_rows),
        "fan_node_ids": fan_node_ids,
        "fan_edge_node_pairs": [
            [int(row["source_rewrite_node_id"]), int(row["target_rewrite_node_id"])]
            for row in fan_edge_rows
        ],
        "fan_graph_diameter": observable_values["fan_graph_diameter"],
        "fan_graph_radius": observable_values["fan_graph_radius"],
        "fan_gromov_delta": fan_delta["delta"],
        "fan_gromov_delta_twice": fan_delta["delta_twice"],
        "fan_delta_witness_node_ids": [
            fan_node_ids[index] for index in fan_delta["witness_language_ranks"]
        ],
        "fan_distance_histogram": histogram(
            [
                int(fan_distances[source, target])
                for source in range(len(fan_node_ids))
                for target in range(source + 1, len(fan_node_ids))
            ]
        ),
        "fan_degree_histogram": histogram(
            [int(value) for value in fan_degrees.tolist()]
        ),
        "observed_signature_threshold": OBSERVED_SIGNATURE_THRESHOLD,
        "full_sector_intermediate_path_count": full_sector_path_count,
        "high_signature_intermediate_path_count": high_signature_path_count,
        "full_sector_and_high_signature_path_count": strict_path_count,
        "strict_full_sector_high_signature_paths": strict_paths,
        "x2_first_path_count": x2_first_path_count,
        "x4_first_path_count": x4_first_path_count,
        "intermediate_signature_range": {
            "min": min(intermediate_signatures),
            "max": max(intermediate_signatures),
        },
        "endpoint_restoration_summary": summary_rows,
        "fan_node_table_sha256": sha_array(fan_node_table),
        "fan_edge_table_sha256": sha_array(fan_edge_table),
        "geodesic_path_table_sha256": sha_array(geodesic_path_table),
        "restoration_summary_table_sha256": sha_array(restoration_summary_table),
        "fan_adjacency_sha256": sha_array(fan_adjacency),
        "fan_distances_sha256": sha_array(fan_distances),
        "fan_observable_table_sha256": sha_array(fan_observable_table),
    }

    fan_json = {
        "schema": "c985.d20_signature_boundary_spine_aperture_geodesic_fan@1",
        "object": "d20",
        "geodesic_fan_rule": {
            "source": "certified language graph boundary endpoints and the ambient 56-node rewrite complex",
            "aperture": "rewrite node 44, the absent x2/x4 full-sector max-signature node",
            "paths": "all ambient shortest rewrite paths from language-boundary endpoints to the aperture",
            "preservation_test": "an intermediate path node must be full-sector and have signature at least the observed gate-language maximum 175",
        },
        "boundary_endpoint_node_ids": BOUNDARY_ENDPOINT_IDS,
        "aperture_node_id": APERTURE_NODE_ID,
        "observed_signature_threshold": OBSERVED_SIGNATURE_THRESHOLD,
        "fan_nodes": [
            {
                **row,
                "canonical_word": str(node_by_id[row["rewrite_node_id"]]["canonical_word"]),
            }
            for row in fan_node_rows
        ],
        "fan_edges": [
            {
                **row,
                "source_word": str(node_by_id[row["source_rewrite_node_id"]]["canonical_word"]),
                "target_word": str(node_by_id[row["target_rewrite_node_id"]]["canonical_word"]),
            }
            for row in fan_edge_rows
        ],
        "geodesic_paths": [
            {
                **row,
                "source_word": str(node_by_id[row["source_boundary_node_id"]]["canonical_word"]),
                "intermediate_word": str(node_by_id[row["intermediate_node_id"]]["canonical_word"]),
                "aperture_word": str(node_by_id[row["aperture_node_id"]]["canonical_word"]),
            }
            for row in path_rows
        ],
        "endpoint_restoration_summary": summary_rows,
        "summary": {
            "geodesic_path_count": len(path_rows),
            "fan_node_count": len(fan_node_rows),
            "fan_edge_count": len(fan_edge_rows),
            "fan_graph_diameter": observable_values["fan_graph_diameter"],
            "fan_graph_radius": observable_values["fan_graph_radius"],
            "fan_gromov_delta": fan_delta["delta"],
            "strict_full_sector_high_signature_paths": strict_paths,
            "full_sector_and_high_signature_path_count": strict_path_count,
            "x2_first_path_count": x2_first_path_count,
            "x4_first_path_count": x4_first_path_count,
            "intermediate_signature_range": witness["intermediate_signature_range"],
        },
    }

    certificate = {
        "schema": "c985.d20_signature_boundary_spine_aperture_geodesic_fan_certificate@1",
        "status": STATUS
        if all(checks.values())
        else "C985_D20_SIGNATURE_BOUNDARY_SPINE_APERTURE_GEODESIC_FAN_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the two language-boundary endpoints have exactly six shortest ambient rewrite paths to aperture node 44",
            "each shortest path restores x2 and x4 in two one-symbol rewrite steps",
            "the geodesic fan has 9 nodes, 12 edges, diameter 4, and exact Gromov delta 1",
            "only the path 48 -> 42 -> 44 is both full-sector at the intermediate node and above the observed signature threshold 175",
            "the path 20 -> 19 -> 44 is full-sector but falls below the strict high-signature threshold at 173",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_geodesic_fan@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The finite language-boundary aperture has a certified ambient "
            "rewrite geodesic fan: six shortest two-step paths restore x2/x4 "
            "from boundary endpoints into node 44, and exactly one path "
            "preserves both full-sector coverage and the observed high-signature "
            "threshold."
        ),
        "stage_protocol": {
            "draft": "treat node 44 as the missing x2/x4 aperture adjacent to the language boundary",
            "witness": "enumerate every shortest ambient rewrite path from boundary endpoints 20 and 48 to node 44",
            "coherence": "check restoration order, full-sector flags, signature thresholds, and fan hyperbolicity",
            "closure": "certify the finite aperture fan without claiming arbitrary ambient geodesic uniqueness",
            "emit": "emit geodesic-fan JSON/CSV/NPZ, certificate, report, verifier command, and next target",
        },
        "inputs": {
            "language_graph_report": input_entry(
                LANGUAGE_GRAPH_REPORT,
                {
                    "status": language_report.get("status"),
                    "certificate_sha256": language_report.get("certificate_sha256"),
                },
            ),
            "language_graph": input_entry(LANGUAGE_GRAPH_JSON),
            "language_graph_nodes": input_entry(LANGUAGE_GRAPH_NODE_CSV),
            "language_graph_edges": input_entry(LANGUAGE_GRAPH_EDGE_CSV),
            "language_aperture_distances": input_entry(LANGUAGE_APERTURE_CSV),
            "language_graph_tables": input_entry(LANGUAGE_GRAPH_TABLES),
            "language_graph_certificate": input_entry(LANGUAGE_GRAPH_CERTIFICATE),
            "rewrite_complex_report": input_entry(
                REWRITE_COMPLEX_REPORT,
                {
                    "status": rewrite_report.get("status"),
                    "certificate_sha256": rewrite_report.get("certificate_sha256"),
                },
            ),
            "rewrite_complex": input_entry(REWRITE_COMPLEX_JSON),
            "rewrite_complex_nodes": input_entry(REWRITE_COMPLEX_NODE_CSV),
            "rewrite_complex_edges": input_entry(REWRITE_COMPLEX_EDGE_CSV),
            "rewrite_complex_tables": input_entry(REWRITE_COMPLEX_TABLES),
            "rewrite_complex_certificate": input_entry(REWRITE_COMPLEX_CERTIFICATE),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT)
            if VALIDATOR_SCRIPT.exists()
            else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "signature_boundary_spine_aperture_geodesic_fan": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan.json"
            ),
            "aperture_geodesic_fan_nodes_csv": relpath(
                OUT_DIR / "aperture_geodesic_fan_nodes.csv"
            ),
            "aperture_geodesic_fan_edges_csv": relpath(
                OUT_DIR / "aperture_geodesic_fan_edges.csv"
            ),
            "aperture_geodesic_paths_csv": relpath(
                OUT_DIR / "aperture_geodesic_paths.csv"
            ),
            "aperture_restoration_summary_csv": relpath(
                OUT_DIR / "aperture_restoration_summary.csv"
            ),
            "aperture_geodesic_fan_observables_csv": relpath(
                OUT_DIR / "aperture_geodesic_fan_observables.csv"
            ),
            "signature_boundary_spine_aperture_geodesic_fan_tables": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan_tables.npz"
            ),
            "signature_boundary_spine_aperture_geodesic_fan_certificate": relpath(
                OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan_certificate.json"
            ),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "all ambient shortest rewrite paths from language-boundary endpoints 20 and 48 to aperture node 44",
                "the x2/x4 restoration order for every shortest path",
                "full-sector and high-signature preservation flags for the fan",
                "exact fan distances, diameter, radius, and Gromov delta",
                "the unique strict preserving path 48 -> 42 -> 44 at threshold 175",
            ],
            "does_not_certify_because_not_required": [
                "geodesic fans from non-boundary language nodes",
                "arbitrary-length rewrite geodesic uniqueness",
                "new categorical associator, pentagon, braiding, center, or tube-algebra data",
                "that threshold 175 is the only possible notion of high signature mass",
            ],
        },
        "next_highest_yield_item": (
            "Lift the unique strict aperture path 48 -> 42 -> 44 back through "
            "the gate language and boundary-spine order, then certify the "
            "minimal corridor edit that would introduce x2 before the aperture "
            "without losing the existing typed contacts."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_signature_boundary_spine_aperture_geodesic_fan_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified language-graph and rewrite-complex artifacts",
            "enumerate every length-2 rewrite geodesic from boundary endpoints to aperture node 44",
            "check x2/x4 restoration order and preservation thresholds",
            "construct the finite geodesic fan metric and exact Gromov delta",
            "check source hashes, artifact reproducibility, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "signature_boundary_spine_aperture_geodesic_fan": fan_json,
        "aperture_geodesic_fan_nodes_csv": csv_text(
            FAN_NODE_COLUMNS,
            fan_node_rows,
        ),
        "aperture_geodesic_fan_edges_csv": csv_text(
            FAN_EDGE_COLUMNS,
            fan_edge_rows,
        ),
        "aperture_geodesic_paths_csv": csv_text(
            GEODESIC_PATH_COLUMNS,
            path_rows,
        ),
        "aperture_restoration_summary_csv": csv_text(
            RESTORATION_SUMMARY_COLUMNS,
            summary_rows,
        ),
        "aperture_geodesic_fan_observables_csv": csv_text(
            FAN_OBSERVABLE_COLUMNS,
            observable_rows,
        ),
        "fan_node_table": fan_node_table,
        "fan_edge_table": fan_edge_table,
        "geodesic_path_table": geodesic_path_table,
        "restoration_summary_table": restoration_summary_table,
        "fan_adjacency": fan_adjacency,
        "fan_distances": fan_distances,
        "fan_observable_table": fan_observable_table,
        "signature_boundary_spine_aperture_geodesic_fan_certificate": certificate,
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
        OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan.json",
        payloads["signature_boundary_spine_aperture_geodesic_fan"],
    )
    (OUT_DIR / "aperture_geodesic_fan_nodes.csv").write_text(
        payloads["aperture_geodesic_fan_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_geodesic_fan_edges.csv").write_text(
        payloads["aperture_geodesic_fan_edges_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_geodesic_paths.csv").write_text(
        payloads["aperture_geodesic_paths_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_restoration_summary.csv").write_text(
        payloads["aperture_restoration_summary_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "aperture_geodesic_fan_observables.csv").write_text(
        payloads["aperture_geodesic_fan_observables_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan_tables.npz",
        fan_node_table=payloads["fan_node_table"],
        fan_edge_table=payloads["fan_edge_table"],
        geodesic_path_table=payloads["geodesic_path_table"],
        restoration_summary_table=payloads["restoration_summary_table"],
        fan_adjacency=payloads["fan_adjacency"],
        fan_distances=payloads["fan_distances"],
        fan_observable_table=payloads["fan_observable_table"],
    )
    write_json(
        OUT_DIR / "signature_boundary_spine_aperture_geodesic_fan_certificate.json",
        payloads["signature_boundary_spine_aperture_geodesic_fan_certificate"],
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
                "geodesic_path_count": witness["geodesic_path_count"],
                "fan_graph_diameter": witness["fan_graph_diameter"],
                "fan_gromov_delta": witness["fan_gromov_delta"],
                "strict_full_sector_high_signature_paths": witness[
                    "strict_full_sector_high_signature_paths"
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
