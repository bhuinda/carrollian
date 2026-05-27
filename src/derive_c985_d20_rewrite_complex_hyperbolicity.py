from __future__ import annotations

import itertools
import json
import math
from collections import deque
from typing import Any

import numpy as np

try:
    from .derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram, mask_labels
    from .derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from .paths import D20_INVARIANTS, ROOT, relpath
except ImportError:  # Supports direct script execution.
    from derive_c985_d20_symbolic_rewrite_rules import csv_text, histogram, mask_labels
    from derive_c985_typed_simple_object_registry import (
        INDEX_PATH,
        OBJECT_LABELS,
        input_entry,
        load_json,
        self_hash,
        sha_array,
        write_json,
    )
    from paths import D20_INVARIANTS, ROOT, relpath


THEOREM_ID = "c985_d20_rewrite_complex_hyperbolicity"
STATUS = "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_CERTIFIED"
OUT_DIR = D20_INVARIANTS / "proof_obligations" / THEOREM_ID

ASSOCIATIVITY_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_symbolic_associativity"
POINCARE_DIR = D20_INVARIANTS / "proof_obligations" / "c985_d20_poincare_embedding"

ASSOCIATIVITY_REPORT = ASSOCIATIVITY_DIR / "report.json"
SYMBOLIC_ASSOCIATIVITY_JSON = ASSOCIATIVITY_DIR / "symbolic_associativity.json"
SYMBOLIC_ASSOCIATIVITY_TABLES = ASSOCIATIVITY_DIR / "symbolic_associativity_tables.npz"
SYMBOLIC_ASSOCIATIVITY_CERTIFICATE = ASSOCIATIVITY_DIR / "symbolic_associativity_certificate.json"
POINCARE_REPORT = POINCARE_DIR / "report.json"
POINCARE_JSON = POINCARE_DIR / "poincare_embedding.json"
POINCARE_NPZ = POINCARE_DIR / "poincare_embedding.npz"

DERIVE_SCRIPT = ROOT / "src" / "derive_c985_d20_rewrite_complex_hyperbolicity.py"
VALIDATOR_SCRIPT = ROOT / "src" / "certify_c985_d20_rewrite_complex_hyperbolicity.py"

NODE_COLUMNS = [
    "node_id",
    "symbol_0_count",
    "symbol_1_count",
    "symbol_2_count",
    "symbol_3_count",
    "symbol_4_count",
    "symbol_5_count",
    "first_atom_id",
    "second_atom_id",
    "third_atom_id",
    "sector_union_mask",
    "sector_coverage_count",
    "signature_union_count",
    "tensor_path_support_sum",
    "tensor_path_coefficient_mass_sum",
    "normal_word_triple_multiplicity",
    "graph_degree",
]

EDGE_COLUMNS = [
    "edge_id",
    "source_node_id",
    "target_node_id",
    "source_removed_symbol_id",
    "target_added_symbol_id",
    "source_degree",
    "target_degree",
    "source_sector_coverage_count",
    "target_sector_coverage_count",
    "edge_sector_union_count",
    "source_signature_union_count",
    "target_signature_union_count",
    "signature_union_delta_abs",
]


def round10(value: float) -> float:
    return float(round(float(value), 10))


def poincare_distance(left: np.ndarray, right: np.ndarray) -> float:
    numerator = 2.0 * float(np.sum((left - right) ** 2))
    denominator = (1.0 - float(np.sum(left * left))) * (1.0 - float(np.sum(right * right)))
    return float(math.acosh(max(1.0, 1.0 + numerator / denominator)))


def coordinate_lookup(poincare: dict[str, Any]) -> dict[int, np.ndarray]:
    return {
        int(row["atom_id"]): np.asarray([float(row["x"]), float(row["y"])], dtype=np.float64)
        for row in poincare["coordinates"]
    }


def canonical_nodes(
    symbolic_associativity: dict[str, Any],
    poincare: dict[str, Any],
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    atom_coordinates = coordinate_lookup(poincare)
    by_id: dict[int, dict[str, Any]] = {}
    for row in symbolic_associativity["symbolic_triples"]:
        canonical_id = int(row["canonical_triple_id"])
        by_id.setdefault(canonical_id, row)

    node_rows: list[dict[str, Any]] = []
    node_table_rows: list[list[int]] = []
    coordinate_rows: list[list[float]] = []
    for node_id in sorted(by_id):
        row = by_id[node_id]
        symbol_ids = [
            int(row["canonical_first_symbol_id"]),
            int(row["canonical_second_symbol_id"]),
            int(row["canonical_third_symbol_id"]),
        ]
        counts = [0] * 6
        for symbol_id in symbol_ids:
            counts[symbol_id] += 1
        atom_ids = [int(atom_id) for atom_id in row["canonical_atom_ids"]]
        barycenter = sum((atom_coordinates[atom_id] for atom_id in atom_ids), np.zeros(2)) / 3.0
        radius = float(np.linalg.norm(barycenter))
        node = {
            "node_id": node_id,
            "canonical_word": row["canonical_word"],
            "canonical_symbol_ids": symbol_ids,
            "symbol_counts": counts,
            "symbol_0_count": counts[0],
            "symbol_1_count": counts[1],
            "symbol_2_count": counts[2],
            "symbol_3_count": counts[3],
            "symbol_4_count": counts[4],
            "symbol_5_count": counts[5],
            "canonical_atom_ids": atom_ids,
            "first_atom_id": atom_ids[0],
            "second_atom_id": atom_ids[1],
            "third_atom_id": atom_ids[2],
            "sector_union_mask": int(row["sector_union_mask"]),
            "covered_sectors": mask_labels(int(row["sector_union_mask"])),
            "sector_coverage_count": int(row["sector_coverage_count"]),
            "signature_union_count": int(row["signature_union_count"]),
            "signature_union_sha256": row["signature_union_sha256"],
            "tensor_path_support_sum": int(row["tensor_path_support_sum"]),
            "tensor_path_coefficient_mass_sum": int(row["tensor_path_coefficient_mass_sum"]),
            "normal_word_triple_multiplicity": int(row["word_triple_multiplicity"]),
            "graph_degree": 0,
            "poincare_barycenter": {
                "x": round10(barycenter[0]),
                "y": round10(barycenter[1]),
                "radius": round10(radius),
            },
        }
        node_rows.append(node)
        node_table_rows.append(
            [
                int(node["node_id"]),
                *counts,
                *atom_ids,
                int(node["sector_union_mask"]),
                int(node["sector_coverage_count"]),
                int(node["signature_union_count"]),
                int(node["tensor_path_support_sum"]),
                int(node["tensor_path_coefficient_mass_sum"]),
                int(node["normal_word_triple_multiplicity"]),
                0,
            ]
        )
        coordinate_rows.append(
            [
                float(node_id),
                round10(barycenter[0]),
                round10(barycenter[1]),
                round10(radius),
                float(node["sector_coverage_count"]),
                float(node["signature_union_count"]),
                float(node["tensor_path_coefficient_mass_sum"]),
            ]
        )

    return (
        node_rows,
        np.asarray(node_table_rows, dtype=np.int64),
        np.asarray(coordinate_rows, dtype=np.float64),
    )


def build_edges(
    node_rows: list[dict[str, Any]],
    node_table: np.ndarray,
    node_coordinates: np.ndarray,
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    edge_rows: list[dict[str, Any]] = []
    edge_table_rows: list[list[int]] = []
    node_count = len(node_rows)
    adjacency = np.zeros((node_count, node_count), dtype=np.int8)

    for source, target in itertools.combinations(range(node_count), 2):
        source_counts = np.asarray(node_rows[source]["symbol_counts"], dtype=np.int64)
        target_counts = np.asarray(node_rows[target]["symbol_counts"], dtype=np.int64)
        diff = target_counts - source_counts
        if int(np.sum(np.abs(diff))) != 2:
            continue
        removed = int(np.where(diff == -1)[0][0])
        added = int(np.where(diff == 1)[0][0])
        edge_sector_mask = int(node_rows[source]["sector_union_mask"]) | int(
            node_rows[target]["sector_union_mask"]
        )
        source_point = node_coordinates[source, 1:3]
        target_point = node_coordinates[target, 1:3]
        edge = {
            "edge_id": len(edge_rows),
            "source_node_id": source,
            "target_node_id": target,
            "source_word": node_rows[source]["canonical_word"],
            "target_word": node_rows[target]["canonical_word"],
            "source_removed_symbol_id": removed,
            "target_added_symbol_id": added,
            "source_degree": 0,
            "target_degree": 0,
            "source_sector_coverage_count": int(node_rows[source]["sector_coverage_count"]),
            "target_sector_coverage_count": int(node_rows[target]["sector_coverage_count"]),
            "edge_sector_union_count": int(edge_sector_mask.bit_count()),
            "source_signature_union_count": int(node_rows[source]["signature_union_count"]),
            "target_signature_union_count": int(node_rows[target]["signature_union_count"]),
            "signature_union_delta_abs": abs(
                int(node_rows[source]["signature_union_count"])
                - int(node_rows[target]["signature_union_count"])
            ),
            "poincare_barycenter_distance": round10(poincare_distance(source_point, target_point)),
        }
        edge_rows.append(edge)
        adjacency[source, target] = 1
        adjacency[target, source] = 1

    degrees = np.asarray(adjacency.sum(axis=1), dtype=np.int64)
    node_table[:, -1] = degrees
    for row in node_rows:
        row["graph_degree"] = int(degrees[int(row["node_id"])])
    for edge in edge_rows:
        edge["source_degree"] = int(degrees[int(edge["source_node_id"])])
        edge["target_degree"] = int(degrees[int(edge["target_node_id"])])
        edge_table_rows.append([int(edge[column]) for column in EDGE_COLUMNS])

    return edge_rows, np.asarray(edge_table_rows, dtype=np.int64), adjacency


def shortest_paths(adjacency: np.ndarray) -> np.ndarray:
    node_count = int(adjacency.shape[0])
    distances = np.full((node_count, node_count), 10**9, dtype=np.int64)
    neighbors = [np.flatnonzero(adjacency[node]).astype(np.int64).tolist() for node in range(node_count)]
    for source in range(node_count):
        distances[source, source] = 0
        queue: deque[int] = deque([source])
        while queue:
            node = queue.popleft()
            for neighbor in neighbors[node]:
                if distances[source, neighbor] == 10**9:
                    distances[source, neighbor] = distances[source, node] + 1
                    queue.append(neighbor)
    return distances


def gromov_delta_witness(distances: np.ndarray) -> dict[str, Any]:
    best_delta_twice = -1
    best_witness: tuple[int, int, int, int] | None = None
    best_sums: list[int] = []
    for a, b, c, d in itertools.combinations(range(int(distances.shape[0])), 4):
        sums = sorted(
            [
                int(distances[a, b] + distances[c, d]),
                int(distances[a, c] + distances[b, d]),
                int(distances[a, d] + distances[b, c]),
            ]
        )
        delta_twice = sums[2] - sums[1]
        if delta_twice > best_delta_twice:
            best_delta_twice = delta_twice
            best_witness = (a, b, c, d)
            best_sums = sums
    if best_witness is None:
        raise AssertionError("empty graph has no hyperbolicity witness")
    return {
        "delta": round10(best_delta_twice / 2.0),
        "delta_twice": int(best_delta_twice),
        "witness_nodes": [int(x) for x in best_witness],
        "four_point_sums": [int(x) for x in best_sums],
    }


def pair_records(
    graph_distances: np.ndarray,
    poincare_distances: np.ndarray,
    node_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    pairs: list[dict[str, Any]] = []
    for source, target in itertools.combinations(range(len(node_rows)), 2):
        pairs.append(
            {
                "source_node_id": source,
                "target_node_id": target,
                "source_word": node_rows[source]["canonical_word"],
                "target_word": node_rows[target]["canonical_word"],
                "graph_distance": int(graph_distances[source, target]),
                "poincare_barycenter_distance": round10(poincare_distances[source, target]),
            }
        )
    by_poincare = sorted(
        pairs,
        key=lambda row: (
            float(row["poincare_barycenter_distance"]),
            int(row["graph_distance"]),
            -int(row["source_node_id"]),
            -int(row["target_node_id"]),
        ),
        reverse=True,
    )
    diameter_pair = by_poincare[0]
    return {
        "poincare_diameter_pair": diameter_pair,
        "top_20_poincare_distance_pairs": by_poincare[:20],
        "top_20_poincare_pairs_graph_distance_histogram": histogram(
            [int(row["graph_distance"]) for row in by_poincare[:20]]
        ),
    }


def build_payloads() -> dict[str, Any]:
    associativity_report = load_json(ASSOCIATIVITY_REPORT)
    symbolic_associativity = load_json(SYMBOLIC_ASSOCIATIVITY_JSON)
    associativity_certificate = load_json(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE)
    poincare_report = load_json(POINCARE_REPORT)
    poincare = load_json(POINCARE_JSON)
    associativity_tables = np.load(SYMBOLIC_ASSOCIATIVITY_TABLES, allow_pickle=False)
    associativity_table = np.asarray(
        associativity_tables["symbolic_associativity_table"], dtype=np.int64
    )
    poincare_npz = np.load(POINCARE_NPZ, allow_pickle=False)
    atom_coordinate_table = np.asarray(poincare_npz["coordinate_table"], dtype=np.float64)
    atom_poincare_distances = np.asarray(poincare_npz["poincare_distances"], dtype=np.float64)

    node_rows, node_table, node_coordinates = canonical_nodes(symbolic_associativity, poincare)
    edge_rows, edge_table, adjacency = build_edges(node_rows, node_table, node_coordinates)
    graph_distances = shortest_paths(adjacency)
    node_count = len(node_rows)
    poincare_distances = np.zeros((node_count, node_count), dtype=np.float64)
    for source, target in itertools.combinations(range(node_count), 2):
        distance = poincare_distance(node_coordinates[source, 1:3], node_coordinates[target, 1:3])
        poincare_distances[source, target] = distance
        poincare_distances[target, source] = distance

    graph_delta = gromov_delta_witness(graph_distances)
    degree_hist = histogram([int(row["graph_degree"]) for row in node_rows])
    graph_diameter = int(np.max(graph_distances))
    graph_radius = int(np.min(np.max(graph_distances, axis=1)))
    radius_values = node_coordinates[:, 3]
    central_node_id = int(np.argmin(radius_values))
    outermost_node_id = int(np.argmax(radius_values))
    pair_summary = pair_records(graph_distances, poincare_distances, node_rows)
    upper = np.triu_indices(node_count, k=1)
    distance_correlation = float(np.corrcoef(graph_distances[upper], poincare_distances[upper])[0, 1])
    full_sector_node_count = sum(
        1 for row in node_rows if int(row["sector_coverage_count"]) == len(OBJECT_LABELS)
    )
    max_signature_union = max(int(row["signature_union_count"]) for row in node_rows)
    min_signature_union = min(int(row["signature_union_count"]) for row in node_rows)
    max_signature_nodes = [
        {
            "node_id": int(row["node_id"]),
            "canonical_word": row["canonical_word"],
            "canonical_atom_ids": row["canonical_atom_ids"],
        }
        for row in node_rows
        if int(row["signature_union_count"]) == max_signature_union
    ]
    min_signature_nodes = [
        {
            "node_id": int(row["node_id"]),
            "canonical_word": row["canonical_word"],
            "canonical_atom_ids": row["canonical_atom_ids"],
        }
        for row in node_rows
        if int(row["signature_union_count"]) == min_signature_union
    ]
    max_edge_poincare_distance = max(float(row["poincare_barycenter_distance"]) for row in edge_rows)

    rewrite_complex = {
        "schema": "c985.d20_rewrite_complex_hyperbolicity@1",
        "object": "d20",
        "source_symbolic_associativity_certificate": associativity_report.get("certificate_sha256"),
        "source_poincare_embedding_certificate": poincare_report.get("certificate_sha256"),
        "complex_rule": {
            "nodes": "56 sorted length-three symbolic normal forms",
            "edges": "one-symbol replacement between canonical triples, equivalently L1 distance 2 between symbol-count vectors",
            "metric": "unweighted shortest-path metric on the rewrite complex",
            "poincare_comparison": "node coordinates are barycenters of the three certified d20 atom Poincare coordinates",
        },
        "nodes": node_rows,
        "edges": edge_rows,
        "geodesic_witnesses": {
            "graph_hyperbolicity": graph_delta,
            "poincare_diameter_pair": pair_summary["poincare_diameter_pair"],
            "top_20_poincare_distance_pairs": pair_summary["top_20_poincare_distance_pairs"],
        },
        "summary": {
            "node_count": node_count,
            "edge_count": len(edge_rows),
            "degree_histogram": degree_hist,
            "graph_diameter": graph_diameter,
            "graph_radius": graph_radius,
            "graph_gromov_delta": graph_delta["delta"],
            "graph_gromov_delta_twice": graph_delta["delta_twice"],
            "full_sector_node_count": full_sector_node_count,
            "sector_coverage_histogram": histogram(
                [int(row["sector_coverage_count"]) for row in node_rows]
            ),
            "signature_union_count_min": min_signature_union,
            "signature_union_count_max": max_signature_union,
            "max_signature_nodes": max_signature_nodes,
            "min_signature_nodes": min_signature_nodes,
            "poincare_barycenter_radius_min": round10(float(np.min(radius_values))),
            "poincare_barycenter_radius_max": round10(float(np.max(radius_values))),
            "poincare_central_node": {
                "node_id": central_node_id,
                "canonical_word": node_rows[central_node_id]["canonical_word"],
                "canonical_atom_ids": node_rows[central_node_id]["canonical_atom_ids"],
            },
            "poincare_outermost_node": {
                "node_id": outermost_node_id,
                "canonical_word": node_rows[outermost_node_id]["canonical_word"],
                "canonical_atom_ids": node_rows[outermost_node_id]["canonical_atom_ids"],
            },
            "poincare_barycenter_metric_diameter": round10(float(np.max(poincare_distances))),
            "poincare_diameter_pair_graph_distance": int(
                pair_summary["poincare_diameter_pair"]["graph_distance"]
            ),
            "top_20_poincare_pairs_graph_distance_histogram": pair_summary[
                "top_20_poincare_pairs_graph_distance_histogram"
            ],
            "graph_poincare_distance_correlation": round10(distance_correlation),
            "max_edge_poincare_barycenter_distance": round10(max_edge_poincare_distance),
        },
    }

    checks = {
        "symbolic_associativity_report_certified": associativity_report.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "symbolic_associativity_certificate_certified": associativity_certificate.get("status")
        == "C985_D20_SYMBOLIC_ASSOCIATIVITY_CERTIFIED",
        "poincare_embedding_report_certified": poincare_report.get("status")
        == "C985_D20_POINCARE_EMBEDDING_CERTIFIED",
        "symbolic_associativity_table_shape_is_216_by_27": tuple(associativity_table.shape) == (216, 27),
        "poincare_coordinate_table_shape_is_20_by_10": tuple(atom_coordinate_table.shape) == (20, 10),
        "poincare_distance_matrix_shape_is_20_by_20": tuple(atom_poincare_distances.shape) == (20, 20),
        "rewrite_complex_node_count_is_56": node_count == 56,
        "rewrite_complex_edge_count_is_315": len(edge_rows) == 315,
        "rewrite_complex_degree_histogram_is_6_five_30_ten_20_fifteen": degree_hist
        == [
            {"value": 5, "count": 6},
            {"value": 10, "count": 30},
            {"value": 15, "count": 20},
        ],
        "rewrite_complex_connected": bool(np.all(graph_distances < 10**9)),
        "rewrite_complex_graph_diameter_is_3": graph_diameter == 3,
        "rewrite_complex_graph_radius_is_3": graph_radius == 3,
        "rewrite_complex_gromov_delta_is_1": graph_delta["delta_twice"] == 2,
        "rewrite_complex_delta_witness_is_0_6_22_36": graph_delta["witness_nodes"] == [0, 6, 22, 36],
        "rewrite_complex_full_sector_node_count_is_14": full_sector_node_count == 14,
        "rewrite_complex_sector_coverage_histogram_is_6_three_10_four_26_five_14_six": histogram(
            [int(row["sector_coverage_count"]) for row in node_rows]
        )
        == [
            {"value": 3, "count": 6},
            {"value": 4, "count": 10},
            {"value": 5, "count": 26},
            {"value": 6, "count": 14},
        ],
        "rewrite_complex_signature_union_max_is_185": max_signature_union == 185,
        "rewrite_complex_signature_union_min_is_53": min_signature_union == 53,
        "rewrite_complex_max_signature_node_is_44": max_signature_nodes
        == [{"node_id": 44, "canonical_word": "x2 x4 x5", "canonical_atom_ids": [7, 12, 19]}],
        "rewrite_complex_min_signature_node_is_46": min_signature_nodes
        == [{"node_id": 46, "canonical_word": "x3 x3 x3", "canonical_atom_ids": [11, 11, 11]}],
        "all_poincare_barycenters_inside_open_disk": bool(np.all(radius_values < 1.0)),
        "poincare_central_node_is_14": central_node_id == 14,
        "poincare_outermost_node_is_0": outermost_node_id == 0,
        "poincare_barycenter_metric_diameter_is_0_7423247109": round10(float(np.max(poincare_distances)))
        == 0.7423247109,
        "poincare_diameter_pair_is_0_55": [
            pair_summary["poincare_diameter_pair"]["source_node_id"],
            pair_summary["poincare_diameter_pair"]["target_node_id"],
        ]
        == [0, 55],
        "poincare_diameter_pair_is_graph_diameter": int(
            pair_summary["poincare_diameter_pair"]["graph_distance"]
        )
        == graph_diameter,
        "top_20_poincare_pairs_are_graph_diameter": pair_summary[
            "top_20_poincare_pairs_graph_distance_histogram"
        ]
        == [{"value": 3, "count": 20}],
        "graph_poincare_distance_correlation_is_0_4851736825": round10(distance_correlation)
        == 0.4851736825,
        "max_edge_poincare_barycenter_distance_is_0_2509641633": round10(max_edge_poincare_distance)
        == 0.2509641633,
    }

    witness = {
        "node_count": node_count,
        "edge_count": len(edge_rows),
        "degree_histogram": degree_hist,
        "graph_diameter": graph_diameter,
        "graph_radius": graph_radius,
        "graph_gromov_delta": graph_delta["delta"],
        "graph_gromov_delta_twice": graph_delta["delta_twice"],
        "graph_delta_witness_nodes": graph_delta["witness_nodes"],
        "full_sector_node_count": full_sector_node_count,
        "sector_coverage_histogram": rewrite_complex["summary"]["sector_coverage_histogram"],
        "signature_union_count_min": min_signature_union,
        "signature_union_count_max": max_signature_union,
        "max_signature_nodes": max_signature_nodes,
        "min_signature_nodes": min_signature_nodes,
        "poincare_central_node_id": central_node_id,
        "poincare_outermost_node_id": outermost_node_id,
        "poincare_barycenter_radius_min": rewrite_complex["summary"][
            "poincare_barycenter_radius_min"
        ],
        "poincare_barycenter_radius_max": rewrite_complex["summary"][
            "poincare_barycenter_radius_max"
        ],
        "poincare_barycenter_metric_diameter": rewrite_complex["summary"][
            "poincare_barycenter_metric_diameter"
        ],
        "poincare_diameter_pair_node_ids": [
            pair_summary["poincare_diameter_pair"]["source_node_id"],
            pair_summary["poincare_diameter_pair"]["target_node_id"],
        ],
        "poincare_diameter_pair_graph_distance": int(
            pair_summary["poincare_diameter_pair"]["graph_distance"]
        ),
        "top_20_poincare_pairs_graph_distance_histogram": pair_summary[
            "top_20_poincare_pairs_graph_distance_histogram"
        ],
        "graph_poincare_distance_correlation": round10(distance_correlation),
        "max_edge_poincare_barycenter_distance": round10(max_edge_poincare_distance),
        "rewrite_complex_node_table_sha256": sha_array(node_table),
        "rewrite_complex_edge_table_sha256": sha_array(edge_table),
        "rewrite_complex_adjacency_sha256": sha_array(adjacency),
        "rewrite_complex_graph_distances_sha256": sha_array(graph_distances),
        "rewrite_complex_poincare_coordinates_sha256": sha_array(node_coordinates),
        "rewrite_complex_poincare_distances_sha256": sha_array(poincare_distances),
        "symbolic_associativity_table_sha256": sha_array(associativity_table),
        "source_poincare_coordinate_table_sha256": sha_array(atom_coordinate_table),
    }

    certificate = {
        "schema": "c985.d20_rewrite_complex_hyperbolicity_certificate@1",
        "status": STATUS if all(checks.values()) else "C985_D20_REWRITE_COMPLEX_HYPERBOLICITY_PROVISIONAL",
        "checks": checks,
        "witness": witness,
        "certified_reading": [
            "the 56 canonical length-three symbolic normal forms form a connected rewrite complex",
            "one-symbol replacement gives 315 edges and graph diameter 3",
            "the rewrite complex has exact four-point Gromov delta 1",
            "Poincare barycenters of the underlying d20 atom triples stay inside the open disk",
            "the Poincare-diameter node pair is also a graph-diameter geodesic pair",
        ],
    }

    report = {
        "schema": "c985.proof_obligation.d20_rewrite_complex_hyperbolicity@1",
        "status": certificate["status"],
        "all_checks_pass": all(checks.values()),
        "claim": (
            "The 56 canonical length-three symbolic d20 normal forms form a "
            "connected higher-order rewrite complex whose one-symbol replacement "
            "metric is hyperbolic and whose Poincare barycentric geodesics are "
            "consistent with the certified d20 disk chart."
        ),
        "stage_protocol": {
            "draft": "use certified symbolic associativity nodes and certified d20 Poincare coordinates",
            "witness": "materialize the 56-node one-symbol replacement complex, graph distances, and Poincare barycenters",
            "coherence": "check connectedness, exact Gromov delta, sector/signature summaries, and Poincare geodesic agreement",
            "closure": "certify a higher-order d20 rewrite-complex geometry without asserting new C985 categorical data",
            "emit": "emit rewrite-complex JSON/CSV/NPZ, certificate, report, and next hyperbolic target",
        },
        "inputs": {
            "symbolic_associativity_report": input_entry(
                ASSOCIATIVITY_REPORT,
                {
                    "status": associativity_report.get("status"),
                    "certificate_sha256": associativity_report.get("certificate_sha256"),
                },
            ),
            "symbolic_associativity": input_entry(SYMBOLIC_ASSOCIATIVITY_JSON),
            "symbolic_associativity_tables": input_entry(SYMBOLIC_ASSOCIATIVITY_TABLES),
            "symbolic_associativity_certificate": input_entry(SYMBOLIC_ASSOCIATIVITY_CERTIFICATE),
            "poincare_report": input_entry(
                POINCARE_REPORT,
                {
                    "status": poincare_report.get("status"),
                    "certificate_sha256": poincare_report.get("certificate_sha256"),
                },
            ),
            "poincare_embedding": input_entry(POINCARE_JSON),
            "poincare_embedding_npz": input_entry(POINCARE_NPZ),
            "derive_script": input_entry(DERIVE_SCRIPT),
            "validator": input_entry(VALIDATOR_SCRIPT) if VALIDATOR_SCRIPT.exists() else {"path": relpath(VALIDATOR_SCRIPT)},
        },
        "outputs": {
            "rewrite_complex": relpath(OUT_DIR / "rewrite_complex.json"),
            "rewrite_complex_nodes_csv": relpath(OUT_DIR / "rewrite_complex_nodes.csv"),
            "rewrite_complex_edges_csv": relpath(OUT_DIR / "rewrite_complex_edges.csv"),
            "rewrite_complex_tables": relpath(OUT_DIR / "rewrite_complex_tables.npz"),
            "rewrite_complex_certificate": relpath(OUT_DIR / "rewrite_complex_certificate.json"),
            "manifest": relpath(OUT_DIR / "manifest.json"),
            "report": relpath(OUT_DIR / "report.json"),
        },
        "witness": witness,
        "checks": checks,
        "closure_boundary": {
            "certifies": [
                "56-node higher-order rewrite complex from length-three symbolic normal forms",
                "315 one-symbol replacement edges and exact graph geodesic distances",
                "exact graph Gromov delta 1 with a certified four-point witness",
                "Poincare barycenter coordinates and geodesic comparison for every node pair",
                "agreement that the Poincare diameter pair is a graph-diameter pair",
            ],
            "does_not_certify_because_not_required": [
                "arbitrary-length symbolic rewrite confluence",
                "a new associator or pentagon proof for C985 beyond the existing certificate",
                "a packet bridge from d20 atoms to A985/tube coordinates",
                "pivotal, spherical, unitary, braiding, ribbon, or Drinfeld-center data",
            ],
        },
        "next_highest_yield_item": (
            "Lift the 56-node rewrite complex into a sheaf of Poincare geodesic "
            "intervals, then certify which graph geodesics preserve full-sector "
            "coverage and high relation-signature mass."
        ),
    }
    report["certificate_sha256"] = self_hash(report, "certificate_sha256")

    manifest = {
        "schema": "c985.proof_obligation.d20_rewrite_complex_hyperbolicity_manifest@1",
        "name": THEOREM_ID,
        "status": report["status"],
        "certification_tests": [
            "load certified symbolic associativity and Poincare embedding artifacts",
            "deduplicate the 216 symbolic triples into 56 canonical normal-form nodes",
            "construct one-symbol replacement edges and exact shortest-path distances",
            "compute exact graph Gromov hyperbolicity and Poincare barycenter distances",
            "check geodesic comparison, source hashes, and proof-obligation registry consistency",
        ],
        "inputs": report["inputs"],
        "outputs": report["outputs"],
        "report_sha256": report["certificate_sha256"],
    }
    manifest["manifest_sha256"] = self_hash(manifest, "manifest_sha256")

    return {
        "rewrite_complex": rewrite_complex,
        "rewrite_complex_nodes_csv": csv_text(NODE_COLUMNS, node_rows),
        "rewrite_complex_edges_csv": csv_text(EDGE_COLUMNS, edge_rows),
        "node_table": node_table,
        "edge_table": edge_table,
        "adjacency": adjacency,
        "graph_distances": graph_distances,
        "node_poincare_coordinates": node_coordinates,
        "node_poincare_distances": poincare_distances,
        "rewrite_complex_certificate": certificate,
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
    write_json(OUT_DIR / "rewrite_complex.json", payloads["rewrite_complex"])
    (OUT_DIR / "rewrite_complex_nodes.csv").write_text(
        payloads["rewrite_complex_nodes_csv"],
        encoding="utf-8",
    )
    (OUT_DIR / "rewrite_complex_edges.csv").write_text(
        payloads["rewrite_complex_edges_csv"],
        encoding="utf-8",
    )
    np.savez_compressed(
        OUT_DIR / "rewrite_complex_tables.npz",
        node_table=payloads["node_table"],
        edge_table=payloads["edge_table"],
        adjacency=payloads["adjacency"],
        graph_distances=payloads["graph_distances"],
        node_poincare_coordinates=payloads["node_poincare_coordinates"],
        node_poincare_distances=payloads["node_poincare_distances"],
    )
    write_json(OUT_DIR / "rewrite_complex_certificate.json", payloads["rewrite_complex_certificate"])
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
                "node_count": witness["node_count"],
                "edge_count": witness["edge_count"],
                "graph_diameter": witness["graph_diameter"],
                "graph_gromov_delta": witness["graph_gromov_delta"],
                "poincare_diameter_pair_node_ids": witness["poincare_diameter_pair_node_ids"],
                "graph_poincare_distance_correlation": witness["graph_poincare_distance_correlation"],
                "next_highest_yield_item": payloads["report"]["next_highest_yield_item"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
